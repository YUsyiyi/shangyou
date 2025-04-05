import streamlit as st
import os
import requests
from datetime import datetime
import json
from upload_file import generate_coze_data  # 生成请求数据
from utils.coze_test_correct import CozeChatAPI  # 扣子智能体API
# from utils.coze_test_correct import coze_upload_file


# ------------------ 创建/检查上传目录 ------------------
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def coze_upload_file(file_path):
    """调用Coze文件上传API"""
    url = "https://api.coze.cn/v1/files/upload"
    headers = {
        "Authorization": "Bearer pat_yPgDslmEycjg3h67cLVr9cVj8bxi01tQ5BCjfedRMmNqppkkl1ULqGXhGQYDP5bu"
    }
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response
    except Exception as e:
        raise RuntimeError(f"文件上传失败: {str(e)}")

def save_uploaded_file(uploaded_file):
    """保存上传的文件到指定目录"""
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# ------------------ 初始化聊天记录 ------------------
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ------------------ 顶部导航栏（示例） ------------------
st.markdown("""
<div class="top-bar">
    <div class="title">扣子智能体聊天</div>
    <a class="back-link" href="#">回到</a>
</div>
""", unsafe_allow_html=True)

# ------------------ 主容器 ------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# 问候语
st.markdown(
    '<div class="greeting-text">Hi~ 我是你的AI助手，可以为你解决疑惑、梳理文档、配合你工作，事半功倍</div>',
    unsafe_allow_html=True)

# 聊天记录
st.markdown('<div class="chat-history">', unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    role = msg["role"]
    text = msg["text"]
    timestamp = msg.get("timestamp", "")
    file_name = msg.get("file_name", None)

    # 用户 or 扣子
    if role == "user":
        author_class = "user-author"
        author_name = "我"
    else:
        author_class = "bot-author"
        author_name = "扣子智能体"

    # 消息块
    st.markdown(f"""
    <div class="message-item">
        <div class="message-author {author_class}">
            {author_name}
            <span class="message-timestamp">{timestamp}</span>
        </div>
        <div class="message-content">{text}</div>
    </div>
    """, unsafe_allow_html=True)

    # 如果用户上传了文件，则显示“文件卡片”
    if role == "user" and file_name:
        # 拼接出保存路径
        file_path = os.path.join(UPLOAD_DIR, file_name)
        if os.path.exists(file_path):
            # 获取文件大小并转为KB
            file_size_kb = os.path.getsize(file_path) / 1024
            file_size_str = f"{file_size_kb:.2f}KB"

            # 这里统一使用一个文件图标，如果想区分doc/pdf等可自行扩展
            file_icon_url = "https://cdn-icons-png.flaticon.com/512/337/337946.png"

            st.markdown(f"""
            <div class="file-attachment">
                <img class="file-attachment-icon" src="{file_icon_url}" alt="file icon" />
                <div class="file-info">
                    <div class="file-name">{file_name}</div>
                    <div class="file-size">{file_size_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 底部输入区域
st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    # 自定义输入容器
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_text = st.text_area("有问题，尽管问… (Shift+Enter换行)",
                             placeholder="请输入你的文本...",
                             height=70,
                             key="user_input_text2")
    st.markdown('</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "本次上传的文件（图片/文档等）",
        type=["jpg", "png", "jpeg", "pdf", "docx", "txt", "pptx", "xlsx", 'py', 'ppt'],
        key="user_input_file",
        help="支持常见文本/图片文件，请同时上传文件和输入文本"
    )

    submitted = st.form_submit_button("发送", use_container_width=True, on_click=None)

st.markdown('</div>', unsafe_allow_html=True)  # chat-input-area

# ------------------ 处理提交逻辑 ------------------
if submitted:
    if not uploaded_file or not user_text.strip():
        st.warning("⚠️ 请同时上传文件和输入文本后再发送！")
    else:
        try:
            # 保存并上传文件到Coze
            saved_path = save_uploaded_file(uploaded_file)
            with st.spinner("正在上传文件到Coze..."):
                response = coze_upload_file(saved_path)
            data = response.json()
            file_id = data['data']['id']

            # 写入 output.json
            output_data = {"file_id": file_id, "user_text": user_text}
            with open("output.json", "w") as f:
                json.dump(output_data, f)

            # 将用户消息保存到会话记录
            user_msg = {
                "role": "user",
                "text": user_text,
                "file_name": uploaded_file.name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.chat_history.append(user_msg)

            # 生成请求数据
            request_data = generate_coze_data()
            if not request_data:
                raise ValueError("生成请求参数失败")

            # 调用扣子智能体API
            coze_api = CozeChatAPI(
                api_key="pat_yPgDslmEycjg3h67cLVr9cVj8bxi01tQ5BCjfedRMmNqppkkl1ULqGXhGQYDP5bu",
                bot_id="7489797704949153842"
            )
            with st.spinner("正在获取扣子智能体的回复..."):
                api_result = coze_api.ask_question(request_data)

            # 处理API结果
            if 'answers' in api_result:
                for answer in api_result['answers']:
                    bot_msg = {
                        "role": "bot",
                        "text": answer,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.chat_history.append(bot_msg)
            else:
                error_text = f"API错误: {api_result.get('error', '未知错误')}"
                bot_msg = {
                    "role": "bot",
                    "text": error_text,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.chat_history.append(bot_msg)

            # 刷新页面
            st.rerun()

        except Exception as e:
            st.error(f"处理过程中发生错误：{str(e)}")

st.markdown('</div>', unsafe_allow_html=True)  # main-container 结束
