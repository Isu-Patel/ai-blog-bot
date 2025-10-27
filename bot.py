# ============================================
# 30 Days AI Blog Telegram Bot (Gemini + Auto 24h + Keep Alive)
# ============================================

import os
import json
import threading
import asyncio
from datetime import datetime, timedelta
from flask import Flask
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ----------------------------
# CONFIG: set your tokens here OR via environment variables
# ----------------------------
BOT_TOKEN = "8004004924:AAHSpHgeDGHGek69gCTvVLg1B-C9CuvdnSE"
GEMINI_API_KEY = "AIzaSyCASA0_4bI7CLjr9HOyb2eHJ3rALhyMF18"
# ----------------------------

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Topics
TOPICS = [
    "Python Basics", "Machine Learning", "Deep Learning", "Natural Language Processing",
    "Data Science", "Computer Vision", "Web Development with Flask", "API Integration",
    "Prompt Engineering", "Generative AI", "Neural Networks", "AI Ethics",
    "Automation with Python", "Chatbot Development", "Data Visualization",
    "AI in Healthcare", "AI in Education", "AI in Business", "AI in Robotics",
    "Reinforcement Learning", "AI & Creativity", "AI Tools Overview", "Voice Assistants",
    "Edge AI", "AI in Gaming", "AI Security", "AI in Finance", "AI Hardware",
    "AI Project Ideas", "Future of AI"
]

DATA_FILE = "user_progress.json"

# ----------------------------
# Persistence helpers
# ----------------------------
def load_progress():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_progress(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

progress = load_progress()  # { "user_id": {"day": int, "last_time": "iso"} }

def ensure_user(uid_str):
    if uid_str not in progress:
        progress[uid_str] = {"day": 1, "last_time": datetime.now().isoformat()}
        save_progress(progress)
    return progress[uid_str]

# ----------------------------
# AI generation (sync)
# ----------------------------
def generate_blog_sync(topic):
    prompt = (
        f"Write a well-formatted, engaging blog post (~250-500 words) about: {topic}. "
        "Include a catchy heading, 2–4 short paragraphs, and make it easy to understand."
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini Error:", e)
        return "⚠️ Sorry, I couldn’t generate the blog right now. Please try again later."

async def generate_blog(topic):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, generate_blog_sync, topic)

# ----------------------------
# Commands
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = ensure_user(uid)

    day = user["day"]
    topic = TOPICS[day - 1]

    await update.message.reply_text(f"📘 30 Days AI Blog Challenge\n\n📅 Day {day}: *{topic}*\n\nGenerating your blog...")
    blog = await generate_blog(topic)

    user["last_time"] = datetime.now().isoformat()
    save_progress(progress)
    await update.message.reply_text(blog)

async def regive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = ensure_user(uid)
    day = user["day"]
    topic = TOPICS[day - 1]

    await update.message.reply_text(f"🔄 Regenerating a new blog for Day {day}: *{topic}* ...")
    blog = await generate_blog(topic)
    await update.message.reply_text(blog)

async def nextday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = ensure_user(uid)

    user["day"] += 1
    if user["day"] > len(TOPICS):
        user["day"] = len(TOPICS)
        save_progress(progress)
        await update.message.reply_text("🎉 You’ve completed all 30 days! 🎉")
        return

    user["last_time"] = datetime.now().isoformat()
    save_progress(progress)

    day = user["day"]
    topic = TOPICS[day - 1]
    await update.message.reply_text(f"🌅 Moving to Day {day}: *{topic}*\n\nGenerating your blog...")
    blog = await generate_blog(topic)
    await update.message.reply_text(blog)

# ----------------------------
# ⏰ Background task: auto-advance every 24 hours
# ----------------------------
async def auto_nextday(app):
    while True:
        now = datetime.now()
        for uid, data in list(progress.items()):
            try:
                last = datetime.fromisoformat(data.get("last_time"))
            except Exception:
                last = now
            # If 24 hours passed, move user to next day automatically
            if now - last >= timedelta(hours=24) and data["day"] < len(TOPICS):
                data["day"] += 1
                data["last_time"] = now.isoformat()
                save_progress(progress)

                topic = TOPICS[data["day"] - 1]
                blog = await generate_blog(topic)
                try:
                    await app.bot.send_message(
                        chat_id=int(uid),
                        text=f"⏰ 24 hours have passed!\nHere’s your new blog for Day {data['day']}: *{topic}*"
                    )
                    await app.bot.send_message(chat_id=int(uid), text=blog)
                except Exception as e:
                    print(f"⚠️ Could not auto-send to {uid}: {e}")
        await asyncio.sleep(3600)  # Check every hour

# ----------------------------
# Flask keep-alive server
# ----------------------------
flask_app = Flask("")

@flask_app.route("/")
def home():
    return "🤖 AI Blog Bot is alive!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

# ----------------------------
# Main
# ----------------------------
def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("regive", regive))
    app.add_handler(CommandHandler("nextday", nextday))

    print("🤖 Bot is running... 24-hour auto-day updater active.")
    loop = asyncio.get_event_loop()
    loop.create_task(auto_nextday(app))
    app.run_polling()

if __name__ == "__main__":
    main()
