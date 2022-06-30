"""Function for checking the correctness of the answers."""

import re
import string
from difflib import SequenceMatcher

STRING_EQUALITY_RATIO = 0.7


def is_correct_answer(users_answer: str, correct_answer: str) -> bool:
    """Check if answer given by user is correct.

    Comments in brackets [] or () aren't taken into consideration when counting string match ratio.
    Punctuation symbols are excluded from calculation too.

    Args:
        users_answer: answer received from user.
        correct_answer: answer from the database.

    Returns:
        True if answer is correct else False.
    """
    commentless_answer = re.sub(r'\s?\(.+\)|\s?\[.+]', '', correct_answer)
    filtered_correct_answer = ''.join(
        [symbol for symbol in commentless_answer.lower() if symbol not in string.punctuation],
    )
    filtered_users_answer = ''.join(
        [symbol for symbol in users_answer.lower() if symbol not in string.punctuation],
    )
    matching_ratio = SequenceMatcher(None, filtered_correct_answer, filtered_users_answer).ratio()
    return matching_ratio >= STRING_EQUALITY_RATIO
