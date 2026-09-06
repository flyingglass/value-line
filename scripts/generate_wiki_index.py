"""
generate_wiki_index.py — 生成「投研 Wiki」多页静态站点

页面结构与交互：
    index.html                               首页（按 标的/投资案例/多学科 导航 + 搜索）
    view/stocks/<标的>/index.html            标的组页：文件夹标签(跟踪/经营/…/概览/原始资料)，
                                             点击标签在当前页切换面板，不跳转
    view/stocks/<标的>/<目录…>/<文章>.html    独立文章阅读页
    view/cases/<案例专题>/…                  投资案例专题（组页同上，如 案例/方法论/时间线）
    view/general/index.html                  多学科整组页（主题=顶栏 tab，就地切换）
    view/general/<分类>/<文章>.html          通用文章阅读页

规则：
    · 组根散落的 md 收进「概览」标签（不叫「其他文档」、不单独铺卡片）
    · 组内子目录/主题点击 = 当前页 Tab 切换，不再生成子目录独立页
    · 每篇 md 仍生成独立阅读页，正文由浏览器端 marked 渲染（base64 内嵌原文，可离线解码）
    · 多学科整组页与标的/案例组页同构：主题 当 tab，首页只保留标题+主题 chip+进入

运行：
    .venv\\Scripts\\python scripts\\generate_wiki_index.py
"""
import os, re, yaml, sys, base64
from datetime import date, datetime as dt
from urllib.parse import quote

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(BASE, "research-wiki")
OUT_HOME = os.path.join(WIKI_DIR, "index.html")
VIEW_DIR = os.path.join(WIKI_DIR, "view")
GENERAL_VIEW_DIR = os.path.join(VIEW_DIR, "general")
GENERAL_IDX = os.path.join(GENERAL_VIEW_DIR, "index.html")

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ---------------------------------------------------------------------------
# 分组元数据
# ---------------------------------------------------------------------------
stock_info = {
    'TCL中环': '光伏', 'TCL科技': '面板', '云铝股份': '金属与矿业',
    '京东方': '面板', '人福医药': '制药', '宁德时代': '能源',
    '安琪酵母': '化工', '建滔积层板': '工业', '建滔集团': '工业',
    '时代天使': '医疗健康', '泡泡玛特': '消费', '贵州茅台': '消费', '润泽科技': '互联网',
    '阿里巴巴': '互联网', '拼多多': '互联网',
    '神火股份': '金属与矿业', '紫金矿业': '金属与矿业', '腾讯控股': '互联网',
    'AMZN': '互联网', 'GOOGL': '互联网', 'MSFT': '互联网',
}

# 行业标签配色（浅底 + 深字），同类行业在首页/目录页用同色区分
INDUSTRY_STYLE = {
    '互联网': 'background:#dbeafe;color:#1e40af',
    '消费': 'background:#fce7f3;color:#be185d',
    '光伏': 'background:#fef3c7;color:#b45309',
    '面板': 'background:#e0f2fe;color:#0369a1',
    '金属与矿业': 'background:#e2e8f0;color:#57534e',
    '制药': 'background:#ccfbf1;color:#0f766e',
    '能源': 'background:#d9f99d;color:#3f6212',
    '化工': 'background:#ede9fe;color:#6d28d9',
    '工业': 'background:#cffafe;color:#0e7490',
    '医疗健康': 'background:#ffe4e6;color:#be123c',
}
INDUSTRY_STYLE_DEFAULT = 'background:#eef0f3;color:#555'

page_labels = {
    'overview': '数据目录', 'thesis': '投资 Thesis',
    'industry-chain': '产业链全景', 'operating-metrics': '运营指标',
    'research-reports': '研报索引',
    '数据目录': '数据目录', '投资论点': '投资 Thesis',
    '产业链': '产业链全景', '运营指标': '运营指标',
    '渠道改革': '渠道改革', '销量与吨价': '销量与吨价',
    '券商研报': '研报索引',
}

# 作者案例专题目录（research/ 下的子目录名 → 组显示名）
CASE_GROUP_NAMES = {
    '疯狂的里海': '里海 · 作者案例专题',
}

# 组顶层文件夹（标签）的展示顺序；未列出的按名称字典序；概览 紧随其后；原始资料始终垫底
GROUP_DIR_ORDER = {
    '泡泡玛特': ['跟踪', '经营', '需求', '业绩'],
    '疯狂的里海': ['案例', '方法论', '时间线'],
}

RAW_DIR_NAMES = ('原始资料', '原始资料·源')

topic_rules = [
    ('生物学', ['道金斯', '戴蒙德', '里德利', '格里宾', '自私', '枪炮', '基因组', '冰河期', '生物进化']),
    ('复杂经济学', ['复杂经济', '阿瑟', '收益递增', '技术自创生', '技术本质', '技术革命', '组合进化']),
    ('书籍摘要', ['艾德勒', '阅读法', '四级阅读']),
    ('心理学', ['西奥迪尼', '影响力', '卡尼曼', '思考快与慢']),
    ('芒格·格栅理论', ['芒格', '穷查理', '格栅', '哈格斯特朗', '伯克希尔', '巴芒', '迪士尼', '竞争性毁灭', '倾覆力矩', '临界质量', 'ESS', '进化', '商业基因']),
]

synthesis_stock_map = {
    'popmart': '泡泡玛特', 'maotai': '贵州茅台',
    'dahang': '贵州茅台', 'disney': '迪士尼',
    'sanrio': '泡泡玛特', 'generational': '泡泡玛特',
    '国企激励机制': '贵州茅台',
    '京东方': '京东方',
}

