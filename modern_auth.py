"""
Modern Authentication Components for Ticker AI
Completely redesigned sign-in and create account interfaces
"""

import streamlit as st
import time
from user_management import authenticate_user, register_user, get_total_user_count


def load_modern_auth_css():
    """Load modern authentication-specific CSS"""
    st.markdown("""
    <style>
    /* Authentication Page Styles */
    .auth-page {
        min-height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem;
    }
    
    .auth-container {
        width: 100%;
        max-width: 420px;
        margin: 0 auto;
    }
    
    .auth-card {
        background: var(--bg-primary);
        border-radius: 1.5rem;
        padding: 3rem 2rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        border: 1px solid var(--border-color);
        backdrop-filter: blur(16px);
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .auth-logo {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .auth-logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1.5rem;
    }
    
    .auth-logo-text {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .auth-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .auth-subtitle {
        color: var(--text-secondary);
        font-size: 1rem;
        margin-bottom: 0;
    }
    
    .auth-form {
        margin-top: 2rem;
    }
    
    .auth-form-group {
        margin-bottom: 1.5rem;
    }
    
    .auth-form-label {
        display: block;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
    }
    
    .auth-divider {
        margin: 2rem 0;
        text-align: center;
        position: relative;
    }
    
    .auth-divider::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 1px;
        background: var(--border-color);
    }
    
    .auth-divider-text {
        background: var(--bg-primary);
        padding: 0 1rem;
        color: var(--text-muted);
        font-size: 0.875rem;
    }
    
    .auth-switch {
        text-align: center;
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border-color);
    }
    
    .auth-switch-text {
        color: var(--text-secondary);
        margin-bottom: 1rem;
    }
    
    .auth-stats {
        background: var(--bg-secondary);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .auth-stats-number {
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-primary);
        display: block;
    }
    
    .auth-stats-label {
        color: var(--text-secondary);
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
    
    .password-toggle {
        position: absolute;
        right: 0.75rem;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        color: var(--text-muted);
        cursor: pointer;
        padding: 0.25rem;
    }
    
    .password-field {
        position: relative;
    }
    
    /* Mobile responsive */
    @media (max-width: 480px) {
        .auth-card {
            padding: 2rem 1.5rem;
            border-radius: 1rem;
        }
        
        .auth-title {
            font-size: 1.5rem;
        }
        
        .auth-logo-text {
            font-size: 1.5rem;
        }
        
        .auth-logo-icon {
            width: 40px;
            height: 40px;
            font-size: 1.25rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def modern_login_form():
    """Modern redesigned login form"""
    st.markdown("""
    <div class="auth-page">
        <div class="auth-container">
            <div class="auth-card">
                <div class="auth-header">
                    <div class="auth-logo">
                        <div class="auth-logo-icon">T</div>
                        <span class="auth-logo-text">Ticker AI</span>
                    </div>
                    <h1 class="auth-title">Welcome Back</h1>
                    <p class="auth-subtitle">Sign in to access your investment insights</p>
                </div>
    """, unsafe_allow_html=True)
    
    # User statistics
    total_users = get_total_user_count()
    st.markdown(f"""
        <div class="auth-stats">
            <span class="auth-stats-number">{total_users}</span>
            <div class="auth-stats-label">Registered Users</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("modern_login_form", clear_on_submit=False):
        st.markdown('<div class="auth-form">', unsafe_allow_html=True)
        
        # Email/Phone field
        st.markdown('<div class="auth-form-group">', unsafe_allow_html=True)
        st.markdown('<label class="auth-form-label">Email or Phone</label>', unsafe_allow_html=True)
        email_or_phone = st.text_input(
            "",
            placeholder="Enter your email or phone number",
            key="modern_login_email_phone",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Password field
        st.markdown('<div class="auth-form-group">', unsafe_allow_html=True)
        st.markdown('<label class="auth-form-label">Password</label>', unsafe_allow_html=True)
        password = st.text_input(
            "",
            type="password",
            placeholder="Enter your password",
            key="modern_login_password",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Buttons
        col1, col2 = st.columns([3, 2])
        with col1:
            submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        with col2:
            forgot_password = st.form_submit_button("Forgot Password?", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle form submission
        if submit:
            if email_or_phone and password:
                # Check for admin credentials first
                admin_credentials = {
                    "email": "gkraem@vt.edu",
                    "phone": "240-285-7119",
                    "password": "Hokie719",
                    "name": "Grant Kraemer"
                }
                
                is_admin_login = (
                    (email_or_phone == admin_credentials["email"] or email_or_phone == admin_credentials["phone"]) and 
                    password == admin_credentials["password"]
                )
                
                if is_admin_login:
                    admin_user = {
                        "name": admin_credentials["name"],
                        "email": admin_credentials["email"],
                        "phone": admin_credentials["phone"],
                        "is_admin": True
                    }
                    st.session_state["user"] = admin_user
                    st.session_state.view_mode = "admin"
                    st.success("Admin login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    try:
                        auth_result = authenticate_user(email_or_phone, password)
                        if isinstance(auth_result, tuple) and len(auth_result) == 2:
                            success, result = auth_result
                            if success:
                                st.session_state["user"] = result
                                st.success("Login successful!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(result)
                        else:
                            st.error("Authentication error occurred")
                    except Exception as e:
                        st.error("Login failed. Please try again.")
            else:
                st.error("Please fill in all fields.")
        
        if forgot_password:
            st.info("📧 Please contact support at gkraem@vt.edu for password reset assistance.")
    
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def modern_register_form():
    """Modern redesigned registration form"""
    st.markdown("""
    <div class="auth-page">
        <div class="auth-container">
            <div class="auth-card">
                <div class="auth-header">
                    <div class="auth-logo">
                        <div class="auth-logo-icon">T</div>
                        <span class="auth-logo-text">Ticker AI</span>
                    </div>
                    <h1 class="auth-title">Create Account</h1>
                    <p class="auth-subtitle">Join thousands of investors using AI-powered analysis</p>
                </div>
    """, unsafe_allow_html=True)
    
    # User statistics
    total_users = get_total_user_count()
    st.markdown(f"""
        <div class="auth-stats">
            <span class="auth-stats-number">{total_users}</span>
            <div class="auth-stats-label">Registered Users</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("modern_register_form", clear_on_submit=True):
        st.markdown('<div class="auth-form">', unsafe_allow_html=True)
        
        # Full Name field
        st.markdown('<div class="auth-form-group">', unsafe_allow_html=True)
        st.markdown('<label class="auth-form-label">Full Name</label>', unsafe_allow_html=True)
        name = st.text_input(
            "",
            placeholder="Enter your full name",
            key="modern_register_name",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Email field
        st.markdown('<div class="auth-form-group">', unsafe_allow_html=True)
        st.markdown('<label class="auth-form-label">Email Address</label>', unsafe_allow_html=True)
        email = st.text_input(
            "",
            placeholder="Enter your email address",
            key="modern_register_email",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Phone field
        st.markdown('<div class="auth-form-group">', unsafe_allow_html=True)
        st.markdown('<label class="auth-form-label">Phone Number</label>', unsafe_allow_html=True)
        phone = st.text_input(
            "",
            placeholder="Enter your phone number",
            key="modern_register_phone",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Password field
        st.markdown('<div class="auth-form-group">', unsafe_allow_html=True)
        st.markdown('<label class="auth-form-label">Password</label>', unsafe_allow_html=True)
        password = st.text_input(
            "",
            type="password",
            placeholder="Create a secure password",
            key="modern_register_password",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Confirm Password field
        st.markdown('<div class="auth-form-group">', unsafe_allow_html=True)
        st.markdown('<label class="auth-form-label">Confirm Password</label>', unsafe_allow_html=True)
        confirm_password = st.text_input(
            "",
            type="password",
            placeholder="Confirm your password",
            key="modern_register_confirm_password",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit button
        submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle form submission
        if submit:
            if not all([name, email, phone, password, confirm_password]):
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                try:
                    result = register_user(name, email, phone, password)
                    if isinstance(result, tuple) and len(result) == 2:
                        success, message = result
                        if success:
                            st.success("Account created successfully! Please sign in.")
                            time.sleep(2)
                            st.session_state.auth_mode = "login"
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Registration failed. Please try again.")
                except Exception as e:
                    st.error("Registration failed. Please try again.")
    
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def modern_auth_page():
    """Modern authentication page with tabbed interface"""
    load_modern_auth_css()
    
    # Initialize auth mode
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    
    # Create tabs for login/register
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    
    with tab1:
        if st.session_state.auth_mode != "login":
            st.session_state.auth_mode = "login"
        modern_login_form()
        
        # Switch to register
        st.markdown("""
        <div class="auth-switch">
            <div class="auth-switch-text">Don't have an account?</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Create Account", key="switch_to_register", use_container_width=True):
            st.session_state.auth_mode = "register"
            st.rerun()
    
    with tab2:
        if st.session_state.auth_mode != "register":
            st.session_state.auth_mode = "register"
        modern_register_form()
        
        # Switch to login
        st.markdown("""
        <div class="auth-switch">
            <div class="auth-switch-text">Already have an account?</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Sign In", key="switch_to_login", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()


def modern_logout_button():
    """Modern logout button for the header"""
    if st.button("Sign Out", key="modern_logout", help="Sign out of your account"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Successfully signed out!")
        time.sleep(1)
        st.rerun()