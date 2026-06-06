"""
app.py — Interfaz principal del asistente turístico Eje Cafetero
Ejecutar con: streamlit run src/app.py
"""

import streamlit as st
from agents.buscador import AgentesBuscador
from agents.redactor import AgentesRedactor
from skills.itinerario_pdf import generar_itinerario_pdf

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

# Mostrar mensajes previos
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Entrada del usuario ────────────────────────────────────────────────────
if pregunta := st.chat_input("¿Qué quieres saber del Eje Cafetero?"):

    # Mostrar pregunta del usuario
    with st.chat_message("user"):
        st.markdown(pregunta)
    st.session_state.mensajes.append({"role": "user", "content": pregunta})

    # Generar respuesta con los agentes
    with st.chat_message("assistant"):
        with st.spinner("Buscando información..."):

            # Agente 1: Buscador recupera documentos relevantes
            buscador = AgentesBuscador()
            fragmentos = buscador.buscar(pregunta)

            # Agente 2: Redactor genera la respuesta con los fragmentos
            redactor = AgentesRedactor()
            respuesta = redactor.redactar(pregunta, fragmentos)

        st.markdown(respuesta)

        # Botón para generar itinerario PDF (Skill)
        if any(p in pregunta.lower() for p in ["itinerario", "plan", "viaje", "días"]):
            if st.button("📄 Descargar itinerario en PDF"):
                pdf_bytes = generar_itinerario_pdf(pregunta, respuesta)
                st.download_button(
                    label="⬇️ Guardar PDF",
                    data=pdf_bytes,
                    file_name="itinerario_eje_cafetero.pdf",
                    mime="application/pdf",
                )

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
