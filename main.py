from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler
from telegram.ext import filters
from auto_registration_system.auto_registration_system import AutoRegistrationSystem

token: str = input("Enter bot token: ")

auto_reg_system = AutoRegistrationSystem()


async def send_all_slots(update: Update):
    await update.message.reply_text(auto_reg_system.get_all_slots_as_string())


async def run_hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text)
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def run_retrieve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_all_slots(update=update)


async def run_av(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(auto_reg_system.get_available_slots_as_string())


async def run_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = auto_reg_system.handle_new(
        username=update.effective_user.username,
        message=update.message.text
    )
    await send_all_slots(update=update)
    await update.message.reply_text(message)


async def run_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = auto_reg_system.handle_reg(message=update.message.text)
    await send_all_slots(update=update)
    await update.message.reply_text(message)


async def run_reserve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = auto_reg_system.handle_reserve(message=update.message.text)
    await send_all_slots(update=update)
    await update.message.reply_text(message)


async def run_dereg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = auto_reg_system.handle_dereg(message=update.message.text)
    await send_all_slots(update=update)
    await update.message.reply_text(message)


async def run_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(AutoRegistrationSystem.get_admin_list_as_string())


async def run_command_not_found(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Command not found!")


async def run_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response: str = "Follow the following syntax:\n"
    response += f"/reg [name 1], ..., [name n] [slot] // register\n"
    response += f"/dereg [name 1], ..., [name n] [slot] // de-register\n"
    response += f"/reserve [name 1], ..., [name n] [slot] // reserve\n"
    response += f"/retrieve // show full list\n"
    response += f"/av // show available slots\n"
    response += f"\n"
    response += f"Shortened commands:\n"
    response += f"/rg: same as /reg\n"
    response += f"/drg: same as /dereg\n"
    response += f"/rs: same as /reserve\n"
    response += f"/all: same as /retrieve\n"
    response += f"\n"
    response += f"Detailed guide: https://hackmd.io/@1UKfawZER96uwy_xohcquQ/B1fyW-c4R"
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
app.add_handler(CommandHandler("all", run_retrieve)) # same as /retrieve
app.add_handler(CommandHandler("new", run_new))
app.add_handler(CommandHandler("reg", run_reg))
app.add_handler(CommandHandler("rg", run_reg)) # same as /reg
app.add_handler(CommandHandler("reserve", run_reserve))
app.add_handler(CommandHandler("rs", run_reserve)) # same as /reserve
app.add_handler(CommandHandler("dereg", run_dereg))
app.add_handler(CommandHandler("drg", run_dereg)) # same as /drg
app.add_handler(CommandHandler("admin", run_admin))
app.add_handler(CommandHandler("av", run_av))
app.add_handler(CommandHandler("help", run_help))
app.add_handler(MessageHandler(filters.COMMAND, run_command_not_found))

app.run_polling()
