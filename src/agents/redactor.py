"""
agents/redactor.py — Agente 2: Redactor
Responsabilidad: tomar los fragmentos recuperados por el Buscador y
generar una respuesta coherente y citada usando el LLM (Groq/Llama).
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.2-90b-text-preview")


class AgentesRedactor:
    """
    Agente especializado en generación de respuestas.
    Recibe fragmentos del Buscador y produce texto en lenguaje natural.
    """

    def __init__(self):
        self.cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def _construir_contexto(self, fragmentos: list[dict]) -> str:
        """Formatea los fragmentos como contexto para el LLM."""
        partes = []
        for i, f in enumerate(fragmentos, 1):
            partes.append(f"[Fuente {i}: {f['fuente']}]\n{f['texto']}")
        return "\n\n".join(partes)

    def redactar(self, pregunta: str, fragmentos: list[dict]) -> str:
        """
        Genera una respuesta en lenguaje natural citando las fuentes.

        Args:
            pregunta: Pregunta original del usuario.
            fragmentos: Lista de fragmentos recuperados por el Buscador.

        Returns:
            Respuesta en markdown con citación de fuentes.
        """
        contexto = self._construir_contexto(fragmentos)
        fuentes_usadas = list({f["fuente"] for f in fragmentos})

        prompt_sistema = """Eres un asistente turístico experto en el Eje Cafetero colombiano
(Risaralda, Quindío y Caldas). Respondes en español con un tono amigable y útil.

INSTRUCCIONES:
- Usa ÚNICAMENTE la información del contexto proporcionado.
- Al final de tu respuesta, incluye una sección "📚 Fuentes:" listando los documentos usados.
- Si la información no está en el contexto, dilo claramente.
- Sé conciso pero completo. Usa listas cuando sea útil."""

        prompt_usuario = f"""Contexto recuperado de los documentos:
{contexto}

Pregunta del usuario: {pregunta}

Responde usando solo la información del contexto y cita las fuentes al final."""

        print(f"[Agente Redactor] Generando respuesta con {GROQ_MODEL}...")

        respuesta = self.cliente.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user",   "content": prompt_usuario},
            ],
            temperature=0.3,
            max_tokens=800,
        )

        return respuesta.choices[0].message.content
