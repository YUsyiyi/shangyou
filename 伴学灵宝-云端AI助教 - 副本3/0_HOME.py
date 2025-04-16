import streamlit as st
from utils.auth import login_user, register_user

def show():
    # 页面设置
    st.set_page_config(
        page_title="伴学灵宝 - 登录 / 注册",
        page_icon="🎓",
        layout="centered",
    )

    # 全局样式美化
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Noto Sans SC', sans-serif;
            background-color: #f3f8ff;
        }

        .stTabs [data-baseweb="tab"] {
            font-size: 18px;
            padding: 8px 24px;
        }

        .stButton>button {
            background-color: #4B8BF4;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-size: 1rem;
            transition: all 0.3s ease-in-out;
        }

        .stButton>button:hover {
            background-color: #3A6DD8;
            transform: scale(1.03);
        }

        .card {
            background-color: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-top: 1rem;
        }

        </style>
    """, unsafe_allow_html=True)

    # 页面标题
    st.markdown("<h1 style='text-align: center; color: #3A6DD8;'>🎓 伴学灵宝</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: grey;'>AI 赋能的教学辅助平台</h4>", unsafe_allow_html=True)

    # 登录 / 注册 Tab 页面
    tab1, tab2 = st.tabs(["🔐 登录", "📝 注册"])

    with tab1:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("欢迎回来 👋")
            st.caption("请输入你的邮箱以登录")

            email = st.text_input("📧 邮箱", key="login_email")
            if st.button("登录"):
                if login_user(email):
                    st.success("登录成功，正在跳转...")
                    st.switch_page("app.py")
            st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("新用户注册 🆕")
            st.caption("请输入信息以注册账号")

            email = st.text_input("📧 邮箱", key="register_email")

            user_type = st.radio("选择用户类型",
                                 options=["学生", "老师"],
                                 index=0,
                                 format_func=lambda x: f"{'👨‍🎓' if x == '学生' else '👨‍🏫'} {x}",
                                 horizontal=True)

            if st.button("注册"):
                type_value = 0 if user_type == "学生" else 1
                if register_user(email, type_value):
                    st.success("注册成功，正在跳转...")
                    st.switch_page("app.py")
            st.markdown("</div>", unsafe_allow_html=True)

    # 底部欢迎信息
    with st.container():
        st.divider()
        st.markdown("""
        <div style="padding: 1rem; text-align: center;">
            <h4>🎉 欢迎使用 <span style="color: #4B8BF4;">伴学灵宝</span>！</h4>
            <p style="color: grey;">一个融合 AI 技术的教学平台，助力学生成长，辅助老师教学。</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    show()
