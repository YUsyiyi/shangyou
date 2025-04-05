import streamlit as st
import json
from typing import List, Optional
def get_user_type(email: str) -> Optional[int]:
    """专门获取用户类型字段"""
    conn = st.connection("mysql", type="sql", autocommit=True)
    try:
        # 聚焦查询单个字段
        result = conn.query(
            "SELECT type FROM users WHERE email = :email",
            params={"email": email}
        )
        
        if result.empty:
            st.warning(f"用户 {email} 不存在")
            return None
            
        # 确认数据类型安全转换
        user_type = int(result.iloc[0]['type'])
        return user_type
    except Exception as e:
        st.error(f"获取用户类型失败: {str(e)}")
        return None
def update_learning_progress(email: str, progress_items: List[str]) -> bool:
    """Update user's learning progress in database"""
    conn = st.connection("mysql", type="sql", autocommit=True)
    try:
        # Convert list to JSON string for storage
        progress_json = json.dumps(progress_items)
        
        conn.query(
            """UPDATE users 
               SET learning_progress = :progress 
               WHERE email = :email""",
            params={"progress": progress_json, "email": email}
        )
        return True
    except Exception as e:
        
        return False

def update_com_level(email: str, level: str) -> bool:
    """Update user's competency level in database"""
    conn = st.connection("mysql", type="sql", autocommit=True)
    try:
        conn.query(
            """UPDATE users 
               SET com_level = :level 
               WHERE email = :email""",
            params={"level": level, "email": email}
        )
        return True
    except Exception as e:
        return False

def update_blind_spots(email: str, blind_spots: List[str]) -> bool:
    """Update user's knowledge blind spots in database"""
    conn = st.connection("mysql", type="sql", autocommit=True)
    try:
        # Convert list to JSON string for storage
        blind_spots_json = json.dumps(blind_spots)
        
        conn.query(
            """UPDATE users 
               SET blind_spots = :blind_spots 
               WHERE email = :email""",
            params={"blind_spots": blind_spots_json, "email": email}
        )
        return True
    except Exception as e:
        
        return False

def get_user_data(email: str) -> Optional[dict]:
    """Get complete user data from database"""
    conn = st.connection("mysql", type="sql", autocommit=True)
    try:
        result = conn.query(
            """SELECT email, learning_progress, com_level, blind_spots,type 
               FROM users WHERE email = :email""",
            params={"email": email}
        )
        
        if result.empty:
            return None
            
        data = result.iloc[0].to_dict()
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
def  get_know_com_blind_solve(learning_progress,com_level,blind_spot,answer,title):

    # 假设 com_level 和 learning_progress 已经定义
    # 构建字典
    data = {
        "know_level": learning_progress,
        "com_level": com_level,
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
    conn = st.connection("mysql", type="sql", autocommit=True)
    try:
        result = conn.query(
            """SELECT email, learning_progress, com_level, blind_spots 
               FROM users WHERE email = :email""",
            params={"email": email}
        )
        
        if result.empty:
            return None
            
        data = result.iloc[0].to_dict()
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
    conn = st.connection("mysql", type="sql", autocommit=True)
    try:
        # 查询所有用户数据
        result = conn.query(
            """SELECT email, learning_progress, com_level, blind_spots 
               FROM users"""
        )
        
        if result.empty:
            return []
            
        users_data = []
        # 遍历每一行数据
        for _, row in result.iterrows():
            user_data = row.to_dict()
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
def get_all_users_data() -> List[Dict]:
    """获取数据库中所有用户的学习数据"""
    conn = st.connection("mysql", type="sql", autocommit=True)
    try:
        # 查询所有用户数据
        result = conn.query(
            """SELECT email, learning_progress, com_level, blind_spots 
               FROM users"""
        )
        
        if result.empty:
            return []
            
        users_data = []
        # 遍历每一行数据
        for _, row in result.iterrows():
            user_data = row.to_dict()
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
            # 仅保留核心数据字段
            summary.extend([
                f"邮箱：{user['email']}",
                f"能力等级：{user['com_level']}",
                "学习进度原始数据：",
                str(user['learning_progress']),
                "知识盲点原始数据：",
                str(user['blind_spots']),
                "-"*40 + "\n"
            ])
        
        summary.extend([
            "\n备注说明：",
            "您的学生都很棒噢",
            "✅✅✅✅✅"
        ])
        
        return "\n".join(summary)    