#!/usr/bin/env python

import logging
import requests
import json

from telegram import ForceReply, Update, LoginUrl, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

base_url = f"https://opensplitbackend.onrender.com/"

# States for add expense dialog
NAME, PAYER, AMOUNT, RECEIVERS = range(4)


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_type = update.message.chat.type
    if chat_type == "private":
        username = update.message.from_user.username
        url = f"{base_url}users/@{username}/balance"
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"{response.status_code}:{response.text}")
            await update.message.reply_text(f"Error obtaining {username} balance. Please try again later.",
                                            do_quote=False)
        else:
            balance = response.json()
            message = format_user_balance(balance)
            await update.message.reply_text(message, do_quote=False)
    else:
        group_id = update.message.chat["id"]
        url = f"{base_url}groups/{group_id}/balance"
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"{response.status_code}:{response.text}")
            await update.message.reply_text("Error obtaining group balance. Please try again later.",
                                            do_quote=False)
        else:
            balance = response.json()
            message = format_balance(balance)
            await update.message.reply_text(message, do_quote=False)


def format_user_balance(balance: dict):
    if not balance:
        return "You don't belong to any group account."
    else:
        message = ""
        for g, d in balance.items():
            message += f"Group \"{g}\": {d:.2f}€\n"
        return message


def format_balance(balance: dict):
    if all(x == 0 for x in balance.values()):
        return "The group account is balanced."
    else:
        message = ""
        users_who_owe = {n: b for n, b in balance.items() if b < 0}
        users_who_are_owed = {n: b for n, b in balance.items() if b > 0}
        users_in_balance = {n: b for n, b in balance.items() if b == 0}
        if users_who_owe:
            message += "Users who owe money:\n"
            for n, b in users_who_owe.items():
                message += f"{n} : {b:.2f}€\n"
        if users_who_are_owed:
            message += "Users who are owed money:\n"
            for n, b in users_who_are_owed.items():
                message += f"{n} : {b:.2f}€\n"
        if users_in_balance:
            message += "Users who don't owe and aren't owed:\n"
            for n, b in users_in_balance.items():
                message += f"{n} : {b:.2f}€\n"
        return message


async def calculate_exchanges(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mock_content = [{"payer": "@DaniPVargas", "receiver": "@sergioalvper", "amount": 36.5},
                    {"payer": "@CastilloDel", "receiver": "@AntonGomez", "amount": 34.2}]
    chat_type = update.message.chat.type
    if chat_type == "private":
        await update.message.reply_text("Sorry, this function is only available for group chats.")
    else:
        group_id = update.message.chat["id"]
        url = f"{base_url}groups/{group_id}/exchanges"
        headers = {"Content-Type": "application/json"}
        # response = requests.get(url, headers=headers)
        if 200 != 200:  # response.status_code != 200:
            # logger.error(f"{response.status_code}:{response.text}")
            await update.message.reply_text("Error obtaining group exchanges. Please try again later.",
                                            do_quote=False)
        else:
            # exchanges = response.json()
            exchanges = mock_content
            message = format_exchanges(exchanges)
            await update.message.reply_text(message, do_quote=False)


def format_exchanges(exchanges):
    if not exchanges:
        return "No money exchanges are needed."
    else:
        message = "The following exchanges are needed to balance the group account:\n"
        for exchange in exchanges:
            message += f"· {exchange['payer']} owes {exchange['amount']
                :.2f}€ to {exchange['receiver']}\n"
        return message


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open('help.json', "r") as fp:
        data = json.load(fp)

    message = f"{data['message']}\n\n"
    for command in data["commands"].keys():
        message += f"/{command}: {data['commands'][command]}\n"

    await update.message.reply_text(f"{message}", do_quote=False)


async def register_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for member in update.message.new_chat_members:
        if member.username == "opensplit_bot":
            group_id = update.message.chat["id"]
            data = {"name": update.message.chat["title"]}
            headers = {"Content-Type": "application/json"}
            url = f"{base_url}groups/{group_id}"
            response = requests.put(
                url, headers=headers, data=json.dumps(data))
            if response.status_code != 200:
                logger.error(f"{response.status_code}:{response.text}")
                message = "Error adding group to OpenSplit. Please try it again later."
            else:
                message = f"{
                    update.message.chat['title']} has been added to OpenSplit."
            await update.message.reply_text(message, do_quote=False)


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_type = update.message.chat.type
    if chat_type == "private":
        await update.message.reply_text("Sorry, this function is only available for group chats.", do_quote=False)
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
    context.chat_data['amount'] = float(
        update.message.text.replace(",", ".").replace("€", ""))
    await update.message.reply_text(f"We are almost done! Finally, Enter the users to whom {context.chat_data['payer']} has paid, separated by spaces. Remember to mention them using @.",
                                    reply_markup=ForceReply(selective=True))
    return RECEIVERS


async def receivers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['receivers'] = list(set([update.message.parse_entity(
        x) for x in update.message.entities if x.type == "mention"]))
    body = {"name": context.chat_data['name'], "payer": context.chat_data['payer'],
            "amount": context.chat_data['amount'], "receivers": context.chat_data["receivers"]}
    group_id = update.message.chat["id"]
    headers = {"Content-Type": "application/json"}
    url = f"{base_url}groups/{group_id}/expenses"
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code != 200:
        logger.error(f"{response.status_code}:{response.text}")
        message = "Error adding the new expense. Please try again later."
    else:
        message = "The new expense has been added correctly."
    await update.message.reply_text(message, do_quote=False)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("The expense addition has been canceled")
    return ConversationHandler.END


async def handle_unexpected_input(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("I can't understand you. Please check the format of your message and answer again.",
                                    reply_markup=ForceReply(selective=True))
    return


async def web_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [[InlineKeyboardButton("Login in web", login_url=LoginUrl("https://opensplit.onrender.com/home"))]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Click the button to log in:", reply_markup=reply_markup)

    pass


def main() -> None:
    with open('BOT_API_KEY', "r") as fp:
        token = fp.read()
    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_expense", add_expense)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PAYER: [MessageHandler(filters.TEXT & filters.Entity("mention"), payer)],
            AMOUNT: [MessageHandler(filters.TEXT & filters.Regex(r"^(?:[1-9]\d*|0)?(?:[.,]\d+)?€?$"), amount)],
            RECEIVERS: [MessageHandler(filters.TEXT & filters.Entity("mention"), receivers)],
        },
        fallbacks=[CommandHandler("cancel", cancel),
                   MessageHandler(filters.ALL, handle_unexpected_input)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler(
        "calculate_exchanges", calculate_exchanges))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, register_group))
    application.add_handler(CommandHandler("web_login", web_login))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
