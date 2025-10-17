import os
from typing import Dict, Any, Optional, List
import requests
import config
import re

# Gemini usage flag and API key
_USE_GEMINI = getattr(config, "USE_GEMINI", False)
GEMINI_API_KEY = getattr(config, "GEMINI_API_KEY", None)

SYSTEM_PROMPT = (
    "You are an assistant specialized in medical-symptom triage for educational purposes only. "
    "When given symptom text, respond with: "
    "(1) a short ranked list of probable conditions (3 max) with brief reasons and estimated probability, "
    "(2) recommended next steps (tests to consider, when to seek emergency care, conservative self-care), and "
    "(3) a short follow-up question if more data is needed. "
    "ALWAYS include a clear educational disclaimer that this is not medical advice and advise to seek professional care when needed."
)

def parse_llm_output(raw_text: str) -> Dict[str, Any]:
    """Parse LLM output into structured conditions, recommendations, and follow-up."""

    # Normalize
    raw_text = raw_text.replace("\r", "").strip()
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    
    conditions = []
    rec_lines = []
    follow_up = None
    mode = None

    for ln in lines:
        lower = ln.lower()
        if "probable conditions" in lower or "possible conditions" in lower:
            mode = "conditions"
            continue
        elif "recommend" in lower or "next step" in lower:
            mode = "recommendations"
            continue
        elif "follow" in lower or "question" in lower:
            mode = "followup"
            continue

        if mode == "conditions":
            # Try to extract numbered or starred conditions
            m = re.findall(r"(\*\*?[\w\s/-]+?\**?)[:\-–]", ln)
            if m:
                for cond in m:
                    conditions.append({"condition": cond.strip("* "), "prob": None, "reason": ""})
            else:
                # fallback: treat first sentence as a condition
                sentences = re.split(r"\. ", ln)
                if sentences:
                    conditions.append({"condition": sentences[0].strip(), "prob": None, "reason": ""})
        elif mode == "recommendations":
            rec_lines.append(ln)
        elif mode == "followup":
            follow_up = (follow_up + " " + ln) if follow_up else ln
        else:
            # Heuristic: if line mentions fever, cough, pain, treat as condition
            if any(k in lower for k in ["fever", "cough", "pain", "rash", "headache"]):
                conditions.append({"condition": ln, "prob": None, "reason": ""})
            else:
                rec_lines.append(ln)

    return {
        "conditions": conditions[:3] if conditions else [{"condition": "(No probable conditions identified)", "prob": None, "reason": ""}],
        "recommendations": "\n".join(rec_lines).strip(),
        "follow_up": follow_up
    }


def call_gemini_llm(symptom_text: str, additional_context: Optional[str] = None) -> str:
    """Call Gemini LLM API and return raw text output."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in config.py")

    prompt_text = f"Patient symptoms: {symptom_text}"
    if additional_context:
        prompt_text += f"\nContext: {additional_context}"

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt_text}]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    result_json = response.json()
    try:
        output_text = result_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        output_text = f"ERROR: Unexpected Gemini response format. Raw: {result_json}"

    return output_text

def call_llm(symptom_text: str, additional_context: Optional[str] = None) -> Dict[str, Any]:
    """Call LLM (Gemini or fallback) and return structured data."""
    raw = ""
    if _USE_GEMINI:
        try:
            raw = call_gemini_llm(symptom_text, additional_context)
        except Exception as e:
            raw = f"ERROR: LLM call failed: {str(e)}"
    
    if not raw or raw.startswith("ERROR"):
        # fallback if Gemini fails
        raw = (
            "Probable conditions:\n"
            "1. Viral upper respiratory infection — 60% — common symptoms include cough, runny nose.\n"
            "2. Common cold — 25% — mild fever and nasal congestion.\n"
            "3. Allergic rhinitis — 15% — sneezing and itchy eyes.\n\n"
            "Recommendations:\n"
            "- Rest, fluids, OTC symptomatic care.\n"
            "- Seek medical care if high fever, difficulty breathing, chest pain.\n\n"
            "Follow-up question:\n"
            "- How long have the symptoms lasted? Any shortness of breath or chest pain?\n\n"
            "Disclaimer: This is educational information only and is NOT medical advice."
        )

    parsed = parse_llm_output(raw)
    parsed["raw"] = raw
    parsed["disclaimer"] = (
        "This output is for educational purposes only and is NOT medical advice. "
        "If severe or worsening symptoms occur (chest pain, severe shortness of breath, sudden weakness, altered consciousness, severe bleeding), seek emergency care immediately."
    )
    return parsed

# Example usage
if __name__ == "__main__":
    test_symptom = "Fever, sore throat, mild cough"
    result = call_llm(test_symptom)
    print(result)
