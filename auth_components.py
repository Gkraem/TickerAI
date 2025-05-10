import streamlit as st
from user_management import register_user, authenticate_user, logout_user

def render_svg(svg_file):
    with open(svg_file, "r") as f:
        svg_content = f.read()
    return svg_content

def login_form():
    """Display the login form"""
    # Add extra CSS for compact form fields
    st.markdown("""
    <style>
    /* Reduce space between form items */
    .stTextInput label {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("login_form", border=False, clear_on_submit=False):
        identifier = st.text_input("Email or Phone", key="login_identifier")
        password = st.text_input("Password", type="password", key="login_password")
        
        submit_button = st.form_submit_button("Sign In")
        
        if submit_button:
            if not identifier or not password:
                st.error("Please fill in all fields")
            else:
                success, result = authenticate_user(identifier, password)
                if success:
                    st.session_state["user"] = result
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(result)

def register_form():
    """Display the registration form"""
    # Add same compact styling as login form
    st.markdown("""
    <style>
    /* Reduce space between form items */
    .stTextInput label {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("register_form", border=False, clear_on_submit=False):
        # More compact form with reduced spacing
        name = st.text_input("Full Name", key="register_name")
        email = st.text_input("Email", key="register_email")
        phone = st.text_input("Phone Number", key="register_phone")
        password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
        
        submit_button = st.form_submit_button("Create Account")
        
        if submit_button:
            if not name or not email or not phone or not password or not confirm_password:
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = register_user(name, email, phone, password)
                if success:
                    st.success(message)
                    # Set active tab to login after successful registration
                    st.session_state["auth_tab"] = "login"
                    st.rerun()
                else:
                    st.error(message)

def auth_page():
    """Main authentication page with tabs for login and registration"""
    # Add CSS for compact layout with no scrolling
    st.markdown("""
    <style>
    /* Compact vertical layout */
    div[data-testid="stVerticalBlock"] {
        display: flex;
        flex-direction: column;
        justify-content: center;
        max-height: 90vh;
        padding: 0;
        margin: 0;
    }
    
    /* Remove form borders */
    .stForm > div:first-child {
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }
    
    /* Make form more compact */
    .stTextInput {
        margin-bottom: 0 !important;
    }
    
    /* Reduce vertical spacing */
    .element-container {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Single branding with logo only
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px; margin-top: -30px;">
            <div style="width: 40px; height: 40px;">
                {render_svg("assets/logo.svg")}
            </div>
        </div>
        <p style="text-align: center; color: #a5b4fc; margin-bottom: 10px; font-size: 16px;">Stock Market Analyzer</p>
        """, unsafe_allow_html=True)
    
    # Auth tabs
    if "auth_tab" not in st.session_state:
        st.session_state["auth_tab"] = "login"
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Sign In", key="tab_signin", use_container_width=True, 
                    type="secondary" if st.session_state["auth_tab"] == "register" else "primary"):
            st.session_state["auth_tab"] = "login"
            st.rerun()
    
    with col2:
        if st.button("Create Account", key="tab_register", use_container_width=True,
                    type="secondary" if st.session_state["auth_tab"] == "login" else "primary"):
            st.session_state["auth_tab"] = "register"
            st.rerun()
    
    # Show the active tab
    if st.session_state["auth_tab"] == "login":
        login_form()
    else:
        register_form()

def logout_button():
    """Display a logout button in the sidebar"""
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()