"""Module for creating quiz questions and answers pairs in Redis from quiz fixture files."""

import logging
import re
import time
from os import listdir
from os.path import join

from redis import Redis
from redis.client import Pipeline

from bots.settings import (
    ANSWER_REGEX, PICTURE_INDICATOR, QUESTION_REGEX, QUIZ_TASKS_DIR, TASKS_DATABASE,
)

logger = logging.getLogger(__name__)


def parse_quiz_file(path_to_file: str, pipeline: Pipeline) -> None:
    """Parse quiz file and append creation of questions and answers in Redis to pipeline.

    If question supposed to be with picture he won't be added to database.

    Args:
        path_to_file: path to file with quiz content.
        pipeline: Redis pipeline for bulk loading.
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
    for question, answer in zip(questions, answers):
        pipeline.set(question, answer)


def load_quiz_tasks() -> None:
    """Script for loading quiz questions and answers to Redis from all quiz files."""
    starting_time = time.time()
    logger.info('Started uploading quiz tasks.')
    redis_client = Redis(db=TASKS_DATABASE)
    loading_pipeline = redis_client.pipeline()
    quiz_files_paths = [join(QUIZ_TASKS_DIR, file_name) for file_name in listdir(QUIZ_TASKS_DIR)]
    for path in quiz_files_paths:
        parse_quiz_file(path_to_file=path, pipeline=loading_pipeline)
    loading_pipeline.execute()
    logger.info(f'Uploading finished in {time.time() - starting_time} seconds.')


if __name__ == '__main__':
    logging.basicConfig(
        format='QUIZ_UPLOAD %(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO,
    )
    load_quiz_tasks()
