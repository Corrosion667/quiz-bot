"""Module for telegram implementation of quiz bot."""

import json
import logging
import os
import string
from typing import Optional

from dotenv import load_dotenv
from redis import Redis
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler, Updater,
)

from bots.settings import (
    CANCEL_TEXT, GREETING, HELP_TEXT, SCORE_TEXT, STRING_EQUALITY_RATIO, TASKS_DATABASE,
    USERS_DATABASE, BotStates, ButtonText,
)
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


def is_correct_answer(users_answer: str, correct_answer: str) -> bool:
    """Check if answer given by user os correct.

    Args:
        users_answer: answer received from user.
        correct_answer: answer from the database.

    Returns:
        True if answer is correct else False.
    """
    filtered_users_answer = ''.join(
        [symbol for symbol in users_answer.lower() if symbol not in string.punctuation]
    )
    filtered_correct_answer = ''.join(
        [symbol for symbol in correct_answer.lower() if symbol not in string.punctuation]
    )
    if SequenceMatcher(
            None, filtered_correct_answer, filtered_users_answer,
    ).ratio() >= STRING_EQUALITY_RATIO:
        return True
    return False


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


def handle_score_request(update: Update, context: CallbackContext) -> None:
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


def handle_solution_attempt(update: Update, context: CallbackContext) -> Optional[int]:
    user = update.effective_user
    incoming_message = update.message
    if incoming_message is None or user is None:
        return None
    user_id_db = f'user_tg_{user.id}'
    users_db = context.bot_data['users']
    saved_user_data = json.loads(users_db.get(user_id_db))
    asked_question = saved_user_data['last_asked_question']
    tasks_db = context.bot_data['tasks']
    print(tasks_db.get(asked_question))
    if is_correct_answer(incoming_message.text, tasks_db.get(asked_question)):
        print(tasks_db.get(asked_question))


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
                MessageHandler(Filters.regex('^Мой счёт$'), handle_score_request),
                CommandHandler('help', help_user),
            ],
            BotStates.CHECK_ANSWER.value: [
                MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request),
                MessageHandler(Filters.regex('^Мой счёт$'), handle_score_request),
                CommandHandler('help', help_user),
                MessageHandler(Filters.text, handle_solution_attempt),
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
