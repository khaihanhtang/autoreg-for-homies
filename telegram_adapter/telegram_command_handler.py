from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove, ForceReply, User, Message, CallbackQuery
from telegram.constants import MessageEntityType, ParseMode
from telegram.ext import ContextTypes

from auto_registration_system.auto_registration_system import AutoRegistrationSystem
from auto_registration_system.command_handler.handler_dereg import DeregHandler
from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.data_structure.time_manager import TimeManager
from tracer import Tracer
from string_parser.string_parser import StringParser
from data_handler.data_handler import DataHandler

import time

from config import Config


class TelegramCommandHandler:

    time_manager: TimeManager = TimeManager(
            time_zone=Config.time_zone,
            input_time_format=Config.input_time_format,
            output_time_format=Config.output_time_format
        )

    auto_reg_system: AutoRegistrationSystem = AutoRegistrationSystem(
        admins=Config.admins,
        chat_ids=Config.chat_ids,
        alias_file_name=Config.alias_file_name,
        time_manager=time_manager,
    )

    tracer: Tracer = Tracer(
        log_file_name=Config.log_file_name,
        history_file_name=Config.history_file_name,
        time_manager=time_manager
    )

    data_handler: DataHandler = DataHandler(
        directory_data=Config.directory_data,
        file_main_list=Config.file_name_main_list,
        file_release_time=Config.file_name_release_time,
        file_pre_released_list=Config.file_name_pre_released_list
    )

    @staticmethod
    def initialize():
        try:
            main_list_as_str, release_time_as_str, pre_released_list_str = (TelegramCommandHandler
                                                                            .data_handler
                                                                            .read_data_from_files()
                                                                            )
            print("Main List:")
            print(main_list_as_str)
            try:
                TelegramCommandHandler.auto_reg_system.handle_new(
                    username="*",  # special username for enforcing admin
                    message=f"/{TelegramCommandHandler.COMMAND_NEW} {main_list_as_str}",
                    chat_id=Config.default_chat_id
                )
                print("Main list is loaded successfully!")
            except Exception:
                print("Unable to load main list! Main list is reset to be empty!")

            print("------------------------------------------")
            print(f"Release time: {release_time_as_str}")
            try:
                message = TelegramCommandHandler.auto_reg_system.handle_notitime(
                    username="*",  # special username for enforcing admin
                    message=f"/{TelegramCommandHandler.COMMAND_NOTITIME} {release_time_as_str}",
                    time_manager=TelegramCommandHandler.time_manager
                )
                print(f"{message}")
            except Exception:
                print("Unable to load release time! Release time is set to be None!")

            print(TelegramCommandHandler.auto_reg_system.release_time_manager.release_time)

            print("------------------------------------------")
            print("Pre-released list:")
            print(pre_released_list_str)
            try:
                TelegramCommandHandler.auto_reg_system.handle_new(
                    username="*",  # special username for enforcing admin
                    message=f"/{TelegramCommandHandler.COMMAND_NEW} {pre_released_list_str}",
                    chat_id=0,  # chat_id is set for making pre-released list
                )
                print(TelegramCommandHandler.auto_reg_system.get_all_slots_as_string(is_main_data=False))
                print("Pre-released list is loaded successfully!")
            except Exception:
                print("Unable to load pre-released list! Pre-released list is reset to be empty!")
        except Exception:
            print("No data or error data in files!")


    NUM_BUTTONS_PER_LINE = 3

    last_chat_id = None
    last_message_id = None

    last_av_chat_id = None
    last_av_message_id = None

    COMMAND_START = "start"
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
    COMMAND_RESET = "reset"
    COMMAND_NOTITIME = "notitime"
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
    def make_callback_data_for_drg_for_specific_slot(telegram_id: int, slot_label: str) -> str:
        return f"{TelegramCommandHandler.CALLBACK_DATA_DRG} {telegram_id} {slot_label}"

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
        button_list.append([
            InlineKeyboardButton(
                text="Hủy đăng kí",
                callback_data=TelegramCommandHandler.CALLBACK_DATA_DRG
            )
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
    def is_callback_data_drg_initial(query_data: str) -> bool:
        return query_data == TelegramCommandHandler.CALLBACK_DATA_DRG

    @staticmethod
    def is_callback_data_drg_for_specific_slot(query_data: str) -> bool:
        callback_data_drg_len = len(TelegramCommandHandler.CALLBACK_DATA_DRG)
        return (len(query_data) > callback_data_drg_len
                and query_data[:callback_data_drg_len] == TelegramCommandHandler.CALLBACK_DATA_DRG)

    @staticmethod
    async def run_button_drg_initially(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
        inline_button_list = None
        id_string = TelegramCommandHandler.get_id_string_from_telegram_user(user=query.from_user)
        slots_able_to_be_deregistered = DeregHandler.search_for_slots_able_to_be_deregistered(
            id_string=id_string,
            data=TelegramCommandHandler.auto_reg_system.data
        )
        response = f""
        clickable_link_for_telegram_id: str = StringParser.make_clickable_link_for_telegram_id(
            telegram_id=query.from_user.id,
            full_name=query.from_user.full_name
        )

        alias_or_full_name = TelegramCommandHandler.auto_reg_system.identity_manager.get_alias_or_full_name(
            telegram_id=query.from_user.id,
            full_name=StringParser.process_telegram_full_name(telegram_full_name=query.from_user.full_name)
        )
        if len(slots_able_to_be_deregistered) > 0:
            response += (f"Những slot có thể hủy đăng kí cho {clickable_link_for_telegram_id} "
                         + f"với tên/alias {StringParser.replace_escape_characters_for_markdown(alias_or_full_name)}")
            button_list = []
            current_line_button_list = None
            button_count = 0
            for slot_label, slot in slots_able_to_be_deregistered:
                button = InlineKeyboardButton(
                    text=f"slot {slot_label}",
                    callback_data=TelegramCommandHandler.make_callback_data_for_drg_for_specific_slot(
                        telegram_id=query.from_user.id,
                        slot_label=slot_label
                    )
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
            inline_button_list = InlineKeyboardMarkup(inline_keyboard=button_list)
        else:
            response += (f"Không có slot nào cho {clickable_link_for_telegram_id} "
                         + f"\\(với tên/alias {StringParser.replace_escape_characters_for_markdown(alias_or_full_name)}\\) để hủy đăng kí\\!")

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=response,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_button_list
        )

    @staticmethod
    async def run_button_drg_for_specific_slot(
            context: ContextTypes.DEFAULT_TYPE,
            from_chat_id: int,
            from_message_id: int,
            sender: User,
            query_data: str,
            id_string: str,
            identity_message: str
    ):
        clickable_link_for_sender_telegram_id: str = StringParser.make_clickable_link_for_telegram_id(
            telegram_id=sender.id,
            full_name=sender.full_name
        )

        callback_data = StringParser.remove_first_word(message=query_data)
        enforced_telegram_id = int(StringParser.get_first_word(message=callback_data))
        if enforced_telegram_id != sender.id:
            await context.bot.send_message(
                chat_id=from_chat_id,
                text=f"{clickable_link_for_sender_telegram_id} "
                     + "không được phép hủy đăng kí giúp thành viên khác bằng cách này\\!",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
        slot_label = StringParser.remove_first_word(message=callback_data)
        message = f"/{TelegramCommandHandler.COMMAND_DRG} {id_string} {slot_label}"
        res = await context.bot.send_message(
            chat_id=from_chat_id,
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
        await TelegramCommandHandler.run_dereg(
            update=Update(update_id=res.id, message=new_message),
            context=context,
            effective_user=sender
        )
        try:
            await context.bot.deleteMessage(
                message_id=from_message_id,
                chat_id=from_chat_id
            )
        except Exception:
            TelegramCommandHandler.log_message(message="Failed to delete previous message!")

    @staticmethod
    async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        id_string = TelegramCommandHandler.get_id_string_from_telegram_user(user=query.from_user)
        clickable_link_for_telegram_id: str = StringParser.make_clickable_link_for_telegram_id(
            telegram_id=query.from_user.id,
            full_name=query.from_user.full_name
        )
        identity_message = f"\\(from {clickable_link_for_telegram_id}\\)"

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
            return
        elif TelegramCommandHandler.is_callback_data_drg_initial(query_data=query.data):
            await TelegramCommandHandler.run_button_drg_initially(query=query, context=context)
            return
        elif TelegramCommandHandler.is_callback_data_drg_for_specific_slot(query_data=query.data):
            await TelegramCommandHandler.run_button_drg_for_specific_slot(
                context=context,
                from_chat_id=query.message.chat.id,
                from_message_id=query.message.message_id,
                sender=query.from_user,
                query_data=query.data,
                id_string=id_string,
                identity_message=identity_message
            )
            return

    @staticmethod
    async def write_data_and_update_bot_message_for_full_list(
            update: Update or None,
            context: ContextTypes.DEFAULT_TYPE,
            message: str or None,
            parse_mode: ParseMode or None = None,
            is_main_data: bool = True,
    ):
        all_slots_as_string = TelegramCommandHandler.auto_reg_system.get_all_slots_as_string(is_main_data=is_main_data)

        # sends all slots to chat
        new_chat_id = None
        new_message_id = None
        if all_slots_as_string is not None:
            inline_buttons: InlineKeyboardMarkup = TelegramCommandHandler.make_inline_buttons_for_registration(
                data=TelegramCommandHandler.auto_reg_system.data
            ) if is_main_data else None
            sent_message_info = await TelegramCommandHandler.reply_message(
                update=update,
                text=all_slots_as_string,
                reply_markup=inline_buttons
            ) if update is not None else await context.bot.send_message(
                chat_id=Config.default_chat_id,
                text=all_slots_as_string,
                reply_markup=inline_buttons
            )
            new_chat_id = sent_message_info.chat_id
            new_message_id = sent_message_info.message_id
            TelegramCommandHandler.tracer.log(
                message=f"(from system) \n{all_slots_as_string}"
            )
        else:
            to_be_sent_text = "Danh sách chơi trống!"
            await TelegramCommandHandler.reply_message(
                update=update, text=to_be_sent_text
            ) if update is not None else await context.bot.send_message(
                chat_id=Config.default_chat_id,
                text=to_be_sent_text
            )

        # inform message
        if message is not None and is_main_data:
            await TelegramCommandHandler.reply_message(
                update=update,
                text=message,
                parse_mode=parse_mode
            ) if update is not None else await context.bot.send_message(
                chat_id=Config.default_chat_id,
                text=message,
                parse_mode=parse_mode
            )

        # delete previous message
        if is_main_data:
            if TelegramCommandHandler.last_chat_id is not None and TelegramCommandHandler.last_message_id is not None:
                try:
                    await context.bot.deleteMessage(
                        message_id=TelegramCommandHandler.last_message_id,
                        chat_id=TelegramCommandHandler.last_chat_id
                    )
                except Exception:
                    TelegramCommandHandler.log_message(message="Failed to delete previous message!")
            TelegramCommandHandler.last_chat_id = new_chat_id
            TelegramCommandHandler.last_message_id = new_message_id

        # write all data to file
        TelegramCommandHandler.auto_reg_system.write_all_data_to_files(data_handler=TelegramCommandHandler.data_handler)

    @staticmethod
    def log_message_from_user(update: Update, is_history_required: bool = True):
        TelegramCommandHandler.tracer.log(
            message=f"(from {TelegramCommandHandler.get_id_string_from_telegram_user(user=update.message.from_user)})"
                    + f" {update.message.text}",
            is_history_required=is_history_required
        )

    @staticmethod
    def log_message(message: str):
        TelegramCommandHandler.tracer.log(message=message)

    @staticmethod
    async def run_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        TelegramCommandHandler.log_message_from_user(update=update)
        TelegramCommandHandler.run_job_for_release(context=context)
        await TelegramCommandHandler.reply_message(
            update=update,
            text="Checked and started all potential jobs!"
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
                TelegramCommandHandler.log_message(message="Failed to delete message!")

        # record id of current message
        if new_av_chat_id is not None and new_av_message_id is not None:
            TelegramCommandHandler.last_av_chat_id = new_av_chat_id
            TelegramCommandHandler.last_av_message_id = new_av_message_id

    @staticmethod
    async def run_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
        (message, is_in_main_group) = TelegramCommandHandler.auto_reg_system.handle_new(
            username=update.effective_user.username,
            message=update.message.text,
            chat_id=update.message.chat_id
        )
        TelegramCommandHandler.log_message_from_user(update=update, is_history_required=is_in_main_group)
        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=message,
            is_main_data=is_in_main_group
        )
        if not is_in_main_group:
            await TelegramCommandHandler.reply_message(
                update=update,
                text="This is pre-released list, not public yet!"
            )
            if TelegramCommandHandler.auto_reg_system.release_time_manager.enabled:
                await TelegramCommandHandler.reply_message(
                    update=update,
                    text=f"✅ The intended release time is {
                        TelegramCommandHandler.auto_reg_system.release_time_manager.release_time_to_str()
                    }"
                )
            else:
                await TelegramCommandHandler.reply_message(
                    update=update,
                    text="❌ Please set up release time!"
                )

    @staticmethod
    def remove_jobs(name: str, context: ContextTypes.DEFAULT_TYPE):
        jobs = context.job_queue.get_jobs_by_name(name=name)
        for job in jobs:
            job.schedule_removal()

    @staticmethod
    async def attempt_release_data(context: ContextTypes.DEFAULT_TYPE) -> None:
        # print(f"Beep!")
        if TelegramCommandHandler.auto_reg_system.attempt_release_data():
            TelegramCommandHandler.remove_jobs(name=Config.job_name_for_release, context=context)
            await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
                update=None,
                context=context,
                message="Danh sách vừa được cập nhật!"
            )

    @staticmethod
    def run_job_for_release(context: ContextTypes.DEFAULT_TYPE):
        TelegramCommandHandler.remove_jobs(name=Config.job_name_for_release, context=context)
        if TelegramCommandHandler.auto_reg_system.release_time_manager.enabled:
            context.job_queue.run_repeating(
                callback=TelegramCommandHandler.attempt_release_data,
                interval=Config.repeating_interval_for_release,
                name=Config.job_name_for_release,
            )

    @staticmethod
    async def run_notitime(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = TelegramCommandHandler.auto_reg_system.handle_notitime(
            username=update.effective_user.username,
            message=update.message.text,
            time_manager=TelegramCommandHandler.time_manager,
        )
        await TelegramCommandHandler.reply_message(
            update=update,
            text=message
        )
        TelegramCommandHandler.run_job_for_release(context=context)

        # write all data to file
        TelegramCommandHandler.auto_reg_system.write_all_data_to_files(data_handler=TelegramCommandHandler.data_handler)

    @staticmethod
    async def run_reset(update: Update, _):
        TelegramCommandHandler.log_message_from_user(update=update)
        message = TelegramCommandHandler.auto_reg_system.handle_reset(
            username=update.effective_user.username
        )
        await TelegramCommandHandler.reply_message(
            update=update,
            text=message
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
        response += f"/{TelegramCommandHandler.COMMAND_AKA} [alias]\t(người dùng tự cài đặt alias)\n"
        response += f"/{TelegramCommandHandler.COMMAND_AKA}\t(người dùng xem alias của chính mình)\n"
        response += f"\n"
        response += f"Các lệnh rút ngắn:\n"
        response += f"/{TelegramCommandHandler.COMMAND_RG}\t(giống như /reg)\n"
        response += f"/{TelegramCommandHandler.COMMAND_DRG}\t(giống như /dereg)\n"
        response += f"/{TelegramCommandHandler.COMMAND_RS}\t(giống như /reserve)\n"
        response += f"\n"
        response += f"Hướng dẫn chi tiết: https://hackmd.io/@1UKfawZER96uwy_xohcquQ/B1fyW-c4R"
        await TelegramCommandHandler.reply_message(update=update, text=response)
