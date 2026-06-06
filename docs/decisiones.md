# Decisiones Técnicas — Asistente Turístico Eje Cafetero

## Decisión 1: ChromaDB como base vectorial

**Contexto:**  
El proyecto requería una base de datos vectorial para almacenar y recuperar embeddings de los documentos del corpus. Las opciones evaluadas fueron ChromaDB, FAISS y LanceDB.

**Decisión:**  
Se eligió ChromaDB.

**Razones:**  
- Instalación en una línea (`pip install chromadb`), sin dependencias de sistema.  
- Persistencia automática en disco: no requiere reindexar entre sesiones.  
- API sencilla compatible con el nivel de experiencia del equipo.  
- Open source, gratuita, sin límites de documentos para el tamaño del corpus.

**Consecuencias:**  
- No escala a millones de documentos, pero para 15–50 PDFs es más que suficiente.  
- La búsqueda vectorial pura es ligeramente menos eficiente que FAISS en datasets grandes.

---

## Decisión 2: Búsqueda híbrida (semántica + BM25)

**Contexto:**  
El RAG básico solo usa similitud semántica. En el dominio turístico del Eje Cafetero, los usuarios escriben nombres propios específicos (Salento, Valle del Cocora, Los Nevados) que pueden no aparecer en los embeddings de la misma forma.

**Decisión:**  
Se implementó búsqueda híbrida combinando embeddings (70%) con BM25 (30%).

**Razones:**  
- BM25 es excelente para coincidencias exactas de palabras clave y nombres propios.  
- La combinación reduce los falsos negativos cuando el nombre exacto no está semánticamente cercano.  
- BM25Okapi es ligero y no requiere una segunda base de datos.

**Consecuencias:**  
- Código más complejo en el retriever, pero con mejora medible en precisión.  
- Los pesos (70/30) son configurables y pueden ajustarse según evaluación.

---

## Decisión 3: Groq API con Llama 3.3

**Contexto:**  
El proyecto debe usar herramientas gratuitas. Las opciones eran: modelo local (Ollama), Google AI Studio o Groq.

**Decisión:**  
Se eligió Groq API con el modelo `llama-3.3-70b-versatile`.

**Razones:**  
- API gratuita con límite de 14,400 tokens/minuto — suficiente para demos y desarrollo.  
- Tiempo de respuesta < 1 segundo gracias al hardware especializado de Groq.  
- No requiere GPU local, funciona en cualquier computador.  
- Llama 3.3 70B tiene mejor desempeño en español que versiones anteriores.

**Consecuencias:**  
- Dependencia de conexión a internet durante el uso.  
- El límite gratuito puede agotarse con uso intensivo, pero no en condiciones normales del proyecto.

---

## Decisión 4: LangGraph para orquestación multiagente

**Contexto:**  
El sistema requiere dos agentes especializados (Buscador y Redactor) que deben ejecutarse en secuencia con estado compartido. Las opciones eran: llamada directa entre clases, LangChain AgentExecutor, o LangGraph.

**Decisión:**  
Se eligió LangGraph con un `StateGraph`.

**Razones:**  
- LangGraph modela el flujo como un grafo dirigido con estado tipado (`TypedDict`), lo que hace explícita la arquitectura multiagente.  
- Permite añadir nodos condicionales o bucles en el futuro sin reescribir la lógica de los agentes.  
- El estado compartido (`EstadoAsistente`) garantiza que los datos fluyan de forma controlada entre nodos.

**Consecuencias:**  
- Leve overhead de inicialización al compilar el grafo, imperceptible en la práctica.  
- Arquitectura más formal que una llamada directa, pero justificada por la claridad y extensibilidad.

---

## Decisión 5: MCP para información de clima en tiempo real

**Contexto:**  
El asistente debía integrarse con una fuente de datos externa en tiempo real. Se evaluó embeber la llamada a la API directamente en los agentes vs. encapsularla en un servidor MCP.

**Decisión:**  
Se implementó un servidor MCP (`weather_server.py`) que expone la herramienta `obtener_clima`, invocada desde `app.py` cuando el usuario menciona una ciudad del Eje Cafetero.

**Razones:**  
- MCP separa la lógica de la herramienta del agente que la usa, siguiendo el principio de responsabilidad única.  
- El servidor MCP es reutilizable: cualquier otro agente o aplicación puede consumirlo.  
- Demuestra comprensión del protocolo MCP (Model Context Protocol) en un caso real.

**Consecuencias:**  
- Requiere una API key de OpenWeatherMap (gratuita).  
- Si la key no está configurada, el clima simplemente no se muestra, sin romper la funcionalidad principal.
