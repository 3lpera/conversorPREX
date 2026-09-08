import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import httpx

app = FastAPI(title="Prex Rate Converter Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

cache_cotizaciones = {
    "uyu_to_ars": None,
    "usd_to_ars": None,
    "base_usd_ars": None,
    "base_usd_uyu": None,
    "last_updated": None,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
}


async def obtener_cotizaciones_prex():
  async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
    response = await client.get("https://www.prexcard.com/hacelabien", follow_redirects=True)
    if response.status_code != 200:
      raise Exception(
          f"Error al conectar con Prex: Status {response.status_code}"
      )
    print("URL final:", response.url)
    with open("respuesta.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    soup = BeautifulSoup(response.text, "html.parser")
    input_arg = soup.find("input", id="cotizacionArg")
    input_uy = soup.find("input", id="cotizacionUy")

    if not input_arg or not input_uy:
      raise ValueError("No se encontraron las etiquetas de cotización en el DOM")

    cotizacion_arg = float(
        input_arg.get("value", "0").replace(",", ".")
    )
    cotizacion_uy = float(
        input_uy.get("value", "0").replace(",", ".")
    )
    print(f"Cotización ARS: {cotizacion_arg}, Cotización UYU: {cotizacion_uy}")
    usd_to_ars = cotizacion_arg
    uyu_to_ars = cotizacion_arg / cotizacion_uy 

    return {
        "usd_to_ars": round(usd_to_ars, 2),
        "uyu_to_ars": round(uyu_to_ars, 4),
        "base_usd_ars": cotizacion_arg,
        "base_usd_uyu": cotizacion_uy,
    }


async def tarea_actualizar_cache():
  while True:
    try:
      datos = await obtener_cotizaciones_prex()
      cache_cotizaciones.update(datos)
      cache_cotizaciones["last_updated"] = datetime.now().isoformat()
    except Exception as e:
      print(f"Error actualizando cotizaciones: {e}")
    await asyncio.sleep(600)


@app.on_event("startup")
async def startup_event():
  asyncio.create_task(tarea_actualizar_cache())


@app.get("/")
async def serve_index():
  return FileResponse("static/index.html")


@app.get("/cotizaciones")
async def get_rates():
  if not cache_cotizaciones["last_updated"]:
    raise HTTPException(
        status_code=503, detail="Cotizaciones no disponibles aún"
    )
  return cache_cotizaciones


@app.get("/convertir")
async def convertir(monto: float, origen: str):
  origen = origen.lower()
  if not cache_cotizaciones["last_updated"]:
    raise HTTPException(
        status_code=503, detail="El servicio se está inicializando"
    )

  if origen == "uyu":
    rate = cache_cotizaciones["uyu_to_ars"]
    resultado = monto * rate
  elif origen == "usd":
    rate = cache_cotizaciones["usd_to_ars"]
    resultado = monto * rate
  else:
    raise HTTPException(
        status_code=400,
        detail="Moneda de origen no válida. Usar 'uyu' o 'usd'",
    )

  return {
      "monto_origen": monto,
      "moneda_origen": origen.upper(),
      "resultado_ars": round(resultado, 2),
      "cotizacion_aplicada": rate,
      "ultima_actualizacion": cache_cotizaciones["last_updated"],
  }