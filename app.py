import streamlit as st
from utils.auth import logout_user
import streamlit as st
from utils.auth import login_user, register_user
def main():
    # 初始化 session
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None

    # 页面基础设置
    st.set_page_config(
        page_title="伴学灵宝 - 云端AI课件",
        page_icon="https://img.icons8.com/color/48/artificial-intelligence.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 美化样式：引入字体、统一按钮颜色、文字居中等
    st.markdown("""
        <style>
        html, body, [class*="css"]  {
            font-family: 'Noto Sans SC', sans-serif;
        }

        .stButton>button {
            background-color: #4B8BF4;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            font-size: 1rem;
            transition: 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #3A6DD8;
            transform: scale(1.05);
        }
        section[data-testid="stSidebar"] {
    width: 220px !important;  /* 你可以改成你想要的宽度，比如180px、250px等 */
    min-width: 220px !important;
    max-width: 220px !important;
                

        .stSidebar > div:first-child {
            padding-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    # 侧边栏设计
    with st.sidebar:
        if st.session_state.user_email:
            st.success(f"👤 当前登录用户：{st.session_state.user_email}")
            if(st.session_state.user_type == 0):
                st.sidebar.info("👋 伴学灵宝-云端AI课件")            
                st.sidebar.page_link("app.py", label="🔒 首页")
                st.sidebar.page_link("pages/1_课程讲义学习_课程知识搜集.py", label="📘 课程讲义学习")
                st.sidebar.page_link("pages/2_讲义知识学伴_AI教学设计.py", label="📖 讲义知识理解")
                st.sidebar.page_link("pages/3_讲义练习辅导_课堂游戏资源.py", label="🧠 讲义练习辅导")
                st.sidebar.page_link("pages/4_课堂任务完成_发布课堂任务.py", label="✅ 课堂任务完成")
                st.sidebar.page_link("pages/5_自行选择训练_试卷批改.py", label="📝 自行选择训练")
                st.sidebar.page_link("pages/6_个人学情查询_班级数据管理.py", label="📊 个人学情查询")

            else:
                st.sidebar.info("👋 伴学灵宝-云端AI课件")            
                st.sidebar.page_link("app.py", label="🔒 首页")
                st.sidebar.page_link("pages/1_课程讲义学习_课程知识搜集.py", label="📘 课程知识搜集")
                st.sidebar.page_link("pages/2_讲义知识学伴_AI教学设计.py", label="📖 AI教学设计")
                st.sidebar.page_link("pages/3_讲义练习辅导_课堂游戏资源.py", label="🧠 课堂游戏资源")
                st.sidebar.page_link("pages/4_课堂任务完成_发布课堂任务.py", label="✅ 发布课堂任务")
                st.sidebar.page_link("pages/5_自行选择训练_试卷批改.py", label="📝 试卷批改")
                st.sidebar.page_link("pages/6_个人学情查询_班级数据管理.py", label="📊 班级数据管理")
            if st.button("🚪 退出登录"):
                logout_user()
                st.rerun()
        else:
            st.info("🔐 你还未登录，部分功能不可用")

    # 主页面内容区
        # 页面标题
    st.markdown("<h1 style='text-align: center; color: #3A6DD8;'>👋 欢迎来到 伴学灵宝--云端AI课件</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: grey;'>AI 赋能的教学辅助平台</h4>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding: 1rem; background-color: #f0f4ff; border-radius: 10px; margin-top: 1rem;'>
        🧠 本平台集成了 <strong>Agent</strong>、<strong>云存储</strong>、<strong>大模型</strong>功能，
        为教师提供强大教学辅助，为学生打造智能化,个性化学习体验。
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.user_email:
        st.success("✅ 已成功登录，可以开始使用平台的全部功能啦！")
        st.markdown("""
    <div style="background-color: #f0f4ff; padding: 1.5rem; border-radius: 12px; margin-top: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">

    <h3>🧑‍🎓 学生端功能说明</h3>
    <ul style="line-height: 1.8;">
        <li>📘 支持 <strong>课堂讲义智能分析</strong>，快速抓住知识重点</li>
        <li>🧠 自动生成 <strong>思维导图</strong>，构建清晰知识网络</li>
        <li>🎮 提供 <strong>游戏化AI辅导</strong>，提升知识点理解乐趣</li>
        <li>📊 结合个体学习情况，<strong>精准分析学习盲点</strong></li>
        <li>🧩 提供 <strong>定制化练习题</strong>，根据薄弱点个性推荐</li>
    </ul>

    <hr style="margin: 1.5rem 0;">

    <h3>👩‍🏫 教师端功能说明</h3>
    <ul style="line-height: 1.8;">
        <li>📚 <strong>查阅知识库</strong>、完善知识点体系</li>
        <li>📝 快速生成 <strong>教学设计</strong> 与 <strong>教学PPT</strong></li>
        <li>🕹️ 获取 <strong>趣味教学小游戏</strong>，活跃课堂氛围</li>
        <li>🧑‍🏫 进行 <strong>班级管理</strong>，掌握学生参与情况</li>
        <li>📈 分析 <strong>班级整体学习数据</strong>，精准教学</li>
        <li>📝 <strong>在线批改作业与试卷</strong>，提升效率</li>
    </ul>

    </div>
    """, unsafe_allow_html=True)
    else:
        col1, col2 = st.columns([5, 1])

        with col1:
            st.warning("⚠️ 请先登录，才能使用全部功能")
        


        
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


        # 登录 / 注册 Tab 页面
        tab1, tab2 = st.tabs(["🔐 登录", "📝 注册"])

        with tab1:
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader("欢迎回来 👋")
                st.caption("请输入你的学号以登录")

                email = st.text_input("📧 学号", key="login_email")
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

                email = st.text_input("📧 学号", key="register_email")

                user_type = st.radio("选择用户类型",
                                    options=["学生", "老师"],
                                    index=0,
                                    format_func=lambda x: f"{'👨‍🎓' if x == '学生' else '👨‍🏫'} {x}",
                                    horizontal=True)

                # 如果是学生，显示班级选择
                class_id = None
                if user_type == "学生":
                    class_id = st.number_input("班级ID", min_value=1, step=1, value=1)  # 默认值设为1

                if st.button("注册"):
                    type_value = 0 if user_type == "学生" else 1
                    if register_user(email, type_value, int(class_id) if user_type == "学生" else None):
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
    main()
