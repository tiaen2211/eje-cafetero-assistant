"""
agents/grafo.py — Orquestador LangGraph
Define el flujo multiagente: Buscador → Redactor con estado compartido.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END

from agents.buscador import AgentesBuscador
from agents.redactor import AgentesRedactor


class EstadoAsistente(TypedDict):
    """Estado compartido entre los agentes del grafo."""
    pregunta: str
    fragmentos: list[dict]
    respuesta: str


def nodo_buscador(estado: EstadoAsistente) -> EstadoAsistente:
    """Nodo 1: recupera fragmentos relevantes del corpus."""
    buscador = AgentesBuscador()
    fragmentos = buscador.buscar(estado["pregunta"])
    return {"fragmentos": fragmentos}


def nodo_redactor(estado: EstadoAsistente) -> EstadoAsistente:
    """Nodo 2: genera la respuesta citando las fuentes."""
    redactor = AgentesRedactor()
    respuesta = redactor.redactar(estado["pregunta"], estado["fragmentos"])
    return {"respuesta": respuesta}


def construir_grafo():
    """Construye y compila el grafo de agentes."""
    builder = StateGraph(EstadoAsistente)

    builder.add_node("buscador", nodo_buscador)
    builder.add_node("redactor", nodo_redactor)

    builder.set_entry_point("buscador")
    builder.add_edge("buscador", "redactor")
    builder.add_edge("redactor", END)

    return builder.compile()


# Grafo compilado (singleton)
grafo_asistente = construir_grafo()


def consultar(pregunta: str) -> tuple[str, list[dict]]:
    """
    Punto de entrada principal del sistema multiagente.

    Returns:
        (respuesta, fragmentos) — texto generado y fuentes usadas.
    """
    resultado = grafo_asistente.invoke({
        "pregunta": pregunta,
        "fragmentos": [],
        "respuesta": "",
    })
    return resultado["respuesta"], resultado["fragmentos"]
