import streamlit as st
import streamlit.components.v1 as components
from utils.coze_teacher_game import get_coze_response as get_coze_response2
import json
from utils.Two_chat import chat
from utils.zhupai_student import display_chat_history

def show():
        if 'user_email' not in st.session_state or not st.session_state.user_email:
            st.warning("请先登录！")
            return
        if 'selected_answer' not in st.session_state:
            st.session_state.selected_answer = None
        if st.session_state.user_type == 0:
            st.sidebar.info("🌈 伴学灵宝-云端AI助教")
            st.sidebar.page_link("app.py", label="🏠 首页")
            st.sidebar.page_link("pages/1_课程讲义学习_课程知识搜集.py", label="📚 课程讲义学习")
            st.sidebar.page_link("pages/2_讲义知识学伴_AI教学设计.py", label="🎓 讲义知识理解")
            st.sidebar.page_link("pages/3_讲义练习辅导_课堂游戏资源.py", label="🎮 讲义练习辅导")
            st.sidebar.page_link("pages/4_课堂任务完成_发布课堂任务.py", label="✨ 课堂任务完成")
            st.sidebar.page_link("pages/5_自行选择训练_试卷批改.py", label="✏️ 自行选择训练")
            st.sidebar.page_link("pages/6_个人学情查询_班级数据管理.py", label="📈 个人学情查询")
            st.markdown("""
<div style="background: linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%); 
            padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 6px 16px rgba(255,152,0,0.2);
            border-left: 5px solid #ff9800;
            transition: transform 0.3s ease;">
    <h3 style="color: #e65100; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">🎲 AI知识点游戏</h3>
    <p style="font-size: 0.95rem; color: #bf360c;">🎯 这个工具允许您通过上传难懂的,需操作的知识点(如汉诺塔递归),生成游戏网页,您可以在课堂上使用此工具帮助你更快地理解知识点。</p>
</div>
""", unsafe_allow_html=True) 
            knowledge_input = st.text_input(" ", placeholder="请输入要生成游戏的知识点",key="first")
            game_submit = st.button("🎮 生成游戏")
            if game_submit and knowledge_input:
                with st.spinner("🔄 正在生成游戏代码..."):
                    result= get_coze_response2(knowledge_input)
                    html_content = json.loads(result['answers'][0])
                    html_content=html_content.get("code")
                    components.html(html_content, height=700)
            st.markdown("""
<div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
            padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 6px 16px rgba(76,175,80,0.2);
            border-left: 5px solid #4caf50;
            transition: transform 0.3s ease;">
    <h3 style="color: #2e7d32; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">👩‍🏫 AI知识点辅导</h3>
    <p style="font-size: 0.95rem; color: #1b5e20;">💬 这个工具允许您通过上传难懂的知识点,通过与定制智能体交流,帮助您在课堂上使用此工具帮助你更快地理解知识点。</p>
</div>
""", unsafe_allow_html=True) 
            display_chat_history()


        if st.session_state.user_type == 1:
            st.sidebar.info("🌈 伴学灵宝-云端AI助教")            
            st.sidebar.page_link("app.py", label="🏠 首页")
            st.sidebar.page_link("pages/1_课程讲义学习_课程知识搜集.py", label="📚 课程知识搜集")
            st.sidebar.page_link("pages/2_讲义知识学伴_AI教学设计.py", label="🎓 AI教学设计")
            st.sidebar.page_link("pages/3_讲义练习辅导_课堂游戏资源.py", label="🎮 课堂游戏资源")
            st.sidebar.page_link("pages/4_课堂任务完成_发布课堂任务.py", label="✨ 发布课堂任务")
            st.sidebar.page_link("pages/5_自行选择训练_试卷批改.py", label="✏️ 试卷批改")
            st.sidebar.page_link("pages/6_个人学情查询_班级数据管理.py", label="📈 班级数据管理")                            
            st.markdown("""
<div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
            padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 6px 16px rgba(33,150,243,0.2);
            border-left: 5px solid #2196f3;
            transition: transform 0.3s ease;">
    <h3 style="color: #0d47a1; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">📚 教学设计助手</h3>
    <p style="font-size: 0.95rem; color: #1565c0;">✨ 用于教师的教学设计支持，帮助生成个性化的教学PPT和优化教学内容</p>
</div>
""", unsafe_allow_html=True)
            st.markdown("### 🎯 教学设计流程：👇")
            st.table([
                ["1. 与AI进行对话", "获取教学设计建议"],
                ["2. 选择最佳设计方案", "生成PPT讲义"],
                ["3. 查看PPT缩略图", "快速调整内容"]
            ])
            
            st.markdown("""
            ### 💡 提示：✨
            通过与AI的合作，您可以大幅提升教学设计效率，节省时间，轻松创建高质量的课堂资料。
            """)
            st.markdown("---")
            chat("message2","coze2")

               
if __name__ == "__main__":
    show()
