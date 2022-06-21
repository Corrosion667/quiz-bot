"""Settings module of the project."""

import os
from enum import Enum
from pathlib import Path


class ButtonText(Enum):
    """Class with titles for bot buttons."""

    NEW_QUESTION = 'Новый вопрос'
    GIVE_UP = 'Сдаться'
    SCORE = 'Мой счёт'


QUIZ_TASKS_DIR = os.path.join(Path(__file__).absolute().parent.parent, 'quiz_tasks')

TASKS_DATABASE = 1
USERS_DATABASE = 2

GREETING = 'Приветствуем вас в нашей викторине, {user}!\n{help}'
HELP_TEXT = (
    f'Нажмите "{ButtonText.NEW_QUESTION.value}" для начала викторины.\n'
    + f'Нажмите "{ButtonText.GIVE_UP.value}", чтобы узнать правильный ответ.\n'
    + f'Узнать счёт можно нажав "{ButtonText.SCORE.value}".\n'
    + '/cancel - закончить викторину.\n/help - получить справку о функционале бота.'
)
SCORE_TEXT = 'Правильных ответов: {successes}.\nНеугадано вопросов (сдались): {give_ups}.'
CANCEL_TEXT = (
    'Спасибо за участие в квизе! Ваш прогресс сохранён.\n'
    + 'Для возобновления отправьте команду /start.'
)
NEXT = f'Для следующего вопроса нажмите "{ButtonText.NEW_QUESTION.value}"'
RIGHT_ANSWER = f'Правильно, поздравляю! {NEXT}'
WRONG_ANSWER = 'Ответ неверный, попробуйте ещё раз.'
GIVE_UP = 'Правильный ответ:\n{answer}\n{next}'
STRING_EQUALITY_RATIO = 0.7
