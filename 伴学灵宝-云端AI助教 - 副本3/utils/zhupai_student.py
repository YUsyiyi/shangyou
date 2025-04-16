import streamlit as st
import requests
import json
# 初始化 API 配置
api_key = "a4a7572ba1c04768af82efc0697939ad.VFd64APkbdGmiXzb"
botid = "1905241995522240512"
baseUrl = 'https://open.bigmodel.cn/api/llm-application/open/v3/application/invoke'
headers = {
    "Authorization": f"{api_key}",
    'Content-Type': 'application/json'
}

# 使用统一的对话历史变量
if "message_name" not in st.session_state:
    st.session_state.message_name = []

# 为了方便书写, 给 st.session_state.message_name 起个短别名
message1 = st.session_state.message_name

def process_question_answer(response_data):
    # 如果 response_data['choices'][0]['index'] 为 True, 则认为返回异常
    if response_data['choices'][0]['index']:
        return f"应答异常：{response_data['msg']}"
    else:
        return response_data['choices'][0]['messages']['content']['msg']

def question_service(question_text):
    """
    question_text: 这里建议直接传入用户输入的纯文本，如 "你好"
    """

    # 构建消息历史列表以发送给后端
    messages = []
    for msg in message1:
        messages.append({
            "role": msg["role"],
            "content": [{
                "key": "query" if msg["role"] == "user" else "response",
                "value": msg["content"],
                "type": "input" if msg["role"] == "user" else "output"
            }]
        })
    
    # 添加当前用户问题
    messages.append({
        "role": "user",
        "content": [{
            "key": "query",
            "value": question_text,
            "type": "input"
        }]
    })

    data = {
        "app_id": botid,
        "user_id": "roxy",
        "stream": False,
        "messages": messages
    }

    # 向后端 AI 接口发送请求
    response = requests.post(baseUrl, headers=headers, data=json.dumps(data))
    
    # === 以下这部分才是往前端展示的对话写入 ===
    if response.status_code == 200:
        response_data = response.json()
        answer = process_question_answer(response_data)
        # （1）记录用户发送
        message1.append({"role": "user", "content": question_text})
        # （2）记录 AI 回复
        message1.append({"role": "assistant", "content": answer})
        return answer
    else:
        error_msg = f"请求失败，状态码: {response.status_code}\n错误信息: {response.text}"
        message1.append({"role": "system", "content": error_msg})
        return error_msg

def display_chat_history():
    """
    仅做对话显示 & 采集输入，不在此处追加对话历史，避免重复
    """
    # 遍历展示所有对话记录
    for msg in message1:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        elif msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])
        else:
            st.error(msg["content"])

    # 通用聊天输入
    user_input = st.chat_input("从这里开始! 请输入您的问题...", key="user_input1")
    if user_input:
        with st.spinner("思考中..."):
            # 仅调用后端服务并等待回复，不再额外 append
            # 如果需要传更多上下文，可以自己拼接, 但要注意别在前端多次append
            response = question_service(user_input)  
        # 重新渲染以显示最新消息
        st.rerun()


