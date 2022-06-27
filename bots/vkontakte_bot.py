"""Module for vkontakte implementation of quiz bot."""

import os

from dotenv import load_dotenv
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id
from vk_api.vk_api import VkApiMethod

from bots.settings import ButtonText


def create_keyboard() -> VkKeyboard:
    """Create keyboard for user to interact with him.

    Returns:
        Keyboard with buttons for new question request, give up and score request.
    """
    keyboard = VkKeyboard()
    keyboard.add_button(ButtonText.QUESTION.value, color=VkKeyboardColor.POSITIVE)
    keyboard.add_button(ButtonText.GIVE_UP.value, color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button(ButtonText.SCORE.value, color=VkKeyboardColor.PRIMARY)
    return keyboard


def interact_longpoll(vk_long_poll: VkLongPoll, vk_api_method: VkApiMethod) -> None:
    """Interact with VK longpoll server.

    Args:
        vk_long_poll: instance of VK Long Poll.
        vk_api_method: instance of VK Api Method.
    """
    keyboard = create_keyboard()
    for event in vk_long_poll.listen():
        # if json.loads(event.payload).get('command') == 'start':
        #     pass
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            vk_api_method.messages.send(
                user_id=event.user_id,
                message=event.text,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
            )


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
