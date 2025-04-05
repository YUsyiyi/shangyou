import streamlit as st
from utils.coze_ppt_generate import get_coze_response
import json
import requests
import re
import os 
def show():
    
    user_input = st.text_area("请输入知识点", height=100)

    # 按钮
    if st.button("提交"):

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