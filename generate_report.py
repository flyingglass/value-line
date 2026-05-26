"""
generate_report.py — 从 report_data.json 生成自包含 HTML (Value Line 风格)
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "report_data.json"), encoding="utf-8") as f:
    DATA = json.load(f)

# 营收结构现在从 report_data.json 动态读取 (来自 SQLite revenue_structure 表)
# 不再硬编码

DATA_JS = json.dumps(DATA, ensure_ascii=False)

HTML = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1200">
<title>Value Line — POP MART 09992.HK</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:#f4f4f0;color:#1a1a1a;width:1180px;margin:0 auto;padding:12px;font-size:11px;line-height:1.4}}
.section{{margin:5px 0}}
.section-title{{font-size:11.5px;font-weight:700;color:#333;border-bottom:1.5px solid #333;padding-bottom:2px;margin-bottom:3px;text-transform:uppercase;letter-spacing:0.5px}}
.sub{{font-size:9px;color:#888}}
.header{{display:flex;justify-content:space-between;align-items:center;background:#1a1a1a;color:#fff;padding:5px 12px;font-size:11.5px}}
.header .code{{font-weight:700;font-size:13px}}
.header .val{{font-weight:700;font-size:13px;color:#ffd740}}
.header .lbl{{color:#aaa;font-size:9px}}
.chart-row{{display:flex;gap:6px;height:320px}}
.chart-main{{flex:1}}
.chart-side{{width:185px;background:#fff;padding:5px 7px;font-size:9.5px;border:1px solid #e0e0e0}}
.chart-side table{{width:100%;border-collapse:collapse;margin-top:3px}}
.chart-side td,.chart-side th{{padding:1px 3px;text-align:right}}
.chart-side th{{font-weight:600;border-bottom:1px solid #ccc;font-size:9px}}
.chart-side .note{{color:#999;font-size:8.5px;margin-top:5px;line-height:1.35}}
.metric-table{{overflow-x:auto}}
.metric-table table{{border-collapse:collapse;font-size:10px;width:100%}}
.metric-table th,.metric-table td{{text-align:right;padding:1.5px 4px;border-right:1px solid #e8e8e8;white-space:nowrap}}
.metric-table th:first-child,.metric-table td:first-child{{text-align:left;font-weight:600;min-width:125px}}
.metric-table th{{background:#333;color:#fff;font-weight:500;font-size:9.5px}}
.metric-table tr:nth-child(even){{background:#fafafa}}
.metric-table tr:nth-child(odd){{background:#fff}}
.metric-table .highlight{{background:#fffde7!important;font-weight:600}}
.block-row{{display:flex;gap:6px;margin:5px 0}}
.block-row>div{{flex:1;background:#fff;padding:5px 7px;font-size:9.5px;border:1px solid #e0e0e0}}
.block-row table{{width:100%;border-collapse:collapse}}
.block-row td{{padding:0.5px 2px}}
.block-row .bold{{font-weight:700;text-align:right}}
.block-row .ttl{{font-weight:600;font-size:10px;margin-bottom:2px;border-bottom:1px solid #ccc;padding-bottom:1.5px}}
.semi-table{{font-size:10px;margin-top:4px}}
.semi-table table{{border-collapse:collapse;width:100%}}
.semi-table th,.semi-table td{{text-align:right;padding:1px 3px;border:1px solid #ddd}}
.semi-table th{{background:#f5f5f5;font-weight:600;font-size:9.5px}}
.semi-table td:first-child,.semi-table th:first-child{{text-align:left;font-weight:600}}
.rev-row{{display:flex;gap:6px}}
.rev-row>div{{flex:1;height:190px;background:#fff;border:1px solid #e0e0e0}}
.analyst-row{{display:flex;gap:6px}}
.analyst-row>div{{flex:1;font-size:10px;line-height:1.55;padding:6px 8px;background:#fff;border:1px solid #e0e0e0}}
.analyst-row .bt{{font-weight:700;font-size:10.5px;margin-bottom:3px}}
.footer{{padding:5px;text-align:center;color:#bbb;font-size:9.5px;border:1px dashed #ddd;margin-top:3px}}
</style>
</head>
<body>
<div id="app"></div>
<script>
var DATA = {DATA_JS};

(function(){{
  var d=DATA, M=d.metric_defs, Y=d.years, MT=d.data, SA=d.semi_annual;
  var app=document.getElementById('app');
  var html='';

  // ============================================================
  // 区域一: Header
  // ============================================================
  html+='<div class="header">';
  html+='<span class="code">POP MART 09992.HK</span>';
  html+='<span class="lbl">股价</span><span class="val">'+(d.spot.price||'--')+'</span>';
  html+='<span class="lbl">52周高低</span><span class="val">—</span>';
  html+='<span class="lbl">PE(TTM)</span><span class="val">'+(d.spot.pe||0).toFixed(1)+'</span>';
  html+='<span class="lbl">PB</span><span class="val">'+(d.spot.pb||0).toFixed(2)+'</span>';
  html+='<span class="lbl">股息率</span><span class="val">'+(d.spot.div_yield||0).toFixed(2)+'%</span>';
  html+='</div>';

  // ============================================================
  // Current Position (估值定位)
  // ============================================================
  var pos=d.position||{{}};
  function positionBar(label, data, unit, color){{
    if(!data.current) return '';
    var pct=Math.max(0, Math.min(100, data.pct||50));
    var lowText=(data.pct!=null && data.pct<0)?'⇐ LOW':'';
    var highText=(data.pct!=null && data.pct>100)?'HIGH ⇒':'';
    var s='<div style="display:flex;align-items:center;gap:4px;margin:1px 0;font-size:9px">';
    s+='<span style="width:42px;font-weight:600">'+label+'</span>';
    s+='<span style="width:40px;text-align:right;color:#999;font-size:8px">'+data.min+unit+'</span>';
    s+='<div style="flex:1;height:8px;background:#e8e8e8;border-radius:4px;position:relative;margin:0 4px">';
    s+='<div style="position:absolute;top:-2px;left:calc('+pct+'% - 2px);width:4px;height:12px;background:'+color+';border-radius:2px"></div>';
    s+='</div>';
    s+='<span style="width:40px;text-align:left;color:#999;font-size:8px">'+data.max+unit+'</span>';
    s+='<span style="width:55px;font-weight:700;color:'+color+'">'+data.current+unit+'</span>';
    s+='<span style="color:#ff6b35;font-size:8px"> '+lowText+highText+'</span>';
    s+='</div>';
    return s;
  }}
  html+='<div class="section-title">Current Position (历史估值区间定位)</div>';
  html+='<div style="display:flex;gap:12px;background:#fff;padding:4px 8px;border:1px solid #e0e0e0;font-size:10px">';
  html+='<div style="flex:1">';
  html+=positionBar('P/E(TTM)',pos.pe||{{}},'x','#ef232a');
  html+=positionBar('Price',pos.price||{{}},'','#333');
  html+=positionBar('P/B',pos.pb||{{}},'x','#378ADD');
  html+='</div>';
  html+='<div style="width:140px;font-size:8px;color:#999;line-height:1.4;border-left:1px solid #eee;padding-left:8px">';
  html+='PE Range: '+(pos.pe?pos.pe.min+'x ~ '+pos.pe.max+'x':'—')+'<br>';
  html+='Price Range: '+(pos.price?pos.price.min+' ~ '+pos.price.max:'—')+'<br>';
  html+='Avg PE: '+(pos.pe?pos.pe.avg+'x':'—')+'<br>';
  html+='Avg Price: '+(pos.price?pos.price.avg:'—')+'<br>';
  html+='<span style="color:#ff6b35">'+(pos.pe && pos.pe.pct<0?'★ PE 低于历史最低':'')+'</span>';
  html+='</div></div>';

  // ============================================================
  // 区域二: 走势图 (Log Scale + RS line + Total Return)
  // ============================================================
  var kl=d.kline, hsi=d.hsi_kline||[], lastIdx=kl.length-1;
  function totalReturn(n){{
    if(kl.length<=n) return '—';
    var start=kl[kl.length-1-n].close, end=kl[lastIdx].close;
    if(!start||!end) return '—';
    return ((end/start-1)*100).toFixed(0)+'%';
  }}
  html+='<div class="section-title">Monthly Price Ranges (Log Scale) + Relative Strength vs HSI</div>';
  html+='<div class="chart-row"><div class="chart-main" id="chart_kline"></div>';
  html+='<div class="chart-side"><div style="font-weight:600;font-size:10px">% Total Return</div>';
  html+='<table><tr><th></th><th>1yr</th><th>3yr</th><th>5yr</th></tr>';
  html+='<tr><td>POPMART</td><td>'+totalReturn(12)+'</td><td>'+totalReturn(36)+'</td><td>'+totalReturn(60)+'</td></tr>';
  html+='<tr><td>HSI</td><td>—</td><td>—</td><td>—</td></tr></table>';
  html+='<div class="note" style="margin-top:6px">— — — Cash Flow per Sh x15<br>— — Relative Strength Line<br>(POPMART vs HSI, indexed)<br><br>Insider: N/A<br>Institutional: N/A</div></div></div>';

  // ============================================================
  // 区域三: 23行指标表
  // ============================================================
  html+='<div class="section-title">Statistical Array</div><div class="metric-table"><table>';
  html+='<tr><th>Indicators</th>';
  Y.forEach(function(y){{html+='<th>'+y+'</th>';}});
  html+='</tr>';
  M.forEach(function(m){{
    var isDividend=(m.field==='DPS'||m.field==='PAYOUT_RATIO');
    html+='<tr'+(isDividend?' class="highlight"':'')+'>';
    html+='<td>'+m.name_cn+(isDividend?' ★':'')+'<br><span class="sub">'+m.name_en+'</span></td>';
    Y.forEach(function(y){{
      var v=(MT[y]||{{}})[m.field];
      var txt='—';
      if(v!=null){{
        if(m.unit==='亿')txt=v>1e8?(v/1e8).toFixed(1):v.toFixed(2);
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

  // ============================================================
  // 区域四: Capital Structure & Quarterly
  // 1. CAPITAL STRUCTURE | 2. CURRENT POSITION | 3. ANNUAL RATES | 4. QUARTERLY
  // ============================================================
  var cs=d.capital_structure||{{}}, cp=d.current_position||{{}}, ar=d.annual_rates||{{}}, qt=d.quarterly||{{}};
  var latestYr=Y[Y.length-1];

  html+='<div class="section-title">Capital Structure & Quarterly Data</div>';

  // ----- Block 1: CAPITAL STRUCTURE + Block 3: ANNUAL RATES (side by side) -----
  html+='<div class="block-row">';

  // 1. CAPITAL STRUCTURE
  html+='<div><div class="ttl">1. Capital Structure (as of '+Y[Y.length-1]+'-12-31)</div><table>';
  html+='<tr><td>Total Debt</td><td class="bold">¥'+(cs.total_debt||0).toFixed(1)+'B</td></tr>';
  html+='<tr><td>LT Debt</td><td class="bold">¥'+(cs.lt_debt||0).toFixed(1)+'B</td>';
  html+='<td style="color:#999">('+cs.lt_debt_pct+'% of Capital)</td></tr>';
  html+='<tr><td>Total Assets</td><td class="bold">¥'+(cs.total_assets||0).toFixed(1)+'B</td></tr>';
  html+='<tr><td>Shareholders Eq.</td><td class="bold">¥'+(cs.total_equity||0).toFixed(1)+'B</td></tr>';
  html+='<tr><td>Common Stock</td><td class="bold">'+cs.common_shares_str+'</td></tr>';
  html+='<tr><td>Market Cap</td><td class="bold">¥'+(cs.mkt_cap||0).toFixed(0)+'B</td>';
  html+='<td style="color:#999">('+(cs.cap_label||'—')+')</td></tr>';
  html+='</table></div>';

  // 2. Key Ratios
  var ly=MT[latestYr]||{{}};
  html+='<div><div class="ttl">Key Ratios (FY'+latestYr+')</div><table>';
  html+='<tr><td>Gross Margin</td><td class="bold">'+(ly.GROSS_PROFIT_RATIO||0).toFixed(1)+'%</td></tr>';
  html+='<tr><td>Net Margin</td><td class="bold">'+(ly.NET_PROFIT_RATIO||0).toFixed(1)+'%</td></tr>';
  html+='<tr><td>ROE</td><td class="bold">'+(ly.ROE_AVG||0).toFixed(1)+'%</td></tr>';
  html+='<tr><td>ROIC</td><td class="bold">'+(ly.ROIC_YEARLY||0).toFixed(1)+'%</td></tr>';
  html+='<tr><td>EPS</td><td class="bold">'+(ly.BASIC_EPS||0).toFixed(2)+'</td></tr>';
  html+='<tr><td>Rev/Sh</td><td class="bold">'+(ly.PER_OI||0).toFixed(2)+'</td></tr>';
  html+='<tr><td>BV/Sh</td><td class="bold">'+(ly.BPS||0).toFixed(2)+'</td></tr>';
  html+='<tr><td>CF/Sh</td><td class="bold">'+(ly.PER_NETCASH_OPERATE||0).toFixed(2)+'</td></tr>';
  html+='</table></div>';

  // 3. ANNUAL RATES of Change
  html+='<div><div class="ttl">3. Annual Rates of Change</div><table>';
  html+='<tr><th></th><th>Past 10yr</th><th>Past 5yr</th><th>Future 3-5yr</th></tr>';
  var ar_items=[
    ['Sales',ar.sales],['Cash Flow',ar.cashflow],['Earnings',ar.earnings],['Dividends',ar.dividends]
  ];
  ar_items.forEach(function(item){{
    var vals=item[1]||{{}};
    html+='<tr><td>'+item[0]+'</td>';
    html+='<td class="bold">'+(vals['10yr']!=null?vals['10yr'].toFixed(1)+'%':'—')+'</td>';
    html+='<td class="bold">'+(vals['5yr']!=null?vals['5yr'].toFixed(1)+'%':'—')+'</td>';
    html+='<td class="bold">'+vals['future']+'</td>';
    html+='</tr>';
  }});
  html+='</table></div></div>';

  // ----- Block 2: CURRENT POSITION (3-year comparison) -----
  html+='<div class="block-row">';
  html+='<div style="flex:1.5"><div class="ttl">2. Current Position (Balance Sheet, ¥ Billions)</div>';
  html+='<table style="font-size:9px">';
  var cpYears=cp.years||[];
  html+='<tr><th></th>';
  cpYears.forEach(function(yr){{html+='<th style="text-align:right">'+yr+'</th>';}});
  html+='</tr>';
  (cp.items||[]).forEach(function(item){{
    var isTotal=(item.name.indexOf('Current Assets')>=0||item.name.indexOf('Current Liabilities')>=0);
    html+='<tr'+(isTotal?' style="font-weight:700;border-top:1px solid #333"':'')+'>';
    html+='<td>'+(isTotal?'<b>':'')+item.name+(isTotal?'</b>':'')+'</td>';
    cpYears.forEach(function(yr){{
      html+='<td style="text-align:right">'+(item[yr]||0).toFixed(1)+'</td>';
    }});
    html+='</tr>';
  }});
  html+='</table></div>';
  html+='</div>';

  // ----- Block 4: QUARTERLY TABLES (港股: H1/H2) -----
  html+='<div class="block-row">';
  // Sales
  html+='<div><div class="ttl">4a. Quarterly Sales (¥ B) <span style="font-weight:400;color:#999;font-size:8px">港股H1/H2</span></div>';
  html+='<table style="font-size:9px">';
  html+='<tr><th>Year</th><th>H1</th><th>H2</th><th>Full</th></tr>';
  (qt.sales||[]).forEach(function(r){{
    html+='<tr><td>'+r.year+'</td><td>'+r.q1q2+'</td><td>'+r.q3q4+'</td><td style="font-weight:700">'+r.full+'</td></tr>';
  }});
  html+='</table></div>';
  // EPS
  html+='<div><div class="ttl">4b. Quarterly EPS <span style="font-weight:400;color:#999;font-size:8px">港股H1/H2</span></div>';
  html+='<table style="font-size:9px">';
  html+='<tr><th>Year</th><th>H1</th><th>H2</th><th>Full</th></tr>';
  (qt.eps||[]).forEach(function(r){{
    html+='<tr><td>'+r.year+'</td><td>'+(r.q1q2!=null?r.q1q2.toFixed(2):'—')+'</td><td>'+(r.q3q4!=null?r.q3q4.toFixed(2):'—')+'</td><td style="font-weight:700">'+(r.full!=null?r.full.toFixed(2):'—')+'</td></tr>';
  }});
  html+='</table></div>';
  // Dividends
  html+='<div><div class="ttl">4c. Quarterly Dividends <span style="font-weight:400;color:#999;font-size:8px">HKD/股</span></div>';
  html+='<table style="font-size:9px">';
  html+='<tr><th>Year</th><th>H1</th><th>H2</th><th>Full</th></tr>';
  (qt.dividends||[]).forEach(function(r){{
    html+='<tr><td>'+r.year+'</td>';
    html+='<td>'+(r.q1q2>0?r.q1q2.toFixed(3):'—')+'</td>';
    html+='<td>'+(r.q3q4>0?r.q3q4.toFixed(3):'—')+'</td>';
    html+='<td style="font-weight:700">'+(r.full>0?r.full.toFixed(3):'—')+'</td>';
    html+='</tr>';
  }});
  html+='</table></div>';
  html+='</div>';

  // ============================================================
  // 区域五: 营收结构
  // ============================================================
  html+='<div class="section-title">Revenue Breakdown — FY2025</div>';
  html+='<div class="rev-row"><div id="chart_channel"></div><div id="chart_ip"></div><div id="chart_region"></div></div>';

  // ============================================================
  // 区域六: 分析师
  // ============================================================
  html+='<div class="section-title">Business / Analyst Commentary</div><div class="analyst-row">';
  html+='<div><div class="bt">BUSINESS</div><p>POP MART (09992.HK) is a leading character-based entertainment company in China, specializing in IP incubation, pop toy retail, theme parks, and IP experiences. The Group owns 17 artist IPs with annual revenue exceeding RMB100M, including THE MONSTERS (LABUBU), MOLLY, SKULLPANDA, DIMOO, and CRYBABY. By end-2025, overseas revenue accounted for 43.8%, with 530 retail stores (445 in PRC + 85 overseas) and 2,396 roboshops.</p></div>';
  html+='<div><div class="bt">ANALYST COMMENTARY</div><p>POP MART delivered record FY2025 results: revenue RMB37.1B (+184.7%), net profit RMB12.8B (+308.8%), gross margin 72.1%, ROE 77.5%, ROIC 130.7%. THE MONSTERS surpassed RMB14B in revenue, becoming the first RMB10B+ IP. H1 2025 already exceeded full-year 2024 revenue, demonstrating explosive growth. Overseas revenue share rose from 38.9% to 43.8% YoY. Key risks: high-growth sustainability, IP lifecycle management, US-China trade tensions.</p></div></div>';

  // 区域七: 市场情绪
  var v=d.validation||{{}};
  html+='<div class="footer">Section VII: Market Sentiment — Institutional Ratings / Price Target Consensus / Fund Flows (TBD)';
  html+='<br><span style="font-size:9px;color:#999">Data Validation: AKShare ↔ Annual Report PDF — '+(v.status==='OK'?'✅ ALL 15 checks passed (0 mismatch)':'⚠️ '+v.status)+' | PDF-only: Semi-Annual H1, Revenue Structure</span></div>';

  app.innerHTML=html;

  // ============================================================
  // ECharts
  // ============================================================
  setTimeout(function(){{
    var dates=kl.map(function(k){{return k.date;}}),
        ohlc=kl.map(function(k){{return [k.open,k.close,k.low,k.high];}});

    // RS line: normalize both stock and HSI to 100 at the start
    var rsDates=[], rsStock=[], rsHsi=[];
    if(hsi.length>0){{
      var hsiMap={{}};
      hsi.forEach(function(h){{hsiMap[h.date]=h.close;}});
      var baseStock=null,baseHsi=null;
      dates.forEach(function(dt){{
        var sc=kl.find(function(k){{return k.date===dt;}});
        var hc=hsiMap[dt];
        if(sc&&hc){{
          if(baseStock===null){{baseStock=sc.close;baseHsi=hc;}}
          rsDates.push(dt);
          rsStock.push(baseStock?(sc.close/baseStock*100).toFixed(1):100);
          rsHsi.push(baseHsi?(hc/baseHsi*100).toFixed(1):100);
        }}
      }});
    }}

    var series=[
      {{name:'Candlestick',type:'candlestick',data:ohlc,
        itemStyle:{{color:'#ef232a',color0:'#14b143',borderColor:'#ef232a',borderColor0:'#14b143'}}}}
    ];

    // Add CF line
    var cfData=d.cf_line||[];
    var cfMap={{}};
    cfData.forEach(function(c){{cfMap[c.date]=c.value;}});
    var cfSeries=dates.map(function(dt){{return cfMap[dt]||null;}});
    if(cfSeries.some(function(v){{return v!=null;}})){{
      series.push({{name:'CFx15',type:'line',data:cfSeries,
        lineStyle:{{type:'dashed',color:'#333',width:1.1}},symbol:'none'}});
    }}

    // Add RS lines
    if(rsStock.length>0){{
      series.push({{name:'POPMART Indexed',type:'line',data:rsStock,
        lineStyle:{{color:'#ef232a',width:1.5}},symbol:'none',
        yAxisIndex:1}});
      series.push({{name:'HSI Indexed',type:'line',data:rsHsi,
        lineStyle:{{color:'#333',width:1.2,type:'dotted'}},symbol:'none',
        yAxisIndex:1}});
    }}

    var c1=echarts.init(document.getElementById('chart_kline'));
    c1.setOption({{
      tooltip:{{trigger:'axis'}},
      legend:{{data:['CFx15','POPMART Indexed','HSI Indexed'],bottom:0,textStyle:{{fontSize:9}}}},
      grid:{{left:55,right:70,top:10,bottom:40}},
      xAxis:{{type:'category',data:dates,axisLabel:{{fontSize:8,rotate:45}}}},
      yAxis:[
        {{type:'log',scale:true,axisLabel:{{fontSize:8}},splitLine:{{lineStyle:{{color:'#e8e8e8'}}}}}},
        {{type:'value',axisLabel:{{fontSize:8}},splitLine:{{show:false}},name:'Indexed=100'}}
      ],
      series:series
    }});

    var c2=echarts.init(document.getElementById('chart_channel'));
    c2.setOption({{title:{{text:'By Channel (PRC)',textStyle:{{fontSize:10}},left:'center',top:3}},
      series:[{{type:'pie',radius:['35%','65%'],center:['50%','55%'],
        label:{{fontSize:8,formatter:'{{b}}\\n{{d}}%'}},
        data:(DATA.revenue_structure.by_channel||[]).map(function(x){{return {{name:x.name,value:x.value}};}})}}]
    }});

    var c3=echarts.init(document.getElementById('chart_ip'));
    c3.setOption({{title:{{text:'By IP (RMB M)',textStyle:{{fontSize:10}},left:'center',top:3}},
      grid:{{left:55,right:15,top:28,bottom:55}},
      xAxis:{{type:'category',data:(DATA.revenue_structure.by_ip||[]).map(function(x){{return x.name;}}),axisLabel:{{fontSize:7,rotate:30}}}},
      yAxis:{{type:'value',axisLabel:{{fontSize:7}}}},
      series:[{{type:'bar',data:(DATA.revenue_structure.by_ip||[]).map(function(x){{return x.value;}}),
        itemStyle:{{color:'#378ADD'}},barMaxWidth:24}}]
    }});

    var c4=echarts.init(document.getElementById('chart_region'));
    c4.setOption({{title:{{text:'By Region',textStyle:{{fontSize:10}},left:'center',top:3}},
      series:[{{type:'pie',radius:['40%','70%'],center:['50%','50%'],
        label:{{fontSize:9,formatter:'{{b}}\\n{{d}}%'}},
        data:(DATA.revenue_structure.by_region||[]).map(function(x){{return {{name:x.name,value:x.value}};}})}}]
    }});
  }},300);
}})();
</script>
</body>
</html>'''

# 写入
out_path = os.path.join(BASE, "report.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"Generated: {out_path} ({len(HTML)} chars)")
print(f"  Sections: Header + Chart(RS) + 23-line + Cap/SA/CAGR + Revenue + Analyst + Sentiment")
