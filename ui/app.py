import streamlit as st
from ui.components.ui_header import render_header
from ui.components.ui_footer import render_footer
from ui.layout_utils import render_main_layout

def main():
    st.set_page_config(page_title="CogOS Jarvis", layout="wide", page_icon="🧠")
    render_header()
    render_main_layout()
    render_footer()

if __name__ == "__main__":
    main()
