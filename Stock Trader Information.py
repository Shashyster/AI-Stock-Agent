#!/usr/bin/env python3
"""
Company & Stock Information Tracker
Fetches comprehensive company information and historical stock data
"""

import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
import sys
import ssl
import urllib3

# Disable SSL warnings for urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CompanyInfoTracker:
    def __init__(self):
        self.company_name = None
        self.ticker = None
        self.stock_data = None
        
        # Popular NASDAQ companies for reference
        self.nasdaq_examples = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc. (Google)',
            'AMZN': 'Amazon.com Inc.',
            'NVDA': 'NVIDIA Corporation',
            'META': 'Meta Platforms Inc. (Facebook)',
            'TSLA': 'Tesla, Inc.',
            'AMD': 'Advanced Micro Devices',
            'INTC': 'Intel Corporation',
            'NFLX': 'Netflix, Inc.',
            'COST': 'Costco Wholesale Corporation',
            'AVGO': 'Broadcom Inc.',
            'PEP': 'PepsiCo, Inc.',
            'CSCO': 'Cisco Systems, Inc.',
            'ADBE': 'Adobe Inc.',
            'CMCSA': 'Comcast Corporation',
            'TXN': 'Texas Instruments Incorporated',
            'QCOM': 'QUALCOMM Incorporated',
            'AMGN': 'Amgen Inc.',
            'ISRG': 'Intuitive Surgical, Inc.'
        }
        
    def search_ticker(self, company_name):
        """Search for company ticker symbol"""
        self.company_name = company_name
        
        # Try to get ticker using yfinance
        try:
            # First, try as if it's already a ticker
            ticker = yf.Ticker(company_name.upper())
            info = ticker.info
            
            if 'symbol' in info and info['symbol']:
                self.ticker = company_name.upper()
                return self.ticker
        except:
            pass
        
        print(f"\nSearching for ticker symbol for '{company_name}'...")
        print("If known, you can enter the ticker symbol directly (e.g., AAPL for Apple)")
        
        return None
    
    def get_company_info(self):
        """Fetch comprehensive company information"""
        if not self.ticker:
            print("No ticker symbol available.")
            return None
        
        try:
            # Create ticker with session that handles SSL better
            ticker = yf.Ticker(self.ticker)
            
            # First, test connectivity with a simple historical data fetch
            try:
                test_data = ticker.history(period="1d")
                if test_data.empty:
                    print(f"Warning: Could not fetch data for ticker '{self.ticker}'. It may be invalid or delisted.")
            except Exception as test_error:
                print(f"Connection test failed: {test_error}")
                print("Please check your internet connection and try again.")
                return None
            
            # Try to get info
            info = None
            try:
                info = ticker.info
            except Exception as fetch_error:
                # If info fails, try to get at least basic data from history
                print(f"Warning: Could not fetch detailed info: {fetch_error}")
                print("Attempting to retrieve basic information from price data...")
                
                # Get basic info from historical data  
                hist = ticker.history(period="5d")
                if not hist.empty:
                    latest = hist.iloc[-1]
                    info = {
                        'symbol': self.ticker,
                        'longName': self.ticker,
                        'regularMarketPrice': float(latest['Close']),
                        'previousClose': float(hist.iloc[-2]['Close']) if len(hist) > 1 else float(latest['Close']),
                    }
                else:
                    print("Unable to fetch any data for this ticker.")
                    return None
            
            # Check if info is empty or invalid
            if not info or len(info) == 0:
                print(f"Error: No data returned for ticker '{self.ticker}'.")
                print("Possible reasons:")
                print("  - The ticker symbol may be incorrect")
                print("  - Yahoo Finance may be temporarily unavailable")
                print("  - Network connectivity issues")
                return None
            
            # Check if we got an error response (sometimes Yahoo returns minimal data)
            if len(info) < 5:
                print(f"Warning: Limited data returned for ticker '{self.ticker}'.")
                print("The ticker may be invalid or delisted.")
                # Still try to display what we have
            
            print("\n" + "="*80)
            print(f"COMPANY INFORMATION: {info.get('longName', 'N/A')}")
            print("="*80)
            
            # Basic Information
            print("\n--- BASIC INFORMATION ---")
            print(f"Symbol: {info.get('symbol', 'N/A')}")
            print(f"Company Name: {info.get('longName', 'N/A')}")
            print(f"Sector: {info.get('sector', 'N/A')}")
            print(f"Industry: {info.get('industry', 'N/A')}")
            print(f"Country: {info.get('country', 'N/A')}")
            print(f"Website: {info.get('website', 'N/A')}")
            print(f"Description: {info.get('longBusinessSummary', 'N/A')[:300]}...")
            
            # Market Data
            print("\n--- CURRENT MARKET DATA ---")
            print(f"Current Price: ${info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))}")
            print(f"Previous Close: ${info.get('previousClose', 'N/A')}")
            print(f"Open: ${info.get('open', 'N/A')}")
            print(f"Day Range: ${info.get('dayLow', 'N/A')} - ${info.get('dayHigh', 'N/A')}")
            print(f"52 Week Range: ${info.get('fiftyTwoWeekLow', 'N/A')} - ${info.get('fiftyTwoWeekHigh', 'N/A')}")
            print(f"Volume: {info.get('volume', 'N/A'):,}" if isinstance(info.get('volume'), (int, float)) else f"Volume: {info.get('volume', 'N/A')}")
            print(f"Average Volume: {info.get('averageVolume', 'N/A'):,}" if isinstance(info.get('averageVolume'), (int, float)) else f"Average Volume: {info.get('averageVolume', 'N/A')}")
            
            # Valuation Metrics
            print("\n--- VALUATION METRICS ---")
            market_cap = info.get('marketCap', 'N/A')
            if isinstance(market_cap, (int, float)):
                print(f"Market Cap: ${market_cap:,.0f} ({self._format_large_number(market_cap)})")
            else:
                print(f"Market Cap: {market_cap}")
            
            print(f"Enterprise Value: {self._format_large_number(info.get('enterpriseValue', 'N/A'))}")
            print(f"P/E Ratio (Trailing): {info.get('trailingPE', 'N/A')}")
            print(f"P/E Ratio (Forward): {info.get('forwardPE', 'N/A')}")
            print(f"PEG Ratio: {info.get('pegRatio', 'N/A')}")
            print(f"Price to Book: {info.get('priceToBook', 'N/A')}")
            print(f"Price to Sales: {info.get('priceToSalesTrailing12Months', 'N/A')}")
            
            # Financial Performance
            print("\n--- FINANCIAL PERFORMANCE ---")
            print(f"Revenue (TTM): {self._format_large_number(info.get('totalRevenue', 'N/A'))}")
            print(f"Revenue Per Share: ${info.get('revenuePerShare', 'N/A')}")
            print(f"Profit Margin: {self._format_percentage(info.get('profitMargins', 'N/A'))}")
            print(f"Operating Margin: {self._format_percentage(info.get('operatingMargins', 'N/A'))}")
            print(f"Return on Assets: {self._format_percentage(info.get('returnOnAssets', 'N/A'))}")
            print(f"Return on Equity: {self._format_percentage(info.get('returnOnEquity', 'N/A'))}")
            print(f"Earnings Per Share (EPS): ${info.get('trailingEps', 'N/A')}")
            print(f"Quarterly Earnings Growth: {self._format_percentage(info.get('earningsQuarterlyGrowth', 'N/A'))}")
            print(f"Revenue Growth: {self._format_percentage(info.get('revenueGrowth', 'N/A'))}")
            
            # Dividend Information
            print("\n--- DIVIDEND INFORMATION ---")
            print(f"Dividend Rate: ${info.get('dividendRate', 'N/A')}")
            print(f"Dividend Yield: {self._format_percentage(info.get('dividendYield', 'N/A'))}")
            print(f"Payout Ratio: {self._format_percentage(info.get('payoutRatio', 'N/A'))}")
            print(f"Ex-Dividend Date: {self._format_date(info.get('exDividendDate', 'N/A'))}")
            
            # Analyst Recommendations
            print("\n--- ANALYST RECOMMENDATIONS ---")
            print(f"Recommendation: {info.get('recommendationKey', 'N/A').upper() if info.get('recommendationKey') else 'N/A'}")
            print(f"Target Mean Price: ${info.get('targetMeanPrice', 'N/A')}")
            print(f"Target High Price: ${info.get('targetHighPrice', 'N/A')}")
            print(f"Target Low Price: ${info.get('targetLowPrice', 'N/A')}")
            print(f"Number of Analyst Opinions: {info.get('numberOfAnalystOpinions', 'N/A')}")
            
            # Company Officers
            if 'companyOfficers' in info and info['companyOfficers']:
                print("\n--- KEY EXECUTIVES ---")
                for officer in info['companyOfficers'][:5]:  # Top 5 officers
                    print(f"{officer.get('title', 'N/A')}: {officer.get('name', 'N/A')}")
            
            return info
            
        except Exception as e:
            print(f"Error fetching company information: {e}")
            return None
    
    def get_historical_data(self, period="max"):
        """Fetch historical stock data"""
        if not self.ticker:
            print("No ticker symbol available.")
            return None
        
        try:
            ticker = yf.Ticker(self.ticker)
            
            print(f"\n--- FETCHING HISTORICAL DATA (Period: {period}) ---")
            hist = ticker.history(period=period)
            
            if hist.empty:
                print("No historical data available.")
                return None
            
            self.stock_data = hist
            
            print(f"\nHistorical data retrieved from {hist.index[0].date()} to {hist.index[-1].date()}")
            print(f"Total trading days: {len(hist)}")
            
            # Display summary statistics
            print("\n--- PRICE STATISTICS (All Time) ---")
            print(f"Highest Close: ${hist['Close'].max():.2f} on {hist['Close'].idxmax().date()}")
            print(f"Lowest Close: ${hist['Close'].min():.2f} on {hist['Close'].idxmin().date()}")
            print(f"Average Close: ${hist['Close'].mean():.2f}")
            print(f"Current Price: ${hist['Close'].iloc[-1]:.2f}")
            
            # Calculate returns
            total_return = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            print(f"Total Return: {total_return:.2f}%")
            
            # Year by year performance
            self._display_yearly_performance(hist)
            
            return hist
            
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None
    
    def _display_yearly_performance(self, hist):
        """Display year-by-year stock performance"""
        print("\n--- YEARLY PERFORMANCE ---")
        
        hist_copy = hist.copy()
        hist_copy['Year'] = hist_copy.index.year
        
        yearly_data = hist_copy.groupby('Year').agg({
            'Open': 'first',
            'Close': 'last',
            'High': 'max',
            'Low': 'min',
            'Volume': 'sum'
        })
        
        yearly_data['Return %'] = ((yearly_data['Close'] - yearly_data['Open']) / yearly_data['Open'] * 100)
        
        print(f"\n{'Year':<8} {'Open':<12} {'Close':<12} {'High':<12} {'Low':<12} {'Return %':<12}")
        print("-" * 80)
        
        for year, row in yearly_data.iterrows():
            print(f"{year:<8} ${row['Open']:<11.2f} ${row['Close']:<11.2f} ${row['High']:<11.2f} ${row['Low']:<11.2f} {row['Return %']:<11.2f}%")
    
    def save_to_csv(self, filename=None):
        """Save historical data to CSV"""
        if self.stock_data is None or self.stock_data.empty:
            print("No data to save.")
            return
        
        if filename is None:
            filename = f"{self.ticker}_historical_data_{datetime.now().strftime('%Y%m%d')}.csv"
        
        try:
            self.stock_data.to_csv(filename)
            print(f"\nHistorical data saved to: {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def _format_large_number(self, num):
        """Format large numbers in readable format"""
        if not isinstance(num, (int, float)):
            return str(num)
        
        if num >= 1_000_000_000_000:
            return f"${num/1_000_000_000_000:.2f}T"
        elif num >= 1_000_000_000:
            return f"${num/1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"${num/1_000_000:.2f}M"
        else:
            return f"${num:,.2f}"
    
    def _format_percentage(self, num):
        """Format percentage values"""
        if not isinstance(num, (int, float)):
            return str(num)
        return f"{num*100:.2f}%"
    
    def _format_date(self, timestamp):
        """Format Unix timestamp to readable date"""
        if not isinstance(timestamp, (int, float)):
            return str(timestamp)
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        except:
            return str(timestamp)
    
    def list_nasdaq_examples(self):
        """Display popular NASDAQ companies"""
        print("\n" + "="*80)
        print("POPULAR NASDAQ COMPANIES (Examples)")
        print("="*80)
        print("\nYou can use any of these ticker symbols:")
        print(f"\n{'Ticker':<10} {'Company Name':<50}")
        print("-" * 80)
        for ticker, name in sorted(self.nasdaq_examples.items()):
            print(f"{ticker:<10} {name:<50}")
        print("\nNote: This script works with ANY valid ticker symbol on Yahoo Finance,")
        print("including all NASDAQ, NYSE, and other exchange-listed companies.")
        print("="*80)


def main():
    print("="*80)
    print("COMPANY & STOCK INFORMATION TRACKER")
    print("="*80)
    
    tracker = CompanyInfoTracker()
    
    # Get company name or ticker
    if len(sys.argv) > 1:
        company_input = " ".join(sys.argv[1:]).strip()
        
        # Check for special commands
        if company_input.lower() in ['--help', '-h', 'help']:
            print("\nUsage:")
            print("  python3 'Stock Trader Information.py' <TICKER>")
            print("  ./stock <TICKER>")
            print("\nExamples:")
            print("  ./stock AAPL")
            print("  ./stock MSFT")
            print("  ./stock TSLA")
            print("\nSpecial commands:")
            print("  --list or --nasdaq  : Show popular NASDAQ companies")
            print("  --help or -h        : Show this help message")
            return
        elif company_input.lower() in ['--list', '--nasdaq', 'list', 'nasdaq']:
            tracker.list_nasdaq_examples()
            return
    else:
        company_input = input("\nEnter company name or ticker symbol (or 'list' for NASDAQ examples): ").strip()
        
        if company_input.lower() in ['list', 'nasdaq', '--list', '--nasdaq']:
            tracker.list_nasdaq_examples()
            company_input = input("\nEnter ticker symbol: ").strip()
    
    if not company_input:
        print("No company name provided. Exiting.")
        return
    
    # Try to use as ticker first
    tracker.ticker = company_input.upper()
    
    # Fetch company information
    info = tracker.get_company_info()
    
    if info is None:
        print("\nUnable to fetch company information. Please verify the ticker symbol.")
        return
    
    # Fetch historical data
    hist = tracker.get_historical_data(period="max")
    
    # Ask if user wants to save data
    save_option = input("\nWould you like to save the historical data to CSV? (y/n): ").strip().lower()
    if save_option == 'y':
        tracker.save_to_csv()
    
    print("\n" + "="*80)
    print("Analysis Complete!")
    print("="*80)


if __name__ == "__main__":
    main()