import requests
from typing import *
from .endpoints import endpoints


class PollBot:
    def __init__(self, user: str, password: str, host: str, login_type: str = 'pollev'):
        self.user = user
        self.password = password
        self.host = host
        self.login_type = login_type

        self.session = requests.Session()
        self.session.headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
        }
        self.last_poll_id = None  # Avoid re-answering polls

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    @staticmethod
    def timestamp() -> float:
        from time import time
        return round(time() * 1000)

    def _get_csrf_token(self) -> str:
        return self.session.get(endpoints['csrf'].format(timestamp=self.timestamp())).json()['token']

    def _pollev_login(self) -> bool:
        """
        Logs into PollEv via the homepage.

        Returns True on success, False otherwise.
        """
        r = self.session.post(endpoints['login'],
                              headers={'x-csrf-token': self._get_csrf_token()},
                              data={'login': self.user, 'password': self.password})
        # If login is successful, PollEv sends an empty HTTP response.
        return not r.text

    def _uw_login(self) -> bool:
        """
        Logs into PollEv through MyUW.

        Returns True on success, False otherwise.
        """
        import bs4 as bs
        import re

        # UW implements a SAML-based Single-Sign-On protocol for user authentication.
        r = self.session.get(endpoints['uw_saml'])
        soup = bs.BeautifulSoup(r.text, "html.parser")
        session_id = re.findall('jsessionid=(.*)\.', soup.find('form', id='idplogindiv')['action'])
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

        r = self.session.post(endpoints['uw_callback'], data={'SAMLResponse': saml_response['value']})
        auth_token = re.findall('pe_auth_token=(.*)', r.url)[0]
        self.session.post(endpoints['uw_auth_token'],
                          headers={'x-csrf-token': self._get_csrf_token()},
                          data={'token': auth_token})
        return True

    def login(self) -> bool:
        if self.login_type.lower() == 'pollev':
            return self._pollev_login()
        elif self.login_type.lower() == 'uw':
            return self._uw_login()
        raise ValueError(f"{self.login_type} is not a supported login type; use 'pollev' or 'uw'.")

    def get_firehose_token(self) -> str:
        """
        Given that the user is logged in, retrieve a firehose token.
        If the poll host is not affiliated with UW, PollEv will return
        a firehose token with a null value.

        Exits if the specified poll host is not found.
        """
        from uuid import uuid4
        # Before issuing a token, AWS checks for two visitor cookies that
        # PollEverywhere generates using js. They are random uuids.
        self.session.cookies['pollev_visitor'] = str(uuid4())
        self.session.cookies['pollev_visit'] = str(uuid4())
        r = self.session.get(endpoints['firehose_auth'].format(
            host=self.host, timestamp=self.timestamp)
        )

        if "presenter not found" in r.text.lower():
            raise ValueError(f"'{self.host}' is not a valid poll host.")
        return r.json()['firehose_token']

    def get_new_poll_id(self, firehose_token=None) -> Union[str, None]:
        import json

        try:
            if firehose_token:
                r = self.session.get(endpoints['firehose_with_token'].format(
                    host=self.host, token=firehose_token, timestamp=self.timestamp
                ), timeout=0.3)
            else:
                r = self.session.get(endpoints['firehose_no_token'].format(
                    host=self.host, timestamp=self.timestamp
                ), timeout=0.3)
            # Unique id for poll
            poll_id = json.loads(r.json()['message'])['uid']
            return poll_id if poll_id != self.last_poll_id else None

        # Firehose either doesn't respond or responds with no data if no poll is open.
        except (requests.exceptions.ReadTimeout, KeyError):
            return None

    def answer_poll(self, poll_id) -> Union[dict, None]:
        import random

        poll_data = self.session.get(endpoints['poll_data'].format(uid=poll_id)).json()
        option_id = random.choice(poll_data['options'])['id']
        r = self.session.post(
            endpoints['respond_to_poll'].format(uid=poll_id),
            headers={'x-csrf-token': self._get_csrf_token()},
            data={'option_id': option_id, 'isPending': True, 'source': "pollev_page"}
        )
        self.last_poll_id = poll_id
        return r.json()
