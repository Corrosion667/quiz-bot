"""Settings module of the project."""

import os
from enum import Enum
from pathlib import Path


class ButtonText(Enum):
    """Class with titles for bot buttons."""

    QUESTION = 'Новый вопрос'
    GIVE_UP = 'Сдаться'
    SCORE = 'Мой счёт'


PICTURE_INDICATOR = '(pic:'
QUESTION_REGEX = '^Вопрос.+\n'
ANSWER_REGEX = '^Ответ.+\n'

QUIZ_TASKS_DIR = os.path.join(Path(__file__).absolute().parent.parent, 'quiz_tasks')

TASKS_DATABASE = 1
USERS_DATABASE = 2

GREETING_VK = (
    'Приветствуем вас в нашей викторине!\n'
    + f'Нажмите "{ButtonText.QUESTION.value}" для начала викторины.\n'
    + f'Нажмите "{ButtonText.GIVE_UP.value}", чтобы узнать правильный ответ.\n'
    + f'Узнать счёт можно нажав "{ButtonText.SCORE.value}".\n'
)
GREETING_TG = 'Приветствуем вас в нашей викторине, {user}!\n{help}'
HELP_TEXT = (
    f'Нажмите "{ButtonText.QUESTION.value}" для начала викторины.\n'
    + f'Нажмите "{ButtonText.GIVE_UP.value}", чтобы узнать правильный ответ.\n'
    + f'Узнать счёт можно нажав "{ButtonText.SCORE.value}".\n'
    + '/cancel - закончить викторину.\n/help - получить справку о функционале бота.'
)
SCORE_TEXT = 'Правильных ответов: {successes}.\nНеугадано вопросов: {give_ups}.'
CANCEL_TEXT = (
    'Спасибо за участие в квизе! Ваш прогресс сохранён.\n'
    + 'Для возобновления отправьте команду /start.'
)
NEXT = f'Для следующего вопроса нажмите "{ButtonText.QUESTION.value}"'
RIGHT_ANSWER = f'Правильно, поздравляю! {NEXT}'
WRONG_ANSWER = 'Ответ неверный, попробуйте ещё раз.'
GIVE_UP = 'Правильный ответ:\n{answer}\n{next}'
GIVE_UP_STUB_VK = f'Вопрос ещё не был задан! Пожалуйста, нажмите {ButtonText.QUESTION.value}!'
STRING_EQUALITY_RATIO = 0.7
