from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import filters

from config import Config
from telegram_adapter.telegram_command_handler import TelegramCommandHandler

import logging

token: str = input("Enter bot token: ")

logger = logging.getLogger(__name__)
logging.basicConfig(filename=Config.log_file_name, encoding='utf-8', level=logging.INFO)

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
    CommandHandler(command=TelegramCommandHandler.COMMAND_RESET, callback=TelegramCommandHandler.run_reset)
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
    CommandHandler(command=TelegramCommandHandler.COMMAND_LOCK, callback=TelegramCommandHandler.run_lock)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_UNLOCK, callback=TelegramCommandHandler.run_unlock)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_HELP, callback=TelegramCommandHandler.run_help)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_HISTORY, callback=TelegramCommandHandler.run_history)
)
app.add_handler(
    CommandHandler(command=TelegramCommandHandler.COMMAND_AKA, callback=TelegramCommandHandler.run_aka)
)
app.add_handler(
    MessageHandler(filters=filters.COMMAND, callback=TelegramCommandHandler.run_command_not_found)
)
app.add_handler(CallbackQueryHandler(TelegramCommandHandler.handle_buttons))

app.run_polling()
