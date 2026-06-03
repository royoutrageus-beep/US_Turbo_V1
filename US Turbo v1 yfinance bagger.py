import yfinance as yf
import pandas as pd
import streamlit as st
import time, random, requests, numpy as np, pytz
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

TOKEN   = st.secrets.get("TELEGRAM_TOKEN", "")
CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")
ny_tz   = pytz.timezone("America/New_York")

for _k,_v in [("tt_last_sent",set()),("wl_results",[]),("wl_mode_used",""),
               ("scan_results",[]),("data_dict",{}),("last_scan_time",None),
               ("last_scan_mode","Scalping ⚡"),("sector_data",{}),
               ("gapup_results",[]),("overnight_results",[]),("beta_data",[])]:
    if _k not in st.session_state: st.session_state[_k]=_v

st.set_page_config(layout="wide",page_title="US Turbo v1.2",page_icon="🦅",initial_sidebar_state="collapsed")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');
:root{--bg:#080c10;--surface:#0d1117;--border:#1c2533;--accent:#00e5ff;
      --green:#00ff88;--red:#ff3d5a;--amber:#ffb700;--purple:#bf5fff;
      --orange:#ff7b00;--muted:#4a5568;--text:#c9d1d9;--heading:#e6edf3;}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'Syne',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stSidebar"]{display:none!important;}
[data-testid="stExpander"]{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:8px!important;margin-bottom:12px!important;}
[data-testid="stExpander"] summary{font-family:'Space Mono',monospace!important;font-size:12px!important;color:var(--accent)!important;letter-spacing:1px!important;}
.settings-label{font-family:'Space Mono',monospace;font-size:10px;color:var(--muted);letter-spacing:2px;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--border);}
.tt-header{display:flex;align-items:center;padding:16px 0 12px;border-bottom:1px solid var(--border);margin-bottom:16px;}
.tt-logo{font-family:'Space Mono',monospace;font-size:22px;font-weight:700;color:var(--accent);letter-spacing:-1px;}
.tt-sub{font-size:11px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;}
.live-badge{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.3);border-radius:20px;font-family:'Space Mono',monospace;font-size:10px;color:var(--accent);letter-spacing:1px;margin-left:auto;}
.live-dot{width:6px;height:6px;background:var(--green);border-radius:50%;animation:blink 1s infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.2;}}
.metric-row{display:flex;gap:10px;margin-bottom:18px;flex-wrap:wrap;}
.metric-card{flex:1;min-width:110px;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px 14px;position:relative;overflow:hidden;}
.metric-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--accent);}
.metric-card.green::before{background:var(--green);}.metric-card.red::before{background:var(--red);}
.metric-card.amber::before{background:var(--amber);}.metric-card.orange::before{background:var(--orange);}
.metric-card.purple::before{background:var(--purple);}
.metric-label{font-size:10px;color:var(--muted);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;}
.metric-value{font-family:'Space Mono',monospace;font-size:24px;font-weight:700;color:var(--heading);line-height:1;}
.metric-sub{font-size:10px;color:var(--muted);margin-top:3px;}
.signal-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;margin-bottom:20px;}
.signal-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;position:relative;overflow:hidden;}
.signal-card.gacor{border-color:rgba(0,255,136,.4);background:rgba(0,255,136,.03);}
.signal-card.potensial{border-color:rgba(255,183,0,.3);background:rgba(255,183,0,.03);}
.signal-card.watch{border-color:rgba(0,229,255,.2);}
.signal-card.bagger{border-color:rgba(191,95,255,.6);background:rgba(191,95,255,.05);box-shadow:0 0 20px rgba(191,95,255,.15);}
.signal-card::after{content:'';position:absolute;top:0;left:0;width:4px;height:100%;}
.signal-card.gacor::after{background:var(--green);}.signal-card.potensial::after{background:var(--amber);}
.signal-card.watch::after{background:var(--accent);}.signal-card.bagger::after{background:var(--purple);}
.sc-ticker{font-family:'Space Mono',monospace;font-size:18px;font-weight:700;color:var(--heading);}
.sc-price{font-family:'Space Mono',monospace;font-size:13px;color:var(--muted);}
.sc-signal{font-size:13px;font-weight:700;margin:6px 0;}
.sc-bars{display:flex;gap:3px;margin:8px 0;}
.sc-bar{height:16px;border-radius:2px;}
.sc-bar.filled{background:var(--green);}.sc-bar.filled-purple{background:var(--purple);}.sc-bar.empty{background:var(--border);}
.sc-stats{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;}
.sc-stat{font-family:'Space Mono',monospace;font-size:10px;color:var(--muted);}.sc-stat span{color:var(--text);}
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
</style>""",unsafe_allow_html=True)

# ════ USD/IDR CONVERTER ════
@st.cache_data(ttl=1800)
def get_usd_idr():
    """Live USD/IDR — yFinance Ticker (chart API, no rate limit) → ExchangeRate-API → fallback"""
    # Source 1: yFinance Ticker().history() — chart API, tidak kena rate limit
    try:
        t = yf.Ticker("USDIDR=X")
        df = t.history(period="2d", interval="1d", auto_adjust=True, timeout=8)
        if df is not None and not df.empty:
            c = df["Close"].dropna()
            if len(c) >= 1:
                rate = float(c.iloc[-1])
                if 10000 < rate < 25000:
                    return rate, "yFinance"
    except: pass
    # Source 2: ExchangeRate-API (free)
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=8)
        if r.status_code == 200:
            data = r.json()
            if "rates" in data and "IDR" in data["rates"]:
                rate = float(data["rates"]["IDR"])
                if 10000 < rate < 25000:
                    return rate, "ExchangeRate-API"
    except: pass
    return 16200.0, "Fallback (stale)"

def usd_to_idr(usd_price, rate):
    idr = usd_price * rate
    if idr >= 1_000_000: return f"Rp{idr/1_000_000:.2f}jt"
    elif idr >= 1_000:   return f"Rp{idr:,.0f}"
    else:                return f"Rp{idr:.0f}"

def fmt_idr(idr_val):
    if idr_val >= 1_000_000_000: return f"Rp{idr_val/1_000_000_000:.2f}M"
    elif idr_val >= 1_000_000:   return f"Rp{idr_val/1_000_000:.1f}jt"
    elif idr_val >= 1_000:       return f"Rp{idr_val:,.0f}"
    return f"Rp{idr_val}"

# ════ FETCH ENGINE v1.2 — ZERO RATE LIMIT ════
# yf.Ticker().history() = chart API endpoint = tidak kena rate limit
# yf.download()         = bulk endpoint = DIHAPUS TOTAL
# Tidak ada custom User-Agent — justru bisa trigger detection

@st.cache_data(ttl=300,show_spinner=False)
def _fetch_ticker(ticker, period="7d", interval="15m"):
    """Core fetch. Semua data lewat sini. US stocks = no suffix."""
    try:
        t  = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval, auto_adjust=True, timeout=15)
        if df is None or df.empty: return None
        df.columns = [c.capitalize() for c in df.columns]
        req = ["Open","High","Low","Close","Volume"]
        if any(c not in df.columns for c in req): return None
        df = df[req].dropna(subset=["Close"])
        df = df[df["Volume"] > 0]
        return df if len(df) >= 2 else None
    except: return None

def _fetch_parallel(tickers, period="7d", interval="15m", workers=5, delay=(0.1, 0.4)):
    """Parallel fetch — workers=5 + delay = cepat tapi sopan ke Yahoo."""
    results = {}; lock = __import__("threading").Lock()
    shuffled = list(tickers); random.shuffle(shuffled)  # acak = tidak terdeteksi
    def _one(t):
        time.sleep(random.uniform(*delay))
        df = _fetch_ticker(t, period, interval)
        if df is not None:
            with lock: results[t] = df
    with ThreadPoolExecutor(max_workers=workers) as exe:
        list(exe.map(_one, shuffled))
    return results

@st.cache_data(ttl=300,show_spinner=False)
def fetch_intraday(tickers, chunk=None):
    """Parallel 15m intraday — no rate limit."""
    return _fetch_parallel(list(tickers), "7d", "15m", workers=5)

@st.cache_data(ttl=600,show_spinner=False)
def get_market_regime():
    """SPX + VIX regime — Ticker().history(), no download()."""
    try:
        df_spx = _fetch_ticker("^GSPC", "60d", "1d")
        if df_spx is None or len(df_spx) < 10:
            return ("UNKNOWN", 0, 0, 0, "No data", 0.0, 20.0)
        close = df_spx["Close"].dropna()
        ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
        ema55 = float(close.ewm(span=min(55, len(close)-1), adjust=False).mean().iloc[-1])
        price = float(close.iloc[-1])
        chg   = float((close.iloc[-1]-close.iloc[-2])/close.iloc[-2]*100)
        vix_val = 20.0
        try:
            df_vix = _fetch_ticker("^VIX", "5d", "1d")
            if df_vix is not None and not df_vix.empty:
                vix_val = float(df_vix["Close"].iloc[-1])
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
    return{
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
                    "label":"⚪ REGIME UNKNOWN — Manual Mode","color":"#4a5568","desc":""},
    }.get(regime,{"mode":"Scalping ⚡","min_score":4,"min_rvol":1.5,"sl_mult":0.8,"label":"⚪","color":"#4a5568","desc":""})

@st.cache_data(ttl=3600,show_spinner=False)
def fetch_pivot_data(ticker):
    """Pivot dari daily data — Ticker().history()."""
    try:
        df = _fetch_ticker(ticker, "5d", "1d")
        if df is None or len(df) < 2: return None
        p = df.iloc[-2]; h,l,c = float(p["High"]),float(p["Low"]),float(p["Close"])
        pp = (h+l+c)/3
        return {"PP":pp,"R1":2*pp-l,"R2":pp+(h-l),"R3":h+2*(pp-l),
                "S1":2*pp-h,"S2":pp-(h-l),"S3":l-2*(h-pp)}
    except: return None

@st.cache_data(ttl=360,show_spinner=False)
def fetch_mtf_data(ticker):
    """MTF via resample — 1 fetch, 3 timeframe, zero extra API call."""
    result = {}
    df15 = _fetch_ticker(ticker, "7d", "15m")
    if df15 is None or len(df15) < 10: return result
    if len(df15) >= 20: result["M15"] = df15
    for rs_rule,rs_key,min_b in [("1h","H1",10),("1D","D1",3)]:
        try:
            dr = df15.resample(rs_rule).agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna(subset=["Close"])
            dr = dr[dr["Volume"]>0]
            if len(dr) >= min_b: result[rs_key] = dr
        except: pass
    return result

@st.cache_data(ttl=600,show_spinner=False)
def fetch_sector_rotation(sector_stocks):
    """Sector fetch — parallel Ticker().history()."""
    tickers = sector_stocks[:10]
    raw = _fetch_parallel(tickers, "5d", "1d", workers=5)
    results = []
    for t, df in raw.items():
        try:
            if df is None or len(df) < 2: continue
            close=float(df["Close"].iloc[-1]); prev=float(df["Close"].iloc[-2])
            chg=(close-prev)/prev*100; vol=float(df["Volume"].iloc[-1])
            avgv=float(df["Volume"].mean()); rvol=vol/avgv if avgv>0 else 1.0
            results.append({"ticker":t,"close":close,"chg":round(chg,2),"rvol":round(rvol,2)})
        except: continue
    return results

@st.cache_data(ttl=300,show_spinner=False)
def scan_gap_up(tickers, min_gap_pct=0.5):
    """Gap Up scan — parallel Ticker().history()."""
    raw = _fetch_parallel(list(tickers), "5d", "1d", workers=6)
    results = []
    for t, df in raw.items():
        try:
            if df is None or len(df) < 3: continue
            today=df.iloc[-1]; prev=df.iloc[-2]
            cl=float(today["Close"]); ht=float(today["High"]); lt=float(today["Low"])
            hp=float(prev["High"]); vol=float(today["Volume"]); avgv=float(df["Volume"].mean())
            rvol=vol/avgv if avgv>0 else 1.0
            gs=0; reasons=[]
            if cl>hp:
                gs+=3; reasons.append(f"Gap {(cl-hp)/hp*100:.1f}% above prev High ✦✦")
            cr=(cl-lt)/max(ht-lt,0.01)
            if cr>0.85: gs+=2; reasons.append(f"Closed near HOD {cr:.0%}")
            elif cr>0.70: gs+=1; reasons.append(f"Strong close {cr:.0%}")
            if rvol>3.0:   gs+=2; reasons.append(f"RVOL={rvol:.1f}x SURGE 🔥")
            elif rvol>2.0: gs+=1; reasons.append(f"RVOL={rvol:.1f}x")
            elif rvol>1.5: gs+=0.5
            if len(df)>=3:
                c3=(cl-float(df.iloc[-3]["Close"]))/float(df.iloc[-3]["Close"])*100
                if c3>3: gs+=1; reasons.append(f"3D ROC +{c3:.1f}%")
                elif c3>1: gs+=0.5
            if gs<3: continue
            results.append({"Ticker":t,"Price":round(cl,2),"Gap Score":round(gs,1),
                "Chg %":round((cl-float(prev["Close"]))/float(prev["Close"])*100,2),
                "Close Ratio":round(cr,2),"RVOL":round(rvol,2),"Prev High":round(hp,2),
                "Signal":"GAP UP 🚀" if gs>=4 else "POTENTIAL ⚡",
                "Reasons":" · ".join(reasons[:3])})
        except: continue
    return sorted(results, key=lambda x:x["Gap Score"], reverse=True)

def calc_trailing_stop(entry,current,atr,method="ATR",atr_mult=2.0,pct=3.0):
    if method=="ATR":      td=atr*atr_mult; sp=current-td
    elif method=="Persen": td=current*(pct/100); sp=current*(1-pct/100)
    else:                  td=atr*1.5; sp=current-td
    return{"stop":round(sp,2),"distance":round(td,2),
           "profit_float":round((current-entry)/entry*100,2),
           "profit_locked":round((sp-entry)/entry*100,2) if sp>entry else 0,
           "is_profitable":sp>entry}

def calc_pivot_points(high,low,close):
    pp=(high+low+close)/3; r1=2*pp-low; r2=pp+(high-low); r3=high+2*(pp-low)
    s1=2*pp-high; s2=pp-(high-low); s3=low-2*(high-pp)
    return{"PP":pp,"R1":r1,"R2":r2,"R3":r3,"S1":s1,"S2":s2,"S3":s3}

def get_pivot_position(price,pivots):
    if pivots is None: return "Unknown","#4a5568"
    pp=pivots["PP"]
    if price>pivots["R2"]:   return "Above R2 🔴","#ff3d5a"
    elif price>pivots["R1"]: return "R1→R2 🟠","#ff7b00"
    elif price>pp:           return "PP→R1 🟢","#00ff88"
    elif price>pivots["S1"]: return "S1→PP 🟡","#ffb700"
    elif price>pivots["S2"]: return "S2→S1 🔴","#ff3d5a"
    else:                    return "Below S2 🔴","#ff3d5a"

# ════ STOCK LIST ════
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
    "DKNG","LYFT","WMT","PG","KO","PEP","MDLZ","KHC","GIS","K",
    "MKC","HRL","CPB","CAG","SJM","MO","PM","BTI","CL","CHD",
    "CLX","EL","COTY","KR","SYY","USFD","SFM",
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
seen=set(); raw_stocks=[x for x in raw_stocks if not(x in seen or seen.add(x))]
stocks_yf=raw_stocks; stock_map={s:s for s in raw_stocks}

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

# ════ INDICATORS ════
def ema(s,n): return s.ewm(span=n,adjust=False).mean()
def rsi_smooth(s,p=14,sm=3):
    d=s.diff(); g=d.clip(lower=0).rolling(p).mean(); l=(-d.clip(upper=0)).rolling(p).mean()
    rs=g/l.replace(0,np.nan); raw=100-100/(1+rs); return raw,ema(raw,sm)
def stochastic(h,l,c,k=14,d=3):
    ll=l.rolling(k).min(); hh=h.rolling(k).max()
    K=100*(c-ll)/(hh-ll).replace(0,np.nan); D=K.rolling(d).mean()
    return K.fillna(50),D.fillna(50)
def macd(s,f=12,sl=26,sg=9):
    ml=ema(s,f)-ema(s,sl); sig=ema(ml,sg); return ml,sig,ml-sig
def vwap(df):
    tp=(df["High"]+df["Low"]+df["Close"])/3; return(tp*df["Volume"]).cumsum()/df["Volume"].cumsum()

def apply_intraday_indicators(df):
    if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.droplevel(1)
    df["EMA9"]=ema(df["Close"],9);   df["EMA21"]=ema(df["Close"],21)
    df["EMA50"]=ema(df["Close"],50); df["EMA200"]=ema(df["Close"],200)
    df["RSI"],df["RSI_EMA"]=rsi_smooth(df["Close"],14,3)
    df["STOCH_K"],df["STOCH_D"]=stochastic(df["High"],df["Low"],df["Close"],14,3)
    df["MACD"],df["MACD_Sig"],df["MACD_Hist"]=macd(df["Close"])
    try:    df["VWAP"]=vwap(df)
    except: df["VWAP"]=df["Close"]
    df["BB_mid"]=df["Close"].rolling(20).mean(); df["BB_std"]=df["Close"].rolling(20).std()
    df["BB_upper"]=df["BB_mid"]+2*df["BB_std"]; df["BB_lower"]=df["BB_mid"]-2*df["BB_std"]
    df["BB_pct"]=(df["Close"]-df["BB_lower"])/(df["BB_upper"]-df["BB_lower"])
    df["AvgVol"]=df["Volume"].rolling(20).mean()
    df["RVOL"]=df["Volume"]/df["AvgVol"].replace(0,np.nan)
    df["NetVol"]=np.where(df["Close"]>=df["Open"],df["Volume"],-df["Volume"])
    df["NetVol3"]=pd.Series(df["NetVol"],index=df.index).rolling(3).sum()
    df["NetVol8"]=pd.Series(df["NetVol"],index=df.index).rolling(8).sum()
    df["VolSpike"]=df["RVOL"]>2.5
    df["Body"]=(df["Close"]-df["Open"]).abs()
    df["BodyRatio"]=df["Body"]/(df["High"]-df["Low"]).replace(0,np.nan)
    df["BullBar"]=(df["Close"]>df["Open"])&(df["BodyRatio"]>0.5)
    df["ROC3"]=df["Close"].pct_change(3); df["ROC8"]=df["Close"].pct_change(8)
    df["HH"]=df["High"]>df["High"].shift(1); df["HL"]=df["Low"]>df["Low"].shift(1)
    df["LL"]=df["Low"]<df["Low"].shift(1);   df["LH"]=df["High"]<df["High"].shift(1)
    tr=pd.concat([df["High"]-df["Low"],(df["High"]-df["Close"].shift()).abs(),(df["Low"]-df["Close"].shift()).abs()],axis=1).max(axis=1)
    df["ATR"]=tr.rolling(14).mean()
    return df

# ════ SCORING ════
def score_scalping(r,p,p2):
    s=0;rs=[]
    if r["EMA9"]>r["EMA21"]>r["EMA50"]: s+=1.5;rs.append("EMA stack ▲")
    elif r["EMA9"]>r["EMA21"]:           s+=0.8;rs.append("EMA9>21")
    if r["Close"]>r["VWAP"]:             s+=1;  rs.append("Above VWAP")
    mh=r["MACD_Hist"]; pmh=float(p["MACD_Hist"])
    if mh>0 and mh>pmh:
        s+=1.5;rs.append("MACD hist expanding ✦")
        if p2 is not None and pmh>float(p2["MACD_Hist"]): s+=0.3
    elif mh>0: s+=0.5;rs.append("MACD hist +")
    re=float(r["RSI_EMA"])
    if 52<re<68: s+=0.8;rs.append(f"RSI-EMA={re:.1f}")
    elif re>=68: s-=0.5
    rv=float(r["RVOL"])
    if rv>2.0: s+=1;rs.append(f"RVOL={rv:.1f}x surge")
    elif rv>1.5: s+=0.6;rs.append(f"RVOL={rv:.1f}x")
    if bool(r["BullBar"]): s+=0.5;rs.append("Bullish bar")
    if float(r["NetVol3"])>0: s+=0.4;rs.append("Net vol +")
    if r["Close"]<r["EMA200"]*0.98: s-=0.5
    return max(0,min(6,round(s,1))),rs,{}

def score_momentum(r,p,p2):
    s=0;rs=[]
    if bool(r["HH"]) and bool(r["HL"]): s+=1.5;rs.append("HH+HL pattern ▲")
    elif bool(r["HH"]): s+=0.8
    rv=float(r["RVOL"])
    if rv>3.0: s+=1.5;rs.append(f"RVOL={rv:.1f}x SURGE 🔥")
    elif rv>2.0: s+=1.0;rs.append(f"RVOL={rv:.1f}x")
    elif rv>1.5: s+=0.5
    roc=float(r["ROC3"])*100
    if roc>2.0: s+=1.5;rs.append(f"ROC3={roc:.1f}%")
    elif roc>1.0: s+=0.8;rs.append(f"ROC3={roc:.1f}%")
    elif roc<0: s-=0.5
    re=float(r["RSI_EMA"])
    if 55<re<75: s+=0.8;rs.append(f"RSI-EMA={re:.1f}")
    if re>78: s-=0.8;rs.append("⚠️ RSI overbought")
    sk=float(r["STOCH_K"]); sd=float(r["STOCH_D"])
    if sk>60 and sk>sd: s+=0.8;rs.append("STOCH K>D bullish")
    if r["MACD_Hist"]>0 and r["MACD_Hist"]>float(p["MACD_Hist"]): s+=0.8;rs.append("MACD expanding")
    if r["Close"]>r["VWAP"]: s+=0.5;rs.append("Above VWAP")
    return max(0,min(6,round(s,1))),rs,{}

def score_reversal(r,p,p2):
    s=0;rs=[];osc=0
    re=float(r["RSI_EMA"])
    if re<30:   osc+=1;s+=1.5;rs.append(f"RSI-EMA={re:.1f} OS extreme")
    elif re<40: osc+=1;s+=0.8;rs.append(f"RSI-EMA={re:.1f} OS")
    sk=float(r["STOCH_K"]); sd=float(r["STOCH_D"])
    if sk<20:   osc+=1;s+=1;  rs.append(f"STOCH={sk:.0f} extreme OS")
    elif sk<30: osc+=1;s+=0.5
    bp=float(r["BB_pct"])
    if bp<0.05:   osc+=1;s+=1; rs.append("BB lower touch")
    elif bp<0.15: osc+=1;s+=0.5
    if osc<1.5: return 0,[],{}
    rev=0; pk=float(p["STOCH_K"]); pd_=float(p["STOCH_D"])
    if sk<30 and sk>sd and pk<=pd_:   rev+=1;s+=2;  rs.append("STOCH %K cross ↑ OS ✦✦")
    elif sk<25 and sk>sd:             rev+=1;s+=1.2;rs.append("STOCH K>D extreme OS")
    rp=float(p["RSI_EMA"])
    if re>rp and re<42: rev+=1;s+=1.2;rs.append("RSI-EMA pivot ↑")
    mh=float(r["MACD_Hist"]); mph=float(p["MACD_Hist"])
    if mh>mph and mh<0: rev+=1;s+=0.8;rs.append("MACD hist diverge ↑")
    if rev==0: s*=0.3
    if bool(r["VolSpike"]) and float(r["Close"])<float(r["Open"]): s+=0.8;rs.append("Volume climax sell")
    elif float(r["RVOL"])>1.5: s+=0.4
    if float(r["NetVol3"])>0: s+=0.5;rs.append("Net vol turning +")
    if float(r["BodyRatio"])>0.75 and float(r["Close"])<float(r["Open"]): s-=0.8;rs.append("⚠️ Strong bear bar")
    return max(0,min(6,round(s,1))),rs,{}

def score_bagger(r,p,p2,df_full):
    s=0;rs=[];cl=float(r["Close"]); rv=float(r["RVOL"]); re=float(r["RSI_EMA"])
    e9=float(r["EMA9"]); e21=float(r["EMA21"]); e50=float(r["EMA50"]); e200=float(r["EMA200"])
    wp="SCANNING"; is_sw=False; rh=cl*1.05; rl=cl*0.95; swb=min(20,len(df_full)-2)
    try:
        rh=float(df_full["High"].iloc[-swb-1:-1].max()); rl=float(df_full["Low"].iloc[-swb-1:-1].min())
        rp=(rh-rl)/max(rl,0.01)*100; is_sw=rp<8.0
        if is_sw: s+=1.0+max(0,(8.0-rp)/8.0)*0.5; rs.append(f"Sideways {rp:.1f}% ({swb}B) ✦"); wp="A-B"
    except: pass
    try:
        vm20=float(df_full["AvgVol"].iloc[-1]); vl5=float(df_full["Volume"].iloc[-6:-1].mean())
        dr=vl5/max(vm20,1)
        if dr<0.5 and is_sw:    s+=2.0;rs.append(f"Dry vol {dr:.2f}x stealth accum ✦✦");wp="A-B AKUMULASI"
        elif dr<0.7 and is_sw:  s+=1.2;rs.append(f"Vol drying {dr:.2f}x ✦");wp="A-B AKUMULASI"
        elif dr<0.85 and is_sw: s+=0.6;rs.append(f"Vol below avg {dr:.2f}x")
    except: pass
    try:
        if len(df_full)>=12:
            nv=[float(df_full["NetVol"].iloc[i]) for i in range(-11,-1)]
            np_=sum(1 for v in nv if v>0); nr=np_/10
            if nr>=0.7 and is_sw:  s+=1.5;rs.append(f"Stealth net buy {np_}/10 bars ✦✦")
            elif nr>=0.6:          s+=0.8;rs.append(f"Net buy {np_}/10 bars")
            elif nr>=0.5:          s+=0.4
    except:
        if float(r["NetVol3"])>0 and float(r["NetVol8"])>0: s+=0.8;rs.append("Net buyer sustained ✦")
        elif float(r["NetVol3"])>0: s+=0.3
    try:
        bc=float(r["BB_std"]); ba=float(df_full["BB_std"].iloc[-11:-1].mean())
        sq=bc/max(ba,0.0001)
        if sq<0.7 and is_sw:  s+=1.5;rs.append(f"BB squeeze {sq:.2f}x ✦✦")
        elif sq<0.85:         s+=0.8;rs.append(f"BB squeeze {sq:.2f}x")
    except: pass
    spd=False
    try:
        lb=min(15,len(df_full)-3); pl=df_full["Low"].iloc[-lb-2:-2]
        sup=float(pl.min()); bl=float(r["Low"]); bc_=float(r["Close"]); bh=float(r["High"])
        if bl<sup and bc_>sup:
            rc=(bc_-bl)/max(bh-bl,0.0001)
            if rc>0.7 and rv>1.2:  s+=3.0;rs.append(f"🔥 SPRING! {rc:.0%} rebound ✦✦✦");wp="SPRING ⚡";spd=True
            elif rc>0.5:           s+=1.8;rs.append(f"Spring ({rc:.0%}) ✦✦");wp="SPRING";spd=True
        if float(p["Low"])<sup and float(p["Close"])>sup and bc_>float(p["Close"]) and not spd:
            s+=2.0;rs.append("Post-spring confirmation 🚀 ✦✦");wp="POST-SPRING";spd=True
    except: pass
    try:
        ar=cl>rh*0.998; tb=float(r["BodyRatio"])>0.55; bb2=float(r["Close"])>float(r["Open"])
        if rv>4.0 and ar and tb and bb2:  s+=3.0;rs.append(f"🚀 PHASE D! RVOL={rv:.1f}x ✦✦✦");wp="PHASE D 🚀"
        elif rv>3.0 and ar and bb2:       s+=2.2;rs.append(f"Breakout RVOL={rv:.1f}x ✦✦");wp="BREAKOUT ✦"
        elif rv>2.0 and ar:              s+=1.5;rs.append(f"Breakout attempt RVOL={rv:.1f}x")
        elif ar:                         s+=0.8;rs.append("Above resistance")
        else:
            if rv>4.0:   s+=1.5;rs.append(f"RVOL={rv:.1f}x MASSIVE 🔥🔥")
            elif rv>3.0: s+=1.0;rs.append(f"RVOL={rv:.1f}x SURGE 🔥")
            elif rv>2.0: s+=0.5;rs.append(f"RVOL={rv:.1f}x")
            elif rv<1.3 and wp not in ["A-B AKUMULASI","SPRING","POST-SPRING"]: s-=0.5
    except:
        if rv>4.0:   s+=1.5;rs.append(f"RVOL={rv:.1f}x MASSIVE 🔥🔥")
        elif rv>3.0: s+=1.0;rs.append(f"RVOL={rv:.1f}x SURGE 🔥")
        elif rv>2.0: s+=0.5
    if e9>e21>e50>e200: s+=1.5;rs.append("EMA golden stack ✦✦")
    elif e9>e21>e50:    s+=1.0;rs.append("EMA stack ▲")
    elif e9>e21:        s+=0.4
    if wp in ["A-B","A-B AKUMULASI","SPRING","POST-SPRING"]:
        if 25<=re<=52:  s+=1.0;rs.append(f"RSI-EMA={re:.1f} accum zone ✓")
        elif re<25:     s+=0.6
        elif re>65:     s-=0.3
    else:
        if 52<re<72:   s+=1.0;rs.append(f"RSI-EMA={re:.1f} momentum")
        elif re>=72:   s-=0.5;rs.append(f"⚠️ RSI OB {re:.1f}")
        elif re<40:    s-=0.3
    if cl>float(r["VWAP"]): s+=0.5;rs.append("Above VWAP")
    if e200>0 and cl<e200*0.88: s-=1.0
    try:
        if len(df_full)>=4:
            bc3=sum(1 for i in range(-3,0) if float(df_full["Close"].iloc[i])>float(df_full["Open"].iloc[i]))
            if bc3==3: s+=0.8;rs.append("3x consecutive bull bars")
            elif bc3==2: s+=0.3
    except: pass
    if wp!="SCANNING": rs.insert(0,f"⚙️ Wyckoff: {wp}")
    return max(0,min(6,round(s,1))),rs,{"wyckoff_phase":wp}

def score_overnight(r,p,p2):
    s=0;rs=[]
    hl=float(r["High"])-float(r["Low"]); cp=(float(r["Close"])-float(r["Low"]))/max(hl,0.01)
    if cp>0.75:   s+=2;  rs.append(f"Closed near HOD ({cp:.0%}) ✦✦")
    elif cp>0.55: s+=1;  rs.append(f"Strong close ({cp:.0%})")
    rv=float(r["RVOL"])
    if rv>3.0:   s+=2;   rs.append(f"RVOL={rv:.1f}x SURGE 🔥")
    elif rv>2.0: s+=1.5; rs.append(f"RVOL={rv:.1f}x power hour")
    elif rv>1.5: s+=0.8; rs.append(f"RVOL={rv:.1f}x")
    if r["EMA9"]>r["EMA21"]>r["EMA50"]:  s+=1.5;rs.append("EMA stack ▲")
    elif r["EMA9"]>r["EMA21"]:            s+=0.8;rs.append("EMA9>21")
    re=float(r["RSI_EMA"])
    if 45<re<70:  s+=1;  rs.append(f"RSI-EMA={re:.1f} ✓")
    elif re>=70:  s-=1;  rs.append(f"⚠️ RSI OB {re:.1f}")
    elif re<40:   s+=0.5;rs.append(f"RSI bounce zone {re:.1f}")
    if float(r["MACD_Hist"])>0 and float(r["MACD_Hist"])>float(p["MACD_Hist"]):
        s+=1;rs.append("MACD hist expanding ✦")
    elif float(r["MACD_Hist"])>0: s+=0.5;rs.append("MACD +")
    if float(r["Close"])>float(r["VWAP"]): s+=0.5;rs.append("Above VWAP")
    if float(r["NetVol8"])>0: s+=0.5;rs.append("Net buyer 8 bar")
    elif float(r["NetVol3"])>0: s+=0.3
    return max(0,min(6,round(s,1))),rs,{}

def score_mtf(ticker,mode="Scalping ⚡"):
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
    vals=list(scores.values()); avg=sum(vals)/len(vals); bc=sum(1 for v in vals if v>=4)
    if bc==len(vals):  return "FULL ALIGN 🔥","#00ff88",avg
    elif bc>=2:        return "PARTIAL ⚡","#ffb700",avg
    elif bc==1:        return "MIXED ⚠️","#ff7b00",avg
    else:              return "NO ALIGN ❌","#ff3d5a",avg

def get_signal(score,mode):
    t={"Scalping ⚡":{5:"RIPPING ⚡",4:"POTENSIAL 🔥",3:"WATCH 👀"},
       "Momentum 🚀":{5:"RIPPING 🚀",4:"POTENSIAL 🔥",3:"WATCH 👀"},
       "Reversal 🎯":{5:"REVERSAL 🎯",4:"POTENSIAL 🔥",3:"WATCH 👀"},
       "Bagger 💎":{5:"BAGGER 💎",4:"KANDIDAT 🚀",3:"WATCH 👀"}}.get(mode,{})
    for th in sorted(t.keys(),reverse=True):
        if score>=th: return t[th]
    return "WAIT"

def get_card_class(sig):
    if "BAGGER" in sig or "KANDIDAT" in sig: return "bagger"
    if "RIPPING" in sig or "REVERSAL" in sig: return "gacor"
    if "POTENSIAL" in sig: return "potensial"
    if "WATCH" in sig:     return "watch"
    return ""

def send_telegram(results_top,source="Scanner"):
    if not TOKEN or not CHAT_ID: return
    now_et=datetime.now(ny_tz); is_open=(now_et.hour==9 and now_et.minute>=30) or (10<=now_et.hour<16)
    sep="━"*28
    mkt="🟢 MARKET OPEN" if is_open else "🌙 AFTER HOURS"
    src="WATCHLIST" if source=="Watchlist" else "ALERT"
    hdr=(f"{mkt}\n🦅 *US TURBO {src}*\n"
         f"⏰ `{now_et.strftime('%H:%M:%S')} ET` · `{now_et.strftime('%d %b %Y')}`\n{sep}\n")
    body=""
    for r in results_top[:5]:
        sig=r.get("Signal","-")
        em="💎" if "BAGGER" in sig else("🏆" if("RIPPING" in sig or "REVERSAL" in sig) else("🔥" if "POTENSIAL" in sig else "👀"))
        te="📈" if "▲" in r.get("Trend","") else("📉" if "▼" in r.get("Trend","") else "➡️")
        bar="█"*int(r["Score"])+"░"*(6-int(r["Score"]))
        pd_=r.get("Price_fmt",f"Rp{int(r.get('Price(IDR)',r.get('Price(USD)',0)*16200)):,}")
        td=r.get("TP_fmt","—"); sd_=r.get("SL_fmt","—")
        pu=r.get("Price(USD)",r.get("Price",0))
        body+=(f"\n{em} *{r['Ticker']}*  `{sig}`\n"
               f"   💰 {pd_} (${pu:.2f}) {te}\n"
               f"   📊 Score: `[{bar}] {r['Score']}/6`\n"
               f"   📈 RSI-EMA: `{r.get('RSI-EMA',0)}` | RVOL: `{r.get('RVOL',0)}x`\n"
               f"   🎯 TP: {td} | SL: {sd_} | R:R `{r['R:R']}`\n"
               f"   💡 _{r.get('Reasons','')[:60]}_\n")
    footer=f"\n{sep}\n⚡ _US Turbo v1.2 · 15M · NYSE/NASDAQ · Zero Rate Limit_\n⚠️ _NOT financial advice. DYOR!_"
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id":CHAT_ID,"text":hdr+body+footer,"parse_mode":"Markdown"},timeout=10)
    except: pass

# ════ HEADER ════
regime,spx_price,ema20,ema55,regime_detail,spx_chg,vix_val=get_market_regime()
rcfg=get_regime_config(regime); rcolor=rcfg["color"]
chg_col="#00ff88" if spx_chg>=0 else "#ff3d5a"; chg_sym="▲" if spx_chg>=0 else "▼"
vix_col="#ff3d5a" if vix_val>30 else("#ffb700" if vix_val>20 else "#00ff88")
vix_lbl="⚠️ FEAR" if vix_val>30 else("😐 CAUTION" if vix_val>20 else "🧊 CALM")
now_et=datetime.now(ny_tz)
_idr_rate,_idr_src=get_usd_idr()

st.markdown(f"""
<div class="tt-header">
  <div><div class="tt-logo">🦅 US TURBO</div>
  <div class="tt-sub">Intraday 15M · Auto Regime · Bagger · v1.2 · Zero Rate Limit ✅</div></div>
  <div class="live-badge"><div class="live-dot"></div>📊 yF Chart API · LIVE {now_et.strftime("%H:%M:%S")} ET</div>
