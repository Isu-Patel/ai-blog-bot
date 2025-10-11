# ============================================
# 30 Days AI Blog Telegram Bot (Gemini + Keep Alive)
# ============================================

import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime, timedelta
from flask import Flask
import threading

# ============================================
# 🔑 TOKENS
# ============================================
BOT_TOKEN = "8004004924:AAHSpHgeDGHGek69gCTvVLg1B-C9CuvdnSE"
GEMINI_API_KEY = "AIzaSyCASA0_4bI7CLjr9HOyb2eHJ3rALhyMF18"
# ============================================

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- 30 Topics ---
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

# --- Track user progress ---
user_day = {}
last_blog = {}
last_time = {}

# --- AI Blog Generation ---
def generate_blog(topic):
    prompt = f"Write a well-formatted 250-word blog post with headings and short paragraphs about '{topic}'."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini Error:", e)
        return "⚠️ Sorry, I couldn’t generate the blog right now. Please try again later."

# --- /start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_day[user_id] = 1
    last_time[user_id] = datetime.now()

    topic = TOPICS[0]
    await update.message.reply_text(f"📘 30 Days AI Blog Challenge\n\n📅 Day 1: *{topic}*\n\nGenerating your blog...")

    blog = generate_blog(topic)
    last_blog[user_id] = blog
    await update.message.reply_text(blog)

# --- /regive command ---
async def regive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    day = user_day.get(user_id, 1)
    topic = TOPICS[day - 1]
    await update.message.reply_text(f"🔄 Regenerating a new blog for *Day {day}: {topic}*...")

    blog = generate_blog(topic)
    last_blog[user_id] = blog
    await update.message.reply_text(blog)

# --- /nextday command ---
async def nextday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = datetime.now()

    # If 24 hours passed, move to next day
    if user_id in last_time and now - last_time[user_id] >= timedelta(hours=24):
        user_day[user_id] = user_day.get(user_id, 1) + 1
        last_time[user_id] = now
    elif user_id not in user_day:
        user_day[user_id] = 1
        last_time[user_id] = now

    if user_day[user_id] > len(TOPICS):
        await update.message.reply_text("🎉 You’ve completed all 30 days! Great job!")
        return

    day = user_day[user_id]
    topic = TOPICS[day - 1]
    await update.message.reply_text(f"🌅 Day {day}: *{topic}*\n\nGenerating your blog...")

    blog = generate_blog(topic)
    last_blog[user_id] = blog
    await update.message.reply_text(blog)

# --- Flask Keep Alive ---
app = Flask('')

@app.route('/')
def home():
    return "🤖 Telegram Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    thread = threading.Thread(target=run)
    thread.start()

# --- Main Bot Setup ---
def main():
    keep_alive()  # ✅ Keeps bot running 24/7
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("regive", regive))
    app_bot.add_handler(CommandHandler("nextday", nextday))

    print("🤖 Bot is running... try sending /start in Telegram.")
    app_bot.run_polling()

if __name__ == "__main__":
    main()

