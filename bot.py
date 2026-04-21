from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8742040135:AAFlkhkICLDT2eijOw6F47IWuXQg5a4BR2o"

# 🔥 Welcome Message (with name)
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        name = user.first_name

        await update.message.reply_text(
            f"Welcome, {name}.\n\n"
            "Welcome to this establishment.\n\n"
            "I am entrusted with maintaining order and ensuring your experience here remains… pleasant.\n\n"
            "Should you require assistance, I am here to attend to your generous requests.\n\n"
            "Please do keep in mind—\n"
            "You are a guest within this space.\n"
            "Conduct yourself with proper grace and respect toward others, as any form of misconduct shall not be tolerated.\n\n"
            "I would suggest you begin with /start for a more refined introduction and understanding of your place here,\n"
            "and /help should you require any assistance at all.\n\n"
            "Now then… do enjoy your stay."
        )

# ⚡ /ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am present.")

# 👤 /info (works on self or reply)
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    else:
        user = update.message.from_user

    name = user.first_name
    username = f"@{user.username}" if user.username else "No username"

    await update.message.reply_text(
        f"Name: {name}\nUsername: {username}\nID: {user.id}"
    )

# 👑 /admins
async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    names = [admin.user.first_name for admin in chat_admins]

    await update.message.reply_text(
        "Overseers of this establishment:\n" + "\n".join(names)
    )

# 🚨 /report
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        reported_user = update.message.reply_to_message.from_user.first_name
        await update.message.reply_text(
            f"{reported_user} has been reported. The matter shall be observed."
        )
    else:
        await update.message.reply_text(
            "Reply to a message if you wish to report someone."
        )

# 🔧 Run bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("admins", admins))
app.add_handler(CommandHandler("report", report))

app.run_polling()