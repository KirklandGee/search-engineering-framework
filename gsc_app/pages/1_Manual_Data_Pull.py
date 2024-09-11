import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from modules.data_processing import process_gsc_data, group_gsc_data

# Set page configuration
st.set_page_config(
    page_title="Manual Data Pull - SE Framework GSC API Tool",
    page_icon="📊",
    layout="wide"
)


sites_list = st.session_state.auth_manager.get_site_list(st.session_state.service) if 'service' in st.session_state else []
# Sort the sites list alphabetically
sites_list.sort()


if 'credentials' not in st.session_state:
    st.session_state.credentials = None

# Initialize the request state if it doesn't exist
if 'request' not in st.session_state:
    st.session_state.request = {
        "startDate": (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d"),
        "endDate": datetime.now().strftime("%Y-%m-%d"),
        "dimensions": ["page", "query"],
        "type": "web",
        "dimensionFilterGroups": [],
        "rowLimit": 100,
        "startRow": 0,
        "aggregationType": "byPage"
    }

if 'selected_site' not in st.session_state:
    st.session_state.selected_site = sites_list[0] if sites_list else None

col1, col2 = st.columns([3, 2])

with col1:
    st.title("Manual Data Pull")
    st.write("You can use this tool to manually access your own data from the Google Search Console API.\n\nYou can use the filters to refine your query and the dimensions to group your data.")


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






# If we have credentials, initialize the service
if st.session_state.credentials:
    service = st.session_state.auth_manager.get_service(st.session_state.credentials)
    if service:
        st.session_state.service = service
        st.session_state.auth_manager.save_cached_credentials(st.session_state.credentials)  # Cache the credentials

if 'service' in st.session_state and st.session_state.service:
    
    if sites_list:
        # Move the filter configuration above the main form
        with st.expander("Configure Filters", expanded=False):

            st.write("Set up filters for your GSC request")
            with st.form("filter_form"):
                filter_dimension = st.selectbox("Filter Dimension", 
                                                ["page", "query", "country", "device", "search_appearance"])
                filter_operator = st.selectbox("Filter Operator", ["contains", "equals", "notContains", "notEquals"])
                filter_expression = st.text_input("Filter Expression")
                
                filter_submitted = st.form_submit_button("Apply Filter")
            
            if filter_submitted:
                if filter_expression:
                    st.session_state.request["dimensionFilterGroups"] = [
                        {
                            "groupType": "and",
                            "filters": [
                                {
                                    "dimension": filter_dimension,
                                    "operator": filter_operator,
                                    "expression": filter_expression
                                }
                            ]
                        }
                    ]
                    st.success("Filter applied successfully!")
                else:
                    st.session_state.request["dimensionFilterGroups"] = []
                    st.info("Filter cleared.")
                        
        # Main form for GSC request
        with st.form("gsc_request_form"):
            if sites_list:
                selected_site = st.selectbox("Select a site:", sites_list, 
                                             key="site_selector")
            else:
                st.warning("No sites available. Please check your Google Search Console account.")
                selected_site = None
            
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input("Start Date", value=datetime.strptime(st.session_state.request["startDate"], "%Y-%m-%d"))
                data_type = st.selectbox("Search Appearance", ["web", "image", "video", "news", "discover"], index=["web", "image", "video", "news", "discover"].index(st.session_state.request["type"]))
            
            with col2:
                end_date = st.date_input("End Date", value=datetime.strptime(st.session_state.request["endDate"], "%Y-%m-%d"))
                dimensions = st.multiselect("Dimensions", 
                                            ["date", "query", "page", "country", "device", "search_appearance"],
                                            default=st.session_state.request["dimensions"])
            
            def on_submit():
                st.session_state.selected_site = st.session_state.site_selector

            submitted = st.form_submit_button("Fetch Data", on_click=on_submit)
            
        if submitted:
            # Update the request state
            st.session_state.request.update({
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
                "dimensions": dimensions,
                "type": data_type,
            })
            
            result = st.session_state.auth_manager.search_analytics_query(st.session_state.service, st.session_state.selected_site, st.session_state.request)
            result_daily = st.session_state.auth_manager.search_analytics_query_daily(st.session_state.service, st.session_state.selected_site, st.session_state.request)
            if result:
                df_display = process_gsc_data(result, st.session_state.request)
                df_grouped = group_gsc_data(df_display)
                if df_grouped is not None:
                    st.markdown("## Grouped by Page:")
                    st.dataframe(df_grouped, hide_index=True)
                if df_display is not None:
                    st.markdown("## All Data:")
                    st.dataframe(df_display, hide_index=True)

                else:
                    st.info("No data returned for the given query.")
            else:
                st.error("Failed to fetch data from Search Console.")

            if result_daily:
                df_display_daily = process_gsc_data(result_daily, st.session_state.request)
                st.markdown("## Daily Data:")
                st.dataframe(df_display_daily, hide_index=True)

            else:
                st.error("Failed to fetch daily data from Search Console.")