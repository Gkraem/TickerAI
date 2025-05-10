import streamlit as st
from user_management import is_authenticated, get_session_user, is_admin
from auth_components import auth_page, logout_button
from admin import admin_panel

# Set page configuration
st.set_page_config(
    page_title="Ticker AI Admin",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for admin panel
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
.stMetric {
    background-color: rgba(28, 131, 225, 0.1);
    border-radius: 8px;
    padding: 10px;
    border: 1px solid rgba(28, 131, 225, 0.2);
}
.dataframe {
    font-size: 14px;
}
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: rgba(38, 39, 48, 0.8);
    color: #FAFAFA;
    text-align: center;
    padding: 10px 0;
    font-size: 14px;
    backdrop-filter: blur(10px);
}
.footer-content {
    display: flex;
    justify-content: space-between;
    padding: 0 20px;
}
.admin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.header-buttons {
    display: flex;
    gap: 10px;
}
</style>
""", unsafe_allow_html=True)

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
    
    if not user or not isinstance(user, dict):
        st.error("User session error. Please log in again.")
        st.button("Return to Login", on_click=lambda: st.switch_page("/app.py"))
        st.stop()
    
    # Create a modern header with buttons
    st.markdown(
        """
        <div class="admin-header">
            <h1>Ticker AI Admin Panel</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # User info and navigation buttons in columns
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**Logged in as:** {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
    
    with col2:
        # Return to main app button
        if st.button("Return to Stock Analyzer", use_container_width=True):
            st.switch_page("/app.py")
    
    # Add a separator
    st.markdown("<hr style='margin-top: 0; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    # Show admin panel content
    admin_panel()
    
    # Add logout button at bottom 
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # Centered logout button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Logout", type="primary", use_container_width=True):
            st.session_state["user"] = None
            st.switch_page("/app.py")