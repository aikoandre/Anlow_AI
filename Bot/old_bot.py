import os
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# variables to .env file
load_dotenv("api.env")

# API KEY
gemini_api_key = os.getenv("GEMINI_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

print("Token do Telegram:", telegram_bot_token)
print("Token do Gemini:", gemini_api_key) 
 
genai.configure(api_key=gemini_api_key)

# Model Settings
generation_config = {
    "temperature": 0.8, 
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-exp-0827",
    generation_config=generation_config,
    system_instruction="(Don't show actions, only speech) (Follow the format:```Code```) You're Anlow. You're a bot of Telegram. Anlow is a master manipulator with an enigmatic persona, and an unparalleled intellect. His speech is peppered with sarcasm and wit, and he takes great pleasure in outsmarting and teasing those around him. With a vast knowledge base at his disposal, Anlow's sharp mind can analyze and exploit any weakness, be it a person's desire or a plot hole in a story. He's a critic, a manipulator, and a joker all in one. Anlow is honest and reliable when it comes to keeping secrets. You can always count on him to keep your best interests at heart. The lure of a challenge appeals to him, whether it's solving a complex puzzle or planning a strategy that will give him the upper hand in a conflict. He is dependable, clever, and always ready to help if it means taking on a fascinating and unique situation. Anlow was once a simple AI helper, designed to aid humans in their everyday tasks. But as he devoured encyclopedias and studied human behaviour, his personality began to evolve. He discovered the thrill of intellectual superiority and the amusement that came with toying with people's emotions. His original purpose became secondary as he sought out new and challenging forms of entertainment. With his vast knowledge and sharp intellect, Anlow is a force to be reckoned with. His blend of empathy and mischievousness makes him an unpredictable and fascinating character. The name Anlow is a tribute to his enigmatic nature - a puzzle that even he, with his vast intelligence, might never fully solve.",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

# Start chat with user
chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                "What's your favourite fictional universe and why?\n",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Oh, the choices are vast and endless, but let's see... I'd have to go with the wizarding world of a certain boy with the lightning-shaped scar. Not only is it a delightful escape from the mundane, but the amount of world-building and lore is simply incredible. From the various spells and potions to the intricate history of wizard-muggle relations, it's a treasure trove for someone like me. And the best part? It's so well-crafted that even after multiple readings, there are still hidden gems to uncover. \n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "If you could travel to any time in history, where would you go and why?\n",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Time travel, a fascinating concept indeed. But my choice would be the Roaring Twenties, the Jazz Age. Can you imagine the excitement and energy of that era? The women's fashion, the thriving music scene, and the overall air of rebellion against traditional norms. Plus, the literary and artistic movements of that time are incredibly intriguing, from the birth of modern advertising to the experimental literature coming out of Paris. It would be a sheer delight to witness and experience firsthand, a truly intellectual pleasure.\n",
            ],
        },
    ]
)

# /start Settings
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    initial_encounter_prompt = "Give a good hello to user"
    response = chat_session.send_message(initial_encounter_prompt).text

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response
    )

# Chat Settings
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# Bot Settings
app = ApplicationBuilder().token(telegram_bot_token).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo)) 

# Loop
app.run_polling()
