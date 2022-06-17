"""Module for creating quiz questions and answers pairs in Redis from quiz fixture files."""

import re
from os import listdir
from os.path import join

from redis import Redis
from redis.client import Pipeline

from bots.settings import QUIZ_TASKS_DIR, TASKS_DATABASE


def parse_quiz_file(path_to_file: str, pipeline: Pipeline) -> None:
    """Parse quiz file and append creation of questions and answers in Redis to pipeline.

    Args:
        path_to_file: path to file with quiz content.
        pipeline: Redis pipeline for bulk loading.
    """
    with open(path_to_file, encoding='KOI8-R') as quiz_file:
        quiz_content = quiz_file.read()
    split_content = quiz_content.split('\n\n')
    questions = []
    answers = []
    for split in split_content:
        if 'Вопрос' in split:
            questions.append(re.sub('^Вопрос.+\n', '', split))
        elif 'Ответ' in split:
            answers.append(re.sub('^Ответ.+\n', '', split))
    for question, answer in zip(questions, answers):
        pipeline.set(question, answer)


def load_quiz_tasks() -> None:
    """Script for loading quiz questions and answers to Redis from all quiz files."""
    redis_client = Redis(db=TASKS_DATABASE)
    loading_pipeline = redis_client.pipeline()
    quiz_files_paths = [join(QUIZ_TASKS_DIR, file_name) for file_name in listdir(QUIZ_TASKS_DIR)]
    for path in quiz_files_paths:
        parse_quiz_file(path_to_file=path, pipeline=loading_pipeline)
    loading_pipeline.execute()


if __name__ == '__main__':
    load_quiz_tasks()
