import traceback

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove, ForceReply, User, Message
from telegram.constants import MessageEntityType, ParseMode
from telegram.ext import ContextTypes

from auto_registration_system.auto_registration_system import AutoRegistrationSystem
from auto_registration_system.data_structure.registration_data import RegistrationData
from time_manager import TimeManager
from tracer import Tracer
from string_parser.string_parser import StringParser

import time

from config import Config


class TelegramCommandHandler:

    auto_reg_system: AutoRegistrationSystem = AutoRegistrationSystem(
        admins=Config.admins,
        chat_ids=Config.chat_ids,
        alias_file_name=Config.alias_file_name
    )

    tracer: Tracer = Tracer(
        log_file_name=Config.log_file_name,
        history_file_name=Config.history_file_name,
        time_manager=TimeManager(time_zone=Config.time_zone, time_format=Config.time_format)
    )

    NUM_BUTTONS_PER_LINE = 3

    last_chat_id = None
    last_message_id = None

    last_av_chat_id = None
    last_av_message_id = None

    COMMAND_HELLO = "hello"
    COMMAND_RETRIEVE = "retrieve"
    COMMAND_ALL = "all"
    COMMAND_NEW = "new"
    COMMAND_REG = "reg"
    COMMAND_RG = "rg"
    COMMAND_RESERVE = "reserve"
    COMMAND_RS = "rs"
    COMMAND_DEREG = "dereg"
    COMMAND_DRG = "drg"
    COMMAND_ADMIN = "admin"
    COMMAND_AV = "av"
    COMMAND_ALLPLAYABLE = "allplayable"
    COMMAND_LOCK = "lock"
    COMMAND_UNLOCK = "unlock"
    COMMAND_HELP = "help"
    COMMAND_HISTORY = "history"
    COMMAND_AKA = "aka"
    CALLBACK_DATA_HELP = f"_{COMMAND_HELP}"
    CALLBACK_DATA_ALL = f"_{COMMAND_ALL}"
    CALLBACK_DATA_DRG = f"_{COMMAND_DRG}"
    CALLBACK_DATA_AV = f"_{COMMAND_AV}"
    CALLBACK_DATA_RG = f"_{COMMAND_RG}"

    SECOND_CLICK_TO_DEREGISTER = False

    @staticmethod
    async def reply_message(
            update: Update,
            text: str,
            parse_mode: ParseMode or None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
    ):
        try:
            if len(text.strip()) == 0:
                text = "Có lỗi xảy ra! Tin nhắn được gửi rỗng!"
            return await update.message.reply_text(text=text, parse_mode=parse_mode, reply_markup=reply_markup)
        except Exception as e:
            TelegramCommandHandler.tracer.log(
                message=f"(from system) We caught an error when replying message: {repr(e)}"
            )
            time.sleep(10)
            await TelegramCommandHandler.reply_message(update=update, text="Vừa có lỗi kết nối! Đang thử lại!")
            return await TelegramCommandHandler.reply_message(
                update=update,
                text=text,
                reply_markup=reply_markup
            )

    @staticmethod
    def make_callback_data_for_rg(slot_label: str) -> str:
        return f"{TelegramCommandHandler.CALLBACK_DATA_RG} {slot_label}"

    @staticmethod
    def make_inline_buttons_for_registration(data: RegistrationData) -> InlineKeyboardMarkup:
        button_count = 0
        button_list = []
        current_line_button_list = None
        for date_venue in data.bookings_by_date_venue:
            for slot_label in data.bookings_by_date_venue[date_venue]:
                button = InlineKeyboardButton(
                    text=f"slot {slot_label}",
                    callback_data=TelegramCommandHandler.make_callback_data_for_rg(slot_label=slot_label)
                )
                if button_count % TelegramCommandHandler.NUM_BUTTONS_PER_LINE == 0:
                    if current_line_button_list is not None:
                        button_list.append(current_line_button_list)
                    current_line_button_list = [button]
                else:
                    current_line_button_list.append(button)
                button_count += 1
        if current_line_button_list is not None:
            button_list.append(current_line_button_list)

        # add buttons all and help
        button_list.append([
            # InlineKeyboardButton(
            #     text=TelegramCommandHandler.COMMAND_DRG,
            #     callback_data=TelegramCommandHandler.CALLBACK_DATA_DRG
            # ),
            InlineKeyboardButton(
                text=TelegramCommandHandler.COMMAND_ALL,
                callback_data=TelegramCommandHandler.CALLBACK_DATA_ALL
            ),
            InlineKeyboardButton(
                text=TelegramCommandHandler.COMMAND_AV,
                callback_data=TelegramCommandHandler.CALLBACK_DATA_AV
            ),
            InlineKeyboardButton(
                text=TelegramCommandHandler.COMMAND_HELP,
                callback_data=TelegramCommandHandler.CALLBACK_DATA_HELP
            ),
        ])
        return InlineKeyboardMarkup(inline_keyboard=button_list)

    @staticmethod
    def get_id_string_from_telegram_user(user: User):
        return TelegramCommandHandler.auto_reg_system.identity_manager.get_alias_or_full_name(
            telegram_id=user.id,
            full_name=StringParser.process_telegram_full_name(telegram_full_name=user.full_name)
        )

    # @staticmethod
    # def get_full_name_from_query(query: CallbackQuery) -> str:
    #     full_name = query.from_user.full_name
    #     char_list = list(full_name)
    #     for i, c in enumerate(char_list):
    #         if c == ",":
    #             char_list[i] = ""
    #     full_name = StringParser.split_names(message="".join(char_list))[0]
    #     return full_name
    #
    # @staticmethod
    # def get_full_name_from_update(update: Update) -> str:
    #     full_name = update.message.from_user.full_name
    #     char_list = list(full_name)
    #     for i, c in enumerate(char_list):
    #         if c == ",":
    #             char_list[i] = ""
    #     full_name = StringParser.split_names(message="".join(char_list))[0]
    #     return full_name

    @staticmethod
    def is_callback_data_rg(query_data: str) -> bool:
        first_word = StringParser.get_first_word(message=query_data)
        if first_word == TelegramCommandHandler.CALLBACK_DATA_RG:
            return True
        return False

    @staticmethod
    async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        full_name = StringParser.process_telegram_full_name(telegram_full_name=query.from_user.full_name)
        id_string = TelegramCommandHandler.get_id_string_from_telegram_user(user=query.from_user)
        identity_message = (f"\\(from [{StringParser.replace_escape_characters_for_markdown(full_name)}]"
                            + f"(tg://user?id={query.from_user.id})\\)")

        # handle special case for all and help
        if query.data == TelegramCommandHandler.CALLBACK_DATA_ALL:
            res = await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=f"/{TelegramCommandHandler.COMMAND_ALL}\t{identity_message}",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            await TelegramCommandHandler.run_retrieve(update=Update(update_id=res.id, message=res), context=context)
            return
        elif query.data == TelegramCommandHandler.CALLBACK_DATA_HELP:
            res = await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=f"/{TelegramCommandHandler.COMMAND_HELP}\t{identity_message}",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            await TelegramCommandHandler.run_help(update=Update(update_id=res.id, message=res), _=None)
            return
        elif query.data == TelegramCommandHandler.CALLBACK_DATA_AV:
            res = await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=f"/{TelegramCommandHandler.COMMAND_AV}\t{identity_message}",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            await TelegramCommandHandler.run_av(update=Update(update_id=res.id, message=res), context=context)
            return
        elif TelegramCommandHandler.is_callback_data_rg(query_data=query.data):
            slot_label = StringParser.get_last_word(message=query.data)
            message = f"/{TelegramCommandHandler.COMMAND_RG} {id_string} {slot_label}"
            res = await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=f"{StringParser.replace_escape_characters_for_markdown(message=message)}\t{identity_message}",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            new_message = Message(
                message_id=res.id,
                date=res.date,
                chat=res.chat,
                from_user=res.from_user,
                text=message
            )
            new_message.set_bot(res.get_bot())
            await TelegramCommandHandler.run_reg(
                update=Update(update_id=res.id, message=new_message),
                context=context,
                effective_user=query.from_user.username
            )

    @staticmethod
    async def write_data_and_update_bot_message_for_full_list(
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
            message: str or None,
            parse_mode: ParseMode or None=None
    ):
        all_slots_as_string = TelegramCommandHandler.auto_reg_system.get_all_slots_as_string()

        # sends all slots to chat
        new_chat_id = None
        new_message_id = None
        if all_slots_as_string is not None:
            sent_message_info = await TelegramCommandHandler.reply_message(
                update=update,
                text=all_slots_as_string,
                reply_markup=TelegramCommandHandler.make_inline_buttons_for_registration(
                    data=TelegramCommandHandler.auto_reg_system.data
                )
            )
            new_chat_id = sent_message_info.chat_id
            new_message_id = sent_message_info.message_id
            TelegramCommandHandler.tracer.log(message=f"(from system)\n{all_slots_as_string}")
        else:
            await TelegramCommandHandler.reply_message(update=update, text="Danh sách chơi trống!")

        # inform message
        if message is not None:
            await TelegramCommandHandler.reply_message(update=update, text=message, parse_mode=parse_mode)

        # delete previous message
        if TelegramCommandHandler.last_chat_id is not None and TelegramCommandHandler.last_message_id is not None:
            try:
                await context.bot.deleteMessage(
                    message_id=TelegramCommandHandler.last_message_id,
                    chat_id=TelegramCommandHandler.last_chat_id
                )
            except Exception:
                pass
        TelegramCommandHandler.last_chat_id = new_chat_id
        TelegramCommandHandler.last_message_id = new_message_id

    @staticmethod
    def log_message_from_user(update: Update):
        TelegramCommandHandler.tracer.log(
            message=f"(from {TelegramCommandHandler.get_id_string_from_telegram_user(user=update.message.from_user)})"
                    + f" {update.message.text}"
        )

    @staticmethod
    async def run_hello(update: Update, _):
        TelegramCommandHandler.log_message_from_user(update=update)
        await TelegramCommandHandler.reply_message(update=update, text=f'Chào {update.effective_user.first_name}')

    @staticmethod
    async def run_retrieve(update: Update, context: ContextTypes.DEFAULT_TYPE):
        TelegramCommandHandler.log_message_from_user(update=update)
        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=None
        )

    @staticmethod
    async def run_av(update: Update, context: ContextTypes.DEFAULT_TYPE):
        TelegramCommandHandler.log_message_from_user(update=update)

        # send new message
        sent_message_info = await TelegramCommandHandler.reply_message(
            update=update,
            text="Danh sách các slot còn thiếu người:\n\n" +
                 TelegramCommandHandler.auto_reg_system.get_available_slots_as_string(),
            reply_markup=TelegramCommandHandler.make_inline_buttons_for_registration(
                data=TelegramCommandHandler.auto_reg_system.data
            )
        )
        new_av_chat_id = sent_message_info.chat_id
        new_av_message_id = sent_message_info.message_id

        # try delete previous message
        if TelegramCommandHandler.last_av_chat_id is not None and TelegramCommandHandler.last_av_chat_id is not None:
            try:
                await context.bot.deleteMessage(
                    message_id=TelegramCommandHandler.last_av_message_id,
                    chat_id=TelegramCommandHandler.last_av_chat_id
                )
            except Exception:
                pass

        # record id of current message
        if new_av_chat_id is not None and new_av_message_id is not None:
            TelegramCommandHandler.last_av_chat_id = new_av_chat_id
            TelegramCommandHandler.last_av_message_id = new_av_message_id

    @staticmethod
    async def run_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
        TelegramCommandHandler.log_message_from_user(update=update)
        message = TelegramCommandHandler.auto_reg_system.handle_new(
            username=update.effective_user.username,
            message=update.message.text
        )
        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=message
        )

    @staticmethod
    async def run_reg(update: Update, context: ContextTypes.DEFAULT_TYPE, effective_user: str or None = None):
        TelegramCommandHandler.log_message_from_user(update=update)

        if effective_user is None:
            effective_user = update.effective_user.username

        response, suggestion = TelegramCommandHandler.auto_reg_system.handle_register(
            command_string_for_suggestion=TelegramCommandHandler.COMMAND_DRG,
            username=effective_user,
            message=update.message.text,
            chat_id=update.message.chat_id
        )
        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=response
        )

        if suggestion is not None:
            await TelegramCommandHandler.reply_message(
                update=update,
                text=suggestion,
                parse_mode=ParseMode.MARKDOWN_V2
            )

    @staticmethod
    async def run_reserve(update: Update, context: ContextTypes.DEFAULT_TYPE, effective_user: str or None = None):
        TelegramCommandHandler.log_message_from_user(update=update)

        if effective_user is None:
            effective_user = update.effective_user.username

        message = TelegramCommandHandler.auto_reg_system.handle_reserve(
            username=effective_user,
            message=update.message.text,
            chat_id=update.message.chat_id
        )
        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=message
        )

    @staticmethod
    async def run_dereg(update: Update, context: ContextTypes.DEFAULT_TYPE, effective_user: User or None = None):
        TelegramCommandHandler.log_message_from_user(update=update)

        if effective_user is None:
            effective_user = update.effective_user

        id_string = TelegramCommandHandler.get_id_string_from_telegram_user(user=effective_user)

        message = TelegramCommandHandler.auto_reg_system.handle_deregister(
            command_string=TelegramCommandHandler.COMMAND_DRG,
            username=effective_user.username,
            id_string=id_string,
            message=update.message.text,
            chat_id=update.message.chat_id
        )
        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=message,
            parse_mode=ParseMode.MARKDOWN_V2
        )

    @staticmethod
    async def run_admin(update: Update, _):
        TelegramCommandHandler.log_message_from_user(update=update)

        await TelegramCommandHandler.reply_message(
            update=update,
            text=TelegramCommandHandler.auto_reg_system.get_admin_list_as_string()
        )

    @staticmethod
    async def run_command_not_found(update: Update, _):
        TelegramCommandHandler.log_message_from_user(update=update)

        await TelegramCommandHandler.reply_message(update=update, text="Sai lệnh!")

    @staticmethod
    async def run_allplayable(update: Update, context: ContextTypes.DEFAULT_TYPE):
        TelegramCommandHandler.log_message_from_user(update=update)

        message = TelegramCommandHandler.auto_reg_system.handle_allplayable(
            username=update.effective_user.username,
            chat_id=update.message.chat_id
        )

        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=message
        )

    @staticmethod
    async def run_lock(update: Update, _):
        TelegramCommandHandler.log_message_from_user(update=update)

        message = TelegramCommandHandler.auto_reg_system.handle_lock(username=update.effective_user.username)

        await TelegramCommandHandler.reply_message(update=update, text=message)

    @staticmethod
    async def run_unlock(update: Update, _):
        TelegramCommandHandler.log_message_from_user(update=update)

        message = TelegramCommandHandler.auto_reg_system.handle_unlock(username=update.effective_user.username)

        await TelegramCommandHandler.reply_message(update=update, text=message)

    @staticmethod
    async def run_history(update: Update, _):
        TelegramCommandHandler.log_message_from_user(update=update)

        try:
            file = TelegramCommandHandler.auto_reg_system.handle_history(
                username=update.effective_user.username,
                history_file_name=Config.history_file_name
            )
            await update.message.reply_document(document=file)
        except Exception:
            await TelegramCommandHandler.reply_message(
                update=update,
                text="Không thể gửi file! Cần quyền admin hoặc kết nối gặp vấn đề!"
            )

    @staticmethod
    async def run_aka(update: Update, _):
        TelegramCommandHandler.log_message_from_user(update=update)

        try:
            response = TelegramCommandHandler.auto_reg_system.handle_aka(
                sender_id=update.effective_user.id,
                sender_full_name=StringParser.process_telegram_full_name(
                    telegram_full_name=update.effective_user.full_name
                ),
                message=update.message.text,
                command_string=TelegramCommandHandler.COMMAND_AKA,
                message_entities=update.message.parse_entities(
                    types=[MessageEntityType.MENTION, MessageEntityType.TEXT_MENTION]
                )
            )
            await TelegramCommandHandler.reply_message(update=update, text=response)
        except Exception as e:
            await TelegramCommandHandler.reply_message(
                update=update,
                text=repr(e)
            )

    @staticmethod
    async def run_help(update: Update, _):
        TelegramCommandHandler.log_message_from_user(update=update)

        response: str = "Sử dụng những cú pháp sau:\n"
        response += f"/{TelegramCommandHandler.COMMAND_REG} [tên 1], ..., [tên n] [slot]\t(đăng kí)\n"
        response += f"/{TelegramCommandHandler.COMMAND_DEREG} [tên 1], ..., [tên n] [slot]\t(hủy đăng kí)\n"
        response += f"/{TelegramCommandHandler.COMMAND_RESERVE} [tên 1], ..., [tên n] [slot]\t(dự bị)\n"
        response += f"/{TelegramCommandHandler.COMMAND_ALL}\t(hiện đầy đủ danh sách)\n"
        response += f"/{TelegramCommandHandler.COMMAND_AV}\t(hiện các slot còn thiếu người)\n"
        response += f"\n"
        response += f"Các lệnh rút ngắn:\n"
        response += f"/{TelegramCommandHandler.COMMAND_RG}\t(giống như /reg)\n"
        response += f"/{TelegramCommandHandler.COMMAND_DRG}\t(giống như /dereg)\n"
        response += f"/{TelegramCommandHandler.COMMAND_RS}\t(giống như /reserve)\n"
        response += f"\n"
        response += f"Hướng dẫn chi tiết: https://hackmd.io/@1UKfawZER96uwy_xohcquQ/B1fyW-c4R"
        await TelegramCommandHandler.reply_message(update=update, text=response)
