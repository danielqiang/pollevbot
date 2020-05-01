import os
from pollevbot import PollBot


def main():
    # Heroku config vars
    user = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    host = os.environ['POLLHOST']

    with PollBot(user, password, host) as bot:
        bot.run()


if __name__ == '__main__':
    main()
