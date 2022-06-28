"""Module for vkontakte implementation of quiz bot."""

import json
import os

from dotenv import load_dotenv
from redis import Redis
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id
from vk_api.vk_api import VkApiMethod

from bots.settings import (
    GIVE_UP, GIVE_UP_STUB_VK, GREETING_VK, NEXT, SCORE_TEXT, TASKS_DATABASE, USERS_DATABASE,
    ButtonText,
)


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
    tasks_connector = Redis(db=TASKS_DATABASE, decode_responses=True)
    users_connector = Redis(db=USERS_DATABASE, decode_responses=True)
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
            reply_message = GREETING_VK
        elif event.message == ButtonText.QUESTION.value:
            reply_message = handle_new_question_request(databases=databases, user_id=user_id_db)
        elif event.message == ButtonText.GIVE_UP.value:
            reply_message = handle_give_up_request(databases=databases, user_id=user_id_db)
        elif event.message == ButtonText.SCORE.value:
            reply_message = handle_score_request(databases=databases, user_id=user_id_db)
        else:
            reply_message = handle_solution_attempt()
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
        return GIVE_UP_STUB_VK
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
        Score text message for user.
    """
    users_db = databases['users']
    saved_user_data = json.loads(users_db.get(user_id))
    successes = saved_user_data['success']
    give_ups = saved_user_data['give_up']
    return SCORE_TEXT.format(successes=successes, give_ups=give_ups)


def handle_solution_attempt() -> str:
    """Docstring.

    Returns:
        stub string.
    """
    return 'STUB'


def main() -> None:
    """Run the bot as script."""
    load_dotenv()
    vk_token = os.getenv('VKONTAKTE_TOKEN')
    vk_api = VkApi(token=vk_token)
    vk_api_connector = vk_api.get_api()
    vk_long_poll = VkLongPoll(vk_api)
    while True:  # noqa: WPS457
        interact_longpoll(vk_long_poll=vk_long_poll, vk_api_method=vk_api_connector)


if __name__ == '__main__':
    main()
