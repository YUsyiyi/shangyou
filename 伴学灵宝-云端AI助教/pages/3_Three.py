import streamlit as st
from utils.ai_processor import get_problem_help, grade_solution
from utils.zhupai_student import question_service
from utils.db_operations import get_user_data2, get_know_com
from utils.coze_ppt_generate import get_coze_response
import json
import streamlit.components.v1 as components
import os
import requests
from utils.coze_file import CozeChatAPI  # 新增导入
from upload_file import generate_coze_data  # 新增导入

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
    <h3 style="color: #1a4d8f;">🧑‍🏫AI练习辅导</h3>
    <p style="font-size: 0.95rem; color: #333;">这个工具将展示来自课程讲义的题目,你可以在此进行题目练习(不仅是来自讲义),随后使用AI进行批阅</p>
</div>
""", unsafe_allow_html=True)         
        # 获取练习题（假设已存在 session 中）
        exercise_keys = [k for k in st.session_state.keys() if k.startswith("exercise_")]
        if exercise_keys:
            st.subheader("📘 当前练习题")

            for i, key in enumerate(sorted(exercise_keys), 1):
                question = st.session_state[key]  # 直接是 "**Exercise:** xxx" 格式的字符串
                with st.container():
                    st.markdown(f"**题目 {i}:** {question}")
                    st.text_input("你的答案：", key=f"answer_input_{i}")

                    if st.button(f"问AI这道题", key=f"ask_ai_btn_{i}"):
                        if 'chat_history' not in st.session_state:
                            st.session_state.chat_history = []

                        # 提问内容为纯题目文本
                        raw_q = question.replace("**Exercise:**", "").strip()
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": f"请帮我理解这道题：{raw_q}"
                        })

                        student = get_user_data2(st.session_state.user_email)
                        with st.spinner("思考中..."):
                            combined_data = {
                                "prompt": f"请帮我理解这道题：{raw_q}",
                                "students_data": student
                            }
                            response = question_service(str(combined_data))
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": response
                            })
                        st.rerun()

        st.divider()

        # 聊天记录展示
        st.subheader("🤖 AI交流区")
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            elif msg["role"] == "assistant":
                st.chat_message("assistant").write(msg["content"])
            else:
                st.error(msg["content"])

        # 通用聊天输入
        user_input = st.chat_input("请输入您的问题...", key="user_input1")
        if user_input:
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            student = get_user_data2(st.session_state.user_email)
            with st.spinner("思考中..."):
                combined_data = {
                    "prompt": user_input,
                    "students_data": student
                }
                response = question_service(str(combined_data))
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
            st.rerun()

    if st.session_state.user_type == 1:
            with st.sidebar:
                st.title("伴学灵宝-云端AI助教")
                st.page_link("app.py", label="注销")
                st.page_link("pages/1_Begin.py", label="课程知识搜集")
                st.page_link("pages/2_Two.py", label="AI教学设计")
                st.page_link("pages/3_Three.py", label="游戏资源设计")
                st.page_link("pages/4_Four.py", label="班级数据管理")
                st.page_link("pages/5_Five.py", label="试卷批改")   
            st.markdown("""
<div style="background-color: #f0f8ff; padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
    <h3 style="color: #1a4d8f;">🧑‍🏫 点名游戏生成器</h3>
    <p style="font-size: 0.95rem; color: #333;">这个工具允许您通过上传班级名单文件（如：Excel、CSV等），
            系统将自动生成一个点名游戏，您可以在课堂上使用这个游戏提高学生参与度。</p>
</div>
""", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("选择文件", type=["txt", "csv", "pdf", "docx", "jpg", "png","pptx","xlsx"])
            user_text = "."
            submitted = st.button("提交班级名单表") 
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
                                bot_id="7489751691873943552"
                            )

                            # 第三阶段：调用聊天API并显示结果
                            with st.spinner("正在获取AI响应..."):
                                api_result = coze_api.ask_question(request_data)    
                                print(api_result)
                                html_content = json.loads(api_result['answers'][0])       
                                html_content=html_content.get("code")
                                components.html(html_content, height=700)

                        except Exception as e:
                            st.error(f"处理过程中发生错误：{str(e)}")
if __name__ == "__main__":
    show()
