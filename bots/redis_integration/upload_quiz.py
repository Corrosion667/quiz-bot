"""Module for creating quiz questions and answers pairs in Redis from quiz fixture files."""

import re

from redis import Redis

from bots.redis_integration.settings import REDIS_HOST, REDIS_PORT, TASKS_DATABASE


def parse_quiz_file(path_to_file):
    """Parse quiz file and create records in Redis of questions and answers.

    Args:
        path_to_file: path to file with quiz content.
    """
    client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=TASKS_DATABASE)
    with open(path_to_file, encoding='KOI8-R') as quiz_file:
        quiz_content = quiz_file.read()
    split_content = quiz_content.split('\n\n')
    questions = [
        re.sub('^Вопрос.+\n', '', split) for split in split_content if 'Вопрос' in split
    ]
    answers = [
        re.sub('^Ответ.+\n', '', split) for split in split_content if 'Ответ' in split
    ]
    for question, answer in zip(questions, answers):
        client.set(question, answer)
