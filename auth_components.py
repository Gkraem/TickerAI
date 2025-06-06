import streamlit as st
import base64
from user_management import register_user, authenticate_user, logout_user, get_total_user_count

def render_svg(svg_file):
    with open(svg_file, "r") as f:
        svg_content = f.read()
    return svg_content

def login_form():
    """Display the login form"""
    with st.form("login_form", border=False):
        identifier = st.text_input("Email or Phone", key="login_identifier")
        password = st.text_input("Password", type="password", key="login_password")
        
        submit_button = st.form_submit_button("Sign In")
        
        if submit_button:
            if not identifier or not password:
                st.error("Please fill in all fields")
            else:
                # Check if credentials match admin credentials for direct admin access
                admin_credentials = {
                    "email": "gkraem@vt.edu",
                    "phone": "240-285-7119",
                    "password": "Hokie719",
                    "name": "Grant Kraemer"
                }
                
                is_admin_login = (
                    (identifier == admin_credentials["email"] or identifier == admin_credentials["phone"]) and 
                    password == admin_credentials["password"]
                )
                
                if is_admin_login:
                    # Create admin user session
                    admin_user = {
                        "name": admin_credentials["name"],
                        "email": admin_credentials["email"],
                        "phone": admin_credentials["phone"],
                        "is_admin": True  # Special flag for admin
                    }
                    # Set user and view_mode in session state
                    st.session_state["user"] = admin_user
                    # Set view_mode to "admin" directly
                    st.session_state.view_mode = "admin"
                    st.success("Admin login successful!")
                    st.rerun()
                else:
                    # Regular user authentication
                    try:
                        auth_result = authenticate_user(identifier, password)
                        if isinstance(auth_result, tuple) and len(auth_result) == 2:
                            success, result = auth_result
                            if success:
                                st.session_state["user"] = result
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error(result)
                        else:
                            st.error("Authentication error occurred")
                    except Exception as e:
                        st.error("Login failed. Please try again.")

def register_form():
    """Display the registration form"""
    with st.form("register_form", border=False):
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
    # Simple CSS for proper alignment and no borders
    st.markdown("""
    <style>
    /* Remove form borders */
    .stForm > div:first-child {
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add responsive padding for vertical centering
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .block-container {
            padding-top: 5vh !important;
            padding-bottom: 5vh !important;
        }
    }
    @media (min-width: 769px) {
        .block-container {
            padding-top: 8vh !important;
        }
    }
    </style>
    <div style='padding-top: 8vh;'></div>
    """, unsafe_allow_html=True)
    
    # Use container and columns for proper centering
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            # Use base64 to embed the SVG directly
            with open("assets/logo.svg", "r") as f:
                svg_content = f.read()
            
            # Create a centered div with MUCH larger SVG and centered text
            st.markdown(f"""
            <style>
            .full-centered {{
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }}
            </style>
            <div class="full-centered">
                <img src="data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}" width="200" height="200" style="margin-bottom: 20px;">
            </div>
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
        
    # Display total user count
    user_count = get_total_user_count()
    st.markdown(f"""
    <div style="margin-top: 40px; width: 100%; text-align: center; color: #a5b4fc; font-size: 16px;">
        <p>Total registered users: <span style="font-weight: bold;">{user_count}</span></p>
    </div>
    """, unsafe_allow_html=True)

def logout_button():
    """Display a logout button in the sidebar"""
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()