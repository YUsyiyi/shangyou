import streamlit as st
from utils.auth import login_user, register_user

def show():
    with st.sidebar:
        st.title("🎓 AI Teaching Assistant")
        st.page_link("app.py", label="🏠 首页")
        st.page_link("pages/1_📚_Lecture_Generator.py", label="📚 AI讲义生成")
        st.page_link("pages/2_✏_Problem_Tutor.py", label="✏ AI做题辅导")
        st.page_link("pages/3_📊_Learning_Analysis.py", label="📊 我的学情")

    st.title("🏠 AI教学助手")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        if st.button("Login"):
            if login_user(email):
                print(type(email))
                st.switch_page("app.py")
    
    with tab2:
        st.subheader("Register")
        email = st.text_input("Email", key="register_email")
        user_type = st.radio("选择用户类型", 
                           options=["学生", "老师"],
                           index=0,
                           format_func=lambda x: f"{'👨🎓' if x == '学生' else '👨🏫'} {x}")

        if st.button("Register"):
            type_value = 0 if user_type == "学生" else 1
            if register_user(email,type_value):
                st.switch_page("app.py")
    
    st.divider()
    st.write("""
    ### 欢迎使用AI教学助手！
该工具帮助学生：
- 📚 从材料生成讲义笔记
- ✏ 提供问题解答帮助
- 📊 跟踪学习进度
    """)
if __name__ == "__main__":
    show()
