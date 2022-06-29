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

from bots.check_answer import is_correct_answer
from bots.settings import (
    CANCEL_TEXT, GIVE_UP, GREETING_TG, HELP_TEXT, NEXT, REDIS_HOST, RIGHT_ANSWER, SCORE_TEXT,
    TASKS_DATABASE, USERS_DATABASE, WRONG_ANSWER, ButtonText,
)

logger = logging.getLogger(__name__)

CHOOSING, CHECK_ANSWER = range(2)


def start(update: Update, context: CallbackContext) -> Optional[int]:
    """Handle /start command.

    Greet the user and create record in the database if he is a newcomer.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.

    Returns:
        Conversation state of command choosing.
    """
    if not ((incoming_message := update.message) and (user := update.effective_user)):
        return None
    keyboard_menu = [
        [ButtonText.QUESTION.value, ButtonText.GIVE_UP.value], [ButtonText.SCORE.value],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard_menu)
    incoming_message.reply_text(
        text=GREETING_TG.format(user=user.first_name, help=HELP_TEXT),
        reply_markup=reply_markup,
    )
    users_db = context.bot_data['users']
    user_id_db = f'user_tg_{user.id}'
    if not users_db.get(user_id_db):
        users_db.set(
            user_id_db, json.dumps({'last_asked_question': None, 'success': 0, 'give_up': 0}),
        )
    logger.info(f'User {user.id} entered the quiz.')
    return CHOOSING


def help_user(update: Update, context: CallbackContext) -> None:
    """Send information with bot functions when the command /help is issued.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.
    """
    if not (incoming_message := update.message):
        return
    incoming_message.reply_text(text=HELP_TEXT)


def handle_score_request(update: Update, context: CallbackContext) -> None:
    """Send user information about his successful attempts and give ups.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.
    """
    if not ((incoming_message := update.message) and (user := update.effective_user)):
        return
    users_db = context.bot_data['users']
    user_id_db = f'user_tg_{user.id}'
    saved_user_data = json.loads(users_db.get(user_id_db))
    successes = saved_user_data['success']
    give_ups = saved_user_data['give_up']
    incoming_message.reply_text(text=SCORE_TEXT.format(successes=successes, give_ups=give_ups))


def handle_new_question_request(update: Update, context: CallbackContext) -> Optional[int]:
    """Send user a question.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.

    Returns:
        Conversation state of checking user's answer.
    """
    if not ((incoming_message := update.message) and (user := update.effective_user)):
        return None
    tasks_db = context.bot_data['tasks']
    random_question = tasks_db.randomkey()
    user_id_db = f'user_tg_{user.id}'
    users_db = context.bot_data['users']
    saved_user_data = json.loads(users_db.get(user_id_db))
    saved_user_data['last_asked_question'] = random_question
    users_db.set(user_id_db, json.dumps(saved_user_data))
    incoming_message.reply_text(random_question)
    return CHECK_ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext) -> Optional[int]:
    """Check user's answer.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.

    Returns:
        Conversation state of checking user's answer or command choosing.
    """
    if not ((incoming_message := update.message) and (user := update.effective_user)):
        return None
    user_id_db = f'user_tg_{user.id}'
    users_db = context.bot_data['users']
    saved_user_data = json.loads(users_db.get(user_id_db))
    asked_question = saved_user_data['last_asked_question']
    tasks_db = context.bot_data['tasks']
    correct_answer = tasks_db.get(asked_question)
    users_answer = update.message.text
    if not users_answer:
        return None
    if is_correct_answer(users_answer=users_answer, correct_answer=correct_answer):
        saved_user_data['success'] += 1
        users_db.set(user_id_db, json.dumps(saved_user_data))
        incoming_message.reply_text(RIGHT_ANSWER)
        return CHOOSING
    incoming_message.reply_text(WRONG_ANSWER)
    return CHECK_ANSWER


def handle_give_up_request(update: Update, context: CallbackContext) -> Optional[int]:
    """Send user right answer whe he gives up.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.

    Returns:
        Conversation state of checking user's answer.
    """
    if not ((incoming_message := update.message) and (user := update.effective_user)):
        return None
    user_id_db = f'user_tg_{user.id}'
    users_db = context.bot_data['users']
    saved_user_data = json.loads(users_db.get(user_id_db))
    saved_user_data['give_up'] += 1
    users_db.set(user_id_db, json.dumps(saved_user_data))
    tasks_db = context.bot_data['tasks']
    asked_question = saved_user_data['last_asked_question']
    right_answer = tasks_db.get(asked_question)
    incoming_message.reply_text(GIVE_UP.format(answer=right_answer, next=NEXT))
    return CHOOSING


def cancel(update: Update, context: CallbackContext) -> Optional[int]:
    """Cancel and end the conversation.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.

    Returns:
        Ending conversation state.
    """
    if not ((incoming_message := update.message) and (user := update.effective_user)):
        return None
    incoming_message.reply_text(text=CANCEL_TEXT, reply_markup=ReplyKeyboardRemove())
    logger.info(f'User {user.id} left the quiz.')
    return ConversationHandler.END


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error happened during bot running.

    Args:
        update: incoming update object.
        context: indicates that this is a callback function.
    """
    logger.error(msg='Exception while handling an update:', exc_info=context.error)


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
    tasks_connector = Redis(host=REDIS_HOST, db=TASKS_DATABASE, decode_responses=True)
    users_connector = Redis(host=REDIS_HOST, db=USERS_DATABASE, decode_responses=True)
    dispatcher.bot_data = {'tasks': tasks_connector, 'users': users_connector}
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex(f'^{ButtonText.QUESTION.value}$'), handle_new_question_request,
                ),
                MessageHandler(Filters.regex(f'^{ButtonText.SCORE.value}$'), handle_score_request),
                CommandHandler('help', help_user),
            ],
            CHECK_ANSWER: [
                MessageHandler(
                    Filters.regex(f'^{ButtonText.QUESTION.value}$'), handle_new_question_request,
                ),
                MessageHandler(Filters.regex(f'^{ButtonText.SCORE.value}$'), handle_score_request),
                MessageHandler(
                    Filters.regex(f'^{ButtonText.GIVE_UP.value}$'), handle_give_up_request,
                ),
                CommandHandler('help', help_user),
                MessageHandler(Filters.text ^ Filters.command, handle_solution_attempt),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conversation_handler)
    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    logger.info('Bot started.')
    updater.idle()


if __name__ == '__main__':
    main()
