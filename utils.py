from typing import Optional
from schemas import SymptomRequest
import re

def normalize_text(text: str) -> str:
    t = text.strip()
    # minimal normalization; expand as needed
    t = re.sub(r"\s+", " ", t)
    return t

def needs_more_info(parsed: dict) -> bool:
    # Simple heuristic: if follow_up present then needs more info
    if parsed.get("follow_up"):
        return True
    # Also if conditions empty or recommendations too short
    conds = parsed.get("conditions", [])
    if not conds:
        return True
    return False
