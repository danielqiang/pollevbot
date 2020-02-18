from PollEvBot.bot import PollBot
from itertools import count
import sys
import time

sys.tracebacklimit = 0  # Avoid long tracebacks


def launch_ui(user: str, password: str, host: str, login_type: str = 'pollev'):
    with PollBot(user, password, host, login_type=login_type) as bot:
        if not bot.login():
            raise RuntimeError("Your username or password was incorrect.")
        print("Login successful.")
        token = bot.get_firehose_token()

        for i in count(1):
            poll_id = bot.get_new_poll_id(firehose_token=token)
            if not poll_id:
                print("\r{} has not opened any new polls. Waiting 2 seconds before checking again. "
                      "Checked {} times so far.".format(bot.host.capitalize(), i),
                      end='')
                time.sleep(2)
                continue
            print(f"\n{bot.host.capitalize()} has opened a new poll! Waiting {0} seconds before responding.")
            resp = bot.answer_poll(poll_id)
            print(resp)


def main():
    user = 'My Username'
    password = 'My Password'
    host = 'PollEverywhere URL Extension e.g. "uwpsych"'

    # If you're not using a UW PollEv account, just omit the 'login_type' argument
    launch_ui(user, password, host, login_type='uw')


if __name__ == '__main__':
    main()