"""
generate_report.py — 从 report_data.json 生成自包含 HTML (Value Line 标准三栏布局)
参照: Timberland Co. 价值线标准版
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "report_data.json"), encoding="utf-8") as f:
    DATA = json.load(f)

DATA_JS = json.dumps(DATA, ensure_ascii=False)

HTML = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1280">
<title>Value Line — {DATA['meta']['name_en']} {DATA['meta']['code']}.{DATA['meta']['market']}</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:Arial,Helvetica,sans-serif;font-size:10px;line-height:1.25;color:#000;width:1280px;margin:0 auto;background:#fff}}
.container{{display:grid;grid-template-columns:275px 1fr;min-height:100vh;border-top:1px solid #000;border-bottom:1px solid #000;padding:4px 0}}

/* ===== 左栏 ===== */
.left-col{{border-right:1px solid #000;padding:4px 5px;font-size:9px}}
.left-col .sec{{margin-bottom:5px}}
.left-col .sec-title{{font-weight:700;font-size:9.5px;border-bottom:1px solid #000;padding-bottom:1px;margin-bottom:3px;text-transform:uppercase}}
.left-col table{{width:100%;border-collapse:collapse;font-size:8.5px}}
.left-col td{{padding:1px 2px}}
.left-col .r{{text-align:right}}
.left-col .b{{font-weight:700}}
.left-col p{{margin:2px 0;font-size:8.5px}}

/* ===== 中栏 ===== */
.center-col{{border-right:1px solid #000;padding:4px 6px;display:flex;flex-direction:column}}

/* Header */
.header{{display:flex;align-items:center;justify-content:space-between;padding:2px 8px;border-bottom:2px solid #000;margin:0 0 2px 0}}
.header .code{{font-weight:700;font-size:17px;font-family:"Times New Roman",serif}}
.header .info{{text-align:right;font-size:8.5px;line-height:1.3}}
.header .info .v{{font-weight:700;font-size:10px}}
.header .ratings{{display:flex;gap:10px;font-size:8px;text-align:center}}
.header .ratings span{{font-weight:700;display:block;font-size:10px}}

/* Chart section */
.chart-area{{margin:2px 0;border-bottom:1px solid #000}}
.chart-title{{font-weight:700;font-size:9px;margin-bottom:0px}}
.chart-row{{display:flex}}
.chart-box{{flex:1;height:260px}}
.return-box{{width:150px;font-size:8.5px;padding:3px 5px}}
.return-box table{{width:100%;border-collapse:collapse;margin-bottom:3px}}
.return-box td,.return-box th{{padding:1px 3px;text-align:right;font-size:8px}}
.return-box th{{border-bottom:1px solid #999}}
.return-box .note{{font-size:7.5px;color:#666;line-height:1.2}}

/* 23-line table */
.stat-table{{margin:2px 0;overflow-x:auto}}
.stat-table table{{border-collapse:collapse;font-size:8.5px;width:100%;table-layout:fixed}}
.stat-table th,.stat-table td{{text-align:right;padding:2px 8px;border-right:1px solid #ddd;white-space:nowrap;line-height:1.3}}
.stat-table th{{background:#eee;font-weight:700;font-size:8px}}
.stat-table td:first-child,.stat-table th:first-child{{text-align:left;width:110px;white-space:nowrap}}
.stat-table tr:nth-child(even){{background:#fafafa}}

/* 对齐表 — Yearly High/Low 和 K线轴年份 */
.align-table{{margin:0;padding:1px 8px}}
.align-table table{{border-collapse:collapse;font-size:8px;width:100%;table-layout:fixed}}
.align-table th,.align-table td{{text-align:right;padding:0 3px;border-right:1px solid transparent}}
.align-table th:first-child,.align-table td:first-child{{text-align:left;width:110px}}
.stat-table .sep td{{border-bottom:2px solid #000;padding:0}}
.stat-table .sep-sm td{{border-bottom:1px solid #999}}

/* Analyst */
.analyst{{margin:4px 0;padding:4px 6px;font-size:9px;line-height:1.35;border-top:1px solid #000}}
.analyst b{{display:block;margin-bottom:2px}}
.analyst p{{margin-bottom:3px}}
</style>
</head>
<body>
<div id="app"></div>
<script>
var DATA = {DATA_JS};

(function(){{
  var d=DATA, M=d.metric_defs, Y=d.years, MT=d.data, QT=d.quarterly,
      cs=d.capital_structure||{{}}, cp=d.current_position||{{}},
      ar=d.annual_rates||{{}}, qt=d.quarterly||{{}},
      yhl=d.yearly_hl||[], pos=d.position||{{}}, v=d.validation||{{}};
  // 统一年份: 使用 indicators 全量, Yearly HL 缺失则空
  var yhlMap={{}}; yhl.forEach(function(h){{yhlMap[h.year]=h;}});
  var allY=Y.slice(-10);  // 最多10年 (不足则全部)
  var spot=d.spot||{{}};
  var latestYr=Y[Y.length-1], ly=MT[latestYr]||{{}};
  var meta=d.meta||{{}};
  var stockName=meta.name_en||meta.name||'N/A';
  var stockCode=meta.code||'';
  var stockMarket=meta.market||'';
  var currency=meta.currency||'¥';
  var indexName=meta.index_name||'HSI';
  var indexNameCn=meta.index_name_cn||'恒生指数';
  var app=document.getElementById('app');
  var html='';

  html+='<div class="container">';

  // ========================
  // 左栏
  // ========================
  html+='<div class="left-col">';

  // Business — VL风格，分段可读
  var rev=d.revenue_structure||{{}}, ch=(rev.by_channel||[]), ip=(rev.by_ip||[]), rg=(rev.by_region||[]);
  var desc=cs.business_desc||'';
  var bizP=[], bizHtml='';
  // P1: 业务描述
  if(desc){{
    var dot=desc.indexOf('。');
    bizP.push(dot>0?desc.substring(0,dot):desc.substring(0,80));
  }}
  // P2: IP+渠道+地域 (营收结构)
  var p2=[];
  if(ip.length>0){{
    var ipTop=ip.slice(0,3).map(function(c){{return c.name+' '+c.pct+'%';}}).join('、');
    p2.push('核心IP：'+ipTop);
  }}
  if(ch.length>0){{
    var chTop=ch.slice(0,3).map(function(c){{return c.name+' '+c.pct+'%';}}).join('、');
    p2.push('渠道：'+chTop);
  }}
  if(rg.length>0){{
    var rgTop=rg.slice(0,3).map(function(c){{return c.name+' '+c.pct+'%';}}).join('、');
    p2.push('地域：'+rgTop);
  }}
  if(p2.length) bizP.push(p2.join('；'));
  // P3: 折旧/员工/CEO/注册地/网站
  // P3: 折旧/员工
  var p3=[];
  var depr=ly.DEPRECIATION, revs=ly.OPERATE_INCOME;
  if(depr&&revs) p3.push('折旧率'+(depr/revs*100).toFixed(1)+'%');
  if(cs.employee_count) p3.push('员工'+(cs.employee_count/10000).toFixed(1)+'万人（'+latestYr+'）');
  if(p3.length) bizP.push(p3.join('。'));
  // P4: CEO/注册地/网站
  var p4=[];
  if(meta.ceo) p4.push('首席执行官：'+meta.ceo);
  if(meta.inc) p4.push('注册地：'+meta.inc);
  if(meta.website) p4.push(meta.website);
  if(p4.length) bizP.push(p4.join('。'));
  bizHtml='<span style="font-weight:700">BUSINESS:</span> '+bizP[0];
  if(bizP[1]) bizHtml+='<br>'+bizP[1];
  if(bizP[2]) bizHtml+='<br>'+bizP[2];
  if(bizP[3]) bizHtml+='<br>'+bizP[3];
  html+='<div style="font-size:10px;line-height:1.4;margin-bottom:4px">'+bizHtml+'</div>';

  // Capital Structure — 完全参考VL截图布局
  var csDate=Y[Y.length-1]+'-12-31', csUnit=cs.unit||'亿';
  html+='<div class="sec">';
  html+='<div style="border-bottom:1px solid #000;margin-bottom:2px"></div>';
  html+='<div style="font-size:10px;font-weight:700;margin-bottom:2px">CAPITAL STRUCTURE as of '+csDate+'</div>';
  html+='<table style="width:100%;border-collapse:collapse;font-size:10px;line-height:1.5">';
  // Row 1: Total Debt | Due in 5 Yrs
  html+='<tr><td style="white-space:nowrap;font-weight:700">Total Debt</td><td style="text-align:right;font-weight:700;padding-right:8px">'+(cs.total_debt||0).toFixed(1)+' '+csUnit+'</td>';
  html+='<td style="width:8px"></td><td style="white-space:nowrap;font-weight:700">Due in 5 Yrs</td><td style="text-align:right;font-weight:700">'+(cs.due_in_5yr||0).toFixed(1)+' '+csUnit+'</td></tr>';
  // Row 2: LT Debt | LT Interest
  html+='<tr><td style="white-space:nowrap;font-weight:700">LT Debt</td><td style="text-align:right;font-weight:700;padding-right:8px">'+(cs.lt_debt||0).toFixed(1)+' '+csUnit+'</td>';
  html+='<td></td><td style="white-space:nowrap;font-weight:700">LT Interest</td><td style="text-align:right;font-weight:700">'+(cs.total_int||0).toFixed(2)+' '+csUnit+'</td></tr>';
  // Row 3: (coverage)
  html+='<tr><td colspan="5" style="font-size:10px;color:#000;padding-left:0">(Total interest coverage: '+cs.coverage+')</td></tr>';
  // Row 4: (% of Cap'l) — 右对齐
  html+='<tr><td colspan="5" style="text-align:right;font-size:10px;color:#000;padding-left:0">('+cs.lt_debt_pct+'% of Cap\u2019l)</td></tr>';
  // Row 5: Pfd Stock | None (Leases/Pension不适用港股)
  html+='<tr><td style="white-space:nowrap;font-weight:700">Pfd Stock</td><td style="text-align:right;font-weight:700;padding-right:8px">'+(cs.pfd_stock||'None')+'</td><td></td><td></td><td></td></tr>';
  html+='</table>';
  // Common Stock 单独块
  html+='<div style="margin-top:4px;font-size:10px;line-height:1.4">';
  html+='<div style="display:flex;justify-content:space-between"><span style="font-weight:700">Common Stock</span><span style="font-weight:700;margin-left:2px">'+cs.common_shares_str+' shs.</span></div>';
  html+='<div style="text-align:left;font-weight:700">as of '+csDate+'</div>';
  html+='</div>';
  // MARKET CAP
  html+='<div style="margin-top:4px;font-size:10px;line-height:1.4">';
  html+='<div style="display:flex;justify-content:space-between;font-weight:700"><span>MARKET CAP:</span><span>'+(cs.mkt_cap||0).toFixed(0)+' '+csUnit+' ('+cs.cap_label+')</span></div>';
  html+='</div>';
  html+='<div style="border-bottom:1px solid #000;margin-top:4px"></div>';
  html+='</div>';

  // Current Position — VL格式
  var cpYears=cp.years||[];
  html+='<div class="sec" style="border-bottom:1px solid #000;padding-bottom:4px;margin-bottom:6px">';
  html+='<div style="margin-bottom:2px"></div>';
  // 标题行: 标题 + 列名同行
  html+='<table style="width:100%;border-collapse:collapse;font-size:10px;line-height:1.4">';
  html+='<tr style="font-weight:700">';
  html+='<td style="white-space:nowrap">CURRENT POSITION</td>';
  cpYears.forEach(function(yr, i){{
    var label=(i===cpYears.length-1)?yr+'-12-31':yr;
    html+='<td style="text-align:right">'+label+'</td>';
  }});
  html+='</tr>';
  // 单位行
  html+='<tr><td style="font-size:8px;color:#000;font-weight:700">(亿)</td>';
  cpYears.forEach(function(){{html+='<td></td>';}});
  html+='</tr>';
  // 数据行
  var cpDef=[
    ['Cash Assets',0,0],['Receivables',1,0],['Inventory (Avg Cst)',2,0],['Other',3,0],
    ['Current Assets',4,1],
    ['Accts Payable',5,0],['Debt Due',6,0],['Other',7,0],
    ['Current Liab.',8,1]
  ];
  var cpItems=cp.items||[];
  cpDef.forEach(function(d){{
    var label=d[0], idx=d[1], isBold=d[2];
    if(isBold){{
      html+='<tr style="font-weight:700">';
    }}else{{
      html+='<tr>';
    }}
    html+='<td style="white-space:nowrap">'+label+'</td>';
    var item=cpItems[idx];
    cpYears.forEach(function(yr){{
      var v=(item&&item[yr]!=null)?item[yr].toFixed(1):'—';
      html+='<td style="text-align:right;'+(isBold?'border-top:1px solid #000':'')+'">'+v+'</td>';
    }});
    html+='</tr>';
  }});
  html+='</table></div>';

  // Annual Rates of Change — VL标准 (per sh, 复合增长率)
  var has10=ar.has_10yr;
  var colKeys=has10?['10yr','5yr','3yr','1yr']:['5yr','3yr','1yr'];
  var colParts=colKeys.map(function(k){{
    var m=k.match(/^(\\d+)(yr)$/);
    return m?[m[1]+' Yrs.']:[k];
  }});
  html+='<div class="sec" style="border-bottom:1px solid #000;padding-bottom:0;margin-bottom:0">';
  html+='<table style="width:100%;border-collapse:collapse;font-size:10px;line-height:1.3">';
  // 标题行: ANNUAL RATES + 列名第一行
  html+='<tr><td style="white-space:nowrap;font-weight:700">ANNUAL RATES</td>';
  colParts.forEach(function(p){{html+='<td style="text-align:right;font-weight:700">Past</td>';}});
  html+='</tr>';
  // 副标题行: of change (per sh) + 列名第二行
  html+='<tr><td style="font-size:9px;color:#666">of change (per sh)</td>';
  colParts.forEach(function(p){{html+='<td style="text-align:right;font-weight:700">'+p[0]+'</td>';}});
  html+='</tr>';
  // 数据行
  var arData=[
    ['Revenues',ar.sales],['"Cash Flow"',ar.cashflow],['Earnings',ar.earnings],
    ['Dividends',ar.dividends],['Book Value',ar.book_value]
  ];
  arData.forEach(function(a){{
    var v=a[1]||{{}};
    html+='<tr><td style="white-space:nowrap;font-weight:700">'+a[0]+'</td>';
    colKeys.forEach(function(k){{
      var pct=(v[k]!=null)?v[k].toFixed(1)+'%':'—';
      html+='<td style="text-align:right">'+pct+'</td>';
    }});
    html+='</tr>';
  }});
  html+='</table></div>';

  // 季度/半年度表 — VL三表紧排, 单 table + 垂直分割线
  var hasQ=(qt.sales||[])[0]&&qt.sales[0].has_quarter;
  function renderQSection(title, data, decimal, hasQq, isFirst){{
    if(!data||!data.length) return '';
    var show=data.slice(-5);
    // Section title
    var sepStyle=isFirst?'':'border-top:1px solid #999;';
    var h='<tr><td style="font-weight:700;'+sepStyle+'padding-top:4px">Year</td>';
    h+='<td colspan="4" style="text-align:center;font-weight:700;border-left:2px solid #000;border-right:2px solid #000;'+sepStyle+'padding-top:4px">'+title+'</td>';
    h+='<td style="border-left:2px solid #000;'+sepStyle+'padding-top:4px"></td></tr>';
    // Header
    h+='<tr style="font-weight:700">';
    h+='<td style="width:16%;border-bottom:1px solid #000"></td>';
    var qLabels=['Q1','Q2','Q3','Q4'];
    qLabels.forEach(function(l,i){{
      var s='width:14%;text-align:right;padding-right:3px;border-bottom:1px solid #000';
      if(i===0) s+=';border-left:2px solid #000;padding-left:3px;text-align:left';
      if(i===3) s+=';padding-right:3px';
      h+='<td style="'+s+'">'+l+'</td>';
    }});
    h+='<td style="width:16%;text-align:right;padding-right:3px;font-weight:700;border-left:2px solid #000;border-bottom:1px solid #000">Full Year</td></tr>';
    // Data rows
    show.forEach(function(r){{
      h+='<tr>';
      h+='<td style="font-weight:700">'+r.year+'</td>';
      if(hasQq){{
        var vs=[r.q1,r.q2,r.q3,r.q4,r.full];
        vs.forEach(function(v,i){{
          var s='text-align:right;padding-right:3px';
          if(i===0) s='text-align:left;border-left:2px solid #000;padding-left:3px';
          if(i===4) s+=';font-weight:700;border-left:2px solid #000;padding-left:3px';
          h+='<td style="'+s+'">'+(v!=null?v.toFixed(decimal):'—')+'</td>';
        }});
      }}else{{
        h+='<td style="text-align:left;color:#999;border-left:2px solid #000;padding-left:3px;padding-right:3px">—</td>';
        h+='<td style="text-align:right;padding-right:3px">'+(r.q1!=null?r.q1.toFixed(decimal):'—')+'</td>';
        h+='<td style="text-align:right;color:#999;padding-right:3px">—</td>';
        h+='<td style="text-align:right;padding-right:3px">'+(r.q3!=null?r.q3.toFixed(decimal):'—')+'</td>';
        h+='<td style="text-align:right;font-weight:700;border-left:2px solid #000;padding-left:3px;padding-right:3px">'+(r.full!=null?r.full.toFixed(decimal):'—')+'</td>';
      }}
      h+='</tr>';
    }});
    return h;
  }}
  html+='<div class="sec" style="border-bottom:1px solid #000;padding-bottom:2px;margin-bottom:2px">';
  html+='<table style="width:100%;border-collapse:collapse;font-size:10px;line-height:1.3">';
  html+=renderQSection('QUARTERLY REVENUES (亿)', qt.sales, 1, hasQ, true);
  html+=renderQSection('EARNINGS PER SHARE', qt.eps, 2, hasQ, false);
  html+=renderQSection('QUARTERLY DIVIDENDS PAID', qt.dividends, 3, hasQ, false);
  html+='</table>';
  if(!hasQ) html+='<div style="border-top:1px solid #000;font-size:8px;color:#666;margin-top:3px;padding-top:3px">*港股仅披露半年报，Q2/Q4暂无数据。</div>';
  html+='</div>';

  html+='</div>'; // end left-col

  // ========================
  // 中栏
  // ========================
  html+='<div class="center-col">';

  // ===== VL Header: HTML table 2行, rowspan=2跨两行 =====
  var medianPE=spot.median_pe||null;
  var trailingPE=spot.pe||ly.PE_AVG||null;
  var relPE=ly.PE_RELATIVE||(pos.pe?pos.pe.avg:null);
  var divYld=spot.div_yield||ly.DIV_YIELD;

  html+='<table class="header" style="border-collapse:collapse;border-bottom:2px solid #000;margin:0 0 2px 0;width:100%"><tr>';

  // Row 1
  html+='<td rowspan="2" style="vertical-align:middle;padding:5px 10px;border-right:1px solid #999">';
  html+='<span class="code" style="font-size:18px;font-weight:700;line-height:1">'+(stockName||'N/A')+'</span> ';
  html+='<span style="font-size:9px;font-weight:700;color:#000;line-height:1">'+stockCode+'.'+stockMarket+'</span></td>';

  html+='<td style="vertical-align:bottom;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">RECENT</td>';
  html+='<td rowspan="2" style="vertical-align:middle;text-align:center;padding:0 10px;border-right:1px solid #999;font-size:18px;font-weight:700">'+(spot.price!=null?spot.price.toFixed(2):'—')+'</td>';
  html+='<td style="vertical-align:bottom;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">P/E</td>';
  html+='<td rowspan="2" style="vertical-align:middle;text-align:center;padding:0 10px;font-size:17px;font-weight:700">'+(trailingPE!=null?trailingPE.toFixed(1):'—')+'</td>';
  // ⑥ (Trailing: xx 第一行
  html+='<td style="vertical-align:bottom;padding:2px 8px;line-height:1;border-right:1px solid #999;font-size:9px;font-weight:700">';
  if(trailingPE){{html+='(Trailing:'+trailingPE.toFixed(1)+')';}}
  html+='</td>';
  html+='<td style="vertical-align:bottom;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">RELATIVE</td>';
  html+='<td rowspan="2" style="vertical-align:middle;text-align:center;padding:0 10px;border-right:1px solid #999;font-size:17px;font-weight:700">'+(relPE!=null?relPE.toFixed(2):'—')+'</td>';
  html+='<td style="vertical-align:bottom;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">DIV’D</td>';
  html+='<td rowspan="2" style="vertical-align:middle;text-align:center;padding:0 10px;font-size:17px;font-weight:700">'+(divYld!=null?divYld.toFixed(1)+'%':'—')+'</td>';

  html+='</tr><tr>';

  // Row 2
  html+='<td style="vertical-align:top;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">PRICE</td>';
  html+='<td style="vertical-align:top;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">RATIO</td>';
  html+='<td style="vertical-align:top;padding:2px 8px;line-height:1;border-right:1px solid #999;font-size:9px;font-weight:700">';
  if(medianPE){{html+='(Median:'+medianPE.toFixed(1)+')';}}
  html+='</td>';
  html+='<td style="vertical-align:top;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">P/E RATIO</td>';
  html+='<td style="vertical-align:top;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">YLD</td>';

  html+='</tr></table>';

  // Chart



  // Chart
  var kl=d.kline, hsi=d.index_kline||[];

  // ========== 统一表格: Yearly High/Low + K线 + 23-line ==========
  var showYears=allY;  // 最多10年
  var yrCount=showYears.length;
  html+='<table style="table-layout:fixed;width:100%;border-collapse:collapse;font-size:8.5px">';
  var tdStyle='border-right:1px solid #ddd;padding:2px 8px', thStyle='border-right:1px solid #ddd;text-align:right;padding:2px 8px';
  
  // Row 1: High
  html+='<tr><td style="padding:0 3px;'+tdStyle+'">High</td>';
  showYears.forEach(function(yr){{
    var hl=yhlMap[yr];
    html+='<td style="text-align:right;padding:0 3px;'+tdStyle+'">'+(hl?hl.high:'—')+'</td>';
  }});
  html+='</tr>';
  // Row 3: Low
  html+='<tr><td style="padding:0 3px;'+tdStyle+'">Low</td>';
  showYears.forEach(function(yr){{
    var hl=yhlMap[yr];
    html+='<td style="text-align:right;padding:0 3px;'+tdStyle+'">'+(hl?hl.low:'—')+'</td>';
  }});
  html+='</tr>';
  
  // Row 4: K线图行 — LEGENDS + % TOT. RETURN(左) + 图表(右)
  // chart 260px + volume 30px = 290px flex容器, Percent用margin-top:auto沉底
  html+='<tr><td style="padding:0 3px;vertical-align:top;'+tdStyle+'">';
  html+='<div style="display:flex;flex-direction:column;height:290px;font-size:8px;line-height:1.4">';
  html+='<div>';
  html+='<div style="font-weight:700;font-size:8.5px;margin:2px 0 1px 0">LEGENDS</div>';
  html+='<div style="border-bottom:1px solid #000;margin:2px 0"></div>';
  html+='<div style="font-size:10px;color:#1976D2;line-height:1.1">\u2501\u2501\u2501</div>';
  html+='<div>15.0 x \"Cash Flow\" p sh</div>';
  html+='<div style="margin:4px 0"></div>';
  html+='<div style="font-size:10px;color:#ef232a;line-height:1.1">\u00B7\u00B7\u00B7\u00B7\u00B7\u00B7</div>';
  html+='<div>Relative Price Strength</div>';
  html+='<div style="margin:3px 0"></div>';
  html+='<div>Splits: '+(meta.splits||'None')+'</div><div>Options: '+(meta.options||'No')+'</div>';
  html+='<div style="margin:15px 0 2px 0"></div>';
  html+='<div style="font-weight:700;font-size:8.5px;margin-bottom:2px">% HIST. RETURN</div>';
  html+='<div style="border-bottom:1px solid #000;margin:0 0 2px 0"></div>';
  var trR2=d.total_returns||{{}};
  var trStock2=trR2.stock||{{}};
  var trIndex2=trR2.index||{{}};
  html+='<table style="width:100%;border-collapse:collapse;font-size:8.5px;line-height:1.35;margin:1px 0">';
  html+='<tr><td></td><td style="text-align:right;font-weight:700">THIS</td><td style="text-align:right;font-weight:700">'+indexName+'</td></tr>';
  html+='<tr><td></td><td style="text-align:right;font-weight:700">STOCK</td><td style="text-align:right"></td></tr>';
  html+='<tr><td>1 yr.</td><td style="text-align:right">'+(trStock2['1yr']!=null?trStock2['1yr'].toFixed(1)+'%':'—')+'</td><td style="text-align:right">'+(trIndex2['1yr']!=null?trIndex2['1yr'].toFixed(1)+'%':'—')+'</td></tr>';
  html+='<tr><td>3 yr.</td><td style="text-align:right">'+(trStock2['3yr']!=null?trStock2['3yr'].toFixed(1)+'%':'—')+'</td><td style="text-align:right">'+(trIndex2['3yr']!=null?trIndex2['3yr'].toFixed(1)+'%':'—')+'</td></tr>';
  html+='<tr><td>5 yr.</td><td style="text-align:right">'+(trStock2['5yr']!=null?trStock2['5yr'].toFixed(1)+'%':'—')+'</td><td style="text-align:right">'+(trIndex2['5yr']!=null?trIndex2['5yr'].toFixed(1)+'%':'—')+'</td></tr>';
  html+='</table>';
  html+='</div>';
  html+='</div></td>';
  html+='<td colspan="'+yrCount+'" style="padding:0">';
  html+='<div class="chart-box" id="chart_kline"></div>';
  html+='<div id="chart_volume" style="height:50px;margin-top:6px;position:relative"></div>';
  
  // Row 5: 年份行
  html+='<tr style="border-top:1px solid #000;border-bottom:1px solid #000"><td style="font-size:10px;color:#000;padding:2px 3px;'+tdStyle+'">Year</td>';
  showYears.forEach(function(y){{html+='<td style="text-align:center;font-size:10px;font-weight:700;padding:2px 3px;'+tdStyle+'">'+y+'</td>';}});
  html+='</tr>';
  
  // Row 6+: 24-line metrics
  M.forEach(function(m, idx){{
    var sepBefore=[5];
    var sepAfter=[6,7,10,13,15,17,20,22];
    if(sepBefore.indexOf(m.order)>=0){{
      html+='<tr class="sep"><td colspan="'+(yrCount+1)+'" style="border-bottom:1px solid #000"></td></tr>';
    }}
    html+='<tr>';
    html+='<td style="text-align:left;white-space:nowrap;font-size:9px;font-weight:700;'+tdStyle+'">'+m.name_en+' <span style="font-size:7.5px;color:#666;font-weight:400">'+m.name_cn+'</span></td>';
    showYears.forEach(function(y){{
      var v=(MT[y]||{{}})[m.field];
      var txt='—';
      if(v!=null){{
        if(m.unit==='亿')txt=v.toFixed(1);
        else if(m.unit==='%')txt=v.toFixed(1)+'%';
        else if(m.unit==='元')txt=v.toFixed(2);
        else if(m.unit==='百万股')txt=v.toFixed(0);
        else txt=v.toString();
      }}
      html+='<td style="text-align:right;font-size:8.5px;'+tdStyle+'">'+txt+'</td>';
    }});
    html+='</tr>';
    if(sepAfter.indexOf(m.order)>=0){{
      html+='<tr class="sep"><td colspan="'+(yrCount+1)+'" style="border-bottom:1px solid #000"></td></tr>';
    }}
  }});
  html+='</table>';
  
  // Analyst Commentary — VL标准 300-400字三段式 (占位，后续LLM生成)
  var commentary=[
    '泡泡玛特增速见顶？股价从高点腰斩后何去何从',
    '2026年5月31日 — 泡泡玛特2025年报交出史诗级成绩：营收371.2亿（+185%），每股收益9.58元（+308%），ROE高达57%。但股价自2025年高点HKD 334已回落近半，当前HKD 173.4。是市场提前消化逆天的增长，还是回调创造了入场机会？',
    '细看结构，海外收入占比从20%跃至44%（亚太21.6%+美洲18.3%），"中国IP全球输出"的故事正在兑现。THE MONSTERS独占38%，SKULLPANDA及其他IP形成第二梯队。但2025年的爆发式增长受益于海外门店从0到1的渠道红利——当基数上升后，2026年的增速几乎必然放缓。我们的预测：营收增20%-30%、EPS增15%-25%，取决于拉美和欧洲新市场的爬坡速度。',
    '当前股价对应PE约17倍（经汇率调整），处于历史估值区间的最低10%分位——这在三年营收CAGR 100%的公司中极为罕见。PB 10.4倍位于中位，ROE 57%则属顶级。公司净现金状态，无财务风险，折旧率仅3%。2025年派息CNY 2.38/股，股息率约1.4%，尚有提升空间。综合判断：估值已回归合理甚至偏低，但高基数下增速放缓是必然，建议关注2026年中报的海外同店增速作为验证信号。'
  ];
  html+='<div class="analyst" style="font-size:10px">';
  html+='<span style="font-size:12px;font-weight:700">AI Commentary: '+commentary[0]+'</span>';
  html+='<p style="text-align:justify;margin:4px 0">'+commentary[1]+'</p>';
  html+='<p style="text-align:justify;margin:4px 0">'+commentary[2]+'</p>';
  html+='<p style="text-align:justify;margin:4px 0">'+commentary[3]+'</p>';
  html+='</div>';

  html+='</div>'; // end center-col

  html+='</div>'; // end container
  app.innerHTML=html;

  // ECharts
  setTimeout(function(){{
    // 补齐K线起始前的空年份，对齐指标表列
    var padMonths=[], padOHLC=[], firstKL=kl.length>0?kl[0].date:null;
    if(firstKL && showYears.length>0){{
      var beginYr=parseInt(showYears[0],10), endYr=parseInt(firstKL.substring(0,4),10), endMo=parseInt(firstKL.substring(5,7),10);
      for(var y=beginYr; y<=endYr; y++){{
        var maxM=(y===endYr)?endMo-1:12;
        for(var m=1; m<=maxM; m++){{padMonths.push(y+'-'+(m<10?'0'+m:''+m));padOHLC.push([null,null,null,null]);}}
      }}
    }}
    var dates=padMonths.concat(kl.map(function(k){{return k.date;}})),
        ohlc=padOHLC.concat(kl.map(function(k){{return [Math.log(k.open),Math.log(k.close),Math.log(k.low),Math.log(k.high)];}}));

    // RS line
    var rsStock=[], rsHsi=[], rsDates=[];
    if(hsi.length>0){{
      var hsiMap={{}};
      hsi.forEach(function(h){{hsiMap[h.date]=h.close;}});
      var baseS=null,baseH=null;
      dates.forEach(function(dt){{
        var sc=kl.find(function(k){{return k.date===dt;}});
        var hc=hsiMap[dt];
        if(sc&&hc){{
          if(baseS===null){{baseS=sc.close;baseH=hc;}}
          rsStock.push(baseS?(sc.close/baseS*100).toFixed(1):100);
          rsHsi.push(baseH?(hc/baseH*100).toFixed(1):100);
        }}
      }});
    }}

    var series=[
      {{name:stockName,type:'candlestick',data:ohlc,
        itemStyle:{{color:'#ef232a',color0:'#14b143',borderColor:'#ef232a',borderColor0:'#14b143'}}}}
    ];

    var cfData=d.cf_line||[];
    var cfMap={{}};
    cfData.forEach(function(c){{cfMap[c.date]=c.value;}});
    var cfSeries=dates.map(function(dt){{
      var yr=dt.substring(0,4);
      var v=cfMap[yr];
      return v!=null?Math.log(v):null;
    }});
    if(cfSeries.some(function(v){{return v!=null;}})){{
      series.push({{name:'15x CF',type:'line',data:cfSeries,
        lineStyle:{{type:'solid',color:'#1976D2',width:1.2}},symbol:'none'}});
    }}
    if(rsStock.length>0){{
      series.push({{name:stockName+' (idx)',type:'line',data:rsStock,
        lineStyle:{{color:'#ef232a',width:1.2,type:'dotted'}},symbol:'none',yAxisIndex:1}});
      series.push({{name:indexName+' (idx)',type:'line',data:rsHsi,
        lineStyle:{{color:'#999',width:1,type:'dotted'}},symbol:'none',yAxisIndex:1}});
    }}

    // 年分隔线
    var yearLines=[];
    dates.forEach(function(d,i){{if(d.endsWith('-01'))yearLines.push({{xAxis:i,lineStyle:{{color:'#ccc',width:1,type:'solid'}}}});}});
    series[0].markLine={{silent:true,animation:false,symbol:'none',data:yearLines,label:{{show:false}}}};

    // 对数Y轴范围: 种子序列 [1,1.6,2.4,4,6] × 10^k + 4%缓冲区
    var pVals=kl.map(function(k){{return k.close;}}).filter(function(v){{return v>0;}});
    var pMin=Math.min.apply(null,pVals), pMax=Math.max.apply(null,pVals);
    var lnMin=Math.log(pMin), lnMax=Math.log(pMax), lnDl=lnMax-lnMin;
    var lnBuf=lnDl*0.04;
    var yMin=lnMin-lnBuf, yMax=lnMax+lnBuf;
    // 种子序列生成刻度标签 (自然对数统一)
    var tLo=Math.exp(yMin), tHi=Math.exp(yMax);
    var seeds=[1,1.6,2.4,4,6];
    var ticks=[], pow=Math.pow(10,Math.floor(Math.log(tLo)/Math.LN10)-1);
    while(pow<=tHi*1.1){{
      seeds.forEach(function(m){{
        var v=pow*m; if(v>=tLo&&v<=tHi) ticks.push(v);
      }});
      pow*=10;
    }}
    var logTicks=ticks.map(function(v){{return Math.log(v);}});
    var klineChart=echarts.init(document.getElementById('chart_kline'));
    klineChart.setOption({{
      tooltip:{{trigger:'axis',axisPointer:{{label:{{show:false}}}},valueFormatter:function(v){{return v!=null?'$'+Math.exp(Number(v)).toFixed(2):'-';}}}},
      grid:{{left:0,right:28,top:4,bottom:24}},
      xAxis:{{type:'category',data:dates,boundaryGap:false,
        axisLabel:{{fontSize:7,color:'#333',fontWeight:700,margin:2,
          formatter:function(v){{return v&&v.endsWith('-01')?v.slice(0,4):'';}},
          interval:0,showMinLabel:true,showMaxLabel:true}},
        axisLine:{{show:true,lineStyle:{{color:'#999',width:0.5}}}},
        axisTick:{{show:false}},
        splitLine:{{show:true,lineStyle:{{color:'#ccc',width:0.5}}}}}},
      yAxis:[
        {{type:'value',min:yMin,max:yMax,
          axisLabel:{{fontSize:9,color:'#000',
            formatter:function(v){{var p=Math.exp(v);return p>=100?Math.round(p):p>=10?p.toFixed(0):p.toFixed(1);}}}},position:'right'}},
        {{type:'value',axisLabel:{{fontSize:8,color:'#999'}},splitLine:{{show:false}},position:'left'}}],
      series:series
    }});

    // Monthly Volume % — VL item 11: 按年份匹配股本
    var volData=[], totalShM=ly.TOTAL_SHARES;
    var shByYear={{}};
    showYears.forEach(function(y){{shByYear[y]=(MT[y]||{{}}).TOTAL_SHARES;}});
    var shFallback=shByYear[showYears[showYears.length-1]]||totalShM;
    dates.forEach(function(dt){{
      var k=kl.find(function(k){{return k.date===dt;}});
      var yr=dt.substring(0,4);
      var sh=shByYear[yr]||shFallback;
      if(k&&k.volume&&sh){{
        volData.push(+(k.volume/(sh*1e6)*100).toFixed(2));
      }}else{{volData.push(null);}}
    }});
    var vMax=0;
    volData.forEach(function(v){{if(v!=null&&v>vMax)vMax=v;}});
    // Y轴刻度: 比例缓冲+自适应interval, 向上取整到nice number
    var maxVol=vMax*1.2, interval=maxVol<=5?1:maxVol<=50?5:10;
    var ceilVol=Math.ceil(maxVol/interval)*interval||interval, step=ceilVol/3;
    var volChart=echarts.init(document.getElementById('chart_volume'));
    volChart.setOption({{
      tooltip:{{trigger:'axis',
        formatter:function(p){{var k=kl[p[0].dataIndex],up=k&&k.close>k.open;
          return '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:'+(up?'#ef232a':'#14b143')+';margin-right:4px;vertical-align:middle"></span>PST: '+(p[0].value!=null?p[0].value.toFixed(2)+'%':'-');}}}},
      grid:{{left:0,right:28,top:0,bottom:0,containLabel:false}},
      xAxis:{{type:'category',data:dates,show:false,boundaryGap:false,
        axisPointer:{{show:true,type:'shadow',shadowStyle:{{color:'rgba(25,118,210,.08)'}},label:{{show:false}}}}}},
      yAxis:{{type:'value',position:'left',min:0,max:ceilVol,splitNumber:3,
        axisLabel:{{show:false}},
        splitLine:{{show:false}},
        axisLine:{{show:false}},axisTick:{{show:false}}}},
      series:[{{name:'Vol%',type:'bar',data:volData,
        emphasis:{{itemStyle:{{color:'#ff6600'}}}},
        itemStyle:{{color:function(p){{var d=dates[p.dataIndex];return d&&d.endsWith('-01')?'#7b1fa2':'#1976D2';}}}},barWidth:'60%',
        markLine:{{silent:true,symbol:'none',animation:false,
          data:[{{yAxis:ceilVol,name:'',lineStyle:{{color:'#000',width:3.0,type:'solid'}}}},
                {{yAxis:step*2,name:'',lineStyle:{{color:'#000',width:0.5,type:'solid'}}}},
                {{yAxis:step,name:'',lineStyle:{{color:'#000',width:0.5,type:'solid'}}}}]
        }}}}]
    }});
    // DOM 标签画左侧 Percent/shares/traded — convertToPixel 取刻度 y 像素, 放在 chart_volume 外
    var volCnt=document.getElementById('chart_volume');
    volCnt.style.overflow='visible';
    var vals=[ceilVol,step*2,step], labels=['Percent','shares','traded'];
    var vsDiv=document.createElement('div');
    vsDiv.style.cssText='position:absolute;left:-72px;width:68px;top:0;bottom:0;pointer-events:none;z-index:1';
    vals.forEach(function(v,i){{
      var py=volChart.convertToPixel({{yAxisIndex:0}},v);
      var d=document.createElement('div');
      d.style.cssText='position:absolute;left:0;right:0;top:'+(py||0)+'px;font-size:8.5px;font-weight:700;display:flex;justify-content:space-between;padding-right:4px';
      d.innerHTML='<span>'+labels[i]+'</span><span>'+Math.round(v)+'</span>';
      vsDiv.appendChild(d);
    }});
    volCnt.appendChild(vsDiv);
    // K线图 ↔ 成交量图联动
    klineChart.group='vl'; volChart.group='vl'; echarts.connect('vl');
    // click K线 → 成交量柱高亮 + tooltip
    klineChart.on('click',function(p){{
      volChart.dispatchAction({{type:'downplay',seriesIndex:0}});
      volChart.dispatchAction({{type:'highlight',seriesIndex:0,dataIndex:p.dataIndex}});
      volChart.dispatchAction({{type:'showTip',seriesIndex:0,dataIndex:p.dataIndex}});
    }});
    // click 成交量图空白 → 取消高亮
    volChart.getZr().on('click',function(e){{if(!e.target)volChart.dispatchAction({{type:'downplay',seriesIndex:0}});}});
    klineChart.group='vl'; volChart.group='vl'; echarts.connect('vl');

  }},300);
}})();
</script>
</body>
</html>'''

out_path = os.path.join(BASE, DATA['meta']['name_en'].replace(' ','_')+'.html')
out_alt = os.path.join(os.environ.get("TEMP", os.environ.get("TMP", "/tmp")), "vl_report.html")
try:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(HTML)
except Exception:
    with open(out_alt, "w", encoding="utf-8") as f:
        f.write(HTML)
    out_path = out_alt
print(f"Generated: {out_path} ({len(HTML)} chars)")
print(f"  Layout: Left(275px) + Center(flex) — Value Line classic 2-column")
