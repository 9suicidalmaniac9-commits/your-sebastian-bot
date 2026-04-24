from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import timedelta

TOKEN = "8742040135:AAEbiEGlWG5i3ejpU_bsSgjH97u792OIkSE"

# ================= OLD COMMANDS (UNCHANGED STYLE) =================

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        text = f"""Welcome, {user.first_name}

Welcome to this establishment.

I am entrusted with maintaining order and ensuring your experience here remains… pleasant.

Should you require assistance, I am here to attend to your generous requests.

Please do keep in mind—
You are a guest within this space.
Conduct yourself with proper grace and respect toward others, as any form of misconduct shall not be tolerated.

I would suggest you begin with /start for a more refined introduction and understanding of your place here,
and /help should you require any assistance at all.

Now then… do enjoy your stay."""
        await update.message.reply_text(text)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am present.")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.message.from_user
    await update.message.reply_text(
        f"User information:\n\n"
        f"Name: {user.first_name}\n"
        f"ID: {user.id}\n"
        f"Username: @{user.username if user.username else 'Not available'}"
    )

async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    names = [a.user.first_name for a in admins]
    await update.message.reply_text(
        "Overseers of this establishment:\n\n" + "\n".join(names)
    )


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        await update.message.reply_text(
            "The matter has been noted.\n\nIt will be observed and handled accordingly."
        )
    else:
        await update.message.reply_text(
            "Kindly reply to the message you wish to bring to attention."        

# ================= SEBASTIAN SYSTEM =================

warnings = {}

async def is_protected(user_id, chat):
    admins = await chat.get_administrators()
    return user_id in [a.user.id for a in admins]

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """Welcome.

I am your devoted attendant—refined, composed, and ever at your service.

I carry out requests with precision and quiet efficiency, maintaining a certain standard within this establishment. You may find me, at times, a hell of a butler when such standards are concerned.

This space is kept composed by design. You are free to take part, provided you understand how to conduct yourself accordingly.

For a complete outline of how things function here, including commands and their proper use, you are advised to proceed with /help.

Now then… do behave appropriately."""
    await update.message.reply_text(text)

# HELP
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """Command Directory:

— Basic  
/ping — confirm presence  
/info — view user details  
/admins — list administrators  

— Interaction  
/report — bring a matter to attention (reply required)  

— Moderation  
/warn — issue a notice  
/warnings — view notice count  
/mute — restrict a user temporarily  
/unmute — restore ability to speak  

— Administrative  
/ban — remove a user (admin only)  
/unban — allow return (admin only)  

—

Response to /help.

Commands are to be used with awareness and restraint."""
    await update.message.reply_text(text)

# WARN SYSTEM (12h mute + auto ban)
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user
    chat = update.effective_chat

    if await is_protected(user.id, chat):
        await update.message.reply_text("That action is not within your reach.")
        return

    warnings[user.id] = warnings.get(user.id, 0) + 1
    count = warnings[user.id]

    mute_until = update.message.date + timedelta(hours=12)

    if count == 1:
        await chat.restrict_member(user.id, ChatPermissions(can_send_messages=False), until_date=mute_until)
        await update.message.reply_text(
            "Consider this a formal notice.\n\nI would prefer not to repeat myself over matters of basic conduct.\n\nYou will remain silent for a while."
        )

    elif count == 2:
        await update.message.reply_text(
            "You have already been addressed once.\n\nI trust I do not need to explain this again.\n\nAdjust yourself accordingly."
        )

    elif count >= 3:
        await chat.ban_member(user.id)
        await update.message.reply_text(
            "You were given sufficient opportunity.\n\nEven a butler has limits.\n\nThis concludes your presence here."
        )

# WARNINGS
async def warnings_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user
    count = warnings.get(user.id, 0)

    if count == 0:
        await update.message.reply_text(
            "No notices have been issued.\n\nDo see that it remains that way."
        )
    else:
        await update.message.reply_text(
            f"Current standing: {count} notice(s).\n\nI would advise not increasing that number."
        )

# MUTE
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user
    chat = update.effective_chat

    if await is_protected(user.id, chat):
        await update.message.reply_text("That action is not within your reach.")
        return

    mute_until = update.message.date + timedelta(hours=12)

    await chat.restrict_member(user.id, ChatPermissions(can_send_messages=False), until_date=mute_until)

    await update.message.reply_text(
        "That will be sufficient.\n\nYou will remain silent for a while.\n\nDo consider your approach when you return."
    )

# UNMUTE
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user

    await update.effective_chat.restrict_member(user.id, ChatPermissions(can_send_messages=True))

    await update.message.reply_text(
        "You may proceed again.\n\nDo ensure the previous inconvenience is not repeated."
    )

# BAN (ADMIN ONLY)
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user
    chat = update.effective_chat

    admins = await chat.get_administrators()
    admin_ids = [a.user.id for a in admins]

    if update.message.from_user.id not in admin_ids:
        return

    if user.id in admin_ids:
        await update.message.reply_text("That action is not within your reach.")
        return

    await chat.ban_member(user.id)

    await update.message.reply_text(
        "Your presence is no longer required.\n\nYou’ve exceeded what was permitted.\n\nThis matter is concluded."
    )

# UNBAN
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        return

    user_id = int(context.args[0])

    await update.effective_chat.unban_member(user_id)

    await update.message.reply_text(
        "You have been allowed back.\n\nDo not misunderstand this as leniency."
    )

# ================= HANDLERS =================

app = ApplicationBuilder().token(TOKEN).build()

# OLD
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("admins", admins))
app.add_handler(CommandHandler("report", report))

# NEW (separate group)
app.add_handler(CommandHandler("start", start), group=1)
app.add_handler(CommandHandler("help", help_command), group=1)
app.add_handler(CommandHandler("warn", warn), group=1)
app.add_handler(CommandHandler("warnings", warnings_check), group=1)
app.add_handler(CommandHandler("mute", mute), group=1)
app.add_handler(CommandHandler("unmute", unmute), group=1)
app.add_handler(CommandHandler("ban", ban), group=1)
app.add_handler(CommandHandler("unban", unban), group=1)

app.run_polling()
