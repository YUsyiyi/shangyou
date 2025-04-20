import sqlite3
import streamlit as st
import pandas as pd
import json
import random
learning_progress_options = [
    "字符串", "基本运算", "if语句", "逻辑运算符", "字符串切片", 
    "列表", "字典", "函数", "递归", "文件操作", "异常处理", "面向对象",
    "列表推导式", "元组", "集合", "字典推导式", "条件表达式", "模块", 
    "类", "对象", "继承", "多态", "封装", "静态方法", "类方法", 
    "装饰器", "lambda表达式", "生成器", "迭代器", "正则表达式", "时间模块", 
    "日期与时间", "函数参数传递", "递归算法", "模块化编程", "命名空间", 
    "异常捕获", "try-except", "文件读取", "文件写入", "装饰器链", 
    "属性", "类变量", "实例变量", "自定义异常", "内存管理", "垃圾回收", 
    "编码与解码", "Python虚拟机", "闭包", "命令行参数"
]

blind_spots_options = [
    "for循环", "while循环", "break", "递归", "二分查找", 
    "动态规划", "正则表达式", "集合", "lambda表达式", "装饰器",
    "冒泡排序", "插入排序", "选择排序", "快速排序", "归并排序", 
    "堆排序", "桶排序", "计数排序", "基数排序", "链表", "双向链表", 
    "二叉树", "平衡二叉树", "红黑树", "B树", "B+树", "哈希算法", 
    "回溯算法", "贪心算法", "图的遍历", "深度优先搜索", "广度优先搜索", 
    "Dijkstra算法", "Bellman-Ford算法", "动态规划优化", "KMP算法", "TRIE树", 
    "并查集", "AVL树", "线段树", "树的遍历", "堆", "图的最短路径", 
    "A*算法", "并行编程", "多线程调度", "死锁", "Python内存管理", "进程间通信"
]
def generate_student_data():
    """生成60条学生测试数据并注册到1班"""
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
    
    # 确保班级表存在
    from utils.db_operations import create_class_table
    create_class_table()
    
    # 生成60条学生数据
    for i in range(1, 61):
        email = f"20243620{i:02d}"  # 2024352001到2024352060
        type = 0
        learning_progress = random.sample(learning_progress_options, random.randint(3, 5))  # 随机选择3到5个学习进度
        learning_progress = json.dumps(learning_progress)
        
        com_level = str(15)  # 随机选择一个难度级别（例如10到20之间）
        
        blind_spots = random.sample(blind_spots_options, random.randint(3, 5))  # 随机选择3到5个盲点
        blind_spots = json.dumps(blind_spots)
        
        # 插入用户数据
        cursor.execute("""
        INSERT OR REPLACE INTO users 
        (email, learning_progress, com_level, blind_spots, type)
        VALUES (?, ?, ?, ?, ?)
        """, (email, learning_progress, com_level, blind_spots, type))
        
        # 注册到1班
        cursor.execute("""
        INSERT OR REPLACE INTO classes (email, class_id)
        VALUES (?, 2)
        """, (email,))
    
    conn.commit()
    conn.close()
    st.success("成功生成60条学生测试数据并注册到1班！")

def ensure_tables_exist():
    """确保所有需要的表都存在"""
    from utils.db_operations import create_class_table, create_test_table2
    create_class_table()
    create_test_table2()

def get_student_test_records(email: str) -> pd.DataFrame:
    """获取学生的测试记录"""
    conn = sqlite3.connect("database.db")
    query = """
        SELECT teacher_email, title, answer, analysis, class_id
        FROM test
        WHERE student_email = ?
        ORDER BY rowid DESC
    """
    df = pd.read_sql(query, conn, params=(email,))
    conn.close()
    return df

def get_class_test_records(class_id: int) -> pd.DataFrame:
    """获取班级的测试记录"""
    conn = sqlite3.connect("database.db")
    query = """
        SELECT teacher_email, title, student_email, analysis
        FROM test
        WHERE class_id = ?
        ORDER BY rowid DESC
    """
    df = pd.read_sql(query, conn, params=(class_id,))
    conn.close()
    return df

def show_database():
    st.title("📊 Database Viewer")
    ensure_tables_exist()
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
    
    # 显示表选择器，默认选中classes表
    table_names = [table[0] for table in tables]
    default_index = table_names.index("classes") if "classes" in table_names else 0
    selected_table = st.selectbox(
        "📋 选择表",
        table_names,
        index=default_index,
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
    
    if selected_table == "classes":
        # 显示班级统计信息
        st.subheader("📊 班级统计")
        class_stats = pd.read_sql("""
            SELECT class_id, COUNT(email) as student_count 
            FROM classes 
            GROUP BY class_id
            ORDER BY class_id
        """, conn)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("班级数量", len(class_stats))
        with col2:
            st.metric("学生总数", class_stats["student_count"].sum())
        
        st.dataframe(class_stats, height=200)
        
        # 显示详细班级数据
        st.subheader("👥 班级学生详情")
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

def clear_database():
    """清空数据库所有表数据"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        st.warning("数据库中没有表")
        return False
    
    # 禁用外键约束
    cursor.execute("PRAGMA foreign_keys=OFF")
    
    try:
        # 清空每个表，包括test表
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DELETE FROM {table_name}")
            if table_name == "tests":
                st.info(f"✅ 已清空测试表(tests)")
            elif table_name == "classes":
                st.info(f"✅ 已清空班级表(classes)")
            elif table_name == "users":
                st.info(f"✅ 已清空用户表(users)")
            else:
                st.info(f"✅ 已清空表: {table_name}")
        
        conn.commit()
        st.success("数据库所有表数据已清空！")
        return True
    except Exception as e:
        st.error(f"清空数据库失败: {str(e)}")
        return False
    finally:
        # 重新启用外键约束
        cursor.execute("PRAGMA foreign_keys=ON")
        conn.close()

if __name__ == "__main__":
    st.sidebar.title("操作菜单")
    a=st.text_input("请输入密码", "")
    
    if st.button("进入") and a=="shangyou":
        option = st.sidebar.selectbox("选择操作", ["查看数据库", "生成测试数据", "清空数据库"])
        
        if option == "查看数据库":
            show_database()
        elif option == "生成测试数据":
            st.warning("这将清空并重新生成60条学生测试数据！")
            if st.button("确认生成"):
                generate_student_data()
                st.balloons()
        elif option == "清空数据库":
            st.error("⚠️ 这将永久删除所有表数据！")
            if st.checkbox("我确认要清空数据库"):
                if st.button("确认清空"):
                    if clear_database():
                        st.balloons()
