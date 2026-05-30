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
.container{{display:grid;grid-template-columns:275px 1fr;min-height:100vh;overflow:auto}}

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
.chart-box{{flex:1;height:150px}}
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

.footer{{text-align:center;color:#bbb;font-size:8px;padding:3px;border-top:1px solid #eee;margin:6px 0 0 0}}
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

  // Insider Decisions (占位)
  html+='<div class="sec"><div class="sec-title">Insider Decisions</div>';
  html+='<table><tr><td></td><td class="r">Buys</td><td class="r">Sells</td></tr>';
  html+='<tr><td>N/A</td><td class="r">—</td><td class="r">—</td></tr></table></div>';

  // Institutional Decisions (占位)
  html+='<div class="sec"><div class="sec-title">Institutional Decisions</div>';
  html+='<table><tr><td></td><td class="r">Buys</td><td class="r">Sells</td></tr>';
  html+='<tr><td>N/A</td><td class="r">—</td><td class="r">—</td></tr></table></div>';

  // Business — 中文业务简介, 数据驱动 (营收结构来自PDF财报 + SQLite元数据)
  var rev=d.revenue_structure||{{}};
  var ch=(rev.by_channel||[]), ip=(rev.by_ip||[]), rg=(rev.by_region||[]);
  var revYr=latestYr;
  // 从SQLite读取的业务描述 + 员工数 (PDF提取一次存库)
  var bizDesc=cs.business_desc||'';
  var empCount=cs.employee_count;
  var bizHtml='<p>';
  if(bizDesc){{
    bizHtml+=bizDesc;
  }}else{{
    bizHtml+=stockName+'（'+meta.name+'）';
    if(meta.industry) bizHtml+=meta.industry+'行业。';
  }}
  // 补充关键指标
  if(ly.OPERATE_INCOME){{
    bizHtml+=revYr+'年营收'+ly.OPERATE_INCOME.toFixed(1)+'亿';
    if(ly.HOLDER_PROFIT) bizHtml+='，归母净利'+ly.HOLDER_PROFIT.toFixed(1)+'亿';
    if(ly.ROE) bizHtml+='，ROE '+ly.ROE.toFixed(1)+'%';
    bizHtml+='。';
  }}
  // 员工人数
  if(empCount){{
    bizHtml+='员工共计'+(empCount/10000).toFixed(1)+'万人'+(cs.employee_year?'（'+cs.employee_year+'年）':'')+'。';
  }}
  // 渠道结构
  if(ch.length>0){{
    var chStr=ch.slice(0,4).map(function(c){{return c.name+'（'+c.pct+'%）';}}).join('、');
    bizHtml+='业务渠道：'+chStr+'。';
  }}
  // 核心IP
  if(ip.length>0){{
    var ipTop=ip.slice(0,5);
    var ipStr=ipTop.map(function(c){{return c.name+'（'+c.pct+'%）';}}).join('、');
    bizHtml+='核心IP：'+ipStr;
    if(ip.length>5) bizHtml+='等';
    bizHtml+='。';
  }}
  // 地域分布
  if(rg.length>0){{
    var rgStr=rg.map(function(c){{return c.name+'（'+c.pct+'%）';}}).join('、');
    bizHtml+='地域分布：'+rgStr+'。';
  }}
  bizHtml+='</p>';

  // Capital Structure — 2列网格布局 (VL标准名称)
  html+='<div class="sec"><div class="sec-title">CAPITAL STRUCTURE</div>';
  function csHalf(label,val,cls,noteTxt){{
    var h='<div style="width:50%;display:inline-block;vertical-align:top;font-size:8px;line-height:1.6">';
    h+='<div style="display:flex;justify-content:space-between"><span>'+label+'</span><span class="'+(cls||'')+'">'+val+'</span></div>';
    if(noteTxt) h+='<div style="text-align:right;font-size:7px;color:#666;line-height:1.2">('+noteTxt+')</div>';
    h+='</div>';
    return h;
  }}
  html+=csHalf('Total Debt',(cs.total_debt||0).toFixed(1),'r b');
  html+=csHalf('Due in 5 Yrs',(cs.due_in_5yr||0).toFixed(1),'r');
  html+='<br>';
  html+=csHalf('LT Debt',(cs.lt_debt||0).toFixed(1),'r b',cs.lt_debt_pct+'% of Capital');
  html+=csHalf('LT Interest',(cs.total_int||0).toFixed(2),'r',cs.coverage);
  html+='<br>';
  html+=csHalf('Pension Assets',typeof cs.pension_assets==='number'?cs.pension_assets.toFixed(1):(cs.pension_assets||'—'),'r');
  html+=csHalf('Pfd Stock',cs.pfd_stock||'None','r');
  html+='<br>';
  html+='<div style="border-top:1px solid #ddd;font-size:7.5px;margin:3px 0 1px 0;padding-top:2px;clear:both">Common Stock '+cs.common_shares_str+' shs</div>';
  html+=csHalf('MARKET CAP',(cs.mkt_cap||0).toFixed(0),'r b');
  html+=csHalf('',cs.cap_label||'','r');
  html+='<div style="clear:both"></div></div>';

  // Current Position — VL标准名称
  html+='<div class="sec"><div class="sec-title">CURRENT POSITION</div>';
  html+='<table>';
  var cpYears=cp.years||[];
  html+='<tr><td><i>(亿元)</i></td>';
  cpYears.forEach(function(yr){{html+='<td class="r">'+yr+'</td>';}});
  html+='</tr>';
  var cpShort=[
    ['Cash Assets',0],['Receivables',1],['Inventory',2],['Other Current Assets',3],
    ['Current Assets',4,true],
    ['Accounts Payable',5],['Debt Due',6],['Other Current Liab',7],
    ['Current Liabilities',8,true]
  ];
  cpShort.forEach(function(s){{
    if(s[2]){{
      html+='<tr style=\"border-top:1px solid #000\"><td><b>'+s[0]+'</b></td>';
    }}else{{
      html+='<tr><td>'+s[0]+'</td>';
    }}
    var item=(cp.items||[])[s[1]];
    cpYears.forEach(function(yr){{html+='<td class=\"r\">'+(item&&item[yr]!=null?item[yr].toFixed(1):'—')+'</td>';}});
    html+='</tr>';
  }});
  html+='</table></div>';

  // Annual Rates of Change — VL标准 (per sh, 复合增长率)
  html+='<div class="sec"><div class="sec-title">ANNUAL RATES</div>';
  var has10=ar.has_10yr;
  var colKeys=has10?['10yr','5yr','3yr']:['5yr','3yr','1yr'];
  var colLabels=has10?['Past 10 Yrs.','Past 5 Yrs.','Past 3 Yrs.']:['Past 5 Yrs.','Past 3 Yrs.','Past 1 Yr.'];
  html+='<table>';
  html+='<tr><td></td>';
  colLabels.forEach(function(l){{html+='<td class="r">'+l+'</td>';}});
  html+='</tr>';
  var arData=[
    ['Revenues',ar.sales],['"Cash Flow"',ar.cashflow],['Earnings',ar.earnings],
    ['Dividends',ar.dividends],['Book Value',ar.book_value]
  ];
  arData.forEach(function(a){{
    var v=a[1]||{{}};
    html+='<tr><td class="b">'+a[0]+'</td>';
    colKeys.forEach(function(k){{
      html+='<td class="r">'+(v[k]!=null?v[k].toFixed(1)+'%':'—')+'</td>';
    }});
    html+='</tr>';
  }});
  html+='</table></div>';

  // 渲染季度/半年度表
  function renderQ(data, columns, title, decimal, annualOnly){{
    if(!data||!data.length) return '';
    var show=data.slice(-5);  // 仅最近5年
    if(annualOnly){{
      // 仅显示年度总额 (用于股息等只有年度数据的)
      var h='<div class=\"sec\"><div class=\"sec-title\">'+title+'</div><table>';
      h+='<tr><td></td><td class=\"r\">Annual</td></tr>';
      show.forEach(function(r){{
        h+='<tr><td>'+r.year+'</td><td class=\"r b\">'+(r.full!=null?r.full.toFixed(decimal):'—')+'</td></tr>';
      }});
      h+='</table></div>';
      return h;
    }}
    var hasQ=show[0].has_quarter;
    // VL标准永远用 Q1/Q2/Q3/Q4
    var cols=['Q1','Q2','Q3','Q4','Full Yr'];
    var h='<div class=\"sec\"><div class=\"sec-title\">'+title+'</div><table>';
    h+='<tr><td></td>';
    cols.forEach(function(c){{h+='<td class=\"r\">'+c+'</td>';}});
    h+='</tr>';
    show.forEach(function(r){{
      h+='<tr><td>'+r.year+'</td>';
      if(hasQ){{
        var vs=[r.q1,r.q2,r.q3,r.q4,r.full];
        vs.forEach(function(v){{h+='<td class=\"r'+(v===r.full?' b':'')+'\">'+(v!=null?v.toFixed(decimal):'—')+'</td>';}});
      }}else{{
        // 半年度数据: H1→Q1+Q2, H2→Q3+Q4 (分别显示在Q1和Q3位置, Q2/Q4为"—")
        h+='<td class=\"r\">'+(r.q1!=null?r.q1.toFixed(decimal):'—')+'</td>';
        h+='<td class=\"r\">—</td>';
        h+='<td class=\"r\">'+(r.q3!=null?r.q3.toFixed(decimal):'—')+'</td>';
        h+='<td class=\"r\">—</td>';
        h+='<td class=\"r b\">'+(r.full!=null?r.full.toFixed(decimal):'—')+'</td>';
      }}
      h+='</tr>';
    }});
    h+='</table>';
    if(!hasQ) h+='<div class=\"note\" style=\"margin-top:1px\">*该市场仅披露半年报, Q2/Q4暂无数据</div>';
    h+='</div>';
    return h;
  }}
  html+=renderQ(qt.sales, ['H1','H2'], 'QUARTERLY REVENUES (亿元)', 1);
  html+=renderQ(qt.eps, ['H1','H2'], 'EARNINGS PER SHARE', 2);
  html+=renderQ(qt.dividends, ['H1','H2'], 'QUARTERLY DIVIDENDS PAID ('+(meta.currency||'CNY')+')', 3);


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
  var kl=d.kline, hsi=d.index_kline||[], lastIdx=kl.length-1;
  function totalReturn(n){{
    if(kl.length<=n) return '—';
    var start=kl[kl.length-1-n].close, end=kl[lastIdx].close;
    if(!start||!end) return '—';
    return ((end/start-1)*100).toFixed(0)+'%';
  }}

  // ========== 统一表格: Yearly High/Low + K线 + 23-line ==========
  var showYears=allY;  // 最多10年
  var yrCount=showYears.length;
  html+='<table style="table-layout:fixed;width:100%;border-collapse:collapse;font-size:8.5px">';
  var tdStyle='border-right:1px solid #ddd;padding:2px 8px', thStyle='border-right:1px solid #ddd;text-align:right;padding:2px 8px';
  
  // Row 1: High
  html+='<tr><td style="font-weight:700;padding:0 3px;'+tdStyle+'">High</td>';
  showYears.forEach(function(yr){{
    var hl=yhlMap[yr];
    html+='<td style="text-align:right;padding:0 3px;'+tdStyle+'">'+(hl?hl.high:'—')+'</td>';
  }});
  html+='</tr>';
  // Row 3: Low
  html+='<tr><td style="font-weight:700;padding:0 3px;'+tdStyle+'">Low</td>';
  showYears.forEach(function(yr){{
    var hl=yhlMap[yr];
    html+='<td style="text-align:right;padding:0 3px;'+tdStyle+'">'+(hl?hl.low:'—')+'</td>';
  }});
  html+='</tr>';
  
  // Row 4: K线图行 — LEGENDS(第一列) + 图表(colspan)
  html+='<tr><td style="padding:1px 3px;vertical-align:top;'+tdStyle+'">';
  html+='<div style="font-size:7px;line-height:1.3">';
  html+='<div style="font-weight:700">LEGENDS</div>';
  html+='<div style="border-bottom:1px solid #000;margin:1px 0"></div>';
  html+='<div>15.0 x CF per Sh</div>';
  html+='<div style="border-bottom:1px solid #000;margin:1px 0"></div>';
  html+='<div>Rel Price Strength</div>';
  html+='<div style="border-bottom:1px solid #000;margin:1px 0"></div>';
  html+='<div>Splits: '+(meta.splits||'None')+'</div><div>Opt: '+(meta.options||'No')+'</div>';
  html+='<div style="border-bottom:1px solid #000;margin:1px 0"></div>';
  html+='<div style="font-weight:700">% Total Return</div>';
  html+='<div>1yr '+totalReturn(12)+'&nbsp; 3yr '+totalReturn(36)+'&nbsp; 5yr '+totalReturn(60)+'</div>';
  html+='<div style="margin-top:2px">P/E '+spot.pe+'x&nbsp; P/B '+spot.pb+'x&nbsp; Yld '+spot.div_yield+'%</div>';
  if(pos.pe){{
    html+='<div>PE H:'+pos.pe.max+' L:'+pos.pe.min+' Avg:'+pos.pe.avg+'</div>';
  }}
  html+='</div></td>';
  html+='<td colspan="'+yrCount+'" style="padding:0">';
  html+='<div class="chart-box" id="chart_kline"></div>';
  html+='<div id="chart_volume" style="height:30px;margin-top:0"></div>';
  html+='</td></tr>';
  
  // Row 5: 年份基准线 — 在K线图和指标之间
  html+='<tr style="border-top:1px solid #ccc;border-bottom:1px solid #ccc"><td style="width:110px;font-size:7px;color:#666;padding:1px 3px;'+tdStyle+'">Year</td>';
  showYears.forEach(function(y){{html+='<td style="text-align:center;font-size:7px;font-weight:700;padding:1px 3px;'+tdStyle+'">'+y+'</td>';}});
  html+='</tr>';
  
  // Row 6+: 24-line metrics — 分区分隔 (每股指标6|股本估值7-10|利润表11-17|资产负债18-20|回报率21-24)
  M.forEach(function(m, idx){{
    var sepAfter=[6,10,17,20];
    html+='<tr>';
    html+='<td style="text-align:left;white-space:nowrap;'+tdStyle+'">'+m.name_en+' <span style="font-size:7px;color:#999">'+m.name_cn+'</span></td>';
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
      html+='<td style="text-align:right;'+tdStyle+'">'+txt+'</td>';
    }});
    html+='</tr>';
    if(sepAfter.indexOf(m.order)>=0){{
      html+='<tr class="sep"><td colspan="'+(yrCount+1)+'" style="border-bottom:2px solid #000"></td></tr>';
    }}
  }});
  html+='</table>';
  
  // Business — MDA (表下方)
  html+='<div class="analyst"><b>BUSINESS</b>'+bizHtml+'</div>';

  // Management Discussion & Analysis (中栏, Business下方)
  var mdaText=cs.mda_text||'';
  if(mdaText){{
    var compact = mdaText.split('\\n\\n').map(function(p){{
      return p.replace(/\\n/g,' ');
    }}).join('<br>');
    html+='<div class="analyst"><b>Management Discussion & Analysis</b><p style="text-align:justify">'+compact+'</p></div>';
  }}

  // Footer — 校验结果汇总
  var vSt=v.status==='OK'?'✅ 全通过':'⚠️ '+(v.checks_passed||0)+'/'+(v.checks_total||0)+' 通过';
  var pdfNote=(v.pdf_years||[]).length>0?' | PDF: FY'+(v.pdf_years||[]).join(',FY'):' | PDF: 无';
  html+='<div class="footer">AKShare + Annual Report | Checks: '+vSt+pdfNote+'</div>';

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
        ohlc=padOHLC.concat(kl.map(function(k){{return [k.open,k.close,k.low,k.high];}}));

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
      return cfMap[yr]||null;
    }});
    if(cfSeries.some(function(v){{return v!=null;}})){{
      series.push({{name:'15x CF',type:'line',data:cfSeries,
        lineStyle:{{type:'dashed',color:'#1976D2',width:1.2}},symbol:'none'}});
    }}
    if(rsStock.length>0){{
      series.push({{name:stockName+' (idx)',type:'line',data:rsStock,
        lineStyle:{{color:'#ef232a',width:1.2}},symbol:'none',yAxisIndex:1}});
      series.push({{name:indexName+' (idx)',type:'line',data:rsHsi,
        lineStyle:{{color:'#999',width:1,type:'dotted'}},symbol:'none',yAxisIndex:1}});
    }}

    // 年分隔线
    var yearLines=[];
    dates.forEach(function(d,i){{if(d.endsWith('-01'))yearLines.push({{xAxis:i,lineStyle:{{color:'#ccc',width:1,type:'solid'}}}});}});
    series[0].markLine={{silent:true,animation:false,symbol:'none',data:yearLines,label:{{show:false}}}};

    echarts.init(document.getElementById('chart_kline')).setOption({{
      tooltip:{{trigger:'axis'}},
      grid:{{left:0,right:18,top:2,bottom:20}},
      xAxis:{{type:'category',data:dates,boundaryGap:false,
        axisLabel:{{fontSize:6.5,color:'#666',fontWeight:700,margin:2,
          formatter:function(v){{return v&&v.endsWith('-01')?v.slice(0,4):'';}},
          interval:0,showMinLabel:true,showMaxLabel:true}},
        axisLine:{{show:true,lineStyle:{{color:'#999',width:0.5}}}},
        axisTick:{{show:false}},
        splitLine:{{show:true,lineStyle:{{color:'#ccc',width:0.5}}}}}},
      yAxis:[
        {{type:'log',scale:true,axisLabel:{{fontSize:6}},position:'right'}},
        {{type:'value',axisLabel:{{fontSize:6}},splitLine:{{show:false}},position:'right'}}],
      series:series
    }});

    // Monthly Volume % — VL item 11
    var volData=[], totalShM=ly.TOTAL_SHARES;
    dates.forEach(function(dt){{
      var k=kl.find(function(k){{return k.date===dt;}});
      if(k&&k.volume&&totalShM){{
        volData.push((k.volume/(totalShM*1e6)*100).toFixed(2));
      }}else{{volData.push(null);}}
    }});
    echarts.init(document.getElementById('chart_volume')).setOption({{
      grid:{{left:0,right:18,top:0,bottom:0}},
      xAxis:{{type:'category',data:dates,show:false,boundaryGap:false}},
      yAxis:{{type:'value',axisLabel:{{fontSize:6}},splitLine:{{show:false}},position:'right',
        axisLabel:{{formatter:function(v){{return v+'%';}}}}}},
      series:[{{name:'Vol%',type:'bar',data:volData,
        itemStyle:{{color:'#1976D2'}},barWidth:'60%'}}]
    }});

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