topic_order = ['芒格·格栅理论', '复杂经济学', '生物学', '心理学', '书籍摘要', '其他']
topic_icons = {
    '芒格·格栅理论': '🧠', '复杂经济学': '🔄', '生物学': '🧬',
    '心理学': '🧩', '书籍摘要': '📚', '其他': '📌',
}

# ---------------------------------------------------------------------------
# 通用工具
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    if not text.startswith('---'):
        return {}, text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except Exception:
        meta = {}
    return meta, parts[2].strip()

def iter_md(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fname in sorted(filenames):
            if not fname.endswith('.md'):
                continue
            full = os.path.join(dirpath, fname)
            yield os.path.relpath(full, root).replace('\\', '/'), full

def extract_summary(body, max_len=120):
    lines = body.strip().split('\n')
    summary = ''
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == '---' or stripped.startswith('#') or stripped.startswith('>') or stripped.startswith('|') or stripped.startswith('- ') or stripped.startswith('* '):
            if summary:
                break
            continue
        cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', stripped)
        cleaned = re.sub(r'\[\[([^\]]+)\]\]', r'\1', cleaned)
        cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)
        summary += cleaned + ' '
        if len(summary) > max_len:
            break
    return summary.strip()[:max_len] + ('...' if len(summary) > max_len else '')

def esc(s):
    s = str(s)
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;'))

def posix_rel(from_file_abs, to_file_abs):
    r = os.path.relpath(to_file_abs, os.path.dirname(from_file_abs))
    return r.replace('\\', '/')

def safe_stem(stem):
    if stem.lower() == 'index':
        return stem + '-页'
    return stem

def page_title(meta, stem):
    label = page_labels.get(stem, stem)
    # title 优先于 topic：带 frontmatter title 的文章应显示具体标题，
    # topic（如"案例×体系映射"）只是分类标签，不该顶替标题
    return meta.get('title') or meta.get('entity') or meta.get('topic') or label

def classify_topic(record):
    hay = record['title'] + ' ' + record['path'] + ' ' + record['body'][:300]
    for topic, kws in topic_rules:
        for kw in kws:
            if kw in hay:
                return topic
    return '其他'

def is_raw_dir(name):
    return name in RAW_DIR_NAMES

# ---------------------------------------------------------------------------
# 扫描 md，返回 groups / cases / general
# ---------------------------------------------------------------------------

def read_article(fpath, relwiki):
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    meta, body = parse_frontmatter(text)
    stem = os.path.splitext(os.path.basename(fpath))[0]
    date_ = meta.get('created') or meta.get('updated') or meta.get('date') or ''
    if isinstance(date_, (date, dt)):
        date_ = date_.isoformat()[:10]
    return {
        'title': page_title(meta, stem),
        'kind': 'wiki',
        'path': relwiki,
        'date': str(date_),
        'summary': extract_summary(body),
        'body': body,
    }

def scan_wiki():
    groups = {}
    cases = {}

    def add_article(gid, gname, industry, art):
        art['kind'] = 'wiki' if art['path'].startswith('research/') else 'raw'
        if gid not in groups:
            groups[gid] = {'name': gname, 'industry': industry, 'articles': []}
        groups[gid]['articles'].append(art)

    def add_case(gid, gname, art):
        art['kind'] = 'wiki' if art['path'].startswith('research/') else 'raw'
        if gid not in cases:
            cases[gid] = {'name': gname, 'articles': []}
        cases[gid]['articles'].append(art)

    # research/<code>/
    research_dir = os.path.join(WIKI_DIR, "research")
    if os.path.isdir(research_dir):
        for sub in sorted(os.listdir(research_dir)):
            subpath = os.path.join(research_dir, sub)
            if not os.path.isdir(subpath) or sub == 'articles':
                continue
            is_case = sub in CASE_GROUP_NAMES
            gname = CASE_GROUP_NAMES.get(sub, sub)
            industry = stock_info.get(sub, '其他')
            for rel, fpath in iter_md(subpath):
                art = read_article(fpath, f"research/{sub}/{rel}")
                if is_case:
                    add_case(sub, gname, art)
                else:
                    add_article(sub, sub, industry, art)

    # raw/research/<code>/
    raw_dir = os.path.join(WIKI_DIR, "raw", "research")
    if os.path.isdir(raw_dir):
        for sub in sorted(os.listdir(raw_dir)):
            subpath = os.path.join(raw_dir, sub)
            if not os.path.isdir(subpath) or sub == 'articles':
                continue
            is_case = sub in CASE_GROUP_NAMES
            gname = CASE_GROUP_NAMES.get(sub, sub)
            industry = stock_info.get(sub, '其他')
            for rel, fpath in iter_md(subpath):
                art = read_article(fpath, f"raw/research/{sub}/{rel}")
                if is_case:
                    add_case(sub, gname, art)
                else:
                    add_article(sub, sub, industry, art)

    # 通用文章
    general = []
    general_dir = os.path.join(WIKI_DIR, "research", "articles")
    if os.path.isdir(general_dir):
        for cat in sorted(os.listdir(general_dir)):
            catpath = os.path.join(general_dir, cat)
            if not os.path.isdir(catpath):
                continue
            for rel, fpath in iter_md(catpath):
                art = read_article(fpath, f"research/articles/{cat}/{rel}")
                art['category'] = cat
                general.append(art)

    raw_gen_dir = os.path.join(WIKI_DIR, "raw", "research", "articles")
    if os.path.isdir(raw_gen_dir):
        for rel, fpath in iter_md(raw_gen_dir):
            art = read_article(fpath, f"raw/research/articles/{rel}")
            art['category'] = 'raw'
            general.append(art)

    # synthesis 中命中标的的 → 归入标的组；未命中 → general
    for art in list(general):
        if art['category'] != 'synthesis':
            continue
        fn = os.path.basename(art['path']).lower()
        matched = None
        for kw, sname in synthesis_stock_map.items():
            if kw in fn:
                matched = sname
                break
        if matched:
            general.remove(art)
            if matched not in stock_info:
                stock_info[matched] = '其他'
            add_article(matched, matched, stock_info.get(matched, '其他'), art)

    # general 主题聚类
    for art in general:
        art['topic'] = classify_topic(art)

    return groups, cases, general

