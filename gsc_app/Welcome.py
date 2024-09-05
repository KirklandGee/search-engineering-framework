import streamlit as st
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Welcome to GSC API Tool",
    page_icon="🔍",
    layout="wide"
)

# Title and introduction
st.title("Welcome to The Search Engineering Framework: GSC API Tool")

st.markdown("""
This tool allows you to access and analyze your data from the Google Search Console API.

### Key Features:
- Authenticate with your Google account
- Select from your available sites
- Fetch and visualize search performance data
- Apply custom filters to your queries
- View data grouped by page or in detailed format
""")

# Add an image (you may need to replace this with an actual image path)
try:
    image = Image.open("path_to_your_image.png")
    st.image(image, caption="GSC API Tool Dashboard", use_column_width=True)
except FileNotFoundError:
    st.info("Add an image to make your welcome page more visually appealing!")

# Instructions
st.header("Getting Started")
st.markdown("""
1. Click on "Manual Data Pull" in the sidebar to begin.
2. Sign in with your Google account when prompted.
3. Select your desired site from the dropdown menu.
4. Set your date range and choose the dimensions you want to analyze.
5. Apply filters if needed to refine your data.
6. Click "Fetch Data" to retrieve and visualize your search console data.
""")

# Additional information
st.header("Need Help?")
st.markdown("""
If you encounter any issues or have questions about using this tool, please contact our support team or refer to the documentation.

Happy analyzing!
""")
