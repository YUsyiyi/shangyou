import streamlit as st
import streamlit as st
import streamlit as st
from utils.coze_ppt_generate import get_coze_response
import json
from utils.coze_file import CozeChatAPI  
import streamlit as st
import json

def chat(message_name,coze_name):
    if coze_name not in st.session_state:
        st.session_state.coze_name = CozeChatAPI(
            api_key="pat_YIYDDe70PzCmnZrK30PhZI2HND1xBanYMc2hdhEFDyQvskVvHTc4mIxPv3h06H3P",
            bot_id="7489797704949153842"
        )

        # 初始化对话历史
        if message_name not in st.session_state:
            st.session_state.message_name = []
            message=st.session_state.message_name

        # 显示历史消息
        for msg in message:
            with st.chat_message(msg["role"], avatar=msg.get("avatar")):
                st.markdown(msg["content"])

        # 用户输入处理
        if prompt := st.chat_input("请输入您的问题..."):
            # 添加用户消息
            message.append({"role": "user", "content": prompt, "avatar": "👤"})

            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            # 获取机器人响应
            with st.spinner("正在思考中，请稍候..."):
                response = st.session_state.coze_name.get_response(
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

                    # # 显示机器人消息和选择选项
                    # with st.chat_message("assistant", avatar="🤖"):
                    #     st.markdown(answer)
                    #     if st.radio(
                    #         "选择此回答",
                    #         [f"回答 {index+1}"],
                    #         key=f"select_answer_{index}",
                    #         index=None
                    #     ):
                    #         st.session_state.selected_answer = answer
                    #         st.success(f"✅ 已选择回答 {index+1}")
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
        #     # 按钮
        # if st.button("提交"):
        #         if 'selected_answer' not in st.session_state or not st.session_state.selected_answer:
        #             st.warning("请先选择一个回答！")
        #             return
        #         user_input = st.session_state.selected_answer
        #         print(user_input)
        #         with st.spinner("思考中..."):
        #             response = get_coze_response(str(user_input))
        #             try:
        #                 parsed_response = json.loads(response['answers'][0])
        #                 st.session_state.ppt = parsed_response.get("ppt", " ")
        #                 print(st.session_state.ppt )
        #                 # 提取所有缩略图链接
        #                 st.session_state.thumbnails = [
        #                     pic["thumbnail"] for pic in parsed_response.get("pic", [])
        #                 ]
        #                 print(st.session_state.thumbnails)
        #             except (KeyError, IndexError, json.JSONDecodeError) as e:
        #                 print(f"解析出错: {e}")
        #                 st.session_state.ppt = " "
        #                 st.session_state.thumbnails = []
        #             if "ppt" in st.session_state and st.session_state.ppt.strip():
        #                 st.markdown(f"📥 [点击下载 PPT]( {st.session_state.ppt} )", unsafe_allow_html=True)

        #             # 展示 PPT 缩略图（可折叠）
        #             if "thumbnails" in st.session_state and st.session_state.thumbnails:
        #                 with st.expander("📂 展示 PPT 预览缩略图"):
        #                     for index, thumbnail in enumerate(st.session_state.thumbnails):
        #                         st.image(thumbnail, caption=f"第 {index + 1} 页", use_container_width=True)    
        #             # 重新渲染以显示最新消息
                                    