import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
import json
import os
import pickle

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
            scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        )
        self.flow.redirect_uri = "http://localhost:8501"  # Adjust this to your Streamlit app's URL

    def get_authorization_url(self):
        return self.flow.authorization_url(prompt='consent')[0]

    def handle_redirect(self, code):
        try:
            self.flow.fetch_token(code=code)
            credentials = self.flow.credentials
            st.session_state.credentials = credentials.to_json()
            return True
        except InvalidGrantError:
            st.error("The authorization code has expired. Please sign in again.")
            st.session_state.credentials = None
            return False

    def get_service(self, credentials):
        if st.session_state.credentials:
            try:
                credentials = Credentials.from_authorized_user_info(json.loads(st.session_state.credentials))
                return build('searchconsole', 'v1', credentials=credentials)
            except Exception as e:
                st.error(f"Error initializing service: {str(e)}")
                st.session_state.credentials = None
        return None
      
    def get_site_list(self, service):
        try:
            sites = service.sites().list().execute()
            return [site['siteUrl'] for site in sites.get('siteEntry', [])]
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def search_analytics_query(self, service, site_url, request_body):
        try:
            new_request = request_body.copy()
            result = service.searchanalytics().query(
                siteUrl=site_url,
                body=new_request
            ).execute()
            return result
        except Exception as e:
            st.error(f"Error querying Search Console API: {str(e)}")
            return None
        
    def search_analytics_query_daily(self, service, site_url, request_body):
        try:
            new_request = request_body.copy()
            new_request['dimensions'] = ['page','query','date']

            result = service.searchanalytics().query(
                siteUrl=site_url,
                body=new_request
            ).execute()
            return result
        except Exception as e:
            st.error(f"Error querying Search Console API: {str(e)}")

    def load_cached_credentials(self):
        cache_file = '.token_cache'
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None

    def save_cached_credentials(self, credentials):
        cache_file = '.token_cache'
        with open(cache_file, 'wb') as f:
            pickle.dump(credentials, f)
