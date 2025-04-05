import streamlit as st
from utils.ai_processor import get_knowledge_guidance
from utils.coze_knowguide import  get_coze_response,display_response
# def display_response(result):
#     """显示API响应结果"""
#     if 'error' in result:
#         answers_str = f"出错: {result['error']}"
#         st.error(answers_str)
#     else:
#         # 显示答案
#         for answer in result['answers']:
#            st.write(answer)
     
def show():
    with st.sidebar:
        st.title("🎓 AI Teaching Assistant")
        st.page_link("app.py", label="🏠 首页")
        st.page_link("pages/1_📚_Lecture_Generator.py", label="📚 AI讲义生成") 
        st.page_link("pages/2_✏_Problem_Tutor.py", label="✏ AI做题辅导")
        st.page_link("pages/3_📊_Learning_Analysis.py", label="📊 我的学情")
        st.page_link("pages/4_💡_Knowledge_Guide.py", label="💡 知识点指导")
    
    st.title("💡 知识点指导")
    
    if 'user_email' not in st.session_state or not st.session_state.user_email:
        st.warning("请先登录!")
        return

    # Knowledge input section
    knowledge = st.text_area("请输入您想了解的知识点", height=150)
    
    if st.button("获取指导"):
        if knowledge:
            with st.spinner("正在生成指导..."):
                # result = get_coze_response(knowledge)
                display_response(knowledge)
        else:
            st.warning("请输入知识点内容")

if __name__ == "__main__":
    show()
