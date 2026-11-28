"""
preview_layouts.py — 排版实验预览页（不影响正式站点）

用途：把「知识库 / 基金经理」tab 的 13 篇真实文章，用 5 套不同形态的版式
渲染到 research-wiki/view/knowledge/layout-preview.html，顶部按钮就地切换，
供人工选型。选型确定后再改 scripts/generate_wiki_index.py 正式落地。

硬约束（针对用户反馈）：
  · 正文标题 >= 17px，摘要 >= 14px，颜色不浅于 #6b7280（不再一片小灰字）
  · 不出现「外层容器 + 分组框 + 卡片框」的嵌套边框，靠字号/留白/细线分级

运行：
    .venv\\Scripts\\python scripts\\preview_layouts.py
"""
import os
import re
import sys
import json

import generate_wiki_index as G

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PREVIEW = os.path.join(G.GENERAL_VIEW_DIR, 'layout-preview.html')
CAT = '基金经理'


def clean_md(s):
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)
    s = re.sub(r'\[\[([^\]]+)\]\]', r'\1', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
    s = re.sub(r'^一句话核心\s*[：:]\s*', '', s)
    return s.strip().rstrip('.').strip()


def core_text(art):
    """取 md 里完整的「一句话核心」段落，不截断（正式页面的 120 字截断太碎）。"""
    m = re.search(r'\*\*一句话核心\*\*\s*[：:]\s*(.+)', art.get('body', ''))
    if m:
        return clean_md(m.group(1))
    return clean_md(art.get('summary', ''))


def build_data():
    _, _, general = G.scan_wiki()
    arts = [a for a in general if a.get('category') == CAT]
    people = {}
    for art in arts:
        person = G.person_of_general(art)
        stem = os.path.splitext(os.path.basename(art['real_path']))[0]
        out = os.path.join(G.GENERAL_VIEW_DIR, art.get('catdir') or CAT,
                           G.safe_stem(stem) + '.html')
        href = G.posix_rel(PREVIEW, out) if os.path.isfile(out) else ''
        people.setdefault(person, []).append({
            't': art['title'],
            'd': art.get('date', ''),
            'c': core_text(art),
            'h': href,
        })
    data = []
    for name, items in sorted(people.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        items.sort(key=lambda x: x['d'], reverse=True)
        data.append({'name': name, 'arts': items})
    return data


PAGE = r"""<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>排版实验 · 知识库 / 基金经理</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#fff;color:#111827;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.bar{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.96);backdrop-filter:blur(8px);border-bottom:1px solid #e5e7eb;padding:11px 26px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.bar .brand{font-size:14px;font-weight:800;white-space:nowrap}
.bar .brand em{font-style:normal;color:#9ca3af;font-weight:500;margin-left:6px}
.sw{display:flex;gap:6px;flex-wrap:wrap}
.sw button{border:1px solid #e5e7eb;background:#fff;border-radius:20px;padding:7px 15px;font-size:13px;cursor:pointer;color:#374151;font-family:inherit;transition:.15s}
.sw button:hover{border-color:#111827}
.sw button.on{background:#111827;border-color:#111827;color:#fff;font-weight:700}
.bar .meta{margin-left:auto;font-size:12px;color:#9ca3af;white-space:nowrap}
.bar .meta a{color:#2563eb;margin-left:12px}
.note{max-width:1080px;margin:0 auto;padding:16px 28px 0;font-size:13px;color:#6b7280;line-height:1.7}
.note b{color:#111827;font-size:14px}
.stage{max-width:1080px;margin:0 auto;padding:24px 28px 100px}

/* 1 大字清单：无卡片、无边框，靠字号 + 细线 + 留白分级 */
.L-type .group{margin:0 0 42px}
.L-type .group-h{display:flex;align-items:baseline;gap:12px;border-bottom:2px solid #111827;padding-bottom:9px;margin-bottom:4px}
.L-type .group-h .nm{font-size:27px;font-weight:800;letter-spacing:.5px}
.L-type .group-h .ct{font-size:13px;color:#6b7280}
.L-type .row{display:grid;grid-template-columns:96px 1fr;gap:18px;padding:14px 0;border-bottom:1px solid #eceef2}
.L-type .row:hover .tt{color:#2563eb}
.L-type .dt{font-size:13px;color:#374151;font-variant-numeric:tabular-nums;padding-top:4px;letter-spacing:.3px}
.L-type .tt{display:block;font-size:18px;font-weight:650;line-height:1.45}
.L-type .cr{display:block;font-size:14px;color:#4b5563;line-height:1.65;margin-top:5px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}

/* 2 双栏人物页：左侧索引，右侧只放一个人的文章，摘要完整 */
.L-split .duo{display:grid;grid-template-columns:210px 1fr;gap:46px}
.L-split .side{position:sticky;top:76px;align-self:start}
.L-split .side .p{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 12px;font-size:14.5px;color:#374151;border-radius:8px;cursor:pointer}
.L-split .side .p:hover{background:#f3f4f6}
.L-split .side .p.on{background:#111827;color:#fff;font-weight:700}
.L-split .side .p small{font-size:12px;opacity:.6;font-weight:500}
.L-split .pn{font-size:34px;font-weight:800;letter-spacing:.5px;border-bottom:2px solid #111827;padding-bottom:12px;margin-bottom:4px}
.L-split .pn small{font-size:14px;font-weight:500;color:#6b7280;margin-left:14px;letter-spacing:0}
.L-split .it{display:block;padding:22px 0;border-bottom:1px solid #e8eaee}
.L-split .it:hover .tt{color:#2563eb}
.L-split .it .dt{font-size:13px;color:#6b7280;letter-spacing:.3px}
.L-split .it .tt{font-size:21px;font-weight:700;line-height:1.4;margin-top:5px}
.L-split .it .cr{font-size:15px;color:#374151;line-height:1.8;margin-top:10px}

/* 3 引文墙：一句话核心是主角，标题作者退成署名 */
.L-quote .qgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));column-gap:44px}
.L-quote .q{display:block;padding:22px 0 20px;border-bottom:1px solid #e8eaee}
.L-quote .q:hover .cr{color:#1d4ed8}
.L-quote .mark{font:44px/0.7 Georgia,serif;color:#c9ced8}
.L-quote .cr{font-family:Georgia,"Songti SC","SimSun",serif;font-size:17px;line-height:1.75;color:#1f2937;margin:10px 0 13px;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.L-quote .by{font-size:12.5px;color:#6b7280;line-height:1.6}
.L-quote .by b{color:#111827;font-size:13px}

/* 4 横向看板：一人一列，13 篇一屏可扫 */
.L-board .board{display:flex;overflow-x:auto;padding-bottom:18px;scrollbar-color:#cbd5e1 transparent}
.L-board .col{min-width:255px;max-width:255px;padding:0 22px;border-left:1px solid #e5e7eb}
.L-board .col:first-child{padding-left:0;border-left:none}
.L-board .cn{font-size:20px;font-weight:800;display:flex;align-items:baseline;gap:9px;margin-bottom:16px}
.L-board .cn small{font-size:12px;color:#6b7280;font-weight:500}
.L-board .it{display:block;margin-bottom:22px}
.L-board .it:hover .tt{color:#2563eb}
.L-board .it .dt{font-size:12px;color:#6b7280}
.L-board .it .tt{font-size:15.5px;font-weight:650;line-height:1.5;margin-top:4px}
.L-board .it .cr{font-size:13.5px;color:#4b5563;line-height:1.65;margin-top:5px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}

/* 5 封面墙：纯 CSS 封面，视觉优先，hover 出摘要 */
.L-cover .covers{display:grid;grid-template-columns:repeat(auto-fill,minmax(232px,1fr));gap:18px}
.L-cover .cv{position:relative;min-height:206px;border-radius:14px;padding:22px;color:#fff;overflow:hidden;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 6px 18px rgba(15,23,42,.12);transition:transform .18s,box-shadow .18s}
.L-cover .cv:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(15,23,42,.2)}
.L-cover .yr{position:absolute;right:-8px;top:-26px;font-size:98px;font-weight:800;opacity:.13;letter-spacing:-6px;line-height:1}
.L-cover .pn{position:relative;font-size:12px;letter-spacing:2px;opacity:.86}
.L-cover .tt{position:relative;font-size:19px;font-weight:750;line-height:1.45}
.L-cover .cr{position:relative;font-size:12px;line-height:1.6;opacity:0;max-height:0;overflow:hidden;transition:opacity .2s,max-height .2s}
.L-cover .cv:hover .cr{opacity:.92;max-height:76px}

@media(max-width:820px){
 .bar{padding:10px 14px}.note,.stage{padding-left:14px;padding-right:14px}
 .L-type .row{grid-template-columns:1fr;gap:2px}.L-split .duo{grid-template-columns:1fr;gap:22px}
 .L-split .side{position:static;display:flex;overflow-x:auto;gap:4px}.L-split .side .p{white-space:nowrap}
 .L-quote .qgrid,.L-cover .covers{grid-template-columns:1fr}
}
</style></head><body>
<div class="bar">
  <span class="brand">排版实验<em>知识库 / 基金经理 · 13 篇真实数据</em></span>
  <div class="sw">
    <button data-k="type">1 大字清单</button>
    <button data-k="split">2 双栏人物页</button>
    <button data-k="quote">3 引文墙</button>
    <button data-k="board">4 横向看板</button>
    <button data-k="cover">5 封面墙</button>
  </div>
  <span class="meta">按 1–5 切换<a href="index.html">看原版 →</a></span>
</div>
<div class="note">当前：<b id="cur"></b> · <span id="hint"></span></div>
<div id="stage" class="stage"></div>
<script>
const DATA=__DATA__;
const META={
 type:{name:'大字清单',hint:'标题 18px / 摘要 14px #4b5563 / 零边框零标签，作者名 27px 做分节'},
 split:{name:'双栏人物页',hint:'点左侧人名切换 · 标题 21px / 摘要 15px 完整不截断'},
 quote:{name:'引文墙',hint:'一句话核心 17px 衬线体当主角，标题与作者退成署名行'},
 board:{name:'横向看板',hint:'一人一列横向滚动，13 篇一屏全见，列间只有细竖线'},
 cover:{name:'封面墙',hint:'纯 CSS 封面卡，鼠标悬停展开摘要；视觉优先、无卡片白底'}
};
const PAL=[['#1e3a5f','#3f74a8'],['#1b4d3e','#37836a'],['#5b3a1f','#a4713a'],['#3b2b63','#7256a8'],['#333b45','#697586'],['#6b2f3a','#b05a68'],['#1f4f5e','#3f8a94'],['#4a4326','#8a7c3c'],['#2f3a6b','#5c68b0'],['#4a2f52','#8c5a91']];
let cur='type',sel=DATA.length?DATA[0].name:'';
const h=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const href=a=>a.h?'href="'+h(a.h)+'"':'href="#"';
const flat=()=>DATA.flatMap((g,gi)=>g.arts.map(a=>Object.assign({},a,{p:g.name,gi:gi})));
const byDate=arr=>arr.sort((x,y)=>String(y.d).localeCompare(String(x.d)));
const VIEWS={};
VIEWS.type=()=>DATA.map(g=>`<section class="group">
 <div class="group-h"><span class="nm">${h(g.name)}</span><span class="ct">${g.arts.length} 篇</span></div>
 ${g.arts.map(a=>`<a class="row" ${href(a)}><span class="dt">${h(a.d)}</span><span><span class="tt">${h(a.t)}</span><span class="cr">${h(a.c)}</span></span></a>`).join('')}
</section>`).join('');
VIEWS.split=()=>{const g=DATA.find(x=>x.name===sel)||DATA[0];if(!g)return'';return `<div class="duo">
 <aside class="side">${DATA.map(x=>`<div class="p ${x.name===sel?'on':''}" data-p="${h(x.name)}"><span>${h(x.name)}</span><small>${x.arts.length}</small></div>`).join('')}</aside>
 <main class="main"><div class="pn">${h(g.name)}<small>${g.arts.length} 篇</small></div>
 ${g.arts.map(a=>`<a class="it" ${href(a)}><div class="dt">${h(a.d)}</div><div class="tt">${h(a.t)}</div><div class="cr">${h(a.c)}</div></a>`).join('')}</main></div>`};
VIEWS.quote=()=>`<div class="qgrid">${byDate(flat()).map(a=>`<a class="q" ${href(a)}><div class="mark">“</div><div class="cr">${h(a.c)}</div><div class="by"><b>${h(a.p)}</b> · ${h(a.d)} · ${h(a.t)}</div></a>`).join('')}</div>`;
VIEWS.board=()=>`<div class="board">${DATA.map(g=>`<div class="col"><div class="cn">${h(g.name)}<small>${g.arts.length} 篇</small></div>${g.arts.map(a=>`<a class="it" ${href(a)}><div class="dt">${h(a.d)}</div><div class="tt">${h(a.t)}</div><div class="cr">${h(a.c)}</div></a>`).join('')}</div>`).join('')}</div>`;
VIEWS.cover=()=>`<div class="covers">${byDate(flat()).map(a=>{const c=PAL[a.gi%PAL.length];return `<a class="cv" ${href(a)} style="background:linear-gradient(135deg,${c[0]},${c[1]})"><span class="yr">${h(String(a.d).slice(0,4))}</span><span class="pn">${h(a.p)}</span><span class="tt">${h(a.t)}</span><span class="cr">${h(a.c)}</span></a>`}).join('')}</div>`;
function render(){
 const s=document.getElementById('stage');
 s.className='stage L-'+cur;
 s.innerHTML=VIEWS[cur]();
 document.getElementById('cur').textContent=META[cur].name;
 document.getElementById('hint').textContent=META[cur].hint;
 document.querySelectorAll('.sw button').forEach(b=>b.classList.toggle('on',b.dataset.k===cur));
}
document.addEventListener('click',e=>{
 const b=e.target.closest('.sw button');if(b){cur=b.dataset.k;render();return;}
 const p=e.target.closest('.side .p');if(p){sel=p.dataset.p;render();return;}
});
document.addEventListener('keydown',e=>{const keys=['type','split','quote','board','cover'];if(e.key>='1'&&e.key<='5'){cur=keys[+e.key-1];render();}});
render();
</script></body></html>
"""


def main():
    data = build_data()
    n = sum(len(g['arts']) for g in data)
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    html = PAGE.replace('__DATA__', payload)
    os.makedirs(G.GENERAL_VIEW_DIR, exist_ok=True)
    with open(PREVIEW, 'w', encoding='utf-8') as f:
        f.write(html)
    linked = sum(1 for g in data for a in g['arts'] if a['h'])
    print(f'  {CAT}: {n} 篇 / {len(data)} 个作者分组，{linked} 篇已链接到站内阅读页')
    print(f'  预览页: {PREVIEW}')


if __name__ == '__main__':
    main()