</div>""",unsafe_allow_html=True)

st.markdown(f"""
<div style="background:rgba(0,0,0,.4);border:1px solid {rcolor}44;border-radius:8px;padding:12px 16px;margin-bottom:14px;border-left:4px solid {rcolor};">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
    <div><div style="font-family:Space Mono,monospace;font-size:12px;font-weight:700;color:{rcolor};letter-spacing:1px;">{rcfg["label"]}</div>
      <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-top:3px;">{rcfg["desc"]}</div></div>
    <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
      <div style="text-align:center;">
        <div style="font-family:Space Mono,monospace;font-size:18px;font-weight:700;color:{rcolor};">{spx_price:,.0f} <span style="font-size:11px;color:{chg_col}">{chg_sym}{abs(spx_chg):.2f}%</span></div>
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
</div>""",unsafe_allow_html=True)

tab_scanner,tab_watchlist,tab_overnight,tab_sector,tab_gapup,tab_trail,tab_backtest=st.tabs(
    ["🦅 Scanner","👁️ Watchlist","🌙 Overnight","🏭 Sectors","📈 Gap Up","🎯 Trailing Stop","📊 Backtest"])

# ════ TAB SCANNER ════
with tab_scanner:
    with st.expander("⚙️  Scanner Settings",expanded=False):
        sc1,sc2,sc3=st.columns(3)
        with sc1:
            st.markdown('<div class="settings-label">SIGNAL MODE</div>',unsafe_allow_html=True)
            auto_regime=st.toggle("🤖 Auto-Mode (Market Regime)",value=True,key="auto_reg")
            if auto_regime:
                scan_mode=rcfg["mode"]
                st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:10px;padding:6px 10px;background:rgba(0,0,0,.3);border-radius:4px;color:{rcolor};">Auto: {scan_mode}</div>',unsafe_allow_html=True)
            else:
                scan_mode=st.radio("Mode",["Scalping ⚡","Momentum 🚀","Reversal 🎯","Bagger 💎"],label_visibility="collapsed",key="smr")
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
            view_mode=st.radio("View",["Card View 🃏","Table View 📊"],label_visibility="collapsed",key="vm")
            scan_size=st.radio("Scan Size",["100 ⚡","200 🔥","Full 🦅"],index=1,horizontal=True,key="ssr")
            st.caption(f"🎯 Regime: {regime} · VIX: {vix_val:.1f} {vix_lbl}")
            st.caption(f"📊 {len(raw_stocks)} stocks available")

    do_scan=st.button("🦅 START SCAN NOW",type="primary",use_container_width=True,key="btn_scan")
    _nc=datetime.now(ny_tz).timestamp()
    if st.session_state.last_scan_time and not do_scan:
        if _nc-st.session_state.last_scan_time>=300 and st.session_state.scan_results:
            do_scan=True

    if do_scan:
        _sz=st.session_state.get("ssr","200 🔥")
        if "100" in _sz:   sl=stocks_yf[:100]
        elif "200" in _sz: sl=stocks_yf[:200]
        else:              sl=stocks_yf
        ph=st.empty(); pb=st.progress(0)
        ph.markdown(f'<div style="color:#00e5ff;font-family:Space Mono,monospace;font-size:12px;">🦅 SCANNING {len(sl)} stocks · {scan_mode}...</div>',unsafe_allow_html=True)
        try:
            data_dict=fetch_intraday(tuple(sl))
            st.session_state.data_dict=data_dict
            results=[]; tickers=list(data_dict.keys())
            for i,ticker in enumerate(tickers):
                pb.progress((i+1)/max(len(tickers),1))
                try:
                    df=data_dict[ticker].copy()
                    if len(df)<30: continue
                    df=apply_intraday_indicators(df)
                    r=df.iloc[-1]; p=df.iloc[-2]; p2=df.iloc[-3] if len(df)>=3 else p
                    cl=float(r["Close"]); vol=float(r["Volume"]); to=cl*vol; rv=float(r["RVOL"])
                    if to<min_turn or rv<vol_thresh: continue
                    if scan_mode=="Scalping ⚡":   sc,rs,_=score_scalping(r,p,p2)
                    elif scan_mode=="Momentum 🚀": sc,rs,_=score_momentum(r,p,p2)
                    elif scan_mode=="Bagger 💎":   sc,rs,_=score_bagger(r,p,p2,df)
                    else:                          sc,rs,_=score_reversal(r,p,p2)
                    if sc<min_score: continue
                    sig=get_signal(sc,scan_mode)
                    if sig=="WAIT": continue
                    atr=float(r["ATR"]) if not np.isnan(float(r["ATR"])) else cl*0.01
                    slm=rcfg.get("sl_mult",0.8)
                    if scan_mode=="Scalping ⚡":   tp=cl+1.5*atr;sl_=cl-slm*atr
                    elif scan_mode=="Momentum 🚀": tp=cl+2.0*atr;sl_=cl-slm*atr
                    elif scan_mode=="Bagger 💎":   tp=cl+3.0*atr;sl_=cl-1.0*atr
                    else:                          tp=cl+2.5*atr;sl_=cl-slm*atr
                    rr=(tp-cl)/max(cl-sl_,0.01)
                    e9=float(r["EMA9"]); e21=float(r["EMA21"]); e50=float(r["EMA50"])
                    trend="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else "◆ SIDE")
                    _r=_idr_rate
                    results.append({
                        "Ticker":stock_map[ticker],
                        "Price(USD)":round(cl,2),"Price(IDR)":int(cl*_r),
                        "Price_fmt":usd_to_idr(cl,_r),
                        "Score":sc,"Signal":sig,"Trend":trend,
                        "RSI-EMA":round(float(r["RSI_EMA"]),1),"Stoch K":round(float(r["STOCH_K"]),1),
                        "Stoch D":round(float(r["STOCH_D"]),1),"MACD Hist":round(float(r["MACD_Hist"]),4),
                        "RVOL":round(rv,2),"BB%":round(float(r["BB_pct"]),2),
                        "ROC 3B%":round(float(r["ROC3"])*100,2),"VWAP_IDR":int(float(r["VWAP"])*_r),
                        "TP_USD":round(tp,2),"SL_USD":round(sl_,2),
                        "TP_IDR":int(tp*_r),"SL_IDR":int(sl_*_r),
                        "TP_fmt":usd_to_idr(tp,_r),"SL_fmt":usd_to_idr(sl_,_r),
                        "R:R":round(rr,1),"Turnover(MRp)":round(to*_r/1e6,1),
                        "Reasons":" · ".join(rs),"_class":get_card_class(sig)
                    })
                except: continue
            ph.empty(); pb.empty()
            st.session_state.scan_results=results
            st.session_state.last_scan_time=datetime.now(ny_tz).timestamp()
            st.session_state.last_scan_mode=scan_mode
            if tele_on and results:
                if "tt_last_sent" not in st.session_state: st.session_state.tt_last_sent=set()
                dft=pd.DataFrame(results).sort_values("Score",ascending=False)
                cs=set(dft["Ticker"].tolist()); na=cs-st.session_state.tt_last_sent
                if na:
                    tn=dft[dft["Ticker"].isin(na)].head(5).to_dict("records")
                    if tn: send_telegram(tn)
                    st.session_state.tt_last_sent.update(na)
                st.session_state.tt_last_sent=st.session_state.tt_last_sent&cs
        except Exception as e:
            try: ph.empty();pb.empty()
            except: pass
            st.error(f"Scan error: {str(e)[:100]}")

    if st.session_state.last_scan_time:
        _nc2=datetime.now(ny_tz).timestamp()
        _rem=max(0,300-(_nc2-st.session_state.last_scan_time))
        _lt=datetime.fromtimestamp(st.session_state.last_scan_time,ny_tz).strftime("%H:%M:%S")
        st.caption(f"⏱️ Next auto-scan: {int(_rem//60):02d}:{int(_rem%60):02d} · Last: {_lt} ET")

    results=st.session_state.scan_results
    if not results and not do_scan:
        st.markdown(f'<div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;"><div style="font-size:36px;margin-bottom:12px;">🦅</div><div style="font-size:13px;letter-spacing:2px;">CLICK SCAN TO START</div><div style="font-size:10px;margin-top:8px;color:#2d3748;">100 ⚡ / 200 🔥 / Full 🦅 · Regime: {regime} · VIX: {vix_val:.1f}</div></div>',unsafe_allow_html=True)
    elif results:
        df_out=pd.DataFrame(results).sort_values("Score",ascending=False).reset_index(drop=True)
        gacor=df_out[df_out["Signal"].str.contains("RIPPING|REVERSAL",na=False)]
        bagger=df_out[df_out["Signal"].str.contains("BAGGER|KANDIDAT",na=False)]
        potensi=df_out[df_out["Signal"].str.contains("POTENSIAL",na=False)]
        avg_rsi=df_out["RSI-EMA"].mean()
        lm=st.session_state.get("last_scan_mode","")
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
            roc=row["ROC 3B%"]; ib="BAGGER" in row["Signal"] or "KANDIDAT" in row["Signal"]
            cls="bagger" if ib else("up" if roc>0 else("down" if roc<0 else "flat"))
            sym="💎" if ib else("▲" if roc>0 else("▼" if roc<0 else "─"))
            pd2=row.get("Price_fmt",f"Rp{row.get('Price(IDR)',0):,}")
            th+=f'<span class="tape-item {cls}">{row["Ticker"]} {pd2} {sym}{abs(roc):.1f}% [{row["Signal"]}]</span>'
        th+=th.replace('tape-inner">',''); th+='</div></div>'
        st.markdown(th,unsafe_allow_html=True)
        if not bagger.empty:
            st.markdown(f'<div class="bagger-alert-box"><div class="bagger-title">💎 BAGGER ALERT · {len(bagger)} CANDIDATES</div></div>',unsafe_allow_html=True)
        if not gacor.empty:
            st.markdown(f'<div class="alert-box"><div class="alert-title">🚨 RIPPING ALERT · {len(gacor)} STOCKS · {lm}</div></div>',unsafe_allow_html=True)
        if view_mode=="Card View 🃏":
            st.markdown('<div class="section-title">Signal Cards</div>',unsafe_allow_html=True)
            ch='<div class="signal-grid">'
            for _,row in df_out.head(20).iterrows():
                si=int(row["Score"]); ib="BAGGER" in row["Signal"] or "KANDIDAT" in row["Signal"]
                bc2="filled-purple" if ib else "filled"
                bars="".join([f'<div class="sc-bar {bc2 if i<si else "empty"}" style="width:28px"></div>' for i in range(6)])
                rc="#00ff88" if row["ROC 3B%"]>0 else "#ff3d5a"
                te="📈" if "▲" in row["Trend"] else("📉" if "▼" in row["Trend"] else "➡️")
                sc2="#bf5fff" if ib else("#00ff88" if si>=5 else "#ffb700" if si>=4 else "#00e5ff")
                pf=row.get("Price_fmt",f"Rp{row.get('Price(IDR)',0):,}")
                tf=row.get("TP_fmt","—"); sf=row.get("SL_fmt","—")
                ch+=f'''<div class="signal-card {row["_class"]}">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div><div class="sc-ticker">{row["Ticker"]}</div>
                    <div class="sc-price" style="color:{rc}">{pf} {te}</div>
                    <div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568">${row.get("Price(USD)",0):.2f} · Rp{_idr_rate:,.0f}/USD</div></div>
                    <div style="text-align:right;"><div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">SCORE</div>
                    <div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:{sc2}">{row["Score"]}</div></div>
                  </div>
                  <div class="sc-signal" style="color:{sc2}">{row["Signal"]}</div>
                  <div class="sc-bars">{bars}</div>
                  <div class="sc-stats">
                    <div class="sc-stat">RSI-EMA <span>{row["RSI-EMA"]}</span></div>
                    <div class="sc-stat">STOCH <span>{row["Stoch K"]:.0f}</span></div>
                    <div class="sc-stat">RVOL <span>{row["RVOL"]}x</span></div>
                    <div class="sc-stat">ROC <span style="color:{rc}">{row["ROC 3B%"]:+.1f}%</span></div>
                  </div>
                  <div class="sc-stats" style="margin-top:6px;">
                    <div class="sc-stat">TP <span style="color:#00ff88">{tf}</span></div>
                    <div class="sc-stat">SL <span style="color:#ff3d5a">{sf}</span></div>
                    <div class="sc-stat">R:R <span>{row["R:R"]}</span></div>
                  </div>
                  <div style="margin-top:8px;font-size:10px;color:#4a5568;line-height:1.4;font-family:Space Mono,monospace;">{row["Reasons"][:80]}</div>
                </div>'''
            ch+='</div>'; st.markdown(ch,unsafe_allow_html=True)
        st.markdown('<div class="section-title">Full Signal Table</div>',unsafe_allow_html=True)
        dc=["Ticker","Price_fmt","Price(USD)","Score","Signal","Trend","RSI-EMA","Stoch K","Stoch D","MACD Hist","RVOL","BB%","ROC 3B%","VWAP_IDR","TP_fmt","SL_fmt","TP_USD","SL_USD","R:R","Turnover(MRp)","Reasons"]
        dc=[c for c in dc if c in df_out.columns]
        st.dataframe(df_out[dc],use_container_width=True,hide_index=True,column_config={
            "Score":         st.column_config.ProgressColumn("Score",min_value=0,max_value=6,format="%.1f"),
            "Price_fmt":     st.column_config.TextColumn("Harga (IDR)"),
            "Price(USD)":    st.column_config.NumberColumn("USD",format="$%.2f"),
            "TP_fmt":        st.column_config.TextColumn("TP (IDR)"),
            "SL_fmt":        st.column_config.TextColumn("SL (IDR)"),
            "TP_USD":        st.column_config.NumberColumn("TP (USD)",format="$%.2f"),
            "SL_USD":        st.column_config.NumberColumn("SL (USD)",format="$%.2f"),
            "VWAP_IDR":      st.column_config.NumberColumn("VWAP (IDR)",format="Rp%d"),
            "RVOL":          st.column_config.NumberColumn("RVOL",format="%.1fx"),
            "ROC 3B%":       st.column_config.NumberColumn("ROC 3B%",format="%.2f%%"),
            "Turnover(MRp)": st.column_config.NumberColumn("Turnover (MRp)",format="Rp%.0fM"),
        })

# ════ TAB WATCHLIST ════
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
        raw_wl=list(dict.fromkeys([t.strip().upper() for ln in wl_input.split("\n") for t in ln.split(",") if t.strip()]))
        if raw_wl:
            with st.spinner(f"Analyzing {len(raw_wl)} stocks..."):
                # Parallel fetch all tickers at once
                raw_d=_fetch_parallel(raw_wl,"7d","15m",workers=5)
                wl_res=[]
                for t in raw_wl:
                    df=raw_d.get(t)
                    if df is None or len(df)<30:
                        wl_res.append({"Ticker":t,"Price":0,"Score":0,"Signal":"No data","Trend":"-",
                            "RSI-EMA":0,"Stoch K":0,"RVOL":0,"BB%":0,"ROC 3B%":0,"VWAP":0,
                            "TP":0,"SL":0,"R:R":0,"ATR":0,"Reasons":"No data","_class":"","MACD Hist":0,
                            "MTF Align":"-","M15":0,"H1":0,"D1":0,"Pivot Pos":"-","PP":0,"R1":0,"S1":0}); continue
                    try:
                        df=apply_intraday_indicators(df)
                        r=df.iloc[-1]; p=df.iloc[-2]; p2=df.iloc[-3] if len(df)>=3 else p
                        cl=float(r["Close"]); atr=float(r["ATR"]) if not np.isnan(float(r["ATR"])) else cl*0.01
                        slm=rcfg.get("sl_mult",0.8)
                        if wl_mode=="Scalping ⚡":   sc,rs,_=score_scalping(r,p,p2);  tp=cl+1.5*atr;sl_=cl-slm*atr
                        elif wl_mode=="Momentum 🚀": sc,rs,_=score_momentum(r,p,p2);  tp=cl+2.0*atr;sl_=cl-slm*atr
                        elif wl_mode=="Bagger 💎":   sc,rs,_=score_bagger(r,p,p2,df); tp=cl+3.0*atr;sl_=cl-1.0*atr
                        else:                        sc,rs,_=score_reversal(r,p,p2);  tp=cl+2.5*atr;sl_=cl-slm*atr
                        sig=get_signal(sc,wl_mode); rr=(tp-cl)/max(cl-sl_,0.01)
                        e9=float(r["EMA9"]); e21=float(r["EMA21"]); e50=float(r["EMA50"])
                        trend="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else "◆ SIDE")
                        pv=fetch_pivot_data(t)
                        pp2=get_pivot_position(cl,pv)[0] if pv else "-"
                        # MTF via resample dari df yang sudah ada
                        mtf2={"M15":sc}
                        try:
                            for rs_,rk_,mb_ in [("1h","H1",10),("1D","D1",3)]:
                                dr=df.resample(rs_).agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna(subset=["Close"])
                                dr=dr[dr["Volume"]>0]
                                if len(dr)>=mb_:
                                    dr=apply_intraday_indicators(dr)
                                    rr2=dr.iloc[-1]; pp3=dr.iloc[-2]; p2r=dr.iloc[-3] if len(dr)>=3 else pp3
                                    if wl_mode=="Scalping ⚡":   scr,_,_=score_scalping(rr2,pp3,p2r)
                                    elif wl_mode=="Momentum 🚀": scr,_,_=score_momentum(rr2,pp3,p2r)
                                    elif wl_mode=="Bagger 💎":   scr,_,_=score_bagger(rr2,pp3,p2r,dr)
                                    else:                         scr,_,_=score_reversal(rr2,pp3,p2r)
                                    mtf2[rk_]=round(scr,1)
                        except: pass
                        al,_,_=mtf_alignment(mtf2)
                        _r=_idr_rate
                        wl_res.append({"Ticker":t,
                            "Price(USD)":round(cl,2),"Price(IDR)":int(cl*_r),"Price_fmt":usd_to_idr(cl,_r),
                            "Score":sc,"Signal":sig,"Trend":trend,
                            "RSI-EMA":round(float(r["RSI_EMA"]),1),"Stoch K":round(float(r["STOCH_K"]),1),
                            "RVOL":round(float(r["RVOL"]),2),"BB%":round(float(r["BB_pct"]),2),
                            "ROC 3B%":round(float(r["ROC3"])*100,2),"VWAP_IDR":int(float(r["VWAP"])*_r),
                            "TP_fmt":usd_to_idr(tp,_r),"SL_fmt":usd_to_idr(sl_,_r),
                            "TP_USD":round(tp,2),"SL_USD":round(sl_,2),
                            "TP_IDR":int(tp*_r),"SL_IDR":int(sl_*_r),
                            "R:R":round(rr,1),"ATR_IDR":int(atr*_r),
                            "MACD Hist":round(float(r["MACD_Hist"]),4),"Reasons":" · ".join(rs),
                            "_class":get_card_class(sig),"MTF Align":al,
                            "M15":mtf2.get("M15",0),"H1":mtf2.get("H1",0),"D1":mtf2.get("D1",0),
                            "Pivot Pos":pp2,
                            "PP":usd_to_idr(pv["PP"],_r) if pv else "—",
                            "R1":usd_to_idr(pv["R1"],_r) if pv else "—",
                            "S1":usd_to_idr(pv["S1"],_r) if pv else "—"})
                    except:
                        wl_res.append({"Ticker":t,"Price":0,"Score":0,"Signal":"Err","Trend":"-",
                            "RSI-EMA":0,"Stoch K":0,"RVOL":0,"BB%":0,"ROC 3B%":0,"VWAP":0,
                            "TP":0,"SL":0,"R:R":0,"ATR":0,"Reasons":"","_class":"","MACD Hist":0,
                            "MTF Align":"-","M15":0,"H1":0,"D1":0,"Pivot Pos":"-","PP":"—","R1":"—","S1":"—"})
            st.session_state.wl_results=wl_res; st.session_state.wl_mode_used=wl_mode
    if wl_tele and st.session_state.wl_results:
        ts=[r for r in st.session_state.wl_results if r.get("Price",r.get("Price(USD)",0))>0]
        if ts: send_telegram(ts[:5],source="Watchlist"); st.success("📡 Sent!")
    if st.session_state.wl_results:
        ok=[r for r in st.session_state.wl_results if r.get("Score",0)>0]
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
        for row in sorted(st.session_state.wl_results,key=lambda x:x.get("Score",0),reverse=True):
            if row.get("Price",row.get("Price(USD)",0))==0:
                ch+=f'<div class="signal-card"><div class="sc-ticker">{row["Ticker"]}</div><div style="font-size:11px;color:#4a5568;margin-top:6px;">{row.get("Signal","No data")}</div></div>'; continue
            si=int(row.get("Score",0)); ib="BAGGER" in row.get("Signal","") or "KANDIDAT" in row.get("Signal","")
            bars="".join([f'<div class="sc-bar {"filled-purple" if ib else "filled" if i<si else "empty"}" style="width:26px"></div>' for i in range(6)])
            sig=row.get("Signal","-")
            sc2="#bf5fff" if ib else("#00ff88" if("RIPPING" in sig or "REVERSAL" in sig) else("#ffb700" if "POTENSIAL" in sig else "#00e5ff" if "WATCH" in sig else "#4a5568"))
            rv=row.get("RSI-EMA",0); rc="#ff3d5a" if rv<30 else("#ffb700" if rv<45 else "#00ff88" if rv>60 else "#c9d1d9")
            roc="#00ff88" if row.get("ROC 3B%",0)>0 else "#ff3d5a"
            te="📈" if "▲" in row.get("Trend","") else("📉" if "▼" in row.get("Trend","") else "➡️")
            pf=row.get("Price_fmt",f"Rp{row.get('Price(IDR)',0):,}")
            tf=row.get("TP_fmt","—"); sf=row.get("SL_fmt","—")
            ch+=f'''<div class="signal-card {row["_class"]}">
              <div style="display:flex;justify-content:space-between;">
                <div><div class="sc-ticker">{row["Ticker"]}</div>
                <div class="sc-price" style="color:{roc}">{pf} {te}</div>
                <div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568">${row.get("Price(USD)",0):.2f}</div></div>
                <div style="text-align:right"><div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568">SCORE</div>
                <div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:{sc2}">{row.get("Score",0)}</div></div>
              </div>
              <div class="sc-signal" style="color:{sc2}">{sig}</div>
              <div class="sc-bars">{bars}</div>
              <div class="sc-stats">
                <div class="sc-stat">RSI-EMA <span style="color:{rc}">{rv}</span></div>
                <div class="sc-stat">RVOL <span>{row.get("RVOL",0)}x</span></div>
                <div class="sc-stat">TP <span style="color:#00ff88">{tf}</span></div>
                <div class="sc-stat">SL <span style="color:#ff3d5a">{sf}</span></div>
              </div>
              <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;">
                <div style="font-family:Space Mono,monospace;font-size:9px;padding:2px 7px;border-radius:10px;background:rgba(0,0,0,.3);color:#4a5568;">📍 {row.get("Pivot Pos","-")}</div>
                <div style="font-family:Space Mono,monospace;font-size:9px;padding:2px 7px;border-radius:10px;background:rgba(0,0,0,.3);color:#4a5568;">MTF: {row.get("MTF Align","-")}</div>
              </div>
              <div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568;margin-top:4px;">M15:{row.get("M15",0)} · H1:{row.get("H1",0)} · D1:{row.get("D1",0)} | PP:{row.get("PP","—")} · R1:{row.get("R1","—")} · S1:{row.get("S1","—")}</div>
              <div style="margin-top:8px;font-size:10px;color:#4a5568;line-height:1.5;font-family:Space Mono,monospace">{row.get("Reasons","")[:80]}</div>
            </div>'''
        ch+='</div>'; st.markdown(ch,unsafe_allow_html=True)
    elif not wl_run:
        st.markdown('<div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;"><div style="font-size:32px;margin-bottom:12px;">👁️</div><div>ENTER TICKERS ABOVE</div></div>',unsafe_allow_html=True)

# ════ TAB OVERNIGHT ════
with tab_overnight:
    nw=datetime.now(ny_tz)
    ipt=(nw.hour==15 and nw.minute>=0) or (nw.hour==15 and nw.minute<=59)
    iot=(nw.hour==9 and nw.minute>=30) or (10<=nw.hour<10 and nw.minute<=30)
    st.markdown(f"""<div style="background:rgba(0,229,255,.05);border:1px solid rgba(0,229,255,.3);border-radius:8px;padding:14px 18px;margin-bottom:16px;">
      <div style="font-family:Space Mono,monospace;font-size:13px;font-weight:700;color:#00e5ff;letter-spacing:1px;">🌙 OVERNIGHT PLAY — Power Hour Entry</div>
      <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-top:4px;">
        Entry: <span style="color:#ffb700">3:00 PM–3:59 PM ET</span> · Exit: <span style="color:#00ff88">Next day 9:30 AM–10:30 AM ET</span> ·
        Status: <span style="color:{'#00ff88' if ipt else '#ffb700' if iot else '#4a5568'}">
          {'🟢 POWER HOUR — Entry window!' if ipt else '🟡 OPEN — Exit window!' if iot else f'⏳ Next Power Hour 3:00 PM ET · Now: {nw.strftime("%H:%M")} ET'}
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
    if do_overnight:
        op=st.empty(); op.info("🌙 Scanning overnight candidates...")
        on_res=[]; sd=st.session_state.get("data_dict",{})
        if not sd:
            try: sd=fetch_intraday(tuple(stocks_yf[:200]))
            except: pass
        pbo=st.progress(0); tko=list(sd.keys())
        for i,ticker in enumerate(tko):
            pbo.progress((i+1)/max(len(tko),1))
            try:
                df=sd[ticker].copy()
                if len(df)<30: continue
                df_c=apply_intraday_indicators(df)
                df_ph=df_c
                try:
                    df_ph=df_c[df_c.index.hour==15] if len(df_c[df_c.index.hour==15])>0 else df_c
                except: pass
                if len(df_ph)<2: df_ph=df_c
                r=df_ph.iloc[-1]; p=df_ph.iloc[-2]; p2=df_ph.iloc[-3] if len(df_ph)>=3 else p
                cl=float(r["Close"]); vol=float(r["Volume"]); to=cl*vol; rv=float(r["RVOL"])
                if to<on_min_turn or rv<on_min_rvol: continue
                sc,rs,_=score_overnight(r,p,p2)
                if sc<on_min_score: continue
                osig="STRONG BUY 🌙" if sc>=5 else("BUY ⚡" if sc>=4 else "WATCH 👀")
                atr=float(r["ATR"]); tp=cl+2.5*atr; sl_=cl-1.2*atr; rr=(tp-cl)/max(cl-sl_,0.01)
                e9=float(r["EMA9"]); e21=float(r["EMA21"]); e50=float(r["EMA50"])
                trend="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else "◆ SIDE")
                hl=float(r["High"])-float(r["Low"]); cp=(float(r["Close"])-float(r["Low"]))/max(hl,0.01)
                _r=_idr_rate
                on_res.append({"Ticker":stock_map.get(ticker,ticker),
                    "Price(USD)":round(cl,2),"Price_fmt":usd_to_idr(cl,_r),
                    "Score":sc,"Signal":osig,"Trend":trend,
                    "RSI-EMA":round(float(r["RSI_EMA"]),1),"Stoch K":round(float(r["STOCH_K"]),1),
                    "RVOL":round(rv,2),"TP_fmt":usd_to_idr(tp,_r),"SL_fmt":usd_to_idr(sl_,_r),
                    "TP_USD":round(tp,2),"SL_USD":round(sl_,2),"R:R":round(rr,1),
                    "Turnover(MRp)":round(to*_r/1e6,1),"Close%":round(cp*100,1),
                    "Reasons":" · ".join(rs),"_class":"gacor" if sc>=5 else "potensial" if sc>=4 else "watch"})
            except: continue
        pbo.empty(); op.empty()
        on_res=sorted(on_res,key=lambda x:x["Score"],reverse=True)
        st.session_state.overnight_results=on_res
        if on_tele and on_res and TOKEN and CHAT_ID:
            now_on=datetime.now(ny_tz); sep="━"*28
            msg=f"🌙 *US OVERNIGHT PLAY*\n⏰ `{now_on.strftime('%H:%M:%S')} ET`\n{sep}\n"
            for r in on_res[:5]:
                bar="█"*int(r["Score"])+"░"*(6-int(r["Score"]))
                msg+=(f"\n🌙 *{r['Ticker']}* `{r['Signal']}`\n💰 {r.get('Price_fmt','')}\n"
                      f"📊 `[{bar}] {r['Score']}/6`\n📈 RSI:`{r['RSI-EMA']}` RVOL:`{r['RVOL']}x`\n"
                      f"🎯 TP:`${r['TP_USD']:.2f}` SL:`${r['SL_USD']:.2f}` R:R:`{r['R:R']}`\n💡 _{r['Reasons'][:50]}_\n")
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
        medals=["🥇","🥈","🥉"]; ct=st.columns(min(3,len(on_results)))
        for idx,col in enumerate(ct):
            if idx>=len(on_results): break
            row=on_results[idx]; sc2="#00ff88" if "STRONG" in row["Signal"] else "#ffb700"
            with col:
                st.markdown(f"""<div style="background:#0d1117;border:1px solid {sc2}44;border-radius:10px;padding:16px;text-align:center;border-top:3px solid {sc2};">
                  <div style="font-size:24px">{medals[idx]}</div>
                  <div style="font-family:Space Mono,monospace;font-size:18px;font-weight:700;color:#e6edf3;">{row["Ticker"]}</div>
                  <div style="font-family:Space Mono,monospace;font-size:20px;font-weight:700;color:{sc2};">{row.get("Price_fmt","—")}</div>
                  <div style="font-size:9px;color:#4a5568;">${row.get("Price(USD)",0):.2f} · Score {row["Score"]}</div>
                  <div style="font-size:11px;font-weight:700;color:{sc2};margin-top:4px;">{row["Signal"]}</div>
                  <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-top:6px;">RVOL {row["RVOL"]}x · RSI {row["RSI-EMA"]}<br>TP {row.get("TP_fmt","—")} · SL {row.get("SL_fmt","—")}</div>
                </div>""",unsafe_allow_html=True)
        df_on=pd.DataFrame(on_results)
        sc3=["Ticker","Price_fmt","Price(USD)","Score","Signal","Trend","RSI-EMA","Stoch K","RVOL","TP_fmt","SL_fmt","TP_USD","SL_USD","R:R","Close%","Turnover(MRp)","Reasons"]
        sc3=[c for c in sc3 if c in df_on.columns]
        st.dataframe(df_on[sc3],use_container_width=True,hide_index=True,column_config={
            "Score":        st.column_config.ProgressColumn("Score",min_value=0,max_value=6,format="%.1f"),
            "Price_fmt":    st.column_config.TextColumn("Harga (IDR)"),
            "Price(USD)":   st.column_config.NumberColumn("USD",format="$%.2f"),
            "TP_fmt":       st.column_config.TextColumn("TP (IDR)"),
            "SL_fmt":       st.column_config.TextColumn("SL (IDR)"),
            "TP_USD":       st.column_config.NumberColumn("TP (USD)",format="$%.2f"),
            "SL_USD":       st.column_config.NumberColumn("SL (USD)",format="$%.2f"),
            "RVOL":         st.column_config.NumberColumn("RVOL",format="%.2fx"),
        })
    elif not do_overnight:
        st.markdown('<div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;"><div style="font-size:32px;margin-bottom:12px;">🌙</div><div>CLICK SCAN OVERNIGHT</div></div>',unsafe_allow_html=True)

