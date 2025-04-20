import streamlit as st
import requests
import json

# 初始化API配置
api_key = "a4a7572ba1c04768af82efc0697939ad.VFd64APkbdGmiXzb"
botid = "1907379412639318016"
baseUrl = 'https://open.bigmodel.cn/api/llm-application/open/v3/application/invoke'
headers = {
    "Authorization": f"{api_key}",
    'Content-Type': 'application/json'
}

def process_question_answer(response_data):
    if response_data['choices'][0]['index']:
        return f"应答异常：{response_data['msg']}"
    else:
        return response_data['choices'][0]['messages']['content']['msg']

def question_service(question_text):
    # 构建消息历史
    messages = []
    for msg in st.session_state.chat_history:
        messages.append({
            "role": msg["role"],
            "content": [{
                "key": "query" if msg["role"] == "user" else "response",
                "value": msg["content"],
                "type": "input" if msg["role"] == "user" else "output"
            }]
        })
    
    # 添加当前问题
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

    # 发送请求
    response = requests.post(baseUrl, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        response_data = response.json()
        answer = process_question_answer(response_data)
        
        # 更新对话历史
        st.session_state.chat_history.append({"role": "user", "content": question_text})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        
        return answer
    else:
        error_msg = f"请求失败，状态码: {response.status_code}\n错误信息: {response.text}"
        st.session_state.chat_history.append({"role": "system", "content": error_msg})
        return error_msg
