#!/bin/bash
set -e

python bots/upload_quiz.py
python bots/telegram_bot.py &
python bots/vkontakte_bot.py
