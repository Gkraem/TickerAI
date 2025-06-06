import streamlit as st
from user_management import load_users, save_users, get_total_user_count
import pandas as pd
import datetime
from collections import Counter

def is_admin():
    """Check if the current user is an admin"""
    if "user" not in st.session_state or st.session_state["user"] is None:
        return False
    
    # Check if the user's email is the admin email
    admin_email = "gkraem@vt.edu"  # Admin email hardcoded for now
    return st.session_state["user"]["email"] == admin_email

def admin_panel():
    """Admin panel for user management"""
    if not is_admin():
        st.error("You don't have permission to access this page")
        return
    
    # Display user stats
    users_data = load_users()
    user_count = get_total_user_count()
    
    # Dashboard stats
    st.markdown("### Dashboard")
    
    st.metric("Total Registered Users", user_count)
    
    # User management section
    st.markdown("---")
    st.header("User Management")
    
    # Create a DataFrame from user data for display
    users_list = []
    for user in users_data["users"]:
        # Create a copy without the password
        user_display = {
            "Name": user.get("name", "Unknown"),
            "Email": user.get("email", "No email"),
            "Phone": user.get("phone", "No phone"),
            "Registration Date": user.get("created_at", "Unknown")
        }
        users_list.append(user_display)
    
    if not users_list:
        st.info("No users registered yet")
    else:
        # Display options for sorting and filtering
        col1, col2 = st.columns(2)
        with col1:
            sort_by = st.selectbox("Sort by", ["Registration Date", "Name", "Email"], index=0)
        with col2:
            ascending = st.checkbox("Ascending order", value=False)
        
        # Display users in a DataFrame
        df = pd.DataFrame(users_list)
        
        # Sort the dataframe
        df = df.sort_values(by=sort_by, ascending=ascending)
        
        st.dataframe(df, use_container_width=True, height=400)
        
        # User deletion
        st.markdown("---")
        st.subheader("Delete User")
        st.warning("⚠️ This action cannot be undone. The user will need to register again.")
        
        delete_options = [f"{user.get('name', 'Unknown')} ({user.get('email', 'No email')})" for user in users_data["users"]]
        selected_user = st.selectbox("Select user to delete", delete_options)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Delete User", type="primary", use_container_width=True):
                # Extract email from selection
                email = selected_user.split("(")[1].split(")")[0]
                
                # Remove the user from the list
                users_data["users"] = [user for user in users_data["users"] if user.get("email") != email]
                save_users(users_data)
                st.success(f"User {selected_user} deleted successfully")
                st.rerun()
    
    # Return to home button
    st.markdown("---")
    if st.button("Return to Stock Search", type="primary", use_container_width=True):
        st.session_state.view_mode = "main"
        st.rerun()
    
    # Add vertical buffer at the bottom
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)