import os
from pollevbot import PollBot
from apscheduler.schedulers.blocking import BlockingScheduler


def run():
    # Heroku config vars
    user = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    host = os.environ['POLLHOST']

    with PollBot(user, password, host, closed_wait=1000) as bot:
        bot.run()


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(run, 'cron',
                      day_of_week=os.environ['DAY_OF_WEEK'],
                      hour=os.environ['HOUR'],
                      minute=os.environ['MINUTE'])
    scheduler.start()


if __name__ == '__main__':
    main()
