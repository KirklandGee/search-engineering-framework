import streamlit as st
import gscwrapper
from modules.gsc_stuff import GSCStuff

# Set page configuration
st.set_page_config(
    page_title="Functions - GSC API Tool",
    page_icon="🛠️",
    layout="wide"
)

gsc = GSCStuff()
account = gsc.load_account()


# Title
st.title("Functions")

# Introduction
st.write("This page demonstrates various functions available in the GSC API Tool.")

def load_data(web_property, start_date, end_date):
    webproperty = gsc.account[web_property]

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

    report = report.show_data()
    print(report)

    return report



# Initialize session state for web property and web properties list
if 'web_properties' not in st.session_state:
    web_properties_df = gsc.account.list_webproperties()
    st.session_state.web_properties = web_properties_df['siteUrl'].tolist()

if 'web_property' not in st.session_state:
    st.session_state.web_property = st.session_state.web_properties[0] if st.session_state.web_properties else None

print("web_property: ", st.session_state.web_property)
with st.form("get_data"):
    web_property = st.selectbox("Choose a web property", 
                                st.session_state.web_properties, 
                                index=st.session_state.web_properties.index(st.session_state.web_property) if st.session_state.web_property in st.session_state.web_properties else 0,
                                key='web_property_select')
    start_date = st.date_input("Start date")
    end_date = st.date_input("End date")
    get_data = st.form_submit_button("Get All Data")
if get_data:
    # Update session state
    st.session_state.web_property = web_property
    report = load_data(web_property, start_date, end_date)
    print(type(report))
    st.dataframe(report, 
                 hide_index=True)


# New 4-column grid for cannibalization report
col1, col2, col3, col4 = st.columns(4)

with col1.form("cannibalization_report"):
    st.write("## Cannibalization Report")
    keyword = st.text_input("Enter brand variants (comma-separated)")
    cannibalization_submit = st.form_submit_button("Generate Report")

with col2.form("ctr_yield"):
    st.write("## CTR Yield Curve")
    ctr_yield_submit = st.form_submit_button("Generate Report")

if cannibalization_submit:
    brand_variants = [variant.strip() for variant in keyword.split(',')]
    cannibalization_data = (
        account[st.session_state.web_property]
        .query
        .dimensions(["query","page"])
        .range(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        .get()
        .cannibalization(brand_variants=brand_variants)
    )
    st.subheader(f"Cannibalization Report")
    st.dataframe(cannibalization_data, hide_index=True, use_container_width=True)

if ctr_yield_submit:
    ctr_yield_data = (
        account[st.session_state.web_property]
        .query
        .dimensions(["query","date"])
        .range(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        .get()
        .ctr_yield_curve()
    )
    st.subheader(f"CTR Yield Curve")
    st.dataframe(ctr_yield_data, hide_index=True, use_container_width=True)



# Sidebar
st.sidebar.header("Function Navigation")
st.sidebar.info("Use this sidebar to navigate between different functions once they are implemented.")
