# 🌿 Asistente Turístico — Eje Cafetero

Asistente inteligente especializado en turismo del Eje Cafetero colombiano, construido con RAG, multiagentes y arquitectura moderna de IA.

**Proyecto Final — Introducción a la Inteligencia Artificial 2026-I**  
**Integrantes:** Sara · Sebastián

---

## ¿Qué hace este asistente?

Responde preguntas en lenguaje natural sobre destinos, rutas, gastronomía, clima y cultura del Eje Cafetero (Risaralda, Quindío y Caldas), usando información recuperada de un corpus propio de documentos con citación de fuentes.

## Arquitectura

```
Usuario (Streamlit)
       ↓
Agente Buscador  →  ChromaDB (búsqueda híbrida)
       ↓
Agente Redactor  →  Groq API / Llama 3.2
       ↓
Respuesta con fuentes citadas
       +
MCP Weather (clima en tiempo real)
Skill PDF (itinerario descargable)
```

## Requisitos

- Python 3.11+
- Cuenta gratuita en [Groq](https://console.groq.com)
- Cuenta gratuita en [OpenWeatherMap](https://openweathermap.org/api)

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/eje-cafetero-assistant.git
cd eje-cafetero-assistant

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus API keys

# 5. Indexar los documentos (solo la primera vez)
python src/rag/ingestor.py

# 6. Lanzar la aplicación
streamlit run src/app.py
```

## Estructura del proyecto

```
eje-cafetero-assistant/
├── src/
│   ├── app.py                  # Interfaz Streamlit
│   ├── agents/
│   │   ├── buscador.py         # Agente que recupera documentos
│   │   └── redactor.py         # Agente que genera la respuesta
│   ├── rag/
│   │   ├── ingestor.py         # Carga y procesa los PDFs
│   │   ├── embedder.py         # Genera embeddings
│   │   └── retriever.py        # Búsqueda híbrida (semántica + BM25)
│   ├── mcp/
│   │   └── weather_server.py   # Servidor MCP de clima
│   └── skills/
│       └── itinerario_pdf.py   # Skill: genera PDF de itinerario
├── data/
│   ├── documentos/             # PDFs del corpus (15+ archivos)
│   └── chroma_db/              # Base vectorial (generada automáticamente)
├── docs/
│   ├── arquitectura.png        # Diagrama general del sistema
│   ├── flujo_rag.png           # Diagrama del pipeline RAG
│   ├── agentes.png             # Diagrama de interacción multiagente
│   └── decisiones.md           # Decisiones técnicas justificadas
├── tests/
│   ├── test_rag.py
│   └── test_agents.py
├── .env.example
├── requirements.txt
└── README.md
```

## Patrones y conceptos implementados

| Concepto | Implementación |
|----------|----------------|
| Transformer | Llama 3.2 vía Groq API |
| Embeddings | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` |
| Base vectorial | ChromaDB local |
| RAG | Pipeline completo con búsqueda híbrida (semántica + BM25) |
| Multiagentes | LangGraph con Agente Buscador + Agente Redactor |
| MCP | Servidor de clima en tiempo real |
| Skill | Generador de itinerario en PDF |
| Interfaz | Streamlit |

## Corpus de documentos

15 documentos sobre el Eje Cafetero, incluyendo guías de ProColombia, fichas de Parques Nacionales, artículos de Wikipedia y páginas de Colombia Travel. Todas las fuentes son abiertas o de dominio público.

## Licencia

Proyecto académico — Universidad [nombre] · 2026
