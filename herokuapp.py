"""
Program to run with Heroku Scheduler add-on
(command: python herokuapp.py)

Required config variables:
    - USERNAME
    - PASSWORD
    - POLLHOST
    - DAY_OF_WEEK (cron string)

Optional config variables:
    - LOGIN_TYPE ('uw' or 'pollev')
    - LIFETIME

Since Heroku Scheduler can only schedule programs
to run at a certain time every day, this program
will check if the current date matches the weekdays
set in the config variable `DAY_OF_WEEK`. If it does,
this program will run pollevbot; if not, the program
will exit.
"""

import os
import logging
from datetime import date
from pollevbot import PollBot

required_vars = {'USERNAME', 'PASSWORD', 'POLLHOST', 'DAY_OF_WEEK'}
missing_vars = sorted(required_vars - set(os.environ))
assert len(missing_vars) == 0, f"Missing required config variables: {missing_vars}"

logger = logging.getLogger(__name__)


def check_day():
    date_map = {
        'mon': '0',
        'tue': '1',
        'wed': '2',
        'thu': '3',
        'fri': '4',
        'sat': '5',
        'sun': '6'
    }
    # DAY_OF_WEEK is a cron string, i.e.
    # '1,3' means run on tuesday and thursday
    day_of_week = [s.strip() for s in os.environ['DAY_OF_WEEK'].split(',')]
    day_of_week = [date_map[s] if s in date_map else s for s in day_of_week]

    return str(date.today().weekday()) in day_of_week


def main():
    # Heroku config vars
    user = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    host = os.environ['POLLHOST']
    login_type = os.environ.get('LOGIN_TYPE', 'uw')
    lifetime = float(os.environ.get('LIFETIME', 'inf'))

    if check_day():
        with PollBot(user, password, host,
                     login_type=login_type, lifetime=lifetime) as bot:
            bot.run()
    else:
        logger.info("pollevbot is not configured to run today. Exiting.")


if __name__ == '__main__':
    main()
