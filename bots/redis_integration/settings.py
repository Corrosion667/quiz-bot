"""Redis settings of the project."""

import os
from pathlib import Path

QUIZ_TASKS_DIR = os.path.join(
    Path(__file__).absolute().parent.parent, 'quiz_tasks',
)

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
TASKS_DATABASE = 1
USERS_DATABASE = 2
