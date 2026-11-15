# agent.py —— Agent 主流程：规划 → 调工具 → 汇总
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import search_notes, analyze_titles, get_trending_tags, MOCK_NOTES

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

MODEL = "qwen-plus"  # 用你项目一跑通的模型名


def step1_plan(keyword: str) -> dict:
    """第1步：让模型做规划 —— 决定调哪些工具、什么顺序"""
    prompt = f"""你是小红书选题分析 Agent，可以调用以下工具：
- search_notes(keyword)：搜索某赛道的热门笔记，返回标题、点赞、标签
- analyze_titles(notes)：统计标题的句式规律、高频标签、平均点赞
- get_trending_tags(keyword)：查询赛道近期热门/衰退话题趋势

可用数据源关键词只有：{list(MOCK_NOTES.keys())}

赛道：{keyword}
请输出 JSON，格式：
{{
  "search_keyword": "从可用关键词里选一个",
  "tool_plan": ["你要按顺序调用的工具名列表"],
  "focus": "重点分析方向（一句话）",
  "reason": "为什么这样安排工具顺序（一句话）"
}}
只输出 JSON，不要其他文字。"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = resp.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "search_keyword": keyword,
            "tool_plan": ["search_notes", "analyze_titles"],
            "focus": "通用分析",
            "reason": "默认流程",
        }

def step2_execute(plan: dict) -> dict:
    keyword = plan["search_keyword"]
    tool_plan = plan["tool_plan"]

    # 保证依赖顺序：先 search_notes，再 analyze_titles
    if "search_notes" in tool_plan:
        tool_plan = (["search_notes"]
                     + [t for t in tool_plan if t != "search_notes"])
    if "analyze_titles" in tool_plan:
        # analyze_titles 必须跟在 search_notes 后
        tool_plan = [t for t in tool_plan if t != "analyze_titles"] + ["analyze_titles"]

    result = {"tool_calls": []}
    for tool_name in tool_plan:
        if tool_name == "search_notes":
            notes = search_notes(keyword)
            result["notes"] = notes
            result["tool_calls"].append(f"search_notes → 返回 {len(notes)} 条笔记")

        elif tool_name == "analyze_titles":
            notes = result.get("notes", [])
            analysis = analyze_titles(notes)
            result["analysis"] = analysis
            result["tool_calls"].append(f"analyze_titles → 识别 {len(analysis['patterns'])} 种句式")

        elif tool_name == "get_trending_tags":
            trends = get_trending_tags(keyword)
            result["trends"] = trends
            result["tool_calls"].append(f"get_trending_tags → 上升话题 {len(trends['rising'])} 个")
    return result

def step3_report(keyword: str, plan: dict, data: dict) -> str:
    """第3步：汇总成报告（用上所有工具返回的数据）"""
    prompt = f"""你是小红书选题分析师。
赛道：{keyword}
分析方向：{plan['focus']}

工具返回数据：
- 热门笔记：{json.dumps(data.get('notes', []), ensure_ascii=False)}
- 标题统计：{json.dumps(data.get('analysis', {}), ensure_ascii=False)}
- 话题趋势：{json.dumps(data.get('trends', {}), ensure_ascii=False)}

请输出一份选题建议报告，包含：
1. 赛道现状（结合话题趋势）
2. 爆款标题规律（基于标题统计）
3. 3个可直接用的新标题（要结合当下上升话题）
4. 一个避坑提醒（结合衰退话题）
用 markdown 格式，每个结论都要有数据支撑。"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    return resp.choices[0].message.content


def run_agent(keyword: str, verbose: bool = True) -> str:
    if verbose:
        print(f">>> [1/3] 规划中...")
    plan = step1_plan(keyword)
    if verbose:
        print(f"    规划结果：{plan}")

    if verbose:
        print(f">>> [2/3] 按计划调工具：{plan.get('tool_plan')}")
    data = step2_execute(plan)
    if verbose:
        for call in data["tool_calls"]:
            print(f"    - {call}")

    if verbose:
        print(f">>> [3/3] 生成报告...")
    report = step3_report(keyword, plan, data)
    return report
if __name__ == "__main__":
    result = run_agent("露营装备")
    print("\n" + "=" * 40)
    print(result)