# Quiz bot

[![Maintainability](https://api.codeclimate.com/v1/badges/7364174229c0f6805dd8/maintainability)](https://codeclimate.com/github/Corrosion667/quiz-bot/maintainability)
[![linter check](https://github.com/Corrosion667/quiz-bot/actions/workflows/linter-check.yml/badge.svg)](https://github.com/Corrosion667/quiz-bot/actions/workflows/linter-check.yml)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

---

## Overview

+ ***Quiz bot*** asks tricky questions on erudition and logic with the only answer option.
+ Repository includes huge database of questions but feel free to choose between them to your liking and to add your own.
+ Bot stores score so every participant will be able to know how many questions he managed to guess and how many did not.

## Deployment

You can try to participate in quiz **here** (please take note that the demo database of questions has been reduced):

| Service       | Link                        |
|---------------|-----------------------------|
| **Telegram**  | https://t.me/artem_quiz_bot |       
| **Vkontakte** | https://vk.com/quizbotdemo  | 

## Running

#### *Before Installation*
1. Create bot in **Telegram** with @BotFather and receive bot **token**;
2. Create public in **Vkontakte** and receive group **token**;
3. Make sure that **docker** and **docker compose** are installed on your machine.

#### *Installation*
1. Clone the repository:
```bash
git clone https://github.com/Corrosion667/quiz-bot.git
```
2. Create **.env** file and set the <ins>following environmental variables</ins> *(as in the .env(example) file)*:

| Environmental     | Description                                                                                        |
|-------------------|----------------------------------------------------------------------------------------------------|
| `TELEGRAM_TOKEN`  | bot token from @BotFather in telegram                                                              |       
| `VKONTAKTE_TOKEN` | group token of vkontakte                                                                           |
| `QUIZ_TASKS_DIR`  | absolute path to folder with tasks for quiz; by default the main directory of project will be used |
3. Run bots with docker compose:
```bash
docker-compose up -d
```