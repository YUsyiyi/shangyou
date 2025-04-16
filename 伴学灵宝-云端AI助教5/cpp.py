import sqlite3
import streamlit as st
import pandas as pd
import json

def generate_student_data():
    """生成60条学生测试数据"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # 创建users表(如果不存在)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        learning_progress TEXT,
        com_level TEXT,
        blind_spots TEXT,
        type INTEGER
    )
    """)
    
    # 生成60条学生数据
    for i in range(1, 61):
        email = f"20243520{i:02d}"  # 2024352001到2024352060
        type = 0
        learning_progress = json.dumps(["字符串","基本运算","if语句","逻辑运算符","字符串切片"])
        com_level = "15"
        blind_spots = json.dumps(["for循环","while循环","break","递归"])
        
        # 插入数据
        cursor.execute("""
        INSERT OR REPLACE INTO users 
        (email, learning_progress, com_level, blind_spots, type)
        VALUES (?, ?, ?, ?, ?)
        """, (email, learning_progress, com_level, blind_spots, type))
    
    conn.commit()
    conn.close()
    st.success("成功生成60条学生测试数据！")

def show_database():
    st.title("📊 Database Viewer")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
                box-shadow: 0 6px 16px rgba(33,150,243,0.2);
                border-left: 5px solid #2196f3;">
        <h3 style="color: #0d47a1;">Database.db 数据查看器</h3>
        <p style="font-size: 0.95rem; color: #1565c0;">查看和浏览数据库内容</p>
    </div>
    """, unsafe_allow_html=True)

    # 连接数据库
    conn = sqlite3.connect("database.db")
    
    # 获取所有表名
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        st.warning("数据库中没有表")
        return
    
    # 显示表选择器
    selected_table = st.selectbox(
        "📋 选择表",
        [table[0] for table in tables],
        key="table_selector"
    )
    
    # 显示表结构
    st.subheader("🔍 表结构")
    cursor.execute(f"PRAGMA table_info({selected_table})")
    columns = cursor.fetchall()
    columns_df = pd.DataFrame(columns, columns=["cid", "name", "type", "notnull", "dflt_value", "pk"])
    st.dataframe(columns_df[["name", "type", "pk"]], hide_index=True)
    
    # 显示表数据
    st.subheader("📝 表数据")
    query = f"SELECT * FROM {selected_table}"
    data = pd.read_sql(query, conn)
    st.dataframe(data, height=400)
    
    # 添加简单查询功能
    st.subheader("🔎 自定义查询")
    custom_query = st.text_area("输入SQL查询语句", f"SELECT * FROM {selected_table} LIMIT 100")
    
    if st.button("▶ 执行查询"):
        try:
            result = pd.read_sql(custom_query, conn)
            st.dataframe(result, height=400)
        except Exception as e:
            st.error(f"查询错误: {str(e)}")
    
    conn.close()

if __name__ == "__main__":
    st.sidebar.title("操作菜单")
    option = st.sidebar.selectbox("选择操作", ["查看数据库", "生成测试数据"])
    
    if option == "查看数据库":
        show_database()
    elif option == "生成测试数据":
        st.warning("这将清空并重新生成60条学生测试数据！")
        if st.button("确认生成"):
            generate_student_data()
            st.balloons()
