import streamlit as st
import json
from utils.ai_processor import generate_blindspot_exercises
from utils.coze_blind_solve import get_coze_response
from utils.auth import get_user_data
from utils.db_operations import get_all_users_data,generate_raw_summary,get_class_students,get_all_classes
from utils.db_operations import get_know_com_blind, get_know_com_blind_solve, update_blind_spots, update_com_level
from datetime import datetime
from utils.zhupai_teacher import question_service
from utils.coze_task_guide import get_coze_response as get_coze_response_task_guide
from utils.coze_get_class_guide import get_coze_response as get_coze_response_get_class_guide
from utils.page6_chat import chat
import contextlib
import traceback
import base64
import io
import pandas as pd
from pandas import DataFrame as df
import random
from utils.text_input import custom_text_input
from cpp import get_class_test_records
def show():
    if 'user_email' not in st.session_state or not st.session_state.user_email:
        st.warning("请先登录！")
        return

    if st.session_state.user_type == 0:
        st.sidebar.info("🌈 伴学灵宝-云端AI课件")
        st.sidebar.page_link("app.py", label="🏠 首页")
        st.sidebar.page_link("pages/1_课程讲义学习_课程知识搜集.py", label="📚 课程讲义学习")
        st.sidebar.page_link("pages/2_讲义知识学伴_AI教学设计.py", label="🎓 讲义知识理解")
        st.sidebar.page_link("pages/3_讲义练习辅导_课堂游戏资源.py", label="🎮 讲义练习辅导")
        st.sidebar.page_link("pages/4_课堂任务完成_发布课堂任务.py", label="✨ 课堂任务完成")
        st.sidebar.page_link("pages/5_自行选择训练_试卷批改.py", label="✏️ 自行选择训练")
        st.sidebar.page_link("pages/6_个人学情查询_班级数据管理.py", label="📈 个人学情查询")
        st.markdown("""
<div style="background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%); 
            padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 6px 16px rgba(0,188,212,0.2);
            border-left: 5px solid #00bcd4;
            transition: transform 0.3s ease;">
    <h3 style="color: #00838f; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">📱 AI学情分析</h3>
    <p style="font-size: 0.95rem; color: #006064;">📊 这个工具将展示个人学习情况,知识盲点;通过解决知识盲点的练习题,实现个性化学习需求</p>
</div>
""", unsafe_allow_html=True)         
        user_data = get_user_data(st.session_state.user_email)
        if not user_data:
            st.error("无法加载用户数据！")
            return


        # **将计算思维水平、学习进度、知识盲区存储为session变量**
        if 'com_level' not in st.session_state:
            st.session_state.com_level = user_data.get('com_level', '0分')

        if 'learning_progress' not in st.session_state:
            st.session_state.learning_progress = user_data.get('learning_progress', [])
        
        if 'blind_spots' not in st.session_state:
            st.session_state.blind_spots = user_data.get('blind_spots', [])

        # 显示班级信息
        if 'class_id' in st.session_state:
            st.header(f"🏫 所在班级: {st.session_state.class_id}", divider="blue")
        
        # **展示学习进度**
        st.header("📈 你的学习进度")
        # 计算思维等级评估
    #     score=int(st.session_state.com_level)
    #     # score = int(st.session_state.com_level.replace('分', '')) if '分' in st.session_state.com_level else 0
    #     if score <= 20:
    #         level_desc = "线性逻辑处理·基础模式识别"
    #     elif score <= 40:
    #         level_desc = "条件分支应用·嵌套结构认知"
    #     elif score <= 60:
    #         level_desc = "抽象模式迁移·动态条件处理" 
    #     elif score <= 80:
    #         level_desc = "并发任务协调·算法优化能力"
    #     else:
    #         level_desc = "元认知建模·跨域方案迁移"
    #     st.subheader(f"计算思维水平: {st.session_state.com_level} ({level_desc})")
        
    #     with st.expander("📊 计算思维等级评估标准"):
    #         st.markdown("""
    # | 分数 | 核心能力维度 | 行为观测指标 | 环境表现阈值 |
    # |------|--------------|--------------|--------------|
    # | 0-20分 | • 线性逻辑处理<br>• 基础模式识别 | • 单线程指令正确率≥70%<br>• 3步内路径规划成功率＞65%<br>• 循环结构误用率＞40% | 迷宫：固定起点-终点<br>画布：单对象操作 |
    # | 20-40分 | • 条件分支应用<br>• 嵌套结构认知 | • 双重条件语句正确率≥60%<br>• 2层嵌套结构实现率＞55%<br>• 路径冗余度下降30% | 迷宫：动态障碍物<br>画布：双对象交互 |
    # | 40-60分 | • 抽象模式迁移<br>• 动态条件处理 | • 跨环境方案复用率＞45%<br>• While循环正确中断率≥65%<br>• 函数调用准确率＞70% | 迷宫：多出口场景<br>画布：参数化绘图 |
    # | 60-80分 | • 并发任务协调<br>• 算法优化能力 | • 多线程冲突解决率＞60%<br>• 执行步骤精简度提升40%<br>• 边界条件覆盖率＞85% | 混合环境：迷宫+画布联动<br>多代理协同任务 |
    # | 80-100分 | • 元认知建模<br>• 跨域方案迁移 | • 非编程场景转化率＞50%<br>• 自定义函数复用价值度＞3次<br>• 异常预判准确率＞75% | 开放环境：自主定义问题<br>多模态交互场景 |
    #         """)

        # 美化已掌握知识点显示
        with st.container(border=True):
            st.subheader("✅ 已掌握知识点", divider="green")
            if not st.session_state.learning_progress:
                st.write("暂无已掌握知识点")
            else:
                cols = st.columns(2)
                for i, topic in enumerate(st.session_state.learning_progress):
                    with cols[i % 2]:
                        st.success(f"📚 {topic}")
        # 美化知识盲区显示
        st.header("⚠️ 知识盲区", divider="orange")
        blind_spots = st.session_state.get("blind_spots", [])

        # 添加新知识盲点
        with st.container(border=True):
            st.subheader("➕ 添加新知识盲点")
            new_blind_spot = st.text_input("输入你想要加强的知识点", key="new_blind_spot")
            if st.button("提交", key="add_blind_spot"):
                if new_blind_spot:
                    if new_blind_spot in blind_spots:
                        st.warning("该知识点已在你的盲点列表中")
                    else:
                        updated_spots = blind_spots + [new_blind_spot]
                        if update_blind_spots(st.session_state.user_email, updated_spots):
                            st.session_state.blind_spots = updated_spots
                            st.success(f"成功添加知识盲点: {new_blind_spot}")
                            st.rerun()
                        else:
                            st.error("添加失败，请稍后再试")
                else:
                    st.warning("请输入有效的知识点")

        # 显示现有知识盲点
        if not blind_spots:
            st.info("🎉 目前没有发现知识盲区！")
        else:
            for spot in blind_spots:
                with st.container(border=True):
                    cols = st.columns([4, 1])
                    with cols[0]:
                        st.error(f"🔴 {spot}")
                    with cols[1]:
                        if st.button(f"开始练习", key=f"solve_{spot}", type="primary"):
                            st.session_state.current_blindspot = spot
                            st.session_state.exercises = None  # 清空旧练习题
                            st.rerun()

        # 显示当前知识盲点的练习（如果已选择）
        if "current_blindspot" in st.session_state:
            current = st.session_state.current_blindspot
            st.subheader(f"🎯 当前知识盲区：{current}")

            # 如果还未获取练习题，先获取并缓存
            if st.session_state.get("exercises") is None:
                with st.spinner("⏳ 正在获取练习题，请稍候..."):
                    message = get_know_com_blind(st.session_state.user_email, current)
                    st.session_state.exercises = generate_blindspot_exercises(message)

            # 如果获取成功，显示题目
            if st.session_state.exercises:
                parsed_data = json.loads(st.session_state.exercises['answers'][0])
                questions = parsed_data["text"]
                reasons = parsed_data["reason"]

                for i, (question, reason) in enumerate(zip(questions, reasons), 1):
                    with st.container():
                        st.write(f"### 练习 {i}: {question}")
                        st.info(f"📖 **出题原因**: {reason}")

                        code_key = f"code_{i}"
                        run_key = f"run_{i}"
                        output_key = f"output_{i}"
                        por_key = f"por_{i}"
                        analysis_key = f"analysis_{i}"  



                        if f"analysis_{i}" not in st.session_state:
                            st.session_state[f"analysis_{i}"] = "未使用AI进行批改"  # Default code

                        # 初始化状态
                        default_code = "# 在这里编写你的代码"




                        if f"code_{i}" not in st.session_state:
                            st.session_state[f"code_{i}"] = "# 在这里编写你的代码"  # Default code

                        code = st.text_area("🧿在此输入你的代码", value=st.session_state[f"code_{i}"], height=200, key=code_key)

                        # Update session state when the user modifies the code
                        if code != st.session_state[f"code_{i}"]:
                            st.session_state[f"code_{i}"] = code


                            ##############################
                        if f"por_{i}" not in st.session_state:
                            st.session_state[f"por_{i}"] = " "  # Default code

                        por = st.text_area("🧿在此处与AI进行交流", value=st.session_state[f"por_{i}"], height=100, key=por_key)

                        # Update session state when the user modifies the code
                        if por != st.session_state[f"por_{i}"]:
                            st.session_state[f"por_{i}"] = por
                            ##############################
            


                        col1, col2, col3, col4 = st.columns(4)
                        # 运行代码按钮
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

                        # 显示之前的输出
                        elif output_key in st.session_state:
                            st.subheader("💡 运行结果：")
                            st.code(st.session_state[output_key])

                        # 提交答案按钮
                        if col3.button(f"📝AI批改--题目 {i}", key=f"sub_{i}"):
                            solution = st.session_state[code_key]
                            with st.spinner("⏳ 正在获取解析，请稍候..."):
                                message2 = get_know_com_blind_solve(
                                    st.session_state.learning_progress,
                                    current,
                                    solution,
                                    question
                                )
                                response = get_coze_response(message2)
                                parsed_response = json.loads(response['answers'][0])

                                # 存入 session_state
                                st.session_state[f"teacher_feedback_{i}"] = parsed_response.get("teacher", "暂无评语")
                                st.session_state[f"encouragement_{i}"] = parsed_response.get("good", "继续努力！")
                                st.session_state[f"solve_whether_{i}"] = parsed_response.get("solvewhether", "false")
                                st.session_state["com_level"] = parsed_response.get("com level", "未知")

                                # 显示反馈
                                st.subheader("📌 AI 批改评语")
                                st.info(st.session_state[f"teacher_feedback_{i}"])
                                st.subheader("💡 鼓励与评价")
                                st.success(st.session_state[f"encouragement_{i}"])
                                # 如果答对了，记录为待移除知识盲点
                                if st.session_state[f"solve_whether_{i}"] == "true":
                                    if "delele_blindspot" not in st.session_state:
                                        st.session_state.delele_blindspot = []
                                    if current not in st.session_state.delele_blindspot:
                                        st.session_state.delele_blindspot.append(current)
                        if col2.button(f"🧠AI辅导--题目 {i}"):
                             solution = st.session_state[code_key]
                             data = {
                                    "题目": question,
                                    "学生代码": solution,
                                    "指令":por
                                            }
                             print(data)
                             with st.spinner("⏳ 正在获取指导，请稍候..."):
                                 guide=get_coze_response_task_guide(str(data))
                                 st.subheader("🧠 AI 辅导建议：")
                                #  for answer in guide['answers']:
                                #     st.write(answer)

                                 for answer in guide['answers']:
                                          combined_answers = "\n\n".join([f"• {a}" for a in guide['answers']])
                                          st.session_state[analysis_key] = combined_answers
                                 with st.expander("🧠 AI 辅导建议（点击展开）"):
                                
                                        st.markdown(
                            f"<div style='font-size: 14px; line-height: 1.6;'>{combined_answers.replace(chr(10), '<br>')}</div>",
                            unsafe_allow_html=True)
                        if col4.button(f"📨提交我的答案--题目 {i}"): 
                            analysis=st.session_state[analysis_key]
                            solution = st.session_state[code_key]
                            print(analysis)
                            print(solution)
                            print(st.session_state.class_id)
    if st.session_state.user_type == 1:
            st.sidebar.info("🌈 伴学灵宝-云端AI课件")            
            st.sidebar.page_link("app.py", label="🏠 首页")
            st.sidebar.page_link("pages/1_课程讲义学习_课程知识搜集.py", label="📚 课程知识搜集")
            st.sidebar.page_link("pages/2_讲义知识学伴_AI教学设计.py", label="🎓 AI教学设计")
            st.sidebar.page_link("pages/3_讲义练习辅导_课堂游戏资源.py", label="🎮 课堂游戏资源")
            st.sidebar.page_link("pages/4_课堂任务完成_发布课堂任务.py", label="✨ 发布课堂任务")
            st.sidebar.page_link("pages/5_自行选择训练_试卷批改.py", label="✏️ 试卷批改")
            st.sidebar.page_link("pages/6_个人学情查询_班级数据管理.py", label="📈 班级数据管理")  
            
            # 班级管理功能
            st.header("👥 班级管理", divider="blue")
            
            with st.container(border=True):
                st.subheader("📚 班级信息")
                # 显示所有班级
                all_classes = get_all_classes()
                if not all_classes:
                    st.warning("📭 暂无班级数据")
                else:
                    cols = st.columns([3,1])
                    with cols[0]:
                        selected_class = st.selectbox("🏫 选择班级", all_classes)
                    
                    with cols[1]:
                        st.metric("👥 班级人数", len(get_class_students(selected_class)))
                    
                    # 班级学生列表
                    with st.expander(f"📋 查看班级 {selected_class} 学生名单", expanded=False):
                        class_students = get_class_students(selected_class)
                        if class_students:
                            st.dataframe(pd.DataFrame({"📧 学生邮箱": class_students}))
                        else:
                            st.info("👻 该班级暂无学生")
            
            with st.container(border=True):
                st.markdown("""
<div style="background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); 
                padding: 1.5rem; border-radius: 12px;
                box-shadow: 0 6px 16px rgba(255,160,0,0.2);
                border-left: 5px solid #ffa000;">
    <h3 style="color: #e65100; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">📊 班级数据分析功能</h3>
    <p style="font-size: 0.95rem; color: #bf360c;">✨ 以下功能可帮助您更好地了解班级学情</p>
</div>
""", unsafe_allow_html=True)
                
                cols = st.columns(3)
                with cols[0]:
                    st.markdown("""
<div style="background: #e3f2fd; padding: 1rem; border-radius: 8px;">
<h4>🔍 分析学生数据</h4>
<p>预测未来学习难点</p>
</div>
""", unsafe_allow_html=True)
                with cols[1]:
                    st.markdown("""
<div style="background: #e8f5e9; padding: 1rem; border-radius: 8px;">
<h4>📚 备课学习资料</h4>
<p>个性化出题</p>
</div>
""", unsafe_allow_html=True)
                with cols[2]:
                    st.markdown("""
<div style="background: #fff3e0; padding: 1rem; border-radius: 8px;">
<h4>💡 课堂讨论案例</h4>
<p>快速调整内容</p>
</div>
""", unsafe_allow_html=True)
            # 添加文字说明    
            all_users = get_all_users_data()
            if 'report_generated' not in st.session_state:
                st.session_state.report_generated = False

            

            if not all_users:
                st.warning("无可用学生数据")
            else:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    
                    if not st.session_state.report_generated:
                        if st.button("📊 生成班级基本数据报告"):
                            st.session_state.raw_report = generate_raw_summary(all_users)
                            st.session_state.report_generated = True
                            st.rerun()
                    else:
                        st.text_area("", 
                                    value=st.session_state.raw_report,
                                    height=600)
                
                with col2:
                    if st.session_state.report_generated:
                        st.download_button(
                            label="📥 下载报告",
                            data=st.session_state.raw_report,
                            file_name="students_report.txt",
                            mime="text/plain",
                            key="unique_download_key"
                        )
                        st.success("报告已就绪")
                        
                        st.metric("总学生数", len(all_users))
                        st.caption(f"生成时间：{datetime.now().strftime('%H:%M:%S')}")
                        
                        if st.button("🔄 重新生成"):
                            st.session_state.report_generated = False
                            st.rerun()
                with col3:
                    # if col3.button("🧝‍♂️ 智能分析&教学指导"):
                        report_data = str(generate_raw_summary(all_users))
                        if "classchat" not in st.session_state:
                            st.session_state.classchat = " "  # Default code

                        st.session_state.classchat  = st.text_area("🧿在此处与AI进行交流", height=100, key="lasschat")
                        if col3.button("🧝‍♂️ 智能分析&教学指导"):
                            print(report_data)

                            print(st.session_state.classchat)
                            data = {
                        "班级学情": report_data,
                        "指令":st.session_state.classchat
                    }
                            print(data)
                            with st.spinner("⏳ 正🧿在获取指导，请稍候..."):
                                guide = get_coze_response_get_class_guide(str(data))
                                combined_answers = "\n\n".join([f"• {a}" for a in guide['answers']])
                            with st.expander("🧠 AI 辅导建议（点击展开）"):
                                st.markdown(
                                    f"<div style='font-size: 14px; line-height: 1.6;'>{combined_answers.replace(chr(10), '<br>')}</div>",
                                    unsafe_allow_html=True
                                )


            # if 'chat_history_page61' not in st.session_state:
            #     st.session_state.chat_history_page61 = []

            # for msg in st.session_state.chat_history_page61:
            #     if msg["role"] == "user":
            #         st.chat_message_page61("user").write(msg["content"])
            #     elif msg["role"] == "assistant":
            #         st.chat_message_page61("assistant").write(msg["content"])
            #     else:
            #         print(1)

            # # 用户输入
            # user_input2 = st.chat_input("这里你可以借助AI帮你分析班级学情...",key="user_input2")
            # if user_input2:
            #     with st.spinner("思考中..."):
            #         combined_data = {
            #             "prompt": user_input2,
            #             "students_data": all_users  # 直接使用从数据库获取的原始数据
            #         }
            #         response = question_service(str(combined_data))
            #         # 重新渲染以显示最新消息
            #         st.rerun()
                                        
if __name__ == "__main__":
    show()
