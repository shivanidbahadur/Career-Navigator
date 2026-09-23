import streamlit as st
from learning.auth import require_login, show_user_sidebar

require_login()
show_user_sidebar()

st.title("AI Career Navigator")
st.write("Welcome! Use the sidebar to open a page.")