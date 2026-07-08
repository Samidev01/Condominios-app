from datetime import date

from django.core.management.base import BaseCommand

from gestion.services import actualizar_morosidad, generar_facturas_mes


class Command(BaseCommand):
    help = "Genera facturas mensuales para todas las unidades con inquilino"

    def add_arguments(self, parser):
        hoy = date.today()
        parser.add_argument("--mes", type=int, default=hoy.month)
        parser.add_argument("--anio", type=int, default=hoy.year)

    def handle(self, *args, **options):
        mes = options["mes"]
        anio = options["anio"]
        creadas, existentes = generar_facturas_mes(mes, anio)
        vencidas = actualizar_morosidad()
        self.stdout.write(
            self.style.SUCCESS(
                f"Facturas {mes:02d}/{anio}: {creadas} creadas, "
                f"{existentes} ya existían. {vencidas} marcadas vencidas."
            )
        )
