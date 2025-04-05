import streamlit as st
from utils.ai_processor import get_problem_help, grade_solution
from utils.zhupai_student import question_service
from utils.db_operations import get_all_users_data, get_user_data2, update_blind_spots, update_com_level, update_learning_progress,generate_raw_summary
def show():
    with st.sidebar:
        st.title("🎓 AI Teaching Assistant")
        st.page_link("app.py", label="🏠 首页")
        st.page_link("pages/1_📚_Lecture_Generator.py", label="📚 AI讲义生成")
        st.page_link("pages/2_✏_Problem_Tutor.py", label="✏ AI做题辅导")
        st.page_link("pages/3_📊_Learning_Analysis.py", label="📊 我的学情")
    st.title("✏ 24h学伴")
    
    if 'user_email' not in st.session_state or not st.session_state.user_email:
        st.warning("Please login first!")
        return

    # # Problem input section
    # if 'current_exercise' in st.session_state:
    #     problem = st.text_area("Problem", value=st.session_state.current_exercise)
    # else:
    #     problem = st.text_area("Enter your problem")

    # col1, col2 = st.columns(2)
    
    # with col1:
    #     # Problem help section
    #     if problem:
    #         st.subheader("Get Help")
    #         hint_level = st.select_slider(
    #             "Hint Level",
    #             options=["Just the Answer", "Basic Hint", "Detailed Explanation", "Step-by-Step Solution"]
    #         )
            
    #         if st.button("Get Help"):
    #             with st.spinner("Generating help..."):
    #                 help_text = get_problem_help(problem, hint_level)
    #                 st.write(help_text)
    
    # with col2:
    #     # Problem grading section
    #     if problem:
    #         st.subheader("Submit Solution")
    #         solution = st.text_area("Your Solution")
            
    #         if st.button("Grade Solution"):
    #             with st.spinner("Grading..."):
    #                 feedback = grade_solution(problem, solution)
    #                 st.write(feedback)
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        elif msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])
        else:
            st.error(msg["content"])

    # 用户输入

    user_input = st.chat_input("请输入您的问题...",key="user_input1")
    if user_input:
        student=get_user_data2(st.session_state.user_email)
        with st.spinner("思考中..."):
            combined_data = {
                "prompt": user_input,
                "students_data": student  # 直接使用从数据库获取的原始数据
            }
            response = question_service(str(combined_data))
            # 重新渲染以显示最新消息
            st.rerun()
if __name__ == "__main__":
    show()