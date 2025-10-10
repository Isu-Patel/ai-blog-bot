# ============================================
# 30 Days AI Blog Telegram Bot (Gemini Version)
# ============================================

import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ============================================
# 🔑 PUT YOUR TOKENS HERE
# ============================================
BOT_TOKEN = "8004004924:AAHSpHgeDGHGek69gCTvVLg1B-C9CuvdnSE"
GEMINI_API_KEY = "AIzaSyCASA0_4bI7CLjr9HOyb2eHJ3rALhyMF18"
# ============================================

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Load the model
model = genai.GenerativeModel("gemini-2.5-flash")

# 30 Topics for 30 Days
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

# Store user progress
user_day = {}
last_blog = {}

# --- Function: Generate Blog using Gemini ---
def generate_blog(topic):
    prompt = f"Write a detailed, engaging, with proper heading and proper syntaxes as a blog or paragraph or blog post (around 250 words) about '{topic}'."
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
    await update.message.reply_text(f"🔄 Generating a new blog for *Day {day}: {topic}*...")

    blog = generate_blog(topic)
    last_blog[user_id] = blog
    await update.message.reply_text(blog)

# --- /nextday command ---
async def nextday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_day[user_id] = user_day.get(user_id, 1) + 1

    if user_day[user_id] > len(TOPICS):
        await update.message.reply_text("🎉 You’ve completed all 30 days! Great job!")
        return

    day = user_day[user_id]
    topic = TOPICS[day - 1]
    await update.message.reply_text(f"🌅 Moving to Day {day}: *{topic}*\n\nGenerating your blog...")

    blog = generate_blog(topic)
    last_blog[user_id] = blog
    await update.message.reply_text(blog)

# --- Main Bot Setup ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("regive", regive))
    app.add_handler(CommandHandler("nextday", nextday))

    print("🤖 Bot is running... try sending /start in Telegram.")
    app.run_polling()

if __name__ == "__main__":
    main()
