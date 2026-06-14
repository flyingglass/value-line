"""
generate_report.py — 从 report_data.json 生成自包含 HTML (Value Line 标准三栏布局)
参照: Timberland Co. 价值线标准版
"""
import json, os, datetime, sys
if sys.platform == 'win32': sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "report_data.json"), encoding="utf-8") as f:
    DATA = json.load(f)

DATA_JS = json.dumps(DATA, ensure_ascii=False)

HTML = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1360">
<title>Value Line — {DATA['meta']['name_en']} {DATA['meta']['code']}.{DATA['meta']['market']}</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:Arial,Helvetica,sans-serif;font-size:10px;line-height:1.25;color:#000;width:1360px;margin:0 auto;background:#fff;-webkit-text-size-adjust:100%}}
.container{{display:grid;grid-template-columns:245px 1fr;border-top:1px solid #000;padding:4px 0}}

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
.chart-box{{flex:1;height:220px}}
.return-box{{width:140px;font-size:8.5px;padding:3px 5px}}
.return-box table{{width:100%;border-collapse:collapse;margin-bottom:3px}}
.return-box td,.return-box th{{padding:1px 3px;text-align:right;font-size:8px}}
.return-box th{{border-bottom:1px solid #999}}
.return-box .note{{font-size:7.5px;color:#666;line-height:1.2}}

/* 23-line table */
.stat-table{{margin:2px 0;overflow-x:auto}}
.stat-table table{{border-collapse:collapse;font-size:8px;width:100%;table-layout:fixed}}
.stat-table th,.stat-table td{{text-align:right;padding:1px 4px;border-right:1px solid #ddd;white-space:nowrap;line-height:1.35}}
.stat-table th{{background:#eee;font-weight:700;font-size:7.5px}}
.stat-table td:first-child,.stat-table th:first-child{{text-align:left;width:130px;white-space:nowrap}}
.stat-table tr:nth-child(even){{background:#fafafa}}

/* 对齐表 — Yearly High/Low 和 K线轴年份 */
.align-table{{margin:0;padding:1px 8px}}
.align-table table{{border-collapse:collapse;font-size:8px;width:100%;table-layout:fixed}}
.align-table th,.align-table td{{text-align:right;padding:0 3px;border-right:1px solid transparent}}
.align-table th:first-child,.align-table td:first-child{{text-align:left;width:130px}}
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
  var allY=Y.slice(-15);  // 最多15年 (不足则全部)
  var spot=d.spot||{{}};
  var latestYr=Y[Y.length-1], ly=MT[latestYr]||{{}};
  var meta=d.meta||{{}};
  var stockName=meta.name_en||meta.name||'N/A';
  var stockCode=meta.code||'';
  var cfMult=d.cf_multiplier||15;
  var pbMult=d.pb_multiplier||1;
  var valMethod=d.valuation_method||'cf';
  var cfLabelStr='x "Cash Flow" p sh';
  var pbLabelStr='x "Book Value" p sh';
  var valLabel=valMethod==='pb'?(pbMult.toFixed(2)+'*BPS'):(cfMult.toFixed(1)+'x CF');
  var legendLine=valMethod==='pb'?(pbMult.toFixed(2)+' '+pbLabelStr):(cfMult.toFixed(1)+' '+cfLabelStr);
  var stockMarket=meta.market||'';
  var currency=meta.currency||'\u00a5';
  var indexName=meta.index_name||'HSI';
  var indexNameCn=meta.index_name_cn||'\u6052\u751f\u6307\u6570';
  var app=document.getElementById('app');
  var html='';

  html+='<div class="container">';

  // ========================
  // 左栏
  // ========================
  html+='<div class="left-col">';

  // Capital Structure — 完全参考VL截图布局
  var csDate=Y[Y.length-1]+'-12-31', csUnit=cs.unit||'\u4ebf';
  html+='<div class="sec">';
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
  // Row 4: (% of Cap\u2019l) — 右对齐
  html+='<tr><td colspan="5" style="text-align:right;font-size:10px;color:#000;padding-left:0">('+cs.lt_debt_pct+'% of Cap\\u2019l)</td></tr>';
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
  html+='<tr><td style="font-size:8px;color:#000;font-weight:700">(\u4ebf)</td>';
  cpYears.forEach(function(){{html+='<td></td>';}});
  html+='</tr>';
  // 数据行
  var cpDef=[
    ['Cash Assets',0,0],['Receivables',1,0],['Inventory (FIFO)',2,0],['Other',3,0],
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
      var v=(item&&item[yr]!=null)?item[yr].toFixed(1):'\u2014';
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
      var pct=(v[k]!=null)?v[k].toFixed(1)+'%':'\u2014';
      html+='<td style="text-align:right">'+pct+'</td>';
    }});
    html+='</tr>';
  }});
  html+='</table></div>';

  // 季度/半年度表 — VL三表紧排, 单 table + 垂直分割线
  var qsLast=(qt.sales||[]).slice(-3);
  var hasQ=qsLast.some(function(r){{return r&&r.has_quarter;}});
  function renderQSection(title, data, decimal, hasQq, isFirst){{
    if(!data||!data.length) return '';
    var show=data.slice(-5);
    var sepStyle=isFirst?'':'border-top:1px solid #999;';
    sepStyle+='line-height:1;';
    var h='<tr><td style="font-weight:700;'+sepStyle+'padding-top:3px">Year</td>';
    h+='<td colspan="4" style="text-align:center;font-weight:700;border-left:2px solid #000;border-right:2px solid #000;'+sepStyle+'padding-top:3px;white-space:nowrap;font-size:9.5px">'+title+'</td>';
    h+='<td style="border-left:2px solid #000;'+sepStyle+'padding-top:3px"></td></tr>';
    // Header
    h+='<tr style="font-weight:700;line-height:1">';
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
          h+='<td style="'+s+'">'+(v!=null?(decimal===3&&v===0?'\u2014':v.toFixed(decimal)):'\u2014')+'</td>';
        }});
      }}else{{
        h+='<td style="text-align:left;color:#999;border-left:2px solid #000;padding-left:3px;padding-right:3px">\u2014</td>';
        h+='<td style="text-align:right;padding-right:3px">'+(r.q1!=null?(decimal===3&&r.q1===0?'\u2014':r.q1.toFixed(decimal)):'\u2014')+'</td>';
        h+='<td style="text-align:right;color:#999;padding-right:3px">\u2014</td>';
        h+='<td style="text-align:right;padding-right:3px">'+(r.q3!=null?(decimal===3&&r.q3===0?'\u2014':r.q3.toFixed(decimal)):'\u2014')+'</td>';
        h+='<td style="text-align:right;font-weight:700;border-left:2px solid #000;padding-left:3px;padding-right:3px">'+(r.full!=null?r.full.toFixed(decimal):'\u2014')+'</td>';
      }}
      h+='</tr>';
    }});
    return h;
  }}
  html+='<div class="sec" style="border-bottom:1px solid #000;padding-bottom:2px;margin-bottom:2px">';
  html+='<table style="width:100%;border-collapse:collapse;font-size:10px;line-height:1.3">';
  html+=renderQSection('QUARTERLY REVENUES (\u4ebf)', qt.sales, 1, hasQ, true);
  html+=renderQSection('EARNINGS PER SHARE', qt.eps, 2, hasQ, false);
  html+=renderQSection('QUARTERLY DIVIDENDS PAID', qt.dividends, 3, hasQ, false);
  html+='</table>';
  if(!hasQ) html+='<div style="border-top:1px solid #000;font-size:8px;color:#666;margin-top:3px;padding-top:3px">*\u6e2f\u80a1\u4ec5\u62ab\u9732\u534a\u5e74\u62a5\uff0cQ2/Q4\u6682\u65e0\u6570\u636e\u3002</div>';
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

  var priceCcy=meta.price_ccy||meta.currency||(stockMarket==='hk'?'HKD':'CNY');
  html+='<td style="vertical-align:bottom;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">RECENT</td>';
  html+='<td rowspan="2" style="vertical-align:middle;text-align:center;padding:0 10px;border-right:1px solid #999;font-size:18px;font-weight:700">'+(spot.price!=null?spot.price.toFixed(2):'\u2014')+' '+priceCcy+'</td>';
  html+='<td style="vertical-align:bottom;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">P/E</td>';
  html+='<td rowspan="2" style="vertical-align:middle;text-align:center;padding:0 10px;font-size:17px;font-weight:700">'+(trailingPE!=null?trailingPE.toFixed(1):'\u2014')+'</td>';
  // \u2465 (Trailing: xx 第一行
  html+='<td style="vertical-align:bottom;padding:2px 8px;line-height:1;border-right:1px solid #999;font-size:9px;font-weight:700">';
  if(trailingPE){{html+='(Trailing:'+trailingPE.toFixed(1)+')';}}
  html+='</td>';
  html+='<td style="vertical-align:bottom;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">RELATIVE</td>';
  html+='<td rowspan="2" style="vertical-align:middle;text-align:center;padding:0 10px;border-right:1px solid #999;font-size:17px;font-weight:700">'+(relPE!=null?relPE.toFixed(2):'\u2014')+'</td>';
  html+='<td style="vertical-align:bottom;padding:2px 8px;font-size:9px;color:#000;font-weight:700;line-height:1">DIV\u2019D</td>';
  html+='<td rowspan="2" style="vertical-align:middle;text-align:center;padding:0 10px;font-size:17px;font-weight:700">'+(divYld!=null?divYld.toFixed(1)+'%':'\u2014')+'</td>';

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
  var kl=d.kline, hsi=d.index_kline||[];

  // ========== 统一表格: Yearly High/Low + K线 + 23-line ==========
  var showYears=allY;  // 最多10年
  var yrCount=showYears.length;
  html+='<table style="table-layout:fixed;width:100%;border-collapse:collapse;font-size:8.5px">';
  html+='<colgroup><col style="width:140px">';
  showYears.forEach(function(){{ html+='<col>'; }});
  html+='</colgroup>';
  var tdStyle='border-right:1px solid #ddd;padding:2px 8px', thStyle='border-right:1px solid #ddd;text-align:right;padding:2px 8px';
  
  // Row 1: High
  html+='<tr><td style="padding:0 3px;'+tdStyle+'">High</td>';
  showYears.forEach(function(yr){{
    var hl=yhlMap[yr];
    html+='<td style="text-align:right;padding:0 3px;'+tdStyle+'">'+(hl?hl.high:'\u2014')+'</td>';
  }});
  html+='</tr>';
  // Row 3: Low
  html+='<tr><td style="padding:0 3px;'+tdStyle+'">Low</td>';
  showYears.forEach(function(yr){{
    var hl=yhlMap[yr];
    html+='<td style="text-align:right;padding:0 3px;'+tdStyle+'">'+(hl?hl.low:'\u2014')+'</td>';
  }});
  html+='</tr>';
  
  // Row 4: K线图行 — LEGENDS + % TOT. RETURN(左) + 图表(右)
  // chart 220px + volume 42px = 262px flex容器, Percent用margin-top:auto沉底
  html+='<tr><td style="width:200px;padding:0 4px;vertical-align:top;border-right:1px solid #ddd">';
  html+='<div style="display:flex;flex-direction:column;height:260px;font-size:9px;line-height:1.4">';
  html+='<div>';
  html+='<div style="font-weight:700;font-size:10px;margin:2px 0 1px 0">LEGENDS</div>';
  html+='<div style="border-bottom:1px solid #000;margin:2px 0"></div>';
  html+='<div style="font-size:10px;color:#1976D2;line-height:1.1">\u2501\u2501\u2501</div>';
  html+='<div>'+legendLine+'</div>';
  html+='<div style="margin:4px 0"></div>';
  html+='<div style="font-size:10px;color:#ef232a;line-height:1.1">\u00B7\u00B7\u00B7\u00B7\u00B7\u00B7</div>';
  html+='<div>Relative Price Strength</div>';
  html+='<div style="margin:3px 0"></div>';
  html+='<div>Splits: '+(meta.splits||'None')+'</div><div>Options: '+(meta.options||'No')+'</div>';
  html+='<div style="margin:15px 0 2px 0"></div>';
  html+='<div style="font-weight:700;font-size:10px;margin-bottom:2px">% HIST. RETURN</div>';
  html+='<div style="border-bottom:1px solid #000;margin:0 0 2px 0"></div>';
  var trR2=d.total_returns||{{}};
  var trStock2=trR2.stock||{{}};
  var trIndex2=trR2.index||{{}};
  html+='<table style="width:100%;border-collapse:collapse;font-size:10px;line-height:1.35;margin:1px 0">';
  html+='<tr><td></td><td style="text-align:right;font-weight:700">THIS</td><td style="text-align:right;font-weight:700">'+indexName+'</td></tr>';
  html+='<tr><td></td><td style="text-align:right;font-weight:700">STOCK</td><td style="text-align:right"></td></tr>';
  html+='<tr><td>1 yr.</td><td style="text-align:right">'+(trStock2['1yr']!=null?trStock2['1yr'].toFixed(1)+'%':'\u2014')+'</td><td style="text-align:right">'+(trIndex2['1yr']!=null?trIndex2['1yr'].toFixed(1)+'%':'\u2014')+'</td></tr>';
  html+='<tr><td>3 yr.</td><td style="text-align:right">'+(trStock2['3yr']!=null?trStock2['3yr'].toFixed(1)+'%':'\u2014')+'</td><td style="text-align:right">'+(trIndex2['3yr']!=null?trIndex2['3yr'].toFixed(1)+'%':'\u2014')+'</td></tr>';
  html+='<tr><td>5 yr.</td><td style="text-align:right">'+(trStock2['5yr']!=null?trStock2['5yr'].toFixed(1)+'%':'\u2014')+'</td><td style="text-align:right">'+(trIndex2['5yr']!=null?trIndex2['5yr'].toFixed(1)+'%':'\u2014')+'</td></tr>';
  html+='</table>';
  html+='</div>';
  html+='</div></td>';
  html+='<td colspan="'+yrCount+'" style="padding:0">';
  html+='<div class="chart-box" id="chart_kline"></div>';
  html+='<div id="chart_volume" style="height:42px;margin-top:6px;position:relative"></div>';
  
  // Row 5: 年份行
  html+='<tr style="border-top:1px solid #000;border-bottom:1px solid #000"><td style="width:40px;font-size:10px;color:#000;padding:2px 4px;border-right:1px solid #ddd">Year</td>';
  showYears.forEach(function(y){{html+='<td style="text-align:center;font-size:10px;font-weight:700;padding:2px 3px;'+tdStyle+'">'+y+'</td>';}});
  html+='</tr>';
  
  // Row 6+: 24-line metrics
  M.forEach(function(m, idx){{
    var sepBefore=[5];
    var sepAfter=[6,7,10,13,15,17,20,22];
    if(sepBefore.indexOf(m.order)>=0){{
      html+='<tr class="sep" style="height:4px"><td colspan="'+(yrCount+1)+'" style="border-bottom:1px solid #000"></td></tr>';
    }}
    var rowBg=(idx%2===0)?'background:#fafafa;':'';
    html+='<tr style="line-height:1.35;'+rowBg+'">';
    html+='<td style="text-align:left;white-space:nowrap;font-size:9.5px;font-weight:700;'+tdStyle+'">'+m.name_en+' <span style="font-size:8px;color:#444;font-weight:400">'+m.name_cn+'</span></td>';
    showYears.forEach(function(y){{
      var v=(MT[y]||{{}})[m.field];
      var txt='\u2014';
      if(v!=null){{
        if(m.unit==='亿')txt=v.toFixed(1);
        else if(m.unit==='%')txt=v.toFixed(1)+'%';
        else if(m.unit==='元')txt=v.toFixed(2);
        else if(m.unit==='百万股')txt=v.toFixed(0);
        else txt=v.toString();
      }}
      html+='<td style="text-align:right;font-size:9px;'+tdStyle+'">'+txt+'</td>';
    }});
    html+='</tr>';
    if(sepAfter.indexOf(m.order)>=0){{
      html+='<tr class="sep" style="height:4px"><td colspan="'+(yrCount+1)+'" style="border-bottom:1px solid #000"></td></tr>';
    }}
  }});
  html+='</table>';
  
  html+='</div>'; // end center-col
  html+='</div>'; // end container

  // ========================
  // 底部全宽: Business + AI Commentary
  // ========================

  // Business — VL风格，分段可读 (全宽)
  var rev=d.revenue_structure||{{}}, ch=(rev.by_channel||[]), ip=(rev.by_ip||[]), rg=(rev.by_region||[]),
      prod=(rev.by_product||[]), ind=(rev.by_industry||[]);
  var desc=(d.analyst&&d.analyst.business)||cs.business_desc||'';
  var bizP=[], bizHtml='';
  if(desc){{bizP.push(desc);}}
  var p2=[];
  if(ip.length>0){{var ipTop=ip.slice(0,3).map(function(c){{return c.name+' '+c.pct+'%';}}).join('\u3001');p2.push('\u6838\u5fc3IP\uff1a'+ipTop);}}
  if(ch.length>0){{var chTop=ch.slice(0,3).map(function(c){{return c.name+' '+c.pct+'%';}}).join('\u3001');p2.push('\u6e20\u9053\uff1a'+chTop);}}
  if(rg.length>0){{var rgTop=rg.slice(0,3).map(function(c){{return c.name+' '+c.pct+'%';}}).join('\u3001');p2.push('\u5730\u57df\uff1a'+rgTop);}}
  if(prod.length>0){{var prodTop=prod.slice(0,3).map(function(c){{return c.name+' '+c.pct+'%';}}).join('\u3001');p2.push('\u4ea7\u54c1\uff1a'+prodTop);}}
  if(ind.length>0){{var indTop=ind.slice(0,5).map(function(c){{return c.name+' '+c.pct+'%';}}).join('\u3001');p2.push('\u884c\u4e1a\uff1a'+indTop);}}
  if(p2.length) bizP.push(p2.join('\uff1b'));
  var p3=[];var depr=ly.DEPRECIATION, revs=ly.OPERATE_INCOME;
  if(depr&&revs) p3.push('\u6298\u65e7\u7387'+(depr/revs*100).toFixed(1)+'%');
  if(cs.employee_count) p3.push('\u5458\u5de5'+(cs.employee_count/10000).toFixed(1)+'\u4e07\u4eba\uff08'+latestYr+'\uff09');
  if(p3.length) bizP.push(p3.join('\u3002'));
  var p4=[];
  if(meta.ceo) p4.push('\u9996\u5e2d\u6267\u884c\u5b98\uff1a'+meta.ceo);
  if(meta.inc) p4.push('\u6ce8\u518c\u5730\uff1a'+meta.inc);
  if(meta.website) p4.push(meta.website);
  if(p4.length) bizP.push(p4.join('\u3002'));
  bizHtml='<span style="font-weight:700">BUSINESS:</span>';
  bizHtml+='<div style="column-count:2;column-gap:24px;margin-top:4px">';
  var left=[bizP[0]];
  if(bizP[1]) left.push('\u00b7 '+bizP[1]);
  var right=[];
  if(bizP[2]) right.push('\u00b7 '+bizP[2]);
  if(bizP[3]) right.push('\u00b7 '+bizP[3]);
  bizHtml+='<div>'+left.join('<br>')+'</div>';
  bizHtml+='<div>'+right.join('<br>')+'</div>';
  bizHtml+='</div>';
  html+='<div style="border-top:1px solid #000;padding:6px 12px;font-size:11px;line-height:1.55">'+bizHtml+'</div>';

  // AI Commentary: per-stock脚本 > PDF提取(mda) > 数据自生成 (4段VL风格, 全宽)
  var commentary=d.analyst&&d.analyst.commentary&&d.analyst.commentary.length?d.analyst.commentary:[
    '\u6682\u65e0\u6570\u636e', '\u6570\u636e\u6682\u4e0d\u53ef\u7528', '\u8bf7\u5148\u8fd0\u884c engine.py \u751f\u6210\u5b8c\u6574\u6570\u636e', ''
  ];
  var fromMda=d.analyst&&d.analyst.commentary_from_mda;
  var fromScript=d.analyst&&d.analyst.commentary_from_script;
  html+='<div style="border-top:1px solid #000;padding:6px 12px 10px 12px;font-size:10px;line-height:1.35">';
  if(fromScript){{
    html+='<span style="font-size:15px;font-weight:700">AI Commentary: '+stockName+' '+latestYr+' (Custom)</span>';
  }}else if(fromMda){{
    html+='<span style="font-size:15px;font-weight:700">AI Commentary: '+(stockName+' MD&A Analysis')+'</span>';
  }}else{{
    html+='<span style="font-size:15px;font-weight:700">AI Commentary: '+stockName+' '+latestYr+'</span>';
  }}
  html+='<div style="column-count:2;column-gap:24px;margin-top:6px">';
  for(var ci=0;ci<commentary.length;ci++){{
    if(commentary[ci]&&commentary[ci].length>5){{
      html+='<p style="text-align:justify;margin:0 0 8px 0;font-size:12px;break-inside:avoid">'+commentary[ci]+'</p>';
    }}
  }}
  html+='</div>';
  html+='</div>';

  // Item 15 Footnotes — EPS \u8c03\u6574\u660e\u7ec6 (\u6bcf\u9879\u8c03\u6574\u72ec\u7acb\u4e00\u884c, \u65e0\u6570\u636e\u7559\u7a7a)
  var footnotes = d.footnotes || [];
  if (footnotes.length > 0) {{
    var fnMap = {{}};
    footnotes.forEach(function(f) {{
      if (f.adj) fnMap[f.year] = {{adj: f.adj || '', src: f.src || '', diff: f.diff || ''}};
    }});
    var fnYears = Object.keys(fnMap).sort();
    if (fnYears.length === 0) return;

    var abbrName = {{'GS':'政府补贴','FV':'公允价值变动','FX':'汇兑收益','II':'投资收益','IM':'资产减值','EL':'权益法亏损','OG':'其他收益','CD':'A股扣非'}};
    var allAbbrs = [];
    fnYears.forEach(function(y) {{
      var src = fnMap[y].src || '';
      var parts = src.match(/([A-Z]+)\\s+([+-][\\d.]+)/g);
      if (parts) {{
        parts.forEach(function(p) {{
          var m = p.match(/([A-Z]+)\\s+([+-][\\d.]+)/);
          if (m && allAbbrs.indexOf(m[1]) < 0) allAbbrs.push(m[1]);
        }});
      }}
    }});
    function fmtVal(v) {{
      if (!v) return '\u2014';
      var n = parseFloat(v);
      return n < 0 ? '(' + Math.abs(n).toFixed(2) + ')' : n.toFixed(2);
    }}

    html += '<div style="border-top:1px solid #000;padding:4px 12px 2px">';
    html += '<table style="width:100%;border-collapse:collapse;font-size:10px;line-height:1.4">';
    var tdLbl = 'padding:2px 4px;border-right:1px solid #ddd';
    var tdCol = 'text-align:center;padding:2px 4px;border-right:1px solid #ddd';
    html += '<tr style="font-weight:700;border-bottom:1px solid #000"><td style="width:68px;padding:2px 4px;white-space:nowrap;' + tdLbl + '">Footnotes</td>';
    fnYears.forEach(function(y) {{ html += '<td style="' + tdCol + '">' + y + '</td>'; }});
    html += '</tr>';

    // 每项调整独立一行
    allAbbrs.forEach(function(a) {{
      var name = abbrName[a] || a;
      html += '<tr><td style="' + tdLbl + ';font-weight:700;color:#000">' + name + '</td>';
      fnYears.forEach(function(y) {{
        var src = fnMap[y].src || '';
        var m = src.match(new RegExp(a + '\\\\s+([+-][\\\\d.]+)'));
        html += '<td style="' + tdCol + '">' + fmtVal(m ? m[1] : '') + '</td>';
      }});
      html += '</tr>';
    }});

    // 合计行放最后
    html += '<tr style=\"border-top:1px solid #000\"><td style="' + tdLbl + ';font-weight:700">adj.NP</td>';
    fnYears.forEach(function(y) {{ html += '<td style="' + tdCol + ';font-weight:700">' + (fnMap[y].diff || '\u2014') + '</td>'; }});
    html += '</tr>';

    html += '</table></div>';
  }}

  // Item 15 Footnotes — \u6570\u636e\u6e90\u8bf4\u660e (\u6df7\u5408 AKShare + TDX \u65f6\u663e\u793a)
  var dsNote = d.data_source_note || '';
  if (dsNote) {{
    html += '<div style="border-top:1px solid #999;padding:3px 12px 2px;font-size:8px;color:#666;line-height:1.35">';
    html += '<span style="font-weight:700">\u6570\u636e\u6e90:</span> ' + dsNote;
    html += '</div>';
  }}

  html+='<div style="font-size:8px;color:#666;text-align:right;margin-top:4px">\u80a1\u4ef7: '+priceCcy+' | \u8d22\u62a5\u6570\u636e: '+(meta.rpt_ccy||'CNY')+' | {datetime.date.today().isoformat()}</div>';
  app.innerHTML=html;

  // ECharts
  setTimeout(function(){{
    // 裁剪K线到指标年份范围 (与 showYears 对齐, 最多15年)
    var minYr=showYears.length>0?parseInt(showYears[0],10):0;
    kl=kl.filter(function(k){{return parseInt(k.date.substring(0,4),10)>=minYr;}});
    // 补齐K线起始前的空月份，对齐指标表列
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

    // RS line — VL 原生: (个股价/基期) ÷ (指数/基期) × 100, >100跑赢
    // 与 dates 等长，缺失月份填 null 避免 tooltip 索引错位
    var rsData=[];
    if(hsi.length>0){{
      var hsiMap={{}};
      hsi.forEach(function(h){{hsiMap[h.date]=h.close;}});
      var baseS=null,baseH=null;
      dates.forEach(function(dt){{
        var sc=kl.find(function(k){{return k.date===dt;}});
        var hc=hsiMap[dt];
        if(sc&&hc){{
          if(baseS===null){{baseS=sc.close;baseH=hc;}}
          rsData.push(baseS?+((sc.close/baseS)/(hc/baseH)*100).toFixed(1):100);
        }}else{{
          rsData.push(null);
        }}
      }});
    }}
    var series=[
      {{name:stockName,type:'candlestick',data:ohlc,
        itemStyle:{{color:'#ef232a',color0:'#14b143',borderColor:'#ef232a',borderColor0:'#14b143'}}}}
    ];

    var valLine=d.valuation_line||d.cf_line||[];
    var valMap={{}};
    valLine.forEach(function(c){{valMap[c.date]=c.value;}});
    var valSeries=dates.map(function(dt){{
      var yr=dt.substring(0,4);
      var v=valMap[yr];
      return v!=null?Math.log(v):null;
    }});
    if(valSeries.some(function(v){{return v!=null;}})){{
      series.push({{name:valLabel,type:'line',data:valSeries,
        lineStyle:{{type:'solid',color:'#1976D2',width:1.2}},symbol:'none'}});
    }}
    if(rsData.length>0){{
      series.push({{name:'RS',type:'line',data:rsData,
        lineStyle:{{color:'#ef232a',width:1.2,type:'dotted'}},symbol:'none',yAxisIndex:1}});
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
    // 统一 tooltip: 日期 → OHLC(从原始kl读) → CF → RS → PST
    var tooltipFmt=function(p){{var di=p[0].dataIndex,h=p[0].axisValue,r='<b>'+h+' HKD</b>',mk=p[0].marker;var dk=kl.find(function(k){{return k.date===h;}});if(dk)r+='<br/>'+mk+' '+stockName+'<br/> open:'+dk.open.toFixed(2)+'<br/> close:'+dk.close.toFixed(2)+'<br/> low:'+dk.low.toFixed(2)+'<br/> high:'+dk.high.toFixed(2);for(var i=1;i<p.length;i++){{var v=p[i].value,n=p[i].seriesName;if(v==null)continue;if(n==='RS')r+='<br/>'+p[i].marker+' '+n+': '+(v!=null?Number(v).toFixed(1):'-');else if(n.indexOf('x CF')>-1||n.indexOf('*BPS')>-1)r+='<br/>'+p[i].marker+' '+n+': '+Math.exp(Number(v)).toFixed(2);}}var pv=volData[di];if(pv!=null){{var up=dk&&dk.close>dk.open;r+='<br/><span style=\"display:inline-block;width:8px;height:8px;border-radius:50%;background:'+(up?'#ef232a':'#14b143')+';margin-right:4px;vertical-align:middle\"></span>PST: '+pv.toFixed(2)+'%';}}return r;}};
    klineChart.setOption({{
      tooltip:{{trigger:'axis',axisPointer:{{label:{{show:false}}}},formatter:tooltipFmt}},
      grid:{{left:0,right:28,top:4,bottom:24}},
      xAxis:{{type:'category',data:dates,boundaryGap:false,
        axisPointer:{{label:{{show:false}}}},
        axisLabel:{{fontSize:8,color:'#333',fontWeight:700,margin:2,
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
      tooltip:{{show:false}},
      grid:{{left:0,right:28,top:0,bottom:0,containLabel:false}},
      xAxis:{{type:'category',data:dates,show:false,boundaryGap:false,
        axisPointer:{{show:true,type:'shadow',shadowStyle:{{color:'rgba(25,118,210,.08)'}},label:{{show:false,formatter:''}},handle:{{show:false}}}}}},
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
      d.style.cssText='position:absolute;left:0;right:0;top:'+(py||0)+'px;font-size:10px;font-weight:700;display:flex;justify-content:space-between;padding-right:4px';
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

  }},300);
}})();
</script>
</body>
</html>'''

out_path = os.path.join(BASE, 'report', DATA['meta']['name_en'].replace(' ','_')+'.html')
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
