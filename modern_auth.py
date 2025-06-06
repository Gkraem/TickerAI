"""
Modern Authentication Components - Complete UI Redesign
Clean, responsive authentication interface that connects to existing backend
"""

import streamlit as st
from user_management import register_user, authenticate_user, get_total_user_count

def load_modern_css():
    """Load the modern CSS framework"""
    with open('assets/modern_styles.css', 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def render_modern_header(is_authenticated=False, user_data=None):
    """Render modern header with theme toggle and authentication state"""
    
    # Initialize theme in session state
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Simple header without complex JavaScript
    st.markdown(f"""
    <div style="
        position: fixed; 
        top: 0; 
        left: 0; 
        right: 0; 
        z-index: 1000; 
        background: white; 
        border-bottom: 1px solid #e2e8f0; 
        padding: 0.75rem 0;
        backdrop-filter: blur(10px);
    ">
        <div style="
            max-width: 1200px; 
            margin: 0 auto; 
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
            padding: 0 1.5rem;
        ">
            <div style="
                display: flex; 
                align-items: center; 
                gap: 0.75rem; 
                font-size: 1.5rem; 
                font-weight: 700; 
                color: #1e293b;
            ">
                <span>📈</span>
                <span>TICKER AI</span>
            </div>
            
            <div style="
                display: flex; 
                align-items: center; 
                gap: 1rem;
            ">
                {"" if not is_authenticated else f'''
                <span style="color: #64748b; margin-right: 1rem;">Welcome, {user_data.get('name', 'User') if user_data else 'User'}</span>
                '''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_theme_icon():
    """Get appropriate theme toggle icon"""
    if st.session_state.get('theme', 'light') == 'light':
        return '🌙'
    return '☀️'

def render_hero_section():
    """Render modern hero section"""
    total_users = get_total_user_count()
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
        color: white;
        padding: 4rem 2rem;
        text-align: center;
        margin-top: 4rem;
    ">
        <div style="max-width: 800px; margin: 0 auto;">
            <h1 style="
                font-size: 3.5rem;
                font-weight: 800;
                margin-bottom: 1.5rem;
                background: linear-gradient(to right, #ffffff, #e0e7ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">TICKER AI</h1>
            <p style="
                font-size: 1.25rem;
                opacity: 0.9;
                margin-bottom: 2rem;
                line-height: 1.7;
            ">
                Advanced AI-powered investment platform delivering comprehensive stock analysis, 
                real-time market insights, and intelligent investment recommendations.
            </p>
            <div style="margin-top: 3rem; opacity: 0.8;">
                <p>Join {total_users:,} investors already using Ticker AI</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_modern_login():
    """Render modern login form"""
    st.markdown("""
    <div style="
        margin-top: 6rem;
        padding: 2rem;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        max-width: 400px;
        margin-left: auto;
        margin-right: auto;
    ">
        <h2 style="text-align: center; margin-bottom: 2rem; color: #1e293b;">
            Sign In to Ticker AI
        </h2>
    """, unsafe_allow_html=True)
    
    # Login form using Streamlit components
    with st.form("modern_login_form", clear_on_submit=False):
        email_or_phone = st.text_input(
            "Email or Phone", 
            placeholder="Enter your email or phone number",
            key="login_email_phone"
        )
        
        password = st.text_input(
            "Password", 
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            login_submitted = st.form_submit_button("Sign In", use_container_width=True)
        with col2:
            if st.form_submit_button("Create Account", use_container_width=True):
                st.session_state.auth_page = "register"
                st.rerun()
    
    if login_submitted:
        if email_or_phone and password:
            user_data = authenticate_user(email_or_phone, password)
            if user_data:
                st.session_state.user = user_data
                st.session_state.authenticated = True
                st.session_state.auth_page = None
                st.success("Successfully signed in!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
        else:
            st.error("Please fill in all fields.")
    
    # Stats section
    total_users = get_total_user_count()
    st.markdown(f"""
        <div style="text-align: center; margin-top: 2rem; color: #64748b;">
            <p>{total_users:,} investors trust Ticker AI</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_modern_register():
    """Render modern registration form"""
    st.markdown("""
    <div style="
        margin-top: 6rem;
        padding: 2rem;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        max-width: 400px;
        margin-left: auto;
        margin-right: auto;
    ">
        <h2 style="text-align: center; margin-bottom: 2rem; color: #1e293b;">
            Join Ticker AI
        </h2>
    """, unsafe_allow_html=True)
    
    # Registration form using Streamlit components
    with st.form("modern_register_form", clear_on_submit=False):
        name = st.text_input(
            "Full Name", 
            placeholder="Enter your full name",
            key="register_name"
        )
        
        email = st.text_input(
            "Email Address", 
            placeholder="Enter your email address",
            key="register_email"
        )
        
        phone = st.text_input(
            "Phone Number", 
            placeholder="Enter your phone number",
            key="register_phone"
        )
        
        password = st.text_input(
            "Password", 
            type="password",
            placeholder="Create a secure password",
            key="register_password"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            register_submitted = st.form_submit_button("Create Account", use_container_width=True)
        with col2:
            if st.form_submit_button("Sign In Instead", use_container_width=True):
                st.session_state.auth_page = "login"
                st.rerun()
    
    if register_submitted:
        if name and email and phone and password:
            try:
                success, message = register_user(name, email, phone, password)
                if success:
                    st.success("Account created successfully! Please sign in.")
                    st.session_state.auth_page = "login"
                    st.rerun()
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"Registration failed: {str(e)}")
        else:
            st.error("Please fill in all fields.")
    
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #64748b;">
            <p>Join thousands of investors making smarter decisions</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_features_section():
    """Render modern features section"""
    st.markdown("""
    <div style="padding: 4rem 2rem; background: #f8fafc;">
        <div style="max-width: 1200px; margin: 0 auto; text-align: center;">
            <h2 style="font-size: 2.5rem; font-weight: 700; color: #1e293b; margin-bottom: 1rem;">
                Powerful Investment Tools
            </h2>
            <p style="font-size: 1.125rem; color: #64748b; max-width: 600px; margin: 0 auto 3rem auto;">
                Everything you need to make informed investment decisions in one platform
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards using Streamlit columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 1rem;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        ">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
            <h3 style="font-size: 1.25rem; font-weight: 600; color: #1e293b; margin-bottom: 0.75rem;">Stock Analyzer</h3>
            <p style="color: #64748b; line-height: 1.6;">
                Get comprehensive analysis of any stock with AI-powered buy ratings and technical indicators.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 1rem;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        ">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🚀</div>
            <h3 style="font-size: 1.25rem; font-weight: 600; color: #1e293b; margin-bottom: 0.75rem;">Power Plays</h3>
            <p style="color: #64748b; line-height: 1.6;">
                Discover top investment opportunities from major indices like Fortune 500 and S&P 500.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 1rem;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        ">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🧠</div>
            <h3 style="font-size: 1.25rem; font-weight: 600; color: #1e293b; margin-bottom: 0.75rem;">AI Insights</h3>
            <p style="color: #64748b; line-height: 1.6;">
                Advanced algorithms analyze market trends and patterns to provide intelligent recommendations.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 1rem;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        ">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📈</div>
            <h3 style="font-size: 1.25rem; font-weight: 600; color: #1e293b; margin-bottom: 0.75rem;">Real-time Data</h3>
            <p style="color: #64748b; line-height: 1.6;">
                Access live market data and financial metrics from trusted financial data providers.
            </p>
        </div>
        """, unsafe_allow_html=True)

def handle_auth_navigation():
    """Handle authentication page navigation"""
    # Initialize session state
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Check for logout
    if st.session_state.get('auth_action') == 'logout':
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.auth_page = None
        st.session_state.auth_action = None
        st.rerun()
    
    # Check for authentication page requests
    if st.session_state.get('auth_action') == 'show_login':
        st.session_state.auth_page = "login"
        st.session_state.auth_action = None
        st.rerun()
    
    if st.session_state.get('auth_action') == 'show_register':
        st.session_state.auth_page = "register"
        st.session_state.auth_action = None
        st.rerun()

def render_modern_auth_page():
    """Main authentication page renderer"""
    load_modern_css()
    handle_auth_navigation()
    
    # Render appropriate page
    if st.session_state.auth_page == "login":
        render_modern_header(is_authenticated=False)
        render_modern_login()
    elif st.session_state.auth_page == "register":
        render_modern_header(is_authenticated=False)
        render_modern_register()
    else:
        # Default landing page
        render_modern_header(is_authenticated=False)
        render_hero_section()
        render_features_section()