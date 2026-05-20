import yfinance as yf
import pandas as pd
import streamlit as st
import time
import requests
import numpy as np
import pytz
from datetime import datetime

# ════════════════════════════════════════════════════
#  CONFIG — isi di Streamlit Secrets
#  TELEGRAM_TOKEN = "xxx"
#  TELEGRAM_CHAT_ID = "xxx"
# ════════════════════════════════════════════════════
TOKEN      = st.secrets.get("TELEGRAM_TOKEN", "")
CHAT_ID    = st.secrets.get("TELEGRAM_CHAT_ID", "")
eastern_tz = pytz.timezone('America/New_York')

# Session state
for _k, _v in [("tt_last_sent", set()), ("wl_results", []),
                ("wl_mode_used", ""), ("scan_results", []),
                ("data_dict", {}), ("last_scan_time", None),
                ("last_scan_mode", "Scalping ⚡")]:
    if _k not in st.session_state: st.session_state[_k] = _v

st.set_page_config(layout="wide", page_title="US Turbo v1", page_icon="🦅", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');
:root {
    --bg:#080c10; --surface:#0d1117; --border:#1c2533;
    --accent:#00e5ff; --green:#00ff88; --red:#ff3d5a;
    --amber:#ffb700; --purple:#bf5fff; --orange:#ff7b00;
    --muted:#4a5568; --text:#c9d1d9; --heading:#e6edf3;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'Syne',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stSidebar"]{display:none!important;}
[data-testid="stExpander"]{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:8px!important;margin-bottom:12px!important;}
[data-testid="stExpander"] summary{font-family:'Space Mono',monospace!important;font-size:12px!important;color:var(--accent)!important;letter-spacing:1px!important;}
.settings-label{font-family:'Space Mono',monospace;font-size:10px;color:var(--muted);letter-spacing:2px;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--border);}
.tt-header{display:flex;align-items:center;padding:16px 0 12px 0;border-bottom:1px solid var(--border);margin-bottom:16px;}
.tt-logo{font-family:'Space Mono',monospace;font-size:22px;font-weight:700;color:var(--accent);letter-spacing:-1px;}
.tt-sub{font-size:11px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;}
.live-badge{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.3);border-radius:20px;font-family:'Space Mono',monospace;font-size:10px;color:var(--accent);letter-spacing:1px;margin-left:auto;}
.live-dot{width:6px;height:6px;background:var(--green);border-radius:50%;animation:blink 1s infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.2;}}
.metric-row{display:flex;gap:10px;margin-bottom:18px;flex-wrap:wrap;}
.metric-card{flex:1;min-width:110px;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px 14px;position:relative;overflow:hidden;}
.metric-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--accent);}
.metric-card.green::before{background:var(--green);}
.metric-card.red::before{background:var(--red);}
.metric-card.amber::before{background:var(--amber);}
.metric-card.orange::before{background:var(--orange);}
.metric-card.purple::before{background:var(--purple);}
.metric-label{font-size:10px;color:var(--muted);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;}
.metric-value{font-family:'Space Mono',monospace;font-size:24px;font-weight:700;color:var(--heading);line-height:1;}
.metric-sub{font-size:10px;color:var(--muted);margin-top:3px;}
.signal-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;margin-bottom:20px;}
.signal-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;position:relative;overflow:hidden;transition:border-color .2s;}
.signal-card.gacor{border-color:rgba(0,255,136,.4);background:rgba(0,255,136,.03);}
.signal-card.potensial{border-color:rgba(255,183,0,.3);background:rgba(255,183,0,.03);}
.signal-card.watch{border-color:rgba(0,229,255,.2);}
.signal-card.bagger{border-color:rgba(191,95,255,.6);background:rgba(191,95,255,.05);box-shadow:0 0 20px rgba(191,95,255,.15);}
.signal-card::after{content:'';position:absolute;top:0;left:0;width:4px;height:100%;}
.signal-card.gacor::after{background:var(--green);}
.signal-card.potensial::after{background:var(--amber);}
.signal-card.watch::after{background:var(--accent);}
.signal-card.bagger::after{background:var(--purple);}
.sc-ticker{font-family:'Space Mono',monospace;font-size:18px;font-weight:700;color:var(--heading);}
.sc-price{font-family:'Space Mono',monospace;font-size:13px;color:var(--muted);}
.sc-signal{font-size:13px;font-weight:700;margin:6px 0;}
.sc-bars{display:flex;gap:3px;margin:8px 0;}
.sc-bar{height:16px;border-radius:2px;}
.sc-bar.filled{background:var(--green);}
.sc-bar.filled-purple{background:var(--purple);}
.sc-bar.empty{background:var(--border);}
.sc-stats{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;}
.sc-stat{font-family:'Space Mono',monospace;font-size:10px;color:var(--muted);}
.sc-stat span{color:var(--text);}
.alert-box{background:rgba(255,61,90,.06);border:1px solid rgba(255,61,90,.4);border-radius:8px;padding:14px 18px;margin-bottom:16px;animation:pulse-border 2s infinite;}
.bagger-alert-box{background:rgba(191,95,255,.06);border:1px solid rgba(191,95,255,.5);border-radius:8px;padding:14px 18px;margin-bottom:16px;animation:pulse-purple 2s infinite;}
@keyframes pulse-border{0%,100%{border-color:rgba(255,61,90,.4);}50%{border-color:rgba(255,61,90,.9);}}
@keyframes pulse-purple{0%,100%{border-color:rgba(191,95,255,.4);}50%{border-color:rgba(191,95,255,.9);}}
.alert-title{color:var(--red);font-family:'Space Mono',monospace;font-size:12px;font-weight:700;letter-spacing:2px;}
.bagger-title{color:var(--purple);font-family:'Space Mono',monospace;font-size:12px;font-weight:700;letter-spacing:2px;}
.tape-wrap{overflow:hidden;white-space:nowrap;border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:5px 0;margin-bottom:16px;background:var(--surface);}
.tape-inner{display:inline-block;animation:marquee 35s linear infinite;}
@keyframes marquee{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.tape-item{display:inline-block;margin:0 18px;font-family:'Space Mono',monospace;font-size:10px;}
.tape-item.up{color:var(--green);}.tape-item.down{color:var(--red);}.tape-item.flat{color:var(--muted);}.tape-item.bagger{color:var(--purple);}
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:8px!important;}
[data-testid="stDataFrame"] thead th{background:var(--surface)!important;color:var(--muted)!important;font-family:'Space Mono',monospace!important;font-size:11px!important;letter-spacing:1px!important;text-transform:uppercase!important;}
::-webkit-scrollbar{width:4px;height:4px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
[data-testid="stNumberInput"] input{background:var(--surface)!important;border:1px solid var(--border)!important;color:var(--heading)!important;font-family:'Space Mono',monospace!important;border-radius:6px!important;}
button[data-testid="baseButton-primary"]{background:var(--accent)!important;color:var(--bg)!important;font-family:'Space Mono',monospace!important;font-weight:700!important;border:none!important;}
.section-title{font-family:'Space Mono',monospace;font-size:11px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;border-left:3px solid var(--accent);padding-left:10px;margin:20px 0 10px 0;}
.bt-result{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px;margin-top:12px;}
.bt-metric{display:inline-block;margin-right:24px;margin-bottom:8px;}
.bt-metric-val{font-family:'Space Mono',monospace;font-size:22px;font-weight:700;}
.bt-metric-lbl{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;}
@media(max-width:768px){.main .block-container{padding-left:.75rem!important;padding-right:.75rem!important;}.signal-grid{grid-template-columns:1fr;}}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  STOCK LIST — US MARKET (NYSE + NASDAQ)
# ════════════════════════════════════════════════════
raw_stocks = [
    # ── Technology
    "AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","AMD","INTC","QCOM",
    "TXN","AVGO","MU","AMAT","KLAC","LRCX","MRVL","CRM","ORCL","NOW",
    "SNOW","PLTR","UBER","NFLX","RBLX","TTWO","EA","SMCI","ARM","DELL",
    "HPQ","HPE","CSCO","ANET","NET","DDOG","CRWD","ZS","PANW","FTNT",
    "OKTA","MDB","VEEV","WDAY","ADBE","INTU","CDNS","SNPS","MPWR","ENTG",
    "ONTO","ON","SWKS","QRVO","WOLF","IONQ","QUBT","RGTI","ACHR","JOBY",
    # ── Financials
    "JPM","BAC","WFC","GS","MS","C","BLK","SCHW","AXP","V",
    "MA","PYPL","SQ","COIN","HOOD","SOFI","AFRM","UPST","NU","FIS",
    "FI","FISV","PAYX","ADP","ICE","CME","CBOE","NDAQ","SPGI","MCO",
    "BX","KKR","APO","CG","ARES","TPG","MET","PRU","AIG","AFL",
    "ALL","TRV","HIG","CB","PGR","L","RLI","EG","AIZ","RE",
    # ── Healthcare
    "JNJ","UNH","PFE","MRK","ABBV","LLY","BMY","AMGN","GILD","BIIB",
    "REGN","MRNA","VRTX","ILMN","ISRG","MDT","SYK","EW","ZBH","HCA",
    "CVS","WBA","MCK","ABC","CAH","DGX","LH","IQV","CRL","MEDP",
    "PODD","DXCM","HOLX","NVCR","HIMS","TDOC","RMD","INSP","IRTC","NEOG",
    # ── Consumer Discretionary
    "HD","LOW","TGT","COST","TJX","ROST","ULTA","NKE","LULU","PVH",
    "RL","ANF","AEO","GPS","M","KSS","DHI","LEN","PHM","GRMN",
    "ORLY","AZO","AAP","GPC","TSCO","DLTR","DG","FIVE","BURL","RH",
    "WSM","BKNG","ABNB","EXPE","HLT","MAR","H","MGM","WYNN","LVS",
    "DKNG","LYFT",
    # ── Consumer Staples
    "WMT","PG","KO","PEP","MDLZ","KHC","GIS","K","MKC","HRL",
    "CPB","CAG","SJM","MO","PM","BTI","CL","CHD","CLX","EL",
    "COTY","KR","SYY","USFD","SFM",
    # ── Energy
    "XOM","CVX","COP","EOG","OXY","PSX","VLO","MPC","SLB","HAL",
    "BKR","DVN","FANG","MRO","APA","HES","CTRA","EQT","AR","RRC",
    "RIG","NOV","PTEN","CHK","SW","OVV","TRGP","KMI","WMB","ET",
    "EPD","MPLX","PAGP",
    # ── Industrials
    "BA","CAT","HON","GE","MMM","RTX","LMT","NOC","GD","TDG",
    "ITW","EMR","ROK","PH","DOV","FTV","ROP","FAST","URI","WAB",
    "FDX","UPS","JBHT","XPO","SAIA","ODFL","CHRW","GXO","GWW","CARR",
    "OTIS","TT","JCI","AAON","BLDR","BECN","IBP","DOOR","AZEK","TREX",
    # ── Materials
    "LIN","APD","SHW","ECL","DD","DOW","NEM","FCX","AA","CLF",
    "X","NUE","STLD","RS","VMC","MLM","WRK","IP","PKG","SON",
    "ATR","BALL","BERY","SEE","SLGN","AMCR",
    # ── Real Estate
    "AMT","PLD","CCI","SPG","O","WP","VICI","EQIX","DLR","PSA",
    "EXR","WELL","VTR","BXP","SLG","KIM","REG","MAC","NNN","STORE",
    # ── Utilities
    "NEE","DUK","SO","AEP","EXC","XEL","PPL","WEC","CMS","NI",
    "ES","EIX","ETR","FE","CNP","AES","BKH","NWE","OGE","AVA",
    # ── Communication Services
    "DIS","CMCSA","CHTR","VZ","T","TMUS","WBD","FOXA","FOX","NWSA",
    "LUMN","OMC","IPG","LAMR","OUT","SPOT","SNAP","PINS","RDDT","MTCH",
    "IAC",
    # ── Extra Growth / Meme / Popular
    "GME","AMC","BBBY","RIVN","LCID","F","GM","STLA","NIO","XPEV",
    "LI","NKLA","WKHS","RIDE","GOEV","HYLN","HYZN","SES","BLNK","CHPT",
    "EVGO","VLCN","MULN","IDEX","SOLO","SOLO","MARA","RIOT","HUT","BTBT",
    "CLSK","CIFR","IREN","CORZ","BTDR",
]

seen = set(); raw_stocks = [x for x in raw_stocks if not (x in seen or seen.add(x))]
stocks_yf = raw_stocks          # No .JK suffix for US
stock_map  = {s: s for s in raw_stocks}

# ════════════════════════════════════════════════════
#  MARKET REGIME DETECTOR — S&P 500
# ════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def get_market_regime():
    try:
        df = yf.download("^GSPC", period="60d", interval="1d",
                         progress=False, auto_adjust=True, timeout=8)
        if df is None or len(df) < 10:
            return ("UNKNOWN", 0, 0, 0, "Data kurang", 0.0)
        close = df["Close"].squeeze()
        ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
        ema55 = float(close.ewm(span=min(55, len(close)-1), adjust=False).mean().iloc[-1])
        price = float(close.iloc[-1])
        chg   = float(((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100)
        if price < ema20:
            return ("RED",      price, ema20, ema55, f"S&P500 {price:,.0f} < EMA20 → Bearish", chg)
        elif price > ema20 and price > ema55:
            return ("GREEN",    price, ema20, ema55, f"S&P500 {price:,.0f} > EMA20 & EMA55 → Bullish", chg)
        else:
            return ("SIDEWAYS", price, ema20, ema55, f"S&P500 {price:,.0f} antara EMA20-EMA55", chg)
    except:
        return ("UNKNOWN", 0, 0, 0, "S&P500 tidak tersedia — manual mode", 0.0)

@st.cache_data(ttl=600)
def get_vix():
    try:
        df = yf.download("^VIX", period="5d", interval="1d",
                         progress=False, auto_adjust=True, timeout=8)
        if df is None or len(df) < 2: return 20.0, 0.0
        close = df["Close"].squeeze()
        vix   = float(close.iloc[-1])
        chg   = float(((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100)
        return vix, chg
    except:
        return 20.0, 0.0

def get_regime_config(regime, vix=20.0):
    # VIX overlay tweak
    if vix > 30:   vix_note = " · ⚠️ VIX FEAR"
    elif vix < 15: vix_note = " · 🧊 VIX LOW"
    else:          vix_note = ""
    return {
        "RED": {
            "mode": "Reversal 🎯", "min_score": 5, "min_rvol": 2.0, "sl_mult": 0.6,
            "label": f"🔴 MARKET MERAH — Reversal Only, Score ≥ 5{vix_note}",
            "color": "#ff3d5a",
            "desc":  "Market bearish. Fokus reversal oversold, filter ketat."
        },
        "GREEN": {
            "mode": "Bagger 💎", "min_score": 4, "min_rvol": 2.0, "sl_mult": 0.8,
            "label": f"🟢 MARKET HIJAU — Bagger Hunt Mode, Score ≥ 4{vix_note}",
            "color": "#00ff88",
            "desc":  "Market bullish. Cari breakout + akumulasi bagger. RVOL ≥ 2x."
        },
        "SIDEWAYS": {
            "mode": "Scalping ⚡", "min_score": 4, "min_rvol": 2.0, "sl_mult": 0.7,
            "label": f"🟡 MARKET SIDEWAYS — Scalping, RVOL ≥ 2x{vix_note}",
            "color": "#ffb700",
            "desc":  "Market sideways. RVOL harus lebih kuat."
        },
        "UNKNOWN": {
            "mode": "Scalping ⚡", "min_score": 4, "min_rvol": 1.5, "sl_mult": 0.8,
            "label": "⚪ REGIME UNKNOWN — Manual Mode",
            "color": "#4a5568",
            "desc":  "Tidak bisa deteksi kondisi market."
        },
    }.get(regime, {
        "mode": "Scalping ⚡", "min_score": 4, "min_rvol": 1.5, "sl_mult": 0.8,
        "label": "⚪ UNKNOWN", "color": "#4a5568", "desc": ""
    })

# ════════════════════════════════════════════════════
#  INDICATORS
# ════════════════════════════════════════════════════
def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def rsi_smooth(s, p=14, smooth=3):
    delta = s.diff()
    gain  = delta.clip(lower=0).rolling(p).mean()
    loss  = (-delta.clip(upper=0)).rolling(p).mean()
    rs    = gain / loss.replace(0, np.nan)
    raw   = 100 - 100/(1+rs)
    return raw, ema(raw, smooth)

def stochastic(h, l, c, k=14, d=3):
    ll = l.rolling(k).min(); hh = h.rolling(k).max()
    K  = 100*(c-ll)/(hh-ll).replace(0,np.nan)
    D  = K.rolling(d).mean()
    return K.fillna(50), D.fillna(50)

def macd(s, f=12, sl=26, sg=9):
    ml = ema(s,f)-ema(s,sl); sig = ema(ml,sg)
    return ml, sig, ml-sig

def vwap(df):
    tp = (df['High']+df['Low']+df['Close'])/3
    return (tp*df['Volume']).cumsum()/df['Volume'].cumsum()

def apply_intraday_indicators(df):
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
    df['EMA9']  = ema(df['Close'],9);  df['EMA21'] = ema(df['Close'],21)
    df['EMA50'] = ema(df['Close'],50); df['EMA200']= ema(df['Close'],200)
    df['RSI'], df['RSI_EMA'] = rsi_smooth(df['Close'],14,3)
    df['STOCH_K'], df['STOCH_D'] = stochastic(df['High'],df['Low'],df['Close'],14,3)
    df['MACD'], df['MACD_Sig'], df['MACD_Hist'] = macd(df['Close'])
    try:    df['VWAP'] = vwap(df)
    except: df['VWAP'] = df['Close']
    df['BB_mid']   = df['Close'].rolling(20).mean()
    df['BB_std']   = df['Close'].rolling(20).std()
    df['BB_upper'] = df['BB_mid']+2*df['BB_std']; df['BB_lower']= df['BB_mid']-2*df['BB_std']
    df['BB_pct']   = (df['Close']-df['BB_lower'])/(df['BB_upper']-df['BB_lower'])
    df['AvgVol']   = df['Volume'].rolling(20).mean()
    df['RVOL']     = df['Volume']/df['AvgVol']
    df['NetVol']   = np.where(df['Close']>=df['Open'],df['Volume'],-df['Volume'])
    df['NetVol3']  = pd.Series(df['NetVol'],index=df.index).rolling(3).sum()
    df['NetVol8']  = pd.Series(df['NetVol'],index=df.index).rolling(8).sum()
    df['VolSpike'] = df['RVOL']>2.5
    df['Body']     = (df['Close']-df['Open']).abs()
    df['BodyRatio']= df['Body']/(df['High']-df['Low']).replace(0,np.nan)
    df['BullBar']  = (df['Close']>df['Open'])&(df['BodyRatio']>0.5)
    df['ROC3']     = df['Close'].pct_change(3); df['ROC8'] = df['Close'].pct_change(8)
    df['HH']= df['High']>df['High'].shift(1);  df['HL']= df['Low']>df['Low'].shift(1)
    df['LL']= df['Low']<df['Low'].shift(1);    df['LH']= df['High']<df['High'].shift(1)
    tr = pd.concat([df['High']-df['Low'],(df['High']-df['Close'].shift()).abs(),(df['Low']-df['Close'].shift()).abs()],axis=1).max(axis=1)
    df['ATR'] = tr.rolling(14).mean()
    return df

# ════════════════════════════════════════════════════
#  SCORING FUNCTIONS
# ════════════════════════════════════════════════════
def score_scalping(r, p, p2):
    score=0; reasons=[]
    if r['EMA9']>r['EMA21']>r['EMA50']:   score+=1.5; reasons.append("EMA stack ▲")
    elif r['EMA9']>r['EMA21']:             score+=0.8; reasons.append("EMA9>21")
    if r['Close']>r['VWAP']:              score+=1;   reasons.append("Above VWAP")
    if r['MACD_Hist']>0 and r['MACD_Hist']>float(p['MACD_Hist']):
        score+=1.5; reasons.append("MACD hist expanding ✦")
        if p2 is not None and float(p['MACD_Hist'])>float(p2['MACD_Hist']): score+=0.3; reasons.append("MACD 3 bar rising")
    elif r['MACD_Hist']>0: score+=0.5; reasons.append("MACD hist +")
    rsi_e=float(r['RSI_EMA'])
    if 52<rsi_e<68:  score+=0.8; reasons.append(f"RSI-EMA={rsi_e:.1f}")
    elif rsi_e>=68:  score-=0.5
    rvol=float(r['RVOL'])
    if rvol>2.0:   score+=1;   reasons.append(f"RVOL={rvol:.1f}x surge")
    elif rvol>1.5: score+=0.6; reasons.append(f"RVOL={rvol:.1f}x")
    if bool(r['BullBar']):    score+=0.5; reasons.append("Bullish bar")
    if float(r['NetVol3'])>0: score+=0.4; reasons.append("Net vol +")
    if r['Close']<r['EMA200']*0.98: score-=0.5
    return max(0,min(6,round(score,1))), reasons, {}

def score_momentum(r, p, p2):
    score=0; reasons=[]
    hh=bool(r['HH']); hl=bool(r['HL'])
    if hh and hl:  score+=1.5; reasons.append("HH+HL pattern ▲")
    elif hh:       score+=0.8
    rvol=float(r['RVOL'])
    if rvol>3.0:   score+=1.5; reasons.append(f"RVOL={rvol:.1f}x SURGE 🔥")
    elif rvol>2.0: score+=1.0; reasons.append(f"RVOL={rvol:.1f}x")
    elif rvol>1.5: score+=0.5
    roc=float(r['ROC3'])*100
    if roc>2.0:   score+=1.5; reasons.append(f"ROC3={roc:.1f}%")
    elif roc>1.0: score+=0.8; reasons.append(f"ROC3={roc:.1f}%")
    elif roc<0:   score-=0.5
    rsi_e=float(r['RSI_EMA'])
    if 55<rsi_e<75: score+=0.8; reasons.append(f"RSI-EMA={rsi_e:.1f}")
    if rsi_e>78:    score-=0.8; reasons.append("⚠️ RSI overbought")
    sk=float(r['STOCH_K']); sd=float(r['STOCH_D'])
    if sk>60 and sk>sd: score+=0.8; reasons.append("STOCH K>D bullish")
    if r['MACD_Hist']>0 and r['MACD_Hist']>float(p['MACD_Hist']): score+=0.8; reasons.append("MACD expanding")
    if r['Close']>r['VWAP']: score+=0.5; reasons.append("Above VWAP")
    return max(0,min(6,round(score,1))), reasons, {}

def score_reversal(r, p, p2):
    score=0; reasons=[]; os_count=0
    rsi_e=float(r['RSI_EMA'])
    if rsi_e<30:   os_count+=1; score+=1.5; reasons.append(f"RSI-EMA={rsi_e:.1f} OS extreme")
    elif rsi_e<40: os_count+=1; score+=0.8; reasons.append(f"RSI-EMA={rsi_e:.1f} OS")
    sk=float(r['STOCH_K']); sd=float(r['STOCH_D'])
    if sk<20:   os_count+=1; score+=1;   reasons.append(f"STOCH={sk:.0f} extreme OS")
    elif sk<30: os_count+=1; score+=0.5
    bp=float(r['BB_pct'])
    if bp<0.05:   os_count+=1; score+=1;   reasons.append("BB lower touch")
    elif bp<0.15: os_count+=1; score+=0.5
    if os_count<1.5: return 0,[],{}
    rev=0
    pk=float(p['STOCH_K']); pd_=float(p['STOCH_D'])
    if sk<30 and sk>sd and pk<=pd_:   rev+=1; score+=2;   reasons.append("STOCH %K cross ↑ OS ✦✦")
    elif sk<25 and sk>sd:             rev+=1; score+=1.2; reasons.append("STOCH K>D extreme OS")
    if p is not None:
        rsi_p=float(p['RSI_EMA'])
        if rsi_e>rsi_p and rsi_e<42: rev+=1; score+=1.2; reasons.append("RSI-EMA pivot ↑")
    mh=float(r['MACD_Hist']); mh_p=float(p['MACD_Hist'])
    if mh>mh_p and mh<0: rev+=1; score+=0.8; reasons.append("MACD hist diverge ↑")
    if rev==0: score*=0.3
    if bool(r['VolSpike']) and float(r['Close'])<float(r['Open']): score+=0.8; reasons.append("Volume climax sell")
    elif float(r['RVOL'])>1.5: score+=0.4
    if float(r['NetVol3'])>0: score+=0.5; reasons.append("Net vol turning +")
    if float(r['BodyRatio'])>0.75 and float(r['Close'])<float(r['Open']): score-=0.8; reasons.append("⚠️ Bearish bar kuat")
    return max(0,min(6,round(score,1))), reasons, {}

# ════════════════════════════════════════════════════
#  BAGGER DETECTOR — Wyckoff Accumulation Edition
#
#  3 Layer Logic:
#  ① Phase A-B  : Sideways + Dry Volume + Stealth Net Buy
#  ② Spring     : New Low → V-Shape Recovery (Shakeout)
#  ③ Phase D    : RVOL Surge + Breakout + Thick Body
#
#  Deteksi sedini mungkin — masuk sebelum ritel sadar.
# ════════════════════════════════════════════════════
def score_bagger(r, p, p2, df_full):
    score  = 0
    reasons = []
    close  = float(r['Close'])
    e9     = float(r['EMA9']);  e21  = float(r['EMA21'])
    e50    = float(r['EMA50']); e200 = float(r['EMA200'])
    rvol   = float(r['RVOL'])
    rsi_e  = float(r['RSI_EMA'])
    wyckoff_phase = "SCANNING"

    # ════════════════════════════════════════════
    # ① PHASE A-B — SIDEWAYS + DRY VOLUME
    #    Bandar nyicil diam-diam, harga gak kemana-mana
    # ════════════════════════════════════════════
    is_sideways = False
    range_high  = close * 1.05   # fallback
    range_low   = close * 0.95
    sideways_bars = min(20, len(df_full) - 2)

    try:
        r_highs    = df_full['High'].iloc[-sideways_bars-1:-1]
        r_lows     = df_full['Low'].iloc[-sideways_bars-1:-1]
        range_high = float(r_highs.max())
        range_low  = float(r_lows.min())
        range_pct  = (range_high - range_low) / max(range_low, 0.01) * 100
        is_sideways = range_pct < 8.0   # <8% = konsolidasi sideways

        if is_sideways:
            tightness_bonus = max(0, (8.0 - range_pct) / 8.0)
            score += 1.0 + tightness_bonus * 0.5
            reasons.append(f"Sideways {range_pct:.1f}% ({sideways_bars}B) ✦")
            wyckoff_phase = "A-B"
    except:
        pass

    # ── Dry Volume: 5 bar terakhir vs MA20 ─────────
    try:
        vol_ma20  = float(df_full['AvgVol'].iloc[-1])
        vol_last5 = float(df_full['Volume'].iloc[-6:-1].mean())
        dry_ratio = vol_last5 / max(vol_ma20, 1)

        if dry_ratio < 0.5 and is_sideways:
            # Volume kering banget = bandar lagi collect diam-diam
            score += 2.0
            reasons.append(f"Dry vol {dry_ratio:.2f}x MA20 — stealth accum ✦✦")
            wyckoff_phase = "A-B AKUMULASI"
        elif dry_ratio < 0.7 and is_sideways:
            score += 1.2
            reasons.append(f"Vol drying {dry_ratio:.2f}x MA20 ✦")
            wyckoff_phase = "A-B AKUMULASI"
        elif dry_ratio < 0.85 and is_sideways:
            score += 0.6
            reasons.append(f"Vol below avg {dry_ratio:.2f}x")
    except:
        pass

    # ── Stealth Net Buy — proxy broker summary ──────
    # Harga diam tapi net buy konsisten = bandar nyicil
    try:
        if len(df_full) >= 12:
            netvols_10   = [float(df_full['NetVol'].iloc[i]) for i in range(-11, -1)]
            net_positive = sum(1 for v in netvols_10 if v > 0)
            net_ratio    = net_positive / 10

            if net_ratio >= 0.7 and is_sideways:
                score += 1.5
                reasons.append(f"Stealth net buy {net_positive}/10 bars ✦✦")
            elif net_ratio >= 0.6:
                score += 0.8
                reasons.append(f"Net buy {net_positive}/10 bars")
            elif net_ratio >= 0.5:
                score += 0.4
    except:
        nv3 = float(r['NetVol3']); nv8 = float(r['NetVol8'])
        if nv3 > 0 and nv8 > 0: score += 0.8; reasons.append("Net buyer sustained ✦")
        elif nv3 > 0:            score += 0.3; reasons.append("Net buyer 3 bar")

    # ── BB Squeeze selama sideways ──────────────────
    try:
        bb_curr  = float(r['BB_std'])
        bb_avg10 = float(df_full['BB_std'].iloc[-11:-1].mean())
        sq_ratio = bb_curr / max(bb_avg10, 0.0001)

        if sq_ratio < 0.7 and is_sideways:
            # BB sangat sempit = volatility dikompres, siap meledak
            score += 1.5
            reasons.append(f"BB squeeze extreme {sq_ratio:.2f}x ✦✦")
        elif sq_ratio < 0.85:
            score += 0.8
            reasons.append(f"BB squeeze {sq_ratio:.2f}x")
    except:
        pass

    # ════════════════════════════════════════════
    # ② SPRING / SHAKEOUT DETECTION
    #    Harga jebol support → rebound cepat = jebak ritel
    #    Sinyal paling powerful di Wyckoff
    # ════════════════════════════════════════════
    spring_detected = False
    try:
        lookback_sp = min(15, len(df_full) - 3)
        prior_lows  = df_full['Low'].iloc[-lookback_sp-2:-2]
        support     = float(prior_lows.min())

        bar_low   = float(r['Low'])
        bar_close = float(r['Close'])
        bar_high  = float(r['High'])

        # Spring: jebol support tapi close di atas = jebakan selesai
        is_spring = bar_low < support and bar_close > support
        if is_spring:
            recovery_strength = (bar_close - bar_low) / max(bar_high - bar_low, 0.0001)
            spring_vol_ok     = rvol > 1.2

            if recovery_strength > 0.7 and spring_vol_ok:
                score += 3.0
                reasons.append(f"🔥 SPRING! Support break → rebound {recovery_strength:.0%} ✦✦✦")
                wyckoff_phase = "SPRING ⚡"
                spring_detected = True
            elif recovery_strength > 0.5:
                score += 1.8
                reasons.append(f"Spring pattern (recovery {recovery_strength:.0%}) ✦✦")
                wyckoff_phase = "SPRING"
                spring_detected = True

        # Post-spring: bar sebelumnya spring, sekarang konfirmasi naik
        is_post_spring = (float(p['Low']) < support and
                          float(p['Close']) > support and
                          bar_close > float(p['Close']))
        if is_post_spring and not spring_detected:
            score += 2.0
            reasons.append("Post-spring confirmation 🚀 ✦✦")
            wyckoff_phase = "POST-SPRING"
            spring_detected = True
    except:
        pass

    # ════════════════════════════════════════════
    # ③ PHASE D — RVOL SURGE + BREAKOUT
    #    Konfirmasi entry aman — bandar gas-in
    # ════════════════════════════════════════════
    try:
        above_resistance = close > range_high * 0.998
        thick_body       = float(r['BodyRatio']) > 0.55
        bull_bar_flag    = float(r['Close']) > float(r['Open'])

        if rvol > 4.0 and above_resistance and thick_body and bull_bar_flag:
            score += 3.0
            reasons.append(f"🚀 PHASE D! RVOL={rvol:.1f}x breakout thick body ✦✦✦")
            wyckoff_phase = "PHASE D 🚀"
        elif rvol > 3.0 and above_resistance and bull_bar_flag:
            score += 2.2
            reasons.append(f"Breakout confirmed RVOL={rvol:.1f}x ✦✦")
            wyckoff_phase = "BREAKOUT ✦"
        elif rvol > 2.0 and above_resistance:
            score += 1.5
            reasons.append(f"Breakout attempt RVOL={rvol:.1f}x")
        elif above_resistance:
            score += 0.8
            reasons.append("Above resistance (low vol)")
        else:
            # Belum breakout — score RVOL standalone
            if rvol > 4.0:   score += 1.5; reasons.append(f"RVOL={rvol:.1f}x MASSIVE 🔥🔥")
            elif rvol > 3.0: score += 1.0; reasons.append(f"RVOL={rvol:.1f}x SURGE 🔥")
            elif rvol > 2.0: score += 0.5; reasons.append(f"RVOL={rvol:.1f}x")
            # Fase akumulasi = RVOL rendah wajar, jangan penalti
            elif rvol < 1.3 and wyckoff_phase not in ["A-B AKUMULASI","SPRING","POST-SPRING"]:
                score -= 0.5
    except:
        if rvol > 4.0:   score += 1.5; reasons.append(f"RVOL={rvol:.1f}x MASSIVE 🔥🔥")
        elif rvol > 3.0: score += 1.0; reasons.append(f"RVOL={rvol:.1f}x SURGE 🔥")
        elif rvol > 2.0: score += 0.5; reasons.append(f"RVOL={rvol:.1f}x")

    # ════════════════════════════════════════════
    # SUPPORTING INDICATORS
    # ════════════════════════════════════════════

    # ── EMA Structure ──────────────────────────────
    if e9 > e21 > e50 > e200:
        score += 1.5; reasons.append("EMA golden stack ✦✦")
    elif e9 > e21 > e50:
        score += 1.0; reasons.append("EMA stack ▲")
    elif e9 > e21:
        score += 0.4
    elif is_sideways and wyckoff_phase in ["A-B AKUMULASI","SPRING","POST-SPRING"]:
        score += 0.2; reasons.append("EMA flat (accum phase OK)")

    # ── RSI — konteks beda per fase ─────────────────
    if wyckoff_phase in ["A-B","A-B AKUMULASI","SPRING","POST-SPRING"]:
        # Saat akumulasi, RSI rendah itu BAGUS
        if 25 <= rsi_e <= 52:
            score += 1.0; reasons.append(f"RSI-EMA={rsi_e:.1f} accum zone ✓")
        elif rsi_e < 25:
            score += 0.6; reasons.append(f"RSI-EMA={rsi_e:.1f} extreme OS (load zone)")
        elif rsi_e > 65:
            score -= 0.3
    else:
        # Phase D / breakout → butuh RSI momentum
        if 52 < rsi_e < 72:
            score += 1.0; reasons.append(f"RSI-EMA={rsi_e:.1f} momentum zone")
        elif rsi_e >= 72:
            score -= 0.5; reasons.append(f"⚠️ RSI OB {rsi_e:.1f}")
        elif rsi_e < 40:
            score -= 0.3

    # ── VWAP & EMA200 floor ─────────────────────────
    if close > float(r['VWAP']): score += 0.5; reasons.append("Above VWAP")
    if close < e200 * 0.88:      score -= 1.0

    # ── Consecutive bull bars ───────────────────────
    try:
        if len(df_full) >= 4:
            bc = sum(1 for i in range(-3, 0)
                     if float(df_full['Close'].iloc[i]) > float(df_full['Open'].iloc[i]))
            if bc == 3:   score += 0.8; reasons.append("3x consecutive bull bars")
            elif bc == 2: score += 0.3
    except:
        pass

    # ── Label fase di depan reasons ─────────────────
    if wyckoff_phase != "SCANNING":
        reasons.insert(0, f"⚙️ Wyckoff: {wyckoff_phase}")

    return max(0, min(6, round(score, 1))), reasons, {"wyckoff_phase": wyckoff_phase}

# ════════════════════════════════════════════════════
#  OVERNIGHT PLAY SCORER — US Power Hour Play
#  Entry: 3:00–4:00 PM ET | Exit: next day 9:30–10:30 AM ET
# ════════════════════════════════════════════════════
def score_overnight(r, p, p2):
    score=0; reasons=[]
    close=float(r['Close']); hi=float(r['High']); lo=float(r['Low'])
    hi_lo=hi-lo; close_pct=(close-lo)/max(hi_lo,0.001)
    # Close near HOD = institutions buying into close
    if close_pct>0.80:   score+=2.5; reasons.append(f"Closed HOD {close_pct:.0%} ✦✦✦")
    elif close_pct>0.65: score+=1.5; reasons.append(f"Strong close {close_pct:.0%} ✦")
    elif close_pct>0.50: score+=0.8; reasons.append(f"Mid-high close {close_pct:.0%}")
    # RVOL surge at EOD = institutional accumulation
    rvol=float(r['RVOL'])
    if rvol>3.0:   score+=2.0; reasons.append(f"RVOL={rvol:.1f}x SURGE 🔥🔥")
    elif rvol>2.0: score+=1.5; reasons.append(f"RVOL={rvol:.1f}x kuat")
    elif rvol>1.5: score+=0.8; reasons.append(f"RVOL={rvol:.1f}x")
    # EMA stack
    if r['EMA9']>r['EMA21']>r['EMA50']:  score+=1.5; reasons.append("EMA stack ▲")
    elif r['EMA9']>r['EMA21']:            score+=0.8; reasons.append("EMA9>21")
    # RSI zone — not overbought
    rsi_e=float(r['RSI_EMA'])
    if 45<rsi_e<72:  score+=1;   reasons.append(f"RSI-EMA={rsi_e:.1f} ✓")
    elif rsi_e>=72:  score-=1;   reasons.append(f"RSI OB {rsi_e:.1f} ⚠️")
    elif rsi_e<40:   score+=0.5; reasons.append(f"RSI={rsi_e:.1f} OS bounce?")
    # MACD expanding
    mh=float(r['MACD_Hist']); mh_p=float(p['MACD_Hist'])
    if mh>0 and mh>mh_p: score+=1;   reasons.append("MACD hist expanding ✦")
    elif mh>0:            score+=0.5; reasons.append("MACD +")
    # Above VWAP = buyers in control
    if float(r['Close'])>float(r['VWAP']): score+=0.5; reasons.append("Above VWAP")
    # Sustained net buyer
    if float(r['NetVol3'])>0 and float(r['NetVol8'])>0:
        score+=0.5; reasons.append("Net buyer sustained ✦")
    return max(0,min(6,round(score,1))), reasons, {}

# ════════════════════════════════════════════════════
#  SIGNAL LABEL & CARD CLASS
# ════════════════════════════════════════════════════
def get_signal(score, mode):
    t = {
        "Scalping ⚡":  {5:"RIPPING ⚡",   4:"POTENSIAL 🔥", 3:"WATCH 👀"},
        "Momentum 🚀":  {5:"RIPPING 🚀",   4:"POTENSIAL 🔥", 3:"WATCH 👀"},
        "Reversal 🎯":  {5:"REVERSAL 🎯",  4:"POTENSIAL 🔥", 3:"WATCH 👀"},
        "Bagger 💎":    {5:"BAGGER 💎",    4:"KANDIDAT 🚀",  3:"WATCH 👀"},
    }.get(mode, {})
    for thresh in sorted(t.keys(), reverse=True):
        if score>=thresh: return t[thresh]
    return "WAIT"

def get_card_class(signal):
    if "BAGGER" in signal:                                 return "bagger"
    if "RIPPING" in signal or "REVERSAL" in signal:       return "gacor"
    if "KANDIDAT" in signal or "POTENSIAL" in signal:     return "potensial"
    if "WATCH" in signal:                                  return "watch"
    return ""

# ════════════════════════════════════════════════════
#  TELEGRAM
# ════════════════════════════════════════════════════
def send_telegram(results_top, source="Scanner"):
    if not TOKEN or not CHAT_ID: return
    now=datetime.now(eastern_tz); is_open=(9<=now.hour<16 and now.weekday()<5)
    sep="━"*28
    hdr=(f"{'🟢 MARKET OPEN' if is_open else '🌙 AFTER HOURS / PRE-MARKET'}\n"
         f"🦅 *US TURBO {'WATCHLIST' if source=='Watchlist' else 'ALERT'}*\n"
         f"⏰ `{now.strftime('%H:%M:%S')} ET` · `{now.strftime('%d %b %Y')}`\n{sep}\n")
    body=""
    for r in results_top[:5]:
        sig=r.get('Signal','-')
        em="💎" if "BAGGER" in sig else("🏆" if ("RIPPING" in sig or "REVERSAL" in sig) else("🔥" if "POTENSIAL" in sig else "👀"))
        te="📈" if "▲" in r.get('Trend','') else("📉" if "▼" in r.get('Trend','') else"➡️")
        bar="█"*int(r['Score'])+"░"*(6-int(r['Score']))
        body+=(f"\n{em} *{r['Ticker']}*  `{sig}`\n"
               f"   💰 Price: `${r['Price']:.2f}` {te}\n"
               f"   📊 Score: `[{bar}] {r['Score']}/6`\n"
               f"   📈 RSI-EMA: `{r.get('RSI-EMA',0)}` | STOCH: `{r.get('Stoch K',0)}`\n"
               f"   🌊 RVOL: `{r.get('RVOL',0)}x` | MACD: `{r.get('MACD Hist',0)}`\n"
               f"   🎯 TP: `${r['TP']:.2f}` | 🛑 SL: `${r['SL']:.2f}` | R:R `{r['R:R']}`\n"
               f"   💡 _{r.get('Reasons','')[:60]}_\n")
    footer=f"\n{sep}\n⚡ _US Turbo v1 · 15M Intraday_\n⚠️ _NOT financial advice. DYOR!_"
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id":CHAT_ID,"text":hdr+body+footer,"parse_mode":"Markdown"},
                      timeout=10)
    except: pass

# ════════════════════════════════════════════════════
#  DATA FETCH
# ════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def fetch_intraday(tickers, chunk=25):
    all_dfs={}
    for i in range(0, len(tickers), chunk):
        batch=tickers[i:i+chunk]
        try:
            raw=yf.download(batch, period="5d", interval="15m",
                            group_by='ticker', progress=False,
                            threads=True, auto_adjust=True)
            for t in batch:
                try:
                    df=raw[t].dropna() if len(batch)>1 else raw.dropna()
                    if isinstance(df.columns, pd.MultiIndex): df.columns=df.columns.droplevel(1)
                    if len(df)>=50: all_dfs[t]=df
                except: pass
        except: pass
        time.sleep(0.5)
    return all_dfs

# ════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════
regime, spx_price, ema20, ema55, regime_detail, spx_chg = get_market_regime()
vix_val, vix_chg = get_vix()
rcfg   = get_regime_config(regime, vix_val)
rcolor = rcfg["color"]
chg_col="#00ff88" if spx_chg>=0 else "#ff3d5a"; chg_sym="▲" if spx_chg>=0 else "▼"
vix_col="#ff3d5a" if vix_val>25 else("#ffb700" if vix_val>18 else "#00ff88")
now_et =datetime.now(eastern_tz)
is_market_open=(9<=now_et.hour<16 and now_et.weekday()<5) or \
               (now_et.hour==9 and now_et.minute>=30)

st.markdown(f"""
<div class="tt-header">
  <div>
    <div class="tt-logo">🦅 US TURBO</div>
    <div class="tt-sub">NYSE · NASDAQ · 15M Intraday · Bagger Detector · v1.0</div>
  </div>
  <div class="live-badge"><div class="live-dot"></div>{'MARKET OPEN' if is_market_open else 'CLOSED'} {now_et.strftime("%H:%M")} ET</div>
</div>""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background:rgba(0,0,0,.4);border:1px solid {rcolor}44;border-radius:8px;
     padding:12px 16px;margin-bottom:14px;border-left:4px solid {rcolor};">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
    <div>
      <div style="font-family:Space Mono,monospace;font-size:12px;font-weight:700;color:{rcolor};letter-spacing:1px;">{rcfg["label"]}</div>
      <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-top:3px;">{rcfg["desc"]}</div>
    </div>
    <div style="display:flex;gap:24px;align-items:center;">
      <div style="text-align:right;font-family:Space Mono,monospace;">
        <div style="font-size:18px;font-weight:700;color:{rcolor};">S&P {spx_price:,.0f} <span style="font-size:11px;color:{chg_col}">{chg_sym}{abs(spx_chg):.2f}%</span></div>
        <div style="font-size:9px;color:#4a5568;">EMA20 {ema20:,.0f} · EMA55 {ema55:,.0f}</div>
      </div>
      <div style="text-align:right;font-family:Space Mono,monospace;">
        <div style="font-size:18px;font-weight:700;color:{vix_col};">VIX {vix_val:.1f}</div>
        <div style="font-size:9px;color:#4a5568;">{'⚠️ FEAR' if vix_val>25 else ('🧊 LOW VOL' if vix_val<15 else '✅ NORMAL')}</div>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  PIVOT POINTS
# ════════════════════════════════════════════════════
def calc_pivot_points(high, low, close):
    pp=( high+low+close)/3
    r1=2*pp-low;  r2=pp+(high-low);  r3=high+2*(pp-low)
    s1=2*pp-high; s2=pp-(high-low);  s3=low-2*(high-pp)
    return {"PP":pp,"R1":r1,"R2":r2,"R3":r3,"S1":s1,"S2":s2,"S3":s3}

@st.cache_data(ttl=3600)
def fetch_pivot_data(ticker):
    try:
        df=yf.download(ticker, period="5d", interval="1d",
                       progress=False, auto_adjust=True, threads=False)
        if df is None or len(df)<2: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns=df.columns.droplevel(1)
        prev=df.iloc[-2]
        return calc_pivot_points(float(prev["High"]),float(prev["Low"]),float(prev["Close"]))
    except: return None

def get_pivot_position(price, pivots):
    if pivots is None: return "Unknown","#4a5568"
    pp=pivots["PP"]
    if price>pivots["R2"]:   return "Above R2 🔴","#ff3d5a"
    elif price>pivots["R1"]: return "R1→R2 🟠","#ff7b00"
    elif price>pp:           return "PP→R1 🟢","#00ff88"
    elif price>pivots["S1"]: return "S1→PP 🟡","#ffb700"
    elif price>pivots["S2"]: return "S2→S1 🔴","#ff3d5a"
    else:                    return "Below S2 🔴","#ff3d5a"

# ════════════════════════════════════════════════════
#  MULTI-TIMEFRAME
# ════════════════════════════════════════════════════
@st.cache_data(ttl=360)
def fetch_mtf_data(ticker):
    result={}
    for interval, period, key in [("15m","3d","M15"),("1h","10d","H1"),("1d","60d","D1")]:
        try:
            df=yf.download(ticker, period=period, interval=interval,
                           progress=False, auto_adjust=True, threads=False)
            if df is not None and not df.empty:
                if isinstance(df.columns, pd.MultiIndex): df.columns=df.columns.droplevel(1)
                df=df.dropna()
                if len(df)>=20: result[key]=df
        except: pass
    return result

def score_mtf(ticker, mode="Scalping ⚡"):
    mtf=fetch_mtf_data(ticker); scores={}
    for tf_key, df in mtf.items():
        try:
            df=apply_intraday_indicators(df.copy())
            if len(df)<3: continue
            r=df.iloc[-1]; p=df.iloc[-2]; p2=df.iloc[-3]
            if mode=="Scalping ⚡":   sc,_,_=score_scalping(r,p,p2)
            elif mode=="Momentum 🚀": sc,_,_=score_momentum(r,p,p2)
            elif mode=="Bagger 💎":   sc,_,_=score_bagger(r,p,p2,df)
            else:                     sc,_,_=score_reversal(r,p,p2)
            scores[tf_key]=round(sc,1)
        except: scores[tf_key]=0
    return scores

def mtf_alignment(scores):
    if not scores: return "No Data","#4a5568",0
    vals=list(scores.values()); avg=sum(vals)/len(vals)
    bullish_count=sum(1 for v in vals if v>=4)
    if bullish_count==len(vals):  return "FULL ALIGN 🔥","#00ff88",avg
    elif bullish_count>=2:        return "PARTIAL ⚡","#ffb700",avg
    elif bullish_count==1:        return "MIXED ⚠️","#ff7b00",avg
    else:                         return "NO ALIGN ❌","#ff3d5a",avg

# ════════════════════════════════════════════════════
#  US SECTORS (GICS)
# ════════════════════════════════════════════════════
SECTORS = {
    "Technology":            ["AAPL","MSFT","NVDA","AMD","INTC","QCOM","TXN","AVGO","CSCO","ANET",
                              "CRM","ORCL","NOW","ADBE","INTU","CDNS","SNPS","VEEV","WDAY","NET"],
    "Semiconductors":        ["NVDA","AMD","INTC","QCOM","TXN","AVGO","MU","AMAT","KLAC","LRCX",
                              "MRVL","SMCI","ARM","ONTO","ENTG","MPWR","ON","SWKS","WOLF","QRVO"],
    "AI & Growth":           ["NVDA","PLTR","SNOW","DDOG","CRWD","ZS","PANW","NET","MDB","IONQ",
                              "QUBT","RGTI","ARM","SMCI","META","MSFT","GOOGL","TSLA","AMZN","CRM"],
    "Financials":            ["JPM","BAC","WFC","GS","MS","C","BLK","SCHW","V","MA",
                              "PYPL","COIN","SPGI","MCO","ICE","CME","BX","KKR","PGR","ALL"],
    "Healthcare":            ["JNJ","UNH","PFE","MRK","ABBV","LLY","BMY","AMGN","GILD","REGN",
                              "MRNA","VRTX","ISRG","MDT","SYK","HCA","CVS","MCK","DXCM","PODD"],
    "Consumer Discretionary":["AMZN","TSLA","HD","LOW","TGT","COST","TJX","NKE","LULU","ROST",
                              "BKNG","ABNB","UBER","DHI","LEN","ORLY","AZO","DLTR","DG","RH"],
    "Consumer Staples":      ["WMT","PG","KO","PEP","MDLZ","MO","PM","CL","GIS","K",
                              "MKC","HRL","CAG","CHD","CLX","EL","KR","SYY","USFD","SFM"],
    "Energy":                ["XOM","CVX","COP","EOG","OXY","PSX","VLO","MPC","SLB","HAL",
                              "BKR","DVN","FANG","EQT","AR","KMI","WMB","ET","EPD","MPLX"],
    "Industrials":           ["BA","CAT","HON","GE","RTX","LMT","NOC","GD","ITW","EMR",
                              "FDX","UPS","FAST","URI","WAB","TDG","ROP","SAIA","ODFL","CARR"],
    "Materials":             ["LIN","APD","SHW","ECL","NEM","FCX","AA","NUE","STLD","VMC",
                              "MLM","DOW","DD","AMCR","BALL","CLF","X","RS","PKG","IP"],
    "Real Estate":           ["AMT","PLD","CCI","EQIX","DLR","PSA","SPG","O","VICI","EXR",
                              "WELL","VTR","BXP","KIM","REG","MAC","NNN","SLG","WP","DLR"],
    "Utilities":             ["NEE","DUK","SO","AEP","EXC","XEL","PPL","WEC","ES","EIX",
                              "ETR","FE","CNP","AES","CMS","NI","BKH","NWE","OGE","AVA"],
    "Communication":         ["GOOGL","META","NFLX","DIS","CMCSA","CHTR","VZ","T","TMUS","SPOT",
                              "SNAP","PINS","RDDT","WBD","OMC","IPG","LAMR","MTCH","IAC","FOXA"],
}
FED_SENSITIVE_SECTORS = ["Financials","Real Estate","Utilities"]

@st.cache_data(ttl=300)
def fetch_sector_rotation(sector_stocks):
    results=[]
    tickers=sector_stocks[:10]
    try:
        raw=yf.download(tickers, period="3d", interval="1d",
                        group_by="ticker", progress=False, threads=True, auto_adjust=True)
        for t in tickers:
            try:
                df=raw[t].dropna() if len(tickers)>1 else raw.copy()
                if isinstance(df.columns, pd.MultiIndex): df.columns=df.columns.droplevel(1)
                df=df.dropna()
                if len(df)<2: continue
                close=float(df["Close"].iloc[-1]); prev=float(df["Close"].iloc[-2])
                chg=(close-prev)/prev*100; vol=float(df["Volume"].iloc[-1])
                avg_v=float(df["Volume"].mean()); rvol=vol/avg_v if avg_v>0 else 1.0
                results.append({"ticker":t,"close":close,"chg":chg,"rvol":round(rvol,2)})
            except: pass
    except: pass
    return results

@st.cache_data(ttl=3600)
def calc_sector_beta(sector_name, sector_stocks, lookback=20):
    try:
        spx=yf.download("^GSPC", period="60d", interval="1d", progress=False, auto_adjust=True)
        if spx is None or len(spx)<lookback: return None
        if isinstance(spx.columns, pd.MultiIndex): spx.columns=spx.columns.droplevel(1)
        spx_ret=spx["Close"].pct_change().dropna()
        tickers=sector_stocks[:8]
        raw=yf.download(tickers, period="60d", interval="1d",
                        group_by="ticker", progress=False, threads=True, auto_adjust=True)
        sec_rets=[]
        for t in tickers:
            try:
                df=raw[t]["Close"].dropna() if len(tickers)>1 else raw["Close"].dropna()
                sec_rets.append(df.pct_change().dropna())
            except: pass
        if not sec_rets: return None
        sec_avg=pd.concat(sec_rets, axis=1).mean(axis=1)
        aligned=pd.concat([spx_ret, sec_avg], axis=1).dropna()
        aligned.columns=["SPX","Sector"]
        if len(aligned)<10: return None
        cov=aligned["Sector"].cov(aligned["SPX"]); var=aligned["SPX"].var()
        beta=round(cov/var,2) if var>0 else 1.0
        corr=round(aligned["Sector"].corr(aligned["SPX"]),2)
        rs5=round((aligned["Sector"].tail(5).sum()-aligned["SPX"].tail(5).sum())*100,2)
        ret_1m_sec=round(aligned["Sector"].tail(20).sum()*100,2)
        ret_1m_spx=round(aligned["SPX"].tail(20).sum()*100,2)
        down_days=aligned[aligned["SPX"]<-0.005]
        avg_down=round(down_days["Sector"].mean()*100,2) if len(down_days)>0 else 0.0
        return {"sector":sector_name,"beta":beta,"corr":corr,"rs5":rs5,
                "ret_1m_sec":ret_1m_sec,"ret_1m_spx":ret_1m_spx,"avg_down":avg_down,
                "defensive":beta<0.8 and corr<0.7}
    except: return None

def get_beta_label(beta):
    if beta<0.6:   return "🛡️ Very Defensive","#00ff88"
    elif beta<0.8: return "🟢 Defensive","#00ff88"
    elif beta<1.0: return "🟡 Moderate","#ffb700"
    elif beta<1.3: return "🟠 Aggressive","#ff7b00"
    else:          return "🔴 High Beta","#ff3d5a"

# ════════════════════════════════════════════════════
#  GAP UP SCANNER
# ════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def scan_gap_up(tickers, min_gap_pct=0.5):
    results=[]
    for i in range(0, len(tickers), 30):
        batch=tickers[i:i+30]
        try:
            raw=yf.download(batch, period="5d", interval="1d",
                            group_by="ticker", progress=False, threads=True, auto_adjust=True)
            for t in batch:
                try:
                    df=raw[t].dropna() if len(batch)>1 else raw.copy()
                    if isinstance(df.columns, pd.MultiIndex): df.columns=df.columns.droplevel(1)
                    df=df.dropna()
                    if len(df)<3: continue
                    today=df.iloc[-1]; prev=df.iloc[-2]
                    close=float(today["Close"]); hi_t=float(today["High"]); lo_t=float(today["Low"])
                    hi_p=float(prev["High"]); vol=float(today["Volume"]); avg_vol=float(df["Volume"].mean())
                    rvol=vol/avg_vol if avg_vol>0 else 1.0
                    gap_score=0; reasons=[]
                    if close>hi_p:
                        gp=(close-hi_p)/hi_p*100
                        gap_score+=3; reasons.append(f"Gap {gp:.1f}% above prev High ✦✦")
                    cr=(close-lo_t)/max(hi_t-lo_t,0.001)
                    if cr>0.85:   gap_score+=2; reasons.append(f"Closed HOD {cr:.0%}")
                    elif cr>0.70: gap_score+=1; reasons.append(f"Strong close {cr:.0%}")
                    if rvol>3.0:   gap_score+=2; reasons.append(f"RVOL={rvol:.1f}x SURGE 🔥")
                    elif rvol>2.0: gap_score+=1; reasons.append(f"RVOL={rvol:.1f}x")
                    elif rvol>1.5: gap_score+=0.5
                    if len(df)>=3:
                        roc3=(close-float(df.iloc[-3]["Close"]))/float(df.iloc[-3]["Close"])*100
                        if roc3>3:   gap_score+=1; reasons.append(f"3D ROC +{roc3:.1f}%")
                        elif roc3>1: gap_score+=0.5
                    if gap_score<3: continue
                    chg_today=(close-float(prev["Close"]))/float(prev["Close"])*100
                    results.append({"Ticker":t,"Price":round(close,2),"Gap Score":round(gap_score,1),
                                    "Chg %":round(chg_today,2),"Close Ratio":round(cr,2),
                                    "RVOL":round(rvol,2),"Prev High":round(hi_p,2),
                                    "Signal":"GAP UP 🚀" if gap_score>=4 else "POTENTIAL ⚡",
                                    "Reasons":" · ".join(reasons[:3])})
                except: pass
        except: pass
        time.sleep(0.3)
    return sorted(results, key=lambda x: x["Gap Score"], reverse=True)

# ════════════════════════════════════════════════════
#  TRAILING STOP ENGINE
# ════════════════════════════════════════════════════
def calc_trailing_stop(entry, current, atr, method="ATR", atr_mult=2.0, pct=3.0):
    if method=="ATR":      trail_dist=atr*atr_mult; stop_price=current-trail_dist
    elif method=="Persen": trail_dist=current*(pct/100); stop_price=current*(1-pct/100)
    else:                  trail_dist=atr*1.5; stop_price=current-trail_dist
    profit_locked=max(0,stop_price-entry)
    profit_pct=(current-entry)/entry*100
    locked_pct=(stop_price-entry)/entry*100 if stop_price>entry else 0
    return {"stop":round(stop_price,2),"distance":round(trail_dist,2),
            "profit_float":round(profit_pct,2),"profit_locked":round(locked_pct,2),
            "is_profitable":stop_price>entry}

# ════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════
tab_scanner, tab_watchlist, tab_overnight, tab_sector, tab_gapup, tab_trail, tab_backtest = st.tabs(
    ["🔥 Scanner","👁️ Watchlist","🌙 Overnight Play","🏭 Sectors","📈 Gap Up","🎯 Trailing Stop","📊 Backtest"]
)

# ════════════════════════════════════════════════════
#  TAB 1: SCANNER
# ════════════════════════════════════════════════════
with tab_scanner:
    with st.expander("⚙️  Scanner Settings", expanded=False):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown('<div class="settings-label">MODE SIGNAL</div>', unsafe_allow_html=True)
            auto_regime=st.toggle("🤖 Auto-Mode (Market Regime)", value=True, key="auto_reg")
            if auto_regime:
                scan_mode=rcfg["mode"]
                st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:10px;padding:6px 10px;background:rgba(0,0,0,.3);border-radius:4px;color:{rcolor};">Auto: {scan_mode}</div>', unsafe_allow_html=True)
            else:
                scan_mode=st.radio("Mode",["Scalping ⚡","Momentum 🚀","Reversal 🎯","Bagger 💎"],
                                   label_visibility="collapsed", key="scan_mode_radio")
            tele_on=st.toggle("📡 Telegram Alert", value=True, key="tele_on")
        with sc2:
            st.markdown('<div class="settings-label">FILTER</div>', unsafe_allow_html=True)
            auto_thresh=st.toggle("🤖 Auto-Threshold", value=True, key="auto_thr")
            if auto_thresh:
                min_score=rcfg["min_score"]; vol_thresh=rcfg["min_rvol"]
                st.caption(f"Auto: Score≥{min_score} · RVOL≥{vol_thresh}x")
            else:
                min_score=st.slider("Min Score (0-6)",0,6,4,key="msc")
                vol_thresh=st.slider("Min RVOL Spike",1.0,5.0,1.5,0.1,key="vol")
            min_turn=st.number_input("Min Turnover ($M)", value=5, step=1, key="trn")*1_000_000
        with sc3:
            st.markdown('<div class="settings-label">TAMPILAN</div>', unsafe_allow_html=True)
            view_mode=st.radio("View",["Card View 🃏","Table View 📊"],label_visibility="collapsed",key="view_mode")
            quick_mode=st.toggle("⚡ Quick (200 stocks)", value=False, key="quick_mode")
            st.caption(f"🎯 Regime: {regime} · VIX: {vix_val:.1f} · Mode: {scan_mode}")
            st.caption(f"📊 {len(raw_stocks)} stocks tersedia")

    do_scan=st.button("🔥 SCAN US STOCKS SEKARANG", type="primary", use_container_width=True, key="btn_scan")

    _now_check=datetime.now(eastern_tz).timestamp(); auto_triggered=False
    if st.session_state.last_scan_time and not do_scan:
        _elapsed=_now_check-st.session_state.last_scan_time
        if _elapsed>=300 and st.session_state.scan_results:
            do_scan=True; auto_triggered=True

    if do_scan:
        scan_list=stocks_yf[:200] if quick_mode else stocks_yf
        prog_ph=st.empty()
        with prog_ph.container():
            label="🔄 AUTO-REFRESH" if auto_triggered else "🔥 SCANNING"
            st.markdown(f'<div style="color:#00e5ff;font-family:Space Mono,monospace;font-size:12px;letter-spacing:1px;">{label} {len(scan_list)} US stocks ({scan_mode})...</div>', unsafe_allow_html=True)
            pb=st.progress(0)
        try:
            data_dict=fetch_intraday(tuple(scan_list))
            st.session_state.data_dict=data_dict
            results=[]; tickers=list(data_dict.keys())
            for i, ticker in enumerate(tickers):
                pb.progress((i+1)/max(len(tickers),1))
                try:
                    df=data_dict[ticker].copy()
                    if len(df)<55: continue
                    df=apply_intraday_indicators(df)
                    r=df.iloc[-1]; p=df.iloc[-2]; p2=df.iloc[-3] if len(df)>=3 else p
                    close=float(r['Close']); vol=float(r['Volume'])
                    turnover=close*vol; rvol=float(r['RVOL'])
                    if turnover<min_turn or rvol<vol_thresh: continue
                    if scan_mode=="Scalping ⚡":   sc,reasons,_=score_scalping(r,p,p2)
                    elif scan_mode=="Momentum 🚀": sc,reasons,_=score_momentum(r,p,p2)
                    elif scan_mode=="Bagger 💎":   sc,reasons,_=score_bagger(r,p,p2,df)
                    else:                          sc,reasons,_=score_reversal(r,p,p2)
                    if sc<min_score: continue
                    sig=get_signal(sc,scan_mode)
                    if sig=="WAIT": continue
                    atr=float(r['ATR']); slm=rcfg.get("sl_mult",0.8)
                    if scan_mode=="Scalping ⚡":   tp=close+1.5*atr; sl=close-slm*atr
                    elif scan_mode=="Momentum 🚀": tp=close+2.0*atr; sl=close-slm*atr
                    elif scan_mode=="Bagger 💎":   tp=close+3.0*atr; sl=close-1.0*atr
                    else:                          tp=close+2.5*atr; sl=close-slm*atr
                    rr=(tp-close)/max(close-sl,0.01)
                    e9=float(r['EMA9']); e21=float(r['EMA21']); e50=float(r['EMA50'])
                    trend="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else"◆ SIDE")
                    results.append({
                        "Ticker":stock_map[ticker],"Price":round(close,2),"Score":sc,"Signal":sig,"Trend":trend,
                        "RSI-EMA":round(float(r['RSI_EMA']),1),"Stoch K":round(float(r['STOCH_K']),1),
                        "Stoch D":round(float(r['STOCH_D']),1),"MACD Hist":round(float(r['MACD_Hist']),4),
                        "RVOL":round(rvol,2),"BB%":round(float(r['BB_pct']),2),
                        "ROC 3B%":round(float(r['ROC3'])*100,2),"VWAP":round(float(r['VWAP']),2),
                        "TP":round(tp,2),"SL":round(sl,2),"R:R":round(rr,1),
                        "Turnover($M)":round(turnover/1e6,1),"Reasons":" · ".join(reasons),
                        "_class":get_card_class(sig)
                    })
                except: continue
            prog_ph.empty()
            st.session_state.scan_results=results
            st.session_state.last_scan_time=datetime.now(eastern_tz).timestamp()
            st.session_state.last_scan_mode=scan_mode
            if tele_on and results:
                if 'tt_last_sent' not in st.session_state: st.session_state.tt_last_sent=set()
                df_tmp=pd.DataFrame(results).sort_values("Score",ascending=False)
                cur_set=set(df_tmp['Ticker'].tolist()); new_alr=cur_set-st.session_state.tt_last_sent
                if new_alr:
                    top_new=df_tmp[df_tmp['Ticker'].isin(new_alr)].head(5).to_dict('records')
                    if top_new: send_telegram(top_new)
                    st.session_state.tt_last_sent.update(new_alr)
                st.session_state.tt_last_sent=st.session_state.tt_last_sent&cur_set
        except Exception as e:
            prog_ph.empty(); st.error(f"Scan error: {str(e)[:100]}")

    if st.session_state.last_scan_time:
        _rem=max(0,300-(_now_check-st.session_state.last_scan_time))
        _last=datetime.fromtimestamp(st.session_state.last_scan_time, eastern_tz).strftime("%H:%M:%S")
        st.caption(f"⏱️ Next auto-scan: {int(_rem//60):02d}:{int(_rem%60):02d} · Last: {_last} ET")

    results=st.session_state.scan_results
    if not results and not do_scan:
        st.markdown(f"""
        <div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;">
          <div style="font-size:36px;margin-bottom:12px;">🦅</div>
          <div style="font-size:13px;letter-spacing:2px;">CLICK SCAN TO START</div>
          <div style="font-size:10px;margin-top:8px;color:#2d3748;">
            {"⚡ Quick: 200 stocks" if quick_mode else f"Full: {len(raw_stocks)} stocks"} · Regime: {regime} · VIX: {vix_val:.1f}
          </div>
        </div>""", unsafe_allow_html=True)
    elif results:
        df_out=pd.DataFrame(results).sort_values("Score",ascending=False).reset_index(drop=True)
        bagger =df_out[df_out["Signal"].str.contains("BAGGER|KANDIDAT",na=False)]
        gacor  =df_out[df_out["Signal"].str.contains("RIPPING|REVERSAL",na=False)]
        potensi=df_out[df_out["Signal"].str.contains("POTENSIAL",na=False)]
        avg_rsi=df_out['RSI-EMA'].mean()

        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-card" style="border-top-color:{rcolor}"><div class="metric-label">Regime</div>
            <div class="metric-value" style="font-size:14px;color:{rcolor}">{regime}</div>
            <div class="metric-sub">S&P {spx_price:,.0f} {chg_sym}{abs(spx_chg):.2f}%</div></div>
          <div class="metric-card" style="border-top-color:{vix_col}"><div class="metric-label">VIX</div>
            <div class="metric-value" style="color:{vix_col}">{vix_val:.1f}</div>
            <div class="metric-sub">{'FEAR' if vix_val>25 else 'NORMAL'}</div></div>
          <div class="metric-card green"><div class="metric-label">Signal Lolos</div>
            <div class="metric-value">{len(df_out)}</div><div class="metric-sub">dari {len(raw_stocks)} stocks</div></div>
          <div class="metric-card purple"><div class="metric-label">BAGGER 💎</div>
            <div class="metric-value">{len(bagger)}</div><div class="metric-sub">breakout kandidat</div></div>
          <div class="metric-card red"><div class="metric-label">RIPPING 🔥</div>
            <div class="metric-value">{len(gacor)}</div><div class="metric-sub">score ≥ 5</div></div>
          <div class="metric-card amber"><div class="metric-label">POTENSIAL</div>
            <div class="metric-value">{len(potensi)}</div></div>
          <div class="metric-card"><div class="metric-label">Avg RSI-EMA</div>
            <div class="metric-value" style="color:{'#00ff88' if avg_rsi>50 else '#ffb700' if avg_rsi>35 else '#ff3d5a'}">{avg_rsi:.1f}</div></div>
        </div>""", unsafe_allow_html=True)

        # Ticker tape
        th='<div class="tape-wrap"><div class="tape-inner">'
        for _,row in df_out.iterrows():
            roc=row['ROC 3B%']; is_bag="BAGGER" in row['Signal'] or "KANDIDAT" in row['Signal']
            cls='bagger' if is_bag else('up' if roc>0 else('down' if roc<0 else'flat'))
            sym='💎' if is_bag else('▲' if roc>0 else('▼' if roc<0 else'─'))
            th+=f'<span class="tape-item {cls}">{row["Ticker"]} ${row["Price"]:.2f} {sym}{abs(roc):.1f}% [{row["Signal"]}]</span>'
        th+=th.replace('tape-inner">',''); th+='</div></div>'
        st.markdown(th, unsafe_allow_html=True)

        if not bagger.empty:
            st.markdown(f'<div class="bagger-alert-box"><div class="bagger-title">💎 BAGGER ALERT · {len(bagger)} KANDIDAT · BREAKOUT + ACCUMULATION</div><div style="font-size:11px;color:#4a5568;margin-top:4px;">N-bar high breakout · Volume surge · EMA golden stack · BB squeeze expand</div></div>', unsafe_allow_html=True)
        if not gacor.empty:
            st.markdown(f'<div class="alert-box"><div class="alert-title">🚨 RIPPING ALERT · {len(gacor)} STOCKS · {scan_mode}</div><div style="font-size:11px;color:#4a5568;margin-top:4px;">Score ≥ 5 · Multi-indicator 15M · Optimal R:R</div></div>', unsafe_allow_html=True)

        if view_mode=="Card View 🃏":
            st.markdown('<div class="section-title">Signal Cards</div>', unsafe_allow_html=True)
            card_html='<div class="signal-grid">'
            for _,row in df_out.head(20).iterrows():
                sc_int=int(row['Score']); is_bag="BAGGER" in row['Signal'] or "KANDIDAT" in row['Signal']
                bar_cls="filled-purple" if is_bag else "filled"
                bars=''.join([f'<div class="sc-bar {bar_cls if i<sc_int else "empty"}" style="width:28px"></div>' for i in range(6)])
                roc_c='#00ff88' if row['ROC 3B%']>0 else'#ff3d5a'
                sig_color='#bf5fff' if is_bag else('#00ff88' if sc_int>=5 else'#ffb700' if sc_int>=4 else'#00e5ff')
                te="📈" if "▲" in row['Trend'] else("📉" if "▼" in row['Trend'] else"➡️")
                card_html+=f"""<div class="signal-card {row['_class']}">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div><div class="sc-ticker">{row['Ticker']}</div><div class="sc-price" style="color:{roc_c}">${row['Price']:.2f} {te}</div></div>
                    <div style="text-align:right;"><div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">SCORE</div>
                    <div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:{sig_color}">{row['Score']}</div></div>
                  </div>
                  <div class="sc-signal" style="color:{sig_color}">{row['Signal']}</div>
                  <div class="sc-bars">{bars}</div>
                  <div class="sc-stats">
                    <div class="sc-stat">RSI-EMA <span>{row['RSI-EMA']}</span></div>
                    <div class="sc-stat">STOCH <span>{row['Stoch K']:.0f}</span></div>
                    <div class="sc-stat">RVOL <span>{row['RVOL']}x</span></div>
                    <div class="sc-stat">ROC <span style="color:{roc_c}">{row['ROC 3B%']:+.1f}%</span></div>
                  </div>
                  <div class="sc-stats" style="margin-top:6px;">
                    <div class="sc-stat">TP <span style="color:#00ff88">${row['TP']:.2f}</span></div>
                    <div class="sc-stat">SL <span style="color:#ff3d5a">${row['SL']:.2f}</span></div>
                    <div class="sc-stat">R:R <span>{row['R:R']}</span></div>
                  </div>
                  <div style="margin-top:8px;font-size:10px;color:#4a5568;line-height:1.4;font-family:Space Mono,monospace;">{row['Reasons'][:80]}</div>
                </div>"""
            card_html+='</div>'
            st.markdown(card_html, unsafe_allow_html=True)

        st.markdown('<div class="section-title">Full Signal Table</div>', unsafe_allow_html=True)
        display_cols=["Ticker","Price","Score","Signal","Trend","RSI-EMA","Stoch K","Stoch D","MACD Hist","RVOL","BB%","ROC 3B%","VWAP","TP","SL","R:R","Turnover($M)","Reasons"]
        st.dataframe(df_out[display_cols], width='stretch', hide_index=True, column_config={
            "Score":       st.column_config.ProgressColumn("Score",min_value=0,max_value=6,format="%.1f"),
            "Price":       st.column_config.NumberColumn("Price",format="$%.2f"),
            "TP":          st.column_config.NumberColumn("TP",format="$%.2f"),
            "SL":          st.column_config.NumberColumn("SL",format="$%.2f"),
            "RVOL":        st.column_config.NumberColumn("RVOL",format="%.1fx"),
            "ROC 3B%":     st.column_config.NumberColumn("ROC 3B%",format="%.2f%%"),
            "Turnover($M)":st.column_config.NumberColumn("Turnover($M)",format="$%.0fM"),
        })

# ════════════════════════════════════════════════════
#  TAB 2: WATCHLIST
# ════════════════════════════════════════════════════
with tab_watchlist:
    st.markdown("""
    <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:12px;
         padding:10px 14px;background:#0d1117;border-radius:6px;border-left:3px solid #00e5ff;">
      Deep analysis for your watchlist. Input US tickers, separated by comma or newline.
    </div>""", unsafe_allow_html=True)

    wc1, wc2, wc3 = st.columns([3,1,1])
    with wc1:
        wl_input=st.text_area("Tickers", placeholder="Contoh:\nAAPL\nNVDA, TSLA, AMD\nMETA, GOOGL",
                              height=120, label_visibility="collapsed", key="wl_input")
    with wc2:
        wl_mode=st.radio("Mode",["Scalping ⚡","Momentum 🚀","Reversal 🎯","Bagger 💎"],key="wl_mode")
        st.caption(f"Regime suggest: {rcfg['mode']}")
    with wc3:
        st.markdown("<br>", unsafe_allow_html=True)
        wl_run=st.button("🔍 Analyze", use_container_width=True, key="wl_run")
        wl_tele=st.button("📡 Send Telegram", use_container_width=True, key="wl_tele")
        wl_share=st.button("📋 Copy Results", use_container_width=True, key="wl_share")

    if wl_run and wl_input.strip():
        raw_wl=list(dict.fromkeys([t.strip().upper() for line in wl_input.split("\n")
                                   for t in line.split(",") if t.strip()]))
        if raw_wl:
            with st.spinner(f"Analyzing {len(raw_wl)} stocks..."):
                wl_res=[]
                for t in raw_wl:
                    df=None
                    try:
                        raw=yf.download(t, period="5d", interval="15m",
                                        progress=False, auto_adjust=True, threads=False)
                        if not raw.empty:
                            if isinstance(raw.columns, pd.MultiIndex): raw.columns=raw.columns.droplevel(1)
                            df=raw.dropna()
                            if len(df)<10: df=None
                    except: pass
                    if df is None or len(df)<55:
                        wl_res.append({"Ticker":t,"Price":0,"Score":0,"Signal":"No data",
                            "RSI-EMA":0,"Stoch K":0,"RVOL":0,"BB%":0,"Trend":"-",
                            "TP":0,"SL":0,"R:R":0,"ROC 3B%":0,"VWAP":0,"ATR":0,
                            "Reasons":"No data","_class":"","MACD Hist":0}); continue
                    try:
                        df=apply_intraday_indicators(df)
                        r=df.iloc[-1]; p=df.iloc[-2]; p2=df.iloc[-3] if len(df)>=3 else p
                        close=float(r['Close']); atr=float(r['ATR']); slm=rcfg.get("sl_mult",0.8)
                        if wl_mode=="Scalping ⚡":   sc,reasons,_=score_scalping(r,p,p2);  tp=close+1.5*atr; sl=close-slm*atr
                        elif wl_mode=="Momentum 🚀": sc,reasons,_=score_momentum(r,p,p2);  tp=close+2.0*atr; sl=close-slm*atr
                        elif wl_mode=="Bagger 💎":   sc,reasons,_=score_bagger(r,p,p2,df); tp=close+3.0*atr; sl=close-1.0*atr
                        else:                        sc,reasons,_=score_reversal(r,p,p2);  tp=close+2.5*atr; sl=close-slm*atr
                        sig=get_signal(sc,wl_mode); rr=(tp-close)/max(close-sl,0.01)
                        e9=float(r['EMA9']); e21=float(r['EMA21']); e50=float(r['EMA50'])
                        trend="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else"◆ SIDE")
                        _pvt=fetch_pivot_data(t); _pvt_pos=get_pivot_position(close,_pvt)[0] if _pvt else "-"
                        _mtf=score_mtf(t, mode=wl_mode); _align,_acol,_avg=mtf_alignment(_mtf)
                        wl_res.append({"Ticker":t,"Price":round(close,2),"Score":sc,"Signal":sig,
                            "Trend":trend,"RSI-EMA":round(float(r['RSI_EMA']),1),
                            "Stoch K":round(float(r['STOCH_K']),1),"RVOL":round(float(r['RVOL']),2),
                            "BB%":round(float(r['BB_pct']),2),"ROC 3B%":round(float(r['ROC3'])*100,2),
                            "VWAP":round(float(r['VWAP']),2),"TP":round(tp,2),"SL":round(sl,2),"R:R":round(rr,1),
                            "ATR":round(atr,2),"MACD Hist":round(float(r['MACD_Hist']),4),
                            "Reasons":" · ".join(reasons),"_class":get_card_class(sig),
                            "Pivot Pos":_pvt_pos,
                            "PP":round(_pvt["PP"],2) if _pvt else 0,
                            "R1":round(_pvt["R1"],2) if _pvt else 0,
                            "S1":round(_pvt["S1"],2) if _pvt else 0,
                            "MTF Align":_align,
                            "M15":_mtf.get("M15",0),"H1":_mtf.get("H1",0),"D1":_mtf.get("D1",0)})
                    except Exception as ex:
                        wl_res.append({"Ticker":t,"Price":0,"Score":0,"Signal":f"Err:{str(ex)[:20]}",
                            "RSI-EMA":0,"Stoch K":0,"RVOL":0,"BB%":0,"Trend":"-",
                            "TP":0,"SL":0,"R:R":0,"ROC 3B%":0,"VWAP":0,"ATR":0,
                            "Reasons":"","_class":"","MACD Hist":0})

            st.session_state.wl_results=wl_res; st.session_state.wl_mode_used=wl_mode
            wl_top=[r for r in wl_res if r["Price"]>0 and
                    any(k in r.get("Signal","") for k in ["RIPPING","REVERSAL","POTENSIAL","BAGGER","KANDIDAT"])]
            if wl_top: send_telegram(wl_top[:5], source="Watchlist"); st.success(f"📡 Alert sent: {len(wl_top)} signals!")
            ok=[r for r in wl_res if r["Score"]>0]
            bag=[r for r in ok if any(k in r.get("Signal","") for k in ["BAGGER","KANDIDAT"])]
            gcr=[r for r in ok if any(k in r.get("Signal","") for k in ["RIPPING","REVERSAL"])]
            pot=[r for r in ok if "POTENSIAL" in r.get("Signal","")]
            st.markdown(f"""
            <div class="metric-row" style="margin-top:16px;">
              <div class="metric-card orange"><div class="metric-label">Watched</div><div class="metric-value">{len(raw_wl)}</div></div>
              <div class="metric-card purple"><div class="metric-label">BAGGER 💎</div><div class="metric-value">{len(bag)}</div></div>
              <div class="metric-card green"><div class="metric-label">RIPPING 🔥</div><div class="metric-value">{len(gcr)}</div></div>
              <div class="metric-card amber"><div class="metric-label">POTENSIAL</div><div class="metric-value">{len(pot)}</div></div>
              <div class="metric-card"><div class="metric-label">Data OK</div><div class="metric-value">{len(ok)}</div></div>
            </div>""", unsafe_allow_html=True)

            ch='<div class="signal-grid">'
            for row in sorted(wl_res, key=lambda x: x["Score"], reverse=True):
                if row["Price"]==0:
                    ch+=f'<div class="signal-card"><div class="sc-ticker">{row["Ticker"]}</div><div style="font-size:11px;color:#4a5568;margin-top:6px;">{row.get("Signal","No data")}</div></div>'
                    continue
                sc_int=int(row["Score"]); bars=''.join([f'<div class="sc-bar {"filled" if i<sc_int else "empty"}" style="width:26px"></div>' for i in range(6)])
                sig=row.get("Signal","-"); is_bag="BAGGER" in sig or "KANDIDAT" in sig
                sc_col="#bf5fff" if is_bag else("#00ff88" if("RIPPING" in sig or "REVERSAL" in sig) else("#ffb700" if "POTENSIAL" in sig else "#00e5ff" if "WATCH" in sig else "#4a5568"))
                rsi_v=row["RSI-EMA"]; rsi_c="#ff3d5a" if rsi_v<30 else("#ffb700" if rsi_v<45 else "#00ff88" if rsi_v>60 else "#c9d1d9")
                roc_c="#00ff88" if row.get("ROC 3B%",0)>0 else "#ff3d5a"
                te="📈" if "▲" in row["Trend"] else("📉" if "▼" in row["Trend"] else "➡️")
                ch+=f"""<div class="signal-card {row['_class']}">
                  <div style="display:flex;justify-content:space-between;">
                    <div><div class="sc-ticker">{row['Ticker']}</div>
                    <div class="sc-price" style="color:{roc_c}">${row['Price']:.2f} {te}</div></div>
                    <div style="text-align:right">
                      <div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568">SCORE</div>
                      <div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:{sc_col}">{row['Score']}</div>
                    </div>
                  </div>
                  <div class="sc-signal" style="color:{sc_col}">{sig}</div>
                  <div class="sc-bars">{bars}</div>
                  <div class="sc-stats">
                    <div class="sc-stat">RSI-EMA <span style="color:{rsi_c}">{rsi_v}</span></div>
                    <div class="sc-stat">STOCH <span>{row['Stoch K']:.0f}</span></div>
                    <div class="sc-stat">RVOL <span>{row['RVOL']}x</span></div>
                  </div>
                  <div class="sc-stats" style="margin-top:6px">
                    <div class="sc-stat">TP <span style="color:#00ff88">${row['TP']:.2f}</span></div>
                    <div class="sc-stat">SL <span style="color:#ff3d5a">${row['SL']:.2f}</span></div>
                    <div class="sc-stat">R:R <span>{row['R:R']}</span></div>
                  </div>
                  <div style="margin-top:8px;font-size:10px;color:#4a5568;line-height:1.5;font-family:Space Mono,monospace">{row['Reasons'][:80]}</div>
                  <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;">
                    <div style="font-family:Space Mono,monospace;font-size:9px;padding:2px 7px;border-radius:10px;background:rgba(0,0,0,.3);color:#4a5568;">📍 {row.get('Pivot Pos','-')}</div>
                    <div style="font-family:Space Mono,monospace;font-size:9px;padding:2px 7px;border-radius:10px;background:rgba(0,0,0,.3);color:#4a5568;">MTF: {row.get('MTF Align','-')}</div>
                  </div>
                  <div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568;margin-top:4px;">
                    M15:{row.get('M15',0)} · H1:{row.get('H1',0)} · D1:{row.get('D1',0)} &nbsp;|&nbsp; PP:${row.get('PP',0):.2f} · R1:${row.get('R1',0):.2f} · S1:${row.get('S1',0):.2f}
                  </div>
                </div>"""
            ch+='</div>'
            st.markdown(ch, unsafe_allow_html=True)

            df_wl=pd.DataFrame([r for r in wl_res if r["Price"]>0])
            if not df_wl.empty:
                show=["Ticker","Price","Score","Signal","Trend","RSI-EMA","Stoch K","RVOL","BB%","ROC 3B%","VWAP","TP","SL","R:R","MTF Align","M15","H1","D1","Pivot Pos","PP","R1","S1","ATR","Reasons"]
                show=[c for c in show if c in df_wl.columns]
                st.dataframe(df_wl[show], width='stretch', hide_index=True, column_config={
                    "Score":   st.column_config.ProgressColumn("Score",min_value=0,max_value=6,format="%.1f"),
                    "Price":   st.column_config.NumberColumn("Price",format="$%.2f"),
                    "TP":      st.column_config.NumberColumn("TP",format="$%.2f"),
                    "SL":      st.column_config.NumberColumn("SL",format="$%.2f"),
                    "RVOL":    st.column_config.NumberColumn("RVOL",format="%.2fx"),
                    "ROC 3B%": st.column_config.NumberColumn("ROC 3B%",format="%.2f%%"),
                })

    if wl_tele and st.session_state.wl_results:
        to_send=[r for r in st.session_state.wl_results if r["Price"]>0]
        if to_send: send_telegram(to_send[:5], source="Watchlist"); st.success(f"📡 Sent!")

    if wl_share and st.session_state.wl_results:
        now_str=datetime.now(eastern_tz).strftime("%d %b %Y %H:%M")
        txt=f"🦅 US TURBO WATCHLIST\n⏰ {now_str} ET\n📊 Mode: {st.session_state.get('wl_mode_used','')} | Regime: {regime} | VIX: {vix_val:.1f}\n"+"─"*28+"\n"
        for r in sorted(st.session_state.wl_results, key=lambda x: x["Score"], reverse=True):
            if r["Price"]==0: continue
            sig=r.get("Signal","-")
            em="💎" if("BAGGER" in sig or "KANDIDAT" in sig) else("🔥" if("RIPPING" in sig or "REVERSAL" in sig) else("⚡" if "POTENSIAL" in sig else "👀"))
            txt+=f"{em} {r['Ticker']} | ${r['Price']:.2f} | Score:{r['Score']} | RSI:{r['RSI-EMA']} | {sig}\n"
            if r.get("Reasons"): txt+=f"   → {r['Reasons'][:60]}\n"
        txt+="─"*28+"\nby US Turbo v1 🦅 · NOT financial advice"
        st.text_area("Copy for group:", txt, height=280, key="share_out")

    if not st.session_state.wl_results and not wl_run:
        st.markdown("""
        <div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;">
          <div style="font-size:32px;margin-bottom:12px;">👁️</div>
          <div style="font-size:12px;letter-spacing:2px;">INPUT TICKERS ABOVE</div>
          <div style="font-size:10px;margin-top:8px;color:#2d3748;">Example: NVDA, TSLA, AAPL, META</div>
        </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  TAB 3: OVERNIGHT PLAY (US Power Hour → Next Open)
# ════════════════════════════════════════════════════
with tab_overnight:
    now_et2=datetime.now(eastern_tz)
    is_entry_time=(now_et2.hour==15 and now_et2.minute>=0) or \
                  (now_et2.hour==15 and now_et2.minute<=45)
    is_exit_time =(now_et2.hour==9  and now_et2.minute>=30) or \
                  (now_et2.hour==10 and now_et2.minute<=30)

    st.markdown(f"""
    <div style="background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.3);
         border-radius:8px;padding:14px 18px;margin-bottom:16px;">
      <div style="font-family:Space Mono,monospace;font-size:13px;font-weight:700;
                  color:#00e5ff;letter-spacing:1px;">🌙 US OVERNIGHT PLAY — Power Hour → Next Open</div>
      <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-top:4px;">
        Entry: <span style="color:#ffb700">3:00 – 4:00 PM ET (Power Hour)</span> &nbsp;·&nbsp;
        Exit: <span style="color:#00ff88">Next Day 9:30 – 10:30 AM ET (Open)</span> &nbsp;·&nbsp;
        Strategy: <span style="color:#c9d1d9">Institutional EOD buying → Gap up next open</span><br>
        Status: <span style="color:{'#00ff88' if is_entry_time else '#ffb700' if is_exit_time else '#4a5568'}">
          {'🟢 WAKTU ENTRY! Scan sekarang!' if is_entry_time else '🟡 EXIT TIME! Check posisi!' if is_exit_time else '⏳ Wait until 3:00 PM ET'}
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    on_c1, on_c2 = st.columns([2,1])
    with on_c1:
        on_min_score=st.slider("Min Overnight Score", 0, 6, 4, key="on_score")
        on_min_rvol =st.slider("Min RVOL", 1.0, 5.0, 1.5, 0.1, key="on_rvol")
    with on_c2:
        on_min_turn=st.number_input("Min Turnover ($M)", value=5, step=1, key="on_turn")*1_000_000
        on_tele=st.toggle("📡 Telegram Alert", value=True, key="on_tele")

    do_overnight=st.button("🌙 SCAN OVERNIGHT PLAY", type="primary", use_container_width=True, key="btn_overnight")
    if "overnight_results" not in st.session_state: st.session_state.overnight_results=[]

    if do_overnight:
        on_prog=st.empty(); on_prog.info("🌙 Scanning overnight candidates...")
        on_res=[]; scan_data=st.session_state.get("data_dict",{})
        if not scan_data:
            try: scan_data=fetch_intraday(tuple(stocks_yf[:200]))
            except: pass

        pb_on=st.progress(0); tickers_on=list(scan_data.keys())
        for i, ticker in enumerate(tickers_on):
            pb_on.progress((i+1)/max(len(tickers_on),1))
            try:
                df=scan_data[ticker].copy()
                if len(df)<55: continue
                df_c=apply_intraday_indicators(df)
                r=df_c.iloc[-1]; p=df_c.iloc[-2]; p2=df_c.iloc[-3] if len(df_c)>=3 else p
                close=float(r['Close']); vol=float(r['Volume'])
                turnover=close*vol; rvol=float(r['RVOL'])
                if turnover<on_min_turn or rvol<on_min_rvol: continue
                sc,reasons,_=score_overnight(r,p,p2)
                if sc<on_min_score: continue
                if sc>=5:   on_sig="STRONG BUY 🌙"
                elif sc>=4: on_sig="BUY ⚡"
                else:       on_sig="WATCH 👀"
                atr=float(r['ATR']); tp=close+2.0*atr; sl=close-1.0*atr
                rr=(tp-close)/max(close-sl,0.01)
                pvt=fetch_pivot_data(ticker); pvt_pos=get_pivot_position(close,pvt)[0] if pvt else "-"
                e9=float(r['EMA9']); e21=float(r['EMA21']); e50=float(r['EMA50'])
                trend="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else"◆ SIDE")
                on_res.append({
                    "Ticker":stock_map.get(ticker,ticker),"Price":round(close,2),
                    "Score":sc,"Signal":on_sig,"Trend":trend,
                    "RSI-EMA":round(float(r['RSI_EMA']),1),"Stoch K":round(float(r['STOCH_K']),1),
                    "RVOL":round(rvol,2),"TP":round(tp,2),"SL":round(sl,2),"R:R":round(rr,1),
                    "Turnover($M)":round(turnover/1e6,1),"Pivot Pos":pvt_pos,
                    "PP":round(pvt["PP"],2) if pvt else 0,
                    "R1":round(pvt["R1"],2) if pvt else 0,
                    "S1":round(pvt["S1"],2) if pvt else 0,
                    "Reasons":" · ".join(reasons),
                    "_class":"gacor" if sc>=5 else "potensial" if sc>=4 else "watch"
                })
            except: continue

        pb_on.empty(); on_prog.empty()
        on_res=sorted(on_res, key=lambda x: x["Score"], reverse=True)
        st.session_state.overnight_results=on_res

        if on_tele and on_res:
            now_on=datetime.now(eastern_tz); sep="━"*28
            msg=(f"🌙 *OVERNIGHT PLAY — US Power Hour*\n"
                 f"⏰ `{now_on.strftime('%H:%M:%S')} ET` · `{now_on.strftime('%d %b %Y')}`\n{sep}\n")
            for r in on_res[:5]:
                bar="█"*int(r['Score'])+"░"*(6-int(r['Score']))
                msg+=(f"\n🌙 *{r['Ticker']}* `{r['Signal']}`\n"
                      f"   💰 Price: `${r['Price']:.2f}`\n"
                      f"   📊 Score: `[{bar}] {r['Score']}/6`\n"
                      f"   📈 RSI-EMA: `{r['RSI-EMA']}` | RVOL: `{r['RVOL']}x`\n"
                      f"   🎯 TP: `${r['TP']:.2f}` | 🛑 SL: `${r['SL']:.2f}` | R:R `{r['R:R']}`\n"
                      f"   💡 _{r['Reasons'][:50]}_\n")
            msg+=f"\n{sep}\n🌙 _Entry 3PM ET · Exit besok 9:30AM ET_\n⚠️ _NOT financial advice!_"
            try:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                              data={"chat_id":CHAT_ID,"text":msg,"parse_mode":"Markdown"}, timeout=10)
            except: pass

    overnight_results=st.session_state.overnight_results
    if overnight_results:
        strong=[r for r in overnight_results if "STRONG" in r.get("Signal","")]
        buy=[r for r in overnight_results if r.get("Signal","")=="BUY ⚡"]
        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-card" style="border-top-color:#00e5ff"><div class="metric-label">Candidates</div>
            <div class="metric-value">{len(overnight_results)}</div></div>
          <div class="metric-card green"><div class="metric-label">Strong Buy 🌙</div>
            <div class="metric-value">{len(strong)}</div></div>
          <div class="metric-card amber"><div class="metric-label">Buy ⚡</div>
            <div class="metric-value">{len(buy)}</div></div>
          <div class="metric-card"><div class="metric-label">Entry</div>
            <div class="metric-value" style="font-size:13px;color:#ffb700">3 PM ET</div></div>
          <div class="metric-card"><div class="metric-label">Exit</div>
            <div class="metric-value" style="font-size:13px;color:#00ff88">9:30 AM ET</div></div>
        </div>""", unsafe_allow_html=True)

        if len(overnight_results)>=1:
            medals=["🥇","🥈","🥉"]
            cols_top=st.columns(min(3, len(overnight_results)))
            for idx,col in enumerate(cols_top):
                if idx>=len(overnight_results): break
                row=overnight_results[idx]
                sig_col="#00ff88" if "STRONG" in row["Signal"] else "#ffb700"
                with col:
                    st.markdown(f"""
                    <div style="background:#0d1117;border:1px solid {sig_col}44;border-radius:10px;
                         padding:16px;text-align:center;border-top:3px solid {sig_col};">
                      <div style="font-size:24px">{medals[idx]}</div>
                      <div style="font-family:Space Mono,monospace;font-size:18px;font-weight:700;color:#e6edf3;">{row['Ticker']}</div>
                      <div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:{sig_col};">${row['Price']:.2f}</div>
                      <div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:{sig_col};">{row['Score']}/6</div>
                      <div style="font-size:11px;font-weight:700;color:{sig_col};">{row['Signal']}</div>
                      <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-top:6px;">
                        RVOL {row['RVOL']}x · RSI {row['RSI-EMA']}<br>TP ${row['TP']:.2f} · SL ${row['SL']:.2f}
                      </div>
                    </div>""", unsafe_allow_html=True)

        df_on=pd.DataFrame(overnight_results)
        show_cols=["Ticker","Price","Score","Signal","Trend","RSI-EMA","Stoch K","RVOL","TP","SL","R:R","Pivot Pos","PP","R1","S1","Turnover($M)","Reasons"]
        show_cols=[c for c in show_cols if c in df_on.columns]
        st.dataframe(df_on[show_cols], width='stretch', hide_index=True, column_config={
            "Score":st.column_config.ProgressColumn("Score",min_value=0,max_value=6,format="%.1f"),
            "Price":st.column_config.NumberColumn("Price",format="$%.2f"),
            "TP":   st.column_config.NumberColumn("TP",format="$%.2f"),
            "SL":   st.column_config.NumberColumn("SL",format="$%.2f"),
            "RVOL": st.column_config.NumberColumn("RVOL",format="%.2fx"),
        })
    elif not do_overnight:
        st.markdown("""
        <div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;">
          <div style="font-size:32px;margin-bottom:12px;">🌙</div>
          <div style="font-size:12px;letter-spacing:2px;">CLICK SCAN OVERNIGHT PLAY</div>
          <div style="font-size:10px;margin-top:8px;color:#2d3748;">Best time: 3:00 – 4:00 PM ET</div>
        </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  TAB 4: SECTOR ROTATION
# ════════════════════════════════════════════════════
with tab_sector:
    st.markdown("""
    <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:14px;
         padding:10px 14px;background:#0d1117;border-radius:6px;border-left:3px solid #ff7b00;">
      Track US sector momentum hari ini. Hijau = rotation in, merah = rotation out.
      <br>🏛️ <b style="color:#00e5ff">Fed Sensitive:</b> Financials, Real Estate, Utilities
    </div>""", unsafe_allow_html=True)

    do_sector=st.button("🏭 REFRESH SECTORS", type="primary", use_container_width=True, key="btn_sector")
    if "sector_data" not in st.session_state: st.session_state.sector_data={}

    if do_sector:
        with st.spinner("Fetching sector data..."):
            sec_data={}
            for sec_name, sec_stocks in SECTORS.items():
                results=fetch_sector_rotation(sec_stocks)
                if results:
                    avg_chg=sum(r["chg"] for r in results)/len(results)
                    avg_rvol=sum(r["rvol"] for r in results)/len(results)
                    bullish=sum(1 for r in results if r["chg"]>0)
                    sec_data[sec_name]={"avg_chg":round(avg_chg,2),"avg_rvol":round(avg_rvol,2),
                                        "bullish":bullish,"total":len(results),
                                        "stocks":results,"is_fed":sec_name in FED_SENSITIVE_SECTORS}
            st.session_state.sector_data=sec_data

    if st.session_state.sector_data:
        sorted_secs=sorted(st.session_state.sector_data.items(), key=lambda x: x[1]["avg_chg"], reverse=True)
        st.markdown('<div class="section-title">Sector Heatmap Today</div>', unsafe_allow_html=True)
        cols_sec=st.columns(3)
        for idx,(sec_name,sec_info) in enumerate(sorted_secs):
            chg=sec_info["avg_chg"]
            col="#00ff88" if chg>1 else("#ffb700" if chg>0 else "#ff3d5a")
            bg="rgba(0,255,136,.06)" if chg>1 else("rgba(255,183,0,.06)" if chg>0 else "rgba(255,61,90,.06)")
            fed_badge=' <span style="color:#00e5ff;font-size:9px">🏛️ FED</span>' if sec_info["is_fed"] else ""
            bull_pct=int(sec_info["bullish"]/max(sec_info["total"],1)*100)
            with cols_sec[idx%3]:
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {col}44;border-radius:8px;padding:12px;margin-bottom:10px;">
                  <div style="font-family:Space Mono,monospace;font-size:10px;font-weight:700;color:#c9d1d9;">{sec_name}{fed_badge}</div>
                  <div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:{col};margin:4px 0;">{chg:+.2f}%</div>
                  <div style="font-size:9px;color:#4a5568;">RVOL avg: {sec_info['avg_rvol']:.1f}x · Bullish: {sec_info['bullish']}/{sec_info['total']} ({bull_pct}%)</div>
                  <div style="height:4px;background:#1c2533;border-radius:2px;margin-top:6px;overflow:hidden;">
                    <div style="width:{bull_pct}%;height:100%;background:{col};border-radius:2px;"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Top Stocks in Strongest Sectors</div>', unsafe_allow_html=True)
        top3=sorted_secs[:3]; cols_top=st.columns(3)
        for cidx,(sec_name,sec_info) in enumerate(top3):
            with cols_top[cidx]:
                chg=sec_info["avg_chg"]; col="#00ff88" if chg>0 else "#ff3d5a"
                st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:11px;color:{col};font-weight:700;margin-bottom:8px;">{sec_name}</div>', unsafe_allow_html=True)
                for stk in sorted(sec_info["stocks"], key=lambda x: x["chg"], reverse=True)[:5]:
                    sc="#00ff88" if stk["chg"]>0 else "#ff3d5a"
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:5px 0;
                         border-bottom:1px solid #1c2533;font-family:Space Mono,monospace;font-size:10px;">
                      <span style="color:#c9d1d9;">{stk['ticker']}</span>
                      <span style="color:{sc}">{stk['chg']:+.1f}%</span>
                      <span style="color:#4a5568;">RVOL {stk['rvol']}x</span>
                    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:24px;">Beta & Relative Strength vs S&P 500</div>', unsafe_allow_html=True)
    do_beta=st.button("🔬 Calculate Beta All Sectors", use_container_width=True, key="btn_beta")
    if "beta_data" not in st.session_state: st.session_state.beta_data=[]

    if do_beta:
        beta_res=[]; bp=st.progress(0); secs=list(SECTORS.items())
        for i,(sec_name,sec_stocks) in enumerate(secs):
            bp.progress((i+1)/len(secs))
            res=calc_sector_beta(sec_name, sec_stocks)
            if res: beta_res.append(res)
        bp.empty(); beta_res=sorted(beta_res, key=lambda x: x["beta"])
        st.session_state.beta_data=beta_res

    if st.session_state.beta_data:
        for b in st.session_state.beta_data:
            beta_lbl,beta_col=get_beta_label(b["beta"])
            rs_col="#00ff88" if b["rs5"]>0 else "#ff3d5a"
            down_col="#00ff88" if b["avg_down"]>0 else "#ff3d5a"
            fed=" 🏛️" if b["sector"] in FED_SENSITIVE_SECTORS else ""
            width=min(100,int(abs(b["beta"])*50))
            st.markdown(f"""
            <div style="background:#0d1117;border:1px solid #1c2533;border-radius:8px;
                 padding:12px 16px;margin-bottom:8px;border-left:4px solid {beta_col};">
              <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div style="flex:2;">
                  <div style="font-family:Space Mono,monospace;font-size:11px;font-weight:700;color:#c9d1d9;">{b['sector']}{fed}</div>
                  <div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568;margin-top:2px;">Correlation: {b['corr']} · 1M Return: {b['ret_1m_sec']:+.1f}%</div>
                </div>
                <div style="text-align:center;min-width:80px;">
                  <div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:{beta_col};">{b['beta']}</div>
                  <div style="font-size:9px;color:{beta_col};">{beta_lbl}</div>
                </div>
                <div style="text-align:center;min-width:80px;">
                  <div style="font-family:Space Mono,monospace;font-size:14px;font-weight:700;color:{rs_col};">{b['rs5']:+.1f}%</div>
                  <div style="font-size:9px;color:#4a5568;">RS 5 Days</div>
                </div>
                <div style="text-align:center;min-width:80px;">
                  <div style="font-family:Space Mono,monospace;font-size:14px;font-weight:700;color:{down_col};">{b['avg_down']:+.2f}%</div>
                  <div style="font-size:9px;color:#4a5568;">Avg SPX↓ day</div>
                </div>
              </div>
              <div style="height:4px;background:#1c2533;border-radius:2px;margin-top:10px;overflow:hidden;">
                <div style="width:{width}%;height:100%;background:{beta_col};border-radius:2px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    if not st.session_state.sector_data:
        st.markdown("""
        <div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;">
          <div style="font-size:32px;margin-bottom:12px;">🏭</div>
          <div style="font-size:12px;letter-spacing:2px;">CLICK REFRESH SECTORS</div>
        </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  TAB 5: GAP UP SCANNER
# ════════════════════════════════════════════════════
with tab_gapup:
    st.markdown("""
    <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:14px;
         padding:10px 14px;background:#0d1117;border-radius:6px;border-left:3px solid #00ff88;">
      Deteksi US stocks yang berpotensi <b style="color:#00ff88">Gap Up di open</b> (9:30 AM ET).
      Strong close + high RVOL + above prev high = Gap Up candidate.
    </div>""", unsafe_allow_html=True)

    gu_c1, gu_c2 = st.columns(2)
    with gu_c1: gu_min_score=st.slider("Min Gap Score",1,6,3,key="gu_score")
    with gu_c2: gu_quick=st.toggle("⚡ Quick Scan (200)", value=True, key="gu_quick")

    do_gapup=st.button("📈 SCAN GAP UP", type="primary", use_container_width=True, key="btn_gapup")
    if "gapup_results" not in st.session_state: st.session_state.gapup_results=[]

    if do_gapup:
        scan_tickers=stocks_yf[:200] if gu_quick else stocks_yf
        with st.spinner(f"Scanning {len(scan_tickers)} stocks for Gap Up..."):
            gu_res=scan_gap_up(scan_tickers)
            gu_res=[r for r in gu_res if r["Gap Score"]>=gu_min_score]
            st.session_state.gapup_results=gu_res
        if gu_res and TOKEN and CHAT_ID:
            now_g=datetime.now(eastern_tz); sep="━"*28
            msg=f"📈 *US GAP UP SCANNER*\n⏰ `{now_g.strftime('%H:%M:%S')} ET`\n{sep}\n"
            for r in gu_res[:5]:
                msg+=(f"\n🚀 *{r['Ticker']}* `{r['Signal']}`\n"
                      f"   💰 Price: `${r['Price']:.2f}` ({r['Chg %']:+.1f}%)\n"
                      f"   📊 Gap Score: `{r['Gap Score']}/6`\n"
                      f"   🌊 RVOL: `{r['RVOL']}x`\n"
                      f"   💡 _{r['Reasons'][:50]}_\n")
            msg+=f"\n{sep}\n⚠️ _NOT financial advice!_"
            try:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                              data={"chat_id":CHAT_ID,"text":msg,"parse_mode":"Markdown"}, timeout=10)
                st.success("📡 Gap Up alert sent!")
            except: pass

    gapup_res=st.session_state.gapup_results
    if gapup_res:
        gap_confirmed=[r for r in gapup_res if "GAP UP" in r.get("Signal","")]
        potential=[r for r in gapup_res if "POTENTIAL" in r.get("Signal","")]
        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-card green"><div class="metric-label">Gap Confirmed 🚀</div><div class="metric-value">{len(gap_confirmed)}</div></div>
          <div class="metric-card amber"><div class="metric-label">Potential ⚡</div><div class="metric-value">{len(potential)}</div></div>
          <div class="metric-card"><div class="metric-label">Total</div><div class="metric-value">{len(gapup_res)}</div></div>
        </div>""", unsafe_allow_html=True)
        gu_html='<div class="signal-grid">'
        for row in gapup_res[:20]:
            sc_int=int(min(row["Gap Score"],6))
            bars=''.join([f'<div class="sc-bar {"filled" if i<sc_int else "empty"}" style="width:26px"></div>' for i in range(6)])
            is_gap="GAP UP" in row.get("Signal","")
            sc_col="#00ff88" if is_gap else "#ffb700"
            chg_c="#00ff88" if row["Chg %"]>0 else "#ff3d5a"
            gu_html+=f"""<div class="signal-card {'gacor' if is_gap else 'potensial'}">
              <div style="display:flex;justify-content:space-between;">
                <div><div class="sc-ticker">{row['Ticker']}</div>
                <div class="sc-price" style="color:{chg_c}">${row['Price']:.2f} ({row['Chg %']:+.1f}%)</div></div>
                <div style="text-align:right">
                  <div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568">GAP SCORE</div>
                  <div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:{sc_col}">{row['Gap Score']}</div>
                </div>
              </div>
              <div class="sc-signal" style="color:{sc_col}">{row['Signal']}</div>
              <div class="sc-bars">{bars}</div>
              <div class="sc-stats">
                <div class="sc-stat">RVOL <span>{row['RVOL']}x</span></div>
                <div class="sc-stat">Close% <span>{row['Close Ratio']:.0%}</span></div>
                <div class="sc-stat">PrevHigh <span>${row['Prev High']:.2f}</span></div>
              </div>
              <div style="margin-top:8px;font-size:10px;color:#4a5568;font-family:Space Mono,monospace;">{row['Reasons'][:80]}</div>
            </div>"""
        gu_html+='</div>'
        st.markdown(gu_html, unsafe_allow_html=True)
        df_gu=pd.DataFrame(gapup_res)
        st.dataframe(df_gu, width='stretch', hide_index=True, column_config={
            "Gap Score": st.column_config.ProgressColumn("Gap Score",min_value=0,max_value=6,format="%.1f"),
            "Price":     st.column_config.NumberColumn("Price",format="$%.2f"),
            "Prev High": st.column_config.NumberColumn("Prev High",format="$%.2f"),
            "RVOL":      st.column_config.NumberColumn("RVOL",format="%.2fx"),
            "Chg %":     st.column_config.NumberColumn("Chg %",format="%.2f%%"),
        })
    elif not do_gapup:
        st.markdown("""
        <div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;">
          <div style="font-size:32px;margin-bottom:12px;">📈</div>
          <div style="font-size:12px;letter-spacing:2px;">CLICK SCAN GAP UP</div>
        </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  TAB 6: TRAILING STOP ENGINE
# ════════════════════════════════════════════════════
with tab_trail:
    st.markdown("""
    <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:14px;
         padding:10px 14px;background:#0d1117;border-radius:6px;border-left:3px solid #bf5fff;">
      Lock profit di US market. ATR 2x = scalping · ATR 3x = swing · Persen = fixed trail.
    </div>""", unsafe_allow_html=True)

    tr_c1, tr_c2 = st.columns(2)
    with tr_c1:
        st.markdown('<div class="settings-label">YOUR POSITION</div>', unsafe_allow_html=True)
        tr_ticker=st.text_input("Ticker (US)", value="NVDA", key="tr_ticker").upper()
        tr_entry=st.number_input("Entry Price ($)", value=500.0, step=0.5, format="%.2f", key="tr_entry")
        tr_qty=st.number_input("Shares", value=10, step=1, key="tr_qty")
    with tr_c2:
        st.markdown('<div class="settings-label">TRAILING SETTINGS</div>', unsafe_allow_html=True)
        tr_method=st.radio("Method",["ATR","Persen","Swing Low"],key="tr_method")
        if tr_method=="ATR":      tr_atr_mult=st.slider("ATR Multiplier",1.0,5.0,2.0,0.5,key="tr_atr_m")
        elif tr_method=="Persen": tr_pct=st.slider("Trailing %",1.0,10.0,3.0,0.5,key="tr_pct")
        tr_alert=st.toggle("🔔 Alert Telegram", value=True, key="tr_alert")

    if st.button("🎯 CALCULATE TRAILING STOP", type="primary", use_container_width=True, key="btn_trail"):
        with st.spinner(f"Fetching {tr_ticker}..."):
            try:
                raw_tr=yf.download(tr_ticker, period="5d", interval="15m",
                                   progress=False, auto_adjust=True, threads=False)
                if not raw_tr.empty:
                    if isinstance(raw_tr.columns, pd.MultiIndex): raw_tr.columns=raw_tr.columns.droplevel(1)
                    df_tr=apply_intraday_indicators(raw_tr.dropna())
                    current=float(df_tr["Close"].iloc[-1]); atr_val=float(df_tr["ATR"].iloc[-1])
                    if tr_method=="ATR":      trail_result=calc_trailing_stop(tr_entry, current, atr_val, "ATR", tr_atr_mult)
                    elif tr_method=="Persen": trail_result=calc_trailing_stop(tr_entry, current, atr_val, "Persen", pct=tr_pct)
                    else:                     trail_result=calc_trailing_stop(tr_entry, current, atr_val, "Swing Low")
                    stop=trail_result["stop"]; dist=trail_result["distance"]
                    p_float=trail_result["profit_float"]; p_locked=trail_result["profit_locked"]
                    is_profit=trail_result["is_profitable"]
                    profit_rp=(current-tr_entry)*tr_qty; locked_rp=max(0,(stop-tr_entry)*tr_qty)
                    stop_col="#00ff88" if is_profit else "#ff3d5a"
                    profit_col="#00ff88" if profit_rp>=0 else "#ff3d5a"
                    st.markdown(f"""
                    <div style="background:#0d1117;border:1px solid {stop_col}44;border-radius:10px;padding:20px;margin-top:12px;">
                      <div class="metric-row">
                        <div class="metric-card"><div class="metric-label">Current Price</div>
                          <div class="metric-value" style="color:#00e5ff">${current:.2f}</div>
                          <div class="metric-sub">ATR: ${atr_val:.2f}</div></div>
                        <div class="metric-card" style="border-top-color:{stop_col}">
                          <div class="metric-label">🎯 Trailing Stop</div>
                          <div class="metric-value" style="color:{stop_col}">${stop:.2f}</div>
                          <div class="metric-sub">Distance: ${dist:.2f}</div></div>
                        <div class="metric-card" style="border-top-color:{profit_col}">
                          <div class="metric-label">Float P&L</div>
                          <div class="metric-value" style="color:{profit_col}">{p_float:+.1f}%</div>
                          <div class="metric-sub">${profit_rp:,.2f}</div></div>
                        <div class="metric-card" style="border-top-color:#00ff88">
                          <div class="metric-label">Locked Profit 🔒</div>
                          <div class="metric-value" style="color:#00ff88">{p_locked:+.1f}%</div>
                          <div class="metric-sub">${locked_rp:,.2f}</div></div>
                      </div>
                      <div style="margin-top:12px;font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">
                        💼 {tr_qty} shares · {'✅ Profit locked!' if is_profit else '⚠️ Stop below entry'}
                      </div>
                    </div>""", unsafe_allow_html=True)
                    if tr_alert and TOKEN and CHAT_ID:
                        now_tr=datetime.now(eastern_tz)
                        msg_tr=(f"🎯 *TRAILING STOP UPDATE*\n⏰ `{now_tr.strftime('%H:%M:%S')} ET`\n{'━'*28}\n"
                                f"📌 *{tr_ticker}* | {tr_method}\n💰 Entry: `${tr_entry:.2f}` → Now: `${current:.2f}`\n"
                                f"🎯 Stop: `${stop:.2f}` | Locked: `{p_locked:+.1f}%` (${locked_rp:,.2f})\n"
                                f"📊 Float: `{p_float:+.1f}%` (${profit_rp:,.2f})\n{'━'*28}\n⚠️ _NOT financial advice!_")
                        try:
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                          data={"chat_id":CHAT_ID,"text":msg_tr,"parse_mode":"Markdown"}, timeout=10)
                            st.success("📡 Trailing stop alert sent!")
                        except: pass
                else:
                    st.error(f"Data for {tr_ticker} not available")
            except Exception as ex:
                st.error(f"Error: {str(ex)[:80]}")

# ════════════════════════════════════════════════════
#  TAB 7: BACKTEST
# ════════════════════════════════════════════════════
with tab_backtest:
    st.markdown('<div class="section-title">Backtest Engine · 15M Intraday · US Stocks</div>', unsafe_allow_html=True)

    bt_c1, bt_c2, bt_c3, bt_c4 = st.columns(4)
    bt_mode=bt_c1.selectbox("Mode",["Scalping ⚡","Momentum 🚀","Reversal 🎯","Bagger 💎"],key="bt_mode")
    bt_sc=bt_c2.slider("Min Score",0,6,4,key="bt_sc")
    bt_fwd=int(bt_c3.number_input("Hold (bars)",value=4,step=1,min_value=1,max_value=20))
    bt_sl_mult=bt_c4.number_input("SL mult (xATR)",value=0.8,step=0.1,min_value=0.1,max_value=3.0)
    st.caption(f"Hold {bt_fwd} bars × 15 min = ~{bt_fwd*15} minutes per trade")

    if st.button("🚀 Run Backtest", type="primary", key="bt_run"):
        data_dict=st.session_state.get("data_dict",{})
        if not data_dict:
            st.warning("Run Scanner first bro!")
        else:
            bt_results=[]; bt_by_trend={"▲ UP":[],"▼ DOWN":[],"◆ SIDE":[]}
            bt_by_session={"Pre-Market 9:30":[],"Mid Day 11-14":[],"Power Hour 15-16":[]}
            bt_by_score={4:[],5:[],6:[]}
            bt_pb=st.progress(0); sample=list(data_dict.keys())[:80]
            for bi, ticker in enumerate(sample):
                bt_pb.progress((bi+1)/len(sample))
                try:
                    d=data_dict[ticker].copy()
                    if len(d)<60: continue
                    d=apply_intraday_indicators(d)
                    for ii in range(50, len(d)-bt_fwd):
                        r0=d.iloc[ii]; r1=d.iloc[ii-1]; r2=d.iloc[ii-2]
                        if bt_mode=="Scalping ⚡":   sc,_,_=score_scalping(r0,r1,r2)
                        elif bt_mode=="Momentum 🚀": sc,_,_=score_momentum(r0,r1,r2)
                        elif bt_mode=="Bagger 💎":   sc,_,_=score_bagger(r0,r1,r2,d.iloc[:ii+1])
                        else:                         sc,_,_=score_reversal(r0,r1,r2)
                        if sc<bt_sc: continue
                        entry=float(r0['Close']); atr_v=float(r0['ATR']) if not np.isnan(float(r0['ATR'])) else entry*0.005
                        if bt_mode=="Scalping ⚡":   tp_p=entry+1.5*atr_v; sl_p=entry-bt_sl_mult*atr_v
                        elif bt_mode=="Momentum 🚀": tp_p=entry+2.0*atr_v; sl_p=entry-bt_sl_mult*atr_v
                        elif bt_mode=="Bagger 💎":   tp_p=entry+3.0*atr_v; sl_p=entry-1.0*atr_v
                        else:                         tp_p=entry+2.5*atr_v; sl_p=entry-bt_sl_mult*atr_v
                        exit_price=float(d.iloc[ii+bt_fwd]['Close'])
                        for fwd_i in range(1, bt_fwd+1):
                            bar=d.iloc[ii+fwd_i]
                            if float(bar['High'])>=tp_p: exit_price=tp_p; break
                            if float(bar['Low'])<=sl_p:  exit_price=sl_p; break
                        ret=(exit_price-entry)/entry*100; bt_results.append(ret)
                        e9=float(r0['EMA9']); e21=float(r0['EMA21']); e50=float(r0['EMA50'])
                        tr="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else "◆ SIDE")
                        bt_by_trend[tr].append(ret)
                        try:
                            hr=d.index[ii].hour
                            if 9<=hr<11:  bt_by_session["Pre-Market 9:30"].append(ret)
                            elif 11<=hr<15: bt_by_session["Mid Day 11-14"].append(ret)
                            elif 15<=hr<16: bt_by_session["Power Hour 15-16"].append(ret)
                        except: pass
                        sc_int=int(sc)
                        if sc_int in bt_by_score: bt_by_score[sc_int].append(ret)
                except: continue
            bt_pb.empty()
            if not bt_results:
                st.warning("No trades match. Lower Min Score.")
            else:
                arr=np.array(bt_results); wr=len(arr[arr>0])/len(arr)*100
                avg=np.mean(arr); med=np.median(arr)
                pf=arr[arr>0].sum()/max(abs(arr[arr<0].sum()),0.01)
                mxdd=arr[arr<0].min() if len(arr[arr<0])>0 else 0
                st.markdown(f"""
                <div class="bt-result">
                  <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;letter-spacing:2px;margin-bottom:14px;">
                    {len(arr)} TRADES · SCORE≥{bt_sc} · HOLD {bt_fwd} BARS (~{bt_fwd*15}M) · {bt_mode}
                  </div>
                  <div style="display:flex;flex-wrap:wrap;">
                    <span class="bt-metric"><div class="bt-metric-val" style="color:{'#00ff88' if wr>=55 else '#ffb700' if wr>=50 else '#ff3d5a'}">{wr:.1f}%</div><div class="bt-metric-lbl">Win Rate</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:{'#00ff88' if avg>0 else '#ff3d5a'}">{avg:+.2f}%</div><div class="bt-metric-lbl">Avg Return</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#00e5ff">{med:+.2f}%</div><div class="bt-metric-lbl">Median</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:{'#00ff88' if pf>=1.5 else '#ffb700' if pf>=1 else '#ff3d5a'}">{pf:.2f}x</div><div class="bt-metric-lbl">Profit Factor</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#ff3d5a">{mxdd:.1f}%</div><div class="bt-metric-lbl">Max Loss</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#00ff88">{sum(1 for x in bt_results if x>0)}</div><div class="bt-metric-lbl">TP Hits</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#ff3d5a">{sum(1 for x in bt_results if x<0)}</div><div class="bt-metric-lbl">SL Hits</div></span>
                  </div>
                </div>""", unsafe_allow_html=True)
                tab_tr,tab_ses,tab_sc2=st.tabs(["📈 Per Trend","⏰ Per Session","🎯 Per Score"])
                with tab_tr:
                    for tr_name,vals in bt_by_trend.items():
                        if not vals: continue
                        a=np.array(vals); wr_t=len(a[a>0])/len(a)*100; avg_t=np.mean(a)
                        col="#00ff88" if wr_t>=55 else("#ffb700" if wr_t>=50 else "#ff3d5a")
                        st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;"><span style="font-family:Space Mono,monospace;font-size:12px;color:#c9d1d9;">{tr_name}</span><span style="font-family:Space Mono,monospace;font-size:11px;color:{col};">{wr_t:.1f}% WR · avg {avg_t:+.2f}% · {len(a)} trades</span></div><div style="height:8px;background:var(--border);border-radius:4px;overflow:hidden;margin-top:4px;"><div style="width:{int(wr_t)}%;height:100%;background:{col};border-radius:4px;"></div></div></div>', unsafe_allow_html=True)
                with tab_ses:
                    for sname,vals in bt_by_session.items():
                        if not vals: continue
                        a=np.array(vals); wr_s=len(a[a>0])/len(a)*100; avg_s=np.mean(a)
                        col="#00ff88" if wr_s>=55 else("#ffb700" if wr_s>=50 else "#ff3d5a")
                        st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;"><span style="font-family:Space Mono,monospace;font-size:12px;color:#c9d1d9;">⏰ {sname}</span><span style="font-family:Space Mono,monospace;font-size:11px;color:{col};">{wr_s:.1f}% WR · avg {avg_s:+.2f}% · {len(a)} trades</span></div><div style="height:8px;background:var(--border);border-radius:4px;overflow:hidden;margin-top:4px;"><div style="width:{int(wr_s)}%;height:100%;background:{col};border-radius:4px;"></div></div></div>', unsafe_allow_html=True)
                with tab_sc2:
                    for sc_lv in [4,5,6]:
                        vals=bt_by_score.get(sc_lv,[])
                        if not vals: continue
                        a=np.array(vals); wr_v=len(a[a>0])/len(a)*100; avg_v=np.mean(a)
                        col="#00ff88" if wr_v>=55 else("#ffb700" if wr_v>=50 else "#ff3d5a")
                        st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;"><span style="font-family:Space Mono,monospace;font-size:12px;color:#c9d1d9;">Score {sc_lv} [{"█"*sc_lv+"░"*(6-sc_lv)}]</span><span style="font-family:Space Mono,monospace;font-size:11px;color:{col};">{wr_v:.1f}% WR · avg {avg_v:+.2f}% · {len(a)} trades</span></div><div style="height:8px;background:var(--border);border-radius:4px;overflow:hidden;margin-top:4px;"><div style="width:{int(wr_v)}%;height:100%;background:{col};border-radius:4px;"></div></div></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════
_now_f=datetime.now(eastern_tz).timestamp()
if st.session_state.last_scan_time:
    _rem2=max(0, 300-(_now_f-st.session_state.last_scan_time))
    mnt2=int(_rem2//60); sec2=int(_rem2%60)
    last_t2=datetime.fromtimestamp(st.session_state.last_scan_time, eastern_tz).strftime("%H:%M:%S")
    time_info=f"⏱️ Next auto-scan: <span style='color:#00e5ff'>{mnt2:02d}:{sec2:02d}</span> · Last: <span style='color:#2dd4bf'>{last_t2} ET</span>"
else:
    time_info="⏱️ Click Scan to start"

st.markdown(f"""
<div style="margin-top:28px;padding-top:14px;border-top:1px solid #1c2533;
     display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;">
  <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">
    🦅 US Turbo v1 · NYSE · NASDAQ · Bagger Detector · VIX Monitor · yFinance
  </div>
  <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">{time_info}</div>
</div>
<div style="font-family:Space Mono,monospace;font-size:9px;color:#2d3748;text-align:center;margin-top:8px;">
  ⚠️ NOT financial advice · For educational purposes only · DYOR always
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  AUTO-REFRESH — Non-blocking
# ════════════════════════════════════════════════════
if st.session_state.last_scan_time:
    _now_f2=datetime.now(eastern_tz).timestamp()
    _elapsed2=_now_f2-st.session_state.last_scan_time
    if _elapsed2>=295:
        time.sleep(5); st.rerun()
