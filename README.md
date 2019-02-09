# PollEvBot

PollEvBot is a bot that automatically responds to polls from PollEverywhere. It continually checks if a specified poll user has opened any polls. Once a poll has been opened, the bot identifies and submits the correct response to PollEverywhere. It submits a random option if the poll does not have a specified correct response.

## Dependencies

[Requests](https://github.com/requests/requests), [BeautifulSoup](https://github.com/waylan/beautifulsoup)

## Requirements

A [PollEverywhere account](https://www.pollev.com). That's it. :)

## Usage

First, install `PollEvBot`:
```
pip install PollEvBot
```

Set your username, password, and desired poll host:
```python
user = 'My Username'
password = 'My Password'
host = 'PollEverywhere URL Extension e.g. "uwpsych"'
```

And run the script.
```python
from PollEvBot.src import Bot

user = 'My Username'
password = 'My Password'
host = 'PollEverywhere URL Extension e.g. "uwpsych"'

# If you're not using a UW PollEv account, just omit the 'organization' argument
with Bot(user, password, host, organization='uw') as bot:
    bot.run()
```
Alternatively, you can input your login credentials into main.py and run it from there.

## Disclaimer

I do not promote or condone the usage of this script for any kind of academic misconduct or dishonesty, including but not limited to cheating on in-class poll quizzes or spoofing attendance polls. I wrote this script for the sole purpose of educating myself on cybersecurity and web protocols, and cannot be held liable for any indirect, incidental, consequential, special, or exemplary damages arising out of or in connection with the usage of this script.
