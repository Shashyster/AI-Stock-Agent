# Stock Information Web Application

A beautiful ChatGPT-like web interface for fetching real-time stock information. Just type a ticker symbol and get comprehensive company data!

## 🚀 Quick Start

### 1. Install Dependencies (if not already installed)
```bash
pip3 install -r requirements.txt
```

### 2. Start the Web Server

**Option A: Using the startup script**
```bash
./start_web.sh
```

**Option B: Direct Python command**
```bash
python3 app.py
```

### 3. Open in Browser

Once the server starts, open your browser and go to:
```
http://localhost:5001
```

## 📱 How to Use

1. **Type a ticker symbol** in the input box at the bottom (e.g., `AAPL`, `MSFT`, `TSLA`)
2. **Press Enter** or click the send button
3. **View comprehensive stock information** including:
   - Basic company information
   - Current market data
   - Valuation metrics
   - Financial performance
   - Dividend information
   - Analyst recommendations

## ✨ Features

- **ChatGPT-like Interface**: Clean, modern design with a chat-style interface
- **Real-time Data**: Fetches live stock information from Yahoo Finance
- **Comprehensive Information**: Get all the details you need about any stock
- **Quick Access**: Click on example tickers to quickly search
- **Responsive Design**: Works on desktop and mobile devices

## 🎯 Example Tickers

Try these popular stocks:
- **AAPL** - Apple Inc.
- **MSFT** - Microsoft Corporation
- **GOOGL** - Alphabet Inc. (Google)
- **TSLA** - Tesla, Inc.
- **NVDA** - NVIDIA Corporation
- **META** - Meta Platforms Inc. (Facebook)
- **AMZN** - Amazon.com Inc.

## 📊 Information Provided

For each stock, you'll get:

- **Basic Information**: Company name, sector, industry, country, website, description
- **Market Data**: Current price, previous close, open, day range, 52-week range, volume
- **Valuation Metrics**: Market cap, enterprise value, P/E ratios, price-to-book, price-to-sales
- **Financial Performance**: Revenue, profit margins, ROA, ROE, EPS, growth rates
- **Dividend Information**: Dividend rate, yield, payout ratio, ex-dividend date
- **Analyst Recommendations**: Target prices, recommendations, number of analyst opinions

## 🛠️ Technical Details

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Data Source**: Yahoo Finance (via yfinance library)
- **Port**: 5001 (default)

## 🔧 Troubleshooting

**Port already in use?**
- Change the port in `app.py` (line with `app.run(port=5001)`)
- Or kill the process using the port

**Can't connect to Yahoo Finance?**
- Check your internet connection
- Some tickers may be invalid or delisted
- Try again in a few moments (rate limiting)

**Module not found errors?**
- Make sure all dependencies are installed: `pip3 install -r requirements.txt`

## 📝 Notes

- The app works with any valid ticker symbol on Yahoo Finance
- Supports NASDAQ, NYSE, and other exchanges
- Data is fetched in real-time from Yahoo Finance
- No API keys required!

Enjoy exploring stock information! 📈

