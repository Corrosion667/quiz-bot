"""Module for creating quiz questions and answers pairs from quiz fixture files."""

import re

from redis import Redis

from bots.redis_integration.settings import QUESTIONS_DATABASE, REDIS_HOST, REDIS_PORT


def parse_quiz_file(path_to_file):
    """Parse quiz file and create instances in Redis with questions and answers.

    Args:
        path_to_file: path to file with quiz content.
    """
    client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=QUESTIONS_DATABASE)
    with open(path_to_file, encoding='KOI8-R') as quiz_file:
        file_contents = quiz_file.read()
    splitted_contents = file_contents.split('\n\n')
    questions = [
        re.sub('^Вопрос.+\n', '', split) for split in splitted_contents if 'Вопрос' in split
    ]
    answers = [
        re.sub('^Ответ.+\n', '', split) for split in splitted_contents if 'Ответ' in split
    ]
    for question, answer in zip(questions, answers):
        client.set(question, answer)
