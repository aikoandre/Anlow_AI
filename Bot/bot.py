import asyncio
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gemini import GeminiConfig
import time
from datetime import datetime

# Load environment variables from the .env file
load_dotenv("api.env")

# API KEY
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

print("Token do Telegram:", telegram_bot_token)

# Initialize Gemini configuration and chat session
gemini_config = GeminiConfig()
chat_session = gemini_config.start_chat()

# Timeout for inactivity in seconds (2 minutes)
TIMEOUT = 120

# Global variables for inactivity tracking
inactivity_message_sent = False
last_activity_time = time.time()  # Initialize with the current time
last_inactivity_message_date = None  # Store the date of the last inactivity message

# Function to check for inactivity and send a message
async def check_inactivity(context: ContextTypes.DEFAULT_TYPE):
    global last_activity_time, inactivity_message_sent, last_inactivity_message_date

    chat_id = context.job.data  # Retrieve the chat_id from the job data

    current_date = datetime.now().date()  # Get the current date

    # Check if the inactivity message has already been sent today
    if last_inactivity_message_date == current_date:
        return  # If the message has already been sent today, do nothing

    # Check inactivity
    if time.time() - last_activity_time > TIMEOUT and not inactivity_message_sent:
        prompt = "Check if user is alive!"
        response = chat_session.send_message(prompt).text
        await context.bot.send_message(chat_id=chat_id, text=response)
        inactivity_message_sent = True
        last_activity_time = time.time()
        last_inactivity_message_date = current_date  # Update the date of the last inactivity message
    elif time.time() - last_activity_time <= TIMEOUT and inactivity_message_sent:
        inactivity_message_sent = False

# Function to update the last activity timestamp
def update_last_activity_time():
    global last_activity_time
    last_activity_time = time.time()

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update_last_activity_time()  # Update the timestamp when the conversation starts
    initial_encounter_prompt = "Give a good hello to the user"
    response = chat_session.send_message(initial_encounter_prompt).text

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response
    )

    # Schedule the check_inactivity task
    context.job_queue.run_repeating(check_inactivity, interval=60, data=update.effective_chat.id)

# Echo message handler
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update_last_activity_time()
    user_message = update.message.text
    response = chat_session.send_message(user_message)

    if response.text:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response.text
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Desculpe, não consegui entender isso. Pode reformular?"
        )

# Bot settings
app = ApplicationBuilder().token(telegram_bot_token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Start polling
app.run_polling()
