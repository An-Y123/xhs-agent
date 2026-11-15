import streamlit as st
from agent import run_agent

st.set_page_config(page_title="小红书选题分析 Agent", page_icon="🔍")
st.title("🔍 小红书选题分析 Agent")
st.caption("输入赛道关键词，Agent 会自动完成：规划 → 调工具查数据 → 生成选题报告")

keyword = st.text_input("输入赛道", placeholder="例如：露营装备、美妆、健身")

if st.button("开始分析") and keyword:
    # 用容器分别承载 3 个步骤，实现逐步展示
    box1 = st.empty()
    box2 = st.empty()
    box3 = st.empty()

    def log(box, icon, text):
        box.markdown(f"{icon} {text}")

    try:
        log(box1, "⏳", "**第1步：规划中** — 正在分析该赛道该搜什么、重点看什么...")

        # 第1步
        from agent import step1_plan
        plan = step1_plan(keyword)
        log(box1, "✅", f"**第1步：规划完成**\n\n- 搜索关键词：`{plan['search_keyword']}`\n- 分析方向：{plan['focus']}")

        # 第2步
        log(box2, "⏳", "**第2步：调用工具** — 正在查询热门笔记并分析标题结构...")
        from agent import step2_execute
        data = step2_execute(plan)
        analysis = data["analysis"]
        log(box2, "✅", f"**第2步：工具调用完成**\n\n- 搜到笔记：**{analysis['count']}** 条\n- 平均点赞：**{analysis['avg_likes']}**\n- 高频标签：{', '.join(t for t, c in analysis['top_tags'])}\n- 识别到的标题句式：{', '.join(analysis['patterns'])}")

        # 第3步
        log(box3, "⏳", "**第3步：生成报告** — 正在结合数据撰写选题建议...")
        from agent import step3_report
        report = step3_report(keyword, plan, data)
        log(box3, "✅", "**第3步：报告生成完成**")

        st.divider()
        st.markdown(report)

    except Exception as e:
        st.error(f"出错了：{e}")