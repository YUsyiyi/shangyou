import streamlit as st
import streamlit.components.v1 as components
from streamlit.components.v1 import html
from utils.file_handler import save_uploaded_file
from utils.ai_processor import generate_lecture_notes
from utils.coze_knowchat import  get_coze_response,display_response
import os
import re
import requests
from datetime import datetime
import json
from upload_file import generate_coze_data  # 新增导入
from utils.coze_file import CozeChatAPI  # 新增导入
from utils.db_operations import get_user_data, update_blind_spots, update_com_level, get_know_com,update_learning_progress,get_user_type
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
def save_uploaded_file(uploaded_file):
    """保存上传的文件到指定目录"""
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path
def coze_upload_file(file_path):
    """调用Coze文件上传API"""
    url = "https://api.coze.cn/v1/files/upload"
    headers = {
        "Authorization": "Bearer pat_yPgDslmEycjg3h67cLVr9cVj8bxi01tQ5BCjfedRMmNqppkkl1ULqGXhGQYDP5bu"########################################################
    }

    try:
        with open(file_path, 'rb') as f:
            file_type = 'application/octet-stream'
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_type = 'image/jpeg'
            elif file_path.lower().endswith('.pdf'):
                file_type = 'application/pdf'

            files = {'file': (os.path.basename(file_path), f, file_type)}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response
    except Exception as e:
        raise RuntimeError(f"文件上传失败: {str(e)}")

