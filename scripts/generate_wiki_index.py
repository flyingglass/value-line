"""
generate_wiki_index.py — 从 research-wiki/ 扫描所有 md，生成自包含 SPA HTML
research-wiki/index.html: 投研 Wiki 浏览器，支持筛选/搜索/展开阅读
"""
import os, re, json, yaml, sys, base64
from datetime import date, datetime as dt
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(BASE, "research-wiki")
OUTPUT = os.path.join(WIKI_DIR, "index.html")

def parse_frontmatter(text):
    """解析 YAML frontmatter，返回 (meta_dict, body_text)"""
    if not text.startswith('---'):
        return {}, text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except:
        meta = {}
    return meta, parts[2].strip()

def iter_md(root):
    """递归遍历 root 下所有 .md 文件，返回 (相对路径, 绝对路径)"""
    for dirpath, dirnames, filenames in os.walk(root):
        for fname in sorted(filenames):
            if not fname.endswith('.md'):
                continue
            full = os.path.join(dirpath, fname)
            yield os.path.relpath(full, root), full

def extract_summary(body, max_len=120):
    """从 body 提取摘要：取第一个非空非标题段落"""
    lines = body.strip().split('\n')
    summary = ''
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == '---' or stripped.startswith('#') or stripped.startswith('>') or stripped.startswith('|') or stripped.startswith('- ') or stripped.startswith('* '):
            if summary:
                break
            continue
        # 去掉 markdown 链接格式
        cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', stripped)
        cleaned = re.sub(r'\[\[([^\]]+)\]\]', r'\1', cleaned)
        cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)
        summary += cleaned + ' '
        if len(summary) > max_len:
            break
    return summary.strip()[:max_len] + ('...' if len(summary) > max_len else '')

