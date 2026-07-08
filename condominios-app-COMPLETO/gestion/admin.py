from django.contrib import admin

from .models import ComprobantePago, Condominio, Factura, Inquilino, Unidad


@admin.register(Condominio)
class CondominioAdmin(admin.ModelAdmin):
    list_display = ["nombre", "direccion"]


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ["identificador", "condominio", "renta_mensual"]
    list_filter = ["condominio"]
    search_fields = ["identificador"]


@admin.register(Inquilino)
class InquilinoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "unidad", "telefono", "email", "fecha_inicio_contrato"]
    search_fields = ["nombre", "telefono", "email"]
    list_filter = ["unidad__condominio"]


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ["unidad", "mes", "anio", "monto", "estado", "fecha_vencimiento"]
    list_filter = ["estado", "anio", "mes"]
    search_fields = ["unidad__identificador"]


@admin.register(ComprobantePago)
class ComprobantePagoAdmin(admin.ModelAdmin):
    list_display = [
        "factura",
        "monto_declarado",
        "fecha_declarada",
        "estado",
        "fecha_subida",
    ]
    list_filter = ["estado"]
    readonly_fields = ["fecha_subida"]
