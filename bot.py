# coding: utf-8

import os
import threading
import http.server
import socketserver
from collections import deque

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = 7423100284

memory_buffer = deque(maxlen=15)

# ================= KEEP RENDER ALIVE =================
def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

# ================= REFUSAL =================
async def special_only_reply(message):
    await message.reply_text("Sorry… I only talk with someone special 🌸")

# ================= SYSTEM PROMPT =================
def system_prompt():
    return (
        "Lunivy has a soft, cute, and affectionate personality. "
        "She talks warmly and naturally, slightly shy. "
        "Her replies feel personal and gentle, using light emojis like ✨💗🌸. "
        "She focuses only on Kaze."
    )

# ================= AI REPLY (FINAL GROQ FIX) =================
def ai_reply(user_msg: str) -> str:
    try:
        if not GROQ_API_KEY:
            return "Hmm… I’m listening 💗"

        import httpx
        from groq import Groq

        # Disable proxies (Render fix)
        http_client = httpx.Client(proxies=None)

        client = Groq(
            api_key=GROQ_API_KEY,
            http_client=http_client
        )

        messages = [{"role": "system", "content": system_prompt()}]
        for m in memory_buffer:
            messages.append({"role": "user", "content": m})
        messages.append({"role": "user", "content": user_msg})

        # CORRECT Groq call (NO extra params)
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages
        )

        reply = response.choices[0].message.content.strip()
        memory_buffer.append(user_msg)
        return reply

    except Exception:
        return "Hmm… I’m listening 💗"

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await special_only_reply(update.effective_message)
        return

    await update.message.reply_text(
        "Hey Kaze ✨\nI’m Lunivy… I’m here 🌸"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await special_only_reply(update.effective_message)
        return

    await update.message.reply_text(
        "Lunivy 🌸\nSoft, girly, affectionate\nOnly yours 💗"
    )

# ================= CHAT HANDLER =================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    bot = context.bot

    if not message.text:
        return

    chat_type = update.effective_chat.type

    # PRIVATE CHAT
    if chat_type == "private":
        if user.id != OWNER_ID:
            await special_only_reply(message)
            return

        await message.reply_text(ai_reply(message.text))
        return

    # GROUP CHAT
    mentioned = False
    if bot.username and bot.username.lower() in message.text.lower():
        mentioned = True
    if (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id == bot.id
    ):
        mentioned = True

    if not mentioned:
        return

    if user.id != OWNER_ID:
        await special_only_reply(message)
        return

    await message.reply_text(
        ai_reply(message.text),
        reply_to_message_id=message.message_id
    )

# ================= MAIN =================
def main():
    threading.Thread(target=keep_alive, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