def scan_wiki():
    """扫描 research-wiki/ 下所有 md，返回 {分组: [文章列表]}"""
    
    stock_info = {
        'TCL中环': '光伏', 'TCL科技': '面板', '云铝股份': '金属与矿业',
        '京东方': '面板', '人福医药': '制药', '宁德时代': '能源',
        '安琪酵母': '化工', '建滔积层板': '工业', '建滔集团': '工业',
        '时代天使': '医疗健康', '泡泡玛特': '消费', '贵州茅台': '消费', '润泽科技': '互联网',
        '阿里巴巴': '互联网', '拼多多': '互联网',
        '神火股份': '金属与矿业', '紫金矿业': '金属与矿业', '腾讯控股': '互联网',
        'AMZN': '互联网', 'GOOGL': '互联网', 'MSFT': '互联网',
    }
    page_labels = {
        # 英文文件名（旧标的）
        'overview': '数据目录', 'thesis': '投资 Thesis',
        'industry-chain': '产业链全景', 'operating-metrics': '运营指标',
        'research-reports': '研报索引',
        # 中文文件名（如贵州茅台）
        '数据目录': '数据目录', '投资论点': '投资 Thesis',
        '产业链': '产业链全景', '运营指标': '运营指标',
        '渠道改革': '渠道改革', '销量与吨价': '销量与吨价',
        '券商研报': '研报索引',
    }
    
    groups = {}  # group_id -> {name, industry, articles: []}
    general = []  # 通用文章（不归属任何标的）
    
    def add_article(group_id, group_name, industry, article):
        if group_id not in groups:
            groups[group_id] = {'name': group_name, 'industry': industry, 'articles': []}
        groups[group_id]['articles'].append(article)
    
    # 1. research/<code>/ — 标的 wiki 页（含子目录：业绩/经营/需求 等）
    research_dir = os.path.join(WIKI_DIR, "research")
    if os.path.isdir(research_dir):
        for sub in sorted(os.listdir(research_dir)):
            subpath = os.path.join(research_dir, sub)
            if not os.path.isdir(subpath) or sub == 'articles':
                continue
            industry = stock_info.get(sub, '其他')
            for relpath, fpath in iter_md(subpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    text = f.read()
                meta, body = parse_frontmatter(text)
                page_key = os.path.splitext(os.path.basename(fpath))[0]
                page_label = page_labels.get(page_key, page_key)
                subdir = os.path.dirname(relpath)
                title = f"[{subdir}] {meta.get('topic') or page_label}" if subdir else (meta.get('topic') or page_label)
                add_article(sub, sub, industry, {
                    'title': title,
                    'kind': 'wiki',
                    'path': f"research/{sub}/{relpath}",
                    'date': meta.get('created') or meta.get('updated') or '',
                    'summary': extract_summary(body),
                    'body': body,
                })
    
    # 2. raw/research/<code>/ — 标的原始资料（含子目录）
    raw_research_dir = os.path.join(WIKI_DIR, "raw", "research")
    if os.path.isdir(raw_research_dir):
        for sub in sorted(os.listdir(raw_research_dir)):
            subpath = os.path.join(raw_research_dir, sub)
            if not os.path.isdir(subpath) or sub == 'articles':
                continue
            industry = stock_info.get(sub, '其他')
            for relpath, fpath in iter_md(subpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    text = f.read()
                meta, body = parse_frontmatter(text)
                base = os.path.splitext(os.path.basename(fpath))[0]
                title = meta.get('topic') or meta.get('title') or base
                subdir = os.path.dirname(relpath)
                if subdir:
                    title = f"[{subdir}] {title}"
                add_article(sub, sub, industry, {
                    'title': title,
                    'kind': 'raw',
                    'path': f"raw/research/{sub}/{relpath}",
                    'date': meta.get('created') or meta.get('date') or '',
                    'summary': extract_summary(body),
                    'body': body,
                })
    
    # 3. research/articles/concepts/ — 概念框架
    concepts_dir = os.path.join(WIKI_DIR, "research", "articles", "concepts")
    if os.path.isdir(concepts_dir):
        for fname in sorted(os.listdir(concepts_dir)):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(concepts_dir, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                text = f.read()
            meta, body = parse_frontmatter(text)
            title = meta.get('topic') or fname.replace('.md', '')
            general.append({
                'title': title, 'kind': 'concept',
                'path': f"research/articles/concepts/{fname}",
                'date': meta.get('created') or '',
                'summary': extract_summary(body), 'body': body,
            })
    
    # 4. research/articles/entities/ — 人物/机构
    entities_dir = os.path.join(WIKI_DIR, "research", "articles", "entities")
    if os.path.isdir(entities_dir):
        for fname in sorted(os.listdir(entities_dir)):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(entities_dir, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                text = f.read()
            meta, body = parse_frontmatter(text)
            title = meta.get('topic') or meta.get('entity') or fname.replace('.md', '')
            general.append({
                'title': title, 'kind': 'entity',
                'path': f"research/articles/entities/{fname}",
                'date': meta.get('created') or '',
                'summary': extract_summary(body), 'body': body,
            })
    
    # 5. research/articles/papers/ — 参考书目
    papers_dir = os.path.join(WIKI_DIR, "research", "articles", "papers")
    if os.path.isdir(papers_dir):
        for fname in sorted(os.listdir(papers_dir)):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(papers_dir, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                text = f.read()
            meta, body = parse_frontmatter(text)
            title = meta.get('topic') or fname.replace('.md', '')
            general.append({
                'title': title, 'kind': 'paper',
                'path': f"research/articles/papers/{fname}",
                'date': meta.get('created') or '',
                'summary': extract_summary(body), 'body': body,
            })
    
    # 6. research/articles/synthesis/ — 综合分析（部分归属标的，部分通用）
    synthesis_dir = os.path.join(WIKI_DIR, "research", "articles", "synthesis")
    # 关键词 → 标的映射
    synthesis_stock_map = {
        'popmart': '泡泡玛特', 'maotai': '贵州茅台',
        'dahang': '贵州茅台', 'disney': '迪士尼',
        'sanrio': '泡泡玛特', 'generational': '泡泡玛特',
        '国企激励机制': '贵州茅台',
        '京东方': '京东方',
    }
    if os.path.isdir(synthesis_dir):
        for fname in sorted(os.listdir(synthesis_dir)):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(synthesis_dir, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                text = f.read()
            meta, body = parse_frontmatter(text)
            title = meta.get('topic') or fname.replace('.md', '')
            article = {
                'title': title, 'kind': 'synthesis',
                'path': f"research/articles/synthesis/{fname}",
                'date': meta.get('created') or '',
                'summary': extract_summary(body), 'body': body,
            }
            # 尝试匹配标的
            fname_lower = fname.lower()
            matched = None
            for kw, stock_name in synthesis_stock_map.items():
                if kw in fname_lower:
                    matched = stock_name
                    break
            if matched:
                if matched not in stock_info:
                    stock_info[matched] = '其他'
                add_article(matched, matched, stock_info.get(matched, '其他'), article)
            else:
                general.append(article)
    
    # 7. raw/research/articles/ — 通用原始资料
    raw_articles_dir = os.path.join(WIKI_DIR, "raw", "research", "articles")
    if os.path.isdir(raw_articles_dir):
        for fname in sorted(os.listdir(raw_articles_dir)):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(raw_articles_dir, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                text = f.read()
            meta, body = parse_frontmatter(text)
            title = meta.get('topic') or meta.get('title') or fname.replace('.md', '')
            general.append({
                'title': title, 'kind': 'raw',
                'path': f"raw/research/articles/{fname}",
                'date': meta.get('created') or meta.get('date') or '',
                'summary': extract_summary(body), 'body': body,
            })
    
    # 将 date 对象转为字符串
    for g in groups.values():
        for a in g['articles']:
            if isinstance(a.get('date'), (date, dt)):
                a['date'] = a['date'].isoformat()[:10]
    for a in general:
        if isinstance(a.get('date'), (date, dt)):
            a['date'] = a['date'].isoformat()[:10]
    
    # 按主题聚类通用知识
    topic_rules = [
        ('生物学', ['道金斯', '戴蒙德', '里德利', '格里宾', '自私', '枪炮', '基因组', '冰河期', '生物进化']),
        ('复杂经济学', ['复杂经济', '阿瑟', '收益递增', '技术自创生', '技术本质', '技术革命', '组合进化']),
        ('书籍摘要', ['艾德勒', '阅读法', '四级阅读']),
        ('心理学', ['西奥迪尼', '影响力', '卡尼曼', '思考快与慢']),
        ('芒格·格栅理论', ['芒格', '穷查理', '格栅', '哈格斯特朗', '伯克希尔', '巴芒', '迪士尼', '竞争性毁灭', '倾覆力矩', '临界质量', 'ESS', '进化', '商业基因']),
    ]
    for a in general:
        hay = a['title'] + ' ' + a['path'] + ' ' + a.get('body', '')[:300]
        matched = None
        for topic, keywords in topic_rules:
            for kw in keywords:
                if kw in hay:
                    matched = topic
                    break
            if matched:
                break
        a['topic'] = matched or '其他'
    
    return groups, general

def build_html(groups, general):
    """生成自包含 SPA HTML，按标的分组"""
    # 将 body 字段 base64 编码，避免 JSON 序列化时的转义问题
    def encode_bodies(obj):
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                if k == 'body' and isinstance(v, str):
                    result[k] = base64.b64encode(v.encode('utf-8')).decode('ascii')
                    result['_b64'] = True
                elif isinstance(v, dict):
                    result[k] = encode_bodies(v)
                elif isinstance(v, list):
                    result[k] = [encode_bodies(item) if isinstance(item, dict) else item for item in v]
                else:
                    result[k] = v
            return result
        return obj
    
    groups_encoded = encode_bodies({k: {'name': v['name'], 'industry': v['industry'], 'articles': v['articles']} for k, v in groups.items()})
    general_encoded = encode_bodies(general)
    groups_json = json.dumps(groups_encoded, ensure_ascii=False)
    general_json = json.dumps(general_encoded, ensure_ascii=False)
    
    # 按行业排序标的
    stock_order = sorted(groups.items(), key=lambda x: (x[1]['industry'], x[0]))
    
    total_stocks = len(groups)
    total_general = len(general)
    total_articles = sum(len(v['articles']) for v in groups.values()) + total_general
    
    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>投研 Wiki</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
:root{{--bg:#f8f9fa;--text:#1a1a1a;--text-muted:#888;--blue:#2563eb;--border:#e0e0e0;--card-bg:#fff}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased}}
.header{{background:#1a1a1a;color:#fff;padding:14px 20px;position:sticky;top:0;z-index:100;display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
.header h1{{font-size:17px;font-weight:600}}
.header h1 span{{color:var(--blue)}}
.header .stats{{font-size:12px;color:#999;display:flex;gap:16px}}
.header .stats strong{{color:#ccc}}
.header-nav a{{color:#ccc;text-decoration:none;font-size:13px;padding:6px 14px;border:1px solid #555;border-radius:6px;transition:all .2s}}
.header-nav a:hover{{color:#fff;border-color:#888;background:#333}}
.filters{{display:flex;gap:8px;padding:12px 20px;max-width:960px;margin:0 auto 16px;flex-wrap:wrap}}
.filters input{{flex:1;min-width:200px;padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;outline:none}}
.filters input:focus{{border-color:#1a73e8}}
.filters select{{padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;background:#fff;outline:none;cursor:pointer}}
.content{{max-width:960px;margin:0 auto;padding:20px}}
.section-title{{font-size:15px;font-weight:700;color:#333;margin:24px 0 12px;padding-bottom:8px;border-bottom:2px solid #1a73e8;display:flex;align-items:center;gap:8px}}
.section-title .count{{font-size:12px;color:#999;font-weight:400}}
.stock-group{{margin-bottom:20px}}
.stock-header{{background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:12px 16px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;transition:border-color .2s}}
.stock-header:hover{{border-color:#1a73e8}}
.stock-header.collapsed{{border-radius:8px}}
.stock-name{{font-size:15px;font-weight:600}}
.stock-industry{{font-size:11px;color:#999;margin-left:8px;padding:2px 8px;background:#f0f0f0;border-radius:4px}}
.stock-articles{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px;padding:4px 0 4px 12px;border-left:2px solid #e0e0e0;margin-left:8px}}
.stock-articles.hidden{{display:none}}
.article-card{{background:#fff;border-radius:6px;padding:12px;cursor:pointer;border:1px solid #e8e8e8;transition:box-shadow .2s}}
.article-card:hover{{box-shadow:0 2px 8px rgba(0,0,0,.06)}}
.article-title{{font-size:13px;font-weight:500;line-height:1.3;margin-bottom:4px}}
.article-meta{{display:flex;gap:6px;flex-wrap:wrap}}
.article-tag{{font-size:10px;padding:1px 6px;border-radius:3px;font-weight:500}}
.tag-wiki{{background:#e8f5e9;color:#2e7d32}}
.tag-raw{{background:#fff3e0;color:#e65100}}
.tag-concept{{background:#e3f2fd;color:#1565c0}}
.tag-entity{{background:#fce4ec;color:#c62828}}
.tag-synthesis{{background:#f3e5f5;color:#7b1fa2}}
.tag-paper{{background:#e0f2f1;color:#00695c}}
.kind-group{{margin-bottom:20px}}
.kind-header{{font-size:14px;font-weight:600;color:#555;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--border)}}
.kind-header .count{{font-size:12px;color:#999;font-weight:400}}
.general-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px}}
.reader{{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:#f8f9fa;z-index:200;flex-direction:column;opacity:0;transition:opacity .2s}}
.reader.active{{display:flex;opacity:1}}
.reader-topbar{{flex-shrink:0;display:flex;justify-content:space-between;align-items:center;padding:12px 20px;background:#fff;border-bottom:1px solid #e0e0e0;box-shadow:0 1px 4px rgba(0,0,0,.05)}}
.reader-topbar h2{{font-size:16px;font-weight:600;flex:1;padding-right:16px;line-height:1.4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.reader-close{{flex-shrink:0;background:#f0f0f0;border:none;font-size:22px;cursor:pointer;color:#666;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;transition:all .15s}}
.reader-close:hover{{background:#e0e0e0;color:#111}}
.reader-body{{flex:1;overflow-y:auto;padding:32px 24px 60px;-webkit-overflow-scrolling:touch}}
.reader-body-inner{{max-width:780px;margin:0 auto}}
.reader-body h1{{font-size:22px;margin:20px 0 10px}}
.reader-body h2{{font-size:18px;margin:18px 0 10px;padding-bottom:4px;border-bottom:1px solid #eee}}
.reader-body h3{{font-size:15px;margin:14px 0 8px}}
.reader-body p{{margin:10px 0}}
.reader-body blockquote{{border-left:3px solid #1a73e8;padding:8px 16px;margin:14px 0;background:#f8f9fa;color:#555}}
.reader-body table{{border-collapse:collapse;width:100%;margin:14px 0;font-size:13px}}
.reader-body th,.reader-body td{{border:1px solid #ddd;padding:6px 10px;text-align:left}}
.reader-body th{{background:#f5f5f5;font-weight:600}}
.reader-body code{{background:#f0f0f0;padding:1px 4px;border-radius:3px;font-size:13px}}
.reader-body pre{{background:#f5f5f5;padding:14px;border-radius:6px;overflow-x:auto;font-size:13px;margin:14px 0}}
.reader-body ul,.reader-body ol{{padding-left:24px;margin:10px 0}}
.reader-body li{{margin:4px 0}}
.reader-body a{{color:#1a73e8}}
.reader-body img{{max-width:100%}}
.reader-body hr{{border:none;border-top:1px solid #eee;margin:18px 0}}
.no-results{{text-align:center;padding:60px 20px;color:#999;font-size:14px}}
@media (max-width:768px){{
.content{{padding:12px}}
.stock-articles{{grid-template-columns:1fr}}
.general-grid{{grid-template-columns:1fr}}
.reader-body{{padding:20px 14px 48px}}
}}
</style>
</head>
<body>
<div class="header">
  <h1><span>投研</span> Wiki</h1>
  <div style="display:flex;align-items:center;gap:16px">
    <div class="stats" id="stats"></div>
    <div class="header-nav">
      <a href="../report/index.html">📊 Value Line</a>
    </div>
  </div>
  </div>
</div>
<div class="filters">
  <input type="text" id="search" placeholder="搜索标题或内容..." oninput="render()">
  <select id="filterView" onchange="render()">
    <option value="all">全部</option>
    <option value="stocks">按标的</option>
    <option value="general">多学科</option>
  </select>
</div>
<div class="content" id="content"></div>
<div class="reader" id="reader">
  <div class="reader-topbar">
    <h2 id="readerTitle"></h2>
    <button class="reader-close" onclick="closeReader()">&times;</button>
  </div>
  <div class="reader-body">
    <div class="reader-body-inner" id="readerBody"></div>
  </div>
</div>

<script>
var GROUPS = {groups_json};
var GENERAL = {general_json};

var kindTags = {{
  'wiki': '<span class="article-tag tag-wiki">Wiki</span>',
  'raw': '<span class="article-tag tag-raw">原始</span>',
  'concept': '<span class="article-tag tag-concept">概念</span>',
  'entity': '<span class="article-tag tag-entity">人物</span>',
  'synthesis': '<span class="article-tag tag-synthesis">综合</span>',
  'paper': '<span class="article-tag tag-paper">参考</span>',
}};

var stockOrder = {json.dumps([k for k, v in stock_order], ensure_ascii=False)};

var allArticles = [];
Object.keys(GROUPS).forEach(function(k) {{
  GROUPS[k].articles.forEach(function(a) {{
    a._group = k;
    a._groupName = GROUPS[k].name;
    a._industry = GROUPS[k].industry;
    allArticles.push(a);
  }});
}});
GENERAL.forEach(function(a) {{ a._group = '_general'; a._groupName = '多学科'; allArticles.push(a); }});

function render() {{
  var q = (document.getElementById('search').value || '').toLowerCase();
  var view = document.getElementById('filterView').value;
  
  var stockArticles = {{}};
  var matchedGeneral = [];
  
  allArticles.forEach(function(a) {{
    if (q) {{
      var hay = (a.title + ' ' + a.summary + ' ' + a.body).toLowerCase();
      if (hay.indexOf(q) === -1) return;
    }}
    if (a._group === '_general') {{
      matchedGeneral.push(a);
    }} else {{
      if (!stockArticles[a._group]) stockArticles[a._group] = [];
      stockArticles[a._group].push(a);
    }}
  }});
  
  var totalVisible = matchedGeneral.length;
  Object.values(stockArticles).forEach(function(arr) {{ totalVisible += arr.length; }});
  document.getElementById('stats').innerHTML = '<span>共 <strong>' + totalVisible + '</strong> 篇</span><span>·</span><span><strong>' + Object.keys(stockArticles).length + '</strong> 个标的</span>';
  
  var html = '';
  
  if (view === 'all' || view === 'stocks') {{
    if (Object.keys(stockArticles).length > 0) {{
      html += '<div class="section-title">📌 按标的 <span class="count">' + Object.keys(stockArticles).length + ' 个标的</span></div>';
      stockOrder.forEach(function(k) {{
        if (!stockArticles[k]) return;
        var g = GROUPS[k];
        var arts = stockArticles[k];
        html += '<div class="stock-group">';
        html += '<div class="stock-header" onclick="toggleStock(this)">';
        html += '<div><span class="stock-name">' + escapeHtml(g.name) + '</span><span class="stock-industry">' + escapeHtml(g.industry) + '</span></div>';
        html += '<span style="font-size:12px;color:#999">' + arts.length + ' 篇 ▾</span>';
        html += '</div>';
        html += '<div class="stock-articles">';
        arts.forEach(function(a) {{
          html += articleCard(a);
        }});
        html += '</div></div>';
      }});
    }}
  }}
  
  if (view === 'all' || view === 'general') {{
    if (matchedGeneral.length > 0) {{
      html += '<div class="section-title">📖 多学科 <span class="count">' + matchedGeneral.length + ' 篇</span></div>';
      
      // 按 topic 聚类
      var topicOrder = ['芒格·格栅理论', '复杂经济学', '生物学', '心理学', '书籍摘要', '其他'];
      var topicIcons = {{
        '芒格·格栅理论': '🧠',
        '复杂经济学': '🔄',
        '生物学': '🧬',
        '心理学': '🧩',
        '书籍摘要': '📚',
        '其他': '📌',
      }};
      var topicGroups = {{}};
      topicOrder.forEach(function(t) {{ topicGroups[t] = []; }});
      matchedGeneral.forEach(function(a) {{
        var t = a.topic || '其他';
        if (!topicGroups[t]) topicGroups[t] = [];
        topicGroups[t].push(a);
      }});
      
      topicOrder.forEach(function(t) {{
        var arts = topicGroups[t];
        if (!arts || arts.length === 0) return;
        html += '<div class="kind-group">';
        html += '<div class="kind-header">' + (topicIcons[t] || '📌') + ' ' + t + ' <span class="count">' + arts.length + ' 篇</span></div>';
        html += '<div class="general-grid">';
        arts.forEach(function(a) {{
          html += '<div class="article-card" data-group="' + a._group + '" data-idx="' + a._idx + '" onclick="openArticle(this.dataset.group,parseInt(this.dataset.idx))">' +
            '<div class="article-title">' + escapeHtml(a.title) + '</div>' +
            '<div class="article-meta">' + (kindTags[a.kind] || '') + '</div>' +
          '</div>';
        }});
        html += '</div></div>';
      }});
      html += '</div>';
    }}
  }}
  
  if (!html) {{
    html = '<div class="no-results">没有匹配的文章</div>';
  }}
  
  document.getElementById('content').innerHTML = html;
}}

function articleCard(a) {{
  return '<div class="article-card" data-group="' + a._group + '" data-idx="' + a._idx + '" onclick="openArticle(this.dataset.group,parseInt(this.dataset.idx))">' +
    '<div class="article-title">' + escapeHtml(a.title) + '</div>' +
    '<div class="article-meta">' + (kindTags[a.kind] || '') + '</div>' +
  '</div>';
}}

// 给所有 article 加上 index
Object.keys(GROUPS).forEach(function(k) {{
  GROUPS[k].articles.forEach(function(a, i) {{ a._idx = i; }});
}});
GENERAL.forEach(function(a, i) {{ a._idx = i; }});

function decodeBody(a) {{
  if (a._b64) {{
    try {{ return decodeURIComponent(Array.prototype.map.call(atob(a.body), function(c) {{ return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2); }}).join('')); }}
    catch(e) {{ return a.body; }}
  }}
  return a.body;
}}

function openArticle(groupId, idx) {{
  var a;
  if (groupId === '_general') {{
    a = GENERAL[idx];
  }} else {{
    a = GROUPS[groupId].articles[idx];
  }}
  document.getElementById('readerTitle').textContent = a.title;
  document.getElementById('readerBody').innerHTML = marked.parse(decodeBody(a));
  document.getElementById('reader').classList.add('active');
  document.body.style.overflow = 'hidden';
}}

function toggleStock(el) {{
  var arts = el.nextElementSibling;
  arts.classList.toggle('hidden');
  var arrow = el.querySelector('span:last-child');
  arrow.textContent = arts.classList.contains('hidden') ? arrow.textContent.replace('▾','▸') : arrow.textContent.replace('▸','▾');
}}

function closeReader() {{
  document.getElementById('reader').classList.remove('active');
  document.body.style.overflow = '';
}}

function escapeHtml(s) {{
  var d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}}

document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') closeReader();
}});

render();
</script>
</body>
</html>'''
    return html

def main():
    print("扫描 research-wiki/ ...")
    groups, general = scan_wiki()
    total_stocks = len(groups)
    total_articles = sum(len(v['articles']) for v in groups.values()) + len(general)
    print(f"  标的: {total_stocks} 个 | 通用: {len(general)} 篇 | 共 {total_articles} 篇")
    
    html = build_html(groups, general)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n生成: {OUTPUT}")
    print(f"  大小: {len(html):,} chars")

if __name__ == '__main__':
    main()
