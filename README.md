# pollevbot

pollevbot is a bot that automatically responds to polls at [pollev.com](https://pollev.com/). It continually checks if a specified poll user has opened any polls. Once a poll has been opened, the bot submits a random response. 

Requires Python 3.7 or later.
## Dependencies

[Requests](https://github.com/requests/requests), [BeautifulSoup](https://github.com/waylan/beautifulsoup)

## Usage

First, install `pollevbot`:
```
pip install pollevbot
```

Set your username, password, and desired poll host:
```python
user = 'My Username'
password = 'My Password'
host = 'PollEverywhere URL Extension e.g. "uwpsych"'
```

And run the script.
```python
from pollevbot import PollBot

user = 'My Username'
password = 'My Password'
host = 'PollEverywhere URL Extension e.g. "uwpsych"'

# If you're using a non-UW PollEv account,
# add the argument "login_type='pollev'"
with PollBot(user, password, host) as bot:
    bot.run()
```
Alternatively, you can set your login credentials in [main.py](pollevbot/main.py) and run it from there.

## Disclaimer

I do not promote or condone the usage of this script for any kind of academic misconduct or dishonesty, including but not limited to cheating on in-class poll quizzes or spoofing attendance polls. I wrote this script for the sole purpose of educating myself on cybersecurity and web protocols, and cannot be held liable for any indirect, incidental, consequential, special, or exemplary damages arising out of or in connection with the usage of this script.
