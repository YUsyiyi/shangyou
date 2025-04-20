import streamlit as st
import random

# 定义一个函数来生成唯一的 text_input 组件
def custom_text_input(label: str, placeholder: str, key_prefix: str):
    # 生成唯一的 key，确保每次调用都会有不同的 key
    unique_key = f"{key_prefix}_{random.randint(1, 10000)}"
    return st.text_input(label, placeholder=placeholder, key=unique_key)

# 在应用中使用这个函数
if st.button("点击获取输入框"):
    # 调用自定义的函数生成 text_input 组件
    user_input = custom_text_input("请输入你的疑问", "在这里输入", "page66")
    
    if user_input:
        st.session_state.por = user_input  # 将输入的值存储在 session_state 中
        st.write(f"你输入的内容是: {user_input}")
