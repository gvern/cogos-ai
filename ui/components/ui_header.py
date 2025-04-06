import streamlit as st
import datetime

def render_header():
    st.markdown("""
<style>
/* Fond et police */
body, .stApp {
    background-color: #0b0c10;
    color: #66fcf1;
    font-family: 'Fira Code', monospace;
}
/* Header */
.header-title {
    font-size: 32px;
    color: #45a29e;
    margin-bottom: 5px;
}
</style>
<div class='header-title'>🧠 CogOS // Mode JARVIS Activé</div>
""", unsafe_allow_html=True)
