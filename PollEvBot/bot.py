import time
import requests
from .endpoints import endpoints


class Bot(requests.Session):
    """
    A response bot for multiple-choice polls on PollEverywhere.

    Identifies and submits correct responses to polls in real-time by parsing response metadata.
    Submits a random response if a poll does not specify a correct option.

    """
    def __init__(self, username, password, poll_host, organization=None):
        super().__init__()
        self.username = username
        self.password = password
        self.poll_host = poll_host.lower()
        self.organization = organization.lower() if organization else None

        # PollEv requires a timestamp (milliseconds since epoch)
        # on most requests.
        self.timestamp = round(time.time() * 1000)
        self.headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                      "(KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"}
        # Unique id for current poll session
        self.uid = None

    def login(self):
        """
        Logs into PollEv. Exits if login fails.
        """
        # Upon successful login, PollEv sets a session_id cookie.
        try:
            if self.organization == 'uw':
                self._uw_login()
            else:
                self._pollev_login()
        except AssertionError:
            exit("Your username or password was incorrect.")

        print("Login successful.\n")

    def _pollev_login(self):
        """
        Logs into PollEv via the homepage.

        :raise AssertionError if login fails.
        """
        r = self.post(endpoints['login'],
                      headers={'x-csrf-token': self.get_csrf_token()},
                      data={'login': self.username, 'password': self.password})
        assert not r.text

    def _uw_login(self):
        """
        Logs into PollEv through MyUW.

        :raise AssertionError if login fails.
        """
        import bs4 as bs
        import re

        # UW implements a SAML-based Single-Sign-On protocol for user authentication.
        # When user authentication fails, UW will send an empty SAML response.
        r = self.get(endpoints['uw_saml'])
        soup = bs.BeautifulSoup(r.text, "html.parser")
        session_id = re.findall('jsessionid=(.*)\.', soup.find('form', id='idplogindiv')['action'])
        r = self.post(endpoints['uw_login'].format(id=session_id),
                      data={
                          'j_username': self.username,
                          'j_password': self.password,
                          '_eventId_proceed': 'Sign in'
                      })
        soup = bs.BeautifulSoup(r.text, "html.parser")
        saml_response = soup.find('input', type='hidden')

        assert saml_response

        r = self.post(endpoints['uw_callback'], data={'SAMLResponse': saml_response['value']})
        auth_token = re.findall('pe_auth_token=(.*)', r.url)[0]
        self.post(endpoints['uw_auth_token'],
                  headers={'x-csrf-token': self.get_csrf_token()},
                  data={'token': auth_token})

    def get_csrf_token(self):
        return self.get(endpoints['csrf'].format(timestamp=self.timestamp)).json()['token']

    @staticmethod
    def generate_uuid():
        """
        Generates a uuid string (32-digit hex string separated by dashes).

        Helper method for get_firehose_token().
        """
        # String digit format: 8-4-4-4-12
        import secrets
        return str(secrets.token_hex(4)) + '-' + str(secrets.token_hex(2)) + '-' + \
               str(secrets.token_hex(2)) + '-' + str(secrets.token_hex(2)) + '-' + \
               str(secrets.token_hex(6))

    def get_firehose_token(self):
        """
        Given that the user is logged in, retrieve a firehose token.
        If the poll host is not affiliated with UW, PollEv will return
        a firehose token with a null value.
        """
        # Before issuing a token, AWS checks for two visitor cookies that
        # PollEverywhere generates using js. They are random uuids.
        self.cookies['pollev_visitor'] = self.generate_uuid()
        self.cookies['pollev_visit'] = self.generate_uuid()
        r = self.get(endpoints['firehose_auth'].format(
            host=self.poll_host, timestamp=self.timestamp)
        )
        return r.json()['firehose_token']

    def has_open_poll(self, firehose_token=None):
        """
        Given that the user is logged in, checks if the poll host has
        any active polls on PollEv. If an active poll exists, retrieves
        the poll's unique id.

        :param firehose_token: Authentication token issued by Firehose.
        """
        import json

        # All polls for PollEv are directed through Amazon Firehose. For hosts affiliated with certain
        # organizations (e.g. UW), Firehose issues an authentication token.
        # Firehose does not issue a token for hosts unaffiliated with an organization.
        try:
            if firehose_token:
                r = self.get(endpoints['firehose_with_token'].format(
                    host=self.poll_host, token=firehose_token, timestamp=self.timestamp
                ), timeout=0.3)
            else:
                r = self.get(endpoints['firehose_no_token'].format(
                    host=self.poll_host, timestamp=self.timestamp
                ), timeout=0.3)
            # The uid is a poll's unique id. If this uid is different, then
            # the host has opened a new poll.
            uid = json.loads(r.json()['message'])['uid']
        # Firehose either doesn't respond or responds with no data if no poll is open.
        except (requests.exceptions.ReadTimeout, KeyError):
            return False
        # Ignore polls we've already answered.
        if self.uid == uid:
            return False

        self.uid = uid
        return True

    def clear_responses(self):
        """
        Given that the user is logged in and the poll is open,
        clears any previous responses sent by the user.
        """
        r = self.get(endpoints['check_responses'].format(uid=self.uid, timestamp=self.timestamp),
                     headers={'accept': 'application/json'})
        # If the poll is currently unanswered, the response json is empty.
        if r.json():
            self.post(endpoints['clear_responses'].format(id=r.json()[0]['id']),
                      headers={'x-http-method-override': 'DELETE',
                               'x-csrf-token': self.get_csrf_token()})

    def answer_poll(self, randomize=True):
        """
        Given that the user is logged in and the poll is open, submits a response to the poll.
        If the poll host specified a correct option, submit the correct option as a response.
        Otherwise, submit the first option or a random option.

        :param randomize: If true, submit a random response when no correct option is specified.
        """
        from random import randint

        poll_data = self.get(endpoints['poll_data'].format(
            uid=self.uid, timestamp=self.timestamp)
        ).json()['multiple_choice_poll']

        index = randint(0, len(poll_data['options']) - 1) if randomize else 0
        has_correct_ans = False
        # Each possible response in a poll has a unique id.
        answer_id = poll_data['options'][index]['id']

        for option in poll_data['options']:
            # If a correct answer exists, submit that one
            if option['correct'] is True:
                answer_id = option['id']
                has_correct_ans = True
                break

        r = self.post(endpoints['respond_to_poll'].format(uid=self.uid, id=answer_id),
                      headers={'x-csrf-token': self.get_csrf_token()},
                      data={'accumulator_id': answer_id, 'poll_id': poll_data['id']})
        self.print_results(poll_data, r, answer_id, has_correct_ans)

    @staticmethod
    def print_results(poll_data, response, answer_id, has_correct_ans):
        """
        Informational terminal output.
        """
        correct_ans_index = answer_id - poll_data['options'][0]['id']

        print("\nPoll Title: " + poll_data['title'] + "\n")
        if response.status_code == 422:
            print("Could not submit a response. This could be because:")
            print("\t1. The host has locked this poll and is not accepting responses at this time.")
            print("\t2. You have already submitted a response.")
        elif has_correct_ans:
            print("The correct answer to this question is option {}: {}.".format(
                str(correct_ans_index + 1), poll_data['options'][correct_ans_index]['humanized_value'])
            )
            print("Successfully selected option " + str(correct_ans_index + 1) + "!")
        else:
            print("The host did not specify a correct answer for this question. ")
            print("Successfully selected option 1: {}!".format(
                str(poll_data['options'][0]['humanized_value']))
            )
        print()

    def run(self, delay=5, wait_to_respond=5, clear_responses=True):
        """
        Runs the script.

        :param delay: Specifies how long the script will wait between queries
                        to check if a poll is open (seconds).
        :param wait_to_respond: Specifies how long the script will wait to
                        respond to an open poll (seconds).
        :param clear_responses: If true, clears any previous responses sent
                        by the user before submitting a response.
        """
        from itertools import count

        self.login()
        token = self.get_firehose_token()

        while True:
            c = count(1)
            while not self.has_open_poll(firehose_token=token):
                print("\r{} has not opened any new polls. Waiting {} seconds before checking again. "
                      "Checked {} times so far.".format(self.poll_host.capitalize(), delay, next(c)),
                      end='')
                time.sleep(delay)
            if wait_to_respond > 0:
                print("{} has opened a new poll! Waiting {} seconds before responding.".format(
                    self.poll_host.capitalize(), wait_to_respond)
                )
                time.sleep(wait_to_respond)
            if clear_responses:
                self.clear_responses()
            self.answer_poll()
