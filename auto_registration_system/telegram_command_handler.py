from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from auto_registration_system.auto_registration_system import AutoRegistrationSystem
from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.string_parser.string_parser import StringParser


class TelegramCommandHandler:

    auto_reg_system = AutoRegistrationSystem()

    NUM_BUTTONS_PER_LINE = 3

    last_chat_id = None
    last_message_id = None

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
    COMMAND_HELP = "help"
    CALLBACK_DATA_HELP = f"_{COMMAND_HELP}"
    CALLBACK_DATA_ALL = f"_{COMMAND_ALL}"

    SECOND_CLICK_TO_DEREGISTER = False

    @staticmethod
    def make_inline_buttons_for_registration(data: RegistrationData) -> InlineKeyboardMarkup:
        button_count = 0
        button_list = []
        current_line_button_list = None
        for datevenue in data.bookings_by_datevenue:
            for slot_label in data.bookings_by_datevenue[datevenue]:
                button = InlineKeyboardButton(text=f"slot {slot_label}", callback_data=slot_label)
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
            InlineKeyboardButton(
                text=TelegramCommandHandler.COMMAND_ALL,
                callback_data=TelegramCommandHandler.CALLBACK_DATA_ALL
            ),
            InlineKeyboardButton(
                text=TelegramCommandHandler.COMMAND_HELP,
                callback_data=TelegramCommandHandler.CALLBACK_DATA_HELP
            ),
        ])
        return InlineKeyboardMarkup(inline_keyboard=button_list)

    @staticmethod
    async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        # handle special case for all and help
        if query.data == TelegramCommandHandler.CALLBACK_DATA_ALL:
            res = await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=f"/{TelegramCommandHandler.COMMAND_ALL}"
            )
            await TelegramCommandHandler.run_retrieve(update=Update(update_id=res.id, message=res), context=context)
            return
        elif query.data == TelegramCommandHandler.CALLBACK_DATA_HELP:
            res = await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=f"/{TelegramCommandHandler.COMMAND_HELP}"
            )
            await TelegramCommandHandler.run_help(update=Update(update_id=res.id, message=res), context=context)
            return

        # find full name
        full_name = query.from_user.full_name
        char_list = list(full_name)
        for i, c in enumerate(char_list):
            if c == ",":
                char_list[i] = ""
        full_name = StringParser.split_names(message="".join(char_list))[0]

        slot_label = query.data
        slot = TelegramCommandHandler.auto_reg_system.data.get_slot(slot_label=slot_label)

        if TelegramCommandHandler.SECOND_CLICK_TO_DEREGISTER:
            use_reg = False
            if not slot.is_in_any_list(proposed_name=full_name):
                use_reg = True
            if slot.is_in_reservations(proposed_name=full_name):
                reservation = slot.get_reservation(proposed_name=full_name)
                if not reservation.is_playable:
                    use_reg = True

            if use_reg:
                res = await context.bot.send_message(
                    chat_id=query.message.chat.id,
                    text=f"/{TelegramCommandHandler.COMMAND_REG} {full_name} {slot_label}"
                )
                await TelegramCommandHandler.run_reg(update=Update(update_id=res.id, message=res), context=context)
            else:
                res = await context.bot.send_message(
                    chat_id=query.message.chat.id,
                    text=f"/{TelegramCommandHandler.COMMAND_DEREG} {full_name} {slot_label}"
                )
                await TelegramCommandHandler.run_dereg(update=Update(update_id=res.id, message=res), context=context)
        else:
            res = await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=f"/{TelegramCommandHandler.COMMAND_REG} {full_name} {slot_label}"
            )
            await TelegramCommandHandler.run_reg(update=Update(update_id=res.id, message=res), context=context)

    @staticmethod
    async def write_data_and_update_bot_message_for_full_list(
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
            message: str or None
    ):
        all_slots_as_string = TelegramCommandHandler.auto_reg_system.get_all_slots_as_string()

        # sends all slots to chat
        new_chat_id = None
        new_message_id = None
        if all_slots_as_string is not None:
            sent_message_info = await update.message.reply_text(
                text=all_slots_as_string,
                reply_markup=TelegramCommandHandler.make_inline_buttons_for_registration(
                    data=TelegramCommandHandler.auto_reg_system.data
                )
            )
            new_chat_id = sent_message_info.chat_id
            new_message_id = sent_message_info.message_id
        else:
            await update.message.reply_text("Danh sách chơi trống!")

        # inform message
        if message is not None:
            await update.message.reply_text(message)

        # delete previous message
        if TelegramCommandHandler.last_chat_id is not None and TelegramCommandHandler.last_message_id is not None:
            try:
                await context.bot.deleteMessage(
                    message_id=TelegramCommandHandler.last_message_id,
                    chat_id=TelegramCommandHandler.last_chat_id
                )
            finally:
                pass
        TelegramCommandHandler.last_chat_id = new_chat_id
        TelegramCommandHandler.last_message_id = new_message_id

    @staticmethod
    async def run_hello(update: Update, _):
        print(update.message.text)
        await update.message.reply_text(f'Chào {update.effective_user.first_name}')

    @staticmethod
    async def run_retrieve(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=None
        )

    @staticmethod
    async def run_av(update: Update, _):
        await update.message.reply_text(TelegramCommandHandler.auto_reg_system.get_available_slots_as_string())

    @staticmethod
    async def run_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    async def run_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = TelegramCommandHandler.auto_reg_system.handle_reg(message=update.message.text)
        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=message
        )

    @staticmethod
    async def run_reserve(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = TelegramCommandHandler.auto_reg_system.handle_reserve(message=update.message.text)
        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=message
        )

    @staticmethod
    async def run_dereg(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = TelegramCommandHandler.auto_reg_system.handle_dereg(message=update.message.text)
        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=message
        )

    @staticmethod
    async def run_admin(update: Update, _):
        await update.message.reply_text(AutoRegistrationSystem.get_admin_list_as_string())

    @staticmethod
    async def run_command_not_found(update: Update, _):
        await update.message.reply_text("Sai lệnh!")

    @staticmethod
    async def run_allplayable(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = TelegramCommandHandler.auto_reg_system.handle_allplayable(
            username=update.effective_user.username,
            message=update.message.text
        )
        await TelegramCommandHandler.write_data_and_update_bot_message_for_full_list(
            update=update,
            context=context,
            message=message
        )

    @staticmethod
    async def run_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(response)