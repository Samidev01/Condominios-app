# App de administración de condominios

Aplicación web para que un administrador gestione un condominio: inquilinos, unidades, facturación mensual de renta, pagos por comprobante (conciliación manual) y alertas de morosidad.

## Stack

- **Backend**: Django 6 + Python
- **Base de datos**: SQLite (desarrollo) o PostgreSQL (producción)
- **Frontend**: plantillas Django + Bootstrap 5
- **Reportes**: exportación PDF y Excel

## Inicio rápido

```bash
# 1. Entorno virtual (opcional)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 2. Dependencias
pip install -r requirements.txt

# 3. Variables de entorno
copy .env.example .env        # Windows
# cp .env.example .env        # Linux/Mac

# 4. Migraciones y usuario admin
python manage.py migrate
python manage.py createsuperuser

# 5. Servidor de desarrollo
python manage.py runserver
```

Abre http://127.0.0.1:8000/ e inicia sesión con el superusuario.

## PostgreSQL (opcional)

```bash
docker compose up -d
```

En `.env`:

```
DB_ENGINE=postgresql
DB_NAME=condominios
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

## Flujo de uso

1. **Configuración** — Registra el condominio (nombre y dirección).
2. **Unidades** — Crea apartamentos/locales con su renta mensual.
3. **Inquilinos** — Asigna un inquilino a cada unidad.
4. **Facturas** — Genera facturas del mes con el botón o el comando:

   ```bash
   python manage.py generar_facturas --mes 7 --anio 2026
   ```

5. **Comprobantes** — Sube la imagen del comprobante, vincúlala a la factura y declara monto/fecha.
6. **Conciliación** — Revisa el comprobante y aprueba (marca factura pagada) o rechaza.
7. **Dashboard** — Ve alertas de morosidad y exporta reportes PDF/Excel.

## Panel Django Admin

Disponible en `/admin/` con el mismo superusuario.

## Despliegue en Render (compartir por URL)

Sigue la guía completa en **[DEPLOY.md](DEPLOY.md)**.

Resumen:
1. Sube el código a GitHub
2. Crea cuenta en [Cloudinary](https://cloudinary.com) (imágenes de comprobantes)
3. En [Render](https://render.com): **New → Blueprint** → selecciona el repo
4. Agrega `CLOUDINARY_URL` cuando lo pida
5. En Render Shell: `python manage.py createsuperuser`
6. Comparte la URL `https://tu-app.onrender.com`

## Despliegue local / VPS

- Configura `SECRET_KEY`, `DEBUG=False` y `ALLOWED_HOSTS`.
- Usa PostgreSQL en producción.
- Ejecuta `python manage.py collectstatic`.
- Para almacenamiento de imágenes en S3, configura `DEFAULT_FILE_STORAGE` con `django-storages` (mejora futura).

## Alcance del MVP

- Un solo administrador, un solo condominio.
- Conciliación manual de pagos (sin OCR ni pasarelas).
- Subida de comprobantes desde navegador (incluye móvil).
