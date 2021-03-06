"""Module with common constants of the project."""

import os
from enum import Enum


class ButtonText(Enum):
    """Class with titles for bot buttons."""

    QUESTION = 'Новый вопрос'
    GIVE_UP = 'Сдаться'
    SCORE = 'Мой счёт'


PICTURE_INDICATOR = '(pic:'
QUESTION_REGEX = r'^Вопрос.+\n'
ANSWER_REGEX = r'^Ответ.+\n'

GREETING_VK = f"""Приветствуем вас в нашей викторине!
Нажмите "{ButtonText.QUESTION.value}" для начала викторины.
Нажмите "{ButtonText.GIVE_UP.value}", чтобы узнать правильный ответ.
Узнать счёт можно нажав "{ButtonText.SCORE.value}"."""

GREETING_TG = 'Приветствуем вас в нашей викторине, {user}!\n{help}'

HELP_TEXT = f"""Нажмите "{ButtonText.QUESTION.value}" для начала викторины.
Нажмите "{ButtonText.GIVE_UP.value}", чтобы узнать правильный ответ.
Узнать счёт можно нажав "{ButtonText.SCORE.value}".
/cancel - закончить викторину.
/help - получить справку о функционале бота."""

SCORE_TEXT = 'Правильных ответов: {successes}.\nНеугадано вопросов: {give_ups}.'

CANCEL_TEXT = """Спасибо за участие в квизе! Ваш прогресс сохранён.
Для возобновления отправьте команду /start."""

NEXT = f'Для следующего вопроса нажмите "{ButtonText.QUESTION.value}".'
RIGHT_ANSWER = f'Правильно, поздравляю! {NEXT}'
WRONG_ANSWER = 'Ответ неверный, попробуйте ещё раз.'
GIVE_UP = 'Правильный ответ:\n{answer}\n{next}'
NO_QUESTION_STUB = f'Вопрос ещё не был задан! Пожалуйста, нажмите {ButtonText.QUESTION.value}!'

TASKS_DATABASE = 1
USERS_DATABASE = 2
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
