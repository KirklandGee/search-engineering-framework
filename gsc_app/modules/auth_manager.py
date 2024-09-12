import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
import json
import gscwrapper

class AuthManager:
    def __init__(self):
        self.client_config = {
            "web": {
                "client_id": st.secrets["google_oauth"]["client_id"],
                "client_secret": st.secrets["google_oauth"]["client_secret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        self.flow = Flow.from_client_config(
            self.client_config,
            scopes=['https://www.googleapis.com/auth/webmasters.readonly'],
            redirect_uri='https://gsc-tools.streamlit.app/'
        )

    def get_authorization_url(self):
        return self.flow.authorization_url(prompt='consent')[0]

    def handle_redirect(self, code):
        try:
            self.flow.fetch_token(code=code)
            return self.flow.credentials.to_json()
        except InvalidGrantError:
            raise ValueError("The authorization code has expired. Please sign in again.")
        except Exception as e:
            raise ValueError(f"An error occurred during authentication: {str(e)}")

    def get_service(self, credentials_json):
        try:
            credentials = Credentials.from_authorized_user_info(json.loads(credentials_json))
            return build('searchconsole', 'v1', credentials=credentials)
        except Exception as e:
            raise ValueError(f"Error initializing service: {str(e)}")

    def get_site_list(self, service):
        try:
            sites = service.sites().list().execute()
            return [site['siteUrl'] for site in sites.get('siteEntry', [])]
        except Exception as e:
            raise ValueError(f"An error occurred while fetching site list: {e}")

    def load_cached_credentials(self):
        return st.session_state.get('credentials')

    def save_cached_credentials(self, credentials_json):
        st.session_state['credentials'] = credentials_json

    def load_wrapper_account(self):
        # Assuming token_data is a JSON string, parse it into a dictionary
        token_data = self.load_cached_credentials()
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
    
    def search_analytics_query(self, service, site, request):
        try:
            result = service.searchanalytics().query(siteUrl=site, body=request).execute()
            return result
        except Exception as e:
            raise ValueError(f"An error occurred while fetching search analytics data: {e}")
        
    def search_analytics_query_daily(self, service, site, request):

        if "date" not in request["dimensions"]:
            request["dimensions"].append("date")
        try:
            result = service.searchanalytics().query(siteUrl=site, body=request).execute()
            return result
        except Exception as e:
            raise ValueError(f"An error occurred while fetching search analytics data: {e}")