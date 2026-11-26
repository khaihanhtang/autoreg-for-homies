import logging
import re
from getpass import getpass

from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, Application, ExtBot,
                          CallbackContext, JobQueue)
from telegram.ext import filters

from telegram_adapter.telegram_command_handler import TelegramCommandHandler
from auto_registration_system.command import Command

def main() -> (Application[
    ExtBot[None], CallbackContext[ExtBot[None], dict, dict, dict], dict, dict, dict, JobQueue[
        CallbackContext[ExtBot[None], dict, dict, dict]]],
               logging.Logger):
    # Load the saved state now. The post-init hook queues release work once Telegram is ready.
    TelegramCommandHandler.initialize()

    token: str = input("Enter bot token: ")
    cloudflare_account_id = ""
    while not re.fullmatch(r"[0-9a-fA-F]{32}", cloudflare_account_id):
        cloudflare_account_id = input("Enter Cloudflare account ID (32 hex characters): ").strip()
    cloudflare_api_token = ""
    while not cloudflare_api_token:
        cloudflare_api_token = getpass("Enter Cloudflare Workers AI API token (required): ").strip()
    print(f"Please remember to run command /{Command.COMMAND_START}")

    to_be_returned_logger: logging.Logger = logging.getLogger(__name__)

    to_be_returned_app = (
        ApplicationBuilder()
        .token(token)
        .read_timeout(60)
        .write_timeout(60)
        .post_init(TelegramCommandHandler.start_release_job)
        .build()
    )

    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_START, callback=TelegramCommandHandler.run_start)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_HELLO, callback=TelegramCommandHandler.run_hello)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_RETRIEVE, callback=TelegramCommandHandler.run_all)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_ALL, callback=TelegramCommandHandler.run_all)
    )  # same as /retrieve
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_NEW, callback=TelegramCommandHandler.run_new)
    )
    # The release commands share one schedule, and /state reports the active mode.
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_NOTITIME, callback=TelegramCommandHandler.run_notitime)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_WEEKLYNOTITIME, callback=TelegramCommandHandler.run_weeklynotitime)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_TESTNOTITIME, callback=TelegramCommandHandler.run_testnotitime)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_STATE, callback=TelegramCommandHandler.run_state)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_RESET, callback=TelegramCommandHandler.run_reset)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_REG, callback=TelegramCommandHandler.run_reg)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_RG, callback=TelegramCommandHandler.run_reg)
    )  # same as /reg
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_RESERVE, callback=TelegramCommandHandler.run_reserve)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_RS, callback=TelegramCommandHandler.run_reserve)
    )  # same as /reserve
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_DEREG, callback=TelegramCommandHandler.run_dereg)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_DRG, callback=TelegramCommandHandler.run_dereg)
    )  # same as /drg
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_ADMIN, callback=TelegramCommandHandler.run_admin)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_AV, callback=TelegramCommandHandler.run_av)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_ALLPENDING, callback=TelegramCommandHandler.run_allpending)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_LOCK, callback=TelegramCommandHandler.run_lock)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_UNLOCK, callback=TelegramCommandHandler.run_unlock)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_HELP, callback=TelegramCommandHandler.run_help)
    )
    to_be_returned_app.add_handler(
        CommandHandler(
            command=Command.COMMAND_AI,
            callback=TelegramCommandHandler.make_ai_callback(
                account_id=cloudflare_account_id, api_token=cloudflare_api_token,
            ),
            block=False,
        )
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_HISTORY, callback=TelegramCommandHandler.run_history)
    )
    to_be_returned_app.add_handler(
        CommandHandler(command=Command.COMMAND_AKA, callback=TelegramCommandHandler.run_aka)
    )
    # Register the catch-all after the named commands so it receives unrecognized commands.
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
