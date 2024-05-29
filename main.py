import string
import sys

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

token: string = input("Enter bot token: ")

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.username}')

# /new: renew booking (beginning of the week), require admin privilege
# /rec: recall booking (when error happens, use this to recally by copying), require admin privilege
# /reg: register slot, for any user
# /dereg: deregister slot, for any user
# /help: guide for user

app = ApplicationBuilder().token(token).build()

app.add_handler(CommandHandler("hello", hello))

app.run_polling()
