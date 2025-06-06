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
    
    header_html = f"""
    <div class="modern-header" data-theme="{st.session_state.theme}">
        <div class="header-container">
            <a href="#" class="header-logo" onclick="scrollToSection('hero')">
                <span>📈</span>
                <span>TICKER AI</span>
            </a>
            
            <nav class="header-nav">
                <ul class="nav-links">
                    {"" if not is_authenticated else '''
                    <li><a href="#" class="nav-link" onclick="scrollToSection('analyzer')">Stock Analyzer</a></li>
                    <li><a href="#" class="nav-link" onclick="scrollToSection('power-plays')">Power Plays</a></li>
                    <li><a href="#" class="nav-link" onclick="scrollToSection('about')">About</a></li>
                    '''}
                </ul>
                
                <div class="header-actions">
                    <button class="theme-toggle" onclick="toggleTheme()">
                        {get_theme_icon()}
                    </button>
                    
                    <div class="auth-buttons">
                        {"" if not is_authenticated else f'''
                        <span style="color: var(--text-secondary); margin-right: 1rem;">Welcome, {user_data.get('name', 'User') if user_data else 'User'}</span>
                        <button class="btn-secondary" onclick="logout()">Sign Out</button>
                        '''}
                        {"" if is_authenticated else '''
                        <button class="btn-secondary" onclick="showLogin()">Sign In</button>
                        <button class="btn-primary" onclick="showRegister()">Get Started</button>
                        '''}
                    </div>
                </div>
            </nav>
        </div>
    </div>
    
    <script>
        function toggleTheme() {{
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            
            // Update Streamlit session state
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: newTheme
            }}, '*');
        }}
        
        function scrollToSection(sectionId) {{
            document.getElementById(sectionId)?.scrollIntoView({{ behavior: 'smooth' }});
        }}
        
        function showLogin() {{
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: 'show_login'
            }}, '*');
        }}
        
        function showRegister() {{
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: 'show_register'
            }}, '*');
        }}
        
        function logout() {{
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: 'logout'
            }}, '*');
        }}
    </script>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

def get_theme_icon():
    """Get appropriate theme toggle icon"""
    if st.session_state.get('theme', 'light') == 'light':
        return '🌙'
    return '☀️'

def render_hero_section():
    """Render modern hero section"""
    total_users = get_total_user_count()
    
    hero_html = f"""
    <div id="hero" class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">TICKER AI</h1>
            <p class="hero-subtitle">
                Advanced AI-powered investment platform delivering comprehensive stock analysis, 
                real-time market insights, and intelligent investment recommendations.
            </p>
            <div class="hero-cta">
                <button class="btn-hero" onclick="showRegister()">Start Analyzing</button>
                <button class="btn-hero" onclick="scrollToSection('about')">Learn More</button>
            </div>
            <div style="margin-top: 3rem; opacity: 0.8;">
                <p>Join {total_users:,} investors already using Ticker AI</p>
            </div>
        </div>
    </div>
    """
    
    st.markdown(hero_html, unsafe_allow_html=True)

def render_modern_login():
    """Render modern login form"""
    st.markdown("""
    <div class="main-container">
        <div class="content-section">
            <div class="section-container">
                <div style="max-width: 400px; margin: 2rem auto;">
                    <div class="modern-form">
                        <h2 style="text-align: center; margin-bottom: 2rem; color: var(--text-primary);">
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
                        <div style="text-align: center; margin-top: 2rem; color: var(--text-muted);">
                            <p>{total_users:,} investors trust Ticker AI</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_modern_register():
    """Render modern registration form"""
    st.markdown("""
    <div class="main-container">
        <div class="content-section">
            <div class="section-container">
                <div style="max-width: 400px; margin: 2rem auto;">
                    <div class="modern-form">
                        <h2 style="text-align: center; margin-bottom: 2rem; color: var(--text-primary);">
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
                        <div style="text-align: center; margin-top: 2rem; color: var(--text-muted);">
                            <p>Join thousands of investors making smarter decisions</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_features_section():
    """Render modern features section"""
    features_html = """
    <div id="features" class="content-section">
        <div class="section-container">
            <div class="section-header">
                <h2 class="section-title">Powerful Investment Tools</h2>
                <p class="section-subtitle">
                    Everything you need to make informed investment decisions in one platform
                </p>
            </div>
            
            <div class="card-grid">
                <div class="modern-card">
                    <div class="card-icon">📊</div>
                    <h3 class="card-title">Stock Analyzer</h3>
                    <p class="card-description">
                        Get comprehensive analysis of any stock with AI-powered buy ratings, 
                        technical indicators, and fundamental metrics.
                    </p>
                </div>
                
                <div class="modern-card">
                    <div class="card-icon">🚀</div>
                    <h3 class="card-title">Power Plays</h3>
                    <p class="card-description">
                        Discover top investment opportunities from major indices like 
                        Fortune 500, S&P 500, and NASDAQ 100.
                    </p>
                </div>
                
                <div class="modern-card">
                    <div class="card-icon">🧠</div>
                    <h3 class="card-title">AI Insights</h3>
                    <p class="card-description">
                        Advanced machine learning algorithms analyze market trends, 
                        sentiment, and patterns to provide intelligent recommendations.
                    </p>
                </div>
                
                <div class="modern-card">
                    <div class="card-icon">📈</div>
                    <h3 class="card-title">Real-time Data</h3>
                    <p class="card-description">
                        Access live market data, earnings information, and financial 
                        metrics from trusted financial data providers.
                    </p>
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(features_html, unsafe_allow_html=True)

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