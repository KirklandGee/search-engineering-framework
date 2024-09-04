import streamlit as st
from modules.auth_manager import AuthManager
from datetime import datetime, timedelta
import os
import pickle
import pandas as pd


# Initialize AuthManager
auth_manager = AuthManager()

# Function to load cached credentials
def load_cached_credentials():
    cache_file = '.token_cache'
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    return None

# Function to save credentials to cache
def save_cached_credentials(credentials):
    cache_file = '.token_cache'
    with open(cache_file, 'wb') as f:
        pickle.dump(credentials, f)

# Load cached credentials
credentials = load_cached_credentials()


# Use cached credentials if available
if credentials:
    st.session_state.credentials = credentials
    service = auth_manager.get_service(credentials)
    if service:
        st.session_state.service = service


sites_list = auth_manager.get_site_list(st.session_state.service)
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
        "startRow": 0
    }

if 'selected_site' not in st.session_state:
    st.session_state.selected_site = sites_list[0] if sites_list else None


st.write(st.session_state)
st.title("The Search Engineering Framework: GSC API Tool")

st.write("You can use this tool to get data from the Google Search Console API.")

# Check if we're handling a redirect (i.e., if there's a 'code' in the URL)
if 'code' in st.query_params:
    if auth_manager.handle_redirect(st.query_params.get('code')):
        st.success("Successfully signed in!")
    # Clear the URL parameters to prevent reusing the same code
    st.query_params.clear()
    st.rerun()

# Display sign-in/sign-out options
if st.session_state.credentials:
    st.write("You are currently signed in.")
    if st.button("Sign out"):
        st.session_state.credentials = None
        st.session_state.service = None
        os.remove('.token_cache')  # Remove the cached token file
        st.experimental_rerun()
else:
    st.write("You are not signed in. Please click the button below to authenticate.")
    authorization_url = auth_manager.get_authorization_url()
    st.link_button("Sign in with Google", authorization_url, use_container_width=True)

# If we have credentials, initialize the service
if st.session_state.credentials:
    service = auth_manager.get_service(st.session_state.credentials)
    if service:
        st.session_state.service = service
        save_cached_credentials(st.session_state.credentials)  # Cache the credentials
        st.success("You're signed in! You can now use the Google Search Console API.")

# Here you can add more functionality that uses the authenticated service
if 'service' in st.session_state and st.session_state.service:
    st.write("You can now use the Google Search Console API.")
    
    
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
                
                st.write("Current filter:")
                st.json(st.session_state.request["dimensionFilterGroups"])
        
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
            
            # Here you would call the API with this request body
            result = auth_manager.search_analytics_query(st.session_state.service, st.session_state.selected_site, st.session_state.request)
            if result:
                # Process and display the data
                rows = result.get('rows', [])
                if rows:
                    # Create a DataFrame from the result
                    df = pd.DataFrame(rows)
                    # Rename columns based on dimensions
                    st.write("Search Console Data:")
                    # Split the keys into separate columns
                    keys = df['keys'].apply(pd.Series)
                    
                    # Rename columns based on dimensions
                    dimension_names = st.session_state.request['dimensions']
                    for i, dim in enumerate(dimension_names):
                        keys = keys.rename(columns={i: dim.capitalize()})
                    
                    # Combine the keys with the metrics
                    df_display = pd.concat([keys, df.drop('keys', axis=1)], axis=1)
                    
                    # Reorder columns to ensure URL and Query are first if present
                    cols = df_display.columns.tolist()
                    for col in ['Query', 'Page']:
                        if col in cols:
                            cols.remove(col)
                            cols.insert(0, col)
                    df_display = df_display[cols]

                    # Convert CTR to percentage and round to 2 decimal places
                    df_display['CTR'] = (df_display['ctr'] * 100).round(2)
                    
                    # Round average position to 2 decimal places
                    df_display['Average Position'] = df_display['position'].round(2)
                    
                    # Drop the original columns
                    df_display = df_display.drop(['ctr', 'position'], axis=1)
                    
                    # Reorder columns to put CTR and Average Position at the end
                    cols = df_display.columns.tolist()
                    cols = [col for col in cols if col not in ['CTR', 'Average Position']] + ['CTR', 'Average Position']
                    df_display = df_display[cols]
                    
                    if 'Page' in df_display.columns and 'Query' in df_display.columns:
                        if 'clicks' in df_display.columns:
                            # Sort the dataframe by clicks in descending order
                            df_display = df_display.sort_values('clicks', ascending=False)
                            
                            # Group by Page and aggregate the data
                            df_grouped = df_display.groupby('Page').agg({
                                'Query': lambda x: ', '.join(x.head(10)),  # Top 10 queries
                                'clicks': 'sum',
                                'impressions': 'sum',
                                'CTR': lambda x: f"{(x.astype(float).mean() * 100):.2f}%",  # Average CTR
                                'Average Position': 'mean'
                            }).reset_index()
                            
                            # Rename the Query column to indicate it shows top queries
                            df_grouped = df_grouped.rename(columns={'Query': 'Top 10 Queries'})
                            
                            st.write("Grouped Search Console Data by Page:")
                            st.dataframe(df_grouped, hide_index=True)
                        else:
                            st.write("Data not grouped: 'clicks' column is missing.")
                    else:
                        st.write("Data not grouped: 'Page' or 'Query' column missing.")

                    st.dataframe(df_display, hide_index=True)

                    # Create a simple bar chart of overall clicks and impressions
                    chart_data = pd.DataFrame({
                        'Metric': ['Clicks', 'Impressions'],
                        'Value': [df['clicks'].sum(), df['impressions'].sum()]
                    })
                    

                else:
                    st.info("No data returned for the given query.")
            else:
                st.error("Failed to fetch data from Search Console.")

