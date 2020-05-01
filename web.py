"""
Program scheduler to run on a Heroku web dyno.

Required config variables:
    - USERNAME
    - PASSWORD
    - POLLHOST
    - DAY_OF_WEEK (cron string)
    - HOUR (cron string)
    - MINUTE (cron string)

Optional config variables:
    - LOGIN_TYPE ('uw' or 'pollev')
    - LIFETIME

web.py is a standalone program that schedules and runs
pollevbot. It uses APScheduler's Cron triggers to simulate
the Unix util cron.

See https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
for more info.
"""


import os
import logging
from pollevbot import PollBot
from apscheduler.schedulers.blocking import BlockingScheduler

required_vars = {'USERNAME', 'PASSWORD', 'POLLHOST', 'DAY_OF_WEEK', 'HOUR', 'MINUTE'}
missing_vars = sorted(required_vars - set(os.environ))
assert len(missing_vars) == 0, f"Missing required config variables: {missing_vars}"

logger = logging.getLogger(__name__)


def run():
    # Heroku config vars
    user = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    host = os.environ['POLLHOST']
    login_type = os.environ.get('LOGIN_TYPE', 'uw')
    lifetime = float(os.environ.get('LIFETIME', 'inf'))

    with PollBot(user, password, host, login_type=login_type, lifetime=lifetime) as bot:
        bot.run()


def main():
    logger.info("Starting blocking scheduler.")

    scheduler = BlockingScheduler()
    scheduler.add_job(run, 'cron',
                      day_of_week=os.environ['DAY_OF_WEEK'],
                      hour=os.environ['HOUR'],
                      minute=os.environ['MINUTE'])
    scheduler.start()


if __name__ == '__main__':
    main()
