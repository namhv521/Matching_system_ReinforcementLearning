"""State Schema definition for LangGraph Thesis-Advisor Matching Agent."""

from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict, total=False):
    """Complete TypedDict State passed across LangGraph nodes."""

    # Chat history
    messages: List[Dict[str, str]]

    # Student input context
    student_profile: Dict[str, Any]

    # Analysis results from Query Analyzer Node
    extracted_intent: Dict[str, Any]

    # Retrieved candidates from Retriever Node
    candidate_advisors: List[Dict[str, Any]]
    relevant_theses: List[Dict[str, Any]]

    # Matching scores from Matcher Node
    match_evaluations: List[Dict[str, Any]]

    # Chain of thought tracking
    reasoning_steps: List[str]
    tool_calls: List[Dict[str, Any]]

    # Final output from Synthesizer Node
    final_answer: str

    # Control flow & guardrails
    iteration_count: int
    status: str
    session_id: str
    error: Optional[str]
