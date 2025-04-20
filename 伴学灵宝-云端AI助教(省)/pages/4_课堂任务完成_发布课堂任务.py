import streamlit as st
from utils.db_operations import create_test_table, add_test_record, get_student_tests, get_all_users_data_new
import contextlib
import traceback
import base64
import io
from utils.coze_task_guide import get_coze_response as get_coze_response_task_guide
from cpp import get_class_test_records
from utils.coze_all_test_analysis import get_coze_response as get_coze_response_all_test_analysis
def show():
    if 'user_email' not in st.session_state or not st.session_state.user_email:
        st.warning("请先登录！")
        return

    # Ensure test table exists
    create_test_table()

    if st.session_state.user_type == 0:  # Student view
        st.sidebar.info("🌈 伴学灵宝-云端AI课件")
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
                por_key = f"session_por_{i}"
                analysis_key = f"session_analysis_{i}"                  

                if f"session_analysis_{i}" not in st.session_state:
                    st.session_state[f"session_analysis_{i}"] = "未使用AI进行批改"  # Default code
                if f"session_code_q{i}" not in st.session_state:
                    st.session_state[f"session_code_q{i}"] = "# "  # Default code

                code = st.text_area("🧿在此输入你的代码", value=st.session_state[f"session_code_q{i}"], height=200, key=code_key)

                # Update session state when the user modifies the code
                if code != st.session_state[f"session_code_q{i}"]:
                    st.session_state[f"session_code_q{i}"] = code


                    ##############################
                if f"session_por_{i}" not in st.session_state:
                    st.session_state[f"session_por_{i}"] = " "  # Default code

                por = st.text_area("🧿在此处与AI进行交流", value=st.session_state[f"session_por_{i}"], height=100, key=por_key)

                # Update session state when the user modifies the code
                if por != st.session_state[f"session_por_{i}"]:
                    st.session_state[f"session_por_{i}"] = por
                    ##############################


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
                        "学生代码": solution,
                        "指令":por
                    }
                    with st.spinner("⏳ 正🧿在获取指导，请稍候..."):
                        guide = get_coze_response_task_guide(str(data))
                        combined_answers = "\n\n".join([f"• {a}" for a in guide['answers']])
                        st.session_state[analysis_key] = combined_answers
                    with st.expander("🧠 AI 辅导建议（点击展开）"):
                        st.markdown(
                            f"<div style='font-size: 14px; line-height: 1.6;'>{combined_answers.replace(chr(10), '<br>')}</div>",
                            unsafe_allow_html=True
                        )
                                
                if col3.button(f"📨提交我的答案--题目 {i}"): 
                    title = test['question']
                    teacher_email = test['teacher_email']
                    analysis = st.session_state[analysis_key]
                    solution = st.session_state[code_key]
                    student_email = st.session_state.user_email
                    class_id = st.session_state.class_id
                    
                    from utils.db_operations import create_test_table2, add_test_record2
                    create_test_table2()
                    if add_test_record2(teacher_email, title, solution, student_email, analysis, class_id):
                        st.success("提交成功！")
                    else:
                        st.error("提交失败，请重试")

    elif st.session_state.user_type == 1:  # Teacher view

        st.sidebar.info("🌈 伴学灵宝-云端AI课件")            
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
        
        # 获取所有班级ID
        from utils.db_operations import get_all_classes
        class_ids = get_all_classes()
        
        if class_ids:
            selected_class = st.selectbox("选择班级", class_ids)
            
            # 获取该班级所有学生
            from utils.db_operations import get_class_students
            student_emails = get_class_students(selected_class)
            
            if student_emails:
                st.info(f"班级 {selected_class} 共有 {len(student_emails)} 名学生")
                
                suc = True
                if st.button(f"📤 向班级 {selected_class} 发布题目"):
                    if question:
                        for email in student_emails:
                            success = add_test_record(
                                student_email=email,
                                question=question,
                                teacher_email=st.session_state.user_email
                            )
                            if not success:
                                st.error(f"发布题目给 {email} 失败")
                                suc = False
                        if suc:
                            st.success(f"向班级 {selected_class} 发布题目成功")
                    else:
                        st.warning("请输入题目内容")
            else:
                st.warning(f"班级 {selected_class} 没有学生")
        else:
            st.warning("没有找到任何班级")
        st.divider()
        st.markdown("""
<div style="background: linear-gradient(135deg, #e8f5e9 0%,#9ACD32 100%); 
            padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 6px 16px rgba(76,175,80,0.2);
            border-left: 5px solid #4caf50;
            transition: transform 0.3s ease;">
    <h3 style="color: #2e7d32; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">🤔 查看学生作答</h3>
    <p style="font-size: 0.95rem; color: #1b5e20;">🛸 根据班级,查看作答情况,AI一键分析作答</p>
</div>
""", unsafe_allow_html=True)      
        st.divider()             
        if st.button("🔍 生成测试报告", type="primary"):
            teacher_email = st.session_state.user_email
            test_records = get_class_test_records(selected_class)
            test_records = test_records[test_records['teacher_email'] == teacher_email]
            
            if not test_records.empty:
                st.success(f"✅ 找到 {len(test_records)} 条测试记录")
                
                # 统计信息
                cols = st.columns(3)
                cols[0].metric("📝 题目数量", test_records['title'].nunique())
                cols[1].metric("👥 参与学生", test_records['student_email'].nunique())

                
                # 按题目分组
                grouped = test_records.groupby('title')
                result = []
                for title, group in grouped:
                    json_data = {
"题目": title,
"所有学生作答与批改": group['analysis'].tolist()
}
                    result.append(json_data)
                
                # 输出结果（可选择以下任意一种方式）
                # 1. 打印到控制台
                
                    with st.expander(f"📌 题目: {title}", expanded=False):
                        st.markdown(f"""
<div style="background: #e8f5e9; padding: 0.5rem; border-radius: 6px;">
<p>🏫 班级: {selected_class} | 👥 作答学生数: {len(group)}</p>
</div>
""", unsafe_allow_html=True)
                
                        # 显示学生作答情况
                        for _, row in group.iterrows():
                            with st.container(border=True):
                                cols = st.columns([1,4])
                                with cols[0]:
                                    st.markdown(f"**👤 学生**\n\n{row['student_email']}")
                                with cols[1]:
                                    st.markdown(f"**📝 作答分析**<br><span style='font-size: 16px;'>{row['analysis']}</span>", unsafe_allow_html=True)
                

                with st.spinner("⏳ 正🧿在获取指导，请稍候..."):
                        st.info("AI 分析班级学情")
                        all_analysis=get_coze_response_all_test_analysis(str(result))
                        combined_answers = "\n\n".join([f"• {a}" for a in all_analysis['answers']])
                        st.markdown(
                            f"""
                            <div style="
                                font-size: 16px;
                                line-height: 1.8;
                                color: #333;
                                font-family: 'Arial', sans-serif;
                                background-color: #9ACD32;
                                padding: 10px;
                                border-radius: 8px;
                                box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
                                white-space: pre-wrap;
                                word-wrap: break-word;
                            ">
                                {combined_answers.replace(chr(10), '<br>')}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                print(result)
            
            else:
                st.warning("🔍 没有找到相关测试记录")
if __name__ == "__main__":
    show()
