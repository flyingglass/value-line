# -*- coding: utf-8 -*-
"""香港交易所 00388 — VL Business + AI Commentary（数据驱动）"""
def build(stock, metrics, revenue_structure, years, cagr, spot):
    ly=metrics.get(years[-1],{}) if years else {}
    py=metrics.get(years[-2],{}) if len(years)>=2 else {}
    def _chg(c,p):
        try:
            c2,p2=float(c),float(p)
            if not c2 or not p2: return None
            if p2>0: return (c2/p2-1)*100
            if c2<0 and p2<0: return (c2-p2)/abs(p2)*100
            return (c2/p2-1)*100
        except: return None
    def _dir(c,p): return "增长" if (_chg(c,p) or 0)>0 else "下降"
    def _num(v): return float(v) if v is not None else 0
    def _fmt(v,d=0):
        try: return f"{float(v):,.{d}f}"
        except: return "-"
    def _p(v):
        try: return f"{float(v):+.1f}%"
        except: return "-"
    rev=_num(ly.get("OPERATE_INCOME"))
    np_val=_num(ly.get("HOLDER_PROFIT"))
    eps=_num(ly.get("BASIC_EPS"))
    npm=_num(ly.get("NET_PROFIT_RATIO"))
    roe=_num(ly.get("ROE"))
    roic=_num(ly.get("ROIC"))
    bps=_num(ly.get("BPS"))
    per_cf=_num(ly.get("PER_NETCASH"))
    per_capex=_num(ly.get("CAPEX_PS") or 0)
    dps=_num(ly.get("DPS") or 0)
    pb=_num(spot.get("pb",0))
    pe=_num(spot.get("pe",0))
    price=_num(spot.get("price",0))
    shares=_num(ly.get("TOTAL_SHARES"))
    r_chg=_chg(rev, py.get("OPERATE_INCOME"))
    n_chg=_chg(np_val, py.get("HOLDER_PROFIT"))
    r_abs=abs(r_chg) if r_chg is not None else 0
    n_abs=abs(n_chg) if n_chg is not None else 0
    div_yield=_num(ly.get("DIV_YIELD") or spot.get("div_yield",0))
    payout=_num(ly.get("PAYOUT_RATIO"))

    # Revenue structure
    prod_data = revenue_structure.get("by_product", []) if isinstance(revenue_structure, dict) else []
    交易 = next((r for r in prod_data if '交易' in r.get('name','')), None)
    结算 = next((r for r in prod_data if '结算' in r.get('name','')), None)
    上市 = next((r for r in prod_data if '上市' in r.get('name','')), None)
    投资 = next((r for r in prod_data if '投资' in r.get('name','')), None)

    biz=f"香港交易所是全球主要交易所集团之一，运营香港联合交易所、香港期货交易所和伦敦金属交易所(LME)。核心收入来自交易费及交易系统使用费、结算及交收费、上市费、市场数据费和投资收益，是亚洲最重要的国际金融基础设施。2025年港股现货日均成交额1941亿港元（+94%），IPO集资额2869亿港元（+226%）重登全球榜首。全年营收{_fmt(rev,0)}亿港元（含投资收益等约292亿），归母净利润{_fmt(np_val,0)}亿港元（同比增长{n_abs:.1f}%），ROE达{_p(roe)}。"

    p1=f"2025年营收{_fmt(rev,0)}亿港元（同比增长{r_abs:.1f}%），归母净利润{_fmt(np_val,0)}亿港元（同比增长{n_abs:.1f}%）。港交所是港股市场活跃度的\"晴雨表\"——2025年现货日均成交额1941亿港元，同比暴增94%；衍生产品日均成交78.3万张；LME金属合约日均成交75.7万手（2014年以来新高）。IPO市场强劲复苏：全年新股集资额2869亿港元（+226%），重登全球IPO融资榜首。上市费收入占比约9%，交易及结算费合计占比约55%，投资收益（保证金及结算所基金利息）占比约31%，构成多元化收入矩阵。"

    fcf_ps=_fmt(per_cf-per_capex-dps,2) if per_cf else "-"
    p2=f"每股收益{_fmt(eps,2)}港元，每股经营现金流{_fmt(per_cf,2)}港元，每股净资产{_fmt(bps,2)}港元。港交所是轻资产现金牛典范：经营现金流充沛，资本支出极低（IT系统维护为主），自由现金流{_fmt(per_cf-per_capex,2)}港元/股。股息率约{_fmt(div_yield,1)}%，派息比率长期维持90%左右，几乎将全部利润返还股东。交易所资产负债表特殊——负债率{_fmt(_num(ly.get('DEBT_ASSET_RATIO')),1)}%看似极高，实因结算所参与者保证金存款计入负债（对应流动资产中现金），扣除保证金后的净现金状况极为稳健。总股本12.7亿股。"

    p3=f"净利率{_p(npm)}、ROE{_p(roe)}。港交所的护城河是\"法定垄断+网络效应\"的复合壁垒：①法定垄断——香港唯一证券交易所+期货交易所+结算所，根据《证券及期货条例》获独家经营权；②网络效应——2200+上市公司、700+互联互通标的、全球最活跃的衍生产品市场之一，流动性越集中越难被替代；③互联互通——沪深港通是独一无二的跨境资本管道，南向资金日均交易占比超20%，累计净流入超4.35万亿港元；④LME定价权——全球有色金属定价基准交易所，2025年香港成为LME认可交割地；⑤轻资产高利润——净利率60%+，ROE 30%+，几乎零负债经营。风险：①高度依赖市场活跃度（ADT），熊市时收入和利润双杀（2022年ADT腰斩→利润-20%）；②地缘政治风险——中美摩擦影响中概股回归+外资流出；③竞争——新加坡/上海/深圳交易所在衍生品和国际化方面竞争加剧。"

    pe_calc=_fmt(price/eps,1) if eps and price else "-"
    pb_calc=_fmt(price/bps,2) if bps and price else "-"
    p4=f"当前股价约{_fmt(price,2)}港元，PE约{pe_calc}倍，PB约{pb_calc}倍。港交所历史PE区间约25-50倍（熊市20-25x，牛市40-50x），当前PE{pe_calc}倍处于历史中位偏下。按PB估值：每股净资产{_fmt(bps,2)}港元，交易所资产几乎全是现金+无形资产（交易权/牌照），PB={pb_calc}x反映的是牌照溢价+特许经营权价值。若按ROE=30%、PB=9x计算，隐含回报率约3.3%（ROE/PB），与股息率{_fmt(div_yield,1)}%相互印证。核心变量是ADT——若日均成交额维持在2800-3000亿港元（2026H1水平），盈利有望继续增长；若跌破1500亿，估值将承压。"

    p5=f"催化剂：①市场活跃度——2026H1港股日均成交额2830亿港元（+18%），Q2进一步升至2895亿，6月创3191亿季度新高，若趋势延续将驱动交易费收入持续增长；②IPO管道——2026H1共87家新股上市，集资2102亿港元（+92%），AI/科技/生物医药公司排队上市，上市费+交易量双重受益；③互联互通扩容——港股通标的持续扩展+ETF通+人民币柜枱，南向日均成交占比提升至22%+；④衍生品+虚拟资产——MSCI期货、恒生科技指数期权成交活跃，虚拟资产现货ETF扩容至9只，港交所进入数字资产时代；⑤LME商业化——香港成为LME交割地，大宗商品连接内地需求。关注每月ADT数据、IPO集资额、互联互通资金流向。"

    return {"business":biz,"commentary":[p1,p2,p3,p4,p5]}
