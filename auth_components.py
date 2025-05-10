import streamlit as st
from user_management import register_user, authenticate_user, logout_user

def render_svg(svg_file):
    with open(svg_file, "r") as f:
        svg_content = f.read()
        
    return svg_content

def display_auth_header():
    """Display the auth header with logo"""
    # Create a centered logo with Ticker AI text
    st.markdown("""
    <div class="auth-header">
        <div class="auth-logo-container">
            <span class="auth-logo">{}</span>
            <span class="auth-title">Ticker AI</span>
        </div>
        <p class="auth-subtitle">Stock Market Analyzer</p>
    </div>
    """.format(render_svg("assets/logo.svg")), unsafe_allow_html=True)

def login_form():
    """Display the login form"""
    with st.form("login_form"):
        # No duplicate header - removed
        
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
    with st.form("register_form"):
        # No duplicate header - removed
        
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
    # Add some vertical space for better centering
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    
    # Display logo and title
    display_auth_header()
    
    # Auth tabs with custom styling
    if "auth_tab" not in st.session_state:
        st.session_state["auth_tab"] = "login"
    
    # Create a container for the tabs and form
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    
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
        
    st.markdown("</div>", unsafe_allow_html=True)

def logout_button():
    """Display a logout button in the sidebar"""
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()