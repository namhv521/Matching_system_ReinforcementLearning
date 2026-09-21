"""LangGraph State Graph definition for the Thesis-Advisor Matching Agent."""

import uuid
import time
from typing import Dict, Any, Optional, AsyncGenerator

from src.agents.state import AgentState
from src.agents.nodes.query_analyzer import analyze_query_node
from src.agents.nodes.retriever import retrieve_data_node
from src.agents.nodes.matcher import evaluate_matching_node
from src.agents.nodes.synthesizer import synthesize_response_node

try:
    from langgraph.graph import StateGraph, START, END
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False


def build_matching_graph():
    """Builds and compiles the LangGraph StateGraph."""
    if HAS_LANGGRAPH:
        workflow = StateGraph(AgentState)

        # Add Nodes
        workflow.add_node("analyze_query", analyze_query_node)
        workflow.add_node("retrieve_data", retrieve_data_node)
        workflow.add_node("evaluate_matching", evaluate_matching_node)
        workflow.add_node("synthesize_response", synthesize_response_node)

        # Add Edges
        workflow.add_edge(START, "analyze_query")
        workflow.add_edge("analyze_query", "retrieve_data")
        workflow.add_edge("retrieve_data", "evaluate_matching")
        workflow.add_edge("evaluate_matching", "synthesize_response")
        workflow.add_edge("synthesize_response", END)

        return workflow.compile()
    return None


# Compiled global graph instance (or None if fallback runner)
compiled_graph = build_matching_graph()


def run_matching_agent(
    query: str,
    student_profile: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
) -> AgentState:
    """Executes the full AI Agent pipeline on student query and profile."""
    sid = session_id or str(uuid.uuid4())
    initial_state: AgentState = {
        "messages": [{"role": "user", "content": query}],
        "student_profile": student_profile or {},
        "extracted_intent": {},
        "candidate_advisors": [],
        "relevant_theses": [],
        "match_evaluations": [],
        "reasoning_steps": [],
        "tool_calls": [],
        "final_answer": "",
        "iteration_count": 1,
        "status": "init",
        "session_id": sid,
        "error": None,
    }

    if HAS_LANGGRAPH and compiled_graph is not None:
        try:
            return compiled_graph.invoke(initial_state)
        except Exception:
            pass

    # High-reliability standalone sequential execution
    state = dict(initial_state)
    state.update(analyze_query_node(state))
    state.update(retrieve_data_node(state))
    state.update(evaluate_matching_node(state))
    state.update(synthesize_response_node(state))
    return state


async def astream_matching_agent(
    query: str,
    student_profile: Optional[Dict[str, Any]] = None
) -> AsyncGenerator[str, None]:
    """Streams thought process and final response chunks."""
    state = run_matching_agent(query, student_profile)

    # Stream reasoning thoughts
    for step in state.get("reasoning_steps", []):
        yield f"data: {{\"type\": \"thought\", \"content\": \"{step}\"}}\n\n"
        time.sleep(0.02)

    # Stream final response tokens
    answer = state.get("final_answer", "")
    words = answer.split(" ")
    for word in words:
        yield f"data: {{\"type\": \"token\", \"content\": \"{word} \"}}\n\n"
        time.sleep(0.01)

    yield f"data: {{\"type\": \"done\", \"status\": \"completed\"}}\n\n"
