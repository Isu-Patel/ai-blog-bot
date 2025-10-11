# # ============================================
# # 30 Days AI Blog Telegram Bot (Gemini + Keep Alive)
# # ============================================

# import google.generativeai as genai
# from telegram import Update
# from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
# from datetime import datetime, timedelta
# from flask import Flask
# import threading

# # ============================================
# # 🔑 TOKENS
# # ============================================
# BOT_TOKEN = "8004004924:AAHSpHgeDGHGek69gCTvVLg1B-C9CuvdnSE"
# GEMINI_API_KEY = "AIzaSyCASA0_4bI7CLjr9HOyb2eHJ3rALhyMF18"
# # ============================================

# # Configure Gemini
# genai.configure(api_key=GEMINI_API_KEY)
# model = genai.GenerativeModel("gemini-2.0-flash")

# # --- 30 Topics ---
# TOPICS = [
#     "Python Basics", "Machine Learning", "Deep Learning", "Natural Language Processing",
#     "Data Science", "Computer Vision", "Web Development with Flask", "API Integration",
#     "Prompt Engineering", "Generative AI", "Neural Networks", "AI Ethics",
#     "Automation with Python", "Chatbot Development", "Data Visualization",
#     "AI in Healthcare", "AI in Education", "AI in Business", "AI in Robotics",
#     "Reinforcement Learning", "AI & Creativity", "AI Tools Overview", "Voice Assistants",
#     "Edge AI", "AI in Gaming", "AI Security", "AI in Finance", "AI Hardware",
#     "AI Project Ideas", "Future of AI"
# ]

# # --- Track user progress ---
# user_day = {}
# last_blog = {}
# last_time = {}

# # --- AI Blog Generation ---
# def generate_blog(topic):
#     prompt = f"Write a well-formatted 250-word blog post with headings and short paragraphs about '{topic}'."
#     try:
#         response = model.generate_content(prompt)
#         return response.text.strip()
#     except Exception as e:
#         print("❌ Gemini Error:", e)
#         return "⚠️ Sorry, I couldn’t generate the blog right now. Please try again later."

# # --- /start command ---
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     user_day[user_id] = 1
#     last_time[user_id] = datetime.now()

#     topic = TOPICS[0]
#     await update.message.reply_text(f"📘 30 Days AI Blog Challenge\n\n📅 Day 1: *{topic}*\n\nGenerating your blog...")

#     blog = generate_blog(topic)
#     last_blog[user_id] = blog
#     await update.message.reply_text(blog)

# # --- /regive command ---
# async def regive(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     day = user_day.get(user_id, 1)
#     topic = TOPICS[day - 1]
#     await update.message.reply_text(f"🔄 Regenerating a new blog for *Day {day}: {topic}*...")

#     blog = generate_blog(topic)
#     last_blog[user_id] = blog
#     await update.message.reply_text(blog)

# # --- /nextday command ---
# async def nextday(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     now = datetime.now()

#     # If 24 hours passed, move to next day
#     if user_id in last_time and now - last_time[user_id] >= timedelta(hours=24):
#         user_day[user_id] = user_day.get(user_id, 1) + 1
#         last_time[user_id] = now
#     elif user_id not in user_day:
#         user_day[user_id] = 1
#         last_time[user_id] = now

#     if user_day[user_id] > len(TOPICS):
#         await update.message.reply_text("🎉 You’ve completed all 30 days! Great job!")
#         return

#     day = user_day[user_id]
#     topic = TOPICS[day - 1]
#     await update.message.reply_text(f"🌅 Day {day}: *{topic}*\n\nGenerating your blog...")

#     blog = generate_blog(topic)
#     last_blog[user_id] = blog
#     await update.message.reply_text(blog)

# # --- Flask Keep Alive ---
# app = Flask('')

# @app.route('/')
# def home():
#     return "🤖 Telegram Bot is alive!"

# def run():
#     app.run(host="0.0.0.0", port=8080)

