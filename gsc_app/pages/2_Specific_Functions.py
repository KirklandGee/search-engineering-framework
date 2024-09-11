import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Specific Functions - SE Framework GSC API Tool",
    page_icon="🛠️",
    layout="wide"
)

col1, col2 = st.columns([3, 2])

with col1:
    st.title("Specific Functions")
    st.markdown("This page allows you to run various functions from [Antione Epert's gscwrapper package](https://github.com/antoineeripret/gsc_wrapper/tree/master) on your GSC data.\n\nPlease select a web property and date range below to get started. ")

with col2:
    # Display sign-in/sign-out options
    if st.session_state.credentials:
        st.write("You are currently signed in.")
        if st.button("Sign out"):
            st.session_state.credentials = None
            st.session_state.service = None
            st.session_state.auth_manager.save_cached_credentials(None)  # Clear the cached credentials
            st.experimental_rerun()

    else:
        st.write("You are not signed in. Please click the button below to authenticate.")
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


def load_data(account, web_property, start_date, end_date):
    webproperty = account[web_property]

    # Convert date objects to string format
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    report = (
        webproperty
        .query
        .range(start_date_str, end_date_str)
        .dimensions(["page","query","date"])
        .get()
    )

    return report



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
    if 'main_report' not in st.session_state:
        st.session_state.main_report = None

    # Function to update session state
    def update_session_state():
        st.session_state.form_web_property = st.session_state.web_property_select
        st.session_state.form_start_date = st.session_state.start_date_input
        st.session_state.form_end_date = st.session_state.end_date_input

    # Replace the form with individual widgets
    st.selectbox("Choose a web property", 
                 st.session_state.web_properties, 
                 index=st.session_state.web_properties.index(st.session_state.form_web_property) if st.session_state.form_web_property in st.session_state.web_properties else 0,
                 key='web_property_select',
                 on_change=update_session_state)

    st.date_input("Start date", key='start_date_input', on_change=update_session_state)
    st.date_input("End date", key='end_date_input', on_change=update_session_state)

    if st.button("Get All Data"):
        st.session_state.main_report = load_data(st.session_state.account, 
                                                 st.session_state.form_web_property, 
                                                 st.session_state.form_start_date, 
                                                 st.session_state.form_end_date)

    # Check if main_report exists and is not None before using it
    if st.session_state.main_report is not None:
        st.subheader("Main Data Report")
        st.dataframe(st.session_state.main_report.show_data(), hide_index=True)
    
    else:
        st.info("No data has been loaded yet. Please select a web property and date range above to fetch data.")


    # New 4-column grid for cannibalization report
    col1, col2, col3 = st.columns(3)

    with col1.form("cannibalization_report"):
        st.write("## Cannibalization Report")
        keyword = st.text_input("Enter brand variants (comma-separated)")
        cannibalization_submit = st.form_submit_button("Generate Report")

    if cannibalization_submit:
        if st.session_state.form_web_property and st.session_state.form_start_date and st.session_state.form_end_date:
            brand_variants = [variant.strip() for variant in keyword.split(',')]
            st.session_state.cannibalization_data = (
                st.session_state.account[st.session_state.form_web_property]
                .query
                .dimensions(["query","page"])
                .range(st.session_state.form_start_date.strftime('%Y-%m-%d'), st.session_state.form_end_date.strftime('%Y-%m-%d'))
                .get()
                .cannibalization(brand_variants=brand_variants)
            )
        else:
            st.error("Please select a web property and date range first.")

    with col2.form("ctr_yield"):
        st.write("## CTR Yield Curve")
        ctr_yield_submit = st.form_submit_button("Generate Report")

    with col3.form("pages_to_kill"):
        st.write("## Find Pages to Kill")
        st.write("Identify pages that are below your chosen threshold for clicks and impressions. This can help you decide which pages to cut or improve.")
        sitemap = st.text_input("Enter the sitemap URL")
        clicks_threshold = st.number_input("Enter the clicks threshold", value=0)
        impressions_threshold = st.number_input("Enter the impressions threshold", value=0)
        pages_to_kill_submit = st.form_submit_button("Generate Report")

    # Initialize session state variables
    if 'cannibalization_data' not in st.session_state:
        st.session_state.cannibalization_data = None
    if 'ctr_yield_data' not in st.session_state:
        st.session_state.ctr_yield_data = None
    if 'pages_to_kill_data' not in st.session_state:
        st.session_state.pages_to_kill_data = None

    # Cannibalization Report
    if st.session_state.cannibalization_data is not None:
        st.subheader("Cannibalization Report")
        st.dataframe(st.session_state.cannibalization_data, hide_index=True, use_container_width=True)

    # CTR Yield Curve
    if ctr_yield_submit:
        if st.session_state.form_web_property and st.session_state.form_start_date and st.session_state.form_end_date:
            st.session_state.ctr_yield_data = (
                st.session_state.account[st.session_state.form_web_property]
                .query
                .dimensions(["query","date"])
                .range(st.session_state.form_start_date.strftime('%Y-%m-%d'), st.session_state.form_end_date.strftime('%Y-%m-%d'))
                .get()
                    .ctr_yield_curve()
                )
        else:
            st.error("Please select a web property and date range first.")

    if st.session_state.ctr_yield_data is not None:
        st.subheader("CTR Yield Curve")
        st.dataframe(st.session_state.ctr_yield_data, hide_index=True, use_container_width=True)

    # Pages to Kill
    if pages_to_kill_submit:
        if st.session_state.form_web_property and st.session_state.form_start_date and st.session_state.form_end_date:
            st.session_state.pages_to_kill_data = (
                st.session_state.account[st.session_state.form_web_property]
                .query
                .dimensions(["page"])
                .range(st.session_state.form_start_date.strftime('%Y-%m-%d'), st.session_state.form_end_date.strftime('%Y-%m-%d'))
                .get()
                .find_potential_contents_to_kill(
                    sitemap,
                    clicks_threshold,
                    impressions_threshold
            )
            )
        else:
            st.error("Please select a web property and date range first.")
    
    if st.session_state.pages_to_kill_data is not None:
        st.subheader("Pages to Kill")
        st.dataframe(st.session_state.pages_to_kill_data, hide_index=True, use_container_width=True)

    # Sidebar
    st.sidebar.header("Function Navigation")
    st.sidebar.info("Use this sidebar to navigate between different functions once they are implemented.")

