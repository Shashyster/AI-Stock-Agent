#!/usr/bin/env python3
"""
Stock Information Web Application
ChatGPT-like interface for stock information
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import urllib3
import re
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

class TechnicalAnalysis:
    """Technical analysis indicators"""
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return None
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
    
    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow:
            return None
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return {
            'macd': float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None,
            'signal': float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else None,
            'histogram': float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else None
        }
    
    @staticmethod
    def calculate_moving_averages(prices):
        """Calculate various moving averages"""
        if len(prices) < 200:
            return {}
        return {
            'sma_20': float(prices.rolling(window=20).mean().iloc[-1]) if len(prices) >= 20 else None,
            'sma_50': float(prices.rolling(window=50).mean().iloc[-1]) if len(prices) >= 50 else None,
            'sma_200': float(prices.rolling(window=200).mean().iloc[-1]) if len(prices) >= 200 else None,
            'ema_12': float(prices.ewm(span=12, adjust=False).mean().iloc[-1]) if len(prices) >= 12 else None,
            'ema_26': float(prices.ewm(span=26, adjust=False).mean().iloc[-1]) if len(prices) >= 26 else None,
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return None
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        current_price = float(prices.iloc[-1])
        upper = float(upper_band.iloc[-1])
        lower = float(lower_band.iloc[-1])
        middle = float(sma.iloc[-1])
        
        # Calculate %B (position within bands)
        if upper != lower:
            percent_b = ((current_price - lower) / (upper - lower)) * 100
        else:
            percent_b = 50.0
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'percent_b': percent_b,
            'bandwidth': ((upper - lower) / middle * 100) if middle > 0 else None
        }
    
    @staticmethod
    def calculate_stochastic(high, low, close, period=14):
        """Calculate Stochastic Oscillator"""
        if len(close) < period:
            return None
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=3).mean()
        return {
            'k': float(k_percent.iloc[-1]) if not pd.isna(k_percent.iloc[-1]) else None,
            'd': float(d_percent.iloc[-1]) if not pd.isna(d_percent.iloc[-1]) else None
        }
    
    @staticmethod
    def calculate_atr(high, low, close, period=14):
        """Calculate Average True Range"""
        if len(close) < period + 1:
            return None
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else None
    
    @staticmethod
    def calculate_obv(close, volume):
        """Calculate On-Balance Volume"""
        if len(close) < 2:
            return None
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return float(obv.iloc[-1]) if not pd.isna(obv.iloc[-1]) else None
    
    @staticmethod
    def calculate_momentum(prices, period=10):
        """Calculate Momentum"""
        if len(prices) < period + 1:
            return None
        momentum = prices.diff(period)
        return float(momentum.iloc[-1]) if not pd.isna(momentum.iloc[-1]) else None


class ValuationModels:
    """Valuation models including DCF and Relative Valuation"""
    
    @staticmethod
    def calculate_dcf(free_cash_flow, growth_rate, terminal_growth_rate, discount_rate, years=5, shares_outstanding=None):
        """
        Calculate DCF (Discounted Cash Flow) valuation
        
        Parameters:
        - free_cash_flow: Current or TTM free cash flow
        - growth_rate: Annual growth rate (as decimal, e.g., 0.10 for 10%)
        - terminal_growth_rate: Long-term growth rate (typically 2-3%)
        - discount_rate: WACC or required rate of return (as decimal)
        - years: Number of years to project
        - shares_outstanding: Number of shares for per-share valuation
        """
        if not isinstance(free_cash_flow, (int, float)) or free_cash_flow <= 0:
            return None
        
        if not isinstance(growth_rate, (int, float)):
            growth_rate = 0.05  # Default 5% growth
        if not isinstance(terminal_growth_rate, (int, float)):
            terminal_growth_rate = 0.025  # Default 2.5% terminal growth
        if not isinstance(discount_rate, (int, float)):
            discount_rate = 0.10  # Default 10% discount rate
        
        # Project future cash flows
        pv_cash_flows = 0
        current_fcf = free_cash_flow
        
        for year in range(1, years + 1):
            current_fcf *= (1 + growth_rate)
            pv = current_fcf / ((1 + discount_rate) ** year)
            pv_cash_flows += pv
        
        # Terminal value (using Gordon Growth Model)
        terminal_fcf = current_fcf * (1 + terminal_growth_rate)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
        pv_terminal = terminal_value / ((1 + discount_rate) ** years)
        
        # Enterprise value
        enterprise_value = pv_cash_flows + pv_terminal
        
        # Equity value (if shares provided)
        if shares_outstanding and shares_outstanding > 0:
            equity_value_per_share = enterprise_value / shares_outstanding
            return {
                'enterprise_value': enterprise_value,
                'equity_value_per_share': equity_value_per_share,
                'pv_cash_flows': pv_cash_flows,
                'pv_terminal': pv_terminal,
                'assumptions': {
                    'growth_rate': growth_rate,
                    'terminal_growth': terminal_growth_rate,
                    'discount_rate': discount_rate,
                    'years': years
                }
            }
        
        return {
            'enterprise_value': enterprise_value,
            'pv_cash_flows': pv_cash_flows,
            'pv_terminal': pv_terminal,
            'assumptions': {
                'growth_rate': growth_rate,
                'terminal_growth': terminal_growth_rate,
                'discount_rate': discount_rate,
                'years': years
            }
        }
    
    @staticmethod
    def calculate_relative_valuation(info, sector_pe=None, industry_pe=None):
        """
        Calculate relative valuation metrics compared to sector/industry
        
        Returns valuation assessment based on P/E, P/B, P/S ratios
        """
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        pb_ratio = info.get('priceToBook', None)
        ps_ratio = info.get('priceToSalesTrailing12Months', None)
        
        relative_assessment = {
            'pe_vs_market': 'N/A',
            'pb_vs_market': 'N/A',
            'ps_vs_market': 'N/A',
            'overall_valuation': 'FAIR',
            'premium_discount': 0
        }
        
        # Market average P/E is typically around 20-25
        market_pe = 22.5
        if isinstance(pe_ratio, (int, float)) and pe_ratio > 0:
            pe_ratio_vs_market = (pe_ratio / market_pe) * 100
            relative_assessment['pe_vs_market'] = f"{pe_ratio_vs_market:.1f}% of market average"
            relative_assessment['premium_discount'] += (pe_ratio_vs_market - 100) / 3
        
        # Market average P/B is typically around 3-4
        market_pb = 3.5
        if isinstance(pb_ratio, (int, float)) and pb_ratio > 0:
            pb_ratio_vs_market = (pb_ratio / market_pb) * 100
            relative_assessment['pb_vs_market'] = f"{pb_ratio_vs_market:.1f}% of market average"
            relative_assessment['premium_discount'] += (pb_ratio_vs_market - 100) / 3
        
        # Market average P/S is typically around 2-3
        market_ps = 2.5
        if isinstance(ps_ratio, (int, float)) and ps_ratio > 0:
            ps_ratio_vs_market = (ps_ratio / market_ps) * 100
            relative_assessment['ps_vs_market'] = f"{ps_ratio_vs_market:.1f}% of market average"
            relative_assessment['premium_discount'] += (ps_ratio_vs_market - 100) / 3
        
        # Determine overall valuation
        avg_premium = relative_assessment['premium_discount']
        if avg_premium > 20:
            relative_assessment['overall_valuation'] = 'EXPENSIVE'
        elif avg_premium > 10:
            relative_assessment['overall_valuation'] = 'SLIGHTLY EXPENSIVE'
        elif avg_premium > -10:
            relative_assessment['overall_valuation'] = 'FAIR'
        elif avg_premium > -20:
            relative_assessment['overall_valuation'] = 'SLIGHTLY CHEAP'
        else:
            relative_assessment['overall_valuation'] = 'CHEAP'
        
        return relative_assessment


class MacroEconomicAnalysis:
    """Macroeconomic trend and economic pressure analysis"""
    
    @staticmethod
    def analyze_macro_environment(ticker_obj, sector, industry):
        """
        Analyze macroeconomic factors affecting the stock
        Uses available market data and sector information
        """
        macro_analysis = {
            'sector_outlook': 'NEUTRAL',
            'economic_pressures': [],
            'market_conditions': 'NEUTRAL',
            'interest_rate_sensitivity': 'MEDIUM',
            'inflation_impact': 'MEDIUM',
            'recession_resilience': 'MEDIUM'
        }
        
        # Sector-based analysis
        sector_lower = sector.lower() if sector else ''
        industry_lower = industry.lower() if industry else ''
        
        # Technology sector
        if 'technology' in sector_lower or 'software' in industry_lower or 'semiconductor' in industry_lower:
            macro_analysis['sector_outlook'] = 'POSITIVE'
            macro_analysis['economic_pressures'].append('Technology sector benefits from digital transformation trends')
            macro_analysis['interest_rate_sensitivity'] = 'HIGH'
            macro_analysis['recession_resilience'] = 'LOW-MEDIUM'
        
        # Financial sector
        elif 'financial' in sector_lower or 'bank' in industry_lower:
            macro_analysis['sector_outlook'] = 'NEUTRAL'
            macro_analysis['interest_rate_sensitivity'] = 'VERY HIGH'
            macro_analysis['economic_pressures'].append('Financial sector highly sensitive to interest rate changes')
            macro_analysis['recession_resilience'] = 'LOW'
        
        # Consumer discretionary
        elif 'consumer' in sector_lower and 'discretionary' in sector_lower:
            macro_analysis['sector_outlook'] = 'CAUTIOUS'
            macro_analysis['economic_pressures'].append('Consumer discretionary sensitive to economic cycles')
            macro_analysis['recession_resilience'] = 'LOW'
            macro_analysis['inflation_impact'] = 'HIGH'
        
        # Consumer staples
        elif 'consumer' in sector_lower and 'staples' in sector_lower:
            macro_analysis['sector_outlook'] = 'STABLE'
            macro_analysis['recession_resilience'] = 'HIGH'
            macro_analysis['economic_pressures'].append('Consumer staples provide defensive characteristics')
            macro_analysis['inflation_impact'] = 'MEDIUM'
        
        # Healthcare
        elif 'healthcare' in sector_lower or 'health' in sector_lower:
            macro_analysis['sector_outlook'] = 'POSITIVE'
            macro_analysis['recession_resilience'] = 'HIGH'
            macro_analysis['economic_pressures'].append('Healthcare sector shows defensive characteristics')
            macro_analysis['inflation_impact'] = 'LOW-MEDIUM'
        
        # Energy
        elif 'energy' in sector_lower or 'oil' in industry_lower:
            macro_analysis['sector_outlook'] = 'VOLATILE'
            macro_analysis['economic_pressures'].append('Energy sector subject to commodity price volatility')
            macro_analysis['recession_resilience'] = 'MEDIUM'
            macro_analysis['inflation_impact'] = 'HIGH'
        
        # Utilities
        elif 'utilities' in sector_lower:
            macro_analysis['sector_outlook'] = 'STABLE'
            macro_analysis['recession_resilience'] = 'HIGH'
            macro_analysis['interest_rate_sensitivity'] = 'HIGH'
            macro_analysis['economic_pressures'].append('Utilities provide stable dividends but sensitive to rates')
        
        # Real Estate
        elif 'real estate' in sector_lower or 'reit' in industry_lower:
            macro_analysis['sector_outlook'] = 'CAUTIOUS'
            macro_analysis['interest_rate_sensitivity'] = 'VERY HIGH'
            macro_analysis['recession_resilience'] = 'LOW-MEDIUM'
            macro_analysis['economic_pressures'].append('Real estate highly sensitive to interest rates and economic cycles')
        
        # General market conditions (using beta as proxy)
        try:
            info = ticker_obj.info if hasattr(ticker_obj, 'info') else {}
            beta = info.get('beta', 1.0)
            if isinstance(beta, (int, float)):
                if beta > 1.3:
                    macro_analysis['market_conditions'] = 'HIGH VOLATILITY'
                    macro_analysis['economic_pressures'].append('High beta indicates high market sensitivity')
                elif beta < 0.7:
                    macro_analysis['market_conditions'] = 'LOW VOLATILITY'
                    macro_analysis['economic_pressures'].append('Low beta indicates defensive characteristics')
        except:
            pass
        
        return macro_analysis


class SocialSentimentAnalysis:
    """Social media and market sentiment analysis"""
    
    @staticmethod
    def analyze_sentiment(ticker, info, hist_data):
        """
        Analyze market sentiment based on available data
        Uses volume, price action, and analyst sentiment as proxies
        """
        sentiment = {
            'overall_sentiment': 'NEUTRAL',
            'retail_interest': 'MEDIUM',
            'institutional_interest': 'MEDIUM',
            'analyst_sentiment': 'NEUTRAL',
            'momentum_sentiment': 'NEUTRAL',
            'indicators': []
        }
        
        # Volume analysis (proxy for interest)
        avg_volume = info.get('averageVolume', 0)
        current_volume = info.get('volume', 0)
        
        if isinstance(avg_volume, (int, float)) and isinstance(current_volume, (int, float)) and avg_volume > 0:
            volume_ratio = current_volume / avg_volume
            if volume_ratio > 1.5:
                sentiment['retail_interest'] = 'HIGH'
                sentiment['indicators'].append('High trading volume suggests strong market interest')
            elif volume_ratio < 0.7:
                sentiment['retail_interest'] = 'LOW'
                sentiment['indicators'].append('Low trading volume suggests weak interest')
        
        # Analyst recommendations
        recommendation = info.get('recommendationKey', '').upper() if info.get('recommendationKey') else ''
        if recommendation in ['STRONG_BUY', 'BUY']:
            sentiment['analyst_sentiment'] = 'BULLISH'
            sentiment['indicators'].append('Analyst recommendations are bullish')
        elif recommendation in ['STRONG_SELL', 'SELL']:
            sentiment['analyst_sentiment'] = 'BEARISH'
            sentiment['indicators'].append('Analyst recommendations are bearish')
        
        # Price momentum (recent performance)
        if hist_data is not None and len(hist_data) >= 20:
            recent_return = ((hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[-20]) / hist_data['Close'].iloc[-20]) * 100
            if recent_return > 10:
                sentiment['momentum_sentiment'] = 'VERY BULLISH'
                sentiment['indicators'].append('Strong recent price momentum indicates positive sentiment')
            elif recent_return > 5:
                sentiment['momentum_sentiment'] = 'BULLISH'
            elif recent_return < -10:
                sentiment['momentum_sentiment'] = 'VERY BEARISH'
                sentiment['indicators'].append('Weak recent price momentum indicates negative sentiment')
            elif recent_return < -5:
                sentiment['momentum_sentiment'] = 'BEARISH'
        
        # Institutional ownership
        inst_ownership = info.get('heldPercentInstitutions', None)
        if isinstance(inst_ownership, (int, float)):
            if inst_ownership > 70:
                sentiment['institutional_interest'] = 'HIGH'
                sentiment['indicators'].append('High institutional ownership indicates professional confidence')
            elif inst_ownership < 30:
                sentiment['institutional_interest'] = 'LOW'
                sentiment['indicators'].append('Low institutional ownership may indicate lack of professional interest')
        
        # Overall sentiment calculation
        sentiment_score = 0
        if sentiment['analyst_sentiment'] == 'BULLISH':
            sentiment_score += 30
        elif sentiment['analyst_sentiment'] == 'BEARISH':
            sentiment_score -= 30
        
        if sentiment['momentum_sentiment'] in ['VERY BULLISH', 'BULLISH']:
            sentiment_score += 25
        elif sentiment['momentum_sentiment'] in ['VERY BEARISH', 'BEARISH']:
            sentiment_score -= 25
        
        if sentiment['retail_interest'] == 'HIGH':
            sentiment_score += 20
        elif sentiment['retail_interest'] == 'LOW':
            sentiment_score -= 20
        
        if sentiment['institutional_interest'] == 'HIGH':
            sentiment_score += 25
        elif sentiment['institutional_interest'] == 'LOW':
            sentiment_score -= 15
        
        if sentiment_score > 40:
            sentiment['overall_sentiment'] = 'BULLISH'
        elif sentiment_score > 15:
            sentiment['overall_sentiment'] = 'SLIGHTLY BULLISH'
        elif sentiment_score < -40:
            sentiment['overall_sentiment'] = 'BEARISH'
        elif sentiment_score < -15:
            sentiment['overall_sentiment'] = 'SLIGHTLY BEARISH'
        
        return sentiment


class StockInfoAPI:
    """API class to fetch stock information"""
    
    @staticmethod
    def format_large_number(num):
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
    
    @staticmethod
    def format_percentage(num):
        """Format percentage values"""
        if not isinstance(num, (int, float)):
            return str(num)
        return f"{num*100:.2f}%"
    
    @staticmethod
    def format_date(timestamp):
        """Format Unix timestamp to readable date"""
        if not isinstance(timestamp, (int, float)):
            return str(timestamp)
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        except:
            return str(timestamp)
    
    @staticmethod
    def generate_ai_analysis(stock_data, hist_data, info, ticker_obj=None):
        """Generate comprehensive AI-powered analysis with DCF, relative valuation, macro analysis, sentiment, and detailed reasoning"""
        analysis = {
            'overallRating': 'NEUTRAL',
            'investmentRecommendation': 'HOLD',
            'longTermOutlook': 'MODERATE',
            'riskLevel': 'MEDIUM',
            'confidence': 0,
            'scores': {},
            'technicalSignals': [],
            'fundamentalSignals': [],
            'riskFactors': [],
            'opportunities': [],
            'summary': '',
            'priceTarget': None,
            'timeHorizon': '12-24 months',
            'dcfValuation': {},
            'relativeValuation': {},
            'macroAnalysis': {},
            'sentimentAnalysis': {},
            'detailedReasoning': {
                'executiveSummary': '',
                'technicalAnalysis': {},
                'fundamentalAnalysis': {},
                'valuationAnalysis': {},
                'macroEconomicFactors': {},
                'sentimentFactors': {},
                'riskAssessment': {},
                'investmentThesis': '',
                'conclusion': ''
            }
        }
        
        try:
            scores = {'technical': 0, 'fundamental': 0, 'momentum': 0, 'value': 0, 'growth': 0}
            signals = []
            risks = []
            opportunities = []
            
            current_price = stock_data.get('currentPrice', 0)
            if isinstance(current_price, str) or current_price == 'N/A':
                current_price = 0
            
            # TECHNICAL ANALYSIS SCORING
            tech_score = 0
            tech_max = 0
            
            # RSI Analysis
            rsi = stock_data.get('rsi', 'N/A')
            if isinstance(rsi, (int, float)):
                tech_max += 20
                if 30 <= rsi <= 70:
                    tech_score += 15
                    signals.append("RSI indicates neutral momentum (neither overbought nor oversold)")
                elif rsi < 30:
                    tech_score += 20
                    signals.append("RSI shows oversold conditions - potential buying opportunity")
                    opportunities.append("Oversold RSI suggests potential rebound")
                elif rsi > 70:
                    tech_score += 5
                    signals.append("RSI indicates overbought conditions - caution advised")
                    risks.append("High RSI suggests potential pullback")
            
            # Moving Average Analysis
            price_vs_sma200 = stock_data.get('priceVsSMA200', None)
            price_vs_sma50 = stock_data.get('priceVsSMA50', None)
            price_vs_sma20 = stock_data.get('priceVsSMA20', None)
            
            tech_max += 25
            if price_vs_sma200 and isinstance(price_vs_sma200, (int, float)):
                if price_vs_sma200 > 0:
                    tech_score += 10
                    signals.append("Price above 200-day SMA - long-term uptrend confirmed")
                else:
                    tech_score += 2
                    signals.append("Price below 200-day SMA - long-term downtrend")
                    risks.append("Trading below 200-day moving average indicates weak long-term trend")
            
            if price_vs_sma50 and isinstance(price_vs_sma50, (int, float)):
                if price_vs_sma50 > 0:
                    tech_score += 8
                    signals.append("Price above 50-day SMA - medium-term bullish")
                else:
                    tech_score += 3
                    signals.append("Price below 50-day SMA - medium-term bearish")
            
            if price_vs_sma20 and isinstance(price_vs_sma20, (int, float)):
                if price_vs_sma20 > 0:
                    tech_score += 7
                    signals.append("Price above 20-day SMA - short-term positive momentum")
                else:
                    tech_score += 3
            
            # MACD Analysis
            macd = stock_data.get('macd', 'N/A')
            macd_signal = stock_data.get('macdSignal', 'N/A')
            macd_hist = stock_data.get('macdHistogram', 'N/A')
            
            tech_max += 15
            if isinstance(macd, (int, float)) and isinstance(macd_signal, (int, float)):
                if macd > macd_signal:
                    tech_score += 10
                    signals.append("MACD above signal line - bullish momentum")
                else:
                    tech_score += 3
                    signals.append("MACD below signal line - bearish momentum")
                    risks.append("MACD bearish crossover indicates weakening momentum")
            
            if isinstance(macd_hist, (int, float)):
                if macd_hist > 0:
                    tech_score += 5
                else:
                    tech_score += 1
            
            # Bollinger Bands Analysis
            bb_percent = stock_data.get('bbPercentB', None)
            tech_max += 10
            if isinstance(bb_percent, (int, float)):
                if 20 <= bb_percent <= 80:
                    tech_score += 10
                    signals.append("Price within normal Bollinger Band range")
                elif bb_percent < 20:
                    tech_score += 8
                    signals.append("Price near lower Bollinger Band - potential support")
                    opportunities.append("Near lower Bollinger Band suggests potential bounce")
                elif bb_percent > 80:
                    tech_score += 5
                    signals.append("Price near upper Bollinger Band - potential resistance")
                    risks.append("Near upper Bollinger Band suggests potential pullback")
            
            # Stochastic Analysis
            stoch_k = stock_data.get('stochK', 'N/A')
            stoch_d = stock_data.get('stochD', 'N/A')
            tech_max += 10
            if isinstance(stoch_k, (int, float)) and isinstance(stoch_d, (int, float)):
                if stoch_k > stoch_d and stoch_k < 80:
                    tech_score += 8
                    signals.append("Stochastic shows bullish momentum")
                elif stoch_k < stoch_d and stoch_k > 20:
                    tech_score += 3
                    signals.append("Stochastic shows bearish momentum")
                elif stoch_k < 20:
                    tech_score += 7
                    opportunities.append("Oversold stochastic suggests potential reversal")
            
            # Volume Analysis
            volume_ratio = stock_data.get('volumeRatio', None)
            tech_max += 10
            if isinstance(volume_ratio, (int, float)):
                if volume_ratio > 120:
                    tech_score += 8
                    signals.append("Above-average volume indicates strong interest")
                elif volume_ratio < 80:
                    tech_score += 3
                    signals.append("Below-average volume suggests weak conviction")
            
            # Momentum Analysis
            momentum = stock_data.get('momentum', 'N/A')
            tech_max += 10
            if isinstance(momentum, (int, float)):
                if momentum > 0:
                    tech_score += 8
                    signals.append("Positive momentum detected")
                else:
                    tech_score += 2
                    signals.append("Negative momentum - price declining")
                    risks.append("Negative momentum indicates downward price pressure")
            
            scores['technical'] = (tech_score / tech_max * 100) if tech_max > 0 else 50
            
            # FUNDAMENTAL ANALYSIS SCORING
            fund_score = 0
            fund_max = 0
            
            # Valuation Metrics
            pe_ratio = info.get('trailingPE', None)
            forward_pe = info.get('forwardPE', None)
            peg_ratio = info.get('pegRatio', None)
            price_to_book = info.get('priceToBook', None)
            
            fund_max += 20
            if isinstance(pe_ratio, (int, float)) and pe_ratio > 0:
                if 10 <= pe_ratio <= 25:
                    fund_score += 15
                    signals.append("P/E ratio in reasonable range")
                elif pe_ratio < 10:
                    fund_score += 18
                    signals.append("Low P/E ratio suggests undervaluation")
                    opportunities.append("Attractive P/E ratio indicates potential value")
                elif pe_ratio > 30:
                    fund_score += 5
                    signals.append("High P/E ratio suggests overvaluation")
                    risks.append("Elevated P/E ratio indicates expensive valuation")
            
            if isinstance(peg_ratio, (int, float)) and peg_ratio > 0:
                fund_max += 15
                if peg_ratio < 1:
                    fund_score += 15
                    signals.append("PEG ratio below 1 - good growth at reasonable price")
                    opportunities.append("Low PEG ratio suggests growth potential")
                elif 1 <= peg_ratio <= 2:
                    fund_score += 10
                    signals.append("PEG ratio in acceptable range")
                else:
                    fund_score += 3
                    risks.append("High PEG ratio suggests overvaluation relative to growth")
            
            # Financial Health
            profit_margin = info.get('profitMargins', None)
            roe = info.get('returnOnEquity', None)
            roa = info.get('returnOnAssets', None)
            debt_to_equity = info.get('debtToEquity', None)
            current_ratio = info.get('currentRatio', None)
            
            fund_max += 20
            if isinstance(profit_margin, (int, float)):
                if profit_margin > 0.15:
                    fund_score += 8
                    signals.append("Strong profit margins indicate efficient operations")
                elif profit_margin > 0:
                    fund_score += 5
                else:
                    fund_score += 1
                    risks.append("Negative profit margins indicate financial distress")
            
            if isinstance(roe, (int, float)):
                if roe > 0.15:
                    fund_score += 6
                    signals.append("High return on equity shows efficient capital use")
                elif roe > 0:
                    fund_score += 3
                else:
                    fund_score += 1
                    risks.append("Negative ROE indicates poor capital efficiency")
            
            if isinstance(debt_to_equity, (int, float)):
                fund_max += 10
                if debt_to_equity < 1:
                    fund_score += 10
                    signals.append("Low debt-to-equity ratio indicates financial stability")
                elif debt_to_equity < 2:
                    fund_score += 7
                else:
                    fund_score += 3
                    risks.append("High debt-to-equity ratio increases financial risk")
            
            if isinstance(current_ratio, (int, float)):
                fund_max += 10
                if 1.5 <= current_ratio <= 3:
                    fund_score += 10
                    signals.append("Healthy current ratio indicates good liquidity")
                elif current_ratio < 1:
                    fund_score += 2
                    risks.append("Current ratio below 1 suggests liquidity concerns")
            
            # Growth Metrics
            revenue_growth = info.get('revenueGrowth', None)
            earnings_growth = info.get('earningsQuarterlyGrowth', None)
            
            fund_max += 15
            if isinstance(revenue_growth, (int, float)):
                if revenue_growth > 0.10:
                    fund_score += 8
                    signals.append("Strong revenue growth indicates expanding business")
                    opportunities.append("High revenue growth suggests market expansion")
                elif revenue_growth > 0:
                    fund_score += 5
                else:
                    fund_score += 1
                    risks.append("Declining revenue indicates business contraction")
            
            if isinstance(earnings_growth, (int, float)):
                if earnings_growth > 0.15:
                    fund_score += 7
                    signals.append("Strong earnings growth shows profitability improvement")
                    opportunities.append("High earnings growth indicates improving fundamentals")
                elif earnings_growth > 0:
                    fund_score += 4
                else:
                    fund_score += 1
                    risks.append("Negative earnings growth indicates declining profitability")
            
            # Market Position
            market_cap = info.get('marketCap', None)
            beta = info.get('beta', None)
            
            fund_max += 10
            if isinstance(market_cap, (int, float)) and market_cap > 10_000_000_000:
                fund_score += 5
                signals.append("Large market cap indicates established company")
            
            if isinstance(beta, (int, float)):
                if 0.8 <= beta <= 1.2:
                    fund_score += 5
                    signals.append("Beta near 1 - market-aligned volatility")
                elif beta > 1.5:
                    fund_score += 2
                    risks.append("High beta indicates high volatility and market sensitivity")
            
            scores['fundamental'] = (fund_score / fund_max * 100) if fund_max > 0 else 50
            
            # MOMENTUM SCORING
            momentum_score = 0
            momentum_max = 0
            
            one_year_return = stock_data.get('oneYearReturn', 'N/A')
            five_year_return = stock_data.get('fiveYearReturn', 'N/A')
            
            momentum_max += 30
            if isinstance(one_year_return, str) and '%' in one_year_return:
                try:
                    ret_val = float(one_year_return.replace('%', ''))
                    if ret_val > 20:
                        momentum_score += 20
                        signals.append("Strong 1-year return indicates positive momentum")
                    elif ret_val > 0:
                        momentum_score += 12
                    else:
                        momentum_score += 3
                        risks.append("Negative 1-year return indicates poor recent performance")
                except:
                    pass
            
            momentum_max += 20
            if isinstance(five_year_return, str) and '%' in five_year_return:
                try:
                    ret_val = float(five_year_return.replace('%', ''))
                    if ret_val > 50:
                        momentum_score += 20
                        signals.append("Excellent 5-year return shows long-term growth")
                        opportunities.append("Strong 5-year track record indicates quality investment")
                    elif ret_val > 20:
                        momentum_score += 15
                    elif ret_val > 0:
                        momentum_score += 8
                    else:
                        momentum_score += 2
                        risks.append("Negative 5-year return indicates long-term underperformance")
                except:
                    pass
            
            scores['momentum'] = (momentum_score / momentum_max * 100) if momentum_max > 0 else 50
            
            # VALUE SCORING
            value_score = 0
            value_max = 0
            
            if isinstance(pe_ratio, (int, float)) and pe_ratio > 0:
                value_max += 25
                if pe_ratio < 15:
                    value_score += 25
                elif pe_ratio < 20:
                    value_score += 18
                elif pe_ratio < 25:
                    value_score += 12
                else:
                    value_score += 5
            
            if isinstance(price_to_book, (int, float)) and price_to_book > 0:
                value_max += 25
                if price_to_book < 1:
                    value_score += 25
                    opportunities.append("Price below book value suggests deep value")
                elif price_to_book < 2:
                    value_score += 18
                elif price_to_book < 3:
                    value_score += 12
                else:
                    value_score += 5
            
            if isinstance(peg_ratio, (int, float)) and peg_ratio > 0:
                value_max += 25
                if peg_ratio < 0.8:
                    value_score += 25
                elif peg_ratio < 1.2:
                    value_score += 18
                else:
                    value_score += 8
            
            # Compare to analyst target
            target_mean = info.get('targetMeanPrice', None)
            if isinstance(target_mean, (int, float)) and current_price > 0:
                value_max += 25
                upside = ((target_mean - current_price) / current_price) * 100
                if upside > 20:
                    value_score += 25
                    opportunities.append(f"Analyst target suggests {upside:.1f}% upside potential")
                elif upside > 10:
                    value_score += 18
                elif upside > 0:
                    value_score += 12
                else:
                    value_score += 5
            
            scores['value'] = (value_score / value_max * 100) if value_max > 0 else 50
            
            # GROWTH SCORING
            growth_score = 0
            growth_max = 0
            
            if isinstance(revenue_growth, (int, float)):
                growth_max += 30
                if revenue_growth > 0.20:
                    growth_score += 30
                elif revenue_growth > 0.10:
                    growth_score += 20
                elif revenue_growth > 0:
                    growth_score += 12
                else:
                    growth_score += 3
            
            if isinstance(earnings_growth, (int, float)):
                growth_max += 30
                if earnings_growth > 0.25:
                    growth_score += 30
                elif earnings_growth > 0.15:
                    growth_score += 20
                elif earnings_growth > 0:
                    growth_score += 12
                else:
                    growth_score += 3
            
            if isinstance(peg_ratio, (int, float)) and peg_ratio > 0:
                growth_max += 20
                if peg_ratio < 1:
                    growth_score += 20
                elif peg_ratio < 1.5:
                    growth_score += 15
                else:
                    growth_score += 5
            
            # Forward P/E vs Trailing P/E
            if isinstance(forward_pe, (int, float)) and isinstance(pe_ratio, (int, float)) and forward_pe > 0 and pe_ratio > 0:
                growth_max += 20
                if forward_pe < pe_ratio:
                    growth_score += 20
                    signals.append("Forward P/E lower than trailing - earnings expected to grow")
                else:
                    growth_score += 8
            
            scores['growth'] = (growth_score / growth_max * 100) if growth_max > 0 else 50
            
            # DCF VALUATION ANALYSIS
            free_cash_flow = info.get('freeCashflow', None)
            shares_outstanding = info.get('sharesOutstanding', None)
            revenue_growth_val = info.get('revenueGrowth', 0.05) if isinstance(info.get('revenueGrowth'), (int, float)) else 0.05
            earnings_growth_val = info.get('earningsQuarterlyGrowth', 0.05) if isinstance(info.get('earningsQuarterlyGrowth'), (int, float)) else 0.05
            
            # Estimate discount rate (WACC proxy) - typically 8-12% for most companies
            beta_val = info.get('beta', 1.0) if isinstance(info.get('beta'), (int, float)) else 1.0
            discount_rate = 0.03 + (beta_val * 0.07)  # Risk-free rate + beta * market risk premium
            
            # Use average of revenue and earnings growth, capped at reasonable levels
            growth_rate = min(max((revenue_growth_val + earnings_growth_val) / 2, 0.02), 0.15)
            
            dcf_result = None
            if isinstance(free_cash_flow, (int, float)) and free_cash_flow > 0:
                dcf_result = ValuationModels.calculate_dcf(
                    free_cash_flow=free_cash_flow,
                    growth_rate=growth_rate,
                    terminal_growth_rate=0.025,  # 2.5% terminal growth
                    discount_rate=discount_rate,
                    years=5,
                    shares_outstanding=shares_outstanding if isinstance(shares_outstanding, (int, float)) else None
                )
            
            if dcf_result and dcf_result.get('equity_value_per_share'):
                dcf_price = dcf_result['equity_value_per_share']
                analysis['dcfValuation'] = {
                    'intrinsicValue': round(dcf_price, 2),
                    'currentPrice': current_price,
                    'upsideDownside': round(((dcf_price - current_price) / current_price * 100), 2) if current_price > 0 else 0,
                    'assumptions': dcf_result.get('assumptions', {})
                }
                if current_price > 0:
                    if dcf_price > current_price * 1.15:
                        value_score += 15
                        opportunities.append(f"DCF model suggests {((dcf_price - current_price) / current_price * 100):.1f}% upside potential")
                    elif dcf_price < current_price * 0.85:
                        value_score -= 10
                        risks.append(f"DCF model suggests {((dcf_price - current_price) / current_price * 100):.1f}% downside risk")
            else:
                analysis['dcfValuation'] = {'status': 'Insufficient data for DCF calculation'}
            
            # RELATIVE VALUATION ANALYSIS
            relative_val = ValuationModels.calculate_relative_valuation(info)
            analysis['relativeValuation'] = relative_val
            if relative_val['overall_valuation'] == 'CHEAP':
                value_score += 10
                opportunities.append("Relative valuation suggests stock is trading at a discount to market")
            elif relative_val['overall_valuation'] == 'EXPENSIVE':
                value_score -= 10
                risks.append("Relative valuation suggests stock is trading at a premium to market")
            
            # MACROECONOMIC ANALYSIS
            sector = stock_data.get('sector', '')
            industry = stock_data.get('industry', '')
            macro_analysis = MacroEconomicAnalysis.analyze_macro_environment(ticker_obj, sector, industry) if ticker_obj else {}
            analysis['macroAnalysis'] = macro_analysis
            
            # Adjust scores based on macro factors
            if macro_analysis.get('sector_outlook') == 'POSITIVE':
                fund_score += 5
                opportunities.append(f"{sector} sector shows positive outlook")
            elif macro_analysis.get('sector_outlook') in ['CAUTIOUS', 'VOLATILE']:
                fund_score -= 5
                risks.append(f"{sector} sector faces headwinds")
            
            if macro_analysis.get('recession_resilience') == 'HIGH':
                fund_score += 3
                opportunities.append("Company shows defensive characteristics in economic downturns")
            elif macro_analysis.get('recession_resilience') == 'LOW':
                fund_score -= 3
                risks.append("Company is vulnerable to economic downturns")
            
            # SENTIMENT ANALYSIS
            sentiment = SocialSentimentAnalysis.analyze_sentiment(
                stock_data.get('symbol', ''),
                info,
                hist_data
            )
            analysis['sentimentAnalysis'] = sentiment
            
            # Adjust scores based on sentiment
            if sentiment['overall_sentiment'] == 'BULLISH':
                momentum_score += 10
                opportunities.append("Market sentiment is bullish")
            elif sentiment['overall_sentiment'] == 'BEARISH':
                momentum_score -= 10
                risks.append("Market sentiment is bearish")
            
            # Recalculate scores after adjustments
            scores['value'] = max(0, min(100, (value_score / value_max * 100) if value_max > 0 else 50))
            scores['fundamental'] = max(0, min(100, (fund_score / fund_max * 100) if fund_max > 0 else 50))
            scores['momentum'] = max(0, min(100, (momentum_score / momentum_max * 100) if momentum_max > 0 else 50))
            
            # OVERALL SCORING
            weights = {'technical': 0.20, 'fundamental': 0.25, 'momentum': 0.15, 'value': 0.20, 'growth': 0.10, 'macro': 0.05, 'sentiment': 0.05}
            overall_score = sum(scores[key] * weights.get(key, 0) for key in scores if key in weights)
            
            analysis['confidence'] = round(overall_score, 1)
            analysis['scores'] = {k: round(v, 1) for k, v in scores.items()}
            analysis['technicalSignals'] = signals[:10]  # Top 10 signals
            analysis['fundamentalSignals'] = [s for s in signals if any(x in s.lower() for x in ['p/e', 'roe', 'debt', 'margin', 'revenue', 'earnings'])]
            analysis['riskFactors'] = list(set(risks))[:8]  # Top 8 risks
            analysis['opportunities'] = list(set(opportunities))[:8]  # Top 8 opportunities
            
            # DETERMINE RATING AND RECOMMENDATION
            if overall_score >= 75:
                analysis['overallRating'] = 'STRONG BUY'
                analysis['investmentRecommendation'] = 'BUY'
                analysis['longTermOutlook'] = 'VERY POSITIVE'
                analysis['riskLevel'] = 'LOW-MEDIUM'
            elif overall_score >= 65:
                analysis['overallRating'] = 'BUY'
                analysis['investmentRecommendation'] = 'BUY'
                analysis['longTermOutlook'] = 'POSITIVE'
                analysis['riskLevel'] = 'MEDIUM'
            elif overall_score >= 55:
                analysis['overallRating'] = 'HOLD'
                analysis['investmentRecommendation'] = 'HOLD'
                analysis['longTermOutlook'] = 'NEUTRAL'
                analysis['riskLevel'] = 'MEDIUM'
            elif overall_score >= 45:
                analysis['overallRating'] = 'WEAK HOLD'
                analysis['investmentRecommendation'] = 'HOLD'
                analysis['longTermOutlook'] = 'CAUTIOUS'
                analysis['riskLevel'] = 'MEDIUM-HIGH'
            else:
                analysis['overallRating'] = 'SELL'
                analysis['investmentRecommendation'] = 'SELL'
                analysis['longTermOutlook'] = 'NEGATIVE'
                analysis['riskLevel'] = 'HIGH'
            
            # Calculate Price Target
            if isinstance(target_mean, (int, float)) and target_mean > 0:
                analysis['priceTarget'] = round(target_mean, 2)
            elif current_price > 0:
                # Estimate based on average of technical and fundamental factors
                if overall_score >= 65:
                    analysis['priceTarget'] = round(current_price * 1.15, 2)
                elif overall_score >= 55:
                    analysis['priceTarget'] = round(current_price * 1.05, 2)
                elif overall_score >= 45:
                    analysis['priceTarget'] = round(current_price * 0.95, 2)
                else:
                    analysis['priceTarget'] = round(current_price * 0.85, 2)
            
            # Generate Summary
            company_name = stock_data.get('companyName', stock_data.get('symbol', 'This stock'))
            summary_parts = [
                f"{company_name} ({stock_data.get('symbol', 'N/A')}) shows an overall investment score of {overall_score:.1f}/100. "
            ]
            
            if overall_score >= 65:
                summary_parts.append("The analysis indicates a STRONG BUY or BUY recommendation. ")
                summary_parts.append("Technical indicators are favorable, fundamentals appear solid, and the stock shows positive momentum. ")
                if opportunities:
                    summary_parts.append(f"Key opportunities include: {', '.join(opportunities[:2])}. ")
            elif overall_score >= 45:
                summary_parts.append("The analysis suggests a HOLD position. ")
                summary_parts.append("While some positive factors exist, there are also concerns that warrant caution. ")
                if risks:
                    summary_parts.append(f"Main risks include: {', '.join(risks[:2])}. ")
            else:
                summary_parts.append("The analysis indicates a SELL or WEAK HOLD recommendation. ")
                summary_parts.append("Multiple risk factors and weak fundamentals suggest caution. ")
                if risks:
                    summary_parts.append(f"Critical concerns: {', '.join(risks[:2])}. ")
            
            summary_parts.append(f"Technical score: {scores['technical']:.1f}/100, Fundamental score: {scores['fundamental']:.1f}/100. ")
            summary_parts.append(f"For long-term investors, this represents a {analysis['longTermOutlook']} opportunity with {analysis['riskLevel']} risk.")
            
            analysis['summary'] = ''.join(summary_parts)
            
            # ========== COMPREHENSIVE "WHY" SECTION ==========
            company_name = stock_data.get('companyName', stock_data.get('symbol', 'This stock'))
            symbol = stock_data.get('symbol', 'N/A')
            
            # EXECUTIVE SUMMARY
            analysis['detailedReasoning']['executiveSummary'] = (
                f"After comprehensive analysis of {company_name} ({symbol}), our AI-powered evaluation system "
                f"has assigned an overall investment score of {overall_score:.1f}/100, resulting in a "
                f"{analysis['overallRating']} recommendation. This assessment integrates technical analysis, "
                f"fundamental metrics, valuation models (DCF and relative), macroeconomic trends, market sentiment, "
                f"and risk factors. The analysis indicates a {analysis['longTermOutlook']} long-term outlook with "
                f"{analysis['riskLevel']} risk levels."
            )
            
            # TECHNICAL ANALYSIS DETAILS
            tech_details = []
            if isinstance(rsi, (int, float)):
                if rsi < 30:
                    tech_details.append(f"RSI of {rsi:.1f} indicates oversold conditions, suggesting potential buying opportunity as the stock may be undervalued short-term.")
                elif rsi > 70:
                    tech_details.append(f"RSI of {rsi:.1f} indicates overbought conditions, suggesting the stock may be due for a pullback.")
                else:
                    tech_details.append(f"RSI of {rsi:.1f} is in neutral territory, indicating balanced momentum.")
            
            if price_vs_sma200 and isinstance(price_vs_sma200, (int, float)):
                if price_vs_sma200 > 0:
                    tech_details.append(f"Price is {price_vs_sma200:.1f}% above the 200-day moving average, confirming a long-term uptrend.")
                else:
                    tech_details.append(f"Price is {abs(price_vs_sma200):.1f}% below the 200-day moving average, indicating a long-term downtrend.")
            
            if isinstance(macd, (int, float)) and isinstance(macd_signal, (int, float)):
                if macd > macd_signal:
                    tech_details.append(f"MACD ({macd:.4f}) is above signal line ({macd_signal:.4f}), indicating bullish momentum.")
                else:
                    tech_details.append(f"MACD ({macd:.4f}) is below signal line ({macd_signal:.4f}), indicating bearish momentum.")
            
            analysis['detailedReasoning']['technicalAnalysis'] = {
                'score': round(scores['technical'], 1),
                'keyIndicators': tech_details,
                'trend': 'BULLISH' if scores['technical'] > 60 else 'BEARISH' if scores['technical'] < 40 else 'NEUTRAL',
                'summary': f"Technical analysis yields a score of {scores['technical']:.1f}/100. " + ' '.join(tech_details[:3])
            }
            
            # FUNDAMENTAL ANALYSIS DETAILS
            fund_details = []
            if isinstance(pe_ratio, (int, float)) and pe_ratio > 0:
                if pe_ratio < 15:
                    fund_details.append(f"P/E ratio of {pe_ratio:.1f} is attractive, suggesting the stock may be undervalued relative to earnings.")
                elif pe_ratio > 30:
                    fund_details.append(f"P/E ratio of {pe_ratio:.1f} is elevated, suggesting the stock may be overvalued and pricing in high growth expectations.")
                else:
                    fund_details.append(f"P/E ratio of {pe_ratio:.1f} is in a reasonable range.")
            
            if isinstance(profit_margin, (int, float)):
                if profit_margin > 0.15:
                    fund_details.append(f"Profit margin of {profit_margin*100:.1f}% is strong, indicating efficient operations and pricing power.")
                elif profit_margin < 0:
                    fund_details.append(f"Negative profit margin of {profit_margin*100:.1f}% indicates the company is losing money, a significant concern.")
            
            if isinstance(roe, (int, float)):
                if roe > 0.15:
                    fund_details.append(f"Return on Equity of {roe*100:.1f}% is excellent, showing efficient use of shareholder capital.")
                elif roe < 0:
                    fund_details.append(f"Negative ROE of {roe*100:.1f}% indicates poor capital efficiency.")
            
            if isinstance(revenue_growth, (int, float)):
                if revenue_growth > 0.10:
                    fund_details.append(f"Revenue growth of {revenue_growth*100:.1f}% is strong, indicating expanding business and market share gains.")
                elif revenue_growth < 0:
                    fund_details.append(f"Declining revenue of {abs(revenue_growth*100):.1f}% indicates business contraction and competitive challenges.")
            
            analysis['detailedReasoning']['fundamentalAnalysis'] = {
                'score': round(scores['fundamental'], 1),
                'keyMetrics': fund_details,
                'financialHealth': 'STRONG' if scores['fundamental'] > 65 else 'WEAK' if scores['fundamental'] < 45 else 'MODERATE',
                'summary': f"Fundamental analysis yields a score of {scores['fundamental']:.1f}/100. " + ' '.join(fund_details[:3])
            }
            
            # VALUATION ANALYSIS DETAILS
            val_details = []
            if dcf_result and dcf_result.get('equity_value_per_share'):
                dcf_price = dcf_result['equity_value_per_share']
                upside = ((dcf_price - current_price) / current_price * 100) if current_price > 0 else 0
                val_details.append(
                    f"DCF (Discounted Cash Flow) model calculates an intrinsic value of ${dcf_price:.2f} per share, "
                    f"compared to current price of ${current_price:.2f}. This suggests {'{:.1f}% upside potential'.format(upside) if upside > 0 else '{:.1f}% downside risk'.format(abs(upside))}. "
                    f"Assumptions: {dcf_result['assumptions'].get('growth_rate', 0)*100:.1f}% growth rate, "
                    f"{dcf_result['assumptions'].get('discount_rate', 0)*100:.1f}% discount rate, "
                    f"{dcf_result['assumptions'].get('terminal_growth', 0)*100:.1f}% terminal growth."
                )
            
            if relative_val.get('overall_valuation'):
                val_details.append(
                    f"Relative valuation analysis indicates the stock is {relative_val['overall_valuation']} compared to market averages. "
                    f"P/E ratio is {relative_val.get('pe_vs_market', 'N/A')} of market average, "
                    f"P/B ratio is {relative_val.get('pb_vs_market', 'N/A')} of market average, "
                    f"and P/S ratio is {relative_val.get('ps_vs_market', 'N/A')} of market average."
                )
            
            analysis['detailedReasoning']['valuationAnalysis'] = {
                'dcfValue': dcf_result.get('equity_value_per_share') if dcf_result else None,
                'relativeValuation': relative_val.get('overall_valuation', 'N/A'),
                'valueScore': round(scores['value'], 1),
                'details': val_details,
                'summary': ' '.join(val_details) if val_details else 'Valuation analysis suggests fair value relative to fundamentals.'
            }
            
            # MACROECONOMIC FACTORS
            macro_details = []
            if macro_analysis.get('sector_outlook'):
                macro_details.append(f"Sector Outlook: {macro_analysis['sector_outlook']}. {sector} sector analysis indicates this outlook based on industry trends and economic cycles.")
            
            if macro_analysis.get('economic_pressures'):
                macro_details.append(f"Economic Pressures: {'; '.join(macro_analysis['economic_pressures'][:3])}")
            
            if macro_analysis.get('interest_rate_sensitivity'):
                macro_details.append(f"Interest Rate Sensitivity: {macro_analysis['interest_rate_sensitivity']}. This stock is {'highly' if 'HIGH' in macro_analysis['interest_rate_sensitivity'] else 'moderately' if 'MEDIUM' in macro_analysis['interest_rate_sensitivity'] else 'minimally'} sensitive to interest rate changes.")
            
            if macro_analysis.get('recession_resilience'):
                macro_details.append(f"Recession Resilience: {macro_analysis['recession_resilience']}. This indicates how well the company may perform during economic downturns.")
            
            analysis['detailedReasoning']['macroEconomicFactors'] = {
                'sectorOutlook': macro_analysis.get('sector_outlook', 'N/A'),
                'economicPressures': macro_analysis.get('economic_pressures', []),
                'interestRateSensitivity': macro_analysis.get('interest_rate_sensitivity', 'N/A'),
                'recessionResilience': macro_analysis.get('recession_resilience', 'N/A'),
                'summary': ' '.join(macro_details) if macro_details else 'Macroeconomic factors are neutral for this investment.'
            }
            
            # SENTIMENT FACTORS
            sent_details = []
            if sentiment.get('overall_sentiment'):
                sent_details.append(f"Overall Market Sentiment: {sentiment['overall_sentiment']}. This reflects the collective market psychology and investor confidence.")
            
            if sentiment.get('analyst_sentiment'):
                sent_details.append(f"Analyst Sentiment: {sentiment['analyst_sentiment']}. Professional analysts' recommendations indicate this sentiment.")
            
            if sentiment.get('momentum_sentiment'):
                sent_details.append(f"Price Momentum Sentiment: {sentiment['momentum_sentiment']}. Recent price action suggests this momentum trend.")
            
            if sentiment.get('retail_interest'):
                sent_details.append(f"Retail Interest: {sentiment['retail_interest']}. Trading volume patterns indicate this level of retail investor participation.")
            
            if sentiment.get('institutional_interest'):
                sent_details.append(f"Institutional Interest: {sentiment['institutional_interest']}. Institutional ownership levels suggest this level of professional investor confidence.")
            
            analysis['detailedReasoning']['sentimentFactors'] = {
                'overallSentiment': sentiment.get('overall_sentiment', 'N/A'),
                'analystSentiment': sentiment.get('analyst_sentiment', 'N/A'),
                'momentumSentiment': sentiment.get('momentum_sentiment', 'N/A'),
                'indicators': sentiment.get('indicators', []),
                'summary': ' '.join(sent_details) if sent_details else 'Market sentiment is neutral.'
            }
            
            # RISK ASSESSMENT
            risk_details = []
            risk_score = 0
            if len(risks) > 5:
                risk_score += 20
                risk_details.append("Multiple significant risk factors identified, indicating elevated investment risk.")
            elif len(risks) > 3:
                risk_score += 10
                risk_details.append("Several risk factors present that warrant careful consideration.")
            
            if scores['fundamental'] < 40:
                risk_score += 15
                risk_details.append("Weak fundamental score suggests underlying business challenges.")
            
            if scores['technical'] < 40:
                risk_score += 10
                risk_details.append("Weak technical indicators suggest negative price momentum.")
            
            if macro_analysis.get('recession_resilience') == 'LOW':
                risk_score += 10
                risk_details.append("Low recession resilience increases vulnerability to economic downturns.")
            
            if isinstance(beta_val, (int, float)) and beta_val > 1.5:
                risk_score += 10
                risk_details.append(f"High beta ({beta_val:.2f}) indicates high volatility and market sensitivity.")
            
            analysis['detailedReasoning']['riskAssessment'] = {
                'riskLevel': analysis['riskLevel'],
                'riskScore': min(100, risk_score),
                'keyRisks': risks[:10],
                'riskFactors': risk_details,
                'summary': f"Risk assessment indicates {analysis['riskLevel']} risk level. " + ' '.join(risk_details[:2]) + (' ' + '; '.join(risks[:3]) if risks else '')
            }
            
            # INVESTMENT THESIS
            thesis_parts = []
            if overall_score >= 65:
                thesis_parts.append(f"{company_name} presents a compelling investment opportunity based on strong fundamentals, favorable technical indicators, and attractive valuation. ")
                thesis_parts.append(f"The company demonstrates solid financial health with a fundamental score of {scores['fundamental']:.1f}/100. ")
                if scores['technical'] > 60:
                    thesis_parts.append(f"Technical analysis supports a bullish outlook with a score of {scores['technical']:.1f}/100. ")
                if scores['value'] > 60:
                    thesis_parts.append(f"Valuation metrics suggest the stock is attractively priced with a value score of {scores['value']:.1f}/100. ")
                if sentiment.get('overall_sentiment') == 'BULLISH':
                    thesis_parts.append("Market sentiment is positive, supporting the investment case. ")
            elif overall_score >= 45:
                thesis_parts.append(f"{company_name} presents a mixed investment profile with both positive and negative factors. ")
                thesis_parts.append(f"While fundamentals score {scores['fundamental']:.1f}/100, there are concerns that limit upside potential. ")
                thesis_parts.append("Investors should carefully weigh the opportunities against the risks before making a decision. ")
            else:
                thesis_parts.append(f"{company_name} faces significant challenges that limit its investment appeal. ")
                thesis_parts.append(f"With a fundamental score of {scores['fundamental']:.1f}/100 and technical score of {scores['technical']:.1f}/100, the stock shows weakness. ")
                thesis_parts.append("Multiple risk factors and weak fundamentals suggest caution is warranted. ")
            
            if opportunities:
                thesis_parts.append(f"Key opportunities include: {', '.join(opportunities[:3])}. ")
            
            analysis['detailedReasoning']['investmentThesis'] = ''.join(thesis_parts)
            
            # CONCLUSION
            conclusion_parts = [
                f"In conclusion, after comprehensive analysis incorporating technical indicators, fundamental metrics, "
                f"DCF and relative valuation models, macroeconomic trends, market sentiment, and risk factors, "
                f"{company_name} ({symbol}) receives an overall investment score of {overall_score:.1f}/100, "
                f"resulting in a {analysis['overallRating']} recommendation. "
            ]
            
            conclusion_parts.append(
                f"The analysis indicates: Technical Analysis: {scores['technical']:.1f}/100, "
                f"Fundamental Analysis: {scores['fundamental']:.1f}/100, "
                f"Momentum: {scores['momentum']:.1f}/100, "
                f"Value: {scores['value']:.1f}/100, "
                f"Growth: {scores['growth']:.1f}/100. "
            )
            
            if analysis.get('priceTarget'):
                conclusion_parts.append(
                    f"Based on our analysis, we establish a price target of ${analysis['priceTarget']:.2f}, "
                    f"representing {((analysis['priceTarget'] - current_price) / current_price * 100):.1f}% "
                    f"{'upside' if analysis['priceTarget'] > current_price else 'downside'} from the current price of ${current_price:.2f}. "
                )
            
            conclusion_parts.append(
                f"For investors with a {analysis['timeHorizon']} time horizon, this represents a "
                f"{analysis['longTermOutlook']} opportunity with {analysis['riskLevel']} risk. "
            )
            
            conclusion_parts.append(
                f"Investors should monitor key factors including: {', '.join([r.split(':')[0] if ':' in r else r[:50] for r in risks[:3]]) if risks else 'general market conditions'}, "
                f"and consider the opportunities: {', '.join([o.split(':')[0] if ':' in o else o[:50] for o in opportunities[:2]]) if opportunities else 'market recovery'}."
            )
            
            analysis['detailedReasoning']['conclusion'] = ''.join(conclusion_parts)
            
        except Exception as e:
            analysis['summary'] = f"Analysis generated with some limitations. Error: {str(e)}"
            analysis['confidence'] = 50
            analysis['detailedReasoning']['executiveSummary'] = f"Analysis encountered limitations: {str(e)}"
        
        return analysis
    
    @staticmethod
    def get_stock_info(ticker):
        """Fetch comprehensive stock information"""
        try:
            ticker_obj = yf.Ticker(ticker.upper())
            
            # Test connectivity
            try:
                test_data = ticker_obj.history(period="1d")
                if test_data.empty:
                    return {"error": f"No data found for ticker '{ticker}'. It may be invalid or delisted."}
            except Exception as e:
                return {"error": f"Connection failed: {str(e)}"}
            
            # Get company info
            try:
                info = ticker_obj.info
            except Exception as e:
                # Try to get basic data from history
                hist = ticker_obj.history(period="5d")
                if not hist.empty:
                    latest = hist.iloc[-1]
                    info = {
                        'symbol': ticker.upper(),
                        'longName': ticker.upper(),
                        'regularMarketPrice': float(latest['Close']),
                        'previousClose': float(hist.iloc[-2]['Close']) if len(hist) > 1 else float(latest['Close']),
                    }
                else:
                    return {"error": f"Unable to fetch data for ticker '{ticker}'"}
            
            if not info or len(info) == 0:
                return {"error": f"No data returned for ticker '{ticker}'"}
            
            # Get historical data from start (max period)
            hist_max = ticker_obj.history(period="max")
            hist_1y = ticker_obj.history(period="1y")
            hist_5y = ticker_obj.history(period="5y")
            
            # Calculate yearly performance
            yearly_performance = []
            if not hist_max.empty:
                hist_copy = hist_max.copy()
                hist_copy['Year'] = hist_copy.index.year
                yearly_data = hist_copy.groupby('Year').agg({
                    'Open': 'first',
                    'Close': 'last',
                    'High': 'max',
                    'Low': 'min',
                    'Volume': 'sum'
                })
                yearly_data['Return %'] = ((yearly_data['Close'] - yearly_data['Open']) / yearly_data['Open'] * 100)
                
                for year, row in yearly_data.iterrows():
                    yearly_performance.append({
                        'year': int(year),
                        'open': float(row['Open']),
                        'close': float(row['Close']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'volume': float(row['Volume']),
                        'return': float(row['Return %'])
                    })
            
            # Format the response
            formatted_info = {
                "symbol": info.get('symbol', ticker.upper()),
                "companyName": info.get('longName', 'N/A'),
                "shortName": info.get('shortName', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "country": info.get('country', 'N/A'),
                "city": info.get('city', 'N/A'),
                "state": info.get('state', 'N/A'),
                "zip": info.get('zip', 'N/A'),
                "phone": info.get('phone', 'N/A'),
                "website": info.get('website', 'N/A'),
                "fullTimeEmployees": info.get('fullTimeEmployees', 'N/A'),
                "description": info.get('longBusinessSummary', 'N/A'),
                "exchange": info.get('exchange', 'N/A'),
                "currency": info.get('currency', 'N/A'),
                
                # Market Data
                "currentPrice": info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
                "previousClose": info.get('previousClose', 'N/A'),
                "open": info.get('open', 'N/A'),
                "dayLow": info.get('dayLow', 'N/A'),
                "dayHigh": info.get('dayHigh', 'N/A'),
                "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow', 'N/A'),
                "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh', 'N/A'),
                "volume": info.get('volume', 'N/A'),
                "averageVolume": info.get('averageVolume', 'N/A'),
                
                # Valuation
                "marketCap": StockInfoAPI.format_large_number(info.get('marketCap', 'N/A')),
                "enterpriseValue": StockInfoAPI.format_large_number(info.get('enterpriseValue', 'N/A')),
                "trailingPE": info.get('trailingPE', 'N/A'),
                "forwardPE": info.get('forwardPE', 'N/A'),
                "pegRatio": info.get('pegRatio', 'N/A'),
                "priceToBook": info.get('priceToBook', 'N/A'),
                "priceToSales": info.get('priceToSalesTrailing12Months', 'N/A'),
                
                # Financial Performance
                "revenue": StockInfoAPI.format_large_number(info.get('totalRevenue', 'N/A')),
                "revenuePerShare": info.get('revenuePerShare', 'N/A'),
                "profitMargin": StockInfoAPI.format_percentage(info.get('profitMargins', 'N/A')),
                "operatingMargin": StockInfoAPI.format_percentage(info.get('operatingMargins', 'N/A')),
                "returnOnAssets": StockInfoAPI.format_percentage(info.get('returnOnAssets', 'N/A')),
                "returnOnEquity": StockInfoAPI.format_percentage(info.get('returnOnEquity', 'N/A')),
                "eps": info.get('trailingEps', 'N/A'),
                "earningsGrowth": StockInfoAPI.format_percentage(info.get('earningsQuarterlyGrowth', 'N/A')),
                "revenueGrowth": StockInfoAPI.format_percentage(info.get('revenueGrowth', 'N/A')),
                
                # Dividends
                "dividendRate": info.get('dividendRate', 'N/A'),
                "dividendYield": StockInfoAPI.format_percentage(info.get('dividendYield', 'N/A')),
                "payoutRatio": StockInfoAPI.format_percentage(info.get('payoutRatio', 'N/A')),
                "exDividendDate": StockInfoAPI.format_date(info.get('exDividendDate', 'N/A')),
                
                # Analyst Recommendations
                "recommendation": info.get('recommendationKey', 'N/A'),
                "targetMeanPrice": info.get('targetMeanPrice', 'N/A'),
                "targetHighPrice": info.get('targetHighPrice', 'N/A'),
                "targetLowPrice": info.get('targetLowPrice', 'N/A'),
                "numberOfAnalystOpinions": info.get('numberOfAnalystOpinions', 'N/A'),
                
                # Additional Financial Metrics
                "totalCash": StockInfoAPI.format_large_number(info.get('totalCash', 'N/A')),
                "totalCashPerShare": info.get('totalCashPerShare', 'N/A'),
                "totalDebt": StockInfoAPI.format_large_number(info.get('totalDebt', 'N/A')),
                "totalDebtPerShare": info.get('totalDebtPerShare', 'N/A'),
                "debtToEquity": info.get('debtToEquity', 'N/A'),
                "currentRatio": info.get('currentRatio', 'N/A'),
                "quickRatio": info.get('quickRatio', 'N/A'),
                "bookValue": info.get('bookValue', 'N/A'),
                "enterpriseToRevenue": info.get('enterpriseToRevenue', 'N/A'),
                "enterpriseToEbitda": info.get('enterpriseToEbitda', 'N/A'),
                "ebitda": StockInfoAPI.format_large_number(info.get('ebitda', 'N/A')),
                "grossMargins": StockInfoAPI.format_percentage(info.get('grossMargins', 'N/A')),
                "freeCashflow": StockInfoAPI.format_large_number(info.get('freeCashflow', 'N/A')),
                "operatingCashflow": StockInfoAPI.format_large_number(info.get('operatingCashflow', 'N/A')),
                "earningsGrowth": StockInfoAPI.format_percentage(info.get('earningsGrowth', 'N/A')),
                "earningsQuarterlyGrowth": StockInfoAPI.format_percentage(info.get('earningsQuarterlyGrowth', 'N/A')),
                "revenuePerShare": info.get('revenuePerShare', 'N/A'),
                "quarterlyRevenueGrowth": StockInfoAPI.format_percentage(info.get('quarterlyRevenueGrowth', 'N/A')),
                
                # Stock Statistics
                "beta": info.get('beta', 'N/A'),
                "52WeekChange": StockInfoAPI.format_percentage(info.get('52WeekChange', 'N/A')),
                "sharesOutstanding": StockInfoAPI.format_large_number(info.get('sharesOutstanding', 'N/A')),
                "floatShares": StockInfoAPI.format_large_number(info.get('floatShares', 'N/A')),
                "sharesShort": StockInfoAPI.format_large_number(info.get('sharesShort', 'N/A')),
                "sharesShortPriorMonth": StockInfoAPI.format_large_number(info.get('sharesShortPriorMonth', 'N/A')),
                "shortRatio": info.get('shortRatio', 'N/A'),
                "shortPercentOfFloat": StockInfoAPI.format_percentage(info.get('shortPercentOfFloat', 'N/A')),
                "heldPercentInsiders": StockInfoAPI.format_percentage(info.get('heldPercentInsiders', 'N/A')),
                "heldPercentInstitutions": StockInfoAPI.format_percentage(info.get('heldPercentInstitutions', 'N/A')),
                
                # Company Officers
                "companyOfficers": info.get('companyOfficers', [])[:10] if info.get('companyOfficers') else [],
                
                # Historical data from start
                "hasHistoricalData": not hist_max.empty,
                "historicalDataPoints": len(hist_max) if not hist_max.empty else 0,
                "dataStartDate": str(hist_max.index[0].date()) if not hist_max.empty else 'N/A',
                "dataEndDate": str(hist_max.index[-1].date()) if not hist_max.empty else 'N/A',
                "totalTradingDays": len(hist_max) if not hist_max.empty else 0,
                "yearlyPerformance": yearly_performance,
            }
            
            # All-time statistics
            if not hist_max.empty:
                formatted_info["allTimeHigh"] = float(hist_max['Close'].max())
                formatted_info["allTimeHighDate"] = str(hist_max['Close'].idxmax().date())
                formatted_info["allTimeLow"] = float(hist_max['Close'].min())
                formatted_info["allTimeLowDate"] = str(hist_max['Close'].idxmin().date())
                formatted_info["allTimeAverage"] = float(hist_max['Close'].mean())
                formatted_info["allTimeMedian"] = float(hist_max['Close'].median())
                formatted_info["allTimeStdDev"] = float(hist_max['Close'].std())
                
                # Calculate total return from start
                start_price = float(hist_max['Close'].iloc[0])
                end_price = float(hist_max['Close'].iloc[-1])
                total_return = ((end_price - start_price) / start_price) * 100
                formatted_info["totalReturnFromStart"] = f"{total_return:.2f}%"
                formatted_info["startPrice"] = start_price
                formatted_info["yearsOfData"] = (hist_max.index[-1] - hist_max.index[0]).days / 365.25
                
                # 1-year statistics
                if not hist_1y.empty:
                    formatted_info["oneYearHigh"] = float(hist_1y['Close'].max())
                    formatted_info["oneYearLow"] = float(hist_1y['Close'].min())
                    formatted_info["oneYearReturn"] = f"{((hist_1y['Close'].iloc[-1] - hist_1y['Close'].iloc[0]) / hist_1y['Close'].iloc[0] * 100):.2f}%"
                
                # 5-year statistics
                if not hist_5y.empty:
                    formatted_info["fiveYearHigh"] = float(hist_5y['Close'].max())
                    formatted_info["fiveYearLow"] = float(hist_5y['Close'].min())
                    formatted_info["fiveYearReturn"] = f"{((hist_5y['Close'].iloc[-1] - hist_5y['Close'].iloc[0]) / hist_5y['Close'].iloc[0] * 100):.2f}%"
            
            # Calculate Technical Indicators
            if not hist_1y.empty and len(hist_1y) >= 200:
                close_prices = hist_1y['Close']
                high_prices = hist_1y['High']
                low_prices = hist_1y['Low']
                volume_data = hist_1y['Volume']
                
                # RSI
                rsi = TechnicalAnalysis.calculate_rsi(close_prices)
                formatted_info["rsi"] = round(rsi, 2) if rsi else 'N/A'
                
                # MACD
                macd = TechnicalAnalysis.calculate_macd(close_prices)
                formatted_info["macd"] = round(macd['macd'], 4) if macd and macd['macd'] else 'N/A'
                formatted_info["macdSignal"] = round(macd['signal'], 4) if macd and macd['signal'] else 'N/A'
                formatted_info["macdHistogram"] = round(macd['histogram'], 4) if macd and macd['histogram'] else 'N/A'
                
                # Moving Averages
                ma = TechnicalAnalysis.calculate_moving_averages(close_prices)
                current_price = float(close_prices.iloc[-1])
                formatted_info["sma20"] = round(ma.get('sma_20', 0), 2) if ma.get('sma_20') else 'N/A'
                formatted_info["sma50"] = round(ma.get('sma_50', 0), 2) if ma.get('sma_50') else 'N/A'
                formatted_info["sma200"] = round(ma.get('sma_200', 0), 2) if ma.get('sma_200') else 'N/A'
                formatted_info["ema12"] = round(ma.get('ema_12', 0), 2) if ma.get('ema_12') else 'N/A'
                formatted_info["ema26"] = round(ma.get('ema_26', 0), 2) if ma.get('ema_26') else 'N/A'
                
                # Price vs Moving Averages
                if ma.get('sma_20') and current_price:
                    formatted_info["priceVsSMA20"] = round(((current_price - ma['sma_20']) / ma['sma_20'] * 100), 2)
                if ma.get('sma_50') and current_price:
                    formatted_info["priceVsSMA50"] = round(((current_price - ma['sma_50']) / ma['sma_50'] * 100), 2)
                if ma.get('sma_200') and current_price:
                    formatted_info["priceVsSMA200"] = round(((current_price - ma['sma_200']) / ma['sma_200'] * 100), 2)
                
                # Bollinger Bands
                bb = TechnicalAnalysis.calculate_bollinger_bands(close_prices)
                if bb:
                    formatted_info["bbUpper"] = round(bb['upper'], 2)
                    formatted_info["bbMiddle"] = round(bb['middle'], 2)
                    formatted_info["bbLower"] = round(bb['lower'], 2)
                    formatted_info["bbPercentB"] = round(bb['percent_b'], 2)
                    formatted_info["bbWidth"] = round(bb['bandwidth'], 2) if bb['bandwidth'] else 'N/A'
                
                # Stochastic
                stoch = TechnicalAnalysis.calculate_stochastic(high_prices, low_prices, close_prices)
                if stoch:
                    formatted_info["stochK"] = round(stoch['k'], 2) if stoch['k'] else 'N/A'
                    formatted_info["stochD"] = round(stoch['d'], 2) if stoch['d'] else 'N/A'
                
                # ATR
                atr = TechnicalAnalysis.calculate_atr(high_prices, low_prices, close_prices)
                formatted_info["atr"] = round(atr, 2) if atr else 'N/A'
                
                # OBV
                obv = TechnicalAnalysis.calculate_obv(close_prices, volume_data)
                formatted_info["obv"] = StockInfoAPI.format_large_number(obv) if obv else 'N/A'
                
                # Momentum
                momentum = TechnicalAnalysis.calculate_momentum(close_prices)
                formatted_info["momentum"] = round(momentum, 2) if momentum else 'N/A'
                
                # Additional Finviz-style metrics
                # Price change percentages
                if len(hist_1y) >= 5:
                    formatted_info["change5d"] = f"{((close_prices.iloc[-1] - close_prices.iloc[-5]) / close_prices.iloc[-5] * 100):.2f}%" if len(hist_1y) >= 5 else 'N/A'
                if len(hist_1y) >= 20:
                    formatted_info["change20d"] = f"{((close_prices.iloc[-1] - close_prices.iloc[-20]) / close_prices.iloc[-20] * 100):.2f}%" if len(hist_1y) >= 20 else 'N/A'
                if len(hist_1y) >= 60:
                    formatted_info["change60d"] = f"{((close_prices.iloc[-1] - close_prices.iloc[-60]) / close_prices.iloc[-60] * 100):.2f}%" if len(hist_1y) >= 60 else 'N/A'
                
                # Volatility (30-day)
                if len(hist_1y) >= 30:
                    returns_30d = close_prices.pct_change().dropna()
                    volatility_30d = returns_30d.tail(30).std() * np.sqrt(252) * 100  # Annualized
                    formatted_info["volatility30d"] = f"{volatility_30d:.2f}%"
                
                # Volume analysis
                avg_volume_20d = volume_data.tail(20).mean()
                current_volume = volume_data.iloc[-1]
                if avg_volume_20d > 0:
                    volume_ratio = (current_volume / avg_volume_20d) * 100
                    formatted_info["volumeRatio"] = round(volume_ratio, 2)
            
            # AI-Powered Analysis and Predictions
            ticker_obj_for_analysis = yf.Ticker(ticker.upper())
            analysis = StockInfoAPI.generate_ai_analysis(formatted_info, hist_1y if not hist_1y.empty else None, info, ticker_obj_for_analysis)
            formatted_info["aiAnalysis"] = analysis
            
            return formatted_info
            
        except Exception as e:
            return {"error": f"Error fetching stock information: {str(e)}"}


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/stock/<ticker>', methods=['GET'])
def get_stock(ticker):
    """API endpoint to get stock information"""
    result = StockInfoAPI.get_stock_info(ticker)
    return jsonify(result)


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint that processes ticker symbols"""
    data = request.json
    message = data.get('message', '').strip().upper()
    
    # Extract ticker symbol from message (1-5 uppercase letters)
    ticker_match = re.search(r'\b([A-Z]{1,5})\b', message)
    if ticker_match:
        ticker = ticker_match.group(1)
        result = StockInfoAPI.get_stock_info(ticker)
        return jsonify(result)
    else:
        return jsonify({
            "error": "Please provide a valid ticker symbol (e.g., AAPL, MSFT, TSLA)"
        })


if __name__ == '__main__':
    # Use environment variable for port (required by most hosting platforms)
    # Default to 5001 for local development
    port = int(os.environ.get('PORT', 5001))
    # Only enable debug mode in development (not in production)
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