def show():
        if 'user_email' not in st.session_state or not st.session_state.user_email:
            st.warning("请先登录！")
            return
        print(st.session_state.user_type)#获取用户类型
        if st.session_state.user_type == 0:
            with st.sidebar:
                st.title("伴学灵宝-云端AI助教")
                st.page_link("app.py", label="注销")
                st.page_link("pages/1_Begin.py", label="课程讲义学习")
                st.page_link("pages/2_Two.py", label="讲义知识理解")
                st.page_link("pages/3_Three.py", label="讲义练习辅导")
                st.page_link("pages/4_Four.py", label="个人学情查询")
                st.page_link("pages/5_Five.py", label="未知")
            st.markdown("""
<div style="background-color: #f0f8ff; padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
    <h3 style="color: #1a4d8f;">🧑‍🏫AI讲义分析</h3>
    <p style="font-size: 0.95rem; color: #333;">这个工具允许您通过上传课程讲义,生成思维导图,知识点,重难点分析,学习资源推荐,练习题.您可以在课堂上使用此工具帮助你更快地理解知识点。</p>
</div>
""", unsafe_allow_html=True)         
            uploaded_file = st.file_uploader("选择文件", type=["txt", "csv", "pdf", "docx", "jpg", "png","pptx"])
            user_text = get_know_com(st.session_state.user_email)
            submitted = st.button("提交您的讲义")  # 改为普通按钮

            if submitted:
                if uploaded_file and user_text:
                    try:
                        # 第一阶段：文件保存和上传
                        saved_path = save_uploaded_file(uploaded_file)
                        st.success(f"文件保存成功：{saved_path}")

                        with st.spinner("正在上传文件到Coze..."):
                            response = coze_upload_file(saved_path)

                        # 生成output.json
                        data = response.json()
                        b = data['data']['id']
                        output_data = {"file_id": b, "user_text": user_text}
                        with open("output.json", "w") as f:
                            json.dump(output_data, f)

                        # 第二阶段：生成请求数据并调用API
                        with st.spinner("生成请求参数..."):
                            request_data = generate_coze_data()
                            if not request_data:
                                raise ValueError("生成请求参数失败")

                        # 初始化API客户端
                        coze_api = CozeChatAPI(
                            api_key="pat_yPgDslmEycjg3h67cLVr9cVj8bxi01tQ5BCjfedRMmNqppkkl1ULqGXhGQYDP5bu",
                            bot_id="7487520074652368911"
                        )

                        # 第三阶段：调用聊天API并显示结果
                        with st.spinner("正在获取AI响应..."):
                            api_result = coze_api.ask_question(request_data)
                        st.subheader("AI助教反馈")
                        print(api_result)
                        if 'answers' in api_result:
                            answers = json.loads(api_result['answers'][0])
                            st.session_state.answers = json.loads(api_result['answers'][0])                     
                            if 'pic' in answers and answers['pic']:
                                st.markdown("### 思维导图展示!:")
                                st.image(answers['pic'], caption="分析图示", use_container_width=True)
                        if 'answers' in st.session_state:
                            answers = st.session_state.answers
                            # 分栏布局
                            t1, t2 = st.columns(2)
                            with t1:
                                st.subheader("📌 关键知识点")
                                st.write(answers['knowledge_points'])
                                st.subheader("⚠️ 难点解析")
                                st.write(answers['difficult_points'])


                            with t2:
                                # st.subheader("📈 计算思维分析")
                                # st.write(answers['com_analysis'])
                                st.subheader("🎯 重点内容")
                                st.write(answers['key_points'])
                            # 解析学习网址
                            if 'url_title' in answers:
                                st.subheader("📚 相关学习资源")
                                
                                with st.expander("点击展开学习资源 📖"):
                                    for item in answers['url_title']:
                                        try:
                                        
                                            st.markdown(f"🔗{item}")
                                        except ValueError:
                                            continue  # 防止解析错误

                            # 叠加卡片式内容
                            st.subheader("📖 知识掌握情况")
                            st.write(answers['know_analysis'])
                            st.markdown("### ✅ 已掌握的知识:")
                            st.success("\n".join([f"- {item}" for item in answers['know_level']]))
                            success=update_learning_progress(st.session_state.user_email, answers['know_level'])
                            print(success)
                            
                            # 练习题目
                            st.subheader("📖 知识点练习题")
                            selected_question = None  # 变量存储当前选中的题目

                            # 遍历题目列表
                            for i, question in enumerate(answers['output'], 1):
                                with st.container():  # 使用容器分隔不同的题目
                                    exercise_for_std=f"**Exercise:** {question}"
                                    st.session_state[f"exercise_{i}"]=exercise_for_std 
                                    st.write(f"**Exercise {i}:** {question}")  # 显示完整题目
                            st.subheader("💡 学习建议")
                            st.info(answers['advise'])

                            # 结束
                            st.markdown("---")
                            st.write("👨‍🏫 **AI 助教提供个性化学习方案，助你提升编程能力！**")
                            
                        else:
                            st.error(f"API错误: {api_result.get('error', '未知错误')}")

                    except Exception as e:
                        st.error(f"处理过程中发生错误：{str(e)}")
                else:
                    st.warning("⚠️ 请上传文件后再提交！")
        if st.session_state.user_type == 1:
            with st.sidebar:
                st.title("伴学灵宝-云端AI助教")
                st.page_link("app.py", label="注销")
                st.page_link("pages/1_Begin.py", label="课程知识搜集")
                st.page_link("pages/2_Two.py", label="AI教学设计")
                st.page_link("pages/3_Three.py", label="游戏资源设计")
                st.page_link("pages/4_Four.py", label="班级数据管理")
                st.page_link("pages/5_Five.py", label="试卷批改")                     
                # Knowledge input section
            st.markdown("""
<div style="background-color: #f0f8ff; padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
    <h3 style="color: #1a4d8f;">📚 教学资料采集区</h3>
    <p style="font-size: 0.95rem; color: #333;">请粘贴您上课所讲的知识点，系统将根据教材内容,智能提取有效信息，辅助生成完整知识点。</p>
</div>
""", unsafe_allow_html=True)

            # 分离输入框样式
            st.markdown("### ✏️ 输入知识点内容")
            knowledge = st.text_area("例如：递归、for循环……", height=180, label_visibility="collapsed")

            st.markdown("<br>", unsafe_allow_html=True)

            # 美化按钮（伪 hover）
            button_css = """
                <style>
                div.stButton > button {
                    background-color: #4a90e2;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0.5rem 1.5rem;
                    font-size: 1rem;
                    transition: 0.3s ease;
                }
                div.stButton > button:hover {
                    background-color: #357ABD;
                    transform: scale(1.02);
                }
                </style>
            """
            st.markdown(button_css, unsafe_allow_html=True)

            if st.button("🚀 获取智能数据", use_container_width=True):
                if knowledge.strip():
                    with st.spinner("🤖 正在生成教学内容，请稍候..."):
                        # result = get_coze_response(knowledge)
                        display_response(knowledge)
                else:
                    st.warning("⚠️ 请输入知识点内容后再提交")




if __name__ == "__main__":
    show()