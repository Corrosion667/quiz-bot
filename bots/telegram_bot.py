"""Module for telegram implementation of quiz bot."""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler, Updater,
)

from bots.settings import GREETING, HELP_TEXT, BotStates, ButtonText

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> Optional[int]:
    """Greet the user. Handler for /start command.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.

    Returns:
        Conversation state of command choosing.
    """
    user = update.effective_user
    incoming_message = update.message
    if incoming_message is None or user is None:
        return None
    keyboard_menu = [
        [ButtonText.NEW_QUESTION.value, ButtonText.GIVE_UP.value], [ButtonText.SCORE.value],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard_menu)
    incoming_message.reply_text(
        text=GREETING.format(user=user.first_name, help=HELP_TEXT),
        reply_markup=reply_markup,
    )
    return BotStates.CHOOSING.value


def help_user(update: Update, context: CallbackContext) -> None:
    """Send information with bot fucnions when the command /help is issued.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.
    """
    incoming_message = update.message
    if incoming_message is None:
        return
    incoming_message.reply_text(text=f'{HELP_TEXT}')


def handle_new_question_request(update: Update, context: CallbackContext) -> Optional[int]:
    """Send user a message.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.

    Returns:
        Conversation state of command choosing.
    """
    incoming_message = update.message
    if incoming_message is None or incoming_message.text is None:
        return None
    incoming_message.reply_text(incoming_message.text)
    return BotStates.CHOOSING.value


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.

    Returns:
        Ending conversation state.
    """
    return ConversationHandler.END


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
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BotStates.CHOOSING.value: [
                MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request),
                CommandHandler('help', help_user),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conversation_handler)
    updater.start_polling()
    logger.info('Bot started.')
    updater.idle()


if __name__ == '__main__':
    main()