# def keep_alive():
#     thread = threading.Thread(target=run)
#     thread.start()

# # --- Main Bot Setup ---
# def main():
#     keep_alive()  # ✅ Keeps bot running 24/7
#     app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
#     app_bot.add_handler(CommandHandler("start", start))
#     app_bot.add_handler(CommandHandler("regive", regive))
#     app_bot.add_handler(CommandHandler("nextday", nextday))

#     print("🤖 Bot is running... try sending /start in Telegram.")
#     app_bot.run_polling()

# if __name__ == "__main__":
#     main()
# bot.py
# 30 Days AI Blog Telegram Bot (fixed nextday + persistence + keep_alive)

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
BOT_TOKEN = os.getenv("8004004924:AAHSpHgeDGHGek69gCTvVLg1B-C9CuvdnSE")
GEMINI_API_KEY = os.getenv("AIzaSyCASA0_4bI7CLjr9HOyb2eHJ3rALhyMF18")
# ----------------------------

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")  # or gemini-2.0/1.5 depending on access

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
# AI generation (blocking) — keep sync for genai, will run in executor
# ----------------------------
def generate_blog_sync(topic):
    prompt = (
        f"Write a well-formatted, engaging blog post (~250-500 words) about: {topic}. "
        "Include a short heading and 2-4 short paragraphs. Make it easy-to-read and informative."
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
# Command handlers
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = ensure_user(uid)

    # auto-advance if 24+ hours passed since last_time
    try:
        last = datetime.fromisoformat(user.get("last_time"))
    except Exception:
        last = datetime.now()
    now = datetime.now()
    if (now - last) >= timedelta(hours=24):
        # Only auto-increment up to length limit
        if user["day"] < len(TOPICS):
            user["day"] += 1
            user["last_time"] = now.isoformat()
            save_progress(progress)

    day = user["day"]
    topic = TOPICS[max(0, min(day - 1, len(TOPICS) - 1))]

    await update.message.reply_text(f"📘 30 Days AI Blog Challenge\n\n📅 Day {day}: *{topic}*\n\nGenerating your blog...")
    blog = await generate_blog(topic)
    # update last_time when we deliver a blog
    user["last_time"] = datetime.now().isoformat()
    save_progress(progress)

    await update.message.reply_text(blog)

async def regive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = ensure_user(uid)
    day = user["day"]
    topic = TOPICS[max(0, min(day - 1, len(TOPICS) - 1))]

    await update.message.reply_text(f"🔄 Regenerating a new blog for Day {day}: *{topic}* ...")
    blog = await generate_blog(topic)
    # Do NOT change day or last_time on regive — preserves ability to auto-advance on real 24h
    await update.message.reply_text(blog)

async def nextday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    user = ensure_user(uid)

    # Increment day by 1 (forced by user); cap at max
    user["day"] = user.get("day", 1) + 1
    if user["day"] > len(TOPICS):
        user["day"] = len(TOPICS)
        save_progress(progress)
        await update.message.reply_text("🎉 You’ve completed all 30 days! 🎉")
        return

    # Update last_time because we intentionally moved to the next day and delivered a blog
    user["last_time"] = datetime.now().isoformat()
    save_progress(progress)

    day = user["day"]
    topic = TOPICS[day - 1]
    await update.message.reply_text(f"🌅 Moved to Day {day}: *{topic}*\n\nGenerating your blog...")
    blog = await generate_blog(topic)
    await update.message.reply_text(blog)

# ----------------------------
# Keep-alive web server for hosting platforms (Render/Replit)
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
    if BOT_TOKEN.startswith("YOUR_") or GEMINI_API_KEY.startswith("YOUR_"):
        print("⚠️ Warning: Replace BOT_TOKEN and GEMINI_API_KEY with your actual keys or set environment variables.")
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("regive", regive))
    app.add_handler(CommandHandler("nextday", nextday))

    print("🤖 Bot is running... try sending /start in Telegram.")
    app.run_polling()

if __name__ == "__main__":
    main()
