# Despliegue en Render

Guía paso a paso para publicar la app y compartirla por URL.

## Requisitos previos

1. Cuenta en [GitHub](https://github.com) (gratis)
2. Cuenta en [Render](https://render.com) (gratis)
3. Cuenta en [Cloudinary](https://cloudinary.com) (gratis) — para guardar imágenes de comprobantes

> **Nota:** En Render el disco es temporal; sin Cloudinary las imágenes subidas se pierden al reiniciar el servidor.

---

## Paso 1 — Subir el código a GitHub

Si Git no funciona en tu PC, puedes crear el repositorio en GitHub y subir los archivos desde la web (botón **Upload files**).

```bash
cd C:\Users\Administrador\Projects\condominios-app
git init
git add .
git commit -m "App condominios MVP"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/condominios-app.git
git push -u origin main
```

---

## Paso 2 — Crear cuenta en Cloudinary

1. Regístrate en https://cloudinary.com
2. En el **Dashboard**, copia la URL que aparece como **API environment variable**:
   ```
   cloudinary://123456789:abcdefgh@tu-cloud-name
   ```
3. Guárdala; la usarás en Render.

---

## Paso 3 — Desplegar en Render (método Blueprint)

1. Entra a https://dashboard.render.com
2. Clic en **New +** → **Blueprint**
3. Conecta tu cuenta de GitHub y selecciona el repositorio `condominios-app`
4. Render detectará el archivo `render.yaml` y creará:
   - Base de datos PostgreSQL (`condominios-db`)
   - Servicio web (`condominios-app`)
5. Cuando pida variables, agrega:
   - **CLOUDINARY_URL** = la URL que copiaste de Cloudinary
6. Clic en **Apply**

El primer despliegue tarda unos 5–10 minutos.

---

## Paso 4 — Crear el usuario administrador

Cuando el deploy termine en verde:

1. En Render, abre el servicio **condominios-app**
2. Pestaña **Shell** (consola en la nube)
3. Ejecuta:

```bash
python manage.py createsuperuser
```

Elige usuario y contraseña que le compartirás al administrador del condominio.

---

## Paso 5 — Compartir la app

Tu URL será algo como:

```
https://condominios-app-xxxx.onrender.com
```

Envía al administrador:

| Dato | Valor |
|------|-------|
| **URL** | `https://condominios-app-xxxx.onrender.com` |
| **Usuario** | el que creaste |
| **Contraseña** | la que definiste |

Funciona en celular, tablet y PC desde cualquier navegador.

---

## Plan gratuito de Render — qué esperar

- El servicio **se apaga** tras ~15 min sin uso; el primer acceso puede tardar **30–60 segundos** en despertar.
- La base de datos PostgreSQL gratuita expira a los **90 días** (Render avisa por email).
- Para uso continuo sin pausas, necesitas plan de pago (~$7/mes web + ~$7/mes DB).

---

## Despliegue manual (sin Blueprint)

Si prefieres crear los servicios a mano:

### Base de datos
- **New +** → **PostgreSQL** → nombre `condominios-db` → plan Free

### Servicio web
- **New +** → **Web Service** → conecta el repo
- **Runtime:** Python
- **Build command:** `./build.sh`
- **Start command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
- **Variables de entorno:**

| Variable | Valor |
|----------|-------|
| `PYTHON_VERSION` | `3.12.9` |
| `DATABASE_URL` | *(Internal Database URL de PostgreSQL)* |
| `SECRET_KEY` | *(generar valor aleatorio largo)* |
| `DEBUG` | `False` |
| `CLOUDINARY_URL` | `cloudinary://...` |

Render añade automáticamente `RENDER_EXTERNAL_HOSTNAME` para `ALLOWED_HOSTS`.

---

## Comandos útiles en Render Shell

```bash
# Generar facturas del mes actual
python manage.py generar_facturas

# Generar facturas de un mes específico
python manage.py generar_facturas --mes 7 --anio 2026
```

---

## Solución de problemas

| Problema | Solución |
|----------|----------|
| Error 502 al abrir la URL | Espera a que termine el deploy o revisa los logs en Render |
| Las imágenes no se guardan | Verifica que `CLOUDINARY_URL` esté configurada |
| Error CSRF al iniciar sesión | `RENDER_EXTERNAL_HOSTNAME` debe estar activo (automático en Render) |
| App muy lenta al inicio | Normal en plan gratuito (cold start) |
