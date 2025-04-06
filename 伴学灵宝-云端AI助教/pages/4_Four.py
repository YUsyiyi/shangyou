import streamlit as st
import json
from utils.ai_processor import generate_blindspot_exercises
from utils.coze_blind_solve import get_coze_response
from utils.auth import get_user_data
from utils.db_operations import get_all_users_data,generate_raw_summary
from utils.db_operations import get_know_com_blind, get_know_com_blind_solve, update_blind_spots, update_com_level
from datetime import datetime
from utils.zhupai_teacher import question_service


def show():
    if 'user_email' not in st.session_state or not st.session_state.user_email:
        st.warning("请先登录！")
        return

    if st.session_state.user_type == 0:
        with st.sidebar:
            st.title("伴学灵宝-云端AI助教")
            st.page_link("app.py", label="注销")
            st.page_link("pages/1_Begin.py", label="课程讲义学习")
            st.page_link("pages/2_Two.py", label="讲义知识理解")
            st.page_link("pages/3_Three.py", label="讲义练习辅导")
            st.page_link("pages/4_Four.py", label="个人学情查询")
            st.page_link("pages/5_Five.py", label="未知")
        st.markdown("""
<div style="background-color: #f0f8ff; padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
    <h3 style="color: #1a4d8f;">🧑‍🏫AI学情分析</h3>
    <p style="font-size: 0.95rem; color: #333;">这个工具将展示个人学习情况,知识盲点;通过解决知识盲点的练习题,实现个性化学习需求</p>
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
        blind_spots = st.session_state.blind_spots

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
                            st.session_state.exercises = None  # **清空练习题**
                            st.rerun()

        # **如果有选中的知识盲区**
        if 'current_blindspot' in st.session_state:
            st.subheader(f"Exercises for: {st.session_state.current_blindspot}")

            # **只在 session_state 中没有练习题时获取**
            if 'exercises' not in st.session_state or st.session_state.exercises is None:
                with st.spinner("⏳ 正在获取练习题，请稍候..."):
                    message = get_know_com_blind(st.session_state.user_email, st.session_state.current_blindspot)
                    st.session_state.exercises = generate_blindspot_exercises(message)  # **缓存练习题**
            
            # **解析缓存的练习题**
            parsed_data = json.loads(st.session_state.exercises['answers'][0])
            questions = parsed_data["text"]
            reasons = parsed_data["reason"]

            for i, (question, reason) in enumerate(zip(questions, reasons), 1):
                with st.container():
                    st.write(f"### 练习 {i}: {question}")
                    st.info(f"📖 **出题原因**: {reason}")

                    solution = st.text_area("你的答案", key=f"sol_{i}")

                    # **确保 session_state 变量**
                    if f"solve_whether_{i}" not in st.session_state:
                        st.session_state[f"solve_whether_{i}"] = "false"

                    if st.button(f"提交答案 {i}", key=f"sub_{i}"):
                        with st.spinner("⏳ 正在获取解析，请稍候..."):
                            message2 = get_know_com_blind_solve(
                                st.session_state.learning_progress,
                                st.session_state.com_level,
                                st.session_state.current_blindspot,
                                solution,
                                question
                            )
                            response = get_coze_response(message2)
                            parsed_response = json.loads(response['answers'][0])

                            # **存入 session_state**
                            st.session_state[f"teacher_feedback_{i}"] = parsed_response.get("teacher", "暂无评语")
                            st.session_state[f"encouragement_{i}"] = parsed_response.get("good", "继续努力！")
                            st.session_state[f"solve_whether_{i}"] = parsed_response.get("solvewhether", "false")
                            st.session_state["com_level"] = parsed_response.get("com level", "未知")
                        
                            # **显示 AI 批改评语**
                            st.subheader("📌 AI 批改评语")
                            st.info(st.session_state[f"teacher_feedback_{i}"])

                            st.subheader("💡 鼓励与评价")
                            st.success(st.session_state[f"encouragement_{i}"])

                            # **更新计算思维分数**
                            update_com_level(st.session_state.user_email, st.session_state["com_level"])
                            ##############################
                            
                            st.success("✅ AI助教一直陪伴您噢~")

                            # **如果答对了，记录待删除的知识盲点**
                            if st.session_state[f"solve_whether_{i}"] == "true":
                                if "delele_blindspot" not in st.session_state:
                                    st.session_state.delele_blindspot = []
                                    st.session_state.delele_blindspot.append(st.session_state.current_blindspot)
                                    
                                else:
                                    st.session_state.delele_blindspot.append(st.session_state.current_blindspot)
                                    

        # **更新学习进度**
        if st.button("📌 更新此次学习进度~", key="update_progress"):
            if "delele_blindspot" in st.session_state:
                user_data = get_user_data(st.session_state.user_email)
                blind_spots = user_data.get('blind_spots', [])
                updated_blind_spots = [spot for spot in blind_spots if spot not in st.session_state.delele_blindspot]
                success = update_blind_spots(st.session_state.user_email, updated_blind_spots)

                if success:
                    st.success("🎉 你已掌握新知识，盲区列表已更新！")
                    user_data = get_user_data(st.session_state.user_email)
                    st.session_state.com_level = user_data.get('com_level', '0分')
                    st.session_state.blind_spots = user_data.get('blind_spots', [])
                    st.rerun()
                else:
                    st.error("❌ 更新盲区列表失败，请稍后重试。")
                    st.rerun()


    if st.session_state.user_type == 1:
            with st.sidebar:
                st.title("伴学灵宝-云端AI助教")
                st.page_link("app.py", label="注销")
                st.page_link("pages/1_Begin.py", label="课程知识搜集")
                st.page_link("pages/2_Two.py", label="AI教学设计")
                st.page_link("pages/3_Three.py", label="游戏资源设计")
                st.page_link("pages/4_Four.py", label="班级数据管理")
                st.page_link("pages/5_Five.py", label="试卷批改") 
            st.markdown("""
<div style="background-color: #f0f8ff; padding: 1.5rem; border-radius: 12px; margin-top: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
    <h3 style="color: #1a4d8f;">班级数据分析</h3>
    <p style="font-size: 0.95rem; color: #333;">用于教师的获取班级学情，借助AI分析,生成个性化的教学指导</p>
</div>
""", unsafe_allow_html=True)
            st.table([
                ["1. 分析学生数据", "预测未来学习难点"],
                ["2. 备课学习资料连接", "个性化出题"],
                ["3. 生成课堂讨论案例", "快速调整内容"]
            ])
            # 添加文字说明    
            all_users = get_all_users_data()
            if 'report_generated' not in st.session_state:
                st.session_state.report_generated = False

            

            if not all_users:
                st.warning("无可用学生数据")
            else:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    
                    if not st.session_state.report_generated:
                        if st.button("生成完整报告"):
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
            user_input2 = st.chat_input("这里你可以借助AI帮你分析班级学情...",key="user_input2")
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
