import streamlit as st
import json
from utils import db_operations
from typing import Optional
def init_db_connection():
    """Initialize and return MySQL connection"""
    try:
        conn = st.connection("mysql", type="sql", autocommit=True)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None
def register_user(email,type):
    """Register a new user with default learning d
    ata"""
    conn = init_db_connection()
    try:
        # Check if user exists
        existing_user = conn.query(
            "SELECT email FROM users WHERE email = :email",
            params={"email": email}
        )
        
        if not existing_user.empty:
            st.error("Email already registered!")
            return False
            
        # Insert new user with default values
        conn.query(
            """INSERT INTO users (email, learning_progress, com_level, blind_spots,type) 
               VALUES (:email, '[]', '0', '[]',:type)""",
            params={"email": email
                    , "type":int(type)}
            
        )
        
        st.success("Registration successful!")
        return True
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")
        return False

def login_user(email):
    """Login existing user"""
    conn = init_db_connection()
    try:
        user = conn.query(
            "SELECT email FROM users WHERE email = :email",
            params={"email": email}
        )
        
        if user.empty:
            st.error("Email not found!")
            return False
        result = conn.query(
            """SELECT email, learning_progress, com_level, blind_spots,type 
               FROM users WHERE email = :email""",
            params={"email": email}
        )
        
        if result.empty:
            return None
            
        data = result.iloc[0].to_dict()
        data['type'] = int(data['type'])    
        st.session_state.user_email = email


        st.session_state.user_type=data['type']
        st.success("Login successful!")
        return True
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False

def logout_user():
    """Logout current user"""
    if 'user_email' in st.session_state:
        del st.session_state.user_email
        del st.session_state.user_type
    st.success("Logged out successfully!")

def get_user_data(email: str) -> Optional[dict]:
    """Get complete user data including learning progress"""
    return db_operations.get_user_data(email)
def get_user_type(email: str) -> Optional[dict]:
    """Get complete user data including learning progress"""
    return db_operations.get_user_type(email)
