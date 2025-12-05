import streamlit as st

def colored_header(text, emoji=""):
    st.markdown(
        f"<h2 style='color: #d89ccc;'>{emoji} {text}</h2>",
        unsafe_allow_html=True
    )