# ---------------------------------------------------------------------------
# 页面树（把每组文章按其物理目录组织成文件夹结构）
# ---------------------------------------------------------------------------

class Folder:
    __slots__ = ('name', 'subs', 'files')
    def __init__(self, name=''):
        self.name = name      # '' 表示组根
        self.subs = {}        # name -> Folder
        self.files = []       # article list

    def insert(self, parts, article):
        if len(parts) == 1:
            self.files.append(article)
        else:
            n = parts[0]
            if n not in self.subs:
                self.subs[n] = Folder(n)
            self.subs[n].insert(parts[1:], article)

    def md_count(self):
        return len(self.files) + sum(s.md_count() for s in self.subs.values())

def raw_top_name(gid, articles):
    """该组 raw 文章在组树/输出目录里使用的顶层文件夹名"""
    if any(a['path'].startswith('research/' + gid + '/' + RAW_DIR_NAMES[0] + '/') for a in articles):
        return RAW_DIR_NAMES[1]   # 真实 wiki 目录恰好叫「原始资料」时才退避
    return RAW_DIR_NAMES[0]

def build_group_tree(articles, gid):
    root = Folder('')
    raw_name = raw_top_name(gid, articles)
    raw_folder = None
    for art in articles:
        p = art['path']
        if p.startswith(f"research/{gid}/"):
            parts = p[len(f"research/{gid}/"):].split('/')
            root.insert(parts, art)
        elif p.startswith(f"raw/research/{gid}/"):
            if raw_folder is None:
                raw_folder = Folder(raw_name)
                root.subs[raw_name] = raw_folder
            parts = p[len(f"raw/research/{gid}/"):].split('/')
            raw_folder.insert(parts, art)
        else:  # synthesis 等映射进组的文章 → 组根
            root.files.append(art)
    # 排序：顶层目录按配置/字典序；文件按名称
    def sort_folder(f, is_top):
        if f.subs:
            names = list(f.subs.keys())
            if is_top and gid in GROUP_DIR_ORDER:
                prio = {n: i for i, n in enumerate(GROUP_DIR_ORDER[gid])}
                names.sort(key=lambda n: (prio.get(n, 100), n))
            else:
                names.sort()
            f.subs = {n: f.subs[n] for n in names}
        f.files.sort(key=lambda a: os.path.basename(a['path']))
        for sf in f.subs.values():
            sort_folder(sf, False)
    sort_folder(root, True)
    # 原始资料强制垫底
    if raw_name in root.subs:
        rf = root.subs.pop(raw_name)
        root.subs[raw_name] = rf
    return root

def ordered_tabs(gid, root):
    """带 gid 顺序的组页标签列表：配置目录优先 → 其余字典序 → 概览 → 原始资料。返回 [(name, count)]"""
    wiki_names = [n for n in root.subs if not is_raw_dir(n)]
    prio = GROUP_DIR_ORDER.get(gid, [])
    order = [n for n in prio if n in wiki_names] + \
            [n for n in sorted(wiki_names) if n not in prio]
    tabs = [(n, root.subs[n].md_count()) for n in order]
    if root.files:
        tabs.append(('概览', len(root.files)))
    for n in root.subs:
        if is_raw_dir(n):
            tabs.append((n, root.subs[n].md_count()))
    return tabs

# ---------------------------------------------------------------------------
# HTML 片段
# ---------------------------------------------------------------------------

