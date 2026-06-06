"""
mcp/weather_server.py — Servidor MCP: Clima en tiempo real
Integra la API de OpenWeatherMap para obtener el clima actual
de cualquier ciudad del Eje Cafetero que el usuario mencione.

Ejecutar el servidor MCP:
    python src/mcp/weather_server.py
"""

import os
import json
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Ciudades del Eje Cafetero con sus coordenadas para mayor precisión
CIUDADES_EJE = {
    "pereira": "Pereira,CO",
    "manizales": "Manizales,CO",
    "armenia": "Armenia,CO",
    "salento": "Salento,CO",
    "filandia": "Filandia,CO",
    "quimbaya": "Quimbaya,CO",
    "cartago": "Cartago,CO",
}

app = Server("eje-cafetero-weather")


@app.list_tools()
async def listar_herramientas() -> list[types.Tool]:
    """Declara las herramientas disponibles en este servidor MCP."""
    return [
        types.Tool(
            name="obtener_clima",
            description="Obtiene el clima actual de una ciudad del Eje Cafetero",
            inputSchema={
                "type": "object",
                "properties": {
                    "ciudad": {
                        "type": "string",
                        "description": "Nombre de la ciudad (ej: Pereira, Manizales, Salento)",
                    }
                },
                "required": ["ciudad"],
            },
        )
    ]


@app.call_tool()
async def llamar_herramienta(nombre: str, argumentos: dict) -> list[types.TextContent]:
    """Ejecuta la herramienta solicitada."""

    if nombre != "obtener_clima":
        raise ValueError(f"Herramienta desconocida: {nombre}")

    ciudad_input = argumentos.get("ciudad", "").lower()
    ciudad_query = CIUDADES_EJE.get(ciudad_input, f"{argumentos['ciudad']},CO")

    try:
        response = requests.get(
            BASE_URL,
            params={
                "q": ciudad_query,
                "appid": API_KEY,
                "units": "metric",
                "lang": "es",
            },
            timeout=5,
        )
        data = response.json()

        if response.status_code != 200:
            resultado = f"No se pudo obtener el clima para {argumentos['ciudad']}."
        else:
            resultado = (
                f"Clima en {data['name']}: "
                f"{data['weather'][0]['description'].capitalize()}, "
                f"{data['main']['temp']:.1f}°C. "
                f"Humedad: {data['main']['humidity']}%. "
                f"Viento: {data['wind']['speed']} m/s."
            )

    except Exception as e:
        resultado = f"Error al consultar el clima: {str(e)}"

    return [types.TextContent(type="text", text=resultado)]


async def main():
    async with stdio_server() as (leer, escribir):
        await app.run(leer, escribir, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
