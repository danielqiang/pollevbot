import requests
import logging
import time
from typing import Optional
from .endpoints import endpoints

logger = logging.getLogger(__name__)
__all__ = ['PollBot']


class LoginError(RuntimeError):
    """Error indicating that login failed."""


class PollBot:
    """Bot for answering polls on PollEverywhere.
    Responses are randomly selected.

    Usage:
    >>> bot = PollBot(user='username', password='password',
    ...               host='host', login_type='uw')
    >>> bot.run()

    Can also be used as a context manager.
    """

    def __init__(self, user: str, password: str, host: str,
                 login_type: str = 'uw', min_option: int = 0,
                 max_option: int = None, closed_wait: float = 5,
                 open_wait: float = 5, lifetime: float = float('inf')):
        """
        Constructor. Creates a PollBot that answers polls on pollev.com.

        :param user: PollEv account username.
        :param password: PollEv account password.
        :param host: PollEv host name, i.e. 'uwpsych'
        :param login_type: Login protocol to use (either 'uw' or 'pollev').
                        If 'uw', uses MyUW (SAML2 SSO) to authenticate.
                        If 'pollev', uses pollev.com.
        :param min_option: Minimum index (0-indexed) of option to select (inclusive).
        :param max_option: Maximum index (0-indexed) of option to select (exclusive).
        :param closed_wait: Time to wait in seconds if no polls are open
                        before checking again.
        :param open_wait: Time to wait in seconds if a poll is open
                        before answering.
        :param lifetime: Lifetime of this PollBot (in seconds).
                        If float('inf'), runs forever.
        :raises ValueError: if login_type is not 'uw' or 'pollev'.
        """
        if login_type not in {'uw', 'pollev'}:
            raise ValueError(f"'{login_type}' is not a supported login type. "
                             f"Use 'uw' or 'pollev'.")
        if login_type == 'pollev' and user.strip().lower().endswith('@uw.edu'):
            logger.warning(f"{user} looks like a UW email. "
                           f"Use login_type='uw' to log in with MyUW.")

        self.user = user
        self.password = password
        self.host = host
        self.login_type = login_type
        # 0-indexed minimum and maximum option
        # indices to select on poll.
        self.min_option = min_option
        self.max_option = max_option
        # Wait time in seconds if poll is
        # closed or open, respectively
        self.closed_wait = closed_wait
        self.open_wait = open_wait

        self.lifetime = lifetime
        self.start_time = time.time()

        self.session = requests.Session()
        self.session.headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
        }
        # IDs of all polls we have answered already
        self.answered_polls = set()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    @staticmethod
    def timestamp() -> float:
        return round(time.time() * 1000)

    def _get_csrf_token(self) -> str:
        url = endpoints['csrf'].format(timestamp=self.timestamp())
        return self.session.get(url).json()['token']

    def _pollev_login(self) -> bool:
        """
        Logs into PollEv through pollev.com.
        Returns True on success, False otherwise.
        """
        logger.info("Logging into PollEv through pollev.com.")

        r = self.session.post(endpoints['login'],
                              headers={'x-csrf-token': self._get_csrf_token()},
                              data={'login': self.user, 'password': self.password})
        # If login is successful, PollEv sends an empty HTTP response.
        return not r.text

    def _uw_login(self):
        """
        Logs into PollEv through MyUW.
        Returns True on success, False otherwise.
        """
        import bs4 as bs
        import re

        logger.info("Logging into PollEv through MyUW.")

        r = self.session.get(endpoints['uw_saml'])
        soup = bs.BeautifulSoup(r.text, "html.parser")
        data = soup.find('form', id='idplogindiv')['action']
        session_id = re.findall(r'jsessionid=(.*)\.', data)

        r = self.session.post(endpoints['uw_login'].format(id=session_id),
                              data={
                                  'j_username': self.user,
                                  'j_password': self.password,
                                  '_eventId_proceed': 'Sign in'
                              })
        soup = bs.BeautifulSoup(r.text, "html.parser")
        saml_response = soup.find('input', type='hidden')

        # When user authentication fails, UW will send an empty SAML response.
        if not saml_response:
            return False

        r = self.session.post(endpoints['uw_callback'],
                              data={'SAMLResponse': saml_response['value']})
        auth_token = re.findall('pe_auth_token=(.*)', r.url)[0]
        self.session.post(endpoints['uw_auth_token'],
                          headers={'x-csrf-token': self._get_csrf_token()},
                          data={'token': auth_token})
        return True

    def login(self):
        """
        Logs into PollEv.

        :raises LoginError: if login failed.
        """
        if self.login_type.lower() == 'uw':
            success = self._uw_login()
        else:
            success = self._pollev_login()
        if not success:
            raise LoginError("Your username or password was incorrect.")
        logger.info("Login successful.")

    def get_firehose_token(self) -> str:
        """
        Given that the user is logged in, retrieve an AWS firehose token.
        If the poll host is not affiliated with UW, PollEv will return
        a firehose token with a null value.

        :raises ValueError: if the specified poll host is not found.
        """
        from uuid import uuid4
        # Before issuing a token, AWS checks for two visitor cookies that
        # PollEverywhere generates using js. They are random uuids.
        self.session.cookies['pollev_visitor'] = str(uuid4())
        self.session.cookies['pollev_visit'] = str(uuid4())
        url = endpoints['firehose_auth'].format(
            host=self.host,
            timestamp=self.timestamp
        )
        r = self.session.get(url)

        if "presenter not found" in r.text.lower():
            raise ValueError(f"'{self.host}' is not a valid poll host.")
        return r.json()['firehose_token']

    def get_new_poll_id(self, firehose_token=None) -> Optional[str]:
        import json

        if firehose_token:
            url = endpoints['firehose_with_token'].format(
                host=self.host,
                token=firehose_token,
                timestamp=self.timestamp
            )
        else:
            url = endpoints['firehose_no_token'].format(
                host=self.host,
                timestamp=self.timestamp
            )
        try:
            r = self.session.get(url, timeout=0.3)
            # Unique id for poll
            poll_id = json.loads(r.json()['message'])['uid']
        # Firehose either doesn't respond or responds with no data if no poll is open.
        except (requests.exceptions.ReadTimeout, KeyError):
            return None
        if poll_id in self.answered_polls:
            return None
        else:
            self.answered_polls.add(poll_id)
            return poll_id

    def answer_poll(self, poll_id) -> dict:
        import random

        url = endpoints['poll_data'].format(uid=poll_id)
        poll_data = self.session.get(url).json()
        options = poll_data['options'][self.min_option:self.max_option]
        try:
            option_id = random.choice(options)['id']
        except IndexError:
            # `options` was empty
            logger.error(f'Could not answer poll: poll only has '
                         f'{len(poll_data["options"])} options but '
                         f'self.min_option was {self.min_option} and '
                         f'self.max_option: {self.max_option}')
            return {}
        r = self.session.post(
            endpoints['respond_to_poll'].format(uid=poll_id),
            headers={'x-csrf-token': self._get_csrf_token()},
            data={'option_id': option_id, 'isPending': True, 'source': "pollev_page"}
        )
        return r.json()

    def alive(self):
        return time.time() <= self.start_time + self.lifetime

    def run(self):
        """Runs the script."""
        try:
            self.login()
            token = self.get_firehose_token()
        except (LoginError, ValueError) as e:
            logger.error(e)
            return

        while self.alive():
            poll_id = self.get_new_poll_id(token)

            if poll_id is None:
                logger.info(f'`{self.host}` has not opened any new polls. '
                            f'Waiting {self.closed_wait} seconds before checking again.')
                time.sleep(self.closed_wait)
            else:
                logger.info(f"{self.host} has opened a new poll! "
                            f"Waiting {self.open_wait} seconds before responding.")
                time.sleep(self.open_wait)
                r = self.answer_poll(poll_id)
                logger.info(f'Received response: {r}')
