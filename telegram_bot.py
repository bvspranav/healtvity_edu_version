import os
import logging
import requests
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import config

load_dotenv()

API_URL = os.getenv("API_URL", config.API_URL)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", config.TELEGRAM_TOKEN)

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not set in env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def escape_markdown(text: str) -> str:
    """
    Escape Telegram MarkdownV2 special characters.
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Send me your symptoms and I'll return probable conditions and recommended next steps (educational only)."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send symptom text like: 'I have cough, fever, and shortness of breath for 2 days'"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    await update.message.reply_text("Processing your symptoms... (educational use only)")
    payload = {"text": txt, "user_id": str(update.effective_user.id)}
    try:
        r = requests.post(f"{API_URL.rstrip('/')}/symptom", json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()

        # Build message sections
        lines = []

        # Probable Conditions
        lines.append("*Probable conditions:*")
        conds = data.get("conditions", [])
        if conds:
            for c in conds[:3]:
                prob_txt = f" ({round(c.get('prob',0)*100)}%)" if c.get('prob') else ""
                reason = f" — {c.get('reason')}" if c.get('reason') else ""
                lines.append(f"- {c.get('condition')}{prob_txt}{reason}")
        else:
            lines.append("- (No probable conditions identified.)")

        # Recommendations
        recs = data.get("recommendations", "").strip()
        if recs:
            lines.append("\n*Recommended next steps:*")
            # Split into bullet points if there are numbered steps
            rec_lines = re.split(r"\n\d+\. ", recs)
            for rl in rec_lines:
                rl = rl.strip()
                if rl:
                    lines.append(f"- {rl}")

        # Follow-up
        follow_up = data.get("follow_up", "").strip()
        if follow_up:
            lines.append("\n*Follow-up question:*")
            lines.append(f"- {follow_up}")

        # Disclaimer
        disclaimer = data.get("disclaimer", "This is educational only. Not medical advice.")
        lines.append("\n*Disclaimer:*")
        lines.append(f"- {disclaimer}")

        message = "\n".join(lines)
        # Escape for MarkdownV2
        await update.message.reply_markdown_v2(escape_markdown(message))

    except Exception as e:
        logging.exception("Error calling API")
        await update.message.reply_text(f"Sorry, there was an error: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Bot started. Press Ctrl-C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
