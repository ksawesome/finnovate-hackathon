"""Main Streamlit app."""

import streamlit as st

st.title("Trial Balance Analyzer")

# Placeholder UI
st.write("Upload trial balance CSV")
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file:
    st.write("File uploaded")

# Add more components later