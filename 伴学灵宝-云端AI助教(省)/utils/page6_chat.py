import streamlit as st
import json
from utils.coze_file import CozeChatAPI

def chat(message_name, coze_name):
    answer = ""
    if coze_name not in st.session_state:
        st.session_state.coze_name = CozeChatAPI(
            api_key="pat_YIYDDe70PzCmnZrK30PhZI2HND1xBanYMc2hdhEFDyQvskVvHTc4mIxPv3h06H3P",
            bot_id="7493364670683283506"
        )

        # 初始化对话历史
        if message_name not in st.session_state:
            st.session_state.message_name = []
            message = st.session_state.message_name

        # 显示历史消息
        for msg in message:
            with st.chat_message(msg["role"], avatar=msg.get("avatar")):
                st.markdown(msg["content"])

        # 用户输入处理
        if prompt := st.chat_input("请输入您的问题..."):
            # 添加用户消息
            message.append({"role": "user", "content": prompt, "avatar": "👤"})
            combine_prompt = {
                                    "题目": prompt,
                                    "代码": " ",
                                    "指令": prompt
                                            }
            with st.chat_message("user", avatar="👤"):
                st.markdown(str(combine_prompt))

            # 获取机器人响应
            with st.spinner("正在思考中，请稍候..."):
                response = st.session_state.coze_api.get_response(
                    question=prompt,
                    conversation_id=st.session_state.get('conversation_id')
                )

            # 处理响应
            if response.get('error'):
                error_msg = f"⚠️ 系统错误: {response['error']}"
                message.append({"role": "assistant", "content": error_msg, "avatar": "🤖"})
                with st.chat_message("assistant", avatar="🤖"):
                    st.error(error_msg)
            else:
                # 更新会话ID
                if response['conversation_id']:
                    st.session_state.conversation_id = response['conversation_id']

                # 显示回答
                if response['answers']:
                    answer = "\n\n".join(response['answers'])
                    index = len(message)  # 当前回答的索引

                    # 添加消息到历史
                    message.append({
                        "role": "assistant",
                        "content": answer,
                        "avatar": "🤖"
                    })

                    # 显示机器人消息
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(answer)

                # 显示追问建议
                if response['follow_ups']:
                    st.divider()
                    st.subheader("推荐追问")

                    cols = st.columns(2)
                    for i, question in enumerate(response['follow_ups'][:4]):
                        with cols[i % 2]:
                            if st.button(question, key=f"follow_up_{i}"):
                                # 自动填入问题
                                message.append({"role": "user", "content": question, "avatar": "👤"})
    return answer
