from pollevbot import PollBot


def main():
    user = 'My Username'
    password = 'My Password'
    host = 'PollEverywhere URL Extension e.g. "uwpsych"'

    # If you're using a non-uw PollEv account,
    # add the argument "login_type='pollev'"
    with PollBot(user, password, host) as bot:
        bot.run()


if __name__ == '__main__':
    main()
