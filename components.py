"""
Modern UI Components for Ticker AI
"""
import streamlit as st

def render_navigation_header():
    """Render modern navigation header with theme toggle"""
    
    # Initialize theme in session state if not exists
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Navigation header HTML
    nav_html = f"""
    <div class="nav-header">
        <div class="nav-logo">
            <span>📊</span>
            <span style="margin-left: 0.5rem;">TICKER AI</span>
        </div>
        
        <div class="nav-menu" id="navMenu">
            <a href="#stock-analyzer" class="nav-link">Stock Analyzer</a>
            <a href="#power-plays" class="nav-link">Power Plays</a>
            <a href="#about" class="nav-link">About</a>
            
            <div class="theme-toggle" onclick="toggleTheme()">
                <div class="theme-toggle-slider"></div>
            </div>
        </div>
        
        <button class="mobile-nav-toggle" onclick="toggleMobileNav()">
            ☰
        </button>
    </div>
    
    <script>
        // Theme toggle functionality
        function toggleTheme() {{
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update Streamlit session state
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: newTheme
            }}, '*');
        }}
        
        // Mobile navigation toggle
        function toggleMobileNav() {{
            const navMenu = document.getElementById('navMenu');
            navMenu.classList.toggle('open');
        }}
        
        // Initialize theme from localStorage
        (function() {{
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        }})();
        
        // Smooth scrolling for navigation links
        document.querySelectorAll('.nav-link').forEach(link => {{
            link.addEventListener('click', function(e) {{
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                if (targetElement) {{
                    targetElement.scrollIntoView({{ behavior: 'smooth' }});
                }}
            }});
        }});
    </script>
    """
    
    st.html(nav_html)

def render_hero_section():
    """Render modern hero section"""
    hero_html = """
    <div class="hero-section" style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 6rem 2rem;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
        border-radius: 0 0 2rem 2rem;
    ">
        <h1 style="
            font-size: 3.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">TICKER AI</h1>
        <p style="
            font-size: 1.25rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        ">Advanced AI-powered investment platform delivering intelligent stock analysis and strategic trading insights</p>
    </div>
    """
    st.html(hero_html)

def render_section_header(title, subtitle=None, emoji=None):
    """Render consistent section headers"""
    header_html = f"""
    <div class="section-header-container" style="text-align: center; margin: 3rem 0 2rem 0;">
        <h2 class="section-header" style="
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
        ">
            {title}
            {f'<span style="font-size: 2rem;">{emoji}</span>' if emoji else ''}
        </h2>
        {f'<p style="color: var(--text-muted); font-size: 1.1rem;">{subtitle}</p>' if subtitle else ''}
        <div class="section-divider" style="
            height: 1px;
            background: linear-gradient(to right, transparent, var(--border-medium), transparent);
            margin: 1.5rem auto;
            max-width: 300px;
        "></div>
    </div>
    """
    st.html(header_html)

def render_metric_card(label, value, change=None, change_type=None):
    """Render modern metric cards"""
    change_class = ""
    change_symbol = ""
    
    if change and change_type:
        if change_type == "positive":
            change_class = "positive"
            change_symbol = "↗"
        elif change_type == "negative":
            change_class = "negative"
            change_symbol = "↘"
    
    card_html = f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {f'<div class="metric-change {change_class}">{change_symbol} {change}</div>' if change else ''}
    </div>
    """
    return card_html

def render_buy_rating_modern(rating, recommendation):
    """Render modern buy rating component"""
    
    # Determine rating color and border
    if rating >= 8:
        rating_color = "var(--success)"
        border_color = "var(--success)"
    elif rating >= 6:
        rating_color = "var(--warning)"
        border_color = "var(--warning)"
    else:
        rating_color = "var(--error)"
        border_color = "var(--error)"
    
    rating_html = f"""
    <div class="rating-container">
        <div class="buy-rating" style="border-color: {border_color};">
            <div class="rating-label">BUY RATING</div>
            <div class="rating-score" style="color: {rating_color};">{rating:.1f}</div>
            <div class="rating-text">{recommendation}</div>
        </div>
    </div>
    """
    st.html(rating_html)

def render_auth_container():
    """Render modern authentication container"""
    auth_html = """
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-logo">📊</div>
                <h2 class="auth-title">Welcome to Ticker AI</h2>
                <p class="auth-subtitle">Sign in to access advanced stock analysis</p>
            </div>
            <div id="auth-content">
                <!-- Auth forms will be rendered here -->
            </div>
        </div>
    </div>
    """
    return auth_html

def apply_modern_theme():
    """Apply modern theme CSS to the app"""
    
    # Load the modern CSS
    with open('assets/modern.css', 'r') as f:
        modern_css = f.read()
    
    # Apply CSS
    st.html(f"<style>{modern_css}</style>")
    
    # Set initial theme
    theme_script = """
    <script>
        // Initialize theme from localStorage or default to light
        (function() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        })();
    </script>
    """
    st.html(theme_script)

def render_card_container(content, title=None, subtitle=None):
    """Render content in a modern card container"""
    
    header_html = ""
    if title:
        header_html = f"""
        <div class="card-header">
            <h3 class="card-title">{title}</h3>
            {f'<p class="card-subtitle">{subtitle}</p>' if subtitle else ''}
        </div>
        """
    
    card_html = f"""
    <div class="card fade-in">
        {header_html}
        <div class="card-content">
            {content}
        </div>
    </div>
    """
    return card_html

def render_button(text, style="primary", onclick=None):
    """Render modern styled buttons"""
    onclick_attr = f'onclick="{onclick}"' if onclick else ''
    
    button_html = f"""
    <button class="btn btn-{style}" {onclick_attr}>
        {text}
    </button>
    """
    return button_html

def render_responsive_grid(items, min_width="250px"):
    """Render responsive grid layout"""
    grid_html = f"""
    <div style="
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax({min_width}, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    ">
        {''.join(items)}
    </div>
    """
    return grid_html