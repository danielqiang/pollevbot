from src import Bot


def main():
    user = 'My Username'
    password = 'My Password'
    host = 'PollEverywhere URL Extension e.g. "uwpsych"'

    # If you're not using a UW PollEv account, just omit the 'organization' argument
    with Bot(user, password, host, organization='uw') as bot:
        bot.run()


if __name__ == '__main__':
    main()
