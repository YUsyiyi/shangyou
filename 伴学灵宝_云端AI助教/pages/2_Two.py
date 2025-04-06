import streamlit as st
from utils.db_operations import get_user_data
import streamlit as st
from utils.coze_knowguide import display_response
import streamlit as st
import streamlit.components.v1 as components
from utils.coze_teacher_game import get_coze_response as get_coze_response2
from utils.coze_ppt_generate import get_coze_response
import os
import re
import requests
from datetime import datetime
import json
from upload_file import generate_coze_data  # 新增导入
from utils.coze_file import CozeChatAPI  # 新增导入
import streamlit as st
import requests
import json
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
    <h3 style="color: #1a4d8f;">🧑‍🏫AI知识点解答</h3>
    <p style="font-size: 0.95rem; color: #333;">您通过上传难懂的知识点,AI将调用网络数据和教材数据,合并最好的解答给您。</p>
</div>
""", unsafe_allow_html=True)           
            knowledge  = st.text_area("请输入您想了解的知识点", height=150)
            
            if st.button("获取指导"):
                if knowledge:
                        user_data = get_user_data(st.session_state.user_email)
                        if not user_data:
                            st.error("无法加载用户数据！")
                            return
                        if 'com_level' not in st.session_state:
                            com_level = user_data.get('com_level', '0分')

                        if 'learning_progress' not in st.session_state:
                            learning_progress = user_data.get('learning_progress', [])
                        
                        if 'blind_spots' not in st.session_state:
                            blind_spots = user_data.get('blind_spots', [])
                            combined_data = {
                                                "know_level": learning_progress,
                                                "com_level": com_level,
                                                "blind_spot": blind_spots,
                                                "knowledge": knowledge
                                            }
                            print(combined_data)
                        with st.spinner("正在生成指导..."):
                            display_response(str(combined_data))
                else:
                    st.warning("请输入知识点内容")
            st.markdown("""
<div style="background-color: #f0f8ff; padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
    <h3 style="color: #1a4d8f;">🧑‍🏫AI知识点游戏</h3>
    <p style="font-size: 0.95rem; color: #333;">这个工具允许您通过上传难懂的,需操作的知识点(如汉诺塔递归),生成游戏网页,您可以在课堂上使用此工具帮助你更快地理解知识点。</p>
</div>
""", unsafe_allow_html=True) 
            st.subheader("🎮 知识点游戏生成")
            knowledge_input = st.text_input("输入知识点", placeholder="请输入要生成游戏的知识点",key="first")
            game_submit = st.button("生成游戏")
            if game_submit and knowledge_input:
                with st.spinner("正在生成游戏代码..."):
                    result= get_coze_response2(knowledge_input)
                    html_content = json.loads(result['answers'][0])
                    html_content=html_content.get("code")
                    components.html(html_content, height=700)
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
    <h3 style="color: #1a4d8f;">📚 教学设计助手</h3>
    <p style="font-size: 0.95rem; color: #333;">用于教师的教学设计支持，帮助生成个性化的教学PPT和优化教学内容</p>
</div>
""", unsafe_allow_html=True)
            # 添加文字说明
            # 使用表格展示流程
            st.markdown("### 🎯 教学设计流程：")
            st.table([
                ["1. 与AI进行对话", "获取教学设计建议"],
                ["2. 选择最佳设计方案", "生成PPT讲义"],
                ["3. 查看PPT缩略图", "快速调整内容"]
            ])
            
            st.markdown("""
            ### 💡 提示：
            通过与AI的合作，您可以大幅提升教学设计效率，节省时间，轻松创建高质量的课堂资料。
            """)
            st.markdown("---")
            # 初始化API实例
            if 'coze_api' not in st.session_state:
                st.session_state.coze_api = CozeChatAPI(
                    api_key="pat_yPgDslmEycjg3h67cLVr9cVj8bxi01tQ5BCjfedRMmNqppkkl1ULqGXhGQYDP5bu",
                    bot_id="7489797704949153842"
                )

            # 初始化对话历史
            if 'messages' not in st.session_state:
                st.session_state.messages = []

            # 显示历史消息
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar=msg.get("avatar")):
                    st.markdown(msg["content"])

            # 用户输入处理
            if prompt := st.chat_input("请输入您的问题..."):
                # 添加用户消息
                st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "👤"})

                with st.chat_message("user", avatar="👤"):
                    st.markdown(prompt)

                # 获取机器人响应
                with st.spinner("正在思考中，请稍候..."):
                    response = st.session_state.coze_api.get_response(
                        question=prompt,
                        conversation_id=st.session_state.get('conversation_id')
                    )

                # 处理响应
                if response.get('error'):
                    error_msg = f"⚠️ 系统错误: {response['error']}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg, "avatar": "🤖"})
                    with st.chat_message("assistant", avatar="🤖"):
                        st.error(error_msg)
                else:
                    # 更新会话ID
                    if response['conversation_id']:
                        st.session_state.conversation_id = response['conversation_id']

                    # 显示回答
                    if response['answers']:
                        answer = "\n\n".join(response['answers'])
                        index = len(st.session_state.messages)  # 当前回答的索引

                        # 添加消息到历史
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "avatar": "🤖"
                        })

                        # 显示机器人消息和“选中”按钮
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(answer)
                            if st.button("✅ 选中此回答", key=f"select_answer_{index}"):
                                st.session_state.selected_answer = answer
                                st.success("✅ 已保存该回答！")
                    # 显示追问建议
                    if response['follow_ups']:
                        st.divider()
                        st.subheader("推荐追问")

                        cols = st.columns(2)
                        for i, question in enumerate(response['follow_ups'][:4]):
                            with cols[i % 2]:
                                if st.button(question, key=f"follow_up_{i}"):
                                    # 自动填入问题
                                    st.session_state.messages.append({"role": "user", "content": question, "avatar": "👤"})
                # 按钮
                if st.button("提交") and "selected_answer" in st.session_state:
                    user_input = st.session_state.selected_answer


                    with st.spinner("思考中..."):
                        response = get_coze_response(user_input)
                        try:
                            parsed_response = json.loads(response['answers'][0])
                            st.session_state.ppt = parsed_response.get("ppt", " ")
                            print(st.session_state.ppt )
                            # 提取所有缩略图链接
                            st.session_state.thumbnails = [
                                pic["thumbnail"] for pic in parsed_response.get("pic", [])
                            ]
                            print(st.session_state.thumbnails)
                        except (KeyError, IndexError, json.JSONDecodeError) as e:
                            print(f"解析出错: {e}")
                            st.session_state.ppt = " "
                            st.session_state.thumbnails = []
                        if "ppt" in st.session_state and st.session_state.ppt.strip():
                            st.markdown(f"📥 [点击下载 PPT]( {st.session_state.ppt} )", unsafe_allow_html=True)

                        # 展示 PPT 缩略图（可折叠）
                        if "thumbnails" in st.session_state and st.session_state.thumbnails:
                            with st.expander("📂 展示 PPT 预览缩略图"):
                                for index, thumbnail in enumerate(st.session_state.thumbnails):
                                    st.image(thumbnail, caption=f"第 {index + 1} 页", use_container_width=True)    
                        # 重新渲染以显示最新消息
                                                        

               
if __name__ == "__main__":
    show()