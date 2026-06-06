"""
app.py — Interfaz principal del asistente turístico Eje Cafetero
Ejecutar con: streamlit run src/app.py
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv

from agents.grafo import consultar
from skills.itinerario_pdf import generar_itinerario_pdf

load_dotenv()

# ── Configuración de la página ─────────────────────────────────────────────
st.set_page_config(
    page_title="Asistente Turístico — Eje Cafetero",
    page_icon="🌿",
    layout="centered",
)

st.title("🌿 Asistente Turístico del Eje Cafetero")
st.caption("Pregúntame sobre destinos, rutas, gastronomía, clima y cultura de Risaralda, Quindío y Caldas.")

# ── Historial de conversación ──────────────────────────────────────────────
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ── Integración MCP: clima en tiempo real ─────────────────────────────────
CIUDADES_EJE = {
    "pereira": "Pereira,CO",
    "manizales": "Manizales,CO",
    "armenia": "Armenia,CO",
    "salento": "Salento,CO",
    "filandia": "Filandia,CO",
    "quimbaya": "Quimbaya,CO",
    "cartago": "Cartago,CO",
    "montenegro": "Montenegro,CO",
    "circasia": "Circasia,CO",
}

def _consultar_clima_mcp(ciudad: str) -> str:
    """
    Llama a la herramienta 'obtener_clima' del servidor MCP de clima.
    Para la demo se invoca la lógica del servidor directamente;
    en producción se conectaría via mcp.ClientSession al proceso stdio.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not api_key:
        return ""
    ciudad_query = CIUDADES_EJE.get(ciudad.lower(), f"{ciudad},CO")
    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": ciudad_query, "appid": api_key, "units": "metric", "lang": "es"},
            timeout=5,
        )
        if resp.status_code != 200:
            return ""
        d = resp.json()
        return (
            f"\n\n🌤️ **Clima actual en {d['name']}:** "
            f"{d['weather'][0]['description'].capitalize()}, "
            f"{d['main']['temp']:.1f}°C — "
            f"Humedad {d['main']['humidity']}%."
        )
    except Exception:
        return ""


def _detectar_ciudad(texto: str) -> str | None:
    """Detecta si el usuario menciona una ciudad del Eje Cafetero."""
    texto_lower = texto.lower()
    for ciudad in CIUDADES_EJE:
        if ciudad in texto_lower:
            return ciudad
    return None


# ── Entrada del usuario ────────────────────────────────────────────────────
if pregunta := st.chat_input("¿Qué quieres saber del Eje Cafetero?"):

    with st.chat_message("user"):
        st.markdown(pregunta)
    st.session_state.mensajes.append({"role": "user", "content": pregunta})

    with st.chat_message("assistant"):
        with st.spinner("Consultando documentos y generando respuesta..."):

            # ── Pipeline multiagente via LangGraph ────────────────────────
            respuesta, fragmentos = consultar(pregunta)

            # ── MCP: enriquecer con clima si mencionan una ciudad ─────────
            ciudad = _detectar_ciudad(pregunta)
            if ciudad:
                info_clima = _consultar_clima_mcp(ciudad)
                if info_clima:
                    respuesta += info_clima

        st.markdown(respuesta)

        # ── Skill: generar PDF de itinerario ──────────────────────────────
        palabras_itinerario = ["itinerario", "plan", "viaje", "días", "visitar", "recorrido"]
        if any(p in pregunta.lower() for p in palabras_itinerario):
            pdf_bytes = generar_itinerario_pdf(pregunta, respuesta)
            st.download_button(
                label="📄 Descargar itinerario en PDF",
                data=pdf_bytes,
                file_name="itinerario_eje_cafetero.pdf",
                mime="application/pdf",
            )

        # ── Mostrar fuentes usadas ────────────────────────────────────────
        if fragmentos:
            with st.expander("📚 Fuentes consultadas"):
                fuentes = list({f["fuente"] for f in fragmentos})
                for f in fuentes:
                    st.markdown(f"- {f}")

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
