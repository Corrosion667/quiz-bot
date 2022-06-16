"""Settings module of the project."""

import os
from pathlib import Path

QUIZ_TASKS_DIR = os.path.join(
    Path(__file__).absolute().parent.parent, 'quiz_tasks',
)
TASKS_DATABASE = 1
USERS_DATABASE = 2
