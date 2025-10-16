import os
import time
from typing import Dict, Any, Optional, List
import requests
import config

# Flag for Gemini usage
_USE_GEMINI = getattr(config, "USE_GEMINI", False)
GEMINI_API_KEY = getattr(config, "GEMINI_API_KEY", None)

SYSTEM_PROMPT = (
    "You are an assistant specialized in medical-symptom triage for educational purposes only. "
    "When given symptom text, respond with: (1) a short ranked list of probable conditions (3 max) with brief reasons and estimated probability, "
    "(2) recommended next steps (tests to consider, when to seek emergency care, conservative self-care), and "
    "(3) a short follow-up question if more data is needed. ALWAYS include a clear educational disclaimer that this is not medical advice and advise to seek professional care when needed."
)

def build_prompt(symptom_text: str, additional_context: Optional[str] = None) -> List[Dict[str, str]]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Patient says: {symptom_text}"}
    ]
    if additional_context:
        messages.append({"role": "user", "content": f"Context: {additional_context}"})
    return messages

def parse_llm_output(raw_text: str) -> Dict[str, Any]:
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    conditions = []
    rec_lines = []
    follow_up = None
    mode = None
    for ln in lines:
        lower = ln.lower()
        if lower.startswith("probable") or lower.startswith("possible") or "conditions" in lower:
            mode = "conditions"
            continue
        if lower.startswith("recommend") or "next step" in lower or "recommendations" in lower:
            mode = "recommendations"
            continue
        if lower.startswith("follow") or "question" in lower:
            mode = "followup"
            continue

        if mode == "conditions":
            import re
            m = re.match(r"^\d+[\.\)]?\s*([\w\s\-/]+?)\s*(?:[—:-]\s*([\d\.%]+))?\s*(?:[—:-]\s*(.+))?$", ln)
            if m:
                name = m.group(1).strip()
                prob_raw = m.group(2)
                reason = m.group(3) or ""
                prob = None
                if prob_raw:
                    if "%" in prob_raw:
                        prob = float(prob_raw.replace("%",""))/100.0
                    else:
                        try:
                            prob = float(prob_raw)
                            if prob > 1:
                                prob = prob/100.0
                        except Exception:
                            prob = None
                conditions.append({"condition": name, "prob": prob if prob is not None else None, "reason": reason})
            else:
                conditions.append({"condition": ln, "prob": None, "reason": ""})
        elif mode == "recommendations":
            rec_lines.append(ln)
        elif mode == "followup":
            follow_up = (follow_up + " " + ln) if follow_up else ln
        else:
            if "%" in ln or "probable" in ln.lower():
                conditions.append({"condition": ln, "prob": None, "reason": ""})
            else:
                rec_lines.append(ln)

    recommendations = "\n".join(rec_lines).strip()
    return {"conditions": conditions or [], "recommendations": recommendations, "follow_up": follow_up}

def call_gemini_llm(symptom_text: str, additional_context: Optional[str] = None) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in config.py")
    
    prompt_text = symptom_text
    if additional_context:
        prompt_text += f"\nContext: {additional_context}"
    
    url = "https://gemini.googleapis.com/v1/models/gemini-2.5-pro:predict"
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "instances": [
            {"input": {"text": prompt_text}}
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    # Adjust depending on Gemini response format
    result_json = response.json()
    try:
        output_text = result_json["predictions"][0]["content"][0]["text"]
    except Exception:
        output_text = "ERROR: Unexpected Gemini response format."
    
    return output_text

def call_llm(symptom_text: str, additional_context: Optional[str] = None) -> Dict[str, Any]:
    raw = ""
    if _USE_GEMINI:
        try:
            raw = call_gemini_llm(symptom_text, additional_context)
        except Exception as e:
            raw = f"ERROR: LLM call failed: {str(e)}"
    else:
        # fallback heuristic
        raw = (
            "Probable conditions:\n"
            "1. Viral upper respiratory infection — 60% — common symptoms include cough, runny nose.\n\n"
            "Recommendations:\n"
            "- Rest, fluids, OTC symptomatic care. Seek care if high fever, breathing difficulty.\n\n"
            "Follow-up question:\n"
            "- How long have the symptoms lasted? Any shortness of breath or chest pain?\n\n"
            "Disclaimer: This is educational information only and is NOT medical advice."
        )
    
    parsed = parse_llm_output(raw)
    parsed["raw"] = raw
    parsed["disclaimer"] = (
        "This output is for educational purposes only and is NOT medical advice. "
        "If the person is experiencing severe or worsening symptoms (chest pain, severe shortness of breath, sudden weakness, altered consciousness, severe bleeding), seek emergency care immediately."
    )
    return parsed
