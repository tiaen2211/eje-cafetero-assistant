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

## Decisión 3: Groq API con Llama 3.2

**Contexto:**  
El proyecto debe usar herramientas gratuitas. Las opciones eran: modelo local (Ollama), Google AI Studio o Groq.

**Decisión:**  
Se eligió Groq API con el modelo Llama 3.2.

**Razones:**  
- API gratuita con límite de 14,400 tokens/minuto — suficiente para demos y desarrollo.  
- Tiempo de respuesta < 1 segundo gracias al hardware especializado de Groq.  
- No requiere GPU local, funciona en cualquier computador.  
- Llama 3.2 tiene buen desempeño en español sin fine-tuning adicional.

**Consecuencias:**  
- Dependencia de conexión a internet durante el uso.  
- El límite gratuito puede agotarse con uso intensivo, pero no en condiciones normales del proyecto.
