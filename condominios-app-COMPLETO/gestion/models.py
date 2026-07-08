from django.db import models
from django.utils import timezone


class Condominio(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.TextField()

    class Meta:
        verbose_name_plural = "Condominios"

    def __str__(self):
        return self.nombre


class Unidad(models.Model):
    condominio = models.ForeignKey(
        Condominio, on_delete=models.CASCADE, related_name="unidades"
    )
    identificador = models.CharField("Número / identificador", max_length=50)
    renta_mensual = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "Unidades"
        unique_together = ["condominio", "identificador"]
        ordering = ["identificador"]

    def __str__(self):
        return f"{self.identificador} — {self.condominio.nombre}"

    @property
    def inquilino_actual(self):
        return getattr(self, "inquilino", None)


class Inquilino(models.Model):
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    unidad = models.OneToOneField(
        Unidad, on_delete=models.CASCADE, related_name="inquilino"
    )
    fecha_inicio_contrato = models.DateField()

    class Meta:
        verbose_name_plural = "Inquilinos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Factura(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_PAGADA = "pagada"
    ESTADO_VENCIDA = "vencida"

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_PAGADA, "Pagada"),
        (ESTADO_VENCIDA, "Vencida"),
    ]

    unidad = models.ForeignKey(
        Unidad, on_delete=models.CASCADE, related_name="facturas"
    )
    mes = models.PositiveSmallIntegerField()
    anio = models.PositiveSmallIntegerField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE
    )
    fecha_vencimiento = models.DateField(null=True, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Facturas"
        unique_together = ["unidad", "mes", "anio"]
        ordering = ["-anio", "-mes", "unidad__identificador"]

    def __str__(self):
        return f"{self.unidad.identificador} — {self.mes:02d}/{self.anio}"

    @property
    def periodo(self):
        return f"{self.mes:02d}/{self.anio}"

    @property
    def esta_vencida(self):
        if self.estado == self.ESTADO_PAGADA:
            return False
        if self.fecha_vencimiento:
            return self.fecha_vencimiento < timezone.localdate()
        return False


class ComprobantePago(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_APROBADO = "aprobado"
    ESTADO_RECHAZADO = "rechazado"

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente de revisión"),
        (ESTADO_APROBADO, "Aprobado"),
        (ESTADO_RECHAZADO, "Rechazado"),
    ]

    factura = models.ForeignKey(
        Factura, on_delete=models.CASCADE, related_name="comprobantes"
    )
    imagen = models.ImageField(upload_to="comprobantes/%Y/%m/")
    monto_declarado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_declarada = models.DateField()
    fecha_subida = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE
    )
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Comprobantes de pago"
        ordering = ["-fecha_subida"]

    def __str__(self):
        return f"Comprobante {self.factura} — {self.get_estado_display()}"