CSS = """\
:root{--bg:#f6f7f9;--text:#1a1a1a;--blue:#2563eb;--border:#e0e0e0}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased}
.topbar{background:#16181d;color:#fff;padding:9px 20px;position:sticky;top:0;z-index:200;display:flex;justify-content:space-between;align-items:center;gap:12px}
.topbar .logo{color:#fff;text-decoration:none;font-size:16px;font-weight:600;white-space:nowrap}
.topbar .logo b{color:#3b82f6}
.topbar .crumb{color:#9aa0a6;font-size:12px;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.topbar .crumb a{color:#c0c4cc;text-decoration:none;margin:0 2px}
.topbar .crumb a:hover{color:#fff;text-decoration:underline}
.topbar .topnav a{color:#c0c4cc;text-decoration:none;font-size:12px;padding:5px 12px;border:1px solid #4a4f5a;border-radius:6px;margin-left:8px;white-space:nowrap}
.topbar .topnav a:hover{color:#fff;border-color:#8a8f9a;background:#262a33}
.wrap{max-width:1040px;margin:0 auto;padding:18px 20px 70px}
.filters{display:flex;gap:8px;padding:2px 0 12px;flex-wrap:wrap}
.filters input{flex:1;min-width:200px;padding:8px 12px;border:1px solid #d6d9e0;border-radius:8px;font-size:14px;outline:none}
.filters input:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.12)}
.section-title{font-size:15px;font-weight:700;color:#333;margin:24px 0 12px;padding-bottom:8px;border-bottom:2px solid #3b82f6;display:flex;align-items:center;gap:8px}
.section-title .count{font-size:12px;color:#9aa0a6;font-weight:400}
.grp{background:#fff;border:1px solid var(--border);border-radius:12px;padding:14px 16px;margin-bottom:14px;box-shadow:0 1px 2px rgba(0,0,0,.03)}
/* 首页标的区：网格排布，一行 4-5 个（无文件夹 chip）；案例/多学科整宽条 */
#sec-stocks{display:flex;flex-direction:column;gap:18px}
#sec-stocks .secgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(188px,1fr));gap:10px;align-items:stretch}
#sec-stocks .grp{margin-bottom:0;min-width:0;background:#f2f7ff;border:1px solid #b7cdea;box-shadow:0 1px 2px rgba(30,60,120,.06)}
#sec-stocks .grp-hd{margin-bottom:0;flex-direction:column;align-items:stretch;gap:6px}
#sec-stocks .grp-hd a.name{display:block;text-align:center;white-space:normal;overflow:visible}
#sec-stocks .grp-hd .pill{align-self:center}
#sec-general{display:grid;grid-template-columns:repeat(auto-fill,minmax(188px,1fr));gap:10px;align-items:stretch}
#sec-general .grp{margin-bottom:0;min-width:0;background:#f2f7ff;border:1px solid #b7cdea;box-shadow:0 1px 2px rgba(30,60,120,.06)}
#sec-general .grp-hd{margin-bottom:0;flex-direction:column;align-items:stretch;gap:6px}
#sec-general .grp-hd a.name{display:block;text-align:center;white-space:normal;overflow:visible}
#sec-general .grp-hd .pill{align-self:center}
.pill.topic{background:#ede9fe;color:#6d28d9}
#sec-cases{display:grid;grid-template-columns:repeat(auto-fill,minmax(188px,1fr));gap:10px;align-items:stretch}
#sec-cases .grp{margin-bottom:0;min-width:0;background:#fbf6fe;border:1px solid #e2c9f0;box-shadow:0 1px 2px rgba(120,40,160,.06)}
#sec-cases .grp-hd{margin-bottom:0;flex-direction:column;align-items:stretch;gap:6px}
#sec-cases .grp-hd a.name{display:block;text-align:center;white-space:normal;overflow:visible}
#sec-cases .grp-hd .pill{align-self:center}
.grp-hd{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:12px}
.grp-hd h2{font-size:16px;font-weight:700}
.grp-hd a.name{font-size:16px;font-weight:700;color:inherit;text-decoration:none}
.grp-hd a.name:hover{color:var(--blue)}
.grp-hd .go{margin-left:auto;font-size:12px;color:var(--blue);text-decoration:none;font-weight:500}
.grp-hd .go:hover{text-decoration:underline}
.pill{font-size:11px;padding:2px 9px;border-radius:10px;background:#eef2ff;color:#4338ca;font-weight:500;white-space:nowrap}
.pill.industry{background:#eef0f3;color:#555}
.pill.case{background:#f6ecf9;color:#8e24aa}
.dirchips{display:flex;gap:8px;flex-wrap:wrap}
.chip{display:inline-flex;align-items:center;gap:6px;text-decoration:none;border:1px solid #e0e2e8;background:#fafbfc;border-radius:9px;padding:6px 13px;font-size:13px;color:#333;transition:all .15s}
.chip:hover{border-color:#3b82f6;color:var(--blue);background:#f3f7ff}
.chip b{color:var(--blue);font-weight:600;font-size:12px}
.chip.raw{border-style:dashed}
.page-hd{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin:4px 0 4px}
.page-hd h1{font-size:24px;font-weight:800;letter-spacing:.3px}
.meta-line{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:6px 0 12px;color:#888;font-size:13px;border-bottom:1px solid #eee;padding-bottom:10px}
.tabbar{display:flex;gap:2px;flex-wrap:wrap;margin:0 0 16px}
.tabbtn{border:1px solid transparent;background:transparent;padding:8px 16px;font-size:14px;color:#555;cursor:pointer;border-radius:8px 8px 0 0;white-space:nowrap;transition:all .12s;font-weight:500}
.tabbtn:hover{color:var(--blue);background:#eef4ff}
.tabbtn.active{color:var(--blue);background:#fff;border-color:#d0d5e0;border-bottom-color:#fff;font-weight:700;box-shadow:0 -1px 4px rgba(0,0,0,.04)}
.tabbtn .n{opacity:.6;font-size:11px;margin-left:5px;font-weight:600}
.panel{display:none}
.panel.active{display:block;background:#fff;border:1px solid #e6e8ee;border-radius:0 12px 12px 12px;padding:16px}
.panel .subhead{font-size:13px;font-weight:700;color:#555;margin:6px 0 10px;display:flex;align-items:center;gap:8px}
.panel .subhead:first-child{margin-top:0}
.panel .subhead .count{font-size:12px;color:#9aa0a6;font-weight:400}
.subhead{border-bottom:1px dashed #eceff4;padding-bottom:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:9px}
.card{display:block;background:#fbfcfe;border:1px solid #e7eaf0;border-radius:10px;padding:11px 13px;text-decoration:none;color:var(--text);transition:box-shadow .15s,border-color .15s,transform .1s}
.card:hover{box-shadow:0 3px 12px rgba(30,60,120,.1);border-color:#b9cdf5;transform:translateY(-1px)}
.card .t{font-size:13.5px;font-weight:600;line-height:1.4;color:#1f2937}
.card:hover .t{color:var(--blue)}
.card .meta{display:flex;gap:6px;align-items:center;margin-top:7px;flex-wrap:wrap}
.card .sum{font-size:12px;color:#8a909a;margin-top:6px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.tag{font-size:10px;padding:1px 7px;border-radius:4px;font-weight:600;white-space:nowrap}
.tag-wiki{background:#e7f6ec;color:#1f8a4c}
.tag-raw{background:#fdf0e2;color:#d97706}
.tag-concept{background:#e3f0fd;color:#1d6fd0}
.tag-entity{background:#fde8ee;color:#d6336c}
.tag-synthesis{background:#f4e9fb;color:#9333ea}
.tag-paper{background:#e1f4f3;color:#0f766e}
.date{font-size:11px;color:#a4a9b1}
.page-title{font-size:24px;margin:4px 0 8px;font-weight:800;line-height:1.35}
.md{font-size:15px;color:#20242c}
.md h1{font-size:21px;margin:24px 0 10px;line-height:1.4}
.md h2{font-size:17px;margin:22px 0 10px;padding-bottom:4px;border-bottom:1px solid #eef0f4;line-height:1.4}
.md h3{font-size:15px;margin:18px 0 8px}
.md h4,.md h5{font-size:14px;margin:14px 0 6px}
.md p{margin:10px 0}
.md blockquote{border-left:3px solid #3b82f6;padding:6px 14px;margin:12px 0;background:#f6f8fc;color:#4b5563;border-radius:0 6px 6px 0}
.md ul,.md ol{padding-left:26px;margin:10px 0}
.md li{margin:4px 0}
.md table{border-collapse:collapse;width:100%;margin:14px 0;font-size:13px;display:block;overflow-x:auto}
.md th,.md td{border:1px solid #dde0e6;padding:6px 10px;text-align:left}
.md th{background:#f4f5f7;font-weight:600}
.md code{background:#f0f1f4;padding:1px 5px;border-radius:3px;font-size:13px}
.md pre{background:#f4f5f8;padding:14px;border-radius:8px;overflow-x:auto;font-size:13px;margin:14px 0}
.md pre code{background:none;padding:0}
.md a{color:#1d6fd0}
.md img{max-width:100%}
.md hr{border:none;border-top:1px solid #e8eaef;margin:18px 0}
.backrow{display:flex;gap:16px;flex-wrap:wrap;margin-top:30px;padding-top:14px;border-top:1px solid #e6e8ee}
.backrow a{color:#555;text-decoration:none;font-size:13px}
.backrow a:hover{color:var(--blue)}
.no-results{display:none;text-align:center;padding:50px 20px;color:#9aa0a6}
.empty{color:#9aa0a6;font-size:13px;padding:24px 8px}
@media (max-width:768px){.wrap{padding:12px}.grid{grid-template-columns:1fr}#sec-stocks{gap:14px}.secgrid,#sec-general,#sec-cases{grid-template-columns:1fr}.md table{display:block}.topbar .crumb{display:none}.tabbar{overflow-x:auto;flex-wrap:nowrap}.tabbtn{padding:7px 12px;font-size:13px}}
"""

