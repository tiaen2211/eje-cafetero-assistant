"""
agents/buscador.py — Agente 1: Buscador
Responsabilidad: recibir la pregunta del usuario y recuperar los fragmentos
más relevantes del corpus usando el RetrieverHibrido.
"""

from rag.retriever import RetrieverHibrido


class AgentesBuscador:
    """
    Agente especializado en recuperación de información.
    Usa búsqueda híbrida (semántica + BM25) sobre ChromaDB.
    """

    def __init__(self):
        self.retriever = RetrieverHibrido()

    def buscar(self, pregunta: str) -> list[dict]:
        """
        Recibe la pregunta del usuario y devuelve los fragmentos relevantes.

        Args:
            pregunta: Texto en lenguaje natural del usuario.

        Returns:
            Lista de dicts con 'texto', 'fuente' y 'score'.
        """
        print(f"[Agente Buscador] Buscando: '{pregunta}'")
        fragmentos = self.retriever.buscar(pregunta)
        print(f"[Agente Buscador] Encontrados {len(fragmentos)} fragmentos.")
        return fragmentos
