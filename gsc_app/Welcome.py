import streamlit as st
from PIL import Image
from modules.auth_manager import AuthManager
# Set page configuration
st.set_page_config(
    page_title="The Search Engineering Framework's GSC API Tool",
    page_icon="🔍",
    layout="wide"
)

# Initialize AuthManager
st.session_state.auth_manager = AuthManager(redirect_uri="https://gsc-api-tool.streamlit.app/")

# Handle OAuth redirect
if 'code' in st.query_params:
    credentials_json = st.session_state.auth_manager.handle_redirect(st.query_params['code'])
    st.session_state.auth_manager.save_cached_credentials(credentials_json)
    st.success("Successfully signed in!")

# Load cached credentials
credentials_json = st.session_state.auth_manager.load_cached_credentials()

# Initialize service if credentials are available
if credentials_json:
    service = st.session_state.auth_manager.get_service(credentials_json)
    st.session_state.service = service

col1, col2 = st.columns([4, 2])
# Title and introduction

with col1:
    st.title("The Search Engineering Framework's GSC API Tool")
    # Display sign-in/sign-out options
    if credentials_json:
        st.write("You are currently signed in.")
        if st.button("Sign out"):
            st.session_state.auth_manager.save_cached_credentials(None)
            st.session_state.pop('service', None)
            st.rerun()

    else:
        st.write("You are not signed in. Please click the button below to authenticate.")
        authorization_url = st.session_state.auth_manager.get_authorization_url()
        st.link_button("Sign in with Google", authorization_url, use_container_width=True)
    
    st.markdown("""
    This tool allows you to access and analyze your data from the Google Search Console API.

    ### Key Features:
    - Authenticate securely with your Google account
    - Select from your available sites in Google Search Console
    - Perform manual data pulls with customizable parameters
    - Apply advanced filters to refine your queries
    - View data grouped by page or in detailed format
    - Generate specialized reports:
    - Cannibalization Report
    - CTR Yield Curve
    - (More to come!)
    - Utilize functions from the gscwrapper package
    - Visualize daily search performance data
    """)


with col2:
    image = Image.open("gsc_app/images/kirkland.jpeg")
    st.image(image, caption="Kirkland Gee: The Search Engineering Framework")