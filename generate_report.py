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
.header .code{{font-weight:700;font-size:14px;font-family:"Times New Roman",serif}}
.header .info{{text-align:right;font-size:8.5px;line-height:1.3}}
.header .info .v{{font-weight:700;font-size:10px}}
.header .ratings{{display:flex;gap:10px;font-size:8px;text-align:center}}
.header .ratings span{{font-weight:700;display:block;font-size:10px}}

/* Chart section */
.chart-area{{margin:2px 0;border-bottom:1px solid #000}}
.chart-title{{font-weight:700;font-size:9px;margin-bottom:0px}}
.chart-row{{display:flex;gap:4px}}
.chart-box{{flex:1;height:150px}}
.return-box{{width:150px;font-size:8.5px;padding:3px 5px}}
.return-box table{{width:100%;border-collapse:collapse;margin-bottom:3px}}
.return-box td,.return-box th{{padding:1px 3px;text-align:right;font-size:8px}}
.return-box th{{border-bottom:1px solid #999}}
.return-box .note{{font-size:7.5px;color:#666;line-height:1.2}}

/* 23-line table */
.stat-table{{margin:2px 0;overflow-x:auto}}
.stat-table table{{border-collapse:collapse;font-size:8.5px;width:100%}}
.stat-table th,.stat-table td{{text-align:right;padding:2px 4px;border-right:1px solid #ddd;white-space:nowrap;line-height:1.3}}
.stat-table th{{background:#eee;font-weight:700;font-size:8px}}
.stat-table td:first-child,.stat-table th:first-child{{text-align:left;min-width:100px;white-space:nowrap}}
.stat-table tr:nth-child(even){{background:#fafafa}}
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
  var d=DATA, M=d.metric_defs, Y=d.years, MT=d.data, SA=d.semi_annual,
      cs=d.capital_structure||{{}}, cp=d.current_position||{{}},
      ar=d.annual_rates||{{}}, qt=d.quarterly||{{}},
      yhl=d.yearly_hl||[], pos=d.position||{{}}, v=d.validation||{{}};
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
    if(ly.ROE_AVG) bizHtml+='，ROE '+ly.ROE_AVG.toFixed(1)+'%';
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

  // Capital Structure — 2列网格布局 (参考图样式)
  var cu=cs.unit||'';
  html+='<div class="sec"><div class="sec-title">Capital Structure'+(cu?' ('+cu+')':'')+'</div>';
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
  html+=csHalf('Total Int',(cs.total_int||0).toFixed(2),'r',cs.coverage);
  html+='<br>';
  html+=csHalf('Pension Assets',typeof cs.pension_assets==='number'?cs.pension_assets.toFixed(1):(cs.pension_assets||'—'),'r');
  html+=csHalf('Pfd Stock',cs.pfd_stock||'—','r');
  html+='<br>';
  html+='<div style="border-top:1px solid #ddd;font-size:7.5px;margin:3px 0 1px 0;padding-top:2px;clear:both">Common Stock '+cs.common_shares_str+' shs</div>';
  html+=csHalf('MARKET CAP',(cs.mkt_cap||0).toFixed(0),'r b');
  html+=csHalf('',cs.cap_label||'—','r');
  html+='<div style="clear:both"></div></div>';

  // Current Position
  html+='<div class="sec"><div class="sec-title">Current Position</div>';
  html+='<table>';
  var cpYears=cp.years||[];
  html+='<tr><td><i>(亿)</i></td>';
  cpYears.forEach(function(yr){{html+='<td class="r">'+yr+'</td>';}});
  html+='</tr>';
  var cpShort=[
    ['Cash',0],['Receivables',1],['Inventory',2],['Other Cur.Assets',3],['<b>Current Assets</b>',4],
    ['Accts Payable',5],['Debt Due',6],['Other Cur.Liab',7],['<b>Current Liab.</b>',8]
  ];
  cpShort.forEach(function(s){{
    var item=(cp.items||[])[s[1]];
    if(!item) return;
    html+='<tr><td>'+s[0]+'</td>';
    cpYears.forEach(function(yr){{html+='<td class="r">'+(item[yr]||0).toFixed(1)+'</td>';}});
    html+='</tr>';
  }});
  html+='</table></div>';

  // Annual Rates of Change — 动态列: 有10年数据→10/5/3yr, 否则5/3/1yr
  html+='<div class="sec"><div class="sec-title">Annual Rates of Change</div>';
  var has10=ar.has_10yr;
  var colKeys=has10?['10yr','5yr','3yr']:['5yr','3yr','1yr'];
  var colLabels=has10?['Past 10yr','Past 5yr','Past 3yr']:['Past 5yr','Past 3yr','Past 1yr'];
  html+='<table>';
  html+='<tr><td></td>';
  colLabels.forEach(function(l){{html+='<td class="r">'+l+'</td>';}});
  html+='</tr>';
  var arData=[
    ['Sales',ar.sales],['Cash Flow',ar.cashflow],['Earnings',ar.earnings],
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

  // Quarterly Sales (港股用H1/H2)
  html+='<div class="sec"><div class="sec-title">Quarterly Sales (亿)</div>';
  html+='<table>';
  html+='<tr><td></td><td class="r">H1</td><td class="r">H2</td><td class="r">Full Yr</td></tr>';
  (qt.sales||[]).forEach(function(r){{
    html+='<tr><td>'+r.year+'</td><td class="r">'+r.q1q2+'</td><td class="r">'+r.q3q4+'</td><td class="r b">'+r.full+'</td></tr>';
  }});
  html+='</table>';
  html+='<div class="note" style="margin-top:1px">*部分市场仅披露半年报, 以H1/H2代替四季</div></div>';

  // Quarterly EPS
  html+='<div class="sec"><div class="sec-title">Earnings Per Share</div>';
  html+='<table>';
  html+='<tr><td></td><td class="r">H1</td><td class="r">H2</td><td class="r">Full Yr</td></tr>';
  (qt.eps||[]).forEach(function(r){{
    html+='<tr><td>'+r.year+'</td><td class="r">'+(r.q1q2!=null?r.q1q2.toFixed(2):'—')+'</td><td class="r">'+(r.q3q4!=null?r.q3q4.toFixed(2):'—')+'</td><td class="r b">'+(r.full!=null?r.full.toFixed(2):'—')+'</td></tr>';
  }});
  html+='</table></div>';

  // Quarterly Dividends
  html+='<div class="sec"><div class="sec-title">Quarterly Divs Paid</div>';
  html+='<table>';
  html+='<tr><td></td><td class="r">H1</td><td class="r">H2</td><td class="r">Full Yr</td></tr>';
  (qt.dividends||[]).forEach(function(r){{
    html+='<tr><td>'+r.year+'</td><td class="r">'+(r.q1q2>0?r.q1q2.toFixed(3):'—')+'</td><td class="r">'+(r.q3q4>0?r.q3q4.toFixed(3):'—')+'</td><td class="r b">'+(r.full>0?r.full.toFixed(3):'—')+'</td></tr>';
  }});
  html+='</table></div>';

  html+='</div>'; // end left-col

  // ========================
  // 中栏
  // ========================
  html+='<div class="center-col">';

  // Header
  var beta='—'; // Beta (AKShare不覆盖所有市场)
  html+='<div class="header">';
  html+='<div><span class="code">'+stockName+'</span><br>';
  html+='<span style="font-size:8px">'+stockCode+'.'+stockMarket+'</span></div>';
  html+='<div class="ratings">';
  html+='<div>Timeliness<br><span>—</span></div>';
  html+='<div>Industry<br><span>'+(meta.industry||'—')+'</span></div>';
  html+='<div>Price<br><span>'+(meta.price_ccy||'—')+'</span></div>';
  html+='<div>Report<br><span>'+(meta.rpt_ccy||'—')+'</span></div>';
  html+='<div>Curr<br><span>'+((meta.currency||'').toUpperCase()||'CNY')+'</span></div>';
  html+='</div>';
  html+='<div class="info">';
  html+='RECENT PRICE <span class="v">'+(spot.price?spot.price.toFixed(2):'—')+'</span><br>';
  html+='PE RATIO <span class="v">'+(spot.pe||'—')+'</span><br>';
  html+='52-Wk Range <span class="v">'+(pos.price?pos.price.min+' ~ '+pos.price.max:'—')+'</span>';
  html+='</div></div>';

  // Chart

  // Chart
  var kl=d.kline, hsi=d.index_kline||[], lastIdx=kl.length-1;
  function totalReturn(n){{
    if(kl.length<=n) return '—';
    var start=kl[kl.length-1-n].close, end=kl[lastIdx].close;
    if(!start||!end) return '—';
    return ((end/start-1)*100).toFixed(0)+'%';
  }}

  // Yearly High/Low — 标题在表头, 删除下方重复标题
  html+='<div style="margin:0;padding:1px 8px;font-size:8.5px">';
  html+='<table style="border-collapse:collapse;font-size:8px;width:100%"><tr style="border-bottom:1px solid #ccc">';
  html+='<th style="padding:0 3px">Yearly High / Low</th>';
  var showYears=yhl.slice(-8);
  showYears.forEach(function(hl){{
    if(!hl) return;
    html+='<th style="text-align:right;padding:0 3px">'+hl.year+'</th>';
  }});
  html+='</tr><tr>';
  html+='<td style="font-weight:700;text-align:center;padding:0 3px">High</td>';
  showYears.forEach(function(hl){{
    if(!hl) return;
    html+='<td style="text-align:right;padding:0 3px">'+hl.high+'</td>';
  }});
  html+='</tr><tr>';
  html+='<td style="font-weight:700;text-align:center;padding:0 3px">Low</td>';
  showYears.forEach(function(hl){{
    if(!hl) return;
    html+='<td style="text-align:right;padding:0 3px">'+hl.low+'</td>';
  }});
  html+='</tr></table>';
  html+='</div>';

  html+='<div class="chart-title">Monthly Price Ranges (Log Scale) + Cash Flow Line</div>';
  html+='<div class="chart-row">';
  // LEGENDS — 紧凑一行
  html+='<div style="font-size:7px;line-height:1.4;padding:1px 3px;min-width:72px;border-right:1px solid #ccc">';
  html+='<div style="font-weight:700">LEGENDS</div>';
  html+='<div style="border-bottom:1px solid #000;margin:1px 0"></div>';
  html+='<div>15.0 x CF per Sh</div>';
  html+='<div style="border-bottom:1px solid #000;margin:1px 0"></div>';
  html+='<div>Rel Price Strength</div>';
  html+='<div style="border-bottom:1px solid #000;margin:1px 0"></div>';
  html+='<div>Splits: '+(meta.splits||'None')+'</div><div>Opt: '+(meta.options||'No')+'</div>';
  html+='</div>';
  html+='<div class="chart-box" id="chart_kline"></div>';
  html+='<div class="return-box">';
  html+='<div style="font-weight:700;font-size:9px;margin-bottom:2px">% Total Return</div>';
  html+='<table><tr><th></th><th>1yr</th><th>3yr</th><th>5yr</th></tr>';
  html+='<tr><td>'+(meta.name||'Stock')+'</td><td>'+totalReturn(12)+'</td><td>'+totalReturn(36)+'</td><td>'+totalReturn(60)+'</td></tr>';
  html+='<tr><td>'+indexName+'</td><td>—</td><td>—</td><td>—</td></tr></table>';
  html+='<div class="note">Log Scale / Monthly High-Low<br>';
  html+='--- Cash Flow per Sh x15<br>';
  html+='--- Relative Strength (vs '+indexName+')<br><br>';
  html+='<div style="display:flex;gap:8px">';
  html+='<div>';
  html+='P/E (TTM): '+spot.pe+'x<br>';
  html+='P/B: '+spot.pb+'x<br>';
  html+='Div Yield: '+spot.div_yield+'%<br>';
  html+='</div>';
  // PE Range 并排右边
  html+='<div>';
  if(pos.pe){{
    html+='PE H: '+pos.pe.max+'x<br>';
    html+='PE L: '+pos.pe.min+'x<br>';
    html+='Avg: '+pos.pe.avg+'x<br>';
  }}
  html+='</div></div>';
  html+='</div>';
  html+='</div></div>';

  // 23-line Statistical Array
  html+='<div class="stat-table"><table>';
  html+='<tr><th></th>';
  Y.forEach(function(y){{html+='<th>'+y+'</th>';}});
  html+='</tr>';
  M.forEach(function(m, idx){{
    // Value Line separators: after rows 2(Cash Flow), 4(Dividends), 6(Book Value), 7(Shares), 10(Div Yield)
    var sepAfter=[2,4,6,7,10];
    var isHigh=(m.field==='DPS'||m.field==='PAYOUT_RATIO');
    html+='<tr'+(isHigh?' style="background:#fffde7"':'')+'>';
    html+='<td style="white-space:nowrap">'+m.name_en+' <span style="font-size:7px;color:#999">'+m.name_cn+'</span></td>';
    Y.forEach(function(y){{
      var v=(MT[y]||{{}})[m.field];
      var txt='—';
      if(v!=null){{
        if(m.unit==='亿')txt=v.toFixed(1);
        else if(m.unit==='%')txt=v.toFixed(1)+'%';
        else if(m.unit==='元')txt=v.toFixed(2);
        else if(m.unit==='百万股')txt=v.toFixed(0);
        else txt=v.toFixed(1);
      }}
      html+='<td>'+txt+'</td>';
    }});
    html+='</tr>';
    if(sepAfter.indexOf(m.order)>=0){{
      var cols=Y.length+1;
      html+='<tr class="sep"><td colspan="'+cols+'"></td></tr>';
    }}
  }});
  html+='</table></div>';

  // Business — 中栏, MDA上方
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
    var dates=kl.map(function(k){{return k.date;}}),
        ohlc=kl.map(function(k){{return [k.open,k.close,k.low,k.high];}});

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

    echarts.init(document.getElementById('chart_kline')).setOption({{
      tooltip:{{trigger:'axis'}},
      grid:{{left:45,right:50,top:2,bottom:18}},
      xAxis:{{type:'category',data:dates,axisLabel:{{fontSize:6}}}},
      yAxis:[
        {{type:'log',scale:true,axisLabel:{{fontSize:7}}}},
        {{type:'value',axisLabel:{{fontSize:7}},splitLine:{{show:false}}}}
      ],
      series:series
    }});

  }},300);
}})();
</script>
</body>
</html>'''

out_path = os.path.join(BASE, "report.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"Generated: {out_path} ({len(HTML)} chars)")
print(f"  Layout: Left(275px) + Center(flex) — Value Line classic 2-column")
