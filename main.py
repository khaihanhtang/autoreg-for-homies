from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler
from telegram.ext import filters
from auto_registration_system.auto_registration_system import AutoRegistrationSystem
from auto_registration_system.data_structure.registration_data import RegistrationData

token: str = input("Enter bot token: ")

auto_reg_system = AutoRegistrationSystem()
last_chat_id = None
last_message_id = None

def make_buttons_for_registration():
    dictionary = {"Name": "a", "Language": "b", "API": "c"}

    buttons = []

    for key, value in dictionary.items():
        buttons.append(
            [InlineKeyboardButton(text=key, callback_data=value)]
        )
    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    print(query)

    if query.data == "a":
        res = await context.bot.send_message(chat_id=query.message.chat.id, text="/reg Hanh f")
        await run_reg(update=Update(update_id=res.id, message=res), context=context)    # TODO: update_id needs to be changed to random integer


async def write_data_and_update_bot_message_for_full_list(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        message: str or None
):
    global last_chat_id, last_message_id
    all_slots_as_string = auto_reg_system.get_all_slots_as_string()

    # sends all slots to chat
    new_chat_id = None
    new_message_id = None
    if all_slots_as_string is not None:
        sent_message_info = await update.message.reply_text(text=all_slots_as_string, reply_markup=make_buttons_for_registration())
        new_chat_id = sent_message_info.chat_id
        new_message_id = sent_message_info.message_id
    else:
        await update.message.reply_text("Danh sách chơi trống!")

    # inform message
    if message is not None:
        await update.message.reply_text(message)

    # delete previous message
    if last_chat_id is not None and last_message_id is not None:
        try:
            await context.bot.deleteMessage(message_id=last_message_id, chat_id=last_chat_id)
        finally:
            pass
    last_chat_id = new_chat_id
    last_message_id = new_message_id


async def run_hello(update: Update, _):
    print(update.message.text)
    await update.message.reply_text(f'Chào {update.effective_user.first_name}')


async def run_retrieve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await write_data_and_update_bot_message_for_full_list(update=update, context=context, message=None)


async def run_av(update: Update, _):
    await update.message.reply_text(auto_reg_system.get_available_slots_as_string())


async def run_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = auto_reg_system.handle_new(
        username=update.effective_user.username,
        message=update.message.text
    )
    await write_data_and_update_bot_message_for_full_list(update=update, context=context, message=message)


async def run_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = auto_reg_system.handle_reg(message=update.message.text)
    await write_data_and_update_bot_message_for_full_list(update=update, context=context, message=message)


async def run_reserve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = auto_reg_system.handle_reserve(message=update.message.text)
    await write_data_and_update_bot_message_for_full_list(update=update, context=context, message=message)


async def run_dereg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = auto_reg_system.handle_dereg(message=update.message.text)
    await write_data_and_update_bot_message_for_full_list(update=update, context=context, message=message)


async def run_admin(update: Update, _):
    await update.message.reply_text(AutoRegistrationSystem.get_admin_list_as_string())


async def run_command_not_found(update: Update, _):
    await update.message.reply_text("Sai lệnh!")


async def run_allplayable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = auto_reg_system.handle_allplayable(
        username=update.effective_user.username,
        message=update.message.text
    )
    await write_data_and_update_bot_message_for_full_list(update=update, context=context, message=message)


async def run_help(update: Update, _):
    response: str = "Sử dụng những cú pháp sau:\n"
    response += f"/reg [tên 1], ..., [tên n] [slot]\t(đăng kí)\n"
    response += f"/dereg [tên 1], ..., [tên n] [slot]\t(hủy đăng kí)\n"
    response += f"/reserve [tên 1], ..., [tên n] [slot]\t(dự bị)\n"
    response += f"/retrieve\t(hiện đầy đủ danh sách)\n"
    response += f"/av\t(hiện các slot còn thiếu người)\n"
    response += f"\n"
    response += f"Các lệnh rút ngắn:\n"
    response += f"/rg\t(giống như /reg)\n"
    response += f"/drg\t(giống như /dereg)\n"
    response += f"/rs\t(giống như /reserve)\n"
    response += f"/all\t(giống như /retrieve)\n"
    response += f"\n"
    response += f"Hướng dẫn chi tiết: https://hackmd.io/@1UKfawZER96uwy_xohcquQ/B1fyW-c4R"
    await update.message.reply_text(response)


app = (
    ApplicationBuilder()
    .token(token)
    .read_timeout(60)
    .write_timeout(60)
    .build()
)

app.add_handler(CommandHandler("hello", run_hello))
app.add_handler(CommandHandler("retrieve", run_retrieve))
app.add_handler(CommandHandler("all", run_retrieve))    # same as /retrieve
app.add_handler(CommandHandler("new", run_new))
app.add_handler(CommandHandler("reg", run_reg))
app.add_handler(CommandHandler("rg", run_reg))  # same as /reg
app.add_handler(CommandHandler("reserve", run_reserve))
app.add_handler(CommandHandler("rs", run_reserve))  # same as /reserve
app.add_handler(CommandHandler("dereg", run_dereg))
app.add_handler(CommandHandler("drg", run_dereg))   # same as /drg
app.add_handler(CommandHandler("admin", run_admin))
app.add_handler(CommandHandler("av", run_av))
app.add_handler(CommandHandler("allplayable", run_allplayable))
app.add_handler(CommandHandler("help", run_help))
app.add_handler(MessageHandler(filters.COMMAND, run_command_not_found))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
