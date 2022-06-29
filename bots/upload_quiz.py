"""Module for creating quiz questions and answers pairs in Redis from quiz fixture files."""

import logging
import os
import re
import time
from os.path import join

from dotenv import load_dotenv
from redis import Redis

from bots.settings import (
    ANSWER_REGEX, DEFAULT_QUIZ_TASKS_DIR, PICTURE_INDICATOR, QUESTION_REGEX, REDIS_HOST,
    TASKS_DATABASE,
)

logger = logging.getLogger(__name__)


def parse_quiz_file(path_to_file: str) -> zip:
    """Parse quiz file and make pairs of questions and answers.

    If question supposed to be with picture he won't be added to database.

    Args:
        path_to_file: path to file with quiz content.

    Returns:
        Questions and answers for them as zip generator.
    """
    with open(path_to_file, encoding='KOI8-R') as quiz_file:
        quiz_content = quiz_file.read()
    split_content = iter(quiz_content.replace('\n\n\n', '\n\n').split('\n\n'))
    questions = []
    answers = []
    for split in split_content:
        if PICTURE_INDICATOR in split:
            next(split_content, None)
            continue
        elif re.match(QUESTION_REGEX, split):
            questions.append(re.sub(QUESTION_REGEX, '', split))
        elif re.match(ANSWER_REGEX, split):
            answers.append(re.sub(ANSWER_REGEX, '', split))
    return zip(questions, answers)


def load_quiz_tasks(quiz_folder: str) -> None:
    """Script for loading quiz questions and answers to Redis from all quiz files.

    Args:
        quiz_folder: path to folder with quiz tasks.
    """
    starting_time = time.time()
    logger.info('Started uploading quiz tasks.')
    redis_client = Redis(host=REDIS_HOST, db=TASKS_DATABASE)
    loading_pipeline = redis_client.pipeline()
    quiz_files_paths = [join(quiz_folder, file_name) for file_name in os.listdir(quiz_folder)]
    for path in quiz_files_paths:
        tasks = parse_quiz_file(path_to_file=path)
        for question, answer in tasks:
            loading_pipeline.set(question, answer)
    loading_pipeline.execute()
    logger.info(f'Uploading finished in {time.time() - starting_time} seconds.')


if __name__ == '__main__':
    logging.basicConfig(
        format='QUIZ_UPLOAD %(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO,
    )
    load_dotenv()
    quiz_folder_path = os.getenv('QUIZ_TASKS_DIR', DEFAULT_QUIZ_TASKS_DIR)
    load_quiz_tasks(quiz_folder_path)