def kind_tag(kind):
    m = {'wiki': 'tag-wiki', 'raw': 'tag-raw', 'concept': 'tag-concept',
         'entity': 'tag-entity', 'synthesis': 'tag-synthesis', 'paper': 'tag-paper'}
    label = {'wiki': 'Wiki', 'raw': '原始', 'concept': '概念', 'entity': '人物',
             'synthesis': '综合', 'paper': '参考'}.get(kind, kind)
    return '<span class="tag ' + m.get(kind, 'tag-wiki') + '">' + label + '</span>'

def card_html(art, from_file):
    href = posix_rel(from_file, art['_out'])
    s = ('<a class="card" href="' + esc(href) + '">'
         '<div class="t">' + esc(art['title']) + '</div>'
         '<div class="meta">' + kind_tag(art['kind']))
    if art.get('date'):
        s += '<span class="date">' + esc(art['date']) + '</span>'
    s += '</div>'
    if art.get('summary'):
        s += '<div class="sum">' + esc(art['summary']) + '</div>'
    s += '</a>'
    return s

def chip_html(text, n, href, raw=False):
    cls = 'chip raw' if raw else 'chip'
    return ('<a class="' + cls + '" href="' + esc(href) + '">' + esc(text) +
            ' <b>' + str(n) + '</b></a>')

def topbar_html(from_file, crumbs):
    """crumbs: (label, target) 或 (label, target, fragment)。fragment 不带 '#'，如 'dir=主题'。"""
    home = posix_rel(from_file, OUT_HOME)
    crumb = '<a href="' + esc(home) + '">投研 Wiki</a>'
    for c in crumbs:
        url = posix_rel(from_file, c[1])
        if len(c) > 2 and c[2]:
            url += '#' + c[2]
        crumb += ' › <a href="' + esc(url) + '">' + esc(c[0]) + '</a>'
    return ('<div class="topbar"><a class="logo" href="' + esc(home) + '">投研<b>Wiki</b></a>'
            '<div class="crumb">' + crumb + '</div>'
            '<div class="topnav"><a href="' + esc(posix_rel(from_file, os.path.join(BASE, 'report', 'index.html'))) + '">📊 Value Line</a></div></div>')

def head_html(title):
    return ('<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            '<title>' + esc(title) + '</title>'
            '<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>'
            '<style>' + CSS + '</style></head><body>')

# ---------------------------------------------------------------------------
# 生成：组页（标的 / 投资案例，单页 Tab 切换）+ 每篇文章的阅读页
# ---------------------------------------------------------------------------

def article_layout(art, gid, raw_name):
    """返回 (tab名, 相对组根的目录链 seg)。seg 也决定文章 HTML 的物理输出位置。"""
    p = art['path']
    if p.startswith('research/' + gid + '/'):
        d = os.path.dirname(p[len('research/' + gid + '/'):])
        seg = [x for x in d.split('/') if x]
        return (seg[0] if seg else '概览'), seg
    if p.startswith('raw/research/' + gid + '/'):
        d = os.path.dirname(p[len('raw/research/' + gid + '/'):])
        inner = [x for x in d.split('/') if x]
        seg = [raw_name] + inner
        return raw_name, seg
    return '概览', []

