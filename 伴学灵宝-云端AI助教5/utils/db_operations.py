import sqlite3
import json
from typing import List, Optional
import streamlit as st
def get_user_type(email: str) -> Optional[int]:
    """专门获取用户类型字段"""
    conn = sqlite3.connect("database.db")
    try:
        # 聚焦查询单个字段
        cursor = conn.cursor()
        cursor.execute(
            "SELECT type FROM users WHERE email = ?",
            (email,)
        )
        result = cursor.fetchone()
        
        if not result:
            st.warning(f"用户 {email} 不存在")
            return None
            
        # 确认数据类型安全转换
        user_type = int(result[0])
        return user_type
    except Exception as e:
        st.error(f"获取用户类型失败: {str(e)}")
        return None
def update_learning_progress(email: str, progress_items: List[str]) -> bool:
    """Update user's learning progress in database"""
    conn = sqlite3.connect("database.db")
    try:
        # Convert list to JSON string for storage
        progress_json = json.dumps(progress_items)
        
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE users 
               SET learning_progress = ? 
               WHERE email = ?""",
            (progress_json, email)
        )
        conn.commit()
        return True
    except Exception as e:
        
        return False

def update_com_level(email: str, level: str) -> bool:
    """Update user's competency level in database"""
    conn = sqlite3.connect("database.db")
    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE users 
               SET com_level = ? 
               WHERE email = ?""",
            (level, email)
        )
        conn.commit()
        return True
    except Exception as e:
        return False

def update_blind_spots(email: str, blind_spots: List[str]) -> bool:
    """Update user's knowledge blind spots in database"""
    conn = sqlite3.connect("database.db")
    try:
        # Convert list to JSON string for storage
        blind_spots_json = json.dumps(blind_spots)
        
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE users 
               SET blind_spots = ? 
               WHERE email = ?""",
            (blind_spots_json, email)
        )
        conn.commit()
        return True
    except Exception as e:
        
        return False

def get_user_data(email: str) -> Optional[dict]:
    """Get complete user data from database"""
    conn = sqlite3.connect("database.db")
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT email, learning_progress, com_level, blind_spots
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
            
        }
        # Convert JSON strings back to lists
        if data['learning_progress']:
            data['learning_progress'] = json.loads(data['learning_progress'])
        if data['blind_spots']:
            data['blind_spots'] = json.loads(data['blind_spots'])
        return data
    except Exception as e:
      
        return None

def  get_com(email):
    user_text=get_user_data(email)
    com_level = user_text.get('com_level', '')
    # 假设 com_level 和 learning_progress 已经定义
    # 构建字典
    data = {
       
        "com_level": com_level
    }

    # 将字典转换为 JSON 格式的字符串
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data

def  get_know_com(email):
    user_text=get_user_data(email)
    learning_progress = user_text.get('learning_progress', [])
    com_level = user_text.get('com_level', '')
    # 假设 com_level 和 learning_progress 已经定义
    # 构建字典
    data = {
        "know_level": learning_progress,
        "com_level": com_level
    }

    # 将字典转换为 JSON 格式的字符串
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data
def  get_know_com_blind(email,blind_spot):
    user_text=get_user_data(email)
    learning_progress = user_text.get('learning_progress', [])
    com_level = user_text.get('com_level', '')
    # 假设 com_level 和 learning_progress 已经定义
    # 构建字典
    data = {
        "know_level": learning_progress,
        "com_level": com_level,
        "blind_spot": blind_spot
    }

    # 将字典转换为 JSON 格式的字符串
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data
def  get_know_com_blind_solve(learning_progress,blind_spot,answer,title):

    # 假设 com_level 和 learning_progress 已经定义
    # 构建字典
    data = {
        "know_level": learning_progress,
        "blind_spot": blind_spot,
        "answer": answer,
        "title": title
    }

    # 将字典转换为 JSON 格式的字符串
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data


#获得一个学生的所有数据:
def get_user_data2(email: str) -> Optional[dict]:
    """Get complete user data from database"""
    conn = sqlite3.connect("database.db")
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT email, learning_progress, com_level, blind_spots 
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
            'blind_spots': result[3]
        }
        # Convert JSON strings back to lists
        if data['learning_progress']:
            data['learning_progress'] = json.loads(data['learning_progress'])
        if data['blind_spots']:
            data['blind_spots'] = json.loads(data['blind_spots'])
        if data['com_level']:
            data['com_level'] = json.loads(data['com_level'])    
        return data
    except Exception as e:
      
        return None
    


#获得所有学生的数据:
from typing import List, Dict

def get_all_users_data() -> List[Dict]:
    """获取数据库中所有用户的学习数据"""
    conn = sqlite3.connect("database.db")
    try:
        # 查询所有用户数据
        cursor = conn.cursor()
        cursor.execute(
            """SELECT email, learning_progress, com_level, blind_spots
               FROM users"""
        )
        results = cursor.fetchall()
        
        if not results:
            return []
            
        users_data = []
        # 遍历每一行数据
        for row in results:
            user_data = {
                'email': row[0],
                'learning_progress': row[1],
                'com_level': row[2],
                'blind_spots': row[3]
            }
            # 转换JSON字段
            if user_data['learning_progress']:
                user_data['learning_progress'] = json.loads(user_data['learning_progress'])
            if user_data['blind_spots']:
                user_data['blind_spots'] = json.loads(user_data['blind_spots'])
            users_data.append(user_data)
            
        return users_data
        
    except Exception as e:
        st.error(f"数据库查询失败: {str(e)}")
        return []
def generate_raw_summary(all_users: List[Dict]) -> str:
  
        summary = ["="*40, "学生原始数据汇总报告", "="*40 + "\n"]
        
        for user in all_users:
            if user['learning_progress']:
                # 仅保留核心数据字段
                summary.extend([
                    f"邮箱：{user['email']}",
                    "学习进度：",
                    str(user['learning_progress']),
                    "知识盲点：",
                    str(user['blind_spots']),
                    "-"*40 + "\n"
                ])
        
        summary.extend([
            "\n备注说明：",
            "您的学生都很棒噢",
            "✅✅✅✅✅"
        ])
        
        return "\n".join(summary)

def create_test_table():
    """Create the test table if it doesn't exist"""
    conn = sqlite3.connect("database.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                student_email TEXT NOT NULL,
                question TEXT NOT NULL,
                teacher_email TEXT NOT NULL,
                FOREIGN KEY(student_email) REFERENCES users(email),
                FOREIGN KEY(teacher_email) REFERENCES users(email)
            )
        """)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"创建测试表失败: {str(e)}")
        return False

def add_test_record(student_email: str, question: str, teacher_email: str) -> bool:
    """Add a new test record to database"""
    conn = sqlite3.connect("database.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tests (student_email, question, teacher_email)
            VALUES (?, ?, ?)
        """, (student_email, question, teacher_email))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"添加测试记录失败: {str(e)}")
        return False

def get_student_tests(student_email: str) -> List[Dict]:
    """Get all tests for a student"""
    conn = sqlite3.connect("database.db")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT question, teacher_email 
            FROM tests 
            WHERE student_email = ?
            ORDER BY rowid DESC
        """, (student_email,))
        
        tests = []
        for row in cursor.fetchall():
            tests.append({
                'question': row[0],
                'teacher_email': row[1]
            })
        return tests
    except Exception as e:
        st.error(f"获取学生测试失败: {str(e)}")
        return []
def get_all_users_data_new() -> List[Dict]:
    """获取所有type=0的学生邮箱"""
    conn = sqlite3.connect("database.db")
    try:
        cursor = conn.cursor()
        # 只查询email字段
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()

        emails_type_0 = []
        for result in results:
            user_type = int(result[4])  # 第5列是 type
            if user_type == 0:
                email = result[0]       # 第1列是 email
                emails_type_0.append(email)

        # 直接提取第一列（email）并过滤空值
        return emails_type_0
    finally:
        conn.close()
