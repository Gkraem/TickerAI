"""
Ticker AI - Modern Application Entry Point
Complete UI redesign with clean, responsive interface
"""

import streamlit as st
from modern_auth import render_modern_auth_page
from modern_app import render_modern_main_app
from user_management import is_authenticated, logout_user

# Page configuration
st.set_page_config(
    page_title="Ticker AI - AI-Powered Investment Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    """Main application entry point"""
    
    # Handle logout action
    if st.session_state.get('auth_action') == 'logout':
        logout_user()
        st.session_state.auth_action = None
        st.rerun()
    
    # Route to appropriate interface
    if is_authenticated():
        # Show main application for authenticated users
        render_modern_main_app()
    else:
        # Show authentication interface for non-authenticated users
        render_modern_auth_page()

if __name__ == "__main__":
    main()