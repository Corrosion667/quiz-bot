"""Redis settings of the project."""

import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
QUIZ_TASKS_DIR = os.path.join(BASE_DIR, 'quiz_tasks')

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
TASKS_DATABASE = 1
USERS_DATABASE = 2
