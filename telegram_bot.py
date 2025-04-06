from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
from dotenv import load_dotenv
import os

from check_tracker import check_status

# Load variables from .env into environment
load_dotenv()

# Access them like normal environment variables
bot_token = os.getenv("YOUR_BOT_TOKEN")


UCI, PASSWORD = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Please send your IRCC UCI.")
    return UCI


async def get_uci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["UCI"] = update.message.text
    await update.message.reply_text("Now send your password.")
    return PASSWORD


async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uci = context.user_data["UCI"]
    password = update.message.text

    await update.message.reply_text("Checking status...")

    try:
        status = await check_status(uci, password)
    except Exception as e:
        status = f"Error: {str(e)}"

    await update.message.reply_text(status)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


app = ApplicationBuilder().token(bot_token).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        UCI: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_uci)],
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.run_polling()
