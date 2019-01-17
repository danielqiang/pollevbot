from PollEvBot.src import Poll


def main():
    host = 'My Favorite Teacher'
    user = 'MyUW Username (@uw.edu email)'
    password = 'MyUW Password'

    with Poll(username=user, password=password, poll_host=host) as poll:
        poll.run(delay=3, wait_to_respond=15, run_forever=True)


if __name__ == '__main__':
    main()
