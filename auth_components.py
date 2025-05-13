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
                else:
                    # Regular user authentication
                    success, result = authenticate_user(identifier, password)
                    if success:
                        st.session_state["user"] = result
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(result)

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
    """Main authentication page with tabs for login and registration using Intellectia.ai styling"""
    # Apply the same Intellectia.ai styling
    st.markdown("""
    <style>
    /* Base styling */
    body {
        background-color: #0f0f0f;
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header styling */
    .auth-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: #1a1a1a;
        border-radius: 8px;
        margin-bottom: 2rem;
    }
    
    .auth-header .logo {
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    /* Auth container styling */
    .auth-container {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 2rem;
        max-width: 450px;
        margin: 0 auto;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .auth-tabs {
        display: flex;
        border-bottom: 1px solid #333;
        margin-bottom: 2rem;
    }
    
    .auth-tab {
        padding: 0.75rem 1.5rem;
        cursor: pointer;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .auth-tab.active {
        border-bottom: 2px solid #007bff;
        color: #007bff;
    }
    
    /* Form styling */
    .stForm {
        margin-top: 1rem;
    }
    
    /* Remove Streamlit form styling */
    .stForm > div:first-child {
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
        padding: 0 !important;
    }
    
    /* Footer styling */
    .auth-footer {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.9rem;
        opacity: 0.6;
    }
    
    /* Button styling to match the main design */
    button[data-testid="baseButton-primary"] {
        background-color: #007bff !important;
        color: white !important;
        font-weight: 500 !important;
    }
    
    button[data-testid="baseButton-secondary"] {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Hide standard Streamlit elements */
    .stDeployButton, footer {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with logo
    st.markdown("""
    <div class="auth-header">
        <div class="logo">Ticker AI</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auth tabs
    if "auth_tab" not in st.session_state:
        st.session_state["auth_tab"] = "login"
    
    # Styled auth container
    st.markdown("""
    <div class="auth-container">
        <h2 style="margin-top: 0; margin-bottom: 1.5rem; text-align: center;">Access Your Account</h2>
        <div class="auth-tabs">
            <div class="auth-tab" id="login-tab">Sign In</div>
            <div class="auth-tab" id="register-tab">Create Account</div>
        </div>
        <div id="auth-content"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Styled tabs that interface with Streamlit buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Sign In", key="tab_signin", use_container_width=True, 
                    type="primary" if st.session_state["auth_tab"] == "login" else "secondary"):
            st.session_state["auth_tab"] = "login"
            st.rerun()
    
    with col2:
        if st.button("Create Account", key="tab_register", use_container_width=True,
                    type="primary" if st.session_state["auth_tab"] == "register" else "secondary"):
            st.session_state["auth_tab"] = "register"
            st.rerun()
    
    # Hide the tab buttons and style the tabs based on the active state
    st.markdown(f"""
    <style>
    .stHorizontalBlock {{
        display: none !important;
    }}
    
    #login-tab {{
        border-bottom: 2px solid {("#007bff" if st.session_state["auth_tab"] == "login" else "transparent")};
        color: {("#007bff" if st.session_state["auth_tab"] == "login" else "inherit")};
    }}
    
    #register-tab {{
        border-bottom: 2px solid {("#007bff" if st.session_state["auth_tab"] == "register" else "transparent")};
        color: {("#007bff" if st.session_state["auth_tab"] == "register" else "inherit")};
    }}
    </style>
    
    <script>
    // Add click handlers to tabs
    document.getElementById('login-tab').addEventListener('click', function() {{
        document.querySelector('button[kind="primary"]').click();
    }});
    
    document.getElementById('register-tab').addEventListener('click', function() {{
        document.querySelector('button[kind="secondary"]').click();
    }});
    </script>
    """, unsafe_allow_html=True)
    
    # Show the active tab
    if st.session_state["auth_tab"] == "login":
        login_form()
    else:
        register_form()
        
    # Display total user count in footer
    user_count = get_total_user_count()
    st.markdown(f"""
    <div class="auth-footer">
        <p>Join our community of {user_count} investors making smarter decisions with AI</p>
    </div>
    """, unsafe_allow_html=True)

def logout_button():
    """Display a logout button in the sidebar"""
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()