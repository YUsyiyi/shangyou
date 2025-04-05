import streamlit as st
from datetime import datetime
import json
from upload_file import generate_coze_data  # 生成请求数据
from utils.coze_test_correct import CozeChatAPI  # 扣子智能体API

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

# 聊天记录显示
st.markdown('<div class="chat-history">', unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    role = msg["role"]
    text = msg["text"]
    timestamp = msg.get("timestamp", "")

    author_class = "user-author" if role == "user" else "bot-author"
    author_name = "我" if role == "user" else "扣子智能体"

    st.markdown(f"""
    <div class="message-item">
        <div class="message-author {author_class}">
            {author_name}
            <span class="message-timestamp">{timestamp}</span>
        </div>
        <div class="message-content">{text}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 底部输入区域
st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_text = st.text_area("有问题，尽管问… (Shift+Enter换行)",
                             placeholder="请输入你的文本...",
                             height=70,
                             key="user_input_text2")
    st.markdown('</div>', unsafe_allow_html=True)

    submitted = st.form_submit_button("发送", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)  # chat-input-area

# ------------------ 处理提交逻辑 ------------------
if submitted:
    if not user_text.strip():
        st.warning("⚠️ 请输入文本后再发送！")
    else:
        try:
            # 保存用户消息到会话
            user_msg = {
                "role": "user",
                "text": user_text,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.chat_history.append(user_msg)

            # 写入 output.json 以便后续 generate_coze_data 使用
            output_data = {"user_text": user_text}
            with open("output.json", "w") as f:
                json.dump(output_data, f)

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

            # 处理API返回
            if 'answers' in api_result:
                for answer in api_result['answers']:
                    bot_msg = {
                        "role": "bot",
                        "text": answer,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.chat_history.append(bot_msg)
            else:
                st.session_state.chat_history.append({
                    "role": "bot",
                    "text": f"API错误: {api_result.get('error', '未知错误')}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            st.rerun()

        except Exception as e:
            st.error(f"处理过程中发生错误：{str(e)}")

st.markdown('</div>', unsafe_allow_html=True)  # main-container 结束
