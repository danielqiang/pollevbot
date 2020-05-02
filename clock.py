"""
Program scheduler to run on a Heroku clock dyno.

Required config variables:
    - USERNAME
    - PASSWORD
    - POLLHOST
    - DAY_OF_WEEK (cron string)
    - HOUR (cron string)
    - MINUTE (cron string)
    - LOGIN_TYPE ('uw' or 'pollev')
    - LIFETIME

clock.py is a standalone program that schedules and runs
pollevbot. It uses APScheduler's Cron triggers to simulate
cron (Unix util).

See https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
for more info.
"""

import os
import logging
import pytz
from pollevbot import PollBot
from apscheduler.schedulers.blocking import BlockingScheduler

required_vars = {'USERNAME', 'PASSWORD', 'POLLHOST', 'DAY_OF_WEEK',
                 'HOUR', 'MINUTE', 'LOGIN_TYPE', 'LIFETIME'}
missing_vars = sorted(required_vars - set(os.environ))
assert len(missing_vars) == 0, f"Missing required config variables: {missing_vars}"

logger = logging.getLogger(__name__)


def run():
    # Heroku config vars
    user = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    host = os.environ['POLLHOST']
    login_type = os.environ['LOGIN_TYPE']
    lifetime = float(os.environ['LIFETIME'])

    with PollBot(user, password, host, login_type=login_type, lifetime=lifetime) as bot:
        bot.run()


def main():
    logger.info("Starting blocking scheduler.")

    scheduler = BlockingScheduler(timezone=pytz.utc)
    scheduler.add_job(run, 'cron',
                      day_of_week=os.environ['DAY_OF_WEEK'],
                      hour=os.environ['HOUR'],
                      minute=os.environ['MINUTE'])
    scheduler.start()


if __name__ == '__main__':
    main()
