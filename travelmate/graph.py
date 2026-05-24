from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .agents import (
    formatter_agent,
    geo_agent,
    itinerary_agent,
    profile_agent,
    transport_agent,
    verification_agent,
)
from .models import PlannerState


def _profile_and_transport_fan_in(state: PlannerState) -> dict:
    """No-op fan-in node — both parallel branches have already written to state."""
    return {}


def build_graph():
    graph = StateGraph(PlannerState)

    # Nodes
    graph.add_node("profile_agent", profile_agent)
    graph.add_node("transport_agent", transport_agent)
    graph.add_node("fan_in", _profile_and_transport_fan_in)
    graph.add_node("geo_agent", geo_agent)
    graph.add_node("itinerary_agent", itinerary_agent)
    graph.add_node("verification_agent", verification_agent)
    graph.add_node("formatter_agent", formatter_agent)

    # profile_agent and transport_agent run in PARALLEL from START
    graph.add_edge(START, "profile_agent")
    graph.add_edge(START, "transport_agent")

    # Both converge at fan_in before geo_agent
    graph.add_edge("profile_agent", "fan_in")
    graph.add_edge("transport_agent", "fan_in")

    # Sequential from fan_in onwards
    graph.add_edge("fan_in", "geo_agent")
    graph.add_edge("geo_agent", "itinerary_agent")
    graph.add_edge("itinerary_agent", "verification_agent")
    graph.add_edge("verification_agent", "formatter_agent")
    graph.add_edge("formatter_agent", END)

    return graph.compile()
