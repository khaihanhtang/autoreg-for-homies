from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from auto_registration_system.auto_registration_system import AutoRegistrationSystem

token: str = input("Enter bot token: ")

auto_reg_system = AutoRegistrationSystem()


async def run_hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def run_retrieve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(auto_reg_system.handle_retrieve(
        username=update.effective_user.username,
        message=update.message.text
    ))


async def run_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(auto_reg_system.handle_new(
        username=update.effective_user.username,
        message=update.message.text
    ))


async def run_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(auto_reg_system.handle_reg(
        username=update.effective_user.username,
        message=update.message.text
    ))


async def run_reserve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(auto_reg_system.handle_reserve(
        username=update.effective_user.username,
        message=update.message.text
    ))


async def run_dereg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(auto_reg_system.handle_dereg(
        username=update.effective_user.username,
        message=update.message.text
    ))


async def run_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(auto_reg_system.handle_admin(
        username=update.effective_user.username,
        message=update.message.text
    ))


async def run_allplayable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(auto_reg_system.handle_allplayable(
        username=update.effective_user.username,
        message=update.message.text
    ))


# /new: renew booking (beginning of the week), require admin privilege
# /rec: recall booking (when error happens, use this to recally by copying), require admin privilege
# /reg: register slot, for any user
# /dereg: deregister slot, for any user
# /help: guide for user

app = (
    ApplicationBuilder()
    .token(token)
    .read_timeout(60)
    .write_timeout(60)
    .build()
)

app.add_handler(CommandHandler("hello", run_hello))
app.add_handler(CommandHandler("retrieve", run_retrieve))
app.add_handler(CommandHandler("new", run_new))
app.add_handler(CommandHandler("reg", run_reg))
app.add_handler(CommandHandler("reserve", run_reserve))
app.add_handler(CommandHandler("dereg", run_dereg))
app.add_handler(CommandHandler("admin", run_admin))
app.add_handler(CommandHandler("allplayable", run_allplayable))

app.run_polling()