def group_article_page(art, seg, out, display_name, group_idx):
    md_file = os.path.join(WIKI_DIR, art['path'].replace('/', os.sep))
    body_b64 = base64.b64encode(art['body'].encode('utf-8')).decode('ascii')
    tab = seg[0] if seg else '概览'
    back_target = posix_rel(out, group_idx) + '#dir=' + quote(tab)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    html = head_html(art['title'])
    html += topbar_html(out, [(display_name, group_idx), (art['title'], out)])
    html += '<div class="wrap">'
    html += '<h1 class="page-title">' + esc(art['title']) + '</h1>'
    html += '<div class="meta-line">' + kind_tag(art['kind'])
    if art.get('date'):
        html += '<span class="date">' + esc(art['date']) + '</span>'
    html += '<span style="margin-left:auto;color:#b0b5bd">' + esc(os.path.dirname(art['path'])) + '</span></div>'
    html += '<div class="md" id="md"></div>'
    html += '<div class="backrow"><a href="' + esc(back_target) + '">← 返回 ' + esc(tab) + '</a>'
    html += '<a href="' + esc(posix_rel(out, group_idx)) + '">目录</a>'
    html += '<a href="' + esc(posix_rel(out, OUT_HOME)) + '">首页</a>'
    html += '<a href="' + esc(posix_rel(out, md_file)) + '" style="margin-left:auto">原文文件 ↗</a></div>'
    html += '</div>'
    html += ('<script>var S="' + body_b64 + '";'
             'function dec(s){return decodeURIComponent(Array.prototype.map.call(atob(s),function(c){return "%"+("00"+c.charCodeAt(0).toString(16)).slice(-2)}).join(""))};'
             'var el=document.getElementById("md");'
             'if(window.marked){el.innerHTML=marked.parse(dec(S));}else{el.textContent=dec(S);}'
             '</script></body></html>')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

def panel_sections(folder_or_rootfiles):
    """把某标签下的文章整理为 [(小节标题或'', [articles]), …]，按目录层级展示。"""
    items = []

    def walk(folder, heading):
        if folder.files:
            items.append((heading, folder.files))
        for name, sub in folder.subs.items():
            walk(sub, name if not heading else heading + ' / ' + name)

    if isinstance(folder_or_rootfiles, Folder):
        walk(folder_or_rootfiles, '')
    else:
        if folder_or_rootfiles:
            items.append(('', folder_or_rootfiles))
    return items

TAB_JS = """\
<script>(function(){
var btns=[].slice.call(document.querySelectorAll('.tabbtn'));
var panels=[].slice.call(document.querySelectorAll('.panel'));
function first(){return btns.length?btns[0].getAttribute('data-dir'):'';}
function activate(dir){
  if(!dir){dir=first();}
  btns.forEach(function(b){b.classList.toggle('active',b.getAttribute('data-dir')===dir);});
  panels.forEach(function(p){var isActive=p.getAttribute('data-dir')===dir; p.classList.toggle('active',isActive); p.style.display=isActive?'block':'none';});
}
function fromHash(){
  var h=(location.hash||'').replace(/^#/,'');
  try{h=decodeURIComponent(h);}catch(e){}
  var m=h.match(/(?:^|&)dir=([^&]*)/);
  return m?m[1]:'';
}
btns.forEach(function(b){b.addEventListener('click',function(e){e.preventDefault();activate(this.getAttribute('data-dir'));});});
window.addEventListener('hashchange',function(){var d=fromHash();if(d)activate(d);});
activate(fromHash());
})();</script>"""

def generate_group(scope, gid, info):
    group_out_dir = os.path.join(VIEW_DIR, scope, gid)
    group_idx = os.path.join(group_out_dir, 'index.html')
    display_name = info.get('name', gid) if scope == 'cases' else gid
    is_case = scope == 'cases'

    raw_name = raw_top_name(gid, info['articles'])
    # 每篇文章的 tab / 输出路径
    for art in info['articles']:
        art['_tab'], seg = article_layout(art, gid, raw_name)
        art['_seg'] = seg
        stem = safe_stem(os.path.splitext(os.path.basename(art['path']))[0])
        art['_out'] = os.path.join(group_out_dir, *seg, stem + '.html')

    root = build_group_tree(info['articles'], gid)
    tabs = ordered_tabs(gid, root)

    # 1) 文章阅读页
    written = []
    for art in info['articles']:
        group_article_page(art, art['_seg'], art['_out'], display_name, group_idx)
        written.append(art['_out'])

    # 2) 组页（单页 Tab）
    total = sum(c for _, c in tabs)
    html = head_html(display_name)
    html += topbar_html(group_idx, [(display_name, group_idx)])
    html += '<div class="wrap">'
    html += '<div class="page-hd"><h1>' + esc(display_name) + '</h1>'
    if is_case:
        html += '<span class="pill case">作者案例</span>'
    else:
        ind = info.get('industry', '其他')
        style = INDUSTRY_STYLE.get(ind, INDUSTRY_STYLE_DEFAULT)
        html += ('<span class="pill industry" style="' + style + '">' + esc(ind) + '</span>')
    html += '<span style="font-size:12px;color:#9aa0a6">' + str(total) + ' 篇</span></div>'
    html += '<div class="meta-line">文件夹标签点击即切换，无需跳转 · 点击文章进入阅读</div>'
    html += '<div class="tabbar">'
    for name, cnt in tabs:
        html += ('<button class="tabbtn" data-dir="' + esc(name) + '">' +
                 esc(name) + '<span class="n">' + str(cnt) + '</span></button>')
    html += '</div>'

    for name, cnt in tabs:
        panel = '<div class="panel" data-dir="' + esc(name) + '">'
        if name == '概览':
            sections = panel_sections(root.files)
        else:
            sections = panel_sections(root.subs[name])
        n_items = 0
        for heading, arts in sections:
            n_items += len(arts)
            if heading:
                panel += '<div class="subhead">' + esc(heading) + ' <span class="count">' + str(len(arts)) + ' 篇</span></div>'
            panel += '<div class="grid">'
            for art in arts:
                panel += card_html(art, group_idx)
            panel += '</div>'
        if not n_items:
            panel += '<div class="empty">（暂无内容）</div>'
        panel += '</div>'
        html += panel

    html += '</div>' + TAB_JS + '</body></html>'
    os.makedirs(group_out_dir, exist_ok=True)
    with open(group_idx, 'w', encoding='utf-8') as f:
        f.write(html)
    written.append(group_idx)
    return written