# ════ TAB SECTORS ════
with tab_sector:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:14px;padding:10px 14px;background:#0d1117;border-radius:6px;border-left:3px solid #00e5ff;">Track US sector rotation. FED-sensitive sectors highlighted.</div>',unsafe_allow_html=True)
    do_sector=st.button("🏭 REFRESH US SECTORS",type="primary",use_container_width=True,key="btn_sector")
    if do_sector:
        with st.spinner("Fetching US sector data..."):
            sec_data={}
            for sec_name,sec_stocks in SECTORS.items():
                results=fetch_sector_rotation(sec_stocks)
                if results:
                    avg_chg=sum(r["chg"] for r in results)/len(results)
                    avg_rvol=sum(r["rvol"] for r in results)/len(results)
                    bullish=sum(1 for r in results if r["chg"]>0)
                    sec_data[sec_name]={"avg_chg":round(avg_chg,2),"avg_rvol":round(avg_rvol,2),
                                        "bullish":bullish,"total":len(results),"stocks":results,
                                        "is_fed":sec_name in FED_SENSITIVE_SECTORS}
            st.session_state.sector_data=sec_data
    if st.session_state.sector_data:
        ss=sorted(st.session_state.sector_data.items(),key=lambda x:x[1]["avg_chg"],reverse=True)
        cs3=st.columns(3)
        for idx,(sn,si) in enumerate(ss):
            chg=si["avg_chg"]; col="#00ff88" if chg>1 else("#ffb700" if chg>0 else "#ff3d5a")
            bg="rgba(0,255,136,.06)" if chg>1 else("rgba(255,183,0,.06)" if chg>0 else "rgba(255,61,90,.06)")
            bp=int(si["bullish"]/max(si["total"],1)*100)
            fb=' <span style="font-size:9px;color:#00e5ff">📊FED</span>' if si.get("is_fed") else ""
            with cs3[idx%3]:
                st.markdown(f"""<div style="background:{bg};border:1px solid {col}44;border-radius:8px;padding:12px;margin-bottom:10px;">
                  <div style="font-family:Space Mono,monospace;font-size:10px;font-weight:700;color:#c9d1d9;">{sn}{fb}</div>
                  <div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:{col};margin:4px 0;">{chg:+.2f}%</div>
                  <div style="font-size:9px;color:#4a5568;">RVOL avg: {si["avg_rvol"]:.1f}x · Bullish: {si["bullish"]}/{si["total"]} ({bp}%)</div>
                  <div style="height:4px;background:#1c2533;border-radius:2px;margin-top:6px;overflow:hidden;">
                    <div style="width:{bp}%;height:100%;background:{col};border-radius:2px;"></div>
                  </div>
                </div>""",unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;"><div style="font-size:32px;margin-bottom:12px;">🏭</div><div>CLICK REFRESH US SECTORS</div></div>',unsafe_allow_html=True)

# ════ TAB GAP UP ════
with tab_gapup:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:14px;padding:10px 14px;background:#0d1117;border-radius:6px;border-left:3px solid #00ff88;">Detect US stocks likely to <b style="color:#00ff88">Gap Up</b> tomorrow open.</div>',unsafe_allow_html=True)
    gc1,gc2=st.columns(2)
    with gc1: gms=st.slider("Min Gap Score",1,6,3,key="gu_score")
    with gc2: gs2=st.radio("Size",["100 ⚡","200 🔥","Full 🦅"],index=1,horizontal=True,key="gu_size")
    do_gu=st.button("📈 SCAN GAP UP",type="primary",use_container_width=True,key="btn_gapup")
    if do_gu:
        _gsz=st.session_state.get("gu_size","200 🔥")
        if "100" in _gsz:   gtk=stocks_yf[:100]
        elif "200" in _gsz: gtk=stocks_yf[:200]
        else:               gtk=stocks_yf
        with st.spinner(f"Scanning {len(gtk)} stocks..."):
            gr=scan_gap_up(gtk); gr=[r for r in gr if r["Gap Score"]>=gms]
            st.session_state.gapup_results=gr
    gr=st.session_state.gapup_results
    if gr:
        gc3=[r for r in gr if "GAP UP" in r.get("Signal","")]
        gp=[r for r in gr if "POTENTIAL" in r.get("Signal","")]
        st.markdown(f"""<div class="metric-row">
          <div class="metric-card green"><div class="metric-label">Gap Confirmed 🚀</div><div class="metric-value">{len(gc3)}</div></div>
          <div class="metric-card amber"><div class="metric-label">Potential ⚡</div><div class="metric-value">{len(gp)}</div></div>
          <div class="metric-card"><div class="metric-label">Total</div><div class="metric-value">{len(gr)}</div></div>
        </div>""",unsafe_allow_html=True)
        gh='<div class="signal-grid">'
        for row in gr[:20]:
            si=int(min(row["Gap Score"],6)); bars="".join([f'<div class="sc-bar {"filled" if i<si else "empty"}" style="width:26px"></div>' for i in range(6)])
            ig="GAP UP" in row.get("Signal",""); sc5="#00ff88" if ig else "#ffb700"
            cc="#00ff88" if row["Chg %"]>0 else "#ff3d5a"
            gh+=f'''<div class="signal-card {'gacor' if ig else 'potensial'}">
              <div style="display:flex;justify-content:space-between;">
                <div><div class="sc-ticker">{row["Ticker"]}</div>
                <div class="sc-price" style="color:{cc}">${row.get("Price",0):.2f} ({row["Chg %"]:+.1f}%)</div></div>
                <div style="text-align:right"><div style="font-family:Space Mono,monospace;font-size:9px;color:#4a5568">GAP SCORE</div>
                <div style="font-family:Space Mono,monospace;font-size:22px;font-weight:700;color:{sc5}">{row["Gap Score"]}</div></div>
              </div>
              <div class="sc-signal" style="color:{sc5}">{row["Signal"]}</div>
              <div class="sc-bars">{bars}</div>
              <div class="sc-stats">
                <div class="sc-stat">RVOL <span>{row["RVOL"]}x</span></div>
                <div class="sc-stat">Close% <span>{row["Close Ratio"]:.0%}</span></div>
                <div class="sc-stat">PrevHigh <span>${row["Prev High"]:.2f}</span></div>
              </div>
              <div style="margin-top:8px;font-size:10px;color:#4a5568;font-family:Space Mono,monospace;">{row["Reasons"][:80]}</div>
            </div>'''
        gh+='</div>'; st.markdown(gh,unsafe_allow_html=True)
        df_gu=pd.DataFrame(gr)
        st.dataframe(df_gu,use_container_width=True,hide_index=True,column_config={
            "Gap Score":st.column_config.ProgressColumn("Gap Score",min_value=0,max_value=6,format="%.1f"),
            "Price":st.column_config.NumberColumn("Price",format="$%.2f"),
            "RVOL":st.column_config.NumberColumn("RVOL",format="%.2fx"),
            "Chg %":st.column_config.NumberColumn("Chg %",format="%.2f%%"),
        })
    elif not do_gu:
        st.markdown('<div style="text-align:center;padding:48px;color:#4a5568;font-family:Space Mono,monospace;"><div style="font-size:32px;margin-bottom:12px;">📈</div><div>CLICK SCAN GAP UP</div></div>',unsafe_allow_html=True)

# ════ TAB TRAILING STOP ════
with tab_trail:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:14px;padding:10px 14px;background:#0d1117;border-radius:6px;border-left:3px solid #bf5fff;">Lock profits. ATR 2x = scalp · ATR 3x = swing · % = fixed trail.</div>',unsafe_allow_html=True)
    tc1,tc2=st.columns(2)
    with tc1:
        st.markdown('<div class="settings-label">POSITION</div>',unsafe_allow_html=True)
        tr_t=st.text_input("Ticker (e.g. NVDA)",value="NVDA",key="tr_ticker").upper()
        tr_e=st.number_input("Entry Price ($)",value=100.0,step=0.5,format="%.2f",key="tr_entry")
        tr_q=st.number_input("Shares",value=100,step=10,key="tr_qty")
    with tc2:
        st.markdown('<div class="settings-label">TRAILING SETTINGS</div>',unsafe_allow_html=True)
        tr_m=st.radio("Method",["ATR","Persen","Swing Low"],key="tr_method")
        if tr_m=="ATR":      tr_am=st.slider("ATR Multiplier",1.0,5.0,2.0,0.5,key="tr_atr_m")
        elif tr_m=="Persen": tr_p=st.slider("Trailing %",1.0,10.0,3.0,0.5,key="tr_pct")
        tr_al=st.toggle("🔔 Telegram Alert",value=True,key="tr_alert")
    if st.button("🎯 CALCULATE TRAILING STOP",type="primary",use_container_width=True,key="btn_trail"):
        with st.spinner(f"Fetching {tr_t}..."):
            try:
                df_tr=_fetch_ticker(tr_t,"7d","15m")  # ← no more yf.download()!
                if df_tr is not None and len(df_tr)>=20:
                    df_tr=apply_intraday_indicators(df_tr)
                    cur=float(df_tr["Close"].iloc[-1]); av=float(df_tr["ATR"].iloc[-1])
                    if tr_m=="ATR":      res=calc_trailing_stop(tr_e,cur,av,"ATR",tr_am)
                    elif tr_m=="Persen": res=calc_trailing_stop(tr_e,cur,av,"Persen",pct=tr_p)
                    else:                res=calc_trailing_stop(tr_e,cur,av,"Swing Low")
                    stop=res["stop"]; dist=res["distance"]
                    pf=res["profit_float"]; pl=res["profit_locked"]; ip=res["is_profitable"]
                    pusd=(cur-tr_e)*tr_q; lusd=max(0,(stop-tr_e)*tr_q)
                    _r=_idr_rate
                    ci=int(cur*_r); si2=int(stop*_r); ai=int(av*_r)
                    ei=int(tr_e*_r); pi2=int(pusd*_r); li2=int(lusd*_r)
                    sc6="#00ff88" if ip else "#ff3d5a"; pc2="#00ff88" if pusd>=0 else "#ff3d5a"
                    st.markdown(f"""<div style="background:#0d1117;border:1px solid {sc6}44;border-radius:10px;padding:20px;margin-top:12px;">
                      <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:12px;">
                        💱 Kurs: Rp{_r:,.0f}/USD ({_idr_src}) · Entry: ${tr_e:.2f} = Rp{ei:,}
                      </div>
                      <div class="metric-row">
                        <div class="metric-card"><div class="metric-label">Harga Sekarang</div>
                          <div class="metric-value" style="color:#00e5ff;font-size:18px;">Rp{ci:,}</div>
                          <div class="metric-sub">${cur:.2f} · ATR Rp{ai:,}</div></div>
                        <div class="metric-card" style="border-top-color:{sc6}"><div class="metric-label">🎯 Trailing Stop</div>
                          <div class="metric-value" style="color:{sc6};font-size:18px;">Rp{si2:,}</div>
                          <div class="metric-sub">${stop:.2f} · Jarak Rp{int(dist*_r):,}</div></div>
                        <div class="metric-card" style="border-top-color:{pc2}"><div class="metric-label">Float P&L</div>
                          <div class="metric-value" style="color:{pc2}">{pf:+.1f}%</div>
                          <div class="metric-sub">Rp{pi2:+,} (${pusd:+,.2f})</div></div>
                        <div class="metric-card" style="border-top-color:#00ff88"><div class="metric-label">Locked 🔒</div>
                          <div class="metric-value" style="color:#00ff88">{pl:+.1f}%</div>
                          <div class="metric-sub">Rp{li2:+,} (${lusd:+,.2f})</div></div>
                      </div>
                      <div style="margin-top:12px;font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">
                        💼 {tr_q} shares · {"✅ Profit locked!" if ip else "⚠️ Stop di bawah entry"}
                      </div>
                    </div>""",unsafe_allow_html=True)
                    if tr_al and TOKEN and CHAT_ID:
                        nt=datetime.now(ny_tz)
                        mt=(f"🎯 *TRAILING STOP UPDATE*\n⏰ `{nt.strftime('%H:%M:%S')} ET`\n{'━'*28}\n"
                            f"📌 *{tr_t}* | {tr_m}\n💰 Entry:`${tr_e:.2f}` (Rp{ei:,}) → Now:`${cur:.2f}` (Rp{ci:,})\n"
                            f"🎯 Stop:`Rp{si2:,}` (${stop:.2f}) | Locked:`{pl:+.1f}%`\n"
                            f"📊 Float:`{pf:+.1f}%` (Rp{pi2:+,})\n{'━'*28}\n⚠️ _NOT financial advice!_")
                        try:
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                          data={"chat_id":CHAT_ID,"text":mt,"parse_mode":"Markdown"},timeout=10)
                            st.success("📡 Alert sent!")
                        except: pass
                else:
                    st.error(f"Data for {tr_t} unavailable.")
            except Exception as ex:
                st.error(f"Error: {str(ex)[:80]}")

