from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, Application, ExtBot,
                          CallbackContext, JobQueue)
from telegram.ext import filters

from telegram_adapter.telegram_command_handler import TelegramCommandHandler

import logging


def main() -> (Application[
    ExtBot[None], CallbackContext[ExtBot[None], dict, dict, dict], dict, dict, dict, JobQueue[
        CallbackContext[ExtBot[None], dict, dict, dict]]],
               logging.Logger):
    TelegramCommandHandler.initialize()

    token: str = input("Enter bot token: ")
    print(f"Please remember to run command /{TelegramCommandHandler.COMMAND_START}")

    to_be_returned_logger: logging.Logger = logging.getLogger(__name__)

    to_be_returned_app = (
        ApplicationBuilder()
        .token(token)
        .read_timeout(60)
        .write_timeout(60)
        .build()
    )

    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_START, callback=TelegramCommandHandler.run_start)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_HELLO, callback=TelegramCommandHandler.run_hello)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_RETRIEVE, callback=TelegramCommandHandler.run_all)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_ALL, callback=TelegramCommandHandler.run_all)
    )  # same as /retrieve
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_NEW, callback=TelegramCommandHandler.run_new)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_NOTITIME, callback=TelegramCommandHandler.run_notitime)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_RESET, callback=TelegramCommandHandler.run_reset)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_REG, callback=TelegramCommandHandler.run_reg)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_RG, callback=TelegramCommandHandler.run_reg)
    )  # same as /reg
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_RESERVE, callback=TelegramCommandHandler.run_reserve)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_RS, callback=TelegramCommandHandler.run_reserve)
    )  # same as /reserve
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_DEREG, callback=TelegramCommandHandler.run_dereg)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_DRG, callback=TelegramCommandHandler.run_dereg)
    )  # same as /drg
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_ADMIN, callback=TelegramCommandHandler.run_admin)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_AV, callback=TelegramCommandHandler.run_av)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_ALLPENDING,
                       callback=TelegramCommandHandler.run_allpending)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_LOCK, callback=TelegramCommandHandler.run_lock)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_UNLOCK, callback=TelegramCommandHandler.run_unlock)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_HELP, callback=TelegramCommandHandler.run_help)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_HISTORY, callback=TelegramCommandHandler.run_history)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=TelegramCommandHandler.COMMAND_AKA, callback=TelegramCommandHandler.run_aka)
    )
    to_be_returned_app.add_handler(
        MessageHandler(filters=filters.COMMAND, callback=TelegramCommandHandler.run_command_not_found)
    )
    to_be_returned_app.add_handler(CallbackQueryHandler(TelegramCommandHandler.handle_buttons))

    to_be_returned_app.run_polling()
    return to_be_returned_app, to_be_returned_logger


if __name__ == "__main__":
    app: Application[
             ExtBot[None],
             CallbackContext[ExtBot[None], dict, dict, dict],
             dict, dict, dict, JobQueue[CallbackContext[ExtBot[None], dict, dict, dict]]] | None = None
    logger: logging.Logger | None = None
    try:
        # deletion_queue: DeletionQueue = DeletionQueue("abc.txt")
        app, logger = main()
    except KeyboardInterrupt:
        if logger is not None:
            logger.handlers.clear()
        if app is not None:
            app.stop_running()
        print("Bot is stopped successfully!")
