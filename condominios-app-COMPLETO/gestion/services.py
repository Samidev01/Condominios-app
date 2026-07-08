from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import ComprobantePago, Factura, Unidad


def ultimo_dia_mes(anio: int, mes: int) -> date:
    return date(anio, mes, monthrange(anio, mes)[1])


def generar_facturas_mes(mes: int, anio: int) -> tuple[int, int]:
    """Genera facturas mensuales para todas las unidades con inquilino."""
    creadas = 0
    existentes = 0
    vencimiento = ultimo_dia_mes(anio, mes)

    unidades = Unidad.objects.filter(inquilino__isnull=False).select_related(
        "inquilino"
    )

    for unidad in unidades:
        _, created = Factura.objects.get_or_create(
            unidad=unidad,
            mes=mes,
            anio=anio,
            defaults={
                "monto": unidad.renta_mensual,
                "fecha_vencimiento": vencimiento,
            },
        )
        if created:
            creadas += 1
        else:
            existentes += 1

    return creadas, existentes


def actualizar_morosidad() -> int:
    """Marca como vencidas las facturas pendientes cuya fecha de vencimiento pasó."""
    hoy = timezone.localdate()
    actualizadas = (
        Factura.objects.filter(
            estado=Factura.ESTADO_PENDIENTE,
            fecha_vencimiento__lt=hoy,
        ).update(estado=Factura.ESTADO_VENCIDA)
    )
    return actualizadas


@transaction.atomic
def aprobar_comprobante(comprobante: ComprobantePago) -> None:
    comprobante.estado = ComprobantePago.ESTADO_APROBADO
    comprobante.save(update_fields=["estado"])

    factura = comprobante.factura
    factura.estado = Factura.ESTADO_PAGADA
    factura.save(update_fields=["estado"])


@transaction.atomic
def rechazar_comprobante(comprobante: ComprobantePago, notas: str = "") -> None:
    comprobante.estado = ComprobantePago.ESTADO_RECHAZADO
    if notas:
        comprobante.notas = notas
    comprobante.save(update_fields=["estado", "notas"])


def resumen_pagos_mes(mes: int, anio: int) -> dict:
    facturas = Factura.objects.filter(mes=mes, anio=anio).select_related(
        "unidad", "unidad__inquilino"
    )

    total_monto = sum((f.monto for f in facturas), Decimal("0"))
    pagadas = sum(1 for f in facturas if f.estado == Factura.ESTADO_PAGADA)
    pendientes = sum(1 for f in facturas if f.estado == Factura.ESTADO_PENDIENTE)
    vencidas = sum(1 for f in facturas if f.estado == Factura.ESTADO_VENCIDA)

    return {
        "facturas": facturas,
        "total_monto": total_monto,
        "pagadas": pagadas,
        "pendientes": pendientes,
        "vencidas": vencidas,
        "total_unidades": facturas.count(),
    }
