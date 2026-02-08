# Stock Information Tracker - Quick Usage Guide

## Simple Usage (Just Type the Ticker!)

You can now run the script in two easy ways:

### Method 1: Using the wrapper script (Easiest!)
```bash
./stock AAPL
./stock MSFT
./stock TSLA
```

### Method 2: Direct Python command
```bash
python3 "Stock Trader Information.py" AAPL
```

## Features

✅ **Works with ALL companies** - Any ticker symbol on Yahoo Finance:
- NASDAQ companies (AAPL, MSFT, GOOGL, etc.)
- NYSE companies (JPM, JNJ, WMT, etc.)
- International stocks
- ETFs and indices

✅ **View popular NASDAQ companies:**
```bash
./stock --list
# or
./stock --nasdaq
```

✅ **Get help:**
```bash
./stock --help
```

## Examples

```bash
# Technology companies
./stock AAPL    # Apple
./stock MSFT    # Microsoft
./stock GOOGL   # Google/Alphabet
./stock NVDA    # NVIDIA
./stock META    # Meta/Facebook

# Other sectors
./stock TSLA    # Tesla
./stock AMZN    # Amazon
./stock NFLX    # Netflix
./stock COST    # Costco
```

## What You Get

For each company, the script provides:
- 📊 Basic company information (name, sector, industry, website)
- 💰 Current market data (price, volume, day range, 52-week range)
- 📈 Valuation metrics (market cap, P/E ratio, price-to-book, etc.)
- 💵 Financial performance (revenue, profit margins, EPS, growth)
- 💸 Dividend information
- 🎯 Analyst recommendations
- 📉 Historical stock data (with option to save to CSV)

## Note

The script works with **any valid ticker symbol** on Yahoo Finance, not just NASDAQ. It automatically fetches data for companies listed on:
- NASDAQ
- NYSE
- Other exchanges supported by Yahoo Finance