# ════ TAB BACKTEST ════
with tab_backtest:
    st.markdown('<div class="section-title">Backtest Engine · 15M Intraday · US Stocks</div>',unsafe_allow_html=True)
    bt1,bt2,bt3,bt4=st.columns(4)
    bt_mode=bt1.selectbox("Mode",["Scalping ⚡","Momentum 🚀","Reversal 🎯","Bagger 💎"],key="bt_mode")
    bt_sc2=bt2.slider("Min Score",0,6,4,key="bt_sc")
    bt_fwd=int(bt3.number_input("Hold (bars)",value=4,step=1,min_value=1,max_value=20))
    bt_sl=bt4.number_input("SL mult (xATR)",value=0.8,step=0.1,min_value=0.1,max_value=3.0)
    st.caption(f"Hold {bt_fwd} bars × 15 min = ~{bt_fwd*15} minutes per trade")
    if st.button("🚀 Run Backtest",type="primary",key="bt_run"):
        dd=st.session_state.get("data_dict",{})
        if not dd: st.warning("Run Scanner first!")
        else:
            bt_r=[]; bt_tr={"▲ UP":[],"▼ DOWN":[],"◆ SIDE":[]}
            bt_ses={"Pre/Open 9:30-11":[],"Midday 11-14":[],"Power Hour 14-16":[]}
            bt_sc3={4:[],5:[],6:[]}
            bpb=st.progress(0); sample=list(dd.keys())[:80]
            for bi,ticker in enumerate(sample):
                bpb.progress((bi+1)/len(sample))
                try:
                    d=dd[ticker].copy()
                    if len(d)<60: continue
                    d=apply_intraday_indicators(d)
                    for ii in range(50,len(d)-bt_fwd):
                        r0=d.iloc[ii]; r1=d.iloc[ii-1]; r2=d.iloc[ii-2]
                        if bt_mode=="Scalping ⚡":   sc,_,_=score_scalping(r0,r1,r2)
                        elif bt_mode=="Momentum 🚀": sc,_,_=score_momentum(r0,r1,r2)
                        elif bt_mode=="Bagger 💎":   sc,_,_=score_bagger(r0,r1,r2,d.iloc[:ii+1])
                        else:                         sc,_,_=score_reversal(r0,r1,r2)
                        if sc<bt_sc2: continue
                        en=float(r0["Close"]); av=float(r0["ATR"]) if not np.isnan(float(r0["ATR"])) else en*0.005
                        if bt_mode=="Scalping ⚡":   tp2=en+1.5*av;sl2=en-bt_sl*av
                        elif bt_mode=="Momentum 🚀": tp2=en+2.0*av;sl2=en-bt_sl*av
                        elif bt_mode=="Bagger 💎":   tp2=en+3.0*av;sl2=en-1.0*av
                        else:                         tp2=en+2.5*av;sl2=en-bt_sl*av
                        ex=float(d.iloc[ii+bt_fwd]["Close"])
                        for fi in range(1,bt_fwd+1):
                            bar=d.iloc[ii+fi]
                            if float(bar["High"])>=tp2: ex=tp2; break
                            if float(bar["Low"])<=sl2:  ex=sl2; break
                        ret=(ex-en)/en*100; bt_r.append(ret)
                        e9=float(r0["EMA9"]); e21=float(r0["EMA21"]); e50=float(r0["EMA50"])
                        tr2="▲ UP" if e9>e21>e50 else("▼ DOWN" if e9<e21<e50 else "◆ SIDE")
                        bt_tr[tr2].append(ret)
                        try:
                            hr=d.index[ii].hour
                            if 9<=hr<11:    bt_ses["Pre/Open 9:30-11"].append(ret)
                            elif 11<=hr<14: bt_ses["Midday 11-14"].append(ret)
                            elif 14<=hr<16: bt_ses["Power Hour 14-16"].append(ret)
                        except: pass
                        si2=int(sc)
                        if si2 in bt_sc3: bt_sc3[si2].append(ret)
                except: continue
            bpb.empty()
            if not bt_r: st.warning("No matching trades. Lower Min Score.")
            else:
                arr=np.array(bt_r); wr=len(arr[arr>0])/len(arr)*100
                avg=np.mean(arr); med=np.median(arr)
                pf=arr[arr>0].sum()/max(abs(arr[arr<0].sum()),0.01)
                mxdd=arr[arr<0].min() if len(arr[arr<0])>0 else 0
                st.markdown(f"""<div class="bt-result">
                  <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;letter-spacing:2px;margin-bottom:14px;">{len(arr)} TRADES · SCORE≥{bt_sc2} · HOLD {bt_fwd} BARS (~{bt_fwd*15}M) · {bt_mode}</div>
                  <div style="display:flex;flex-wrap:wrap;">
                    <span class="bt-metric"><div class="bt-metric-val" style="color:{'#00ff88' if wr>=55 else '#ffb700' if wr>=50 else '#ff3d5a'}">{wr:.1f}%</div><div class="bt-metric-lbl">Win Rate</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:{'#00ff88' if avg>0 else '#ff3d5a'}">{avg:+.2f}%</div><div class="bt-metric-lbl">Avg Return</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#00e5ff">{med:+.2f}%</div><div class="bt-metric-lbl">Median</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:{'#00ff88' if pf>=1.5 else '#ffb700' if pf>=1 else '#ff3d5a'}">{pf:.2f}x</div><div class="bt-metric-lbl">Profit Factor</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#ff3d5a">{mxdd:.1f}%</div><div class="bt-metric-lbl">Max Loss</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#00ff88">{sum(1 for x in bt_r if x>0)}</div><div class="bt-metric-lbl">TP Hits</div></span>
                    <span class="bt-metric"><div class="bt-metric-val" style="color:#ff3d5a">{sum(1 for x in bt_r if x<0)}</div><div class="bt-metric-lbl">SL Hits</div></span>
                  </div>
                </div>""",unsafe_allow_html=True)
                ttr,tse,tsc2=st.tabs(["📈 By Trend","⏰ By Session","🎯 By Score"])
                with ttr:
                    for tn,vals in bt_tr.items():
                        if not vals: continue
                        a=np.array(vals); wr2=len(a[a>0])/len(a)*100; avg2=np.mean(a)
                        col="#00ff88" if wr2>=55 else("#ffb700" if wr2>=50 else "#ff3d5a")
                        st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;"><span style="font-family:Space Mono,monospace;font-size:12px;color:#c9d1d9;">{tn}</span><span style="font-family:Space Mono,monospace;font-size:11px;color:{col};">{wr2:.1f}% WR · avg {avg2:+.2f}% · {len(a)} trades</span></div><div style="height:8px;background:var(--border);border-radius:4px;overflow:hidden;margin-top:4px;"><div style="width:{int(wr2)}%;height:100%;background:{col};border-radius:4px;"></div></div></div>',unsafe_allow_html=True)
                with tse:
                    for sn,vals in bt_ses.items():
                        if not vals: continue
                        a=np.array(vals); wr3=len(a[a>0])/len(a)*100; avg3=np.mean(a)
                        col="#00ff88" if wr3>=55 else("#ffb700" if wr3>=50 else "#ff3d5a")
                        st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;"><span style="font-family:Space Mono,monospace;font-size:12px;color:#c9d1d9;">⏰ {sn}</span><span style="font-family:Space Mono,monospace;font-size:11px;color:{col};">{wr3:.1f}% WR · avg {avg3:+.2f}% · {len(a)} trades</span></div><div style="height:8px;background:var(--border);border-radius:4px;overflow:hidden;margin-top:4px;"><div style="width:{int(wr3)}%;height:100%;background:{col};border-radius:4px;"></div></div></div>',unsafe_allow_html=True)
                with tsc2:
                    for sl3 in [4,5,6]:
                        vals=bt_sc3.get(sl3,[])
                        if not vals: continue
                        a=np.array(vals); wr4=len(a[a>0])/len(a)*100; avg4=np.mean(a)
                        col="#00ff88" if wr4>=55 else("#ffb700" if wr4>=50 else "#ff3d5a")
                        st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;"><span style="font-family:Space Mono,monospace;font-size:12px;color:#c9d1d9;">Score {sl3} [{"█"*sl3+"░"*(6-sl3)}]</span><span style="font-family:Space Mono,monospace;font-size:11px;color:{col};">{wr4:.1f}% WR · avg {avg4:+.2f}% · {len(a)} trades</span></div><div style="height:8px;background:var(--border);border-radius:4px;overflow:hidden;margin-top:4px;"><div style="width:{int(wr4)}%;height:100%;background:{col};border-radius:4px;"></div></div></div>',unsafe_allow_html=True)