# ---------------------------------------------------------------------------
# 生成：通用文章（多学科）
# ---------------------------------------------------------------------------

def general_article_page(art, out):
    md_file = os.path.join(WIKI_DIR, art['path'].replace('/', os.sep))
    body_b64 = base64.b64encode(art['body'].encode('utf-8')).decode('ascii')
    topic = art.get('topic', '通用')
    frag = 'dir=' + quote(topic)
    back_target = posix_rel(out, GENERAL_IDX) + '#' + frag
    html = head_html(art['title'])
    html += topbar_html(out, [('多学科', GENERAL_IDX), (topic, GENERAL_IDX, frag)])
    html += '<div class="wrap">'
    html += '<h1 class="page-title">' + esc(art['title']) + '</h1>'
    html += '<div class="meta-line">' + kind_tag(art['kind'])
    if art.get('date'):
        html += '<span class="date">' + esc(art['date']) + '</span>'
    html += '<span style="margin-left:auto;color:#b0b5bd">' + esc(os.path.dirname(art['path'])) + '</span></div>'
    html += '<div class="md" id="md"></div>'
    html += '<div class="backrow"><a href="' + esc(back_target) + '">← 返回 ' + esc(topic) + '</a>'
    html += '<a href="' + esc(posix_rel(out, GENERAL_IDX)) + '">目录</a>'
    html += '<a href="' + esc(posix_rel(out, OUT_HOME)) + '">首页</a>'
    html += '<a href="' + esc(posix_rel(out, md_file)) + '" style="margin-left:auto">原文文件 ↗</a></div>'
    html += '</div>'
    html += ('<script>var S="' + body_b64 + '";'
             'function dec(s){return decodeURIComponent(Array.prototype.map.call(atob(s),function(c){return "%"+("00"+c.charCodeAt(0).toString(16)).slice(-2)}).join(""))};'
             'var el=document.getElementById("md");'
             'if(window.marked){el.innerHTML=marked.parse(dec(S));}else{el.textContent=dec(S);}'
             '</script></body></html>')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

def general_topic_order(general):
    """按 topic_order 优先、其余字典序，返回出现过的主题列表。"""
    grouped = {}
    for art in general:
        grouped.setdefault(art.get('topic', '其他'), []).append(art)
    ordered = []
    for t in topic_order:
        if t in grouped:
            ordered.append(t)
    for t in sorted(grouped):
        if t not in ordered:
            ordered.append(t)
    return grouped, ordered

def general_group_page(general):
    """多学科整组页：view/general/index.html，主题当顶栏 tab，就地切换（与标的组页同构）。"""
    grouped, ordered = general_topic_order(general)
    total = len(general)
    html = head_html('多学科')
    html += topbar_html(GENERAL_IDX, [('多学科', GENERAL_IDX)])
    html += '<div class="wrap">'
    html += '<div class="page-hd"><h1>多学科</h1><span class="pill case">通用知识</span>'
    html += '<span style="font-size:12px;color:#9aa0a6">' + str(total) + ' 篇</span></div>'
    html += '<div class="meta-line">主题标签点击即切换，无需跳转 · 点击文章进入阅读</div>'
    html += '<div class="tabbar">'
    for t in ordered:
        html += ('<button class="tabbtn" data-dir="' + esc(t) + '">' +
                 esc(t) + '<span class="n">' + str(len(grouped[t])) + '</span></button>')
    html += '</div>'
    for t in ordered:
        panel = '<div class="panel" data-dir="' + esc(t) + '">'
        panel += '<div class="grid">'
        for art in grouped[t]:
            panel += card_html(art, GENERAL_IDX)
        panel += '</div></div>'
        html += panel
    html += '</div>' + TAB_JS + '</body></html>'
    os.makedirs(GENERAL_VIEW_DIR, exist_ok=True)
    with open(GENERAL_IDX, 'w', encoding='utf-8') as f:
        f.write(html)
    return GENERAL_IDX

def generate_general(general):
    written = []
    for art in general:
        cat = art.get('category', 'other')
        out = os.path.join(VIEW_DIR, 'general', cat,
                           safe_stem(os.path.splitext(os.path.basename(art['path']))[0]) + '.html')
        art['_out'] = out
        general_article_page(art, out)
        written.append(out)
    written.append(general_group_page(general))
    return written

# ---------------------------------------------------------------------------
# 生成：首页
# ---------------------------------------------------------------------------

def home_section_blocks(pairs, from_file, scope):
    """pairs: [(gid, info)] 已排好序。scope 决定 stocks/cases 分组链接。
    首页块只保留 名称+标签（无"进入"、无文件夹 chip），一行可放 4-5 个标的。"""
    html = ''
    for gid, info in pairs:
        group_idx = os.path.join(VIEW_DIR, scope, gid, 'index.html')
        data = (info.get('name', gid) + ' ' + info.get('industry', '') + ' ' + gid + ' ' +
                ' '.join(a['title'] for a in info['articles'])).lower()
        html += '<div class="grp" data-search="' + esc(data) + '">'
        html += '<div class="grp-hd"><a class="name" href="' + esc(posix_rel(from_file, group_idx)) + '">' + esc(info.get('name', gid)) + '</a>'
        if scope == 'cases':
            html += '<span class="pill case">作者案例</span>'
        else:
            ind = info.get('industry', '其他')
            style = INDUSTRY_STYLE.get(ind, INDUSTRY_STYLE_DEFAULT)
            html += ('<span class="pill industry" style="' + style + '">' +
                     esc(ind) + '</span>')
        html += '</div>'
        html += '</div>'
    return html

