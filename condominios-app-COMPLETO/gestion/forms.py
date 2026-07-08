from django import forms

from .models import ComprobantePago, Condominio, Factura, Inquilino, Unidad


class CondominioForm(forms.ModelForm):
    class Meta:
        model = Condominio
        fields = ["nombre", "direccion"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class UnidadForm(forms.ModelForm):
    class Meta:
        model = Unidad
        fields = ["condominio", "identificador", "renta_mensual"]
        widgets = {
            "condominio": forms.Select(attrs={"class": "form-select"}),
            "identificador": forms.TextInput(attrs={"class": "form-control"}),
            "renta_mensual": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
        }


class InquilinoForm(forms.ModelForm):
    class Meta:
        model = Inquilino
        fields = [
            "nombre",
            "telefono",
            "email",
            "unidad",
            "fecha_inicio_contrato",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "unidad": forms.Select(attrs={"class": "form-select"}),
            "fecha_inicio_contrato": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ocupadas = Inquilino.objects.values_list("unidad_id", flat=True)
        if self.instance.pk:
            ocupadas = ocupadas.exclude(unidad_id=self.instance.unidad_id)
        self.fields["unidad"].queryset = Unidad.objects.exclude(
            id__in=ocupadas
        ).order_by("identificador")


class ComprobanteForm(forms.ModelForm):
    class Meta:
        model = ComprobantePago
        fields = ["factura", "imagen", "monto_declarado", "fecha_declarada", "notas"]
        widgets = {
            "factura": forms.Select(attrs={"class": "form-select"}),
            "imagen": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "monto_declarado": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "fecha_declarada": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "notas": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["factura"].queryset = Factura.objects.filter(
            estado__in=[Factura.ESTADO_PENDIENTE, Factura.ESTADO_VENCIDA]
        ).select_related("unidad")


class GenerarFacturasForm(forms.Form):
    mes = forms.IntegerField(
        min_value=1,
        max_value=12,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    anio = forms.IntegerField(
        min_value=2000,
        max_value=2100,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )


class FiltroMesForm(forms.Form):
    mes = forms.IntegerField(
        min_value=1,
        max_value=12,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    anio = forms.IntegerField(
        min_value=2000,
        max_value=2100,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
