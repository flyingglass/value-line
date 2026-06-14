# -*- coding: utf-8 -*-
"""
Value Line 中文版 — 标的管理配置
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# 确保数据目录存在
os.makedirs(os.path.join(DATA_DIR, "pdfs"), exist_ok=True)

# ============================================================
# 标的定义
# ============================================================
# ============================================================
# 港股年报PDF直链 (手动维护, 从港交所披露易获取)
# URL格式: https://www.hkexnews.hk/listedco/listconews/sehk/{次年}/{MMDD}/{编号}_c.pdf
# ============================================================
HK_PDF_URLS = {
    "09992": {
        "2025": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0325/2026032500285.pdf",
        "2024": "https://www1.hkexnews.hk/listedco/listconews/sehk/2025/0326/2025032600228_c.pdf",
        "2023": "https://www1.hkexnews.hk/listedco/listconews/sehk/2024/0320/2024032000318_c.pdf",
    },
    "00981": {
        "2025": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0327/2026032700422.pdf",
        "2024": "https://www1.hkexnews.hk/listedco/listconews/sehk/2025/0327/2025032700201.pdf",
        "2023": "https://www1.hkexnews.hk/listedco/listconews/sehk/2024/0322/2024032200320.pdf",
    },
}

STOCKS = {
    # ⚠️ business_desc 和 analyst.commentary 为 fallback:
    #    优先从年报 PDF 提取 (extract_mda.py → engine.py 解析),
    #    仅在 PDF 提取失败时使用以下静态配置。
    # ⚠️ valuation_method: 估值方法, 默认 "cf" (CF倍数×每股现金流)。
    #    "cf" 适合消费/科技/成长股; "pb" 适合银行/保险/周期股/资产型标的 (PB倍数×每股净资产)。
    #    可通过 CLI --method cf|pb 或 --cf N / --pb N 覆盖。
    "09992": {
        "name": "泡泡玛特",
        "name_en": "POP MART",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "王宁",
        "inc": "开曼群岛",
        "website": "www.popmart.com",
        "org_id": "9900047555",
        "hkex_stock_id": "1000068054",
        "pfx": "hk",
        "shares": 1341043150,
        "shares_str": "1,341,043,150",
        "industry": "Consumer",
        "business_desc": "泡泡玛特是中国领先的潮流文化娱乐公司，以IP为核心，业务涵盖艺术家发掘、IP运营、产品设计制造、全球零售及粉丝社区运营。旗下IP包括THE MONSTERS(LABUBU)、SKULLPANDA、MOLLY、DIMOO等。2025年海外收入占比达44%。",
    },
    "00981": {
        "name": "中芯国际",
        "name_en": "SMIC",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "HKD",
        "ceo": "刘训峰",
        "inc": "开曼群岛",
        "website": "www.smics.com",
        "hkex_stock_id": "7249",
        "pfx": "hk",
        "shares": 7967000000,
        "shares_str": "7,967,000,000",
        "industry": "Semiconductor",
        "fiscal_yr_end": "12-31",
        "valuation_method": "pb",
        "business_desc": "中芯国际是中国大陆规模最大、技术最先进的晶圆代工企业，提供0.35μm到FinFET工艺的集成电路制造服务。核心业务为晶圆代工，覆盖逻辑、射频、CIS、PMIC、BCD、NOR Flash、NAND Flash等工艺平台。全球晶圆代工市场排名第五、中国大陆第一。A+H双上市（港股00981，科创板688981）。",
    },
    "09988": {
        "name": "阿里巴巴",
        "name_en": "Alibaba Group",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "吴泳铭",
        "inc": "开曼群岛",
        "website": "www.alibaba.com",
        "org_id": "",
        "pfx": "hk",
        "fiscal_yr_end": "03-31",
        "shares": 19000000000,
        "shares_str": "19,000,000,000",
        "industry": "Technology",
        "business_desc": "阿里巴巴集团是全球领先的电子商务及科技公司，核心业务涵盖中国商业（淘宝、天猫、1688）、国际商业（AliExpress、Lazada、Trendyol）、云计算（阿里云，中国第一）、本地生活、菜鸟物流及数字娱乐。FY2025营收9,964亿。AI驱动云业务加速增长，国际电商和菜鸟为第二增长曲线。",
    },
    "600519": {
        "name": "贵州茅台",
        "name_en": "Kweichow Moutai",
        "market": "cn",
        "exchange": "SSE",
        "currency": "CNY",
        "ceo": "张德芹",
        "inc": "中国贵州仁怀",
        "website": "www.moutaichina.com",
        "org_id": "gssh0600519",      # 巨潮内部ID
        "pfx": "sh",
        "shares": 1256197800,          # 总股本(股数), 约12.56亿股
        "shares_str": "1,256,197,800",
        "industry": "Consumer Staples",
        "fiscal_yr_end": "12-31",
        "business_desc": "贵州茅台是中国高端白酒绝对龙头，核心产品飞天茅台占据2000+元价格带垄断地位。公司拥有不可复制的地理护城河（茅台镇独特微生物环境）、深厚的品牌壁垒（国酒地位）及稀缺产能。年产基酒约5.7万吨，毛利率长期91%+，净利率50%+。",
    },
    "002014": {
        "name": "永新股份",
        "name_en": "Yongxin Co.",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "ceo": "待补充",
        "inc": "中国安徽黄山",
        "website": "www.yongxin-group.com",
        "pfx": "sz",
        "shares": 612000000,
        "shares_str": "612,000,000",
        "industry": "Packaging",
        "fiscal_yr_end": "12-31",
        "business_desc": "永新股份是中国领先的塑料软包装企业，主营食品、日化、医药等领域的复合软包装材料，客户覆盖宝洁、联合利华、雀巢等国际品牌。",
    },
    "00883": {
        "name": "中国海洋石油",
        "name_en": "CNOOC Ltd",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "张传江",
        "inc": "中国香港",
        "website": "www.cnoocltd.com",
        "org_id": "",
        "pfx": "hk",
        "shares": 47500000000,
        "shares_str": "47,500,000,000",
        "industry": "Energy",
        "fiscal_yr_end": "12-31",
        "business_desc": "中国海洋石油有限公司是中国最大的海上原油及天然气生产商，也是全球最大的独立油气勘探及生产企业之一。核心业务为原油和天然气的勘探、开发、生产及销售。收入结构：勘探及生产占比约86%，贸易业务约14%。注册地中国香港，CEO张传江。",
    },
    "01368": {
        "name": "特步国际",
        "name_en": "Xtep Int'l",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "pfx": "hk",
        "shares": 2806072400,
        "shares_str": "2,806,072,400",
        "industry": "Consumer",
        "business_desc": "",
    },
    "002027": {
        "name": "分众传媒",
        "name_en": "Focus Media",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "ceo": "江南春",
        "inc": "中国上海",
        "website": "www.focusmedia.cn",
        "org_id": "gssz0002027",
        "pfx": "sz",
        "shares": 14442000000,
        "shares_str": "14,442,000,000",
        "industry": "Media",
        "fiscal_yr_end": "12-31",
        "business_desc": "分众传媒是中国最大的生活圈媒体平台，核心业务为电梯电视和电梯海报广告，覆盖全国约300个城市的楼宇及影院。客户涵盖消费品、互联网、汽车等行业。公司占据电梯媒体市场领先份额，具有极高的品牌知名度与渠道壁垒。",
    },
    "000807": {
        "name": "云铝股份",
        "name_en": "Yunnan Aluminium",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "org_id": "gssz0000807",
        "pfx": "sz",
        "shares": 3467957588,
        "shares_str": "3,467,957,588",
        "industry": "Metals & Mining",
        "business_desc": "",
    },
    "000933": {
        "name": "神火股份",
        "name_en": "Shenhuo",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "org_id": "gssz0000933",
        "pfx": "sz",
        "shares": 2248548808,
        "shares_str": "2,248,548,808",
        "industry": "Metals & Mining",
        "business_desc": "",
    },
    "600595": {
        "name": "中孚实业",
        "name_en": "Zhongfu Industrial",
        "market": "cn",
        "exchange": "SSE",
        "currency": "CNY",
        "org_id": "gssh0600595",
        "pfx": "sh",
        "shares": 4000000000,
        "shares_str": "4,000,000,000",
        "industry": "Metals & Mining",
        "business_desc": "",
    },
    "002128": {
        "name": "电投能源",
        "name_en": "SPIC Energy",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "org_id": "",
        "pfx": "sz",
        "shares": 2241573493,
        "shares_str": "2,241,573,493",
        "industry": "Energy",
        "business_desc": "",
    },
    "01378": {
        "name": "中国宏桥",
        "name_en": "China Hongqiao",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "org_id": "",
        "pfx": "hk",
        "shares": 9481881123,
        "shares_str": "9,481,881,123",
        "industry": "Metals & Mining",
        "business_desc": "",
    },
    "002532": {
        "name": "天山铝业",
        "name_en": "Tianshan Aluminum",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "org_id": "",
        "pfx": "sz",
        "shares": 4651885415,
        "shares_str": "4,651,885,415",
        "industry": "Metals & Mining",
        "business_desc": "",
    },
    "002568": {
        "name": "百润股份",
        "name_en": "BAIRUN",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "ceo": "刘晓东",
        "inc": "中国上海",
        "website": "www.bairun.net",
        "org_id": "",                # 巨潮自动发现
        "pfx": "sz",
        "shares": 1049700000,
        "shares_str": "1,049,700,000",
        "industry": "Consumer Staples",
        "fiscal_yr_end": "12-31",
        "business_desc": "百润股份是中国预调鸡尾酒行业龙头，旗下RIO锐澳品牌占据80%以上市场份额。主营预调鸡尾酒及食用香精，构建即饮+居家+餐饮全场景覆盖。",
    },
    "00700": {
        "name": "腾讯控股",
        "name_en": "Tencent Holdings",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "马化腾",
        "inc": "开曼群岛",
        "website": "www.tencent.com",
        "shares": 9180000000,
        "shares_str": "9,180,000,000",
        "fiscal_yr_end": "12-31",
        "industry": "Technology",
        "alt_names": ["騰訊控股", "腾讯", "Tencent"],
        "business_desc": "腾讯控股是全球最大的互联网科技公司之一，核心业务涵盖社交通信(微信/QQ，月活13亿+)、游戏(国内+国际，全球最大游戏公司)、金融科技(微信支付/理财通)、云服务及企业服务。2025年营收超7,000亿元，游戏+社交为现金牛，视频号广告+AI大模型+企业服务为增长三极。持续巨额回购（2025年超1,000亿港元），每股收益增厚显著。",
        "analyst": {
            "commentary": [
                "腾讯2025年营收约7,200亿元（+10.2%），non-IFRS扣非净利润约2,200亿元（+22.5%）。游戏：国内基本盘稳固（《王者荣耀》《和平精英》《DNF手游》），国际游戏收入占比突破33%；社交网络：视频号广告VV（播放量）同比增长80%+，广告收入突破1,200亿元；金融科技及企业服务：AI混元大模型全面接入，云业务毛利率大幅改善，企业微信/腾讯会议DAU持续增长。",
                "每股收益¥24.15中，主业经营贡献¥19.80（82%），投资及非经营性贡献¥4.35（18%）。每股经营现金流¥28.50，资本支出¥6.20（AI算力+云基础设施），股份回购¥11.50/股（变相分红），净留存¥10.80/股。2025年回购超1,000亿港元，相当于总股本缩减~3%，每股价值持续增厚。净现金状态（现金-债务>2,000亿），财务极度稳健。",
                "毛利率52.3%、净利率（non-IFRS）30.5%、ROE 22.8%。腾讯的竞争壁垒是全球互联网中最深之一：①社交流量黑洞——微信13亿MAU形成的网络效应是地球上最强的消费者互联网护城河；②游戏产业链垂直整合——从研发（天美/光子/Riot/Supercell）到发行到电竞的全链条控制；③金融+云——微信支付覆盖10亿用户，企业服务处于AI转型风口。风险：监管政策、游戏版号、宏观经济影响广告预算、AI投入回报周期。",
                "当前PE约19倍（non-IFRS口径约15x），低于5年历史中位数23倍。PB约3.3倍。2025年股息率约0.5%（港股通扣税后），但回购收益率约4%，综合股东回报率约4.5%。净现金2,000亿+，安全边际充足。核心逻辑：视频号广告加载率从3%→6%（对标朋友圈8%）带来增量收入千亿级；AI大模型对内降本对外增收——这是PE从20x向25x重估的关键。",
                "腾讯正处于AI应用爆发的历史级催化剂中。混元大模型已覆盖微信搜一搜、腾讯云、腾讯广告、游戏NPC等核心场景。广告业务AI赋能实现精准投放效率大幅提升。企业微信+腾讯会议+混元=中国最大AI办公生态。若能成功将AI转化为可持续的广告/云/企业服务收入增量，PE存在显著重估空间。关注每季度AI相关收入占比披露。",
            ],
        },
    },
    "01698": {
        "name": "腾讯音乐",
        "name_en": "Tencent Music",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "梁柱",
        "inc": "开曼群岛",
        "website": "www.tencentmusic.com",
        "shares": 3220000000,
        "shares_str": "3,220,000,000",
        "fiscal_yr_end": "12-31",
        "industry": "Technology",
        "business_desc": "腾讯音乐娱乐集团是中国领先的在线音乐娱乐平台，运营QQ音乐、酷狗音乐、酷我音乐及全民K歌。通过在线音乐订阅（会员付费）和社交娱乐服务双轮变现。拥有超1.2亿在线音乐付费用户，付费率持续提升。AI音乐创作、AI推荐等新场景拓展中。",
    },
    "00696": {
        "name": "中国民航信息网络",
        "name_en": "TravelSky Technology",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "黄荣顺",
        "inc": "中国北京",
        "website": "www.travelsky.com.cn",
        "shares": 2926000000,
        "shares_str": "2,926,000,000",
        "fiscal_yr_end": "12-31",
        "industry": "Technology",
        "business_desc": "中国民航信息网络（TravelSky）是中国航空旅游业信息技术解决方案的垄断供应商，运营中国唯一的GDS订座系统（处理中国90%+机票预订）。核心业务包括航空信息技术服务（按机票量收费）、结算清算、机场IT及数据网络。垄断地位+政策壁垒确保定价权，利润率稳定40%+，受益于航空出行量增长。",
    },
    "01114": {
        "name": "华晨中国",
        "name_en": "Brilliance China",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "吴小安",
        "inc": "百慕大",
        "website": "www.brilliance-auto.com",
        "pfx": "hk",
        "shares": 5045000000,
        "shares_str": "5,045,000,000",
        "fiscal_yr_end": "12-31",
        "industry": "Automotive",
        "valuation_method": "pb",  # 资产型控股公司，PB 0.5x，适合PB估值
        "business_desc": "华晨中国汽车控股有限公司主要通过其合资企业华晨宝马（与宝马集团50:50合资）获得主要利润贡献。华晨宝马在中国生产销售宝马3系、5系、X3、X5等车型。公司同时制造及销售轻型客车及汽车零部件。受宝马股权转让（华晨宝马2022年转让25%股权）影响，持股降至25%，但品牌溢价和高端车需求仍为利润核心。",
        "analyst": {
            "commentary": [
                "华晨中国：宝马股权转让后，高股息现金牛",
                "2026年6月1日 — 华晨中国核心资产为华晨宝马25%股权。2022年完成向宝马转让25%华晨宝马股权（对价约290亿元），剩余25%股权仍为稳定利润来源。宝马品牌在中国豪华车市场市占率约25%，为华晨提供持续分红。",
                "公司持有大量现金（来自股权转让款），当前净现金约200亿元。自主品牌汽车（中华、金杯）体量较小。华晨宝马年销量约70万辆，高端车型占比持续提升。公司持续高比例派息，受限于宝马股权结构，未来分红稳定性取决于宝马中国业绩。",
                "当前PE约3倍（含一次性收益），PB 0.5倍。股息率超15%（含特别股息）。估值极低反映市场对华晨宝马股权价值的折价预期及公司治理担忧。关注宝马中国销量及分红政策——这是影响华晨价值的最大变量。"
            ],
        },
    },
    "06699": {
        "name": "时代天使",
        "name_en": "Angelalign",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "冯岱",
        "inc": "开曼群岛",
        "website": "www.angelalign.com",
        "pfx": "hk",
        "shares": 170882438,
        "shares_str": "170,882,438",
        "industry": "Healthcare",
        "business_desc": "时代天使是中国领先的隐形矫治解决方案提供商，核心业务为数字化口腔正畸服务。主要产品包括时代天使冠军版、经典版、儿童版及COMFOS等隐形矫治器系列，以及口内扫描仪等辅助设备。公司通过angelMind智能平台连接医生与患者，提供从诊断、方案设计到矫治器生产的全流程数字化正畸服务。拥有亚洲最大口腔数据库之一，覆盖全球数十万案例。2025年海外收入占比达44%。",
    },
    "000651": {
        "name": "格力电器",
        "name_en": "Gree Electric",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "ceo": "董明珠",
        "inc": "中国广东珠海",
        "website": "www.gree.com.cn",
        "pfx": "sz",
        "shares": 5601405741,
        "shares_str": "5,601,405,741",
        "industry": "Home Appliances",
        "fiscal_yr_end": "12-31",
        "business_desc": "格力电器是全球领先的空调制造企业，主营家用空调、商用空调、精密模具及智能装备的研发、生产与销售。格力空调连续多年稳居国内市场份额第一，产品远销全球200多个国家和地区。公司拥有强大的自主研发能力和完整的上下游产业链，是中国制造的一张名片。",
    },
    "600285": {
        "name": "羚锐制药",
        "name_en": "Lingrui Pharma",
        "market": "cn",
        "exchange": "SSE",
        "currency": "CNY",
        "ceo": "熊伟",
        "inc": "中国河南信阳",
        "website": "www.lingrui.com",
        "org_id": "gssh0600285",
        "pfx": "sh",
        "shares": 567000000,
        "shares_str": "567,000,000",
        "industry": "Pharmaceuticals",
        "fiscal_yr_end": "12-31",
        "business_desc": "羚锐制药是中国知名的中药企业，主营骨科外用贴膏剂（通络祛痛膏、壮骨麝香止痛膏等）、心脑血管用药及口服中成药的研发、生产与销售。公司是国内贴膏剂细分领域的龙头企业，核心产品覆盖基层医疗市场，品牌影响力深入县域。",
    },
    "000786": {
        "name": "北新建材",
        "name_en": "BNBM Group",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "ceo": "管理",
        "inc": "中国北京",
        "website": "www.bnbm.com.cn",
        "org_id": "gssz0000786",
        "pfx": "sz",
        "shares": 1702000000,
        "shares_str": "1,702,000,000",
        "industry": "Building Materials",
        "fiscal_yr_end": "12-31",
        "business_desc": '北新建材是中国最大的石膏板建材企业，主营石膏板、龙骨及新型建材的研发、生产和销售。旗下拥有"龙牌"、"泰山"等知名品牌，石膏板国内市场占有率长期保持第一。公司隶属于中国建材集团。',
    },
    "000408": {
        "name": "藏格矿业",
        "name_en": "Zangge Mining",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "ceo": "肖永明",
        "inc": "中国青海格尔木",
        "website": "www.zangge.com",
        "org_id": "gssz0000408",
        "pfx": "sz",
        "shares": 1568898254,
        "shares_str": "1,568,898,254",
        "industry": "Metals & Mining",
        "fiscal_yr_end": "12-31",
        "business_desc": "藏格矿业是中国领先的钾肥和盐湖提锂企业，核心业务为氯化钾（钾肥）和碳酸锂（新能源材料）的开采、生产与销售。公司拥有青海察尔汗盐湖724平方公里采矿权，钾资源储量超2亿吨，锂资源储量超200万吨LCE。控股西藏巨龙铜矿（30.78%股权），铜资源储量超2,000万吨，为第三增长极。实际控制人肖永明。",
    },
    "601225": {
        "name": "陕西煤业",
        "name_en": "Shaanxi Coal",
        "market": "cn",
        "exchange": "SSE",
        "currency": "CNY",
        "ceo": "赵福堂",
        "inc": "中国陕西西安",
        "website": "www.shxcoal.com",
        "org_id": "9900023204",
        "pfx": "sh",
        "shares": 9695000000,
        "shares_str": "9,695,000,000",
        "industry": "Energy",
        "fiscal_yr_end": "12-31",
        "business_desc": "陕西煤业是中国领先的煤炭生产企业，主营煤炭开采、洗选、运输和销售，拥有陕西优质煤炭资源，煤矿主要位于陕北、黄陇等煤田，煤质优良，是中国西部最大的煤炭生产商之一。",
    },
    "600900": {
        "name": "长江电力",
        "name_en": "Yangtze Power",
        "market": "cn",
        "exchange": "SSE",
        "currency": "CNY",
        "ceo": "张星燎",
        "inc": "中国北京",
        "website": "www.cypc.com.cn",
        "org_id": "gssh0600900",
        "pfx": "sh",
        "shares": 24468217716,
        "shares_str": "24,468,217,716",
        "industry": "Utilities",
        "fiscal_yr_end": "12-31",
        "business_desc": "长江电力是全球最大的水电上市公司，主营水力发电业务，拥有三峡、葛洲坝、溪洛渡、向家坝、乌东德、白鹤滩等世界级水电站，总装机容量超7000万千瓦。公司是中国清洁能源的核心旗舰企业。",
    },
    "02899": {
        "name": "紫金矿业",
        "name_en": "Zijin Mining",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "邹来昌",
        "inc": "中国福建厦门",
        "website": "www.zjky.cn",
        "pfx": "hk",
        "shares": 26400000000,
        "shares_str": "26,400,000,000",
        "industry": "Metals & Mining",
        "fiscal_yr_end": "12-31",
        "valuation_method": "pb",
        "business_desc": "紫金矿业是全球领先的大型跨国矿业集团，主营金、铜、锌等金属矿产资源的勘查、开采和冶炼。公司在中国、非洲、南美等地拥有多个世界级矿山，是全球成长最快的大型矿企之一。2025年营收3,491亿元。",
    },
    "02328": {
        "name": "中国财险",
        "name_en": "PICC P&C",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "于泽",
        "inc": "中国北京",
        "website": "property.picc.com",
        "pfx": "hk",
        "shares": 22242765303,
        "shares_str": "22,242,765,303",
        "industry": "Insurance",
        "fiscal_yr_end": "12-31",
        "valuation_method": "pb",  # 保险股适合PB估值
        "business_desc": "中国财险是中国最大的财产保险公司，主营机动车辆保险、企业财产保险、责任保险、意外伤害保险等业务，市场份额长期保持行业第一。公司隶属于中国人民保险集团，H股香港上市。",
    },
    "02099": {
        "name": "中国黄金国际",
        "name_en": "China Gold Intl",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "侯晨光",
        "inc": "加拿大",
        "website": "www.chinagoldintl.com",
        "pfx": "hk",
        "shares": 396413753,
        "shares_str": "396,413,753",
        "industry": "Metals & Mining",
        "fiscal_yr_end": "12-31",
        "business_desc": "中国黄金国际是中国黄金集团的海外旗舰，主营金、铜矿产资源的勘查和开发。公司核心资产包括内蒙古长山壕金矿和西藏甲玛铜金多金属矿，是中国黄金集团旗下唯一的海外上市平台。",
    },
    "01088": {
        "name": "中国神华",
        "name_en": "China Shenhua",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "吕志韧",
        "inc": "中国北京",
        "website": "www.shenhuachina.com",
        "pfx": "hk",
        "shares": 19870000000,
        "shares_str": "19,870,000,000",
        "industry": "Energy",
        "fiscal_yr_end": "12-31",
        "business_desc": "中国神华是中国最大的煤炭生产企业，主营煤炭开采、铁路运输、港口、发电等一体化业务。公司拥有神东、准格尔等世界级煤田，煤电路港航一体化模式具有极强的抗周期能力。A+H 双上市。",
    },
    "03606": {
        "name": "福耀玻璃",
        "name_en": "Fuyao Glass",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "叶舒",
        "inc": "中国福建福清",
        "website": "www.fuyaogroup.com",
        "pfx": "hk",
        "shares": 2600000000,
        "shares_str": "2,600,000,000",
        "industry": "Automotive",
        "fiscal_yr_end": "12-31",
        "business_desc": "福耀玻璃是全球最大的汽车玻璃供应商，主营汽车安全玻璃、浮法玻璃的生产和销售。全球市占率超30%，客户覆盖全球主要汽车厂商。创始人曹德旺。A+H 双上市。",
    },
    "00388": {
        "name": "香港交易所",
        "name_en": "HKEX",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "HKD",
        "ceo": "陈翊庭",
        "inc": "中国香港",
        "website": "www.hkex.com.hk",
        "pfx": "hk",
        "shares": 1270000000,
        "shares_str": "1,270,000,000",
        "industry": "Financial Services",
        "fiscal_yr_end": "12-31",
        "valuation_method": "pb",  # 交易所属于资产密集型，适合PB估值
        "business_desc": "香港交易所是全球主要交易所集团之一，运营香港联合交易所、香港期货交易所和伦敦金属交易所(LME)。核心收入来自交易费、结算费、上市费和数据服务，是亚洲最重要的国际金融基础设施。",
    },
    "09633": {
        "name": "农夫山泉",
        "name_en": "Nongfu Spring",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "钟睒睒",
        "inc": "中国浙江杭州",
        "website": "www.nongfuspring.com",
        "pfx": "hk",
        "shares": 11250000000,
        "shares_str": "11,250,000,000",
        "industry": "Consumer Staples",
        "fiscal_yr_end": "12-31",
        "business_desc": "农夫山泉是中国领先的包装饮用水及饮料企业，主营包装饮用水、茶饮料(东方树叶)、功能饮料(尖叫)和果汁饮料。连续多年保持中国包装饮用水市场占有率第一。",
    },
    "02097": {
        "name": "蜜雪集团",
        "name_en": "Mixue Group",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "张红超",
        "inc": "中国河南郑州",
        "website": "www.mxbc.com",
        "pfx": "hk",
        "shares": 380000000,
        "shares_str": "380,000,000",
        "industry": "Consumer",
        "fiscal_yr_end": "12-31",
        "business_desc": "蜜雪集团是中国最大的现制茶饮企业，全球门店超4万家，主营冰淇淋、柠檬水和茶饮产品。核心商业模式为加盟——向加盟商销售原材料、设备及收取服务费，轻资产、高现金流。定位极致性价比（2-8元价格带）。海外门店（东南亚为主）超4,000家。",
    },
    "605499": {
        "name": "东鹏饮料",
        "name_en": "Eastroc Beverage",
        "market": "cn",
        "exchange": "SSE",
        "currency": "CNY",
        "ceo": "林木勤",
        "inc": "中国广东深圳",
        "website": "www.eastrocbeverage.com",
        "org_id": "9900041766",
        "pfx": "sh",
        "shares": 520000000,
        "shares_str": "520,000,000",
        "industry": "Consumer Staples",
        "fiscal_yr_end": "12-31",
        "business_desc": "东鹏饮料是中国领先的功能饮料企业，核心产品东鹏特饮是国内能量饮料头部品牌。公司通过下沉市场和数字化营销快速扩张，2021年A股上市、2026年港股上市，A+H双资本平台。",
    },
    "01513": {
        "name": "丽珠集团",
        "name_en": "Livzon Pharma",
        "market": "hk",
        "exchange": "SEHK",
        "currency": "CNY",
        "ceo": "唐阳刚",
        "inc": "中国广东珠海",
        "website": "www.livzon.com.cn",
        "pfx": "hk",
        "shares": 940000000,
        "shares_str": "940,000,000",
        "industry": "Pharmaceuticals",
        "fiscal_yr_end": "12-31",
        "business_desc": "丽珠集团是中国领先的综合医药企业，主营化学药、中药、生物药和诊断试剂，核心品种包括消化药(壹丽安)、促性激素、抗感染药物等。A+H 双上市。",
    },
    "300750": {
        "name": "宁德时代",
        "name_en": "CATL",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "ceo": "曾毓群",
        "inc": "中国福建宁德",
        "website": "www.catl.com",
        "org_id": "GD165627",
        "pfx": "sz",
        "shares": 4627000000,
        "shares_str": "4,627,000,000",
        "industry": "Energy",
        "fiscal_yr_end": "12-31",
        "business_desc": "宁德时代是全球最大的动力电池和储能电池制造商，主营动力电池系统、储能电池系统和电池材料回收。全球市占率超35%，客户覆盖特斯拉、宝马、奔驰等全球主要车企。2025年营收4237亿元。",
    },
    "300308": {
        "name": "中际旭创",
        "name_en": "Zhongji Innolight",
        "market": "cn",
        "exchange": "SZSE",
        "currency": "CNY",
        "ceo": "刘圣",
        "inc": "中国江苏苏州",
        "website": "www.zj-innolight.com",
        "pfx": "sz",
        "shares": 1120000000,
        "shares_str": "1,120,000,000",
        "industry": "Semiconductor",
        "fiscal_yr_end": "12-31",
        "business_desc": "中际旭创是全球领先的光模块解决方案提供商，主营高速光通信收发模块的研发、设计和制造。产品覆盖100G/200G/400G/800G/1.6T光模块，是AI算力基础设施核心供应商。客户包括北美云厂商（Google/Meta/Microsoft/Amazon）及国内互联网公司。",
    },
    "NVDA": {
        "name": "英伟达",
        "name_en": "NVIDIA",
        "market": "us",
        "exchange": "NASDAQ",
        "currency": "USD",
        "ceo": "Jensen Huang",
        "inc": "美国特拉华州",
        "website": "www.nvidia.com",
        "pfx": "us",
        "cik": "0001045810",         # SEC CIK (Central Index Key)
        "shares": 2460000000,
        "shares_str": "2,460,000,000",
        "industry": "Semiconductor",
        "fiscal_yr_end": "01-26",  # FY ends ~Jan 26 (varies 25-31)
        "valuation_method": "cf",
        "business_desc": "NVIDIA是全球领先的GPU和AI加速计算公司，核心业务涵盖数据中心（GPU/AI芯片）、游戏、专业可视化和汽车。H100/B100/GB200等AI GPU垄断全球AI训练和推理市场超80%份额。CUDA生态是NVIDIA最深的护城河。2025年营收超1,300亿美元，数据中心占比超80%。",
        "analyst": {
            "commentary": [
                "NVIDIA：AI算力之王，高增长能否持续支撑高估值？",
                "2026年6月 — NVIDIA作为全球AI GPU绝对霸主，Blackwell架构GB200量产推动数据中心营收爆发。FY2026营收预计超1,300亿美元（+100%+），数据中心占比80%+。市场担忧：①AI基础设施投资是否可持续？②竞争（AMD、自研芯片）是否侵蚀份额？③增速拐点何时到来？",
                "NVIDIA的竞争壁垒是全球半导体行业最深的之一：①CUDA软件生态锁定——数百万开发者依赖CUDA，迁移成本极高；②架构代差——Blackwell领先竞品1-2代；③NVLink+InfiniBand端到端系统能力——不是单卖芯片，而是卖整个AI工厂。",
                "当前PE约35-45x，市场对2026年增速定价。若AI Capex维持高增长，估值有支撑；若增速放缓至30-40%，PE可能压缩至20-25x。关注每季度数据中心营收增速和毛利率趋势作为核心信号。",
            ],
        },
    },
}

# ============================================================
# 市场配置 (通用化: 兼容A股/H股/美股)
# ============================================================
MARKET_CONFIG = {
    "hk": {
        "name": "港股",
        "currency": "HKD",
        "index_name": "HSI",
        "index_name_cn": "恒生指数",
        "index_symbol": "HSI",
        "index_akshare_func": "stock_hk_index_daily_sina",
        "pe_estimate": {
            "2013": 11.0, "2014": 10.5, "2015": 10.0, "2016": 11.5,
            "2017": 12.5, "2018": 10.5, "2019": 11.0, "2020": 13.5,
            "2021": 10.5, "2022": 7.5,  "2023": 9.0,  "2024": 8.5, "2025": 8.0,
        },
    },
    "cn": {
        "name": "A股",
        "currency": "CNY",
        "index_name": "CSI300",
        "index_name_cn": "沪深300",
        "index_symbol": "000300",
        "index_akshare_func": "stock_zh_index_daily",
        "pe_estimate": {
            "2013": 12.0, "2014": 13.0, "2015": 18.0, "2016": 14.0,
            "2017": 15.0, "2018": 12.0, "2019": 14.0, "2020": 16.0,
            "2021": 15.0, "2022": 12.0, "2023": 13.0, "2024": 14.0, "2025": 14.0,
        },
    },
    "us": {
        "name": "美股",
        "currency": "USD",
        "index_name": "SPX",
        "index_name_cn": "标普500",
        "index_symbol": ".INX",
        "index_akshare_func": "stock_us_index_daily_sina",
        "pe_estimate": {
            "2013": 17.0, "2014": 18.5, "2015": 19.0, "2016": 20.0,
            "2017": 23.0, "2018": 18.0, "2019": 21.0, "2020": 28.0,
            "2021": 24.0, "2022": 18.0, "2023": 22.0, "2024": 24.0, "2025": 23.0,
        },
    },
}

# ============================================================
# 当前活跃标的
# ============================================================
ACTIVE_STOCK = "NVDA"

# ============================================================
# SQLite 路径
# ============================================================
def db_path(code):
    return os.path.join(DATA_DIR, f"{code}.db")

def pdf_dir(code):
    d = os.path.join(DATA_DIR, "pdfs", code)
    os.makedirs(d, exist_ok=True)
    return d

# ============================================================
# 财报期间定义
# ============================================================
# A股 巨潮分类码
CNINFO_CATEGORIES = {
    "FY":  "category_ndbg_szsh;",   # 年度报告
    "H1":  "category_bndbg_szsh;",  # 半年度报告
    "Q1":  "category_yjdbg_szsh;",  # 一季报
    "Q3":  "category_sjdbg_szsh;",  # 三季报
}

# 港股 港交所披露易分类码
HKEX_CATEGORIES = {
    "FY":  {"t1code": "40000", "t2code": "40100"},  # 年报
    "H1":  {"t1code": "40000", "t2code": "40200"},  # 中期报告
    "Q1":  {"t1code": "10000", "t2code": "13600"},  # 一季报
    "Q3":  {"t1code": "10000", "t2code": "13600"},  # 三季报
}

# 期间中文名
PERIOD_NAME = {
    "FY": "年报",
    "H1": "中报",
    "Q1": "一季报",
    "Q3": "三季报",
}

# ============================================================
# 标题黑名单 (排除非财报公告)
# ============================================================
TITLE_BLACKLIST = [
    "摘要", "已取消", "已撤销", "撤回", "取消", "更正前",
    "募集说明书", "ESG", "可持续发展",
    "审计报告", "财务报表", "意见",
    "英文版", "英文简版", "(英文)", "english",
    "港股公告", "H股公告",
]

# ============================================================
# Value Line 24行指标定义 (完整复刻VL官方名称, A股/H股对齐)
# Gross Margin 置于 Revenues 与 Operating Margin 之间
# 分隔线: 每股(#6) | 估值(#10) | 利润表(#17) | 资产负债(#20)
# ============================================================
VL_METRICS = [
    # (行号, 中文名, 英文名(VL原文), 数据字段, 单位, 来源表)
    # === 每股指标 (1-6) ===
    (1,  "每股营收",     "Revenues per sh",           "PER_OI",               "元",   "calculated"),
    (2,  "每股现金流",   "\"Cash Flow\" per sh",       "PER_NETCASH",          "元",   "calculated"),
    (3,  "每股收益",     "Earnings per sh",            "BASIC_EPS",            "元",   "indicators"),
    (4,  "每股股息",     "Div'ds Decl'd per sh",       "DPS",                  "元",   "dividend"),
    (5,  "每股资本支出", "Cap'l Spending per sh",      "CAPEX_PS",             "元",   "calculated"),
    (6,  "每股账面价值", "Book Value per sh",          "BPS",                  "元",   "indicators"),
    # === 股本与估值 (7-10) ===
    (7,  "发行在外股数", "Common Shs Outst'g (Mill.)",  "TOTAL_SHARES",         "百万股","calculated"),
    (8,  "平均年化PE",   "Avg Ann'l P/E Ratio",        "PE_AVG",               "倍",   "calculated"),
    (9,  "相对PE",       "Relative P/E Ratio",         "PE_RELATIVE",          "倍",   "calculated"),
    (10, "平均股息率",   "Avg Ann'l Div'd Yield",      "DIV_YIELD",            "%",    "calculated"),
    # === 利润表指标 (11-17, Gross Margin 置于 Revenues 与 Op Margin 之间) ===
    (11, "总营收",       "Revenues (亿)",               "OPERATE_INCOME",       "亿",   "indicators"),
    (12, "毛利率",       "Gross Margin",               "GROSS_MARGIN",         "%",    "calculated"),
    (13, "营业利润率",   "Operating Margin",           "OP_MARGIN",            "%",    "calculated"),
    (14, "折旧摊销",     "Depreciation (亿)",           "DEPRECIATION",         "亿",   "cashflow"),
    (15, "净利润",       "Net Profit (亿)",             "HOLDER_PROFIT",        "亿",   "indicators"),
    (16, "所得税率",     "Income Tax Rate",            "TAX_EBT",              "%",    "indicators"),
    (17, "净利润率",     "Net Profit Margin",          "NET_PROFIT_RATIO",     "%",    "calculated"),
    # === 资产负债指标 (18-20) ===
    (18, "营运资金",     "Working Cap'l (亿)",          "WORKING_CAPITAL",      "亿",   "calculated"),
    (19, "长期债务",     "Long-Term Debt (亿)",         "LT_DEBT",              "亿",   "calculated"),
    (20, "股东权益",     "Shr. Equity (亿)",            "TOTAL_EQUITY",         "亿",   "calculated"),
    # === 回报率指标 (21-24) ===
    (21, "投入资本回报率", "Return on Total Cap'l",      "ROIC",                 "%",    "calculated"),
    (22, "股东权益回报率","Return on Shr. Equity",      "ROE",                  "%",    "indicators"),
    (23, "留存利润再投比", "Retained to Com Eq",         "RETAINED_RATIO",       "%",    "calculated"),
    (24, "股息支付率",   "All Div'ds to Net Prof",     "PAYOUT_RATIO",         "%",    "calculated"),
    # 单位: 元(per sh), 亿(aggregate), %(ratio), 百万股(shares)
    # * DILUTED_EPS优先, AKShare
    # † 宣告股息(Decl'd), AKShare
    # ‡ 对标HSI/CSI300, VL ~1700只
]

if __name__ == "__main__":
    print(f"项目路径: {BASE_DIR}")
    print(f"数据目录: {DATA_DIR}")
    print(f"当前标的: {ACTIVE_STOCK} {STOCKS[ACTIVE_STOCK]['name']}")
    print(f"SQLite: {db_path(ACTIVE_STOCK)}")
