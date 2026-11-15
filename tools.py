# tools.py —— Agent 可调用的工具

# 模拟数据：真实项目里这里换成搜索 API / 爬虫
MOCK_NOTES = {
    "露营装备": [
        {"title": "露营3年，这5件装备我劝你别买", "likes": 12000, "tags": ["露营", "避雷"]},
        {"title": "新手露营装备清单｜500元搞定", "likes": 9800, "tags": ["露营", "平价"]},
        {"title": "露营拍照机位｜出片率100%", "likes": 15000, "tags": ["露营", "拍照"]},
        {"title": "露营翻车实录，血泪教训", "likes": 7600, "tags": ["露营", "避雷"]},
        {"title": "周末露营，我只带了这3样", "likes": 11000, "tags": ["露营", "极简"]},
    ],
    "美妆": [
        {"title": "油皮亲妈！这瓶粉底液我回购5次", "likes": 20000, "tags": ["美妆", "粉底"]},
        {"title": "学生党平价彩妆，100元全搞定", "likes": 13000, "tags": ["美妆", "平价"]},
        {"title": "化妆5年才懂的3个避雷点", "likes": 8800, "tags": ["美妆", "避雷"]},
    ],
}


def search_notes(keyword: str) -> list:
    """工具1：搜索某赛道下的热门笔记（支持模糊匹配）"""
    # 先精确匹配
    if keyword in MOCK_NOTES:
        return MOCK_NOTES[keyword]
    # 再模糊匹配：关键词包含关系
    for k, v in MOCK_NOTES.items():
        if k in keyword or keyword in k:
            return v
    return []


def analyze_titles(notes: list) -> dict:
    """工具2：分析标题结构（纯统计，不调模型）"""
    if not notes:
        return {"count": 0, "avg_likes": 0, "top_tags": [], "patterns": []}

    titles = [n["title"] for n in notes]
    likes = [n["likes"] for n in notes]

    # 统计标签
    tag_count = {}
    for n in notes:
        for t in n["tags"]:
            tag_count[t] = tag_count.get(t, 0) + 1
    top_tags = sorted(tag_count.items(), key=lambda x: -x[1])[:5]

    # 简单句式识别
    patterns = []
    if any("避雷" in t or "别买" in t for t in titles):
        patterns.append("避雷/劝退型")
    if any("清单" in t or "这N样" in t or "搞定" in t for t in titles):
        patterns.append("清单/攻略型")
    if any("｜" in t for t in titles):
        patterns.append("竖线分隔型（主题｜卖点）")
    if any(str(i) in t for t in titles for i in range(1, 10)):
        patterns.append("数字型（含具体数字）")

    return {
        "count": len(notes),
        "avg_likes": sum(likes) // len(likes),
        "top_tags": top_tags,
        "patterns": patterns,
    }
# ===== 新增工具3：热门话题趋势 =====
MOCK_TRENDS = {
    "露营装备": {
        "rising": ["精致露营", "车载露营", "亲子露营"],
        "declining": ["硬核野外", "重装徒步"],
        "season": "秋季露营旺季，冲锋衣/防潮垫搜索上升",
    },
    "美妆": {
        "rising": ["早C晚A", "以油养肤", "伪素颜"],
        "declining": ["厚重底妆", "欧美浓妆"],
        "season": "换季期，保湿修护类话题升温",
    },
}


def get_trending_tags(keyword: str) -> dict:
    """工具3：查询赛道近期热门话题趋势"""
    for k, v in MOCK_TRENDS.items():
        if k in keyword or keyword in k:
            return v
    return {"rising": [], "declining": [], "season": "暂无趋势数据"}