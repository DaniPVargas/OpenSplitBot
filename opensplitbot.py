#!/usr/bin/env python

import logging
import requests
import json

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

backend_ip = "127.0.0.1"
backend_port = "8080"
base_url = f"http://{backend_ip}:{backend_port}"
groups_base_url = f"{base_url}/groups"

# States for add expense dialog
NAME, PAYER, AMOUNT, RECEIVERS = range(4)


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_type = update.message.chat.type
    if chat_type == "private":
        username = update.message.from_user.username
        await update.message.reply_text(f"TODO: Obtain balance for {username}")
        #url = f"{groups_base_url}/{group_id}/balance"
        #requests.get(url)
    else:
        group_id = update.message.chat["id"]
        await update.message.reply_text(f"TODO: Obtain balance for group {group_id}")
        #url = f"{groups_base_url}/{group_id}/balance"
        #requests.get(url)


async def calculate_exchanges(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_type = update.message.chat.type
    if chat_type == "private":
        await update.message.reply_text("Sorry, this function is only available for group chats.")
    else:
        group_id = update.message.chat["id"]
        await update.message.reply_text("Calculate exchanges...")
        url = f"{groups_base_url}/{group_id}/balance"
        # requests.get(url)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open('help.json', "r") as fp:
        data = json.load(fp)
    
    message = f"{data["message"]}\n\n"
    for command in data["commands"].keys():
        message += f"/{command}: {data["commands"][command]}\n"
        
    await update.message.reply_text(f"{message}", do_quote=False)


async def register_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for member in update.message.new_chat_members:
        if member.username == "opensplit_bot":
            group_id = update.message.chat["id"]
            data = {"name": update.message.chat["title"]}
            url = f"{groups_base_url}/{group_id}"
            # requests.put(url, data=data)
            await update.message.reply_text(f"{update.message.chat["title"]} added to OpenSplit.", do_quote=False)


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_type = update.message.chat.type
    if chat_type == "private":
        await update.message.reply_text("Sorry, this function is only available for group chats.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please, enter the name of the new expense.", reply_markup=ForceReply(selective=True))
        return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['name'] = update.message.text
    await update.message.reply_text('Okay, now enter the user who has paid the expense. Please, remember to mention them using @.',
                                    reply_markup=ForceReply(selective=True))
    return PAYER


async def payer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['payer'] = update.message.parse_entity(
        update.message.entities[0])
    await update.message.reply_text('Perfect! Now enter the amount that was paid.',
                                    reply_markup=ForceReply(selective=True))
    return AMOUNT


async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['amount'] = float(update.message.text.replace(",", "."))
    await update.message.reply_text(f'We are almost done! Finally, Enter the users to whom {context.chat_data['payer']} has paid, separated by spaces. Remember to mention them using @.',
                                    reply_markup=ForceReply(selective=True))
    return RECEIVERS


async def receivers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['receivers'] = list(set([update.message.parse_entity(
        x) for x in update.message.entities if x.type == "mention"]))
    body = {"name": context.chat_data['name'], "payer": context.chat_data['payer'],
            "amount": context.chat_data['amount'], "receivers": context.chat_data["receivers"]}
    group_id = update.message.chat["id"]
    url = f"{groups_base_url}/{group_id}/expenses"
    # requests.post(url, data = body)
    await update.message.reply_text(f"{body}")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("The expense addition has been canceled")
    return ConversationHandler.END


async def handle_unexpected_input(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("I can't understand you. Please check the format of your message and answer again.",
                                    reply_markup=ForceReply(selective=True))
    return 


def main() -> None:
    with open('BOT_API_KEY', "r") as fp:
        token = fp.read()
    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_expense", add_expense)],
        states={
            NAME: [MessageHandler((filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) & filters.TEXT & ~filters.COMMAND, name)],
            PAYER: [MessageHandler((filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) & filters.TEXT & filters.Entity("mention"), payer)],
            AMOUNT: [MessageHandler((filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) & filters.TEXT & filters.Regex(r"^(?:[1-9]\d*|0)?(?:[.,]\d+)?€?$"), amount)],
            RECEIVERS: [MessageHandler((filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) & filters.TEXT & filters.Entity("mention"), receivers)],
        },
        fallbacks=[CommandHandler("cancel", cancel),
                   MessageHandler(filters.ALL , handle_unexpected_input)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler(
        "calculate_exchanges", calculate_exchanges))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, register_group))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
