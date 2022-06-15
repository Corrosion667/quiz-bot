"""Module for creating quiz questions and answers pairs in Redis from quiz fixture files."""

import re
from dotenv import load_dotenv
import time
from os import listdir
from os.path import join

from redis import Redis

from bots.redis_integration.settings import QUIZ_TASKS_DIR, REDIS_HOST, REDIS_PORT, TASKS_DATABASE


def parse_quiz_file(path_to_file, pipe):
    """Parse quiz file and append creation of questions and answers to in Redis of pipeline.

    Args:
        path_to_file: path to file with quiz content.
    """
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
        pipe.set(question, answer)


def load_quiz_tasks(pipe):
    """Script for loading quiz questions and answers to Redis from all quiz files."""
    quiz_files_paths = [join(QUIZ_TASKS_DIR, file_name) for file_name in listdir(QUIZ_TASKS_DIR)]
    for path in quiz_files_paths:
        parse_quiz_file(path, pipe)


if __name__ == '__main__':
    load_dotenv()
    redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=TASKS_DATABASE, decode_responses=True)
    pipe = redis_client.pipeline()
    start_time = time.time()
    load_quiz_tasks(pipe)
    pipe.execute()
