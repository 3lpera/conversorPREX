# Conversor PREX → ARS

Aplicación web simple para convertir montos desde **UYU** y **USD** a **ARS** usando cotizaciones obtenidas automáticamente desde PREX.

## Qué hace

- Muestra cotización de:
  - `1 UYU` a ARS
  - `1 USD` a ARS
- Permite ingresar un monto y elegir moneda de origen (`UYU` o `USD`)
- Calcula en tiempo real el valor estimado en ARS
- Actualiza cotizaciones en segundo plano cada 10 minutos
- Incluye frontend estático y backend API en FastAPI
- Soporta instalación como PWA (manifest + service worker)

## Tecnologías

- Python
- FastAPI
- Uvicorn
- httpx
- BeautifulSoup4
- HTML/CSS/JavaScript (frontend estático)

## Estructura del proyecto

- `/home/runner/work/conversorPREX/conversorPREX/main.py`: backend FastAPI, scraping, cache y endpoints
- `/home/runner/work/conversorPREX/conversorPREX/static/index.html`: interfaz principal
- `/home/runner/work/conversorPREX/conversorPREX/static/manifest.json`: configuración PWA
- `/home/runner/work/conversorPREX/conversorPREX/static/sw.js`: service worker
- `/home/runner/work/conversorPREX/conversorPREX/requirements.txt`: dependencias Python

## Requisitos

- Python 3.10+ (recomendado)
- pip

## Instalación

```bash
cd /home/runner/work/conversorPREX/conversorPREX
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar la app

```bash
cd /home/runner/work/conversorPREX/conversorPREX
uvicorn main:app --reload
```

Luego abrir en el navegador:

- `http://127.0.0.1:8000/`

## Endpoints

### `GET /`

Sirve la interfaz web.

### `GET /cotizaciones`

Devuelve cotizaciones en cache.

Ejemplo de respuesta:

```json
{
  "uyu_to_ars": 31.2345,
  "usd_to_ars": 1250.5,
  "base_usd_ars": 1250.5,
  "base_usd_uyu": 40.03,
  "last_updated": "2026-09-09T20:00:00.000000"
}
```

### `GET /convertir?monto=<numero>&origen=<uyu|usd>`

Convierte el monto indicado a ARS.

Ejemplo:

`/convertir?monto=100&origen=uyu`

## Notas de funcionamiento

- Al iniciar, la app puede responder `503` hasta tener la primera cotización cargada.
- Si falla la conexión con PREX, se mantiene la última cotización válida en cache.
- El archivo `respuesta.html` se usa para guardar la respuesta HTML obtenida en cada consulta.