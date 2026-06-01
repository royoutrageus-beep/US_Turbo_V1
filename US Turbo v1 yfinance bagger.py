import yfinance as yf
import pandas as pd
import streamlit as st
import time
import random
import requests
import numpy as np
import pytz
from datetime import datetime

TOKEN   = st.secrets.get("TELEGRAM_TOKEN", "")
CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")
ny_tz   = pytz.timezone('America/New_York')

for _k, _v in [("tt_last_sent", set()), ("wl_results", []),
                ("wl_mode_used", ""), ("scan_results", []),
                ("data_dict", {}), ("last_scan_time", None),
                ("last_scan_mode", "Scalping ⚡"),
                ("sector_data", {}), ("gapup_results", []),
                ("overnight_results", []), ("beta_data", [])]:
    if _k not in st.session_state: st.session_state[_k] = _v

st.set_page_config(layout="wide", page_title="US Turbo v1.1", page_icon="🦅", initial_sidebar_state="collapsed")

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
#  USD → IDR LIVE CONVERTER
#  Multi-source: yFinance USDIDR=X → Yahoo Finance
#  → Google Finance scrape → hardcoded fallback 16200
# ════════════════════════════════════════════════════
@st.cache_data(ttl=1800)
def get_usd_idr():
    """Fetch live USD/IDR rate. Returns (rate, source_label)."""
    # Source 1: yFinance ticker USDIDR=X
    try:
        raw = yf.download("USDIDR=X", period="2d", interval="1d",
                          progress=False, auto_adjust=True, timeout=8)
        if raw is not None and not raw.empty:
            c = raw["Close"]
            if isinstance(c, pd.DataFrame): c = c.iloc[:, 0]
            c = c.dropna()
            if len(c) >= 1:
                rate = float(c.iloc[-1])
                if 10000 < rate < 25000:
                    return rate, "yFinance"
    except: pass
    # Source 2: Yahoo Finance JSON API
    try:
        import json
        r = requests.get(
            "https://query1.finance.yahoo.com/v8/finance/chart/USDIDR=X?interval=1d&range=2d",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=8
        )
        if r.status_code == 200:
            data = r.json()
            closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            closes = [x for x in closes if x is not None]
            if closes:
                rate = float(closes[-1])
                if 10000 < rate < 25000:
                    return rate, "Yahoo API"
    except: pass
    # Source 3: ExchangeRate-API (free, no key needed)
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=8)
        if r.status_code == 200:
            data = r.json()
            if "rates" in data and "IDR" in data["rates"]:
                rate = float(data["rates"]["IDR"])
                if 10000 < rate < 25000:
                    return rate, "ExchangeRate-API"
    except: pass
    # Fallback: hardcoded approximation
    return 16200.0, "Fallback (stale)"

def usd_to_idr(usd_price, rate):
    """Convert USD price to IDR string, auto-format."""
    idr = usd_price * rate
    if idr >= 1_000_000:
        return f"Rp{idr/1_000_000:.2f}jt"
    elif idr >= 1_000:
        return f"Rp{idr:,.0f}"
    else:
        return f"Rp{idr:.0f}"

def usd_to_idr_int(usd_price, rate):
    """Return integer IDR value."""
    return int(usd_price * rate)

def fmt_idr(idr_val):
    """Format raw IDR integer nicely."""
    if idr_val >= 1_000_000_000:
        return f"Rp{idr_val/1_000_000_000:.2f}M"
    elif idr_val >= 1_000_000:
        return f"Rp{idr_val/1_000_000:.1f}jt"
    elif idr_val >= 1_000:
        return f"Rp{idr_val:,.0f}"
    return f"Rp{idr_val}"

# ════════════════════════════════════════════════════
#  HUMANIZED FETCH HELPERS v2
# ════════════════════════════════════════════════════
import requests as _req_sess
_YF_SESSION = _req_sess.Session()
_YF_SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
})

def _human_sleep(batch_num, total_batches):
    pct = batch_num / max(total_batches, 1)
    if abs(pct-0.25)<0.06 or abs(pct-0.50)<0.06 or abs(pct-0.75)<0.06:
        pause = random.uniform(3.0, 6.0)
    elif random.random() < 0.10:
        pause = random.uniform(5.0, 9.0)
    elif random.random() < 0.20:
        pause = random.uniform(1.5, 3.5)
    else:
        pause = random.uniform(0.4, 1.3)
    time.sleep(pause)

def _random_chunks(tickers, min_sz=5, max_sz=15):
    lst = list(tickers)
    batches = []
    i = 0
    while i < len(lst):
        sz = min(random.randint(min_sz, max_sz), len(lst)-i)
        batches.append(lst[i:i+sz])
        i += sz
    return batches

def _yf_extract(raw, ticker, n_batch):
    try:
        if raw is None or raw.empty: return None
        _ohlcv = {'Open','High','Low','Close','Volume','open','high','low','close','volume'}
        if n_batch == 1:
            df = raw.copy()
            if isinstance(df.columns, pd.MultiIndex):
                l0 = df.columns.get_level_values(0).unique().tolist()
                l1 = df.columns.get_level_values(1).unique().tolist()
                if any(x in _ohlcv for x in l0):   df = df.droplevel(1, axis=1)
                elif any(x in _ohlcv for x in l1): df = df.droplevel(0, axis=1)
        else:
            if not isinstance(raw.columns, pd.MultiIndex): return None
            l0 = raw.columns.get_level_values(0).unique().tolist()
            l1 = raw.columns.get_level_values(1).unique().tolist()
            if ticker in l0:   df = raw[ticker].copy()
            elif ticker in l1: df = raw.xs(ticker, axis=1, level=1).copy()
            else: return None
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(-1)
        rename = {c: c.capitalize() for c in df.columns if c.islower()}
        if rename: df = df.rename(columns=rename)
        if 'Adj Close' in df.columns and 'Close' not in df.columns:
            df = df.rename(columns={'Adj Close': 'Close'})
        required = ['Open','High','Low','Close','Volume']
        if any(c not in df.columns for c in required): return None
        df = df[required].dropna(subset=['Close'])
        df = df[df['Volume'] > 0]
        return df if len(df) > 0 else None
    except: return None

# ════════════════════════════════════════════════════
#  STOCK LIST — US NYSE / NASDAQ
# ════════════════════════════════════════════════════
raw_stocks = [
    "AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","AMD","INTC","QCOM",
    "TXN","AVGO","MU","AMAT","KLAC","LRCX","MRVL","CRM","ORCL","NOW",
    "SNOW","PLTR","UBER","NFLX","RBLX","TTWO","EA","SMCI","ARM","DELL",
    "HPQ","HPE","CSCO","ANET","NET","DDOG","CRWD","ZS","PANW","FTNT",
    "OKTA","MDB","VEEV","WDAY","ADBE","INTU","CDNS","SNPS","MPWR","ENTG",
    "ONTO","ON","SWKS","QRVO","WOLF","IONQ","QUBT","RGTI","ACHR","JOBY",
    "JPM","BAC","WFC","GS","MS","C","BLK","SCHW","AXP","V",
    "MA","PYPL","SQ","COIN","HOOD","SOFI","AFRM","UPST","NU","FIS",
    "FI","FISV","PAYX","ADP","ICE","CME","CBOE","NDAQ","SPGI","MCO",
    "BX","KKR","APO","CG","ARES","TPG","MET","PRU","AIG","AFL",
    "ALL","TRV","HIG","CB","PGR","L","RLI","EG","AIZ","RE",
    "JNJ","UNH","PFE","MRK","ABBV","LLY","BMY","AMGN","GILD","BIIB",
    "REGN","MRNA","VRTX","ILMN","ISRG","MDT","SYK","EW","ZBH","HCA",
    "CVS","WBA","MCK","ABC","CAH","DGX","LH","IQV","CRL","MEDP",
    "PODD","DXCM","HOLX","NVCR","HIMS","TDOC","RMD","INSP","IRTC","NEOG",
    "HD","LOW","TGT","COST","TJX","ROST","ULTA","NKE","LULU","PVH",
    "RL","ANF","AEO","GPS","M","KSS","DHI","LEN","PHM","GRMN",
    "ORLY","AZO","AAP","GPC","TSCO","DLTR","DG","FIVE","BURL","RH",
    "WSM","BKNG","ABNB","EXPE","HLT","MAR","H","MGM","WYNN","LVS",
    "DKNG","LYFT",
    "WMT","PG","KO","PEP","MDLZ","KHC","GIS","K","MKC","HRL",
    "CPB","CAG","SJM","MO","PM","BTI","CL","CHD","CLX","EL",
    "COTY","KR","SYY","USFD","SFM",
    "XOM","CVX","COP","EOG","OXY","PSX","VLO","MPC","SLB","HAL",
    "BKR","DVN","FANG","MRO","APA","HES","CTRA","EQT","AR","RRC",
    "RIG","NOV","PTEN","CHK","SW","OVV","TRGP","KMI","WMB","ET",
    "EPD","MPLX","PAGP",
    "BA","CAT","HON","GE","MMM","RTX","LMT","NOC","GD","TDG",
    "ITW","EMR","ROK","PH","DOV","FTV","ROP","FAST","URI","WAB",
    "FDX","UPS","JBHT","XPO","SAIA","ODFL","CHRW","GXO","GWW","CARR",
    "OTIS","TT","JCI","AAON","BLDR","BECN","IBP","DOOR","AZEK","TREX",
    "LIN","APD","SHW","ECL","DD","DOW","NEM","FCX","AA","CLF",
    "X","NUE","STLD","RS","VMC","MLM","WRK","IP","PKG","SON",
    "ATR","BALL","BERY","SEE","SLGN","AMCR",
    "AMT","PLD","CCI","SPG","O","WP","VICI","EQIX","DLR","PSA",
    "EXR","WELL","VTR","BXP","SLG","KIM","REG","MAC","NNN","STORE",
    "NEE","DUK","SO","AEP","EXC","XEL","PPL","WEC","CMS","NI",
    "ES","EIX","ETR","FE","CNP","AES","BKH","NWE","OGE","AVA",
    "DIS","CMCSA","CHTR","VZ","T","TMUS","WBD","FOXA","FOX","NWSA",
    "LUMN","OMC","IPG","LAMR","OUT","SPOT","SNAP","PINS","RDDT","MTCH","IAC",
    "GME","AMC","RIVN","LCID","F","GM","STLA","NIO","XPEV",
    "LI","NKLA","WKHS","GOEV","HYLN","BLNK","CHPT",
    "EVGO","MULN","IDEX","SOLO","MARA","RIOT","HUT","BTBT",
    "CLSK","CIFR","IREN","CORZ","BTDR",
]
seen = set(); raw_stocks = [x for x in raw_stocks if not (x in seen or seen.add(x))]
stocks_yf  = raw_stocks
stock_map  = {s: s for s in raw_stocks}

# ════════════════════════════════════════════════════
#  FETCH INTRADAY — HUMANIZED v2
# ════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def fetch_intraday(tickers, chunk=None):
    all_dfs = {}
    batches = _random_chunks(list(tickers), min_sz=5, max_sz=15)
    n_b     = len(batches)
    for bi, batch in enumerate(batches):
        if not batch: continue
        if len(batch) == 1:
            try:
                raw = yf.download(batch[0], period="7d", interval="15m",
                                  progress=False, auto_adjust=True, threads=False)
                df  = _yf_extract(raw, batch[0], 1)
                if df is not None and len(df) >= 30:
                    all_dfs[batch[0]] = df
            except: pass
            time.sleep(random.uniform(0.2, 0.6))
        else:
            try:
                raw = yf.download(list(batch), period="7d", interval="15m",
                                  group_by='ticker', progress=False,
                                  threads=False, auto_adjust=True)
                for t in batch:
                    try:
                        df = _yf_extract(raw, t, len(batch))
                        if df is not None and len(df) >= 30:
                            all_dfs[t] = df
                    except: pass
            except:
                for t in batch:
                    if t in all_dfs: continue
                    try:
                        raw = yf.download(t, period="7d", interval="15m",
                                          progress=False, auto_adjust=True, threads=False)
                        df  = _yf_extract(raw, t, 1)
                        if df is not None and len(df) >= 30:
                            all_dfs[t] = df
                    except: pass
                    time.sleep(random.uniform(0.2, 0.5))
        _human_sleep(bi, n_b)
    return all_dfs

# ════════════════════════════════════════════════════
#  MARKET REGIME — SPX + VIX
# ════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def get_market_regime():
    try:
        df_spx = yf.download("^GSPC", period="60d", interval="1d",
                             progress=False, auto_adjust=True, timeout=8)
        df_vix = yf.download("^VIX",  period="5d",  interval="1d",
                             progress=False, auto_adjust=True, timeout=8)
        if df_spx is None or len(df_spx) < 10:
            return ("UNKNOWN", 0, 0, 0, "No data", 0.0, 0.0)
        close = df_spx["Close"].squeeze()
        if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
        ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
        ema55 = float(close.ewm(span=min(55, len(close)-1), adjust=False).mean().iloc[-1])
        price = float(close.iloc[-1])
        chg   = float(((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100)
        vix_val = 20.0
        try:
            vc = df_vix["Close"].squeeze()
            if isinstance(vc, pd.DataFrame): vc = vc.iloc[:,0]
            vix_val = float(vc.iloc[-1])
        except: pass
        if price < ema20:
            return ("RED",      price, ema20, ema55, f"SPX {price:,.0f} < EMA20 → Bearish", chg, vix_val)
        elif price > ema20 and price > ema55:
            return ("GREEN",    price, ema20, ema55, f"SPX {price:,.0f} > EMA20 & EMA55 → Bullish", chg, vix_val)
        else:
            return ("SIDEWAYS", price, ema20, ema55, f"SPX {price:,.0f} between EMA20-EMA55", chg, vix_val)
    except:
        return ("UNKNOWN", 0, 0, 0, "SPX unavailable", 0.0, 20.0)

def get_regime_config(regime):
    return {
        "RED":     {"mode":"Reversal 🎯","min_score":5,"min_rvol":2.0,"sl_mult":0.6,
                    "label":"🔴 MARKET RED — Reversal Only, Score ≥ 5","color":"#ff3d5a",
                    "desc":"Market bearish. Focus reversal oversold, tight filter."},
        "GREEN":   {"mode":"Bagger 💎","min_score":4,"min_rvol":2.0,"sl_mult":0.8,
                    "label":"🟢 MARKET GREEN — Bagger Hunt Mode, Score ≥ 4","color":"#00ff88",
                    "desc":"Market bullish. Hunt breakout + accumulation baggers."},
        "SIDEWAYS":{"mode":"Scalping ⚡","min_score":4,"min_rvol":2.0,"sl_mult":0.7,
                    "label":"🟡 MARKET SIDEWAYS — Scalping, RVOL ≥ 2x","color":"#ffb700",
                    "desc":"Market sideways. RVOL must be strong."},
        "UNKNOWN": {"mode":"Scalping ⚡","min_score":4,"min_rvol":1.5,"sl_mult":0.8,
                    "label":"⚪ REGIME UNKNOWN — Manual Mode","color":"#4a5568",
                    "desc":"Cannot detect market condition."},
    }.get(regime,{"mode":"Scalping ⚡","min_score":4,"min_rvol":1.5,"sl_mult":0.8,
                  "label":"⚪ UNKNOWN","color":"#4a5568","desc":""})

# ════════════════════════════════════════════════════
#  INDICATORS
# ════════════════════════════════════════════════════
def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def rsi_smooth(s, p=14, smooth=3):
    delta=s.diff(); gain=delta.clip(lower=0).rolling(p).mean()
    loss=(-delta.clip(upper=0)).rolling(p).mean()
    rs=gain/loss.replace(0,np.nan); raw=100-100/(1+rs)
    return raw, ema(raw, smooth)

def stochastic(h, l, c, k=14, d=3):
    ll=l.rolling(k).min(); hh=h.rolling(k).max()
    K=100*(c-ll)/(hh-ll).replace(0,np.nan); D=K.rolling(d).mean()
    return K.fillna(50), D.fillna(50)

def macd(s, f=12, sl=26, sg=9):
    ml=ema(s,f)-ema(s,sl); sig=ema(ml,sg)
    return ml, sig, ml-sig

def vwap(df):
    tp=(df['High']+df['Low']+df['Close'])/3
    return (tp*df['Volume']).cumsum()/df['Volume'].cumsum()

def apply_intraday_indicators(df):
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
    df['EMA9']=ema(df['Close'],9); df['EMA21']=ema(df['Close'],21)
    df['EMA50']=ema(df['Close'],50); df['EMA200']=ema(df['Close'],200)
    df['RSI'],df['RSI_EMA']=rsi_smooth(df['Close'],14,3)
    df['STOCH_K'],df['STOCH_D']=stochastic(df['High'],df['Low'],df['Close'],14,3)
    df['MACD'],df['MACD_Sig'],df['MACD_Hist']=macd(df['Close'])
    try:    df['VWAP']=vwap(df)
    except: df['VWAP']=df['Close']
    df['BB_mid']=df['Close'].rolling(20).mean(); df['BB_std']=df['Close'].rolling(20).std()
    df['BB_upper']=df['BB_mid']+2*df['BB_std']; df['BB_lower']=df['BB_mid']-2*df['BB_std']
    df['BB_pct']=(df['Close']-df['BB_lower'])/(df['BB_upper']-df['BB_lower'])
    df['AvgVol']=df['Volume'].rolling(20).mean()
    df['RVOL']=df['Volume']/df['AvgVol'].replace(0,np.nan)
    df['NetVol']=np.where(df['Close']>=df['Open'],df['Volume'],-df['Volume'])
    df['NetVol3']=pd.Series(df['NetVol'],index=df.index).rolling(3).sum()
    df['NetVol8']=pd.Series(df['NetVol'],index=df.index).rolling(8).sum()
    df['VolSpike']=df['RVOL']>2.5
    df['Body']=(df['Close']-df['Open']).abs()
    df['BodyRatio']=df['Body']/(df['High']-df['Low']).replace(0,np.nan)
    df['BullBar']=(df['Close']>df['Open'])&(df['BodyRatio']>0.5)
    df['ROC3']=df['Close'].pct_change(3); df['ROC8']=df['Close'].pct_change(8)
    df['HH']=df['High']>df['High'].shift(1); df['HL']=df['Low']>df['Low'].shift(1)
    df['LL']=df['Low']<df['Low'].shift(1);   df['LH']=df['High']<df['High'].shift(1)
    tr=pd.concat([df['High']-df['Low'],(df['High']-df['Close'].shift()).abs(),(df['Low']-df['Close'].shift()).abs()],axis=1).max(axis=1)
    df['ATR']=tr.rolling(14).mean()
    return df

# ════════════════════════════════════════════════════
#  SCORING
# ════════════════════════════════════════════════════
def score_scalping(r, p, p2):
    score=0; reasons=[]
    if r['EMA9']>r['EMA21']>r['EMA50']:   score+=1.5; reasons.append("EMA stack ▲")
    elif r['EMA9']>r['EMA21']:             score+=0.8; reasons.append("EMA9>21")
    if r['Close']>r['VWAP']:              score+=1;   reasons.append("Above VWAP")
    if r['MACD_Hist']>0 and r['MACD_Hist']>float(p['MACD_Hist']):
        score+=1.5; reasons.append("MACD hist expanding ✦")
        if p2 is not None and float(p['MACD_Hist'])>float(p2['MACD_Hist']): score+=0.3
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
    rev=0; pk=float(p['STOCH_K']); pd_=float(p['STOCH_D'])
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
    if float(r['BodyRatio'])>0.75 and float(r['Close'])<float(r['Open']): score-=0.8; reasons.append("⚠️ Strong bear bar")
    return max(0,min(6,round(score,1))), reasons, {}

def score_bagger(r, p, p2, df_full):
    score=0; reasons=[]; close=float(r['Close'])
    e9=float(r['EMA9']); e21=float(r['EMA21']); e50=float(r['EMA50']); e200=float(r['EMA200'])
    rvol=float(r['RVOL']); rsi_e=float(r['RSI_EMA']); wyckoff_phase="SCANNING"
    is_sideways=False; range_high=close*1.05; range_low=close*0.95
    sideways_bars=min(20,len(df_full)-2)
    try:
        r_highs=df_full['High'].iloc[-sideways_bars-1:-1]; r_lows=df_full['Low'].iloc[-sideways_bars-1:-1]
        range_high=float(r_highs.max()); range_low=float(r_lows.min())
        range_pct=(range_high-range_low)/max(range_low,0.01)*100; is_sideways=range_pct<8.0
        if is_sideways:
            tightness_bonus=max(0,(8.0-range_pct)/8.0); score+=1.0+tightness_bonus*0.5
            reasons.append(f"Sideways {range_pct:.1f}% ({sideways_bars}B) ✦"); wyckoff_phase="A-B"
    except: pass
    try:
        vol_ma20=float(df_full['AvgVol'].iloc[-1]); vol_last5=float(df_full['Volume'].iloc[-6:-1].mean())
        dry_ratio=vol_last5/max(vol_ma20,1)
        if dry_ratio<0.5 and is_sideways:   score+=2.0; reasons.append(f"Dry vol {dry_ratio:.2f}x — stealth accum ✦✦"); wyckoff_phase="A-B AKUMULASI"
        elif dry_ratio<0.7 and is_sideways: score+=1.2; reasons.append(f"Vol drying {dry_ratio:.2f}x ✦"); wyckoff_phase="A-B AKUMULASI"
        elif dry_ratio<0.85 and is_sideways:score+=0.6; reasons.append(f"Vol below avg {dry_ratio:.2f}x")
    except: pass
    try:
        if len(df_full)>=12:
            netvols_10=[float(df_full['NetVol'].iloc[i]) for i in range(-11,-1)]
            net_positive=sum(1 for v in netvols_10 if v>0); net_ratio=net_positive/10
            if net_ratio>=0.7 and is_sideways:  score+=1.5; reasons.append(f"Stealth net buy {net_positive}/10 bars ✦✦")
            elif net_ratio>=0.6:                score+=0.8; reasons.append(f"Net buy {net_positive}/10 bars")
            elif net_ratio>=0.5:                score+=0.4
    except:
        nv3=float(r['NetVol3']); nv8=float(r['NetVol8'])
        if nv3>0 and nv8>0: score+=0.8; reasons.append("Net buyer sustained ✦")
        elif nv3>0:          score+=0.3
    try:
        bb_curr=float(r['BB_std']); bb_avg10=float(df_full['BB_std'].iloc[-11:-1].mean())
        sq_ratio=bb_curr/max(bb_avg10,0.0001)
        if sq_ratio<0.7 and is_sideways:  score+=1.5; reasons.append(f"BB squeeze {sq_ratio:.2f}x ✦✦")
        elif sq_ratio<0.85:               score+=0.8; reasons.append(f"BB squeeze {sq_ratio:.2f}x")
    except: pass
    spring_detected=False
    try:
        lookback_sp=min(15,len(df_full)-3); prior_lows=df_full['Low'].iloc[-lookback_sp-2:-2]
        support=float(prior_lows.min()); bar_low=float(r['Low']); bar_close=float(r['Close']); bar_high=float(r['High'])
        is_spring=bar_low<support and bar_close>support
        if is_spring:
            recovery_strength=(bar_close-bar_low)/max(bar_high-bar_low,0.0001)
            if recovery_strength>0.7 and rvol>1.2:
                score+=3.0; reasons.append(f"🔥 SPRING! {recovery_strength:.0%} rebound ✦✦✦"); wyckoff_phase="SPRING ⚡"; spring_detected=True
            elif recovery_strength>0.5:
                score+=1.8; reasons.append(f"Spring ({recovery_strength:.0%}) ✦✦"); wyckoff_phase="SPRING"; spring_detected=True
        is_post_spring=(float(p['Low'])<support and float(p['Close'])>support and bar_close>float(p['Close']))
        if is_post_spring and not spring_detected:
            score+=2.0; reasons.append("Post-spring confirmation 🚀 ✦✦"); wyckoff_phase="POST-SPRING"; spring_detected=True
    except: pass
    try:
        above_resistance=close>range_high*0.998; thick_body=float(r['BodyRatio'])>0.55; bull_bar_flag=float(r['Close'])>float(r['Open'])
        if rvol>4.0 and above_resistance and thick_body and bull_bar_flag:
            score+=3.0; reasons.append(f"🚀 PHASE D! RVOL={rvol:.1f}x breakout ✦✦✦"); wyckoff_phase="PHASE D 🚀"
        elif rvol>3.0 and above_resistance and bull_bar_flag:
            score+=2.2; reasons.append(f"Breakout RVOL={rvol:.1f}x ✦✦"); wyckoff_phase="BREAKOUT ✦"
        elif rvol>2.0 and above_resistance: score+=1.5; reasons.append(f"Breakout attempt RVOL={rvol:.1f}x")
        elif above_resistance:              score+=0.8; reasons.append("Above resistance")
        else:
            if rvol>4.0:   score+=1.5; reasons.append(f"RVOL={rvol:.1f}x MASSIVE 🔥🔥")
            elif rvol>3.0: score+=1.0; reasons.append(f"RVOL={rvol:.1f}x SURGE 🔥")
            elif rvol>2.0: score+=0.5; reasons.append(f"RVOL={rvol:.1f}x")
            elif rvol<1.3 and wyckoff_phase not in ["A-B AKUMULASI","SPRING","POST-SPRING"]: score-=0.5
    except:
        if rvol>4.0:   score+=1.5; reasons.append(f"RVOL={rvol:.1f}x MASSIVE 🔥🔥")
        elif rvol>3.0: score+=1.0; reasons.append(f"RVOL={rvol:.1f}x SURGE 🔥")
        elif rvol>2.0: score+=0.5; reasons.append(f"RVOL={rvol:.1f}x")
    if e9>e21>e50>e200:  score+=1.5; reasons.append("EMA golden stack ✦✦")
    elif e9>e21>e50:     score+=1.0; reasons.append("EMA stack ▲")
    elif e9>e21:         score+=0.4
    elif is_sideways and wyckoff_phase in ["A-B AKUMULASI","SPRING","POST-SPRING"]: score+=0.2
    if wyckoff_phase in ["A-B","A-B AKUMULASI","SPRING","POST-SPRING"]:
        if 25<=rsi_e<=52:  score+=1.0; reasons.append(f"RSI-EMA={rsi_e:.1f} accum zone ✓")
        elif rsi_e<25:     score+=0.6; reasons.append(f"RSI-EMA={rsi_e:.1f} extreme OS")
        elif rsi_e>65:     score-=0.3
    else:
        if 52<rsi_e<72:   score+=1.0; reasons.append(f"RSI-EMA={rsi_e:.1f} momentum")
        elif rsi_e>=72:   score-=0.5; reasons.append(f"⚠️ RSI OB {rsi_e:.1f}")
        elif rsi_e<40:    score-=0.3
    if close>float(r['VWAP']): score+=0.5; reasons.append("Above VWAP")
    if e200>0 and close<e200*0.88: score-=1.0
    try:
        if len(df_full)>=4:
            bc=sum(1 for i in range(-3,0) if float(df_full['Close'].iloc[i])>float(df_full['Open'].iloc[i]))
            if bc==3:   score+=0.8; reasons.append("3x consecutive bull bars")
            elif bc==2: score+=0.3
    except: pass
    if wyckoff_phase!="SCANNING": reasons.insert(0,f"⚙️ Wyckoff: {wyckoff_phase}")
    return max(0,min(6,round(score,1))),reasons,{"wyckoff_phase":wyckoff_phase}

def score_overnight(r, p, p2):
    score=0; reasons=[]
    hi_lo=float(r["High"])-float(r["Low"]); close_pct=(float(r["Close"])-float(r["Low"]))/max(hi_lo,0.01)
    if close_pct>0.75:   score+=2;   reasons.append(f"Closed near HOD ({close_pct:.0%}) ✦✦")
    elif close_pct>0.55: score+=1;   reasons.append(f"Strong close ({close_pct:.0%})")
    rvol=float(r["RVOL"])
    if rvol>3.0:   score+=2;   reasons.append(f"RVOL={rvol:.1f}x SURGE 🔥")
    elif rvol>2.0: score+=1.5; reasons.append(f"RVOL={rvol:.1f}x power hour")
    elif rvol>1.5: score+=0.8; reasons.append(f"RVOL={rvol:.1f}x")
    if r["EMA9"]>r["EMA21"]>r["EMA50"]:  score+=1.5; reasons.append("EMA stack ▲")
    elif r["EMA9"]>r["EMA21"]:            score+=0.8; reasons.append("EMA9>21")
    rsi_e=float(r["RSI_EMA"])
    if 45<rsi_e<70:  score+=1;   reasons.append(f"RSI-EMA={rsi_e:.1f} ✓")
    elif rsi_e>=70:  score-=1;   reasons.append(f"⚠️ RSI OB {rsi_e:.1f}")
    elif rsi_e<40:   score+=0.5; reasons.append(f"RSI bounce zone {rsi_e:.1f}")
    if float(r["MACD_Hist"])>0 and float(r["MACD_Hist"])>float(p["MACD_Hist"]):
        score+=1; reasons.append("MACD hist expanding ✦")
    elif float(r["MACD_Hist"])>0: score+=0.5; reasons.append("MACD +")
    if float(r["Close"])>float(r["VWAP"]): score+=0.5; reasons.append("Above VWAP")
    if float(r["NetVol8"])>0: score+=0.5; reasons.append("Net buyer sustained 8 bar")
    elif float(r["NetVol3"])>0: score+=0.3; reasons.append("Net buyer 3 bar")
    return max(0,min(6,round(score,1))),reasons,{}

def get_signal(score, mode):
    t={"Scalping ⚡":{5:"RIPPING ⚡",4:"POTENSIAL 🔥",3:"WATCH 👀"},
       "Momentum 🚀":{5:"RIPPING 🚀",4:"POTENSIAL 🔥",3:"WATCH 👀"},
       "Reversal 🎯":{5:"REVERSAL 🎯",4:"POTENSIAL 🔥",3:"WATCH 👀"},
       "Bagger 💎":{5:"BAGGER 💎",4:"KANDIDAT 🚀",3:"WATCH 👀"}}.get(mode,{})
    for thresh in sorted(t.keys(),reverse=True):
        if score>=thresh: return t[thresh]
    return "WAIT"

def get_card_class(signal):
    if "BAGGER" in signal or "KANDIDAT" in signal: return "bagger"
    if "RIPPING" in signal or "REVERSAL" in signal: return "gacor"
    if "KANDIDAT" in signal or "POTENSIAL" in signal: return "potensial"
    if "WATCH" in signal: return "watch"
    return ""

def send_telegram(results_top, source="Scanner"):
    if not TOKEN or not CHAT_ID: return
    now_et=datetime.now(ny_tz); is_open=(now_et.hour==9 and now_et.minute>=30) or (10<=now_et.hour<16)
    sep="━"*28
    hdr=(f"{'🟢 MARKET OPEN' if is_open else '🌙 AFTER HOURS'}\n"
         f"🦅 *US TURBO {'WATCHLIST' if source=='Watchlist' else 'ALERT'}*\n"
         f"⏰ `{now_et.strftime('%H:%M:%S')} ET` · `{now_et.strftime('%d %b %Y')}`\n{sep}\n")
    body=""
    for r in results_top[:5]:
        sig=r.get('Signal','-')
        em="💎" if "BAGGER" in sig else("🏆" if("RIPPING" in sig or "REVERSAL" in sig) else("🔥" if "POTENSIAL" in sig else "👀"))
        te="📈" if "▲" in r.get('Trend','') else("📉" if "▼" in r.get('Trend','') else "➡️")
        bar="█"*int(r['Score'])+"░"*(6-int(r['Score']))
        p_d=r.get('Price_fmt',f"Rp{int(r.get('Price(IDR)',r.get('Price(USD)',0)*16200)):,}")
        tp_d=r.get('TP_fmt',f"Rp{int(r.get('TP_IDR',r.get('TP_USD',r.get('TP',0))*16200)):,}")
        sl_d=r.get('SL_fmt',f"Rp{int(r.get('SL_IDR',r.get('SL_USD',r.get('SL',0))*16200)):,}")
        p_usd=r.get('Price(USD)',r.get('Price',0))
        body+=(f"\n{em} *{r['Ticker']}*  `{sig}`\n"
               f"   💰 {p_d} (${p_usd:.2f}) {te}\n"
               f"   📊 Score: `[{bar}] {r['Score']}/6`\n"
               f"   📈 RSI-EMA: `{r.get('RSI-EMA',0)}` | RVOL: `{r.get('RVOL',0)}x`\n"
               f"   🎯 TP: {tp_d} | SL: {sl_d} | R:R `{r['R:R']}`\n"
               f"   💡 _{r.get('Reasons','')[:60]}_\n")
    footer=f"\n{sep}\n⚡ _US Turbo v1.1 · 15M · NYSE/NASDAQ_\n⚠️ _NOT financial advice. DYOR!_"
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id":CHAT_ID,"text":hdr+body+footer,"parse_mode":"Markdown"},timeout=10)
    except: pass

# ════════════════════════════════════════════════════
#  PIVOT, MTF, SECTORS, GAP UP, TRAILING
# ════════════════════════════════════════════════════
def calc_pivot_points(high, low, close):
    pp=(high+low+close)/3; r1=2*pp-low; r2=pp+(high-low); r3=high+2*(pp-low)
    s1=2*pp-high; s2=pp-(high-low); s3=low-2*(high-pp)
    return {"PP":pp,"R1":r1,"R2":r2,"R3":r3,"S1":s1,"S2":s2,"S3":s3}

@st.cache_data(ttl=3600)
def fetch_pivot_data(ticker):
    try:
        df=yf.download(ticker,period="5d",interval="1d",progress=False,auto_adjust=True,threads=False)
        if df is None or len(df)<2: return None
        df2=_yf_extract(df,ticker,1)
        if df2 is None or len(df2)<2: return None
        prev=df2.iloc[-2]
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

@st.cache_data(ttl=360)
def fetch_mtf_data(ticker):
    result={}
    try:
        raw=yf.download(ticker,period="7d",interval="15m",progress=False,auto_adjust=True,threads=False)
        df15=_yf_extract(raw,ticker,1)
        if df15 is None or len(df15)<10: return result
        if len(df15)>=20: result["M15"]=df15
        for rs_rule,rs_key,min_b in [("1h","H1",10),("1D","D1",3)]:
            try:
                df_rs=df15.resample(rs_rule).agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna(subset=["Close"])
                df_rs=df_rs[df_rs["Volume"]>0]
                if len(df_rs)>=min_b: result[rs_key]=df_rs
            except: pass
    except: pass
    return result

def score_mtf(ticker, mode="Scalping ⚡"):
    mtf=fetch_mtf_data(ticker); scores={}
    for tf_key,df in mtf.items():
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
    bc=sum(1 for v in vals if v>=4)
    if bc==len(vals):  return "FULL ALIGN 🔥","#00ff88",avg
    elif bc>=2:        return "PARTIAL ⚡","#ffb700",avg
    elif bc==1:        return "MIXED ⚠️","#ff7b00",avg
    else:              return "NO ALIGN ❌","#ff3d5a",avg

SECTORS={
    "Technology":            ["AAPL","MSFT","NVDA","AMD","INTC","QCOM","TXN","AVGO","CSCO","ANET","CRM","ORCL","NOW","ADBE","INTU","CDNS","SNPS","VEEV","WDAY","NET"],
    "Semiconductors":        ["NVDA","AMD","INTC","QCOM","TXN","AVGO","MU","AMAT","KLAC","LRCX","MRVL","SMCI","ARM","ONTO","ENTG","MPWR","ON","SWKS","WOLF","QRVO"],
    "AI & Growth":           ["NVDA","PLTR","SNOW","DDOG","CRWD","ZS","PANW","NET","MDB","IONQ","QUBT","RGTI","ARM","SMCI","META","MSFT","GOOGL","TSLA","AMZN","CRM"],
    "Financials":            ["JPM","BAC","WFC","GS","MS","C","BLK","SCHW","V","MA","PYPL","COIN","SPGI","MCO","ICE","CME","BX","KKR","PGR","ALL"],
    "Healthcare":            ["JNJ","UNH","PFE","MRK","ABBV","LLY","BMY","AMGN","GILD","REGN","MRNA","VRTX","ISRG","MDT","SYK","HCA","CVS","MCK","DXCM","PODD"],
    "Consumer Discretionary":["AMZN","TSLA","HD","LOW","TGT","COST","TJX","NKE","LULU","ROST","BKNG","ABNB","UBER","DHI","LEN","ORLY","AZO","DLTR","DG","RH"],
    "Consumer Staples":      ["WMT","PG","KO","PEP","MDLZ","MO","PM","CL","GIS","K","MKC","HRL","CAG","CHD","CLX","EL","KR","SYY","USFD","SFM"],
    "Energy":                ["XOM","CVX","COP","EOG","OXY","PSX","VLO","MPC","SLB","HAL","BKR","DVN","FANG","EQT","AR","KMI","WMB","ET","EPD","MPLX"],
    "Industrials":           ["BA","CAT","HON","GE","RTX","LMT","NOC","GD","ITW","EMR","FDX","UPS","FAST","URI","WAB","TDG","ROP","SAIA","ODFL","CARR"],
    "Materials":             ["LIN","APD","SHW","ECL","NEM","FCX","AA","NUE","STLD","VMC","MLM","DOW","DD","AMCR","BALL","CLF","X","RS","PKG","IP"],
    "Real Estate":           ["AMT","PLD","CCI","EQIX","DLR","PSA","SPG","O","VICI","EXR","WELL","VTR","BXP","KIM","REG","MAC","NNN","SLG","WP","DLR"],
    "Utilities":             ["NEE","DUK","SO","AEP","EXC","XEL","PPL","WEC","ES","EIX","ETR","FE","CNP","AES","CMS","NI","BKH","NWE","OGE","AVA"],
    "Communication":         ["GOOGL","META","NFLX","DIS","CMCSA","CHTR","VZ","T","TMUS","SPOT","SNAP","PINS","RDDT","WBD","OMC","IPG","LAMR","MTCH","IAC","FOXA"],
}
FED_SENSITIVE_SECTORS=["Financials","Real Estate","Utilities"]

@st.cache_data(ttl=600)
def fetch_sector_rotation(sector_stocks):
    """Humanized fetch — small batches + variable delay, pakai _YF_SESSION."""
    results = []
    tickers = sector_stocks[:10]
    batches = _random_chunks(tickers, min_sz=3, max_sz=6)
    n_b = len(batches)
    for bi, batch in enumerate(batches):
        if not batch: continue
        try:
            raw = yf.download(list(batch), period="5d", interval="1d",
                              group_by="ticker", progress=False,
                              threads=False, auto_adjust=True, session=_YF_SESSION)
            for t in batch:
                try:
                    df = _yf_extract(raw, t, len(batch))
                    if df is None or len(df) < 2: continue
                    close = float(df["Close"].iloc[-1]); prev = float(df["Close"].iloc[-2])
                    chg = (close - prev) / prev * 100
                    vol = float(df["Volume"].iloc[-1])
                    avg_v = float(df["Volume"].mean())
                    rvol = vol / avg_v if avg_v > 0 else 1.0
                    results.append({"ticker": t, "close": close, "chg": chg, "rvol": round(rvol, 2)})
                except: pass
        except:
            # individual fallback
            for t in batch:
                try:
                    raw_s = yf.download(t, period="5d", interval="1d",
                                        progress=False, auto_adjust=True,
                                        threads=False, session=_YF_SESSION)
                    df = _yf_extract(raw_s, t, 1)
                    if df is None or len(df) < 2: continue
                    close = float(df["Close"].iloc[-1]); prev = float(df["Close"].iloc[-2])
                    chg = (close - prev) / prev * 100
                    vol = float(df["Volume"].iloc[-1])
                    avg_v = float(df["Volume"].mean())
                    rvol = vol / avg_v if avg_v > 0 else 1.0
                    results.append({"ticker": t, "close": close, "chg": chg, "rvol": round(rvol, 2)})
                except: pass
                time.sleep(random.uniform(0.3, 0.8))
        _human_sleep(bi, n_b)
    return results

@st.cache_data(ttl=300)
def scan_gap_up(tickers, min_gap_pct=0.5):
    results=[]
    batches=_random_chunks(list(tickers),min_sz=8,max_sz=20)
    n_b=len(batches)
    for bi,batch in enumerate(batches):
        try:
            raw=yf.download(list(batch),period="5d",interval="1d",group_by="ticker",progress=False,threads=False,auto_adjust=True)
            for t in batch:
                try:
                    df=_yf_extract(raw,t,len(batch))
                    if df is None or len(df)<3: continue
                    today=df.iloc[-1]; prev=df.iloc[-2]
                    close=float(today["Close"]); high_t=float(today["High"]); low_t=float(today["Low"])
                    high_p=float(prev["High"]); vol=float(today["Volume"])
                    avg_vol=float(df["Volume"].mean()); rvol=vol/avg_vol if avg_vol>0 else 1.0
                    gap_score=0; reasons=[]
                    if close>high_p:
                        gap_pct=(close-high_p)/high_p*100; gap_score+=3; reasons.append(f"Gap {gap_pct:.1f}% above prev High ✦✦")
                    cr=(close-low_t)/max(high_t-low_t,0.01)
                    if cr>0.85:   gap_score+=2; reasons.append(f"Closed near HOD {cr:.0%}")
                    elif cr>0.70: gap_score+=1; reasons.append(f"Strong close {cr:.0%}")
                    if rvol>3.0:   gap_score+=2; reasons.append(f"RVOL={rvol:.1f}x SURGE 🔥")
                    elif rvol>2.0: gap_score+=1; reasons.append(f"RVOL={rvol:.1f}x")
                    elif rvol>1.5: gap_score+=0.5
                    if len(df)>=3:
                        chg3=(close-float(df.iloc[-3]["Close"]))/float(df.iloc[-3]["Close"])*100
                        if chg3>3: gap_score+=1; reasons.append(f"3D ROC +{chg3:.1f}%")
                        elif chg3>1: gap_score+=0.5
                    if gap_score<3: continue
                    chg_today=(close-float(prev["Close"]))/float(prev["Close"])*100
                    results.append({"Ticker":t,"Price":round(close,2),"Gap Score":round(gap_score,1),
                                    "Chg %":round(chg_today,2),"Close Ratio":round(cr,2),
                                    "RVOL":round(rvol,2),"Prev High":round(high_p,2),
                                    "Signal":"GAP UP 🚀" if gap_score>=4 else "POTENTIAL ⚡",
                                    "Reasons":" · ".join(reasons[:3])})
                except: pass
        except: pass
        _human_sleep(bi,n_b)
    return sorted(results,key=lambda x:x["Gap Score"],reverse=True)

def calc_trailing_stop(entry,current,atr,method="ATR",atr_mult=2.0,pct=3.0):
    if method=="ATR":      trail_dist=atr*atr_mult; stop_price=current-trail_dist
    elif method=="Persen": trail_dist=current*(pct/100); stop_price=current*(1-pct/100)
    else:                  trail_dist=atr*1.5; stop_price=current-trail_dist
    profit_pct=(current-entry)/entry*100
    locked_pct=(stop_price-entry)/entry*100 if stop_price>entry else 0
    return {"stop":round(stop_price,2),"distance":round(trail_dist,2),
            "profit_float":round(profit_pct,2),"profit_locked":round(locked_pct,2),
            "is_profitable":stop_price>entry}

# ════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════
regime,spx_price,ema20,ema55,regime_detail,spx_chg,vix_val=get_market_regime()
rcfg=get_regime_config(regime); rcolor=rcfg["color"]
chg_col="#00ff88" if spx_chg>=0 else "#ff3d5a"; chg_sym="▲" if spx_chg>=0 else "▼"
vix_col="#ff3d5a" if vix_val>30 else("#ffb700" if vix_val>20 else "#00ff88")
vix_lbl="⚠️ FEAR" if vix_val>30 else("😐 CAUTION" if vix_val>20 else "🧊 CALM")
now_et=datetime.now(ny_tz)
# ── Live USD/IDR rate ──
_idr_rate, _idr_src = get_usd_idr()

st.markdown(f"""
<div class="tt-header">
  <div>
    <div class="tt-logo">🦅 US TURBO</div>
    <div class="tt-sub">Intraday 15M · Auto Regime · Bagger · v1.1 · Harga dalam IDR</div>
  </div>
  <div class="live-badge"><div class="live-dot"></div>LIVE {now_et.strftime("%H:%M:%S")} ET</div>
</div>""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background:rgba(0,0,0,.4);border:1px solid {rcolor}44;border-radius:8px;
     padding:12px 16px;margin-bottom:14px;border-left:4px solid {rcolor};">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
    <div>
      <div style="font-family:Space Mono,monospace;font-size:12px;font-weight:700;color:{rcolor};letter-spacing:1px;">{rcfg["label"]}</div>
      <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-top:3px;">{rcfg["desc"]}</div>
    </div>
    <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
      <div style="text-align:center;">
        <div style="font-family:Space Mono,monospace;font-size:18px;font-weight:700;color:{rcolor};">
          {spx_price:,.0f} <span style="font-size:11px;color:{chg_col}">{chg_sym}{abs(spx_chg):.2f}%</span>
        </div>
        <div style="font-size:9px;color:#4a5568;">SPX · EMA20 {ema20:,.0f} · EMA55 {ema55:,.0f}</div>
      </div>
      <div style="text-align:center;padding:6px 12px;background:rgba(0,0,0,.3);border-radius:6px;border:1px solid {vix_col}44;">
        <div style="font-family:Space Mono,monospace;font-size:16px;font-weight:700;color:{vix_col};">{vix_val:.1f}</div>
        <div style="font-size:9px;color:{vix_col};">VIX {vix_lbl}</div>
      </div>
      <div style="text-align:center;padding:6px 12px;background:rgba(0,229,255,.05);border-radius:6px;border:1px solid rgba(0,229,255,.3);">
        <div style="font-family:Space Mono,monospace;font-size:14px;font-weight:700;color:#00e5ff;">Rp{_idr_rate:,.0f}</div>
        <div style="font-size:9px;color:#4a5568;">USD/IDR · {_idr_src}</div>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════
tab_scanner,tab_watchlist,tab_overnight,tab_sector,tab_gapup,tab_trail,tab_backtest=st.tabs(
    ["🦅 Scanner","👁️ Watchlist","🌙 Overnight","🏭 Sectors","📈 Gap Up","🎯 Trailing Stop","📊 Backtest"])

# ════════════════════════════════════════════════════
#  TAB 1: SCANNER
# ════════════════════════════════════════════════════
with tab_scanner:
    with st.expander("⚙️  Scanner Settings", expanded=False):
        sc1,sc2,sc3=st.columns(3)
        with sc1:
            st.markdown('<div class="settings-label">SIGNAL MODE</div>',unsafe_allow_html=True)
            auto_regime=st.toggle("🤖 Auto-Mode (Market Regime)",value=True,key="auto_reg")
            if auto_regime:
                scan_mode=rcfg["mode"]
                st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:10px;padding:6px 10px;background:rgba(0,0,0,.3);border-radius:4px;color:{rcolor};">Auto: {scan_mode}</div>',unsafe_allow_html=True)
            else:
                scan_mode=st.radio("Mode",["Scalping ⚡","Momentum 🚀","Reversal 🎯","Bagger 💎"],label_visibility="collapsed",key="scan_mode_radio")
            tele_on=st.toggle("📡 Telegram Alert",value=True,key="tele_on")
        with sc2:
            st.markdown('<div class="settings-label">FILTER</div>',unsafe_allow_html=True)
            auto_thresh=st.toggle("🤖 Auto-Threshold",value=True,key="auto_thr")
            if auto_thresh:
                min_score=rcfg["min_score"]; vol_thresh=rcfg["min_rvol"]
                st.caption(f"Auto: Score≥{min_score} · RVOL≥{vol_thresh}x")
            else:
                min_score=st.slider("Min Score (0-6)",0,6,4,key="msc")
                vol_thresh=st.slider("Min RVOL",1.0,5.0,1.5,0.1,key="vol")
            min_turn=st.number_input("Min Turnover ($M USD)",value=10,step=5,key="trn")*1_000_000
        with sc3:
            st.markdown('<div class="settings-label">DISPLAY</div>',unsafe_allow_html=True)
            view_mode=st.radio("View",["Card View 🃏","Table View 📊"],label_visibility="collapsed",key="view_mode")
            scan_size=st.radio("Scan Size",["100 ⚡","200 🔥","Full 🦅"],index=1,horizontal=True,key="scan_size_radio")
            st.caption(f"🎯 Regime: {regime} · VIX: {vix_val:.1f} {vix_lbl}")
            st.caption(f"📊 {len(raw_stocks)} stocks available · Default: 200")

    do_scan=st.button("🦅 START SCAN NOW",type="primary",use_container_width=True,key="btn_scan")
    _now_check=datetime.now(ny_tz).timestamp(); auto_triggered=False
    if st.session_state.last_scan_time and not do_scan:
        if _now_check-st.session_state.last_scan_time>=300 and st.session_state.scan_results:
            do_scan=True; auto_triggered=True

    if do_scan:
        _sz=st.session_state.get("scan_size_radio","200 🔥")
        if "100" in _sz:   scan_list=stocks_yf[:100]
        elif "200" in _sz: scan_list=stocks_yf[:200]
        else:              scan_list=stocks_yf
        prog_ph=st.empty()
        label="🔄 AUTO-REFRESH" if auto_triggered else "🦅 SCANNING"
        prog_ph.markdown(f'<div style="color:#00e5ff;font-family:Space Mono,monospace;font-size:12px;">{label} {len(scan_list)} stocks ({scan_mode})...</div>',unsafe_allow_html=True)
        pb=st.progress(0)
        try:
            data_dict=fetch_intraday(tuple(scan_list))
            st.session_state.data_dict=data_dict
            results=[]; tickers=list(data_dict.keys())
            for i,ticker in enumerate(tickers):
                pb.progress((i+1)/max(len(tickers),1))
                try:
                    df=data_dict[ticker].copy()
                    if len(df)<30: continue
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
                    atr=float(r['ATR']) if not np.isnan(float(r['ATR'])) else close*0.01
                    slm=rcfg.get("sl_mult",0.8)
                    if scan_mode=="Scalping ⚡":   tp=close+1.5*atr; sl=close-slm*atr
                    elif scan_mode=="Momentum 🚀": tp=close+2.0*atr; sl=close-slm*atr
                    elif scan_mode=="Bagger 💎":   tp=close+3.0*atr; sl=close-1.0*atr
                    else:                          tp=close+2.5*atr; sl=close-slm*atr
                    rr=(tp-close)/max(close-sl,0.01)
                    e9=float(r['EMA9']); e21=float(r['EMA21']); e50=float(r['EMA50'])
                    trend="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else"◆ SIDE")
                    # Convert to IDR
                    _r = _idr_rate
                    price_idr = int(close * _r)
                    tp_idr    = int(tp * _r)
                    sl_idr    = int(sl * _r)
                    turn_idr  = turnover * _r
                    results.append({
                        "Ticker":stock_map[ticker],
                        "Price(USD)":round(close,2),
                        "Price(IDR)":price_idr,
                        "Price_fmt":usd_to_idr(close,_r),
                        "Score":sc,"Signal":sig,"Trend":trend,
                        "RSI-EMA":round(float(r['RSI_EMA']),1),"Stoch K":round(float(r['STOCH_K']),1),
                        "Stoch D":round(float(r['STOCH_D']),1),"MACD Hist":round(float(r['MACD_Hist']),4),
                        "RVOL":round(rvol,2),"BB%":round(float(r['BB_pct']),2),
                        "ROC 3B%":round(float(r['ROC3'])*100,2),"VWAP_IDR":int(float(r['VWAP'])*_r),
                        "TP_USD":round(tp,2),"SL_USD":round(sl,2),
                        "TP_IDR":tp_idr,"SL_IDR":sl_idr,
                        "TP_fmt":usd_to_idr(tp,_r),"SL_fmt":usd_to_idr(sl,_r),
                        "R:R":round(rr,1),
                        "Turnover(MRp)":round(turn_idr/1e6,1),
                        "Reasons":" · ".join(reasons),
                        "_class":get_card_class(sig)
                    })
                except: continue
            prog_ph.empty(); pb.empty()
            st.session_state.scan_results=results
            st.session_state.last_scan_time=datetime.now(ny_tz).timestamp()
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
            try: prog_ph.empty(); pb.empty()
            except: pass
            st.error(f"Scan error: {str(e)[:100]}")

    if st.session_state.last_scan_time:
        _now_cd=datetime.now(ny_tz).timestamp()
        _rem_cd=max(0,300-(_now_cd-st.session_state.last_scan_time))
        _last_cd=datetime.fromtimestamp(st.session_state.last_scan_time,ny_tz).strftime("%H:%M:%S")
        st.caption(f"⏱️ Next auto-scan: {int(_rem_cd//60):02d}:{int(_rem_cd%60):02d} · Last: {_last_cd} ET")

    results=st.session_state.scan_results
    if not results and not do_scan:
        st.markdown(f'<div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;"><div style="font-size:36px;margin-bottom:12px;">🦅</div><div style="font-size:13px;letter-spacing:2px;">CLICK SCAN TO START</div><div style="font-size:10px;margin-top:8px;color:#2d3748;">100 ⚡ / 200 🔥 / Full 🦅 · Regime: {regime} · VIX: {vix_val:.1f}</div></div>',unsafe_allow_html=True)
    elif results:
        df_out=pd.DataFrame(results).sort_values("Score",ascending=False).reset_index(drop=True)
        gacor=df_out[df_out["Signal"].str.contains("RIPPING|REVERSAL",na=False)]
        bagger=df_out[df_out["Signal"].str.contains("BAGGER|KANDIDAT",na=False)]
        potensi=df_out[df_out["Signal"].str.contains("POTENSIAL",na=False)]
        avg_rsi=df_out['RSI-EMA'].mean()

        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-card" style="border-top-color:{rcolor}"><div class="metric-label">Regime</div>
            <div class="metric-value" style="font-size:16px;color:{rcolor}">{regime}</div>
            <div class="metric-sub">SPX {spx_price:,.0f} {chg_sym}{abs(spx_chg):.2f}%</div></div>
          <div class="metric-card" style="border-top-color:{vix_col}"><div class="metric-label">VIX</div>
            <div class="metric-value" style="font-size:20px;color:{vix_col}">{vix_val:.1f}</div>
            <div class="metric-sub">{vix_lbl}</div></div>
          <div class="metric-card" style="border-top-color:#00e5ff"><div class="metric-label">USD/IDR</div>
            <div class="metric-value" style="font-size:16px;color:#00e5ff">Rp{_idr_rate:,.0f}</div>
            <div class="metric-sub">{_idr_src}</div></div>
          <div class="metric-card green"><div class="metric-label">Signals</div>
            <div class="metric-value">{len(df_out)}</div><div class="metric-sub">of {len(raw_stocks)} stocks</div></div>
          <div class="metric-card purple"><div class="metric-label">BAGGER 💎</div>
            <div class="metric-value">{len(bagger)}</div></div>
          <div class="metric-card red"><div class="metric-label">RIPPING 🔥</div>
            <div class="metric-value">{len(gacor)}</div></div>
          <div class="metric-card amber"><div class="metric-label">POTENSIAL</div>
            <div class="metric-value">{len(potensi)}</div></div>
          <div class="metric-card"><div class="metric-label">Avg RSI-EMA</div>
            <div class="metric-value" style="color:{'#00ff88' if avg_rsi>50 else '#ffb700' if avg_rsi>35 else '#ff3d5a'}">{avg_rsi:.1f}</div></div>
        </div>""",unsafe_allow_html=True)

        th='<div class="tape-wrap"><div class="tape-inner">'
        for _,row in df_out.iterrows():
            roc=row['ROC 3B%']; is_bag="BAGGER" in row['Signal'] or "KANDIDAT" in row['Signal']
            cls='bagger' if is_bag else('up' if roc>0 else('down' if roc<0 else'flat'))
            sym='💎' if is_bag else('▲' if roc>0 else('▼' if roc<0 else'─'))
            price_d=row.get('Price_fmt',f"Rp{row.get('Price(IDR)',0):,}")
            th+=f'<span class="tape-item {cls}">{row["Ticker"]} {price_d} {sym}{abs(roc):.1f}% [{row["Signal"]}]</span>'
        th+=th.replace('tape-inner">',''); th+='</div></div>'
        st.markdown(th,unsafe_allow_html=True)

        if not bagger.empty:
            st.markdown(f'<div class="bagger-alert-box"><div class="bagger-title">💎 BAGGER ALERT · {len(bagger)} CANDIDATES · BREAKOUT + ACCUMULATION</div></div>',unsafe_allow_html=True)
        if not gacor.empty:
            st.markdown(f'<div class="alert-box"><div class="alert-title">🚨 RIPPING ALERT · {len(gacor)} STOCKS · {scan_mode}</div></div>',unsafe_allow_html=True)

        if view_mode=="Card View 🃏":
            st.markdown('<div class="section-title">Signal Cards</div>',unsafe_allow_html=True)
            card_html='<div class="signal-grid">'
            for _,row in df_out.head(20).iterrows():
                sc_int=int(row['Score']); is_bag="BAGGER" in row['Signal'] or "KANDIDAT" in row['Signal']
                bar_cls="filled-purple" if is_bag else "filled"
                bars=''.join([f'<div class="sc-bar {bar_cls if i<sc_int else "empty"}" style="width:28px"></div>' for i in range(6)])
                roc_c='#00ff88' if row['ROC 3B%']>0 else'#ff3d5a'
                te="📈" if "▲" in row['Trend'] else("📉" if "▼" in row['Trend'] else"➡️")
                sig_color='#bf5fff' if is_bag else('#00ff88' if sc_int>=5 else '#ffb700' if sc_int>=4 else '#00e5ff')
                p_fmt=row.get('Price_fmt',f"Rp{row.get('Price(IDR)',0):,}")
                tp_fmt=row.get('TP_fmt',f"Rp{row.get('TP_IDR',0):,}")
                sl_fmt=row.get('SL_fmt',f"Rp{row.get('SL_IDR',0):,}")
                card_html+=f"""<div class="signal-card {row['_class']}">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div><div class="sc-ticker">{row['Ticker']}</div>
                    <div class="sc-price" style="color:{roc_c}">{p_fmt} {te}</div>
                    <div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568">${row.get('Price(USD)',0):.2f} · Rp{_idr_rate:,.0f}/USD</div></div>
                    <div style="text-align:right;">
                      <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">SCORE</div>
                      <div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:{sig_color}">{row['Score']}</div>
                    </div>
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
                    <div class="sc-stat">TP <span style="color:#00ff88">{tp_fmt}</span></div>
                    <div class="sc-stat">SL <span style="color:#ff3d5a">{sl_fmt}</span></div>
                    <div class="sc-stat">R:R <span>{row['R:R']}</span></div>
                  </div>
                  <div style="margin-top:8px;font-size:10px;color:#4a5568;line-height:1.4;font-family:Space Mono,monospace;">{row['Reasons'][:80]}</div>
                </div>"""
            card_html+='</div>'
            st.markdown(card_html,unsafe_allow_html=True)

        st.markdown('<div class="section-title">Full Signal Table</div>',unsafe_allow_html=True)
        display_cols=["Ticker","Price_fmt","Price(USD)","Score","Signal","Trend","RSI-EMA","Stoch K","Stoch D","MACD Hist","RVOL","BB%","ROC 3B%","VWAP_IDR","TP_fmt","SL_fmt","TP_USD","SL_USD","R:R","Turnover(MRp)","Reasons"]
        display_cols=[c for c in display_cols if c in df_out.columns]
        st.dataframe(df_out[display_cols],width='stretch',hide_index=True,column_config={
            "Score":          st.column_config.ProgressColumn("Score",min_value=0,max_value=6,format="%.1f"),
            "Price_fmt":      st.column_config.TextColumn("Harga (IDR)"),
            "Price(USD)":     st.column_config.NumberColumn("USD",format="$%.2f"),
            "TP_fmt":         st.column_config.TextColumn("TP (IDR)"),
            "SL_fmt":         st.column_config.TextColumn("SL (IDR)"),
            "TP_USD":         st.column_config.NumberColumn("TP (USD)",format="$%.2f"),
            "SL_USD":         st.column_config.NumberColumn("SL (USD)",format="$%.2f"),
            "VWAP_IDR":       st.column_config.NumberColumn("VWAP (IDR)",format="Rp%d"),
            "RVOL":           st.column_config.NumberColumn("RVOL",format="%.1fx"),
            "ROC 3B%":        st.column_config.NumberColumn("ROC 3B%",format="%.2f%%"),
            "Turnover(MRp)":  st.column_config.NumberColumn("Turnover (MRp)",format="Rp%.0fM"),
        })

# ════════════════════════════════════════════════════
#  TAB 2: WATCHLIST
# ════════════════════════════════════════════════════
with tab_watchlist:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:12px;padding:10px 14px;background:#0d1117;border-radius:6px;border-left:3px solid #00e5ff;">Deep analysis per stock. MTF + Pivot levels.</div>',unsafe_allow_html=True)
    wc1,wc2,wc3=st.columns([3,1,1])
    with wc1:
        wl_input=st.text_area("Tickers",placeholder="Example:\nAAPL\nNVDA, TSLA, MSFT",height=120,label_visibility="collapsed",key="wl_input")
    with wc2:
        wl_mode=st.radio("Mode",["Scalping ⚡","Momentum 🚀","Reversal 🎯","Bagger 💎"],key="wl_mode")
        st.caption(f"Regime suggest: {rcfg['mode']}")
    with wc3:
        st.markdown("<br>",unsafe_allow_html=True)
        wl_run=st.button("🔍 Analyze",use_container_width=True,key="wl_run")
        wl_tele=st.button("📡 Send Telegram",use_container_width=True,key="wl_tele")
    if wl_run and wl_input.strip():
        raw_wl=list(dict.fromkeys([t.strip().upper() for line in wl_input.split("\n") for t in line.split(",") if t.strip()]))
        if raw_wl:
            with st.spinner(f"Analyzing {len(raw_wl)} stocks..."):
                wl_res=[]
                for t in raw_wl:
                    df=None
                    try:
                        raw=yf.download(t,period="7d",interval="15m",progress=False,auto_adjust=True,threads=False)
                        df=_yf_extract(raw,t,1)
                    except: pass
                    if df is None or len(df)<30:
                        wl_res.append({"Ticker":t,"Price":0,"Score":0,"Signal":"No data","Trend":"-","RSI-EMA":0,"Stoch K":0,"RVOL":0,"BB%":0,"ROC 3B%":0,"VWAP":0,"TP":0,"SL":0,"R:R":0,"ATR":0,"Reasons":"No data","_class":"","MACD Hist":0,"MTF Align":"-","M15":0,"H1":0,"D1":0,"Pivot Pos":"-","PP":0,"R1":0,"S1":0}); continue
                    try:
                        df2=apply_intraday_indicators(df.copy())
                        r=df2.iloc[-1]; p=df2.iloc[-2]; p2=df2.iloc[-3] if len(df2)>=3 else p
                        close=float(r['Close']); atr=float(r['ATR']) if not np.isnan(float(r['ATR'])) else close*0.01
                        slm=rcfg.get("sl_mult",0.8)
                        if wl_mode=="Scalping ⚡":   sc,reasons,_=score_scalping(r,p,p2);  tp=close+1.5*atr; sl=close-slm*atr
                        elif wl_mode=="Momentum 🚀": sc,reasons,_=score_momentum(r,p,p2);  tp=close+2.0*atr; sl=close-slm*atr
                        elif wl_mode=="Bagger 💎":   sc,reasons,_=score_bagger(r,p,p2,df2);tp=close+3.0*atr; sl=close-1.0*atr
                        else:                        sc,reasons,_=score_reversal(r,p,p2);  tp=close+2.5*atr; sl=close-slm*atr
                        sig=get_signal(sc,wl_mode); rr=(tp-close)/max(close-sl,0.01)
                        e9=float(r['EMA9']); e21=float(r['EMA21']); e50=float(r['EMA50'])
                        trend="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else"◆ SIDE")
                        _pvt=fetch_pivot_data(t)
                        _pvt_pos=get_pivot_position(close,_pvt)[0] if _pvt else "-"
                        _mtf=score_mtf(t,wl_mode); _align,_ac,_avg=mtf_alignment(_mtf)
                        _r=_idr_rate
                        wl_res.append({"Ticker":t,
                            "Price(USD)":round(close,2),"Price(IDR)":int(close*_r),
                            "Price_fmt":usd_to_idr(close,_r),
                            "Score":sc,"Signal":sig,"Trend":trend,
                            "RSI-EMA":round(float(r['RSI_EMA']),1),"Stoch K":round(float(r['STOCH_K']),1),
                            "RVOL":round(float(r['RVOL']),2),"BB%":round(float(r['BB_pct']),2),
                            "ROC 3B%":round(float(r['ROC3'])*100,2),
                            "VWAP_IDR":int(float(r['VWAP'])*_r),
                            "TP_fmt":usd_to_idr(tp,_r),"SL_fmt":usd_to_idr(sl,_r),
                            "TP_USD":round(tp,2),"SL_USD":round(sl,2),
                            "TP_IDR":int(tp*_r),"SL_IDR":int(sl*_r),
                            "R:R":round(rr,1),"ATR_IDR":int(atr*_r),
                            "MACD Hist":round(float(r['MACD_Hist']),4),"Reasons":" · ".join(reasons),
                            "_class":get_card_class(sig),"MTF Align":_align,
                            "M15":_mtf.get("M15",0),"H1":_mtf.get("H1",0),"D1":_mtf.get("D1",0),
                            "Pivot Pos":_pvt_pos,
                            "PP":usd_to_idr(_pvt["PP"],_r) if _pvt else "—",
                            "R1":usd_to_idr(_pvt["R1"],_r) if _pvt else "—",
                            "S1":usd_to_idr(_pvt["S1"],_r) if _pvt else "—"})
                    except ex:
                        wl_res.append({"Ticker":t,"Price":0,"Score":0,"Signal":f"Err","Trend":"-","RSI-EMA":0,"Stoch K":0,"RVOL":0,"BB%":0,"ROC 3B%":0,"VWAP":0,"TP":0,"SL":0,"R:R":0,"ATR":0,"Reasons":"","_class":"","MACD Hist":0,"MTF Align":"-","M15":0,"H1":0,"D1":0,"Pivot Pos":"-","PP":0,"R1":0,"S1":0})
            st.session_state.wl_results=wl_res; st.session_state.wl_mode_used=wl_mode
    if wl_tele and st.session_state.wl_results:
        to_send=[r for r in st.session_state.wl_results if r["Price"]>0]
        if to_send: send_telegram(to_send[:5],source="Watchlist"); st.success("📡 Sent!")
    if st.session_state.wl_results:
        ok=[r for r in st.session_state.wl_results if r["Score"]>0]
        bag=[r for r in ok if any(k in r.get("Signal","") for k in ["BAGGER","KANDIDAT"])]
        gcr=[r for r in ok if any(k in r.get("Signal","") for k in ["RIPPING","REVERSAL"])]
        pot=[r for r in ok if "POTENSIAL" in r.get("Signal","")]
        st.markdown(f"""<div class="metric-row" style="margin-top:16px;">
          <div class="metric-card orange"><div class="metric-label">Analyzed</div><div class="metric-value">{len(st.session_state.wl_results)}</div></div>
          <div class="metric-card purple"><div class="metric-label">BAGGER 💎</div><div class="metric-value">{len(bag)}</div></div>
          <div class="metric-card green"><div class="metric-label">RIPPING 🔥</div><div class="metric-value">{len(gcr)}</div></div>
          <div class="metric-card amber"><div class="metric-label">POTENSIAL</div><div class="metric-value">{len(pot)}</div></div>
          <div class="metric-card"><div class="metric-label">Data OK</div><div class="metric-value">{len(ok)}</div></div>
        </div>""",unsafe_allow_html=True)
        ch='<div class="signal-grid">'
        for row in sorted(st.session_state.wl_results,key=lambda x:x["Score"],reverse=True):
            if row["Price"]==0:
                ch+=f'<div class="signal-card"><div class="sc-ticker">{row["Ticker"]}</div><div style="font-size:11px;color:#4a5568;margin-top:6px;">{row.get("Signal","No data")}</div></div>'
                continue
            sc_int=int(row["Score"]); is_bag="BAGGER" in row.get("Signal","") or "KANDIDAT" in row.get("Signal","")
            bar_cls="filled-purple" if is_bag else "filled"
            bars=''.join([f'<div class="sc-bar {bar_cls if i<sc_int else "empty"}" style="width:26px"></div>' for i in range(6)])
            sig=row.get("Signal","-")
            sc_col="#bf5fff" if is_bag else("#00ff88" if("RIPPING" in sig or "REVERSAL" in sig) else("#ffb700" if "POTENSIAL" in sig else "#00e5ff" if "WATCH" in sig else "#4a5568"))
            rsi_v=row["RSI-EMA"]; rsi_c="#ff3d5a" if rsi_v<30 else("#ffb700" if rsi_v<45 else "#00ff88" if rsi_v>60 else "#c9d1d9")
            roc_c="#00ff88" if row.get("ROC 3B%",0)>0 else "#ff3d5a"
            te="📈" if "▲" in row["Trend"] else("📉" if "▼" in row["Trend"] else "➡️")
            p_fmt=row.get('Price_fmt',f"Rp{row.get('Price(IDR)',0):,}")
            tp_fmt=row.get('TP_fmt',f"Rp{row.get('TP_IDR',0):,}")
            sl_fmt=row.get('SL_fmt',f"Rp{row.get('SL_IDR',0):,}")
            ch+=f"""<div class="signal-card {row['_class']}">
              <div style="display:flex;justify-content:space-between;">
                <div><div class="sc-ticker">{row['Ticker']}</div>
                <div class="sc-price" style="color:{roc_c}">{p_fmt} {te}</div>
                <div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568">${row.get('Price(USD)',0):.2f}</div></div>
                <div style="text-align:right"><div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568">SCORE</div>
                <div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:{sc_col}">{row['Score']}</div></div>
              </div>
              <div class="sc-signal" style="color:{sc_col}">{sig}</div>
              <div class="sc-bars">{bars}</div>
              <div class="sc-stats">
                <div class="sc-stat">RSI-EMA <span style="color:{rsi_c}">{rsi_v}</span></div>
                <div class="sc-stat">RVOL <span>{row['RVOL']}x</span></div>
                <div class="sc-stat">TP <span style="color:#00ff88">{tp_fmt}</span></div>
                <div class="sc-stat">SL <span style="color:#ff3d5a">{sl_fmt}</span></div>
              </div>
              <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;">
                <div style="font-family:Space Mono,monospace;font-size:9px;padding:2px 7px;border-radius:10px;background:rgba(0,0,0,.3);color:#4a5568;">📍 {row.get('Pivot Pos','-')}</div>
                <div style="font-family:Space Mono,monospace;font-size:9px;padding:2px 7px;border-radius:10px;background:rgba(0,0,0,.3);color:#4a5568;">MTF: {row.get('MTF Align','-')}</div>
              </div>
              <div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568;margin-top:4px;">M15:{row.get('M15',0)} · H1:{row.get('H1',0)} · D1:{row.get('D1',0)} | PP:{row.get('PP','—')} · R1:{row.get('R1','—')} · S1:{row.get('S1','—')}</div>
              <div style="margin-top:8px;font-size:10px;color:#4a5568;line-height:1.5;font-family:Space Mono,monospace">{row['Reasons'][:80]}</div>
            </div>"""
        ch+='</div>'
        st.markdown(ch,unsafe_allow_html=True)
    elif not wl_run:
        st.markdown('<div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;"><div style="font-size:32px;margin-bottom:12px;">👁️</div><div>ENTER TICKERS ABOVE</div></div>',unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  TAB 3: OVERNIGHT PLAY
# ════════════════════════════════════════════════════
with tab_overnight:
    now_et2=datetime.now(ny_tz)
    is_ph_time=(now_et2.hour==15 and now_et2.minute>=0) or (now_et2.hour==15 and now_et2.minute<=59)
    is_open_time=(now_et2.hour==9 and now_et2.minute>=30) or (10<=now_et2.hour<10 and now_et2.minute<=30)
    st.markdown(f"""
    <div style="background:rgba(0,229,255,.05);border:1px solid rgba(0,229,255,.3);border-radius:8px;padding:14px 18px;margin-bottom:16px;">
      <div style="font-family:Space Mono,monospace;font-size:13px;font-weight:700;color:#00e5ff;letter-spacing:1px;">🌙 OVERNIGHT PLAY — Power Hour Entry</div>
      <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-top:4px;">
        Entry: <span style="color:#ffb700">3:00 PM – 3:59 PM ET (Power Hour)</span> &nbsp;·&nbsp;
        Exit: <span style="color:#00ff88">Next day 9:30 AM – 10:30 AM ET</span> &nbsp;·&nbsp;
        Status: <span style="color:{'#00ff88' if is_ph_time else '#ffb700' if is_open_time else '#4a5568'}">
          {'🟢 POWER HOUR — Entry window!' if is_ph_time else '🟡 OPEN — Exit window!' if is_open_time else f'⏳ Next Power Hour 3:00 PM ET · Now: {now_et2.strftime("%H:%M")} ET'}
        </span>
      </div>
    </div>""",unsafe_allow_html=True)
    on_c1,on_c2=st.columns([2,1])
    with on_c1:
        on_min_score=st.slider("Min Overnight Score",0,6,4,key="on_score")
        on_min_rvol=st.slider("Min RVOL",1.0,5.0,1.5,0.1,key="on_rvol")
    with on_c2:
        on_min_turn=st.number_input("Min Turnover ($M)",value=10,step=5,key="on_turn")*1_000_000
        on_tele=st.toggle("📡 Telegram Alert",value=True,key="on_tele")
    do_overnight=st.button("🌙 SCAN OVERNIGHT PLAYS",type="primary",use_container_width=True,key="btn_on")
    if "overnight_results" not in st.session_state: st.session_state.overnight_results=[]
    if do_overnight:
        on_prog=st.empty(); on_prog.info("🌙 Scanning overnight candidates...")
        on_res=[]; scan_data=st.session_state.get("data_dict",{})
        if not scan_data:
            try: scan_data=fetch_intraday(tuple(stocks_yf[:200]))
            except: pass
        pb_on=st.progress(0); tickers_on=list(scan_data.keys())
        for i,ticker in enumerate(tickers_on):
            pb_on.progress((i+1)/max(len(tickers_on),1))
            try:
                df=scan_data[ticker].copy()
                if len(df)<30: continue
                df_c=apply_intraday_indicators(df)
                # Only look at power hour bars (15:00-15:59 ET)
                df_ph=df_c
                try:
                    df_ph=df_c[df_c.index.hour==15] if len(df_c[df_c.index.hour==15])>0 else df_c
                except: pass
                if len(df_ph)<2: df_ph=df_c
                r=df_ph.iloc[-1]; p=df_ph.iloc[-2]; p2=df_ph.iloc[-3] if len(df_ph)>=3 else p
                close=float(r['Close']); vol=float(r['Volume'])
                turnover=close*vol; rvol=float(r['RVOL'])
                if turnover<on_min_turn or rvol<on_min_rvol: continue
                sc,reasons,_=score_overnight(r,p,p2)
                if sc<on_min_score: continue
                if sc>=5:   on_sig="STRONG BUY 🌙"
                elif sc>=4: on_sig="BUY ⚡"
                else:       on_sig="WATCH 👀"
                atr=float(r['ATR']); tp=close+2.5*atr; sl=close-1.2*atr; rr=(tp-close)/max(close-sl,0.01)
                e9=float(r['EMA9']); e21=float(r['EMA21']); e50=float(r['EMA50'])
                trend="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else"◆ SIDE")
                hi_lo=float(r["High"])-float(r["Low"]); close_pct=(float(r["Close"])-float(r["Low"]))/max(hi_lo,0.01)
                _r=_idr_rate
                on_res.append({
                    "Ticker":stock_map.get(ticker,ticker),
                    "Price(USD)":round(close,2),"Price_fmt":usd_to_idr(close,_r),
                    "Score":sc,"Signal":on_sig,"Trend":trend,
                    "RSI-EMA":round(float(r['RSI_EMA']),1),"Stoch K":round(float(r['STOCH_K']),1),
                    "RVOL":round(rvol,2),
                    "TP_fmt":usd_to_idr(tp,_r),"SL_fmt":usd_to_idr(sl,_r),
                    "TP_USD":round(tp,2),"SL_USD":round(sl,2),
                    "R:R":round(rr,1),
                    "Turnover(MRp)":round(turnover*_r/1e6,1),
                    "Close%":round(close_pct*100,1),
                    "Reasons":" · ".join(reasons),
                    "_class":"gacor" if sc>=5 else "potensial" if sc>=4 else "watch"
                })
            except: continue
        pb_on.empty(); on_prog.empty()
        on_res=sorted(on_res,key=lambda x:x["Score"],reverse=True)
        st.session_state.overnight_results=on_res
        if on_tele and on_res and TOKEN and CHAT_ID:
            now_on=datetime.now(ny_tz); sep="━"*28
            msg=(f"🌙 *US OVERNIGHT PLAY*\n⏰ `{now_on.strftime('%H:%M:%S')} ET`\n{sep}\n")
            for r in on_res[:5]:
                bar="█"*int(r['Score'])+"░"*(6-int(r['Score']))
                msg+=(f"\n🌙 *{r['Ticker']}* `{r['Signal']}`\n💰 {r.get('Price_fmt', f"${r.get('Price(USD)',0):.2f}")}\n"
                      f"📊 `[{bar}] {r['Score']}/6`\n📈 RSI: `{r['RSI-EMA']}` | RVOL: `{r['RVOL']}x`\n"
                      f"🎯 TP: `${r['TP']:.2f}` | SL: `${r['SL']:.2f}`\n💡 _{r['Reasons'][:50]}_\n")
            msg+=f"\n{sep}\n🌙 _Entry 3PM ET · Exit 9:30AM ET_\n⚠️ _NOT financial advice!_"
            try:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                              data={"chat_id":CHAT_ID,"text":msg,"parse_mode":"Markdown"},timeout=10)
            except: pass
    on_results=st.session_state.overnight_results
    if on_results:
        strong=[r for r in on_results if "STRONG" in r.get("Signal","")]
        buy=[r for r in on_results if r.get("Signal","")=="BUY ⚡"]
        st.markdown(f"""<div class="metric-row">
          <div class="metric-card" style="border-top-color:#00e5ff"><div class="metric-label">Candidates</div><div class="metric-value">{len(on_results)}</div></div>
          <div class="metric-card green"><div class="metric-label">Strong Buy 🌙</div><div class="metric-value">{len(strong)}</div></div>
          <div class="metric-card amber"><div class="metric-label">Buy ⚡</div><div class="metric-value">{len(buy)}</div></div>
          <div class="metric-card"><div class="metric-label">Entry</div><div class="metric-value" style="font-size:13px;color:#ffb700">3:00 PM</div></div>
          <div class="metric-card"><div class="metric-label">Exit</div><div class="metric-value" style="font-size:13px;color:#00ff88">9:30 AM</div></div>
        </div>""",unsafe_allow_html=True)
        medals=["🥇","🥈","🥉"]; cols_top=st.columns(min(3,len(on_results)))
        for idx,col in enumerate(cols_top):
            if idx>=len(on_results): break
            row=on_results[idx]; sig_col="#00ff88" if "STRONG" in row["Signal"] else "#ffb700"
            with col:
                st.markdown(f"""<div style="background:#0d1117;border:1px solid {sig_col}44;border-radius:10px;padding:16px;text-align:center;border-top:3px solid {sig_col};">
                  <div style="font-size:24px">{medals[idx]}</div>
                  <div style="font-family:Space Mono,monospace;font-size:18px;font-weight:700;color:#e6edf3;">{row['Ticker']}</div>
                  <div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:{sig_col};">{row.get('Price_fmt',f"Rp{int(row.get('Price(USD)',0)*_idr_rate):,}")}</div>
                  <div style="font-size:9px;color:#4a5568;">${row.get('Price(USD)',0):.2f} · Score {row['Score']}</div>
                  <div style="font-size:11px;font-weight:700;color:{sig_col};margin-top:4px;">{row['Signal']}</div>
                  <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-top:6px;">RVOL {row['RVOL']}x · RSI {row['RSI-EMA']}<br>TP {row.get('TP_fmt','—')} · SL {row.get('SL_fmt','—')}</div>
                </div>""",unsafe_allow_html=True)
        df_on=pd.DataFrame(on_results)
        show_cols=["Ticker","Price_fmt","Price(USD)","Score","Signal","Trend","RSI-EMA","Stoch K","RVOL","TP_fmt","SL_fmt","TP_USD","SL_USD","R:R","Close%","Turnover(MRp)","Reasons"]
        show_cols=[c for c in show_cols if c in df_on.columns]
        st.dataframe(df_on[show_cols],width='stretch',hide_index=True,column_config={
            "Score":         st.column_config.ProgressColumn("Score",min_value=0,max_value=6,format="%.1f"),
            "Price_fmt":     st.column_config.TextColumn("Harga (IDR)"),
            "Price(USD)":    st.column_config.NumberColumn("USD",format="$%.2f"),
            "TP_fmt":        st.column_config.TextColumn("TP (IDR)"),
            "SL_fmt":        st.column_config.TextColumn("SL (IDR)"),
            "TP_USD":        st.column_config.NumberColumn("TP (USD)",format="$%.2f"),
            "SL_USD":        st.column_config.NumberColumn("SL (USD)",format="$%.2f"),
            "RVOL":          st.column_config.NumberColumn("RVOL",format="%.2fx"),
            "Turnover(MRp)": st.column_config.NumberColumn("Turnover (MRp)",format="Rp%.0fM"),
        })
    elif not do_overnight:
        st.markdown('<div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;"><div style="font-size:32px;margin-bottom:12px;">🌙</div><div>CLICK SCAN OVERNIGHT</div></div>',unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  TAB 4: SECTORS
# ════════════════════════════════════════════════════
with tab_sector:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:14px;padding:10px 14px;background:#0d1117;border-radius:6px;border-left:3px solid #00e5ff;">Track US sector rotation. FED-sensitive sectors highlighted.</div>',unsafe_allow_html=True)
    do_sector=st.button("🏭 REFRESH US SECTORS",type="primary",use_container_width=True,key="btn_sector")
    if do_sector:
        with st.spinner("Fetching US sector data..."):
            sec_data={}
            secs_list=list(SECTORS.items())
            n_secs=len(secs_list)
            for si,(sec_name,sec_stocks) in enumerate(secs_list):
                results=fetch_sector_rotation(sec_stocks)
                if results:
                    avg_chg=sum(r["chg"] for r in results)/len(results)
                    avg_rvol=sum(r["rvol"] for r in results)/len(results)
                    bullish=sum(1 for r in results if r["chg"]>0)
                    sec_data[sec_name]={"avg_chg":round(avg_chg,2),"avg_rvol":round(avg_rvol,2),
                                        "bullish":bullish,"total":len(results),"stocks":results,
                                        "is_fed":sec_name in FED_SENSITIVE_SECTORS}
                # Humanized inter-sector pause
                _human_sleep(si, n_secs)
            st.session_state.sector_data=sec_data
    if st.session_state.sector_data:
        sorted_secs=sorted(st.session_state.sector_data.items(),key=lambda x:x[1]["avg_chg"],reverse=True)
        cols_sec=st.columns(3)
        for idx,(sec_name,sec_info) in enumerate(sorted_secs):
            chg=sec_info["avg_chg"]; col="#00ff88" if chg>1 else("#ffb700" if chg>0 else "#ff3d5a")
            bg="rgba(0,255,136,.06)" if chg>1 else("rgba(255,183,0,.06)" if chg>0 else "rgba(255,61,90,.06)")
            bull_pct=int(sec_info["bullish"]/max(sec_info["total"],1)*100)
            fed_badge=' <span style="font-size:9px;color:#00e5ff">📊FED</span>' if sec_info.get("is_fed") else ""
            with cols_sec[idx%3]:
                st.markdown(f"""<div style="background:{bg};border:1px solid {col}44;border-radius:8px;padding:12px;margin-bottom:10px;">
                  <div style="font-family:Space Mono,monospace;font-size:10px;font-weight:700;color:#c9d1d9;">{sec_name}{fed_badge}</div>
                  <div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:{col};margin:4px 0;">{chg:+.2f}%</div>
                  <div style="font-size:9px;color:#4a5568;">RVOL avg: {sec_info['avg_rvol']:.1f}x · Bullish: {sec_info['bullish']}/{sec_info['total']} ({bull_pct}%)</div>
                  <div style="height:4px;background:#1c2533;border-radius:2px;margin-top:6px;overflow:hidden;">
                    <div style="width:{bull_pct}%;height:100%;background:{col};border-radius:2px;"></div>
                  </div>
                </div>""",unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;"><div style="font-size:32px;margin-bottom:12px;">🏭</div><div>CLICK REFRESH US SECTORS</div></div>',unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  TAB 5: GAP UP
# ════════════════════════════════════════════════════
with tab_gapup:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:14px;padding:10px 14px;background:#0d1117;border-radius:6px;border-left:3px solid #00ff88;">Detect US stocks likely to <b style="color:#00ff88">Gap Up</b> tomorrow open.</div>',unsafe_allow_html=True)
    gu_c1,gu_c2=st.columns(2)
    with gu_c1: gu_min_score=st.slider("Min Gap Score",1,6,3,key="gu_score")
    with gu_c2: gu_size=st.radio("Size",["100 ⚡","200 🔥","Full 🦅"],index=1,horizontal=True,key="gu_size")
    do_gapup=st.button("📈 SCAN GAP UP",type="primary",use_container_width=True,key="btn_gapup")
    if "gapup_results" not in st.session_state: st.session_state.gapup_results=[]
    if do_gapup:
        _gsz=st.session_state.get("gu_size","200 🔥")
        if "100" in _gsz:   scan_tickers=stocks_yf[:100]
        elif "200" in _gsz: scan_tickers=stocks_yf[:200]
        else:               scan_tickers=stocks_yf
        with st.spinner(f"Scanning {len(scan_tickers)} stocks..."):
            gu_res=scan_gap_up(scan_tickers)
            gu_res=[r for r in gu_res if r["Gap Score"]>=gu_min_score]
            st.session_state.gapup_results=gu_res
    gapup_res=st.session_state.gapup_results
    if gapup_res:
        gap_confirmed=[r for r in gapup_res if "GAP UP" in r.get("Signal","")]
        potential=[r for r in gapup_res if "POTENTIAL" in r.get("Signal","")]
        st.markdown(f"""<div class="metric-row">
          <div class="metric-card green"><div class="metric-label">Gap Confirmed 🚀</div><div class="metric-value">{len(gap_confirmed)}</div></div>
          <div class="metric-card amber"><div class="metric-label">Potential ⚡</div><div class="metric-value">{len(potential)}</div></div>
          <div class="metric-card"><div class="metric-label">Total</div><div class="metric-value">{len(gapup_res)}</div></div>
        </div>""",unsafe_allow_html=True)
        gu_html='<div class="signal-grid">'
        for row in gapup_res[:20]:
            sc_int=int(min(row["Gap Score"],6)); bars=''.join([f'<div class="sc-bar {"filled" if i<sc_int else "empty"}" style="width:26px"></div>' for i in range(6)])
            is_gap="GAP UP" in row.get("Signal",""); sc_col="#00ff88" if is_gap else "#ffb700"
            chg_c="#00ff88" if row["Chg %"]>0 else "#ff3d5a"
            gu_html+=f"""<div class="signal-card {'gacor' if is_gap else 'potensial'}">
              <div style="display:flex;justify-content:space-between;">
                <div><div class="sc-ticker">{row['Ticker']}</div>
                <div class="sc-price" style="color:{chg_c}">${row.get('Price',0):.2f} ({row['Chg %']:+.1f}%)</div></div>
                <div style="text-align:right"><div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568">GAP SCORE</div>
                <div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:{sc_col}">{row['Gap Score']}</div></div>
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
        st.markdown(gu_html,unsafe_allow_html=True)
        df_gu=pd.DataFrame(gapup_res)
        st.dataframe(df_gu,width='stretch',hide_index=True,column_config={
            "Gap Score":st.column_config.ProgressColumn("Gap Score",min_value=0,max_value=6,format="%.1f"),
            "Price":st.column_config.NumberColumn("Price",format="$%.2f"),
            "RVOL":st.column_config.NumberColumn("RVOL",format="%.2fx"),
            "Chg %":st.column_config.NumberColumn("Chg %",format="%.2f%%"),
        })
    elif not do_gapup:
        st.markdown('<div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;"><div style="font-size:32px;margin-bottom:12px;">📈</div><div>CLICK SCAN GAP UP</div></div>',unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  TAB 6: TRAILING STOP
# ════════════════════════════════════════════════════
with tab_trail:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:14px;padding:10px 14px;background:#0d1117;border-radius:6px;border-left:3px solid #bf5fff;">Lock profits. ATR 2x = scalp · ATR 3x = swing · % = fixed trail.</div>',unsafe_allow_html=True)
    tr_c1,tr_c2=st.columns(2)
    with tr_c1:
        st.markdown('<div class="settings-label">POSITION</div>',unsafe_allow_html=True)
        tr_ticker=st.text_input("Ticker (e.g. NVDA)",value="NVDA",key="tr_ticker").upper()
        tr_entry=st.number_input("Entry Price ($)",value=100.0,step=0.5,format="%.2f",key="tr_entry")
        tr_qty=st.number_input("Shares",value=100,step=10,key="tr_qty")
    with tr_c2:
        st.markdown('<div class="settings-label">TRAILING SETTINGS</div>',unsafe_allow_html=True)
        tr_method=st.radio("Method",["ATR","Persen","Swing Low"],key="tr_method")
        if tr_method=="ATR":      tr_atr_mult=st.slider("ATR Multiplier",1.0,5.0,2.0,0.5,key="tr_atr_m")
        elif tr_method=="Persen": tr_pct=st.slider("Trailing %",1.0,10.0,3.0,0.5,key="tr_pct")
        tr_alert=st.toggle("🔔 Telegram Alert",value=True,key="tr_alert")
    if st.button("🎯 CALCULATE TRAILING STOP",type="primary",use_container_width=True,key="btn_trail"):
        with st.spinner(f"Fetching {tr_ticker}..."):
            try:
                df_tr=None
                try:
                    raw_tr=yf.download(tr_ticker,period="7d",interval="15m",progress=False,auto_adjust=True,threads=False)
                    df_tr=_yf_extract(raw_tr,tr_ticker,1)
                except: pass
                if df_tr is not None and len(df_tr)>=20:
                    df_tr=apply_intraday_indicators(df_tr)
                    current=float(df_tr["Close"].iloc[-1]); atr_val=float(df_tr["ATR"].iloc[-1])
                    if tr_method=="ATR":      trail_result=calc_trailing_stop(tr_entry,current,atr_val,"ATR",tr_atr_mult)
                    elif tr_method=="Persen": trail_result=calc_trailing_stop(tr_entry,current,atr_val,"Persen",pct=tr_pct)
                    else:                     trail_result=calc_trailing_stop(tr_entry,current,atr_val,"Swing Low")
                    stop=trail_result["stop"]; dist=trail_result["distance"]
                    p_float=trail_result["profit_float"]; p_locked=trail_result["profit_locked"]
                    is_profit=trail_result["is_profitable"]
                    profit_usd=(current-tr_entry)*tr_qty; locked_usd=max(0,(stop-tr_entry)*tr_qty)
                    _r=_idr_rate
                    cur_idr=int(current*_r); stop_idr=int(stop*_r); atr_idr=int(atr_val*_r)
                    entry_idr=int(tr_entry*_r); profit_idr=int(profit_usd*_r); locked_idr=int(locked_usd*_r)
                    stop_col="#00ff88" if is_profit else "#ff3d5a"; profit_col="#00ff88" if profit_usd>=0 else "#ff3d5a"
                    st.markdown(f"""<div style="background:#0d1117;border:1px solid {stop_col}44;border-radius:10px;padding:20px;margin-top:12px;">
                      <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:12px;">
                        💱 Kurs: Rp{_r:,.0f}/USD ({_idr_src}) · Entry: ${tr_entry:.2f} = Rp{entry_idr:,}
                      </div>
                      <div class="metric-row">
                        <div class="metric-card"><div class="metric-label">Harga Sekarang</div>
                          <div class="metric-value" style="color:#00e5ff;font-size:18px;">Rp{cur_idr:,}</div>
                          <div class="metric-sub">${current:.2f} · ATR Rp{atr_idr:,}</div></div>
                        <div class="metric-card" style="border-top-color:{stop_col}">
                          <div class="metric-label">🎯 Trailing Stop</div>
                          <div class="metric-value" style="color:{stop_col};font-size:18px;">Rp{stop_idr:,}</div>
                          <div class="metric-sub">${stop:.2f} · Jarak Rp{int(dist*_r):,}</div></div>
                        <div class="metric-card" style="border-top-color:{profit_col}">
                          <div class="metric-label">Float P&L</div>
                          <div class="metric-value" style="color:{profit_col}">{p_float:+.1f}%</div>
                          <div class="metric-sub">Rp{profit_idr:+,} (${profit_usd:+,.2f})</div></div>
                        <div class="metric-card" style="border-top-color:#00ff88">
                          <div class="metric-label">Locked 🔒</div>
                          <div class="metric-value" style="color:#00ff88">{p_locked:+.1f}%</div>
                          <div class="metric-sub">Rp{locked_idr:+,} (${locked_usd:+,.2f})</div></div>
                      </div>
                      <div style="margin-top:12px;font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">
                        💼 {tr_qty} shares · {'✅ Profit locked!' if is_profit else '⚠️ Stop di bawah entry'}
                      </div>
                    </div>""",unsafe_allow_html=True)
                    if tr_alert and TOKEN and CHAT_ID:
                        now_tr=datetime.now(ny_tz)
                        msg_tr=(f"🎯 *TRAILING STOP UPDATE*\n⏰ `{now_tr.strftime('%H:%M:%S')} ET`\n{'━'*28}\n"
                                f"📌 *{tr_ticker}* | {tr_method}\n"
                                f"💰 Entry: `${tr_entry:.2f}` (Rp{entry_idr:,}) → Now: `${current:.2f}` (Rp{cur_idr:,})\n"
                                f"🎯 Stop: `Rp{stop_idr:,}` (${stop:.2f}) | Locked: `{p_locked:+.1f}%`\n"
                                f"📊 Float: `{p_float:+.1f}%` (Rp{profit_idr:+,})\n{'━'*28}\n⚠️ _NOT financial advice!_")
                        try:
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                          data={"chat_id":CHAT_ID,"text":msg_tr,"parse_mode":"Markdown"},timeout=10)
                            st.success("📡 Alert sent!")
                        except: pass
                else:
                    st.error(f"Data for {tr_ticker} unavailable. Try again.")
            except Exception as ex:
                st.error(f"Error: {str(ex)[:80]}")

# ════════════════════════════════════════════════════
#  TAB 7: BACKTEST
# ════════════════════════════════════════════════════
with tab_backtest:
    st.markdown('<div class="section-title">Backtest Engine · 15M Intraday · US Stocks</div>',unsafe_allow_html=True)
    bt_c1,bt_c2,bt_c3,bt_c4=st.columns(4)
    bt_mode=bt_c1.selectbox("Mode",["Scalping ⚡","Momentum 🚀","Reversal 🎯","Bagger 💎"],key="bt_mode")
    bt_sc=bt_c2.slider("Min Score",0,6,4,key="bt_sc")
    bt_fwd=int(bt_c3.number_input("Hold (bars)",value=4,step=1,min_value=1,max_value=20))
    bt_sl_mult=bt_c4.number_input("SL mult (xATR)",value=0.8,step=0.1,min_value=0.1,max_value=3.0)
    st.caption(f"Hold {bt_fwd} bars × 15 min = ~{bt_fwd*15} minutes per trade")
    if st.button("🚀 Run Backtest",type="primary",key="bt_run"):
        data_dict=st.session_state.get("data_dict",{})
        if not data_dict:
            st.warning("Run Scanner first!")
        else:
            bt_results=[]; bt_by_trend={"▲ UP":[],"▼ DOWN":[],"◆ SIDE":[]}
            bt_by_session={"Pre/Open 9:30-11":[],"Midday 11-14":[],"Power Hour 14-16":[]}
            bt_by_score={4:[],5:[],6:[]}
            bt_pb=st.progress(0); sample=list(data_dict.keys())[:80]
            for bi,ticker in enumerate(sample):
                bt_pb.progress((bi+1)/len(sample))
                try:
                    d=data_dict[ticker].copy()
                    if len(d)<60: continue
                    d=apply_intraday_indicators(d)
                    for ii in range(50,len(d)-bt_fwd):
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
                        for fwd_i in range(1,bt_fwd+1):
                            bar=d.iloc[ii+fwd_i]
                            if float(bar['High'])>=tp_p: exit_price=tp_p; break
                            if float(bar['Low'])<=sl_p:  exit_price=sl_p; break
                        ret=(exit_price-entry)/entry*100; bt_results.append(ret)
                        e9=float(r0['EMA9']); e21=float(r0['EMA21']); e50=float(r0['EMA50'])
                        tr="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else "◆ SIDE")
                        bt_by_trend[tr].append(ret)
                        try:
                            hr=d.index[ii].hour
                            if 9<=hr<11:  bt_by_session["Pre/Open 9:30-11"].append(ret)
                            elif 11<=hr<14: bt_by_session["Midday 11-14"].append(ret)
                            elif 14<=hr<16: bt_by_session["Power Hour 14-16"].append(ret)
                        except: pass
                        sc_int=int(sc)
                        if sc_int in bt_by_score: bt_by_score[sc_int].append(ret)
                except: continue
            bt_pb.empty()
            if not bt_results:
                st.warning("No matching trades. Lower Min Score.")
            else:
                arr=np.array(bt_results); wr=len(arr[arr>0])/len(arr)*100
                avg=np.mean(arr); med=np.median(arr)
                pf=arr[arr>0].sum()/max(abs(arr[arr<0].sum()),0.01)
                mxdd=arr[arr<0].min() if len(arr[arr<0])>0 else 0
                st.markdown(f"""<div class="bt-result">
                  <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;letter-spacing:2px;margin-bottom:14px;">{len(arr)} TRADES · SCORE≥{bt_sc} · HOLD {bt_fwd} BARS (~{bt_fwd*15}M) · {bt_mode}</div>
                  <div style="display:flex;flex-wrap:wrap;">
                    <span class="bt-metric"><div class="bt-metric-val" style="color:{'#00ff88' if wr>=55 else '#ffb700' if wr>=50 else '#ff3d5a'}">{wr:.1f}%</div><div class="bt-metric-lbl">Win Rate</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:{'#00ff88' if avg>0 else '#ff3d5a'}">{avg:+.2f}%</div><div class="bt-metric-lbl">Avg Return</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#00e5ff">{med:+.2f}%</div><div class="bt-metric-lbl">Median</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:{'#00ff88' if pf>=1.5 else '#ffb700' if pf>=1 else '#ff3d5a'}">{pf:.2f}x</div><div class="bt-metric-lbl">Profit Factor</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#ff3d5a">{mxdd:.1f}%</div><div class="bt-metric-lbl">Max Loss</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#00ff88">{sum(1 for x in bt_results if x>0)}</div><div class="bt-metric-lbl">TP Hits</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#ff3d5a">{sum(1 for x in bt_results if x<0)}</div><div class="bt-metric-lbl">SL Hits</div></span>
                  </div>
                </div>""",unsafe_allow_html=True)
                tab_tr,tab_ses,tab_sc2=st.tabs(["📈 By Trend","⏰ By Session","🎯 By Score"])
                with tab_tr:
                    for tr_name,vals in bt_by_trend.items():
                        if not vals: continue
                        a=np.array(vals); wr_t=len(a[a>0])/len(a)*100; avg_t=np.mean(a)
                        col="#00ff88" if wr_t>=55 else("#ffb700" if wr_t>=50 else "#ff3d5a")
                        st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;"><span style="font-family:Space Mono,monospace;font-size:12px;color:#c9d1d9;">{tr_name}</span><span style="font-family:Space Mono,monospace;font-size:11px;color:{col};">{wr_t:.1f}% WR · avg {avg_t:+.2f}% · {len(a)} trades</span></div><div style="height:8px;background:var(--border);border-radius:4px;overflow:hidden;margin-top:4px;"><div style="width:{int(wr_t)}%;height:100%;background:{col};border-radius:4px;"></div></div></div>',unsafe_allow_html=True)
                with tab_ses:
                    for sname,vals in bt_by_session.items():
                        if not vals: continue
                        a=np.array(vals); wr_s=len(a[a>0])/len(a)*100; avg_s=np.mean(a)
                        col="#00ff88" if wr_s>=55 else("#ffb700" if wr_s>=50 else "#ff3d5a")
                        st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;"><span style="font-family:Space Mono,monospace;font-size:12px;color:#c9d1d9;">⏰ {sname}</span><span style="font-family:Space Mono,monospace;font-size:11px;color:{col};">{wr_s:.1f}% WR · avg {avg_s:+.2f}% · {len(a)} trades</span></div><div style="height:8px;background:var(--border);border-radius:4px;overflow:hidden;margin-top:4px;"><div style="width:{int(wr_s)}%;height:100%;background:{col};border-radius:4px;"></div></div></div>',unsafe_allow_html=True)
                with tab_sc2:
                    for sc_lv in [4,5,6]:
                        vals=bt_by_score.get(sc_lv,[])
                        if not vals: continue
                        a=np.array(vals); wr_v=len(a[a>0])/len(a)*100; avg_v=np.mean(a)
                        col="#00ff88" if wr_v>=55 else("#ffb700" if wr_v>=50 else "#ff3d5a")
                        st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;"><span style="font-family:Space Mono,monospace;font-size:12px;color:#c9d1d9;">Score {sc_lv} [{"█"*sc_lv+"░"*(6-sc_lv)}]</span><span style="font-family:Space Mono,monospace;font-size:11px;color:{col};">{wr_v:.1f}% WR · avg {avg_v:+.2f}% · {len(a)} trades</span></div><div style="height:8px;background:var(--border);border-radius:4px;overflow:hidden;margin-top:4px;"><div style="width:{int(wr_v)}%;height:100%;background:{col};border-radius:4px;"></div></div></div>',unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  FOOTER + AUTO-REFRESH
# ════════════════════════════════════════════════════
_now_f=datetime.now(ny_tz).timestamp()
if st.session_state.last_scan_time:
    _rem2=max(0,300-(_now_f-st.session_state.last_scan_time))
    mnt2=int(_rem2//60); sec2=int(_rem2%60)
    last_t2=datetime.fromtimestamp(st.session_state.last_scan_time,ny_tz).strftime("%H:%M:%S")
    time_info=f"⏱️ Next auto-scan: <span style='color:#00e5ff'>{mnt2:02d}:{sec2:02d}</span> · Last: <span style='color:#2dd4bf'>{last_t2} ET</span>"
else:
    time_info="⏱️ Click Scan to start"

st.markdown(f"""
<div style="margin-top:28px;padding-top:14px;border-top:1px solid #1c2533;
     display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;">
  <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">
    🦅 US Turbo v1.1 · NYSE/NASDAQ · 15M · yFinance Humanized
  </div>
  <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">{time_info}</div>
</div>
<div style="font-family:Space Mono,monospace;font-size:9px;color:#2d3748;text-align:center;margin-top:8px;">
  ⚠️ NOT financial advice · For educational purposes only · DYOR always
</div>""",unsafe_allow_html=True)

if st.session_state.last_scan_time:
    _now_f2=datetime.now(ny_tz).timestamp()
    if _now_f2-st.session_state.last_scan_time>=295:
        time.sleep(5); st.rerun()
