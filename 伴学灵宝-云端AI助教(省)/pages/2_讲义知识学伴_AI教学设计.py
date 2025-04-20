import streamlit as st
import streamlit.components.v1 as components
from utils.coze_teacher_game import get_coze_response as get_coze_response2
import json
from utils.Two_chat import chat
from utils.zhupai_student import display_chat_history
import requests
import time
class CozeChatAPI:
    def __init__(self, api_key, bot_id, timeout=8000):
        self.api_key = api_key
        self.bot_id = bot_id
        self.timeout = timeout
        self.base_url = 'https://api.coze.cn/v3/chat'
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            'Content-Type': 'application/json'
        }

    def _process_response(self, response_data):
        """处理API响应数据"""
        result = {
            'answers': [],
            'follow_ups': [],
            'conversation_id': None,
            'error': None
        }

        if response_data.get('code') != 0:
            result['error'] = response_data.get('msg', 'Unknown error')
            return result

        messages = response_data.get('data', [])
        if messages:
            result['conversation_id'] = messages[0].get('conversation_id')

            for msg in messages:
                if msg['type'] == 'answer':
                    result['answers'].append(msg['content'])
                elif msg['type'] == 'follow_up':
                    result['follow_ups'].append(msg['content'])

        return result

    def get_response(self, question, conversation_id=None):
        """获取聊天响应（包含重试机制）"""
        payload = {
            "bot_id": self.bot_id,
            "user_id": "streamlit_user",
            "stream": False,
            "auto_save_history": True,
            "additional_messages": [{
                "role": "user",
                "content": question,
                "content_type": "text"
            }]
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        try:
            # 创建初始请求
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            create_data = response.json()

            # 轮询结果
            chat_id = create_data['data']['id']
            conversation_id = create_data['data']['conversation_id']
            return self._poll_result(conversation_id, chat_id)

        except Exception as e:
            return {'error': str(e)}

    def _poll_result(self, conversation_id, chat_id):
        """轮询获取最终结果"""
        start_time = time.time()
        status_url = f"{self.base_url}/retrieve?conversation_id={conversation_id}&chat_id={chat_id}"

        while True:
            if time.time() - start_time > self.timeout:
                return {'error': f"Timeout after {self.timeout} seconds"}

            try:
                status_response = requests.get(status_url, headers=self.headers)
                status_data = status_response.json()

                if status_data['data']['status'] == 'completed':
                    message_url = f"{self.base_url}/message/list?chat_id={chat_id}&conversation_id={conversation_id}"
                    msg_response = requests.get(message_url, headers=self.headers)
                    return self._process_response(msg_response.json())

                time.sleep(1)
            except Exception as e:
                return {'error': str(e)}

# class CozeChatAPI:
#     def __init__(self, api_key, bot_id, timeout=8000):
#         self.api_key = api_key
#         self.bot_id = bot_id
#         self.timeout = timeout
#         self.base_url = 'https://api.coze.cn/v3/chat'
#         self.headers = {
#             "Authorization": f"Bearer {api_key}",
#             'Content-Type': 'application/json'
#         }

#     def _process_response(self, response_data):
#         """处理API响应数据"""
#         result = {
#             'answers': [],
#             'follow_ups': [],
#             'conversation_id': None,
#             'error': None
#         }

#         if response_data.get('code') != 0:
#             result['error'] = response_data.get('msg', 'Unknown error')
#             return result

#         messages = response_data.get('data', [])
#         if messages:
#             result['conversation_id'] = messages[0].get('conversation_id')

#             for msg in messages:
#                 if msg['type'] == 'answer':
#                     result['answers'].append(msg['content'])
#                 elif msg['type'] == 'follow_up':
#                     result['follow_ups'].append(msg['content'])

#         return result

#     def get_response(self, question, conversation_id=None):
#         """获取聊天响应（包含重试机制）"""
#         payload = {
#             "bot_id": self.bot_id,
#             "user_id": "streamlit_user",
#             "stream": False,
#             "auto_save_history": True,
#             "additional_messages": [{
#                 "role": "user",
#                 "content": question,
#                 "content_type": "text"
#             }]
#         }

#         if conversation_id:
#             payload["conversation_id"] = conversation_id

#         try:
#             # 创建初始请求
#             response = requests.post(
#                 self.base_url,
#                 headers=self.headers,
#                 data=json.dumps(payload)
#             )
#             response.raise_for_status()
#             create_data = response.json()

#             # 轮询结果
#             chat_id = create_data['data']['id']
#             conversation_id = create_data['data']['conversation_id']
#             return self._poll_result(conversation_id, chat_id)

#         except Exception as e:
#             return {'error': str(e)}

#     def _poll_result(self, conversation_id, chat_id):
#         """轮询获取最终结果"""
#         start_time = time.time()
#         status_url = f"{self.base_url}/retrieve?conversation_id={conversation_id}&chat_id={chat_id}"

#         while True:
#             if time.time() - start_time > self.timeout:
#                 return {'error': f"Timeout after {self.timeout} seconds"}

#             try:
#                 status_response = requests.get(status_url, headers=self.headers)
#                 status_data = status_response.json()

#                 if status_data['data']['status'] == 'completed':
#                     message_url = f"{self.base_url}/message/list?chat_id={chat_id}&conversation_id={conversation_id}"
#                     msg_response = requests.get(message_url, headers=self.headers)
#                     return self._process_response(msg_response.json())

#                 time.sleep(1)
#             except Exception as e:
#                 return {'error': str(e)}

def show():
        if 'user_email' not in st.session_state or not st.session_state.user_email:
            st.warning("请先登录！")
            return
        if 'selected_answer' not in st.session_state:
            st.session_state.selected_answer = None
        if st.session_state.user_type == 0:
            st.sidebar.info("🌈 伴学灵宝-云端AI课件")
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
    <p style="font-size: 0.95rem; color: #bf360c;">🎯 这个工具允许您通过上传难懂的,需操作的知识点,生成游戏网页,您可以在课堂上使用此工具帮助你更快地理解知识点。</p>
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
            st.markdown("---")
            # display_chat_history()

            if 'coze_api_v2' not in st.session_state:
                st.session_state.coze_api_v2 = CozeChatAPI(
                    api_key="pat_YIYDDe70PzCmnZrK30PhZI2HND1xBanYMc2hdhEFDyQvskVvHTc4mIxPv3h06H3P",
                    bot_id="7495217318852198410"
                )

            # 初始化对话历史
            if 'messages_v2' not in st.session_state:
                st.session_state.messages_v2 = []

            # 显示历史消息
            for msg in st.session_state.messages_v2:
                with st.chat_message(msg["role"], avatar=msg.get("avatar")):
                    st.markdown(msg["content"])

            # 用户输入处理
            if prompt := st.chat_input("请输入您的问题..."):
                # 添加用户消息
                st.session_state.messages_v2.append({"role": "user", "content": prompt, "avatar": "👤"})

                with st.chat_message("user", avatar="👤"):
                    st.markdown(prompt)

                # 获取机器人响应
                with st.spinner("正在思考中，请稍候..."):
                    response = st.session_state.coze_api_v2.get_response(
                        question=prompt,
                        conversation_id=st.session_state.get('conversation_id_v2')
                    )

                # 处理响应
                if response.get('error'):
                    error_msg = f"⚠️ 系统错误: {response['error']}"
                    st.session_state.messages_v2.append({"role": "assistant", "content": error_msg, "avatar": "🦜"})
                    with st.chat_message("assistant", avatar="🦜"):
                        st.error(error_msg)
                else:
                    # 更新会话ID
                    if response['conversation_id']:
                        st.session_state.conversation_id_v2 = response['conversation_id']

                    # 显示回答
                    if response['answers']:
                        answer = "\n\n".join(response['answers'])

                        # 添加消息到历史
                        st.session_state.messages_v2.append({
                            "role": "assistant",
                            "content": answer,
                            "avatar": "🦜"
                        })
                        # 显示追问建议
                        if response['follow_ups']:
                            st.divider()
                            st.subheader("推荐追问")

                            cols = st.columns(2)
                            for i, question in enumerate(response['follow_ups'][:4]):
                                with cols[i % 2]:
                                    if st.button(question, key=f"follow_up_v2_{i}"):
                                        # 自动填入问题
                                        st.session_state.messages_v2.append({"role": "user", "content": question, "avatar": "👤"})

            # 显示最新消息（确保API响应立即显示）
            if st.session_state.messages_v2 and st.session_state.messages_v2[-1]["role"] == "assistant":
                last_msg = st.session_state.messages_v2[-1]
                with st.chat_message(last_msg["role"], avatar=last_msg.get("avatar")):
                    st.markdown(last_msg["content"])



        if st.session_state.user_type == 1:
            st.sidebar.info("🌈 伴学灵宝-云端AI课件")            
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
            st.divider()
            st.markdown("### 🧠 教学设计流程：👇")
            st.markdown("""
<style>
    .dataframe {
        background-color: #f0f8ff !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,105,204,0.2) !important;
    }
    .dataframe th {
        background-color: #1e90ff !important;
        color: white !important;
        font-weight: bold !important;
    }
    .dataframe tr:nth-child(even) {
        background-color: #e6f2ff !important;
    }
    .dataframe td {
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)
            st.table([
                ["1. 🗣️ 与AI进行对话", "📝 获取教学设计建议"],
                ["2. 🏆 选择最佳设计方案", "📚 获取最佳讲义"],
            ])
            st.markdown("---")
            # display_chat_history()

            if 'coze_api_v3' not in st.session_state:
                st.session_state.coze_api_v3 = CozeChatAPI(
                    api_key="pat_YIYDDe70PzCmnZrK30PhZI2HND1xBanYMc2hdhEFDyQvskVvHTc4mIxPv3h06H3P",
                    bot_id="7489797704949153842"
                )

            # 初始化对话历史
            if 'messages_v3' not in st.session_state:
                st.session_state.messages_v3 = []

            # 显示历史消息
            st.markdown("""
<style>
    .stChatMessage {
        border-radius: 16px !important;
        padding: 16px !important;
        margin: 12px 0 !important;
    }
    .stChatMessage.user {
        background-color: #e6f2ff !important;
        border-left: 4px solid #1e90ff !important;
    }
    .stChatMessage.assistant {
        background-color: #f0f8ff !important;
        border-left: 4px solid #4682b4 !important;
    }
    .stChatMessage .avatar {
        background-color: #1e90ff !important;
        color: white !important;
    }
    .stTextInput>div>div>input {
        border-radius: 12px !important;
        border: 1px solid #1e90ff !important;
    }
    .stButton>button {
        background-color: #1e90ff !important;
        color: white !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

            for msg in st.session_state.messages_v3:
                avatar = "🪔" if msg["role"] == "user" else "🌌"
                with st.chat_message(msg["role"], avatar=avatar):
                    content = msg["content"]
                    # 为消息内容添加emoji前缀
                    if msg["role"] == "user":
                        content = f"💬 {content}"
                    else:
                        content = f"📚 {content}"
                    

            # 用户输入处理
            if prompt := st.chat_input("请输入您的问题..."):
                # 添加用户消息
                st.session_state.messages_v3.append({"role": "user", "content": prompt, "avatar": "🪔"})

                with st.chat_message("user", avatar="🪔"):
                    st.markdown(prompt)

                # 获取机器人响应
                with st.spinner("正在思考中，请稍候..."):
                    response = st.session_state.coze_api_v3.get_response(
                        question=prompt,
                        conversation_id=st.session_state.get('conversation_id_v3')
                    )

                # 处理响应
                if response.get('error'):
                    error_msg = f"⚠️ 系统错误: {response['error']}"
                    st.session_state.messages_v3.append({"role": "assistant", "content": error_msg, "avatar": "🌌"})
                    with st.chat_message("assistant", avatar="🌌"):
                        st.error(error_msg)
                else:
                    # 更新会话ID
                    if response['conversation_id']:
                        st.session_state.conversation_id_v3 = response['conversation_id']

                    # 显示回答
                    if response['answers']:
                        answer = "\n\n".join(response['answers'])

                        # 添加消息到历史
                        st.session_state.messages_v3.append({
                            "role": "assistant",
                            "content": answer,
                            "avatar": "🌌"
                        })
                        # 显示追问建议
                        if response['follow_ups']:
                            st.divider()
                            st.subheader("推荐追问")

                            cols = st.columns(2)
                            for i, question in enumerate(response['follow_ups'][:4]):
                                with cols[i % 2]:
                                    if st.button(question, key=f"follow_up_v3_{i}"):
                                        # 自动填入问题
                                        st.session_state.messages_v3.append({"role": "user", "content": question, "avatar": "🪔"})

            # 显示最新消息（确保API响应立即显示）
            if st.session_state.messages_v3 and st.session_state.messages_v3[-1]["role"] == "assistant":
                last_msg = st.session_state.messages_v3[-1]
                with st.chat_message(last_msg["role"], avatar=last_msg.get("avatar")):
                    st.markdown(last_msg["content"])
            

if __name__ == "__main__":
    show()