# ════ FOOTER + AUTO-REFRESH ════
_nf=datetime.now(ny_tz).timestamp()
if st.session_state.last_scan_time:
    _r2=max(0,300-(_nf-st.session_state.last_scan_time)); m2=int(_r2//60); s2=int(_r2%60)
    _lt2=datetime.fromtimestamp(st.session_state.last_scan_time,ny_tz).strftime("%H:%M:%S")
    ti=f"⏱️ Next auto-scan: <span style='color:#00e5ff'>{m2:02d}:{s2:02d}</span> · Last: <span style='color:#2dd4bf'>{_lt2} ET</span>"
else:
    ti="⏱️ Click Scan to start"

st.markdown(f"""
<div style="margin-top:28px;padding-top:14px;border-top:1px solid #1c2533;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;">
  <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">🦅 US Turbo v1.2 · NYSE/NASDAQ · 15M · Zero Rate Limit ✅</div>
  <div style="font-family:Space Mono,monospace;font-size:10px;color:#4a5568;">{ti}</div>
</div>
<div style="font-family:Space Mono,monospace;font-size:9px;color:#2d3748;text-align:center;margin-top:8px;">⚠️ NOT financial advice · For educational purposes only · DYOR always</div>""",unsafe_allow_html=True)

if st.session_state.last_scan_time:
    if datetime.now(ny_tz).timestamp()-st.session_state.last_scan_time>=295:
        time.sleep(5); st.rerun()
