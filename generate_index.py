# -*- coding: utf-8 -*-
"""
generate_index.py — 从 config.py 自动生成 report/index.html
统一入口: 每只股票展示 VL 图表 + 阅读报告 双入口
"""
import os, sys, json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import STOCKS

# 行业中文名
INDUSTRY_CN = {
    "Consumer": "消费",
    "Consumer Staples": "消费",
    "Technology": "互联网",
    "Energy": "能源",
    "Metals & Mining": "金属与矿业",
    "Media": "传媒",
    "Packaging": "包装",
    "Automotive": "汽车",
    "Healthcare": "医疗健康",
    "Home Appliances": "家电",
    "Pharmaceuticals": "制药",
    "Building Materials": "建材",
    "Utilities": "公用事业",
    "Insurance": "保险",
    "Financial Services": "金融服务",
    "Semiconductor": "半导体",
}

# 市场标签
MARKET_LABEL = {"hk": "港股", "cn": "A股", "us": "美股"}
MARKET_CLASS = {"hk": "hk", "cn": "cn", "us": "us"}

# 行业展示顺序
INDUSTRY_ORDER = [
    "Consumer",
    "Technology",
    "Semiconductor",
    "Energy",
    "Metals & Mining",
    "Media", "Packaging",
    "Automotive",
    "Healthcare", "Pharmaceuticals",
    "Home Appliances",
    "Building Materials",
    "Utilities",
    "Insurance",
    "Financial Services",
]


def group_by_industry():
    """按行业分组，Consumer Staples 合并到 Consumer"""
    groups = {}
    for code, stock in STOCKS.items():
        ind = stock.get("industry", "Other")
        # 合并必需消费 → 消费
        if ind == "Consumer Staples":
            ind = "Consumer"
        if ind not in groups:
            groups[ind] = []
        groups[ind].append((code, stock))

    # 按 INDUSTRY_ORDER 排序
    ordered = {}
    for ind in INDUSTRY_ORDER:
        if ind in groups:
            ordered[ind] = groups[ind]
    # 剩余未分类
    for ind, items in groups.items():
        if ind not in ordered:
            ordered[ind] = items
    return ordered


def build_index_html():
    """生成 index.html"""
    groups = group_by_industry()
    total = sum(len(v) for v in groups.values())

    cards_html = ""
    for ind, items in groups.items():
        ind_cn = INDUSTRY_CN.get(ind, ind)
        cards_html += f'    <h3 class="section-title">🎯 {ind_cn}</h3>\n'
        cards_html += '    <div class="grid">\n'

        for code, stock in items:
            name = stock["name"]
            name_en = stock.get("name_en", "")
            market = stock.get("market", "hk")
            mkt_label = MARKET_LABEL.get(market, market)
            mkt_class = MARKET_CLASS.get(market, "hk")

            # report 文件名: POP MART 对应 POP_MART.html
            rpt_name = name_en.replace(" ", "_").replace("/", "_") if name_en else name
            rpt_file = f"{rpt_name}.html" if name_en else f"{code}.html"

            cards_html += '      <div class="card">\n'
            cards_html += f'        <div class="card-title">{name_en} · {name}</div>\n'
            cards_html += '        <div class="card-meta">\n'
            cards_html += f'          <span class="code">{code}</span>\n'
            cards_html += f'          <span class="badge badge-{mkt_class}">{mkt_label}</span>\n'
            cards_html += '        </div>\n'
            cards_html += '        <div class="card-links">\n'
            cards_html += f'          <a href="{rpt_file}" class="pill pill-blue">价值线</a>\n'
            cards_html += f'          <a href="reading/{code}.html" class="pill pill-green">阅读报告</a>\n'
            cards_html += '        </div>\n'
            cards_html += '      </div>\n'

        cards_html += '    </div>\n'

    now = datetime.now().strftime("%Y-%m-%d")

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>价值线+阅读报告 · Value Line Research</title>
<style>
  :root {{
    --bg: #f8f9fa;
    --card-bg: #ffffff;
    --text: #1a1a2e;
    --text-muted: #6c757d;
    --border: #e9ecef;
    --blue: #2563eb;
    --green: #059669;
    --hk: #e03131;
    --cn: #e8590c;
    --us: #2f9e44;
    --radius: 12px;
    --shadow: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 40px 20px 80px; }}
  header {{ text-align: center; padding: 48px 0 32px; }}
  header h1 {{ font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }}
  header h1 span {{ color: var(--blue); }}
  header p {{ color: var(--text-muted); margin-top: 8px; font-size: 14px; }}
  .stats {{ display: flex; justify-content: center; gap: 24px; margin-top: 16px; font-size: 13px; color: var(--text-muted); }}
  .stats strong {{ color: var(--text); }}

  .section-title {{
    font-size: 16px; font-weight: 600; margin: 36px 0 12px;
    padding-bottom: 8px; border-bottom: 1px solid var(--border);
  }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }}

  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    box-shadow: var(--shadow);
    transition: box-shadow 0.15s;
  }}
  .card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,.08); }}
  .card-title {{ font-size: 14px; font-weight: 600; margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .card-meta {{ display: flex; gap: 6px; align-items: center; margin-bottom: 10px; }}
  .code {{ font-family: "SF Mono", "Consolas", monospace; font-size: 12px; color: var(--text-muted); }}
  .badge {{ font-size: 10px; font-weight: 600; padding: 1px 6px; border-radius: 4px; color: #fff; }}
  .badge-hk {{ background: var(--hk); }}
  .badge-cn {{ background: var(--cn); }}
  .badge-us {{ background: var(--us); }}

  .card-links {{ display: flex; gap: 6px; }}
  .pill {{
    display: inline-block; font-size: 11px; font-weight: 500;
    padding: 3px 10px; border-radius: 20px; text-decoration: none;
    transition: opacity 0.15s;
  }}
  .pill:hover {{ opacity: 0.85; }}
  .pill-blue {{ background: #dbeafe; color: #1e40af; }}
  .pill-green {{ background: #d1fae5; color: #065f46; }}

  footer {{
    text-align: center; padding: 40px 0 20px; color: var(--text-muted);
    font-size: 12px;
  }}

  @media (max-width: 640px) {{
    .container {{ padding: 20px 12px 60px; }}
    header h1 {{ font-size: 22px; }}
    .grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1><span>价值线+</span>阅读报告</h1>
    <p>基于年报提取的标准化财务分析 · 对标 Value Line Survey</p>
    <div class="stats">
      <span>共 <strong>{total}</strong> 只标的</span>
      <span>·</span>
      <span>{len(groups)} 个行业</span>
      <span>·</span>
      <span>更新: {now}</span>
    </div>
  </header>

{cards_html}
  <footer>
    Value Line Research · 不构成投资建议
  </footer>
</div>
</body>
</html>'''


if __name__ == "__main__":
    html = build_index_html()
    out_path = os.path.join(BASE_DIR, "report", "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] index.html generated: {out_path}")
    print(f"     Stocks: {len(STOCKS)} | Industries: {len(group_by_industry())}")
