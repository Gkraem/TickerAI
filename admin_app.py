import streamlit as st
from user_management import is_authenticated, get_session_user, is_admin
from auth_components import auth_page, logout_button
from admin import admin_panel

# Set page configuration
st.set_page_config(
    page_title="Ticker AI Admin",
    page_icon="📈",
    layout="wide"
)

# Custom footer
footer_html = """
<div class="footer">
    <div class="footer-content">
        <div class="footer-left">
            Contact: 240-285-7119 | gkraem@vt.edu
        </div>
        <div class="footer-right">
            © 2025 Ticker AI. All rights reserved.
        </div>
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)

# Check if user is authenticated and is admin
if not is_authenticated():
    # Show authentication page when not logged in
    auth_page()
elif not is_admin():
    # Not an admin, show message
    st.error("You don't have permission to access the admin panel")
    st.markdown("Return to the [Ticker AI Stock Analyzer](/)")
else:
    # User is an admin, show admin panel
    user = get_session_user()
    
    # Header
    st.title("Ticker AI Admin Panel")
    st.markdown(f"Logged in as: **{user['name']}** ({user['email']})")
    
    # Add logout button
    if st.button("Logout"):
        st.session_state["user"] = None
        st.rerun()
    
    # Return to main app button
    if st.button("Return to Stock Analyzer"):
        st.switch_page("app.py")
    
    # Show admin panel
    admin_panel()