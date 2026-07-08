import io
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .forms import (
    ComprobanteForm,
    CondominioForm,
    FiltroMesForm,
    GenerarFacturasForm,
    InquilinoForm,
    UnidadForm,
)
from .models import ComprobantePago, Condominio, Factura, Inquilino, Unidad
from .services import (
    actualizar_morosidad,
    aprobar_comprobante,
    generar_facturas_mes,
    rechazar_comprobante,
    resumen_pagos_mes,
)


class AdminLoginView(LoginView):
    template_name = "gestion/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("dashboard")


class AdminLogoutView(LogoutView):
    next_page = reverse_lazy("login")


@login_required
def dashboard(request):
    actualizar_morosidad()

    hoy = date.today()
    resumen = resumen_pagos_mes(hoy.month, hoy.year)

    facturas_vencidas = Factura.objects.filter(
        estado=Factura.ESTADO_VENCIDA
    ).select_related("unidad", "unidad__inquilino")[:10]

    comprobantes_pendientes = ComprobantePago.objects.filter(
        estado=ComprobantePago.ESTADO_PENDIENTE
    ).select_related("factura", "factura__unidad")[:10]

    context = {
        "resumen": resumen,
        "facturas_vencidas": facturas_vencidas,
        "comprobantes_pendientes": comprobantes_pendientes,
        "total_unidades": Unidad.objects.count(),
        "total_inquilinos": Inquilino.objects.count(),
        "mes_actual": hoy.month,
        "anio_actual": hoy.year,
    }
    return render(request, "gestion/dashboard.html", context)


@login_required
def unidad_lista(request):
    unidades = Unidad.objects.select_related("condominio", "inquilino").all()
    return render(request, "gestion/unidad_lista.html", {"unidades": unidades})


@login_required
def unidad_crear(request):
    form = UnidadForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Unidad creada correctamente.")
        return redirect("unidad_lista")
    return render(request, "gestion/formulario.html", {"form": form, "titulo": "Nueva unidad"})


@login_required
def unidad_editar(request, pk):
    unidad = get_object_or_404(Unidad, pk=pk)
    form = UnidadForm(request.POST or None, instance=unidad)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Unidad actualizada.")
        return redirect("unidad_lista")
    return render(
        request,
        "gestion/formulario.html",
        {"form": form, "titulo": f"Editar unidad {unidad.identificador}"},
    )


@login_required
def inquilino_lista(request):
    inquilinos = Inquilino.objects.select_related("unidad", "unidad__condominio").all()
    return render(request, "gestion/inquilino_lista.html", {"inquilinos": inquilinos})


@login_required
def inquilino_crear(request):
    form = InquilinoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Inquilino registrado correctamente.")
        return redirect("inquilino_lista")
    return render(
        request, "gestion/formulario.html", {"form": form, "titulo": "Nuevo inquilino"}
    )


@login_required
def inquilino_editar(request, pk):
    inquilino = get_object_or_404(Inquilino, pk=pk)
    form = InquilinoForm(request.POST or None, instance=inquilino)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Inquilino actualizado.")
        return redirect("inquilino_lista")
    return render(
        request,
        "gestion/formulario.html",
        {"form": form, "titulo": f"Editar inquilino {inquilino.nombre}"},
    )


@login_required
def factura_lista(request):
    hoy = date.today()
    form = FiltroMesForm(
        request.GET or None,
        initial={"mes": hoy.month, "anio": hoy.year},
    )
    mes, anio = hoy.month, hoy.year
    if form.is_valid():
        mes = form.cleaned_data["mes"]
        anio = form.cleaned_data["anio"]

    resumen = resumen_pagos_mes(mes, anio)
    return render(
        request,
        "gestion/factura_lista.html",
        {"form": form, "resumen": resumen, "mes": mes, "anio": anio},
    )


@login_required
def factura_generar(request):
    hoy = date.today()
    form = GenerarFacturasForm(
        request.POST or None, initial={"mes": hoy.month, "anio": hoy.year}
    )
    if request.method == "POST" and form.is_valid():
        mes = form.cleaned_data["mes"]
        anio = form.cleaned_data["anio"]
        creadas, existentes = generar_facturas_mes(mes, anio)
        actualizar_morosidad()
        messages.success(
            request,
            f"Facturas generadas: {creadas} nuevas, {existentes} ya existían.",
        )
        return redirect("factura_lista")
    return render(
        request,
        "gestion/formulario.html",
        {"form": form, "titulo": "Generar facturas mensuales"},
    )


@login_required
def comprobante_lista(request):
    comprobantes = ComprobantePago.objects.select_related(
        "factura", "factura__unidad"
    ).all()
    return render(
        request, "gestion/comprobante_lista.html", {"comprobantes": comprobantes}
    )


@login_required
def comprobante_crear(request):
    form = ComprobanteForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Comprobante subido. Pendiente de revisión.")
        return redirect("comprobante_lista")
    return render(
        request,
        "gestion/formulario.html",
        {"form": form, "titulo": "Subir comprobante de pago", "enctype": True},
    )


@login_required
def comprobante_detalle(request, pk):
    comprobante = get_object_or_404(
        ComprobantePago.objects.select_related("factura", "factura__unidad"), pk=pk
    )
    return render(
        request, "gestion/comprobante_detalle.html", {"comprobante": comprobante}
    )


@login_required
def comprobante_aprobar(request, pk):
    if request.method != "POST":
        return redirect("comprobante_detalle", pk=pk)
    comprobante = get_object_or_404(ComprobantePago, pk=pk)
    if comprobante.estado == ComprobantePago.ESTADO_PENDIENTE:
        aprobar_comprobante(comprobante)
        messages.success(request, "Comprobante aprobado. Factura marcada como pagada.")
    return redirect("comprobante_detalle", pk=pk)


@login_required
def comprobante_rechazar(request, pk):
    comprobante = get_object_or_404(ComprobantePago, pk=pk)
    if request.method == "POST" and comprobante.estado == ComprobantePago.ESTADO_PENDIENTE:
        notas = request.POST.get("notas", "")
        rechazar_comprobante(comprobante, notas)
        messages.warning(request, "Comprobante rechazado.")
    return redirect("comprobante_detalle", pk=pk)


@login_required
def condominio_config(request):
    condominio = Condominio.objects.first()
    form = CondominioForm(
        request.POST or None, instance=condominio if condominio else None
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Datos del condominio guardados.")
        return redirect("dashboard")
    return render(
        request,
        "gestion/formulario.html",
        {"form": form, "titulo": "Configuración del condominio"},
    )


@login_required
def exportar_excel(request):
    hoy = date.today()
    mes = int(request.GET.get("mes", hoy.month))
    anio = int(request.GET.get("anio", hoy.year))
    resumen = resumen_pagos_mes(mes, anio)

    wb = Workbook()
    ws = wb.active
    ws.title = f"Pagos {mes:02d}-{anio}"
    ws.append(["Unidad", "Inquilino", "Monto", "Estado", "Vencimiento"])

    for f in resumen["facturas"]:
        inquilino = getattr(f.unidad, "inquilino", None)
        ws.append(
            [
                f.unidad.identificador,
                inquilino.nombre if inquilino else "—",
                float(f.monto),
                f.get_estado_display(),
                f.fecha_vencimiento.isoformat() if f.fecha_vencimiento else "",
            ]
        )

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="reporte_pagos_{mes:02d}_{anio}.xlsx"'
    )
    return response


@login_required
def exportar_pdf(request):
    hoy = date.today()
    mes = int(request.GET.get("mes", hoy.month))
    anio = int(request.GET.get("anio", hoy.year))
    resumen = resumen_pagos_mes(mes, anio)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f"Reporte de pagos — {mes:02d}/{anio}", styles["Title"]),
        Spacer(1, 12),
        Paragraph(
            f"Pagadas: {resumen['pagadas']} | Pendientes: {resumen['pendientes']} | "
            f"Vencidas: {resumen['vencidas']} | Total: ${resumen['total_monto']}",
            styles["Normal"],
        ),
        Spacer(1, 16),
    ]

    data = [["Unidad", "Inquilino", "Monto", "Estado"]]
    for f in resumen["facturas"]:
        inquilino = getattr(f.unidad, "inquilino", None)
        data.append(
            [
                f.unidad.identificador,
                inquilino.nombre if inquilino else "—",
                f"${f.monto}",
                f.get_estado_display(),
            ]
        )

    table = Table(data, colWidths=[80, 150, 80, 100])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="reporte_pagos_{mes:02d}_{anio}.pdf"'
    )
    return response
