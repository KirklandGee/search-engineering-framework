import streamlit as st
from modules.auth_manager import AuthManager

# Set page configuration
st.set_page_config(
    page_title="Group By Time - SE Framework GSC API Tool",
    page_icon="📅",
    layout="wide"
)

if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = AuthManager()

if 'credentials' not in st.session_state:
    st.session_state.credentials = None

if 'service' not in st.session_state:
    st.session_state.service = None

credentials_json = st.session_state.auth_manager.load_cached_credentials()

if credentials_json:
    service = st.session_state.auth_manager.get_service(credentials_json)
    st.session_state.service = service

def load_grouped_data(account, web_property, start_date, end_date, period):
    webproperty = account[web_property]

    # Convert date objects to string format
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    period_map = {
        "Day": "D",
        "Week": "W",
        "Month": "M",
        "Quarter": "Q",
        "Year": "Y"
    }

    period_letter = period_map.get(period, "D")  # Default to "D" if not found
    report = (
        webproperty
        .query
        .range(start_date_str, end_date_str)
        .dimensions(["date"])
        .get()
    )

    report_grouped = report.group_data_by_period(period=period_letter)
    report_grouped.rename(columns={"date": period}, inplace=True)

    return report_grouped
 
col1, col2 = st.columns([3, 2])

with col1:
    st.title("Group By Time")
    st.markdown("This page allows you to group your data by different time ranges (Day, Week, Month, Quarter, Year).\n\nPlease select a web property and date range below to get started. ")

with col2:
    # Display sign-in/sign-out options
    if st.session_state.credentials:
        st.write("You are currently signed in.")
        if st.button("Sign out"):
            st.session_state.auth_manager.save_cached_credentials(None)  # Clear the cached credentials

    else:
        st.warning("You are not signed in. Please click the button below to authenticate.")
        authorization_url = st.session_state.auth_manager.get_authorization_url()
        st.link_button("Sign in with Google", authorization_url, use_container_width=True)

# Load cached credentials
credentials = st.session_state.auth_manager.load_cached_credentials()

# Use cached credentials if available
if credentials:
    st.session_state.credentials = credentials
    service = st.session_state.auth_manager.get_service(credentials)
    if service:
        st.session_state.service = service

if st.session_state.credentials:
    st.session_state.account = st.session_state.auth_manager.load_wrapper_account()

    # Initialize session state for web property and web properties list
    if 'web_properties' not in st.session_state:
        web_properties_df = st.session_state.account.list_webproperties()
        st.session_state.web_properties = web_properties_df['siteUrl'].tolist()

    if 'web_property' not in st.session_state:
        st.session_state.web_property = st.session_state.web_properties[0] if st.session_state.web_properties else None

    # Initialize session state variables if they don't exist
    if 'form_web_property' not in st.session_state:
        st.session_state.form_web_property = st.session_state.web_properties[0] if st.session_state.web_properties else None
    if 'form_start_date' not in st.session_state:
        st.session_state.form_start_date = None
    if 'form_end_date' not in st.session_state:
        st.session_state.form_end_date = None
    if 'period' not in st.session_state:
        st.session_state.period = "DE"
    if 'grouped_report' not in st.session_state:
        st.session_state.grouped_report = None

    # Function to update session state
    def update_session_state():
        st.session_state.form_web_property = st.session_state.web_property_select
        st.session_state.form_start_date = st.session_state.start_date_input
        st.session_state.form_end_date = st.session_state.end_date_input
        st.session_state.period = st.session_state.period_select

    col1, col2 = st.columns([2, 2])
    # Replace the form with individual widgets
    with col1:
        st.selectbox("Choose a web property", 
                 st.session_state.web_properties, 
                 index=st.session_state.web_properties.index(st.session_state.form_web_property) if st.session_state.form_web_property in st.session_state.web_properties else 0,
                 key='web_property_select',
                 on_change=update_session_state)
        st.selectbox("Choose a period", ["Day", "Week", "Month", "Quarter", "Year"], key='period_select', on_change=update_session_state)


    with col2:
        st.date_input("Start date", key='start_date_input', on_change=update_session_state)
        st.date_input("End date", key='end_date_input', on_change=update_session_state)

    if st.button("Get Data"):
        st.session_state.grouped_report = load_grouped_data(st.session_state.account, 
                                                 st.session_state.form_web_property, 
                                                 st.session_state.form_start_date, 
                                                 st.session_state.form_end_date,
                                                 st.session_state.period)
        
    if st.session_state.grouped_report is not None:
        print(st.session_state.grouped_report)
        period_display = {"D": "Day", "W": "Week", "M": "Month", "Q": "Quarter", "Y": "Year"}
        period_column = st.session_state.grouped_report.columns[0]
        st.subheader(f"Data Grouped by {period_column}")
        st.dataframe(st.session_state.grouped_report, hide_index=True, use_container_width=True)
    
    else:
        st.info("No data has been loaded yet. Please select a web property and date range above to fetch data.")