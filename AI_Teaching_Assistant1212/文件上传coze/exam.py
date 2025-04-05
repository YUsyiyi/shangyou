# 修改后的exam.py
import streamlit as st
import os
import requests
from datetime import datetime
import json
from upload_file import generate_coze_data  # 新增导入
from app1 import CozeChatAPI  # 新增导入

# 创建上传目录
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


# 页面布局
st.title("📁 文件与文本联合上传器")
st.markdown("---")

with st.form("upload_form"):
    uploaded_file = st.file_uploader("选择文件", type=["txt", "csv", "pdf", "docx", "jpg", "png","pptx"])
    user_text = st.text_area("输入文本", placeholder="在这里输入你的文本...")
    submitted = st.form_submit_button("提交全部内容")

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
                bot_id="7487520074652368911"
            )

            # 第三阶段：调用聊天API并显示结果
            with st.spinner("正在获取AI响应..."):
                api_result = coze_api.ask_question(request_data)

            # 显示处理结果
            st.subheader("本地处理结果")
            processing_result = {
                "file_name": os.path.basename(saved_path),
                "file_size": f"{os.path.getsize(saved_path) / 1024:.2f} KB",
                "text_length": len(user_text),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            col1, col2 = st.columns(2)
            with col1:
                st.metric("文件名", processing_result["file_name"])
                st.metric("文件大小", processing_result["file_size"])
            with col2:
                st.metric("文本长度", processing_result["text_length"])
                st.metric("处理时间", processing_result["timestamp"])

            # 显示API响应结果
            st.subheader("AI响应结果")
            if 'answers' in api_result:
                for i, answer in enumerate(api_result['answers'], 1):
                    with st.expander(f"回答 {i}"):
                        st.markdown(answer)

                if api_result['follow_ups']:
                    st.divider()
                    st.subheader("后续建议问题")
                    for question in api_result['follow_ups']:
                        st.caption(f"• {question}")
            else:
                st.error(f"API错误: {api_result.get('error', '未知错误')}")

        except Exception as e:
            st.error(f"处理过程中发生错误：{str(e)}")
    else:
        st.warning("⚠️ 请同时上传文件和输入文本后再提交！")