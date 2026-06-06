# 🌿 Asistente Turístico — Eje Cafetero

Asistente inteligente especializado en turismo del Eje Cafetero colombiano, construido con RAG, multiagentes LangGraph, servidor MCP y arquitectura moderna de IA.

**Proyecto Final — Introducción a la Inteligencia Artificial 2026-I**  
**Integrantes:** Sara Clavo Duque · Joan Sebastián Loaiza  
**Universidad Tecnológica de Pereira**

---

## ¿Qué hace este asistente?

Responde preguntas en lenguaje natural sobre destinos, rutas, gastronomía, clima y cultura del Eje Cafetero (Risaralda, Quindío y Caldas), usando información recuperada de un corpus propio de 15 documentos con citación de fuentes.

## Arquitectura del sistema

```
Usuario (Streamlit)
       │
       ▼
┌─────────────────────────────────────────┐
│         LangGraph StateGraph            │
│                                         │
│  ┌─────────────┐    ┌─────────────────┐ │
│  │   Agente    │───▶│    Agente       │ │
│  │  Buscador   │    │   Redactor      │ │
│  └─────────────┘    └─────────────────┘ │
│         │                   │           │
│    ChromaDB              Groq API       │
│  (búsqueda híbrida)   llama-3.3-70b     │
│  semántica + BM25                       │
└─────────────────────────────────────────┘
       │
       ▼
  MCP Weather ──▶ OpenWeatherMap API
  (clima en tiempo real si mencionas una ciudad)
       │
       ▼
  Skill PDF ──▶ Itinerario descargable (ReportLab)
```

## Pipeline RAG

```
PDFs (15 docs)
    │
    ▼ ingestor.py
Texto extraído
    │
    ▼ dividir_en_chunks()
Fragmentos (500 palabras, 50 overlap)
    │
    ▼ SentenceTransformer
Embeddings (paraphrase-multilingual-mpnet-base-v2)
    │
    ▼ ChromaDB (cosine)
Base vectorial persistente
    │
    ▼ retriever.py — búsqueda híbrida
70% semántica + 30% BM25
    │
    ▼ Top 4 fragmentos → Agente Redactor → Respuesta
```

## Componentes

| Componente | Archivo | Descripción |
|-----------|---------|-------------|
| Orquestador | `src/agents/grafo.py` | LangGraph StateGraph — flujo multiagente |
| Agente Buscador | `src/agents/buscador.py` | Recupera fragmentos relevantes del corpus |
| Agente Redactor | `src/agents/redactor.py` | Genera respuesta citando fuentes con Groq |
| Ingestor RAG | `src/rag/ingestor.py` | Procesa PDFs y construye la base vectorial |
| Retriever híbrido | `src/rag/retriever.py` | Búsqueda semántica + BM25 sobre ChromaDB |
| Servidor MCP | `src/mcp/weather_server.py` | Clima en tiempo real vía OpenWeatherMap |
| Skill PDF | `src/skills/itinerario_pdf.py` | Genera PDF de itinerario descargable |
| Interfaz | `src/app.py` | Streamlit — integra todos los componentes |

## Requisitos previos

- Python 3.11+ (recomendado vía Anaconda)
- Cuenta gratuita en [Groq](https://console.groq.com) → API Key
- Cuenta gratuita en [OpenWeatherMap](https://openweathermap.org/api) → API Key

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tiaen2211/eje-cafetero-assistant.git
cd eje-cafetero-assistant

# 2. Crear entorno conda con Python 3.11
conda create -n eje-cafetero python=3.11 -y
conda activate eje-cafetero

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# 5. Indexar los documentos (solo la primera vez)
#    Copiar los PDFs en data/documentos/ antes de este paso
python src/rag/ingestor.py

# 6. Lanzar la aplicación
streamlit run src/app.py
```

## Estructura del proyecto

```
eje-cafetero-assistant/
├── src/
│   ├── app.py                  # Interfaz Streamlit + integración MCP
│   ├── agents/
│   │   ├── grafo.py            # Orquestador LangGraph (StateGraph)
│   │   ├── buscador.py         # Agente 1: recupera fragmentos del corpus
│   │   └── redactor.py         # Agente 2: genera respuesta con Groq
│   ├── rag/
│   │   ├── ingestor.py         # Carga PDFs y construye ChromaDB
│   │   └── retriever.py        # Búsqueda híbrida (semántica 70% + BM25 30%)
│   ├── mcp/
│   │   └── weather_server.py   # Servidor MCP — herramienta obtener_clima
│   └── skills/
│       └── itinerario_pdf.py   # Skill: genera PDF con ReportLab
├── data/
│   ├── documentos/             # 15 PDFs del corpus turístico
│   └── chroma_db/              # Base vectorial (generada automáticamente)
├── docs/
│   └── decisiones.md           # 5 decisiones técnicas justificadas
├── tests/
│   └── test_rag.py
├── .env.example
├── requirements.txt
└── README.md
```

## Tecnologías usadas

| Concepto | Implementación |
|----------|----------------|
| LLM | Llama 3.3 70B vía Groq API |
| Embeddings | `paraphrase-multilingual-mpnet-base-v2` (sentence-transformers) |
| Base vectorial | ChromaDB local persistente |
| RAG | Pipeline completo con búsqueda híbrida (semántica + BM25) |
| Multiagentes | LangGraph `StateGraph` — Buscador + Redactor |
| MCP | Servidor stdio con herramienta `obtener_clima` |
| Skill | Generador de itinerario en PDF (ReportLab) |
| Interfaz | Streamlit |

## Corpus de documentos

15 documentos sobre el Eje Cafetero: guías de ProColombia, fichas de Parques Nacionales, artículos académicos, artículos de Wikipedia y publicaciones de turismo sostenible. Todas las fuentes son abiertas o de dominio público.

## Decisiones técnicas

Ver [`docs/decisiones.md`](docs/decisiones.md) para la justificación detallada de las 5 decisiones de diseño más importantes del proyecto.

## Licencia

Proyecto académico — Universidad Tecnológica de Pereira · 2026
