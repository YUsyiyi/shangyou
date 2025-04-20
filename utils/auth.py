import streamlit as st
import json
from utils import db_operations
from typing import Optional
import sqlite3
def init_db_connection():
    """Initialize and return database connection"""
    try:
        conn = sqlite3.connect("database.db")
        # Create users table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                learning_progress TEXT,
                com_level TEXT,
                blind_spots TEXT,
                type INTEGER
            )
        """)
        conn.commit()
        return conn
    except Exception as e:
        st.error(f"数据库连接失败: {str(e)}")
        return None
def register_user(email, user_type, class_id=None):
    """Register a new user with default learning data"""
    conn = init_db_connection()
    if not conn:
        return False
        
    try:
        # Validate user_type is 0 (student) or 1 (teacher)
        user_type = int(user_type)
        if user_type not in (0, 1):
            st.error("Invalid user type. Must be 0 (student) or 1 (teacher)")
            return False
            
        cursor = conn.cursor()
        # Check if user exists
        cursor.execute(
            "SELECT email FROM users WHERE email = ?",
            (email,)
        )
        existing_user = cursor.fetchone()
        
        if existing_user:
            st.error("Email already registered!")
            return False
            
        # Set default values based on user type
        if user_type == 0:  # Student
            learning_progress =  json.dumps(["字符串","基本运算","if语句","逻辑运算符","字符串切片"])
            com_level = '15'
            blind_spots = json.dumps(["for循环","while循环","break","递归"])
        else:  # Teacher
            learning_progress = '[]'
            com_level = '0'
            blind_spots = '[]'
            
        # Insert new user
        cursor.execute(
            """INSERT INTO users (email, learning_progress, com_level, blind_spots, type) 
               VALUES (?, ?, ?, ?, ?)""",
            (email, learning_progress, com_level, blind_spots, user_type)
        )
        
        # If student and class_id provided, assign to class
        if user_type == 0 and class_id is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS classes (
                        email TEXT NOT NULL,
                        class_id INTEGER NOT NULL,
                        PRIMARY KEY (email, class_id),
                        FOREIGN KEY(email) REFERENCES users(email)
                    )
                """)
                conn.commit()
               
            except Exception as e:
                st.error(f"创建班级表失败: {str(e)}")
        
            # db_operations.create_class_table()
            # db_operations.assign_class(email, class_id)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO classes (email, class_id)
                    VALUES (?, ?)
                """, (email, class_id))
                conn.commit()
            except Exception as e:
                st.error(f"分配班级失败: {str(e)}")
        conn.commit()
        
        st.success(f"Registration successful as {'student' if user_type == 0 else 'teacher'}!")
        return True
    except ValueError:
        st.error("User type must be 0 (student) or 1 (teacher)")
        return False
    except Exception as e:
        st.error(f"用户注册失败: {str(e)}")
        return False

def login_user(email):
    """Login existing user"""
    conn = init_db_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        # Check if user exists
        cursor.execute(
            "SELECT email FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        
        if not user:
            st.error("Email not found!")
            return False
            
        # Get user data
        cursor.execute(
            """SELECT email, learning_progress, com_level, blind_spots, type 
               FROM users WHERE email = ?""",
            (email,)
        )
        result = cursor.fetchone()
        
        if not result:
            return None
            
        data = {
            'email': result[0],
            'learning_progress': result[1],
            'com_level': result[2],
            'blind_spots': result[3],
            'type': int(result[4])
        }
        
        st.session_state.user_email = email
        st.session_state.user_type = data['type']
        
        # If student, get class info
        if data['type'] == 0:
            class_id = db_operations.get_student_class(email)
            if class_id:
                st.session_state.class_id = class_id
        
        st.success("Login successful!")
        return True
    except Exception as e:
        st.error(f"用户登录失败: {str(e)}")
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

def get_user_class(email: str) -> Optional[int]:
    """Get student's class ID"""
    if db_operations.get_user_type(email) != 0:
        return None
    return db_operations.get_student_class(email)
