import streamlit as st
import json
import os
from passlib.hash import pbkdf2_sha256
from datetime import datetime

# File to store user data
USER_DB_FILE = "user_data.json"

def initialize_user_db():
    """Initialize the user database if it doesn't exist"""
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w") as f:
            json.dump({"users": []}, f)

def load_users():
    """Load users from the database file"""
    initialize_user_db()
    try:
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # If file is corrupted or not found, reset it
        with open(USER_DB_FILE, "w") as f:
            json.dump({"users": []}, f)
        return {"users": []}

def save_users(users_data):
    """Save users to the database file"""
    with open(USER_DB_FILE, "w") as f:
        json.dump(users_data, f, indent=4)

def register_user(name, email, phone, password):
    """Register a new user"""
    users_data = load_users()
    
    # Check if user already exists
    for user in users_data["users"]:
        if user["email"] == email or user["phone"] == phone:
            return False, "Email or phone number already registered"
    
    # Hash password
    hashed_password = pbkdf2_sha256.hash(password)
    
    # Create new user
    new_user = {
        "name": name,
        "email": email,
        "phone": phone,
        "password": hashed_password,
        "created_at": datetime.now().isoformat()
    }
    
    # Add user to database
    users_data["users"].append(new_user)
    save_users(users_data)
    
    # Try to send admin notification
    try:
        from notification import send_admin_notification
        send_admin_notification(new_user)
    except Exception as e:
        print(f"Failed to send admin notification: {str(e)}")
    
    return True, "Registration successful"

def authenticate_user(identifier, password):
    """Authenticate a user by email/phone and password"""
    users_data = load_users()
    
    for user in users_data["users"]:
        # Check if identifier matches email or phone
        if user["email"] == identifier or user["phone"] == identifier:
            # Verify password
            if pbkdf2_sha256.verify(password, user["password"]):
                return True, user
    
    return False, "Invalid credentials"

def get_session_user():
    """Get the current logged-in user from session state"""
    if "user" in st.session_state:
        return st.session_state["user"]
    return None

def is_authenticated():
    """Check if user is authenticated"""
    return "user" in st.session_state

def logout_user():
    """Log out the current user"""
    if "user" in st.session_state:
        del st.session_state["user"]
        
        
def get_total_user_count():
    """
    Returns the total number of registered users in the system
    
    Returns:
    --------
    int
        The total count of registered users
    """
    users_data = load_users()
    return len(users_data["users"])


def is_admin():
    """
    Checks if the current user is an admin
    
    Returns:
    --------
    bool
        True if the user is an admin, False otherwise
    """
    user = get_session_user()
    if not user:
        return False
    
    # Admin email address - only this account has admin access
    admin_email = "gkraem@vt.edu"
    return user.get("email", "") == admin_email