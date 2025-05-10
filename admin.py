import streamlit as st
from user_management import load_users, save_users, get_total_user_count
import pandas as pd

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
    
    st.title("Admin Panel")
    
    # Display user stats
    users_data = load_users()
    user_count = get_total_user_count()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Users", user_count)
    
    # User management section
    st.header("User Management")
    
    # Create a DataFrame from user data for display
    users_list = []
    for user in users_data["users"]:
        # Create a copy without the password
        user_display = {
            "name": user["name"],
            "email": user["email"],
            "phone": user["phone"],
            "created_at": user["created_at"]
        }
        users_list.append(user_display)
    
    if not users_list:
        st.info("No users registered yet")
    else:
        # Display users in a DataFrame
        df = pd.DataFrame(users_list)
        st.dataframe(df, use_container_width=True)
        
        # User deletion
        st.subheader("Delete User")
        delete_options = [f"{user['name']} ({user['email']})" for user in users_data["users"]]
        selected_user = st.selectbox("Select user to delete", delete_options)
        
        if st.button("Delete Selected User", type="primary"):
            # Extract email from selection
            email = selected_user.split("(")[1].split(")")[0]
            
            # Remove the user from the list
            users_data["users"] = [user for user in users_data["users"] if user["email"] != email]
            save_users(users_data)
            st.success(f"User {selected_user} deleted successfully")
            st.rerun()