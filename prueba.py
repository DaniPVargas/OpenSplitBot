#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

import logging
import requests

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Adding new expense...")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Showing balance...")

async def calculate_exchanges(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Calculate exchanges...")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("List of commands and descriptions")

def main() -> None:
    with open('BOT_API_KEY', "r") as fp:
        token = fp.read()
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("add_expense", add_expense))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("calculate_exchanges", calculate_exchanges))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()