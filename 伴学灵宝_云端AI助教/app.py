import streamlit as st
from utils.auth import logout_user

def main():
    # 初始化 session
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None

    # 页面基础设置
    st.set_page_config(
        page_title="伴学灵宝 - 云端AI助教",
        page_icon="🎓",
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
            if st.button("🚪 退出登录"):
                logout_user()
                st.rerun()
        else:
            st.info("🔐 你还未登录，部分功能不可用")

    # 主页面内容区

    st.markdown("## 👋 欢迎来到 **伴学灵宝--云端AI助教**")
    st.markdown("### 一个专为编程学习设计的 AI 教学助手平台")

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


if __name__ == "__main__":
    main()
