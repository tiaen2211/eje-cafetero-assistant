"""
rag/ingestor.py — Carga los documentos PDF y los indexa en ChromaDB
Ejecutar UNA SOLA VEZ antes de arrancar la app:
    python src/rag/ingestor.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()

DATA_PATH   = os.getenv("DATA_PATH",   "./data/documentos")
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
CHUNK_SIZE  = 500   # tokens aprox. por fragmento
CHUNK_OVERLAP = 50  # tokens de solapamiento entre fragmentos


def leer_pdf(ruta: Path) -> str:
    """Extrae todo el texto de un PDF."""
    reader = PdfReader(ruta)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def dividir_en_chunks(texto: str, fuente: str) -> list[dict]:
    """Divide el texto en fragmentos con solapamiento."""
    palabras = texto.split()
    chunks = []
    i = 0
    idx = 0
    while i < len(palabras):
        chunk_palabras = palabras[i : i + CHUNK_SIZE]
        chunks.append({
            "texto": " ".join(chunk_palabras),
            "fuente": fuente,
            "chunk_id": idx,
        })
        i += CHUNK_SIZE - CHUNK_OVERLAP
        idx += 1
    return chunks


def indexar_documentos():
    """Proceso completo: lee PDFs → divide → embeddings → guarda en ChromaDB."""

    # Modelo de embeddings multilingüe (funciona bien con español)
    print("Cargando modelo de embeddings...")
    modelo = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

    # Conexión a ChromaDB
    cliente = chromadb.PersistentClient(path=CHROMA_PATH)
    coleccion = cliente.get_or_create_collection(
        name="eje_cafetero",
        metadata={"hnsw:space": "cosine"},
    )

    # Leer todos los PDFs de la carpeta data/documentos/
    carpeta = Path(DATA_PATH)
    pdfs = list(carpeta.glob("*.pdf"))
    print(f"Encontrados {len(pdfs)} documentos PDF.")

    todos_los_chunks = []
    for pdf in pdfs:
        print(f"  Procesando: {pdf.name}")
        texto = leer_pdf(pdf)
        chunks = dividir_en_chunks(texto, fuente=pdf.name)
        todos_los_chunks.extend(chunks)

    print(f"Total de fragmentos: {len(todos_los_chunks)}")

    # Generar embeddings e indexar en lotes
    textos   = [c["texto"]  for c in todos_los_chunks]
    ids      = [f"{c['fuente']}_chunk{c['chunk_id']}" for c in todos_los_chunks]
    metadatas = [{"fuente": c["fuente"], "chunk_id": c["chunk_id"]} for c in todos_los_chunks]

    print("Generando embeddings (puede tardar unos minutos la primera vez)...")
    embeddings = modelo.encode(textos, show_progress_bar=True).tolist()

    coleccion.upsert(
        documents=textos,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
    )
    print("✅ Indexación completada. ChromaDB listo en:", CHROMA_PATH)


if __name__ == "__main__":
    indexar_documentos()
