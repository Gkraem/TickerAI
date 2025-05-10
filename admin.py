import streamlit as st
from user_management import load_users, save_users, get_total_user_count
import pandas as pd
import os
from notification import send_bulk_sms, send_sms_notification

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
    
    st.title("Ticker AI Admin Panel")
    
    # Display user stats
    users_data = load_users()
    user_count = get_total_user_count()
    
    # Dashboard stats
    st.markdown("### Dashboard")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Registered Users", user_count)
    
    with col2:
        # Check how many users registered in the last 24 hours
        import datetime
        now = datetime.datetime.now()
        last_24h = 0
        last_7d = 0
        
        for user in users_data["users"]:
            try:
                created = datetime.datetime.fromisoformat(user["created_at"])
                time_diff = now - created
                if time_diff.days < 1:
                    last_24h += 1
                if time_diff.days < 7:
                    last_7d += 1
            except (ValueError, KeyError):
                continue
                
        st.metric("New Users (24h)", last_24h)
    
    with col3:
        st.metric("New Users (7d)", last_7d)
    
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
    
    # SMS Notification System
    st.markdown("---")
    st.header("User Notifications")
    
    # Check if Twilio credentials are configured
    twilio_configured = all([
        os.environ.get("TWILIO_ACCOUNT_SID"),
        os.environ.get("TWILIO_AUTH_TOKEN"),
        os.environ.get("TWILIO_PHONE_NUMBER")
    ])
    
    if not twilio_configured:
        st.warning("⚠️ Twilio SMS service is not configured. Please set the TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables to enable SMS notifications.")
        
        # Add button to request Twilio credentials
        if st.button("Configure Twilio Credentials"):
            # This would typically use a secure method to set environment variables
            st.info("Please contact the system administrator to configure Twilio credentials.")
    else:
        st.success("✅ Twilio SMS service is configured and ready to use.")
        
        # SMS notification form
        st.subheader("Send SMS Notification")
        
        # Choose notification recipients
        notification_type = st.radio(
            "Send notification to:",
            ["All Users", "Selected User"]
        )
        
        # Message to send
        notification_message = st.text_area(
            "Notification message:",
            placeholder="Enter your message here...",
            height=100
        )
        
        if notification_type == "Selected User":
            # User selection dropdown
            if users_data["users"]:
                user_options = [f"{user.get('name', 'Unknown')} ({user.get('phone', 'No phone')})" for user in users_data["users"]]
                selected_user_option = st.selectbox("Select user:", user_options)
                
                # Extract user from selection
                selected_user_name = selected_user_option.split(" (")[0]
                selected_user = next((user for user in users_data["users"] if user.get('name') == selected_user_name), None)
                
                if st.button("Send SMS", type="primary", disabled=not notification_message or not selected_user):
                    if not selected_user or not selected_user.get('phone'):
                        st.error("Selected user doesn't have a phone number.")
                    else:
                        with st.spinner("Sending SMS..."):
                            # Format phone number if needed
                            phone = selected_user.get('phone')
                            if not phone.startswith('+'):
                                phone = f"+1{phone.replace('-', '').replace(' ', '')}"
                                
                            # Send the SMS
                            result = send_sms_notification(phone, notification_message)
                            
                            if result["success"]:
                                st.success(f"SMS sent successfully to {selected_user.get('name')}!")
                            else:
                                st.error(f"Failed to send SMS: {result['message']}")
            else:
                st.info("No users available to send notifications to.")
        else:  # All Users
            # Send to all users
            if st.button("Send to All Users", type="primary", disabled=not notification_message):
                if not users_data["users"]:
                    st.error("No users available to send notifications to.")
                else:
                    with st.spinner(f"Sending SMS to {len(users_data['users'])} users..."):
                        results = send_bulk_sms(users_data["users"], notification_message)
                        
                        if results["success"] > 0:
                            st.success(f"Successfully sent {results['success']} of {results['total']} messages.")
                        
                        if results["failed"] > 0:
                            st.error(f"Failed to send {results['failed']} messages.")
                            
                            # Show failures if any
                            if results["failures"]:
                                st.expander("View failures", expanded=False).dataframe(
                                    pd.DataFrame(results["failures"])
                                )
    
    # Display admin contact information
    st.markdown("---")
    st.markdown("### Administrator Contact")
    st.markdown("For system issues, please contact:")
    st.markdown("**Email:** gkraem@vt.edu")
    st.markdown("**Phone:** 240-285-7119")