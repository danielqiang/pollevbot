# pollevbot

**pollevbot** is a bot that automatically responds to polls on [pollev.com](https://pollev.com/). 
It continually checks if a specified host has opened any polls. Once a poll has been opened, 
it submits a random response. 

Requires Python 3.7 or later.
## Dependencies

[Requests](https://pypi.org/project/requests/), 
[BeautifulSoup](https://pypi.org/project/beautifulsoup4/). 

[APScheduler](https://pypi.org/project/APScheduler/) to deploy to Heroku.

## Usage

Install `pollevbot`:
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
Alternatively, you can clone this repo, set your login credentials in 
[main.py](pollevbot/main.py) and run it from there.

## Heroku

**pollevbot** can be configured to run at scheduled dates/times with [Heroku](http://heroku.com/):

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/danielqiang/pollevbot)

#### Example ####

Suppose you want to answer polls made by poll host `teacher123` every Monday and Wednesday 
from 11:30 AM to 12:30 PM in your timezone on your UW account. To do this, set the config 
variables as follows:

* `DAY_OF_WEEK=mon,wed`
* `HOUR=11`
* `LIFETIME=3600`
* `LOGIN_TYPE=uw`
* `MINUTE=30`
* `PASSWORD=yourpassword`
* `POLLHOST=teacher123`
* `USERNAME=yourusername`

**Notes**: 

* The variables (`DAY_OF_WEEK`, `HOUR`, `MINUTE`) are 
[cron](https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html) strings.
* Your timezone is automatically detected.

Then click `Deploy App` and wait for the app to finish building. 
**pollevbot** is now deployed to the Heroku! 

## Disclaimer

I do not promote or condone the usage of this script for any kind of academic misconduct 
or dishonesty. I wrote this script for the sole purpose of educating myself on cybersecurity 
and web protocols, and cannot be held liable for any indirect, incidental, consequential, 
special, or exemplary damages arising out of or in connection with the usage of this script.
