

import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackContext
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Send me your symptoms and I'll return probable conditions and recommended next steps (educational only)."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send symptom text like: 'I have cough, fever, and shortness of breath for 2 days'")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    await update.message.reply_text("Processing your symptoms... (educational use only)")
    payload = {"text": txt, "user_id": str(update.effective_user.id)}
    try:
        r = requests.post(f"{API_URL.rstrip('/')}/symptom", json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        # Build message
        lines = []
        lines.append("*Probable conditions:*")
        conds = data.get("conditions", [])
        if conds:
            for c in conds[:3]:
                prob_txt = f" ({round(c.get('prob',0)*100)}%)" if c.get('prob') else ""
                reason = f" — {c.get('reason')}" if c.get('reason') else ""
                lines.append(f"- {c.get('condition')}{prob_txt}{reason}")
        else:
            lines.append("- (No probable conditions identified.)")
        lines.append("\n*Recommended next steps:*")
        lines.append(data.get("recommendations","(no recommendations)"))
        if data.get("follow_up"):
            lines.append("\n*Follow-up question:*")
            lines.append(data.get("follow_up"))
        lines.append("\n*Disclaimer:*")
        lines.append(data.get("disclaimer","This is educational only. Not medical advice."))
        message = "\n".join(lines)
        await update.message.reply_markdown(message)
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
