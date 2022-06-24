"""Module for vkontakte implementation of quiz bot."""

import os
import random

from dotenv import load_dotenv
from vk_api import VkApi
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.vk_api import VkApiMethod


def interact_longpoll(vk_long_poll: VkLongPoll, vk_api_method: VkApiMethod):
    """Interact with VK longpoll server.

    Args:
        vk_long_poll: instance of VK Long Poll.
        vk_api_method: instance of VK Api Method.
    """
    for event in vk_long_poll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            vk_api_method.messages.send(
                user_id=event.user_id,
                message=event.text,
                random_id=random.randint(1, 1000),
            )


def main():
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
