import streamlit as st
from utils.db_operations import create_test_table, add_test_record, get_student_tests, get_all_users_data_new
import contextlib
import traceback
import base64
import io
from utils.coze_task_guide import get_coze_response as get_coze_response_task_guide
def show():
    if 'user_email' not in st.session_state or not st.session_state.user_email:
        st.warning("请先登录！")
        return

    # Ensure test table exists
    create_test_table()

    if st.session_state.user_type == 0:  # Student view
        st.sidebar.info("🌈 伴学灵宝-云端AI助教")
        st.sidebar.page_link("app.py", label="🏠 首页")
        st.sidebar.page_link("pages/1_课程讲义学习_课程知识搜集.py", label="📚 课程讲义学习")
        st.sidebar.page_link("pages/2_讲义知识学伴_AI教学设计.py", label="🎓 讲义知识理解")
        st.sidebar.page_link("pages/3_讲义练习辅导_课堂游戏资源.py", label="🎮 讲义练习辅导")
        st.sidebar.page_link("pages/4_课堂任务完成_发布课堂任务.py", label="✨ 课堂任务完成")
        st.sidebar.page_link("pages/5_自行选择训练_试卷批改.py", label="✏️ 自行选择训练")
        st.sidebar.page_link("pages/6_个人学情查询_班级数据管理.py", label="📈 个人学情查询")
        st.markdown("""
<div style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); 
            padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 6px 16px rgba(255,152,0,0.2);
            border-left: 5px solid #ff9800;
            transition: transform 0.3s ease;">
    <h3 style="color: #e65100; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">💻 完成课堂任务</h3>
    <p style="font-size: 0.95rem; color: #bf360c;">🎯 选择老师下达的题目,完成训练,可以使用AI辅助噢!</p>
</div>
""", unsafe_allow_html=True)   
        st.header("我的任务:")
        tests = get_student_tests(st.session_state.user_email)
        if not tests:
            st.info("目前没有测试题目")
        else:
            for i,test in enumerate(tests,start=1):
                with st.expander(f"来自 {test['teacher_email']} 的题目"):
                    st.write(test['question'])
                code_key = f"session_code_q{i}"
                run_key = f"session_run_q{i}"
                output_key = f"session_output_q{i}"

                default_code = "# 在这里编写你的代码"

                code = st.text_area(" ", value=default_code, height=200, key=code_key)

                col1, col2, col3, col4 = st.columns(4)

                if col1.button("▶ 运行代码", key=run_key):
                    st.subheader("💡 输出结果：")
                    try:
                        with contextlib.redirect_stdout(io.StringIO()) as f:
                            with contextlib.redirect_stderr(f):
                                exec(code, {})
                        output = f.getvalue()
                        st.session_state[output_key] = output
                        st.code(output)
                    except Exception:
                        st.session_state[output_key] = traceback.format_exc()
                        st.error("❌ 运行出错：")
                        st.code(st.session_state[output_key])

                elif output_key in st.session_state:
                    st.subheader("💡 运行结果：")
                    st.code(st.session_state[output_key])

                if col2.button(f"🧠AI辅导--题目 {i}"):
                    solution = st.session_state[code_key]
                    data = {
                        "题目": test["question"],
                        "学生代码": solution
                    }
                    with st.spinner("⏳ 正在获取指导，请稍候..."):
                        guide = get_coze_response_task_guide(str(data))
                        combined_answers = "\n\n".join([f"• {a}" for a in guide['answers']])

                    with st.expander("🧠 AI 辅导建议（点击展开）"):
                        st.markdown(
                            f"<div style='font-size: 14px; line-height: 1.6;'>{combined_answers.replace(chr(10), '<br>')}</div>",
                            unsafe_allow_html=True
                        )
                                


    elif st.session_state.user_type == 1:  # Teacher view

        st.sidebar.info("🌈 伴学灵宝-云端AI助教")            
        st.sidebar.page_link("app.py", label="🏠 首页")
        st.sidebar.page_link("pages/1_课程讲义学习_课程知识搜集.py", label="📚 课程知识搜集")
        st.sidebar.page_link("pages/2_讲义知识学伴_AI教学设计.py", label="🎓 AI教学设计")
        st.sidebar.page_link("pages/3_讲义练习辅导_课堂游戏资源.py", label="🎮 课堂游戏资源")
        st.sidebar.page_link("pages/4_课堂任务完成_发布课堂任务.py", label="✨ 发布课堂任务")
        st.sidebar.page_link("pages/5_自行选择训练_试卷批改.py", label="✏️ 试卷批改")
        st.sidebar.page_link("pages/6_个人学情查询_班级数据管理.py", label="📈 班级数据管理")          
        st.markdown("""
<div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
            padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 6px 16px rgba(76,175,80,0.2);
            border-left: 5px solid #4caf50;
            transition: transform 0.3s ease;">
    <h3 style="color: #2e7d32; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">💻 发布课堂任务</h3>
    <p style="font-size: 0.95rem; color: #1b5e20;">📤 输入题目,就可以发送给所有学生噢</p>
</div>
""", unsafe_allow_html=True)   
        question = st.text_area("输入题目内容")
        student_emails = get_all_users_data_new()
        print(student_emails)
        if student_emails:
            # 显示选择框并获取单个邮箱
            selected_email = st.selectbox("查看所有学生", student_emails)
            
            # 若后续代码需要保持列表结构（比如需要批量处理）
            # selected_emails = [selected_email]
        else:
            st.warning("没有找到符合条件的学生")
        suc=True
        if st.button("📤 向所有学生发布题目"):
            if question:
                for email in student_emails:
                    success = add_test_record(
                        student_email=email,
                        question=question,
                        teacher_email=st.session_state.user_email
                    )
                    if success:
                       print(1)
                    else:
                        st.error(f"发布题目给 {email} 失败")
                        suc=False
            if suc:
                st.success("向所有学生发布题目成功")
            else:
                st.warning("请输入题目内容")
        else:
            st.info("目前没有学生账户")

if __name__ == "__main__":
    show()
