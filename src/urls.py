POLLEV_HOST_URL = 'https://pollev.com/{}'

# MyUW Login URLs
UW_LOGIN_URL = 'https://idp.u.washington.edu/idp/profile/SAML2/Redirect/SSO;jsessionid={}.idp03?execution=e1s1'
UW_HOME_URL = 'https://idp.u.washington.edu'
SAML_REQ_URL = 'https://www.polleverywhere.com/auth/washington?redirect=https%3A%2F%2Fpollev.com%2F&token_required=false'
UW_REFERRER_URL = 'https://idp.u.washington.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s1'
CALLBACK_URL = 'https://www.polleverywhere.com/auth/washington/callback'
P_AUTH_TOKEN_URL = 'https://pollev.com/?pe_auth_token={}'
P_AUTH_URL = 'https://pollev.com/proxy/api/participant_auth_token'

# Connecting to Poll Channel URLs
POLL_SEARCH_URL = 'https://pollev.com/proxy/api/users/search?login_or_email={}&_={}'
POLL_PROFILE_URL = 'https://pollev.com/proxy/api/users/{}?_={}'
REGISTRATION_URL = 'https://pollev.com/proxy/api/users/{}/registration_info?_={}'
PROFILE_URL = 'https://pollev.com/proxy/api/profile?_={}'
LOGIN_PAGE_URL = "https://pollev.com/login"
CSRF_URL = "https://pollev.com/proxy/api/csrf_token?_={}"

# Responding to Poll URLs
TOKEN_UID_URL = 'https://firehose-production.polleverywhere.com/users/{}/activity/current.json?firehose_token={}&last_message_sequence=0&_={}'
NO_TOKEN_UID_URL = 'https://firehose-production.polleverywhere.com/users/{}/activity/current.json?last_message_sequence=0&_={}'
POLLEV_INFO_URL = 'https://pollev.com/proxy/api/polls/{}?_={}'
SEND_RESPONSE_URL = 'https://pollev.com/proxy/multiple_choice_polls/{}/options/{}/results.json?include_confirmation_message=1'
POLL_RESULTS_URL = 'https://pollev.com/proxy/api/results/{}'
RESPONSE_UID_URL = 'https://pollev.com/proxy/my/results?permalinks%5B%5D={}&per_page=500&include_archived=false&_={}'

