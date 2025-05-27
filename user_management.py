import streamlit as st
import json
import os
from passlib.hash import pbkdf2_sha256
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import create_engine, text
import pandas as pd

# Database connection
def get_db_engine():
    """Get database engine using environment variables"""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return create_engine(database_url)
    else:
        # Fallback to JSON file if database not available
        return None

# File to store user data (fallback)
USER_DB_FILE = "user_data.json"

def initialize_user_db():
    """Initialize the user database if it doesn't exist"""
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w") as f:
            json.dump({"users": []}, f)

def load_users():
    """Load users from PostgreSQL database"""
    engine = get_db_engine()
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT name, email, phone, password_hash, created_at FROM users ORDER BY created_at"))
                users = []
                for row in result:
                    users.append({
                        "name": row[0],
                        "email": row[1], 
                        "phone": row[2],
                        "password": row[3],
                        "created_at": str(row[4])
                    })
                return {"users": users}
        except Exception as e:
            st.error(f"Database error: {e}")
            return {"users": []}
    else:
        # Fallback to JSON if database not available
        initialize_user_db()
        try:
            with open(USER_DB_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            with open(USER_DB_FILE, "w") as f:
                json.dump({"users": []}, f)
            return {"users": []}

def save_users(users_data):
    """Save users to PostgreSQL database"""
    # This function is kept for compatibility but PostgreSQL handles saves automatically
    # Individual user saves are handled in register_user function
    pass

def register_user(name, email, phone, password):
    """Register a new user"""
    engine = get_db_engine()
    
    if engine:
        # Use PostgreSQL database
        try:
            with engine.connect() as conn:
                # Check if user already exists
                result = conn.execute(text("SELECT email FROM users WHERE email = :email"), {"email": email})
                if result.fetchone():
                    return False, "User with this email already exists"
                
                # Hash the password
                password_hash = pbkdf2_sha256.hash(password)
                created_at = datetime.now()
                
                # Insert new user
                conn.execute(text("""
                    INSERT INTO users (name, email, phone, password_hash, created_at) 
                    VALUES (:name, :email, :phone, :password_hash, :created_at)
                """), {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "password_hash": password_hash,
                    "created_at": created_at
                })
                conn.commit()
                return True, "User registered successfully"
        except Exception as e:
            return False, f"Database error: {e}"
    else:
        # Fallback to JSON file
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
    engine = get_db_engine()
    
    if engine:
        # Use PostgreSQL database
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT name, email, phone, password_hash FROM users 
                    WHERE email = :identifier OR phone = :identifier
                """), {"identifier": identifier})
                user_row = result.fetchone()
                
                if user_row and pbkdf2_sha256.verify(password, user_row[3]):
                    user_data = {
                        "name": user_row[0],
                        "email": user_row[1],
                        "phone": user_row[2]
                    }
                    return True, user_data
                return False, "Invalid credentials"
        except Exception as e:
            return False, f"Database error: {e}"
    else:
        # Fallback to JSON file
        users_data = load_users()
        
        for user in users_data["users"]:
            # Check if identifier matches email or phone
            if user["email"] == identifier or user["phone"] == identifier:
                # Verify password
                if pbkdf2_sha256.verify(password, user["password"]):
                    # Return consistent format
                    user_data = {
                        "name": user["name"],
                        "email": user["email"],
                        "phone": user["phone"]
                    }
                    return True, user_data
    
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
    engine = get_db_engine()
    
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                row = result.fetchone()
                return row[0] if row else 0
        except Exception as e:
            st.error(f"Database error: {e}")
            return 0
    else:
        # Fallback to JSON file
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