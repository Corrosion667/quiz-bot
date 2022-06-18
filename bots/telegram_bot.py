"""Module for telegram implementation of quiz bot."""

import json
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from redis import Redis
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler, Updater,
)

from bots.settings import (
    CANCEL_TEXT, GREETING, HELP_TEXT, SCORE_TEXT, TASKS_DATABASE, USERS_DATABASE, BotStates,
    ButtonText,
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> Optional[int]:
    """Handle /start command.

    Greet the user and create record in the database if he is a newcomer.

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
    users_db = context.bot_data['users']
    user_id_db = f'user_tg_{user.id}'
    if not users_db.get(user_id_db):
        users_db.set(
            user_id_db, json.dumps({'last_asked_question': None, 'success': 0, 'failure': 0}),
        )
    logger.info(f'User {user.id} entered the quiz.')
    return BotStates.CHOOSING.value


def help_user(update: Update, context: CallbackContext) -> None:
    """Send information with bot functions when the command /help is issued.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.
    """
    incoming_message = update.message
    if incoming_message is None:
        return
    incoming_message.reply_text(text=HELP_TEXT)


def handler_score_request(update: Update, context: CallbackContext) -> None:
    """Send user information about his successful and failure attempts.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.
    """
    user = update.effective_user
    incoming_message = update.message
    if incoming_message is None or user is None:
        return
    users_db = context.bot_data['users']
    user_id_db = f'user_tg_{user.id}'
    saved_user_data = json.loads(users_db.get(user_id_db))
    successes = saved_user_data['success']
    failures = saved_user_data['failure']
    incoming_message.reply_text(text=SCORE_TEXT.format(successes=successes, failures=failures))


def handle_new_question_request(update: Update, context: CallbackContext) -> Optional[int]:
    """Send user a question.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.

    Returns:
        Conversation state of checking user's answer.
    """
    user = update.effective_user
    incoming_message = update.message
    if incoming_message is None or user is None:
        return None
    tasks_db = context.bot_data['tasks']
    random_question = tasks_db.randomkey()
    user_id_db = f'user_tg_{user.id}'
    users_db = context.bot_data['users']
    saved_user_data = json.loads(users_db.get(user_id_db))
    saved_user_data['last_asked_question'] = random_question
    users_db.set(user_id_db, json.dumps(saved_user_data))
    incoming_message.reply_text(random_question)
    return BotStates.CHECK_ANSWER.value


def cancel(update: Update, context: CallbackContext) -> Optional[int]:
    """Cancel and end the conversation.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.

    Returns:
        Ending conversation state.
    """
    user = update.effective_user
    incoming_message = update.message
    if incoming_message is None or user is None:
        return None
    incoming_message.reply_text(text=CANCEL_TEXT, reply_markup=ReplyKeyboardRemove())
    logger.info(f'User {user.id} left the quiz.')
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
    tasks_connector = Redis(db=TASKS_DATABASE, decode_responses=True)
    users_connector = Redis(db=USERS_DATABASE, decode_responses=True)
    dispatcher.bot_data = {'tasks': tasks_connector, 'users': users_connector}
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BotStates.CHOOSING.value: [
                MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request),
                MessageHandler(Filters.regex('^Мой счёт$'), handler_score_request),
                CommandHandler('help', help_user),
            ],
            BotStates.CHECK_ANSWER.value: [
                MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request),
                MessageHandler(Filters.regex('^Мой счёт$'), handler_score_request),
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
