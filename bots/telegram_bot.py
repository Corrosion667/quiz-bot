"""Module for telegram implementation of quiz bot."""

import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Greet the user. Handler for /start command.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.
    """
    user = update.effective_user
    incoming_message = update.message
    if incoming_message is None or user is None:
        return
    incoming_message.reply_text(f'Hello, {user.first_name}!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.
    """
    incoming_message = update.message
    if incoming_message is None or incoming_message.text is None:
        return
    incoming_message.reply_text(incoming_message.text)


def main() -> None:
    """Run the bot as script."""
    logging.basicConfig(
        format='TELEGRAM_BOT %(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO,
    )
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo,
    ))
    updater.start_polling()
    logger.info('Bot started.')
    updater.idle()


if __name__ == '__main__':
    main()
