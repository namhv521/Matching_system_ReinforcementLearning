"""Hook and logging utility for capturing AI interactions, prompts, tools, and token metrics."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

LOGS_DIR = Path(__file__).resolve().parents[1] / "logs" / "agent"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG_FILE = LOGS_DIR / "agent_interactions.jsonl"


def log_agent_interaction(
    session_id: str,
    user_prompt: str,
    agent_response: str,
    tools_used: list,
    duration_ms: float,
    model_name: str = "mock",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Writes an interaction entry to the append-only JSONL log."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "model_name": model_name,
        "prompt": user_prompt,
        "response": agent_response,
        "tools_count": len(tools_used),
        "tools_executed": tools_used,
        "duration_ms": duration_ms,
        "metadata": metadata or {},
    }

    try:
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[Error logging AI interaction]: {e}")

    return entry


if __name__ == "__main__":
    # Self-test log hook
    test_entry = log_agent_interaction(
        session_id="test-session-001",
        user_prompt="Tìm giảng viên hướng dẫn về NLP",
        agent_response="Đã đề xuất PGS.TS Nguyễn Văn A",
        tools_used=["search_advisors", "check_advisor_capacity"],
        duration_ms=120.5,
        model_name="mock",
    )
    print(f"Recorded test audit entry: {test_entry['session_id']} at {test_entry['timestamp']}")
