import streamlit as st
from utils.auth import logout_user
st.set_page_config(
    page_title="AI Teaching Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    with st.sidebar:
        st.title("🎓 AI Teaching Assistant")
        st.page_link("app.py", label="🏠 首页")
        st.page_link("pages/1_📚_Lecture_Generator.py", label="📚 AI讲义生成")
        st.page_link("pages/2_✏_Problem_Tutor.py", label="✏ AI做题辅导") 
        st.page_link("pages/3_📊_Learning_Analysis.py", label="📊 我的学情")
        st.page_link("pages/4_💡_Knowledge_Guide.py", label="💡 知识点指导")
        if st.session_state.user_email:
            st.write(f"Logged in as: {st.session_state.user_email}")
            if st.button("Logout"):
                logout_user()
                st.rerun()
            
            st.divider()
            
            st.page_link("app.py", label="🏠 首页")
            st.page_link("pages/1_📚_Lecture_Generator.py", label="📚 AI讲义生成")
            st.page_link("pages/2_✏_Problem_Tutor.py", label="✏ AI做题辅导")
            st.page_link("pages/3_📊_Learning_Analysis.py", label="📊 我的学情")
            st.page_link("pages/4_💡_Knowledge_Guide.py", label="💡 知识点指导")
        else:
            st.info("Please login to access all features")

    # Main content area
    if st.session_state.user_email:
        st.success(f"Welcome back, {st.session_state.user_email}!")
        st.write("Navigate to different features using the sidebar.")
    else:
        st.warning("Please login to access the teaching assistant features")

if __name__ == "__main__":
    main()
