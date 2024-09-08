import streamlit as st
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="GSC API Tool",
    page_icon="🔍",
    layout="wide"
)


col1, col2 = st.columns([4, 2])
# Title and introduction

with col1:
    st.title("The Search Engineering Framework's GSC API Tool")
with col2:
    image = Image.open("images/kirkland.jpeg")
    st.image("images/kirkland.jpeg", caption="Kirkland Gee: The Search Engineering Framework")

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
