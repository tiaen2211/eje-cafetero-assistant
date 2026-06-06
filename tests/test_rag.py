"""
tests/test_rag.py — Pruebas básicas del pipeline RAG
Ejecutar con: python -m pytest tests/
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestRetriever:
    """Pruebas del RetrieverHibrido."""

    def test_busqueda_retorna_lista(self):
        """La búsqueda debe retornar una lista."""
        from rag.retriever import RetrieverHibrido
        retriever = RetrieverHibrido()
        resultado = retriever.buscar("qué hacer en Salento")
        assert isinstance(resultado, list)

    def test_busqueda_retorna_max_4(self):
        """La búsqueda no debe retornar más de TOP_K=4 resultados."""
        from rag.retriever import RetrieverHibrido
        retriever = RetrieverHibrido()
        resultado = retriever.buscar("gastronomía del Eje Cafetero")
        assert len(resultado) <= 4

    def test_cada_resultado_tiene_campos(self):
        """Cada fragmento debe tener 'texto', 'fuente' y 'score'."""
        from rag.retriever import RetrieverHibrido
        retriever = RetrieverHibrido()
        resultado = retriever.buscar("Valle del Cocora")
        for r in resultado:
            assert "texto"  in r
            assert "fuente" in r
            assert "score"  in r

    def test_scores_entre_0_y_1(self):
        """Los scores deben estar en el rango [0, 1]."""
        from rag.retriever import RetrieverHibrido
        retriever = RetrieverHibrido()
        resultado = retriever.buscar("parques naturales")
        for r in resultado:
            assert 0.0 <= r["score"] <= 1.0
