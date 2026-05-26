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
<title>Value Line — POP MART 09992.HK</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:Arial,Helvetica,sans-serif;font-size:10px;line-height:1.25;color:#000;width:1280px;margin:0 auto;background:#fff}}
.container{{display:flex;min-height:100vh}}

/* ===== 左栏 260px ===== */
.left-col{{width:270px;border-right:1px solid #000;padding:4px 5px 0 5px;font-size:9px}}
.left-col .sec{{margin-bottom:4px}}
.left-col .sec-title{{font-weight:700;font-size:9.5px;border-bottom:1px solid #000;padding-bottom:1px;margin-bottom:2px;text-transform:uppercase}}
.left-col table{{width:100%;border-collapse:collapse;font-size:8.5px}}
.left-col td{{padding:0 2px}}
.left-col .r{{text-align:right}}
.left-col .b{{font-weight:700}}
.left-col p{{margin:2px 0;font-size:8.5px}}

/* ===== 中栏 720px ===== */
.center-col{{flex:1;padding:4px 0 0 0;display:flex;flex-direction:column}}

/* Header */
.header{{display:flex;align-items:center;justify-content:space-between;padding:3px 8px;border-bottom:2px solid #000;margin:0 4px}}
.header .code{{font-weight:700;font-size:14px;font-family:"Times New Roman",serif}}
.header .info{{text-align:right;font-size:8.5px;line-height:1.3}}
.header .info .v{{font-weight:700;font-size:10px}}
.header .ratings{{display:flex;gap:10px;font-size:8px;text-align:center}}
.header .ratings span{{font-weight:700;display:block;font-size:10px}}

/* Chart section */
.chart-area{{margin:3px 4px;border-bottom:1px solid #000}}
.chart-title{{font-weight:700;font-size:9.5px;margin-bottom:2px}}
.chart-row{{display:flex;gap:4px}}
.chart-box{{flex:1;height:280px}}
.return-box{{width:150px;font-size:8.5px;padding:3px 5px}}
.return-box table{{width:100%;border-collapse:collapse;margin-bottom:3px}}
.return-box td,.return-box th{{padding:1px 3px;text-align:right;font-size:8px}}
.return-box th{{border-bottom:1px solid #999}}
.return-box .note{{font-size:7.5px;color:#666;line-height:1.2}}

/* 23-line table */
.stat-table{{margin:3px 4px;overflow-x:auto}}
.stat-table table{{border-collapse:collapse;font-size:8.5px;width:100%}}
.stat-table th,.stat-table td{{text-align:right;padding:1px 3px;border-right:1px solid #ddd;white-space:nowrap}}
.stat-table th{{background:#eee;font-weight:700;font-size:8px}}
.stat-table td:first-child,.stat-table th:first-child{{text-align:left;min-width:125px}}
.stat-table tr:nth-child(even){{background:#fafafa}}

/* Analyst */
.analyst{{margin:4px;padding:4px 6px;font-size:9px;line-height:1.35;border-top:1px solid #000}}
.analyst b{{display:block;margin-bottom:2px}}
.analyst p{{margin-bottom:3px}}

/* ===== 右栏 260px ===== */
.right-col{{width:255px;border-left:1px solid #000;padding:4px 5px 0 5px;font-size:8.5px}}
.right-col .sec{{margin-bottom:4px}}
.right-col .sec-title{{font-weight:700;font-size:9.5px;border-bottom:1px solid #000;padding-bottom:1px;margin-bottom:2px;text-transform:uppercase}}
.right-col table{{width:100%;border-collapse:collapse;font-size:8px}}
.right-col td{{padding:0.5px 2px}}
.right-col .r{{text-align:right}}
.right-col .b{{font-weight:700}}
.right-col .note{{font-size:7.5px;color:#666}}

.footer{{text-align:center;color:#bbb;font-size:8px;padding:3px;border-top:1px solid #eee;margin:8px 4px 0 4px}}
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
      pos=d.position||{{}}, v=d.validation||{{}};
  var latestYr=Y[Y.length-1], ly=MT[latestYr]||{{}};
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

  // Business
  html+='<div class="sec"><div class="sec-title">Business</div>';
  html+='<p>POP MART is a leading character-based entertainment company in China. Core business includes IP incubation, pop toy design/manufacturing/retail, theme parks, and IP licensing. Owns 17 artist IPs exceeding RMB100M in annual revenue. As of 2025, 530 stores (445 PRC + 85 overseas), 2,396 roboshops. THE MONSTERS (LABUBU) surpassed RMB14B in revenue.</p></div>';

  // Capital Structure
  html+='<div class="sec"><div class="sec-title">Capital Structure</div>';
  html+='<table>';
  html+='<tr><td>Total Debt</td><td class="r b">¥'+(cs.total_debt||0).toFixed(1)+'B</td></tr>';
  html+='<tr><td>LT Debt</td><td class="r b">¥'+(cs.lt_debt||0).toFixed(1)+'B</td>';
  html+='<td style="font-size:7.5px;color:#666">('+cs.lt_debt_pct+'% of Cap)</td></tr>';
  html+='<tr><td>Total Assets</td><td class="r">¥'+(cs.total_assets||0).toFixed(1)+'B</td></tr>';
  html+='<tr><td>Equity</td><td class="r">¥'+(cs.total_equity||0).toFixed(1)+'B</td></tr>';
  html+='<tr><td>Com.Shares</td><td class="r">1,341M</td></tr>';
  html+='<tr><td>Mkt Cap</td><td class="r b">¥'+(cs.mkt_cap||0).toFixed(0)+'B ('+(cs.cap_label||'—')+')</td></tr>';
  html+='</table></div>';

  // Current Position
  html+='<div class="sec"><div class="sec-title">Current Position</div>';
  html+='<table>';
  var cpYears=cp.years||[];
  html+='<tr><td><i>(¥B)</i></td>';
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

  // Annual Rates
  html+='<div class="sec"><div class="sec-title">Annual Rates</div>';
  html+='<table>';
  html+='<tr><td></td><td class="r">Past<br>5yr</td><td class="r">Past<br>10yr</td><td class="r">Est 3-5yr</td></tr>';
  var arData=[
    ['Sales',ar.sales],['Cash Flow',ar.cashflow],['Earnings',ar.earnings],['Dividends',ar.dividends]
  ];
  arData.forEach(function(a){{
    var v=a[1]||{{}};
    html+='<tr><td class="b">'+a[0]+'</td>';
    html+='<td class="r">'+(v['5yr']!=null?v['5yr'].toFixed(1)+'%':'—')+'</td>';
    html+='<td class="r">'+(v['10yr']!=null?v['10yr'].toFixed(1)+'%':'—')+'</td>';
    html+='<td class="r">'+v['future']+'</td>';
    html+='</tr>';
  }});
  html+='</table></div>';

  // Quarterly Sales
  html+='<div class="sec"><div class="sec-title">Quarterly Sales (¥B)</div>';
  html+='<table>';
  html+='<tr><td></td><td class="r">H1</td><td class="r">H2</td><td class="r">Full</td></tr>';
  (qt.sales||[]).forEach(function(r){{
    html+='<tr><td>'+r.year+'</td><td class="r">'+r.q1q2+'</td><td class="r">'+r.q3q4+'</td><td class="r b">'+r.full+'</td></tr>';
  }});
  html+='</table>';
  html+='<div class="note" style="margin-top:1px">*港股仅披露半年报, 以H1/H2代替Q1-Q4</div></div>';

  // Quarterly EPS
  html+='<div class="sec"><div class="sec-title">Quarterly Earns Per Sh</div>';
  html+='<table>';
  html+='<tr><td></td><td class="r">H1</td><td class="r">H2</td><td class="r">Full</td></tr>';
  (qt.eps||[]).forEach(function(r){{
    html+='<tr><td>'+r.year+'</td><td class="r">'+(r.q1q2!=null?r.q1q2.toFixed(2):'—')+'</td><td class="r">'+(r.q3q4!=null?r.q3q4.toFixed(2):'—')+'</td><td class="r b">'+(r.full!=null?r.full.toFixed(2):'—')+'</td></tr>';
  }});
  html+='</table></div>';

  // Quarterly Dividends
  html+='<div class="sec"><div class="sec-title">Quarterly Divs Paid</div>';
  html+='<table>';
  html+='<tr><td></td><td class="r">H1</td><td class="r">H2</td><td class="r">Full</td></tr>';
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
  var spot=d.spot||{{}};
  var beta='—'; // Beta not available for HK stocks via sina
  html+='<div class="header">';
  html+='<div><span class="code">POP MART</span><br>';
  html+='<span style="font-size:8px">09992.HK</span></div>';
  html+='<div class="ratings">';
  html+='<div>Timeliness<br><span>—</span></div>';
  html+='<div>Safety<br><span>—</span></div>';
  html+='<div>Technical<br><span>—</span></div>';
  html+='<div>Beta<br><span>'+beta+'</span></div>';
  html+='<div>Industry<br><span>Consumer</span></div>';
  html+='</div>';
  html+='<div class="info">';
  html+='RECENT PRICE <span class="v">'+(spot.price||'—')+'</span><br>';
  html+='PE RATIO <span class="v">'+(spot.pe||'—')+'</span><br>';
  html+='52-Wk Range <span class="v">'+(pos.price?pos.price.min+' ~ '+pos.price.max:'—')+'</span><br>';
  html+='Target Range<br><span style="font-size:8px">TBD</span>';
  html+='</div>';
  html+='</div>';

  // Chart
  var kl=d.kline, hsi=d.hsi_kline||[], lastIdx=kl.length-1;
  function totalReturn(n){{
    if(kl.length<=n) return '—';
    var start=kl[kl.length-1-n].close, end=kl[lastIdx].close;
    if(!start||!end) return '—';
    return ((end/start-1)*100).toFixed(0)+'%';
  }}
  html+='<div class="chart-title">Monthly Price Ranges (Log Scale) + Cash Flow Line</div>';
  html+='<div class="chart-row">';
  html+='<div class="chart-box" id="chart_kline"></div>';
  html+='<div class="return-box">';
  html+='<div style="font-weight:700;font-size:9px;margin-bottom:2px">% Total Return</div>';
  html+='<table><tr><th></th><th>1yr</th><th>3yr</th><th>5yr</th></tr>';
  html+='<tr><td>POPMART</td><td>'+totalReturn(12)+'</td><td>'+totalReturn(36)+'</td><td>'+totalReturn(60)+'</td></tr>';
  html+='<tr><td>HSI</td><td>—</td><td>—</td><td>—</td></tr></table>';
  html+='<div class="note">Log Scale / Monthly High-Low<br>';
  html+='--- Cash Flow per Sh x15<br>';
  html+='--- Relative Strength (vs HSI)<br><br>';
  html+='P/E (TTM): '+spot.pe+'x<br>';
  html+='P/B: '+spot.pb+'x<br>';
  html+='Div Yield: '+spot.div_yield+'%</div>';
  html+='</div></div>';

  // 23-line Statistical Array
  html+='<div class="stat-table"><table>';
  html+='<tr><th></th>';
  Y.forEach(function(y){{html+='<th>'+y+'</th>';}});
  html+='</tr>';
  M.forEach(function(m){{
    var isHigh=(m.field==='DPS'||m.field==='PAYOUT_RATIO');
    html+='<tr'+(isHigh?' style="background:#fffde7"':'')+'>';
    html+='<td>'+m.name_cn+'<br><span style="font-size:7px;color:#999">'+m.name_en+'</span></td>';
    Y.forEach(function(y){{
      var v=(MT[y]||{{}})[m.field];
      var txt='—';
      if(v!=null){{
        if(m.unit==='亿')txt=v.toFixed(1);
        else if(m.unit==='%')txt=v.toFixed(1);
        else if(m.unit==='元')txt=v.toFixed(2);
        else if(m.unit==='百万股')txt=v.toFixed(0);
        else txt=v.toFixed(1);
      }}
      html+='<td>'+txt+'</td>';
    }});
    html+='</tr>';
  }});
  html+='</table></div>';

  // Analyst Commentary
  html+='<div class="analyst">';
  html+='<b>ANALYST COMMENTARY</b>';
  html+='<p>POP MART delivered record FY2025: revenue ¥37.1B (+184.7%), net profit ¥12.8B (+308.8%), gross margin 72.1%, ROE 77.5%. THE MONSTERS surpassed ¥14B in revenue. Overseas share reached 43.8% from 38.9%. H1 2025 alone exceeded full-year 2024 revenue. At P/E 16.0x, below historical minimum of 18.3x — valuation at cheapest since IPO.</p>';
  html+='<p>Key risks: high-growth sustainability, IP lifecycle concentration (THE MONSTERS = 38% of revenue), US-China trade policy affecting overseas supply chain, intensifying global competition in character-based entertainment.</p>';
  html+='</div>';

  // Revenue Structure
  html+='<div style="font-weight:700;font-size:9.5px;margin:6px 4px 2px 4px;border-bottom:1px solid #000;padding-bottom:2px">REVENUE STRUCTURE — FY2025</div>';
  html+='<div style="display:flex;gap:4px;margin:4px;height:150px">';
  html+='<div style="flex:1" id="chart_channel"></div>';
  html+='<div style="flex:1" id="chart_ip"></div>';
  html+='<div style="flex:1" id="chart_region"></div>';
  html+='</div>';

  // Footer
  html+='<div class="footer">Data: AKShare + Annual/Semi-annual Report PDF | Validation: '+(v.status==='OK'?'✅':'⚠️')+' | Sources: annual indicators, semi-annual income, dividend, revenue structure, HSI kline</div>';

  html+='</div>'; // end center-col

  // ========================
  // 右栏
  // ========================
  html+='<div class="right-col">';
  html+='<div class="sec"><div class="sec-title">Per Share Data</div>';
  html+='<table>';
  html+='<tr><td>Earnings</td><td class="r b">'+(ly.BASIC_EPS||0).toFixed(2)+'</td></tr>';
  html+='<tr><td>Revenues</td><td class="r b">'+(ly.PER_OI||0).toFixed(2)+'</td></tr>';
  html+='<tr><td>Cash Flow</td><td class="r b">'+(ly.PER_NETCASH_OPERATE||0).toFixed(2)+'</td></tr>';
  html+='<tr><td>Book Value</td><td class="r b">'+(ly.BPS||0).toFixed(2)+'</td></tr>';
  html+='<tr><td>Cap Spend</td><td class="r">'+(ly.CAPEX_PS||0).toFixed(2)+'</td></tr>';
  html+='<tr><td>Dividends</td><td class="r b">'+(ly.DPS||0).toFixed(3)+'</td></tr>';
  html+='<tr><td>Com.Shares</td><td class="r">1,341M</td></tr>';
  html+='<tr><td>Avg PE</td><td class="r">'+(ly.PE_AVG||'—')+'</td></tr>';
  html+='<tr><td>Rel PE</td><td class="r">'+(ly.PE_RELATIVE||'—')+'</td></tr>';
  html+='</table></div>';

  html+='<div class="sec"><div class="sec-title">Key Ratios</div>';
  html+='<table>';
  html+='<tr><td>Gross Margin</td><td class="r b">'+(ly.GROSS_PROFIT_RATIO||0).toFixed(1)+'%</td></tr>';
  html+='<tr><td>Net Margin</td><td class="r b">'+(ly.NET_PROFIT_RATIO||0).toFixed(1)+'%</td></tr>';
  html+='<tr><td>ROE</td><td class="r b">'+(ly.ROE_AVG||0).toFixed(1)+'%</td></tr>';
  html+='<tr><td>ROIC</td><td class="r b">'+(ly.ROIC_YEARLY||0).toFixed(1)+'%</td></tr>';
  html+='<tr><td>Debt/Asset</td><td class="r">'+(ly.DEBT_ASSET_RATIO||0).toFixed(1)+'%</td></tr>';
  html+='<tr><td>Payout Ratio</td><td class="r">'+(ly.PAYOUT_RATIO||'—')+'%</td></tr>';
  html+='</table></div>';

  html+='<div class="sec"><div class="sec-title">Valuation Summary</div>';
  html+='<table>';
  html+='<tr><td>PE Range</td><td class="r">'+(pos.pe?pos.pe.min+'x ~ '+pos.pe.max+'x':'—')+'</td></tr>';
  html+='<tr><td>Current PE</td><td class="r b">'+spot.pe+'x</td></tr>';
  html+='<tr><td>Avg Hist PE</td><td class="r">'+(pos.pe?pos.pe.avg+'x':'—')+'</td></tr>';
  html+='<tr><td>Price Range</td><td class="r">'+(pos.price?pos.price.min+' ~ '+pos.price.max:'—')+'</td></tr>';
  html+='<tr><td></td><td class="r" style="color:'+(pos.pe&&pos.pe.pct<0?'#ef232a':'#333')+'">'+(pos.pe&&pos.pe.pct<0?'★ Below Hist Min':'')+'</td></tr>';
  html+='</table></div>';

  html+='</div>'; // end right-col

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
      {{name:'POP MART',type:'candlestick',data:ohlc,
        itemStyle:{{color:'#ef232a',color0:'#14b143',borderColor:'#ef232a',borderColor0:'#14b143'}}}}
    ];

    var cfData=d.cf_line||[];
    var cfMap={{}};
    cfData.forEach(function(c){{cfMap[c.date]=c.value;}});
    var cfSeries=dates.map(function(dt){{return cfMap[dt]||null;}});
    if(cfSeries.some(function(v){{return v!=null;}})){{
      series.push({{name:'CFx15',type:'line',data:cfSeries,
        lineStyle:{{type:'dashed',color:'#333',width:1}},symbol:'none'}});
    }}
    if(rsStock.length>0){{
      series.push({{name:'POP MART (idx)',type:'line',data:rsStock,
        lineStyle:{{color:'#ef232a',width:1.2}},symbol:'none',yAxisIndex:1}});
      series.push({{name:'HSI (idx)',type:'line',data:rsHsi,
        lineStyle:{{color:'#999',width:1,type:'dotted'}},symbol:'none',yAxisIndex:1}});
    }}

    echarts.init(document.getElementById('chart_kline')).setOption({{
      tooltip:{{trigger:'axis'}},
      grid:{{left:50,right:60,top:8,bottom:28}},
      xAxis:{{type:'category',data:dates,axisLabel:{{fontSize:7,rotate:45}}}},
      yAxis:[
        {{type:'log',scale:true,axisLabel:{{fontSize:7}}}},
        {{type:'value',axisLabel:{{fontSize:7}},splitLine:{{show:false}}}}
      ],
      series:series
    }});

    var rs=d.revenue_structure||{{}};
    var pieOpt=function(title,data){{
      return {{
        title:{{text:title,textStyle:{{fontSize:9}},left:'center',top:2}},
        series:[{{type:'pie',radius:['35%','65%'],center:['50%','52%'],
          label:{{fontSize:7,formatter:'{{b}}\\n{{d}}%'}},
          data:data.map(function(x){{return {{name:x.name,value:x.value}};}})}}]
      }};
    }};

    if(rs.by_channel&&rs.by_channel.length)
      echarts.init(document.getElementById('chart_channel')).setOption(pieOpt('By Channel',rs.by_channel));
    if(rs.by_region&&rs.by_region.length)
      echarts.init(document.getElementById('chart_region')).setOption(pieOpt('By Region',rs.by_region));

    if(rs.by_ip&&rs.by_ip.length){{
      echarts.init(document.getElementById('chart_ip')).setOption({{
        title:{{text:'By IP (RMB M)',textStyle:{{fontSize:9}},left:'center',top:2}},
        grid:{{left:50,right:15,top:25,bottom:45}},
        xAxis:{{type:'category',data:rs.by_ip.map(function(x){{return x.name;}}),axisLabel:{{fontSize:6,rotate:25}}}},
        yAxis:{{type:'value',axisLabel:{{fontSize:6}}}},
        series:[{{type:'bar',data:rs.by_ip.map(function(x){{return x.value;}}),
          itemStyle:{{color:'#378ADD'}},barMaxWidth:20}}]
      }});
    }}
  }},300);
}})();
</script>
</body>
</html>'''

out_path = os.path.join(BASE, "report.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"Generated: {out_path} ({len(HTML)} chars)")
print(f"  Layout: Left(270px) + Center(flex) + Right(255px) — Value Line classic 3-column")
