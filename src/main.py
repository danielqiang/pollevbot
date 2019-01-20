from src import Poll


def main():
    user = 'MyUW Username (@uw.edu email)'
    password = 'MyUW Password'
    host = 'PollEverywhere URL Extension e.g. "uwpsych"'

    with Poll(user, password, host) as poll:
        poll.run()


if __name__ == '__main__':
    main()
