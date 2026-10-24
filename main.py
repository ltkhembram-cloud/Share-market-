import os, time
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)
API_KEY = os.getenv("TWELVE_DATA_API_KEY", "").strip()
CACHE_SECONDS = int(os.getenv("MARKET_CACHE_SECONDS", "30"))
cache = {}
STOCKS = [
 {"symbol":"AAPL","name":"Apple","exchange":"NASDAQ","currency":"USD","demo_price":230.0},
 {"symbol":"MSFT","name":"Microsoft","exchange":"NASDAQ","currency":"USD","demo_price":420.0},
 {"symbol":"NVDA","name":"NVIDIA","exchange":"NASDAQ","currency":"USD","demo_price":135.0},
 {"symbol":"GOOGL","name":"Alphabet","exchange":"NASDAQ","currency":"USD","demo_price":175.0},
 {"symbol":"AMZN","name":"Amazon","exchange":"NASDAQ","currency":"USD","demo_price":205.0},
 {"symbol":"TSLA","name":"Tesla","exchange":"NASDAQ","currency":"USD","demo_price":330.0},
 {"symbol":"RELIANCE:NSE","name":"Reliance Industries","exchange":"NSE","currency":"INR","demo_price":1450.0},
 {"symbol":"TCS:NSE","name":"Tata Consultancy Services","exchange":"NSE","currency":"INR","demo_price":4000.0},
 {"symbol":"INFY:NSE","name":"Infosys","exchange":"NSE","currency":"INR","demo_price":1600.0},
 {"symbol":"HDFCBANK:NSE","name":"HDFC Bank","exchange":"NSE","currency":"INR","demo_price":1700.0},
]

def provider_get(path, params):
    if not API_KEY: raise RuntimeError("TWELVE_DATA_API_KEY is not configured")
    r = requests.get("https://api.twelvedata.com/"+path,
                     params={**params, "apikey":API_KEY}, timeout=8)
    r.raise_for_status()
    data = r.json()
    if data.get("status") == "error": raise RuntimeError(data.get("message","Provider error"))
    return data

def quote(stock):
    symbol, now = stock["symbol"], time.time()
    if symbol in cache and now-cache[symbol][0] < CACHE_SECONDS: return cache[symbol][1]
    base = {k:stock[k] for k in ("symbol","name","exchange","currency")}
    if API_KEY:
        try:
            price = float(provider_get("price", {"symbol":symbol})["price"])
            result = {**base,"price":price,"source":"Twelve Data","is_live":True,
                      "updated_at":datetime.now(timezone.utc).isoformat(),
                      "note":"Real-time/delayed status depends on provider plan."}
            cache[symbol] = (now,result)
            return result
        except Exception as e:
            return {**base,"price":None,"source":"unavailable","is_live":False,
                    "updated_at":None,"note":"Market data unavailable: "+str(e)[:140]}
    return {**base,"price":stock["demo_price"],"source":"Demo data","is_live":False,
            "updated_at":None,"note":"Illustrative demo price, not a current quote."}

@app.get("/")
def home(): return render_template("index.html")

@app.get("/api/market")
def market():
    filt=request.args.get("market","all").lower()
    chosen=[s for s in STOCKS if filt=="all" or (filt=="us" and s["currency"]=="USD") or (filt=="india" and s["currency"]=="INR")]
    return jsonify({"stocks":[quote(s) for s in chosen],"provider_configured":bool(API_KEY),
                    "server_time":datetime.now(timezone.utc).isoformat()})

@app.get("/api/history")
def history():
    symbol=request.args.get("symbol","")
    if symbol not in {s["symbol"] for s in STOCKS}: return jsonify({"error":"Unknown symbol"}),400
    if not API_KEY: return jsonify({"symbol":symbol,"values":[],"source":"Demo data","message":"Configure API key for historical prices."})
    try:
        d=provider_get("time_series",{"symbol":symbol,"interval":"1day","outputsize":30,"format":"JSON"})
        vals=[{"datetime":x.get("datetime"),"close":float(x["close"])} for x in d.get("values",[]) if x.get("close")]
        return jsonify({"symbol":symbol,"values":list(reversed(vals)),"source":"Twelve Data"})
    except Exception as e: return jsonify({"symbol":symbol,"values":[],"error":str(e)[:160]}),502

@app.get("/health")
def health(): return jsonify({"ok":True})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")),debug=False)
