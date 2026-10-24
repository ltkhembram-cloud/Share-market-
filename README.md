# StockVerse: Market Quest

A responsive stock-market **paper-trading game** for beginners. It uses virtual money only.

## Local setup
1. Install Python 3.10+.
2. Run `pip install -r requirements.txt`.
3. Optional: set `TWELVE_DATA_API_KEY` in your environment.
4. Run `python main.py`.
5. Open http://127.0.0.1:5000.

Without a key, the app uses clearly labelled illustrative demo prices, not current market prices. With a key, the server requests quotes and daily history from Twelve Data. Data may be delayed, rate-limited, unavailable, or paid depending on plan and exchange entitlements. Confirm provider symbol conventions for Indian shares.

## Deploy on Render
1. Push this folder to GitHub. Never commit `.env` or API keys.
2. Create a Render **Web Service** linked to the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 30`
5. Add `TWELVE_DATA_API_KEY` under Render Environment settings.
6. Deploy and open the URL Render provides.

## Included
- US: AAPL, MSFT, NVDA, GOOGL, AMZN, TSLA
- India: Reliance, TCS, Infosys, HDFC Bank
- Virtual buy/sell, INR and USD cash wallets, positions, average cost, P/L
- Learning missions, XP, level progression, trade history
- Server-side market API key; local browser save

## MVP limitations
This is educational software, not investment advice or a broker. No real orders or money are used. Portfolio state is saved in browser localStorage and is device/browser-specific; clearing it removes the save. Client-side paper-trading state can be edited and is not suitable for prizes, rankings, or multi-user records. Provider configuration does not guarantee real-time access.
