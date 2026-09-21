"""Agent Tools package export."""

from src.agents.tools.advisor_tools import search_advisors, check_advisor_capacity
from src.agents.tools.thesis_tools import search_past_theses, suggest_thesis_topics
from src.agents.tools.matching_tools import (
    compute_compatibility_score,
    get_matching_system_benchmarks,
)

ALL_AGENT_TOOLS = [
    search_advisors,
    check_advisor_capacity,
    search_past_theses,
    suggest_thesis_topics,
    compute_compatibility_score,
    get_matching_system_benchmarks,
]

__all__ = [
    "search_advisors",
    "check_advisor_capacity",
    "search_past_theses",
    "suggest_thesis_topics",
    "compute_compatibility_score",
    "get_matching_system_benchmarks",
    "ALL_AGENT_TOOLS",
]
