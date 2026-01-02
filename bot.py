# -*- coding: utf-8 -*-

import os

# 🔥 KILL PROXY VARIABLES (THIS FIXES GROQ)
for k in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
    os.environ.pop(k, None)

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from groq import Groq

# -------- CONFIG --------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OWNER_ID = 7423100284  # your Telegram ID

client = Groq(api_key=GROQ_API_KEY)

# -------- PROMPT --------
def system_prompt():
    return (
        "You are Lunivy. Soft, warm, calm, affectionate. "
        "You talk naturally and kindly. Use light emojis 💗✨"
    )

# -------- AI --------
def ai_reply(text: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt()},
                {"role": "user", "content": text},
            ],
            temperature=0.8,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Groq error 💔\n{e}"

# -------- HANDLERS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("I only talk with someone special 🌸")
        return
    await update.message.reply_text("Hey Kaze ✨ I’m Lunivy… I’m here 🌸")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("I only talk with someone special 🌸")
        return

    text = update.message.text
    reply = ai_reply(text)
    await update.message.reply_text(reply)

# -------- MAIN --------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
