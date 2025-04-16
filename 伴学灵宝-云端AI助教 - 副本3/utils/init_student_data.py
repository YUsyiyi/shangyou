import sqlite3
import json

def init_student_data():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Create table if not exists (same as auth.py)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            learning_progress TEXT,
            com_level TEXT,
            blind_spots TEXT,
            type INTEGER
        )
    """)
    
    # Sample Python learning data
    students = [
        {
            "email": "student1@example.com",
            "learning_progress": ["变量和数据类型", "条件语句", "循环"],
            "com_level": "15",
            "blind_spots": ["函数参数", "列表推导式"],
            "type": 0
        },
        {
            "email": "student2@example.com",
            "learning_progress": ["函数", "面向对象编程", "异常处理"],
            "com_level": "15",
            "blind_spots": ["装饰器", "生成器"],
            "type": 0
        },
        {
            "email": "student3@example.com",
            "learning_progress": ["模块和包", "文件操作", "正则表达式"],
            "com_level": "15",
            "blind_spots": ["多线程", "异步编程"],
            "type": 0
        },
        {
            "email": "student4@example.com",
            "learning_progress": ["数据结构", "算法基础", "单元测试"],
            "com_level": "15",
            "blind_spots": ["设计模式", "性能优化"],
            "type": 0
        },
        {
            "email": "student5@example.com",
            "learning_progress": ["网络编程", "数据库操作", "Web框架"],
            "com_level": "15",
            "blind_spots": ["元编程", "C扩展"],
            "type": 0
        }
    ]
    
    for student in students:
        # Convert lists to JSON strings
        learning_json = json.dumps(student["learning_progress"], ensure_ascii=False)
        blind_json = json.dumps(student["blind_spots"], ensure_ascii=False)
        
        cursor.execute(
            """INSERT OR REPLACE INTO users 
               (email, learning_progress, com_level, blind_spots, type)
               VALUES (?, ?, ?, ?, ?)""",
            (student["email"], learning_json, student["com_level"], blind_json, student["type"])
        )
    
    conn.commit()
    conn.close()
    print("成功初始化5个学生数据")

if __name__ == "__main__":
    init_student_data()
