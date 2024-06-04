from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler
from telegram.ext import filters
from auto_registration_system.auto_registration_system import AutoRegistrationSystem
from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.telegram_command_handler import TelegramCommandHandler

token: str = input("Enter bot token: ")

app = (
    ApplicationBuilder()
    .token(token)
    .read_timeout(60)
    .write_timeout(60)
    .build()
)

app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_HELLO, callback=TelegramCommandHandler.run_hello)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_RETRIEVE, callback=TelegramCommandHandler.run_retrieve)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_ALL, callback=TelegramCommandHandler.run_retrieve)
)    # same as /retrieve
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_NEW, callback=TelegramCommandHandler.run_new)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_REG, callback=TelegramCommandHandler.run_reg)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_RG, callback=TelegramCommandHandler.run_reg)
)  # same as /reg
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_RESERVE, callback=TelegramCommandHandler.run_reserve)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_RS, callback=TelegramCommandHandler.run_reserve)
)  # same as /reserve
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_DEREG, callback=TelegramCommandHandler.run_dereg)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_DRG, callback=TelegramCommandHandler.run_dereg)
)   # same as /drg
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_ADMIN, callback=TelegramCommandHandler.run_admin)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_AV, callback=TelegramCommandHandler.run_av)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_ALLPLAYABLE, callback=TelegramCommandHandler.run_allplayable)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_HELP, callback=TelegramCommandHandler.run_help)
)
app.add_handler(
    MessageHandler(filters=filters.COMMAND, callback=TelegramCommandHandler.run_command_not_found)
)
app.add_handler(CallbackQueryHandler(TelegramCommandHandler.handle_buttons))

app.run_polling()
