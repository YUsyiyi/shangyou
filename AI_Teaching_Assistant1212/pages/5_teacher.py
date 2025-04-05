import streamlit as st
from utils.ai_processor import get_problem_help, grade_solution
from utils.zhupai_teacher import question_service
from datetime import datetime
from utils.db_operations import get_all_users_data, get_user_data, update_blind_spots, update_com_level, update_learning_progress,generate_raw_summary
def show():
    all_users = get_all_users_data()
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False

    

    if not all_users:
        st.warning("无可用学生数据")
    else:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("数据总览")
            if not st.session_state.report_generated:
                if st.button("生成完整报告"):
                    st.session_state.raw_report = generate_raw_summary(all_users)
                    st.session_state.report_generated = True
                    st.rerun()
            else:
                st.text_area("完整报告", 
                            value=st.session_state.raw_report,
                            height=600)
        
        with col2:
            if st.session_state.report_generated:
                st.download_button(
                    label="下载报告",
                    data=st.session_state.raw_report,
                    file_name="students_report.txt",
                    mime="text/plain",
                    key="unique_download_key"
                )
                st.success("报告已就绪")
                
                st.metric("总学生数", len(all_users))
                st.caption(f"生成时间：{datetime.now().strftime('%H:%M:%S')}")
                
                if st.button("重新生成"):
                    st.session_state.report_generated = False
                    st.rerun()
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
    user_input2 = st.chat_input("请输入您的问题...",key="user_input2")
    if user_input2:
        with st.spinner("思考中..."):
            combined_data = {
                "prompt": user_input2,
                "students_data": all_users  # 直接使用从数据库获取的原始数据
            }
            response = question_service(combined_data)
            # 重新渲染以显示最新消息
            st.rerun()
    
if __name__ == "__main__":
    show()