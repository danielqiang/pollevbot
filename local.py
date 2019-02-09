from src.bot import Bot


def main():
    from scripting_tools import user, password

    host = 'TESTPRESENTE201'

    with Bot(user, password, host, organization='uw') as bot:
        bot.run()


if __name__ == '__main__':
    main()
