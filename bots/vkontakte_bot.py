"""Module for vkontakte implementation of quiz bot."""

import json
import logging
import os
import time

from dotenv import load_dotenv
from redis import Redis
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id
from vk_api.vk_api import VkApiMethod

from bots.check_answer import is_correct_answer
from bots.settings import (
    GIVE_UP, GREETING_VK, NEXT, NO_QUESTION_STUB, REDIS_HOST, RIGHT_ANSWER, SCORE_TEXT,
    TASKS_DATABASE, UNEXPECTED_ERROR_LOG, UNEXPECTED_ERROR_TIMEOUT, USERS_DATABASE, WRONG_ANSWER,
    ButtonText,
)

logger = logging.getLogger(__name__)


def create_keyboard() -> str:
    """Create keyboard for user to interact with him.

    Returns:
        Keyboard with buttons for new question request, give up and score request in JSON format.
    """
    keyboard = VkKeyboard()
    keyboard.add_button(ButtonText.QUESTION.value, color=VkKeyboardColor.POSITIVE)
    keyboard.add_button(ButtonText.GIVE_UP.value, color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button(ButtonText.SCORE.value, color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def interact_longpoll(vk_long_poll: VkLongPoll, vk_api_method: VkApiMethod) -> None:
    """Interact with VK longpoll server.

    Args:
        vk_long_poll: instance of VK Long Poll.
        vk_api_method: instance of VK Api Method.
    """
    tasks_connector = Redis(host=REDIS_HOST, db=TASKS_DATABASE, decode_responses=True)
    users_connector = Redis(host=REDIS_HOST, db=USERS_DATABASE, decode_responses=True)
    databases = {'tasks': tasks_connector, 'users': users_connector}
    keyboard = create_keyboard()
    for event in vk_long_poll.listen():
        if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
            continue
        user_id = event.user_id
        user_id_db = f'user_vk_{user_id}'
        if not users_connector.get(user_id_db):
            users_connector.set(
                user_id_db, json.dumps({'last_asked_question': '', 'success': 0, 'give_up': 0}),
            )
            logger.info(f'User {user_id} entered the quiz.')
            reply_message = GREETING_VK
        elif event.message == ButtonText.QUESTION.value:
            reply_message = handle_new_question_request(databases=databases, user_id=user_id_db)
        elif event.message == ButtonText.GIVE_UP.value:
            reply_message = handle_give_up_request(databases=databases, user_id=user_id_db)
        elif event.message == ButtonText.SCORE.value:
            reply_message = handle_score_request(databases=databases, user_id=user_id_db)
        else:
            reply_message = handle_solution_attempt(
                databases=databases, user_id=user_id_db, users_answer=event.message,
            )
        vk_api_method.messages.send(
            user_id=user_id, message=reply_message, random_id=get_random_id(), keyboard=keyboard,
        )


def handle_new_question_request(databases: dict, user_id: str) -> str:
    """Get random question from database and update it as last asked question for user.

    Args:
        databases: connectors to redis databases (users and tasks).
        user_id: id of the user in Vkontakte in database representation.

    Returns:
        Random question for user.
    """
    tasks_db = databases['tasks']
    question = tasks_db.randomkey()
    users_db = databases['users']
    saved_user_data = json.loads(users_db.get(user_id))
    saved_user_data['last_asked_question'] = question
    users_db.set(user_id, json.dumps(saved_user_data))
    return question


def handle_give_up_request(databases: dict, user_id: str) -> str:
    """Get answer for last asked question to user and increase give up counter.

    Args:
        databases: connectors to redis databases (users and tasks).
        user_id: id of the user in Vkontakte in database representation.

    Returns:
        Answer for asked question or stub message if there haven't been any questions for user yet.
    """
    users_db = databases['users']
    saved_user_data = json.loads(users_db.get(user_id))
    asked_question = saved_user_data['last_asked_question']
    if not asked_question:
        return NO_QUESTION_STUB
    saved_user_data['give_up'] += 1
    saved_user_data['last_asked_question'] = ''
    users_db.set(user_id, json.dumps(saved_user_data))
    tasks_db = databases['tasks']
    return GIVE_UP.format(answer=tasks_db.get(asked_question), next=NEXT)


def handle_score_request(databases: dict, user_id: str) -> str:
    """Get user's score: successes and give ups.

    Args:
        databases: connectors to redis databases (users and tasks).
        user_id: id of the user in Vkontakte in database representation.

    Returns:
        Text message with score for user.
    """
    users_db = databases['users']
    saved_user_data = json.loads(users_db.get(user_id))
    successes = saved_user_data['success']
    give_ups = saved_user_data['give_up']
    return SCORE_TEXT.format(successes=successes, give_ups=give_ups)


def handle_solution_attempt(databases: dict, user_id: str, users_answer: str) -> str:
    """Check user's answer and increase success counter if he is correct.

    Args:
        databases: connectors to redis databases (users and tasks).
        user_id: id of the user in Vkontakte in database representation.
        users_answer: answer received from user.

    Returns:
        Reply message for user whether he was correct or not.
        Stub message could be also returned if there haven't been any questions for user yet.
    """
    users_db = databases['users']
    saved_user_data = json.loads(users_db.get(user_id))
    asked_question = saved_user_data['last_asked_question']
    if not asked_question:
        return NO_QUESTION_STUB
    tasks_db = databases['tasks']
    correct_answer = tasks_db.get(asked_question)
    if not is_correct_answer(users_answer=users_answer, correct_answer=correct_answer):
        return WRONG_ANSWER
    saved_user_data['success'] += 1
    saved_user_data['last_asked_question'] = ''
    users_db.set(user_id, json.dumps(saved_user_data))
    return RIGHT_ANSWER


def main() -> None:
    """Run the bot as script."""
    logging.basicConfig(
        format='VK_BOT %(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO,
    )
    load_dotenv()
    vk_token = os.getenv('VKONTAKTE_TOKEN')
    vk_api = VkApi(token=vk_token)
    vk_api_connector = vk_api.get_api()
    vk_long_poll = VkLongPoll(vk_api)
    logger.info('Bot started.')
    while True:
        try:
            interact_longpoll(vk_long_poll=vk_long_poll, vk_api_method=vk_api_connector)
        except Exception as exc:
            error_message = UNEXPECTED_ERROR_LOG.format(
                exception=exc, timeout=UNEXPECTED_ERROR_TIMEOUT,
            )
            logger.error(error_message)
            time.sleep(UNEXPECTED_ERROR_TIMEOUT)


if __name__ == '__main__':
    main()
