"""
rag/retriever.py — Búsqueda híbrida: semántica (ChromaDB) + palabras clave (BM25)
Esta combinación mejora los resultados cuando el usuario escribe nombres propios
como "Salento", "Los Nevados" o "Valle del Cocora".
"""

import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
TOP_K = 4  # número de fragmentos a recuperar


class RetrieverHibrido:
    """Combina búsqueda semántica y BM25 para mejor precisión."""

    def __init__(self):
        self.modelo = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
        cliente = chromadb.PersistentClient(path=CHROMA_PATH)
        self.coleccion = cliente.get_collection("eje_cafetero")

        # Cargar todos los textos para BM25
        todos = self.coleccion.get(include=["documents", "metadatas"])
        self.textos    = todos["documents"]
        self.metadatas = todos["metadatas"]
        self.bm25 = BM25Okapi([t.lower().split() for t in self.textos])

    def buscar(self, pregunta: str) -> list[dict]:
        """
        Retorna los TOP_K fragmentos más relevantes combinando:
        - 70% peso a similitud semántica (embeddings)
        - 30% peso a coincidencia de palabras (BM25)
        """

        # ── Búsqueda semántica ─────────────────────────────────────────────
        embedding = self.modelo.encode(pregunta).tolist()
        resultados_semanticos = self.coleccion.query(
            query_embeddings=[embedding],
            n_results=TOP_K * 2,  # pedimos más para re-rankear
            include=["documents", "metadatas", "distances"],
        )

        # ── Búsqueda BM25 (palabras clave) ────────────────────────────────
        tokens_pregunta = pregunta.lower().split()
        scores_bm25 = self.bm25.get_scores(tokens_pregunta)

        # ── Combinar scores ───────────────────────────────────────────────
        ids_semanticos = resultados_semanticos["ids"][0]
        docs_semanticos = resultados_semanticos["documents"][0]
        meta_semanticos = resultados_semanticos["metadatas"][0]
        dist_semanticos = resultados_semanticos["distances"][0]

        combinados = []
        for i, doc_id in enumerate(ids_semanticos):
            # Score semántico: distancia coseno invertida (0=igual, 2=opuesto)
            score_sem = 1 - dist_semanticos[i]

            # Score BM25: buscar el índice del documento en la lista global
            try:
                idx_global = next(
                    j for j, m in enumerate(self.metadatas)
                    if m["fuente"] == meta_semanticos[i]["fuente"]
                    and m["chunk_id"] == meta_semanticos[i]["chunk_id"]
                )
                score_bm25_norm = scores_bm25[idx_global] / (max(scores_bm25) + 1e-8)
            except StopIteration:
                score_bm25_norm = 0.0

            score_final = 0.7 * score_sem + 0.3 * score_bm25_norm

            combinados.append({
                "texto": docs_semanticos[i],
                "fuente": meta_semanticos[i]["fuente"],
                "score": score_final,
            })

        # Ordenar por score final y devolver los TOP_K mejores
        combinados.sort(key=lambda x: x["score"], reverse=True)
        return combinados[:TOP_K]
