import os
import logging
from datetime import date
from pollevbot import PollBot

logger = logging.getLogger(__name__)


def check_day():
    # DAY_OF_WEEK is a string of ints delimited
    # by commas, i.e. day_of_week = '1,3' means
    # run on tuesday and thursday
    day_of_week = [s.strip() for s in os.environ['DAY_OF_WEEK'].split(',')]

    return str(date.today().weekday()) in day_of_week


def main():
    # Heroku config vars
    user = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    host = os.environ['POLLHOST']

    if check_day():
        with PollBot(user, password, host, lifetime=3600) as bot:
            bot.run()
    else:
        logger.info("pollevbot is not configured to run today. Exiting.")


if __name__ == '__main__':
    main()
