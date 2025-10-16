# healtvity_edu_version
Healthcare Symptom Checker (Educational) is an AI-powered tool designed to assist users in understanding their symptoms and exploring possible conditions in an educational context. By leveraging Large Language Models (LLMs) such as Gemini and fine-tuning it using the medical data. When the user enters the text in the interface LLM analyzes the text and identifies key symptoms and using the fine-tuned model the system analyzes symptom descriptions provided by users and generates a structured response including:

          1. Probable Conditions – A ranked list of possible conditions with estimated probabilities and reasoning.

          2. Recommendations – Suggested next steps, including tests, self-care, and advice on when to seek professional care.

          3. Follow-up Questions – Short prompts to collect additional information for more accurate symptom analysis.

          4. Educational Disclaimer – Clear warnings emphasizing that the tool is not medical advice.

Perfect! Here's a **GitHub-ready, concise, professional README** with badges and sections optimized for a repo landing page:

# 🩺 Healthcare Symptom Checker (Educational)

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.119.0-green)](https://fastapi.tiangolo.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue)](https://core.telegram.org/bots)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

An educational symptom checker powered by LLMs (OpenAI / Gemini) to provide probable conditions, recommendations, and follow-ups based on user-reported symptoms.  

> ⚠️ Disclaimer: This tool is for educational purposes only. Not a substitute for professional medical advice.

## 🚀 Features

- Predicts **probable conditions** from symptom text
- Provides **recommendations and next steps**
- Suggests **follow-up questions**
- Stores query **history**
- Works via:
  - **FastAPI REST API**
  - **Telegram bot**
- Supports **multiple LLMs**: OpenAI GPT, Gemini, or offline heuristics

## 🎯 Demo

**API endpoint**: `/symptom`  

**Example request**:

```bash
curl -X POST "http://127.0.0.1:8000/symptom" \
-H "Content-Type: application/json" \
-d '{"text": "I have cough and fever", "user_id": "test_user"}'
````

**Sample response**:

```json
{
  "conditions": [
    {
      "condition": "Viral upper respiratory infection",
      "prob": 0.6,
      "reason": "common symptoms include cough, runny nose."
    }
  ],
  "recommendations": "- Rest, fluids, OTC symptomatic care. Seek care if high fever, breathing difficulty.",
  "follow_up": "- How long have the symptoms lasted? Any shortness of breath or chest pain?",
  "disclaimer": "This output is for educational purposes only and is NOT medical advice."
}
```

## ⚙️ Installation

```bash
# Clone repo
git clone https://github.com/yourusername/healthcare-symptom-checker.git
cd "Health Care Symptom Checker"

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_TOKEN=your_telegram_bot_token
API_URL=http://127.0.0.1:8000
USE_OPENAI=True
USE_GEMINI=False
```

## 🏃 Running

**Start FastAPI server**:

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Start Telegram bot** (ensure API server is running):

```bash
python telegram_bot.py
```


## 🔄 Switching LLMs

* OpenAI GPT-3.5 / GPT-4 → set `USE_OPENAI=True`
* Gemini LLM → set `USE_GEMINI=True`
* Offline heuristic fallback → default if no LLM key is provided

## 🧰 Project Structure

Health Care Symptom Checker/
├── data  # data used for model fine-tuning
├── main.py             # FastAPI server
├── telegram_bot.py     # Telegram bot interface
├── llm_client.py       # LLM integration
├── schemas.py          # Request/response models
├── storage.py          # JSON storage for query history
├── config.py           # Settings & API keys
├── train.jsonl         # Optional fine-tuning dataset
└── .env                # Environment variables


## ⚠️ Disclaimer

This project is **educational only**. **Not medical advice**.
Seek professional care for severe or worsening symptoms (chest pain, shortness of breath, altered consciousness, severe bleeding).