def home_section_stock_blocks(groups, from_file):
    """按行业分组，同类标的连排成一行网格；不同行业用独立行隔开（类与类之间留空）。"""
    by_ind = {}
    for gid, info in groups.items():
        by_ind.setdefault(info.get('industry', '其他'), []).append((gid, info))
    html = ''
    for ind in sorted(by_ind):
        order = sorted(by_ind[ind], key=lambda x: x[0])
        html += '<div class="secgrid">' + home_section_blocks(order, from_file, 'stocks') + '</div>'
    return html

def home_section_case_blocks(cases, from_file):
    order = sorted(cases.items(), key=lambda x: x[0])
    return home_section_blocks(order, from_file, 'cases')

def home_section_general(general, from_file):
    """多学科每个主题分类单独一张卡片（不再整体显示 多学科 + 总篇数 的大标题块）。"""
    if not general:
        return ''
    grouped, ordered = general_topic_order(general)
    idx_href = posix_rel(from_file, GENERAL_IDX)
    html = ''
    for topic in ordered:
        arts = grouped[topic]
        href = idx_href + '#dir=' + quote(topic)
        search_text = topic + ' ' + ' '.join(a['title'] for a in arts)
        html += '<div class="grp" data-search="' + esc(search_text).lower() + '">'
        html += '<div class="grp-hd"><a class="name" href="' + esc(href) + '">' + esc(topic) + '</a>'
        html += '<span class="pill topic">' + str(len(arts)) + ' 篇</span></div>'
        html += '</div>'
    return html

def build_home(groups, cases, general):
    stocks_html = home_section_stock_blocks(groups, OUT_HOME)
    cases_html = home_section_case_blocks(cases, OUT_HOME)
    general_html = home_section_general(general, OUT_HOME)

    body = head_html('投研 Wiki')
    body += topbar_html(OUT_HOME, [])
    body += '<div class="wrap">'
    body += '<div class="filters"><input type="text" id="search" placeholder="搜索标的 / 标签 / 文章标题…（正文检索请在打开文章后按 Ctrl+F）" oninput="doSearch()"></div>'
    body += '<div class="section-title" data-sec="stocks">📌 按标的 <span class="count" id="cstocks"></span></div>'
    body += '<div id="sec-stocks">' + stocks_html + '</div>'
    if cases_html:
        body += '<div class="section-title" data-sec="cases">💼 投资案例 <span class="count" id="ccases"></span></div>'
        body += '<div id="sec-cases">' + cases_html + '</div>'
    if general_html:
        body += '<div class="section-title" data-sec="general">📖 多学科 <span class="count" id="cgeneral"></span></div>'
        body += '<div id="sec-general">' + general_html + '</div>'
    body += '<div class="no-results" id="noresults">没有匹配的内容</div>'
    body += '</div>'
    body += ('<script>'
             'function doSearch(){'
             'var q=(document.getElementById("search").value||"").trim().toLowerCase();'
             'var secs={stocks:0,cases:0,general:0},total=0;'
             'document.querySelectorAll(".grp").forEach(function(g){'
             '  var hit=!q||(g.getAttribute("data-search")||"").indexOf(q)>-1;'
             '  g.style.display=hit?"":"none";'
             '  if(hit){total++;var sec=g.closest("#sec-stocks")?"stocks":(g.closest("#sec-cases")?"cases":"general");secs[sec]++;}'
             '});'
             'document.querySelectorAll(".secgrid").forEach(function(g){'
             '  var any=false;'
             '  g.querySelectorAll(".grp").forEach(function(c){if(c.style.display!=="none")any=true;});'
             '  g.style.display=any?"":"none";'
             '});'
             '["stocks","cases","general"].forEach(function(k){'
             '  var t=document.querySelector(\'.section-title[data-sec="\'+k+\'"]\');'
             '  if(!t)return;'
             '  t.style.display=secs[k]>0?"flex":"none";'
             '  var c=document.getElementById("c"+k);'
             '  if(c)c.textContent=secs[k]+" 个分组";'
             '});'
             'document.getElementById("noresults").style.display=total?"none":"block";'
             '}'
             'document.getElementById("search").addEventListener("keydown",function(e){if(e.key==="Escape"){this.value="";doSearch();}});'
             'doSearch();'
             '</script>')
    body += '</body></html>'
    with open(OUT_HOME, 'w', encoding='utf-8') as f:
        f.write(body)

# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main():
    print("扫描 research-wiki/ ...")
    groups, cases, general = scan_wiki()
    n_stock = sum(len(v['articles']) for v in groups.values())
    n_case = sum(len(v['articles']) for v in cases.values())
    print(f"  标的: {len(groups)} 个 ({n_stock} 篇) | 投资案例: {len(cases)} 个专题 ({n_case} 篇) | 通用: {len(general)} 篇")

    print("生成页面 ...")
    os.makedirs(VIEW_DIR, exist_ok=True)
    written = []
    for gid, info in groups.items():
        written += generate_group('stocks', gid, info)
    for gid, info in cases.items():
        written += generate_group('cases', gid, info)
    written += generate_general(general)
    build_home(groups, cases, general)
    written.append(OUT_HOME)

    print(f"  共生成 {len(written)} 个页面")
    print(f"  首页: {OUT_HOME}")
    print(f"  页面目录: {VIEW_DIR}")

if __name__ == '__main__':
    main()
