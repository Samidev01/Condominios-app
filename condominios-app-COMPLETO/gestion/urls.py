from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.AdminLoginView.as_view(), name="login"),
    path("logout/", views.AdminLogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("condominio/", views.condominio_config, name="condominio_config"),
    path("unidades/", views.unidad_lista, name="unidad_lista"),
    path("unidades/nueva/", views.unidad_crear, name="unidad_crear"),
    path("unidades/<int:pk>/editar/", views.unidad_editar, name="unidad_editar"),
    path("inquilinos/", views.inquilino_lista, name="inquilino_lista"),
    path("inquilinos/nuevo/", views.inquilino_crear, name="inquilino_crear"),
    path("inquilinos/<int:pk>/editar/", views.inquilino_editar, name="inquilino_editar"),
    path("facturas/", views.factura_lista, name="factura_lista"),
    path("facturas/generar/", views.factura_generar, name="factura_generar"),
    path("comprobantes/", views.comprobante_lista, name="comprobante_lista"),
    path("comprobantes/nuevo/", views.comprobante_crear, name="comprobante_crear"),
    path("comprobantes/<int:pk>/", views.comprobante_detalle, name="comprobante_detalle"),
    path("comprobantes/<int:pk>/aprobar/", views.comprobante_aprobar, name="comprobante_aprobar"),
    path("comprobantes/<int:pk>/rechazar/", views.comprobante_rechazar, name="comprobante_rechazar"),
    path("exportar/excel/", views.exportar_excel, name="exportar_excel"),
    path("exportar/pdf/", views.exportar_pdf, name="exportar_pdf"),
]
