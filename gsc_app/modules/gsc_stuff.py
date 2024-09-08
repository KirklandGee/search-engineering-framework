import gscwrapper
import json
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GSCStuff:
    def __init__(self):
        self.account = self.load_account()

    def load_account(self):
        with open('/Users/kirklandgee/repos/search-engineering/gsc_app/.token_cache', 'rb') as token_file:
            token_data = pickle.load(token_file)

        # Assuming token_data is a JSON string, parse it into a dictionary
        token_data = json.loads(token_data)

        # Create Credentials object from token data
        credentials = Credentials(
            token=token_data['token'],
            refresh_token=token_data['refresh_token'],
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        )

        # Build the service
        service = build('searchconsole', 'v1', credentials=credentials, cache_discovery=False)

        # Create an Account object (assuming gscwrapper.Account is similar to the one in the original code)
        account = gscwrapper.account.Account(service, credentials)

        return account