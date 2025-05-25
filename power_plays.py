"""
Power Plays functionality - Find top stock opportunities in Fortune 500
"""
import yfinance as yf
import pandas as pd
import streamlit as st
from stock_analyzer import StockAnalyzer
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from utils import format_large_number

# Stock indices for analysis
STOCK_INDICES = {
    "Fortune 500": [
        "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", "NVDA", "UNH", "JNJ",
        "JPM", "V", "PG", "MA", "HD", "ABBV", "MRK", "XOM", "BAC", "CVX", 
        "LLY", "PFE", "KO", "PEP", "TMO", "COST", "AVGO", "DIS", "WMT", "CSCO",
        "ABT", "ACN", "MCD", "VZ", "CRM", "NKE", "CMCSA", "ADBE", "ORCL", "DHR",
        "IBM", "PM", "UPS", "AMD", "TXN", "INTC", "QCOM", "COP", "T", "AMGN",
        "USB", "EMR", "WM", "F", "MTD", "ORLY", "PSA", "PCAR", "AJG", "ROP",
        "IDXX", "PSX", "BX", "APH", "DXCM", "MNST", "CTAS", "CHTR", "ALL", "CMG",
        "YUM", "EXC", "AZO", "MRNA", "GIS", "O", "ADSK", "TT", "HSY", "AEP",
        "GM", "HUM", "VLO", "TDG", "GWW", "D", "MSCI", "MSI", "UBER", "DOW",
        "GPN", "SRE", "KMB", "VICI", "PAYX", "ABNB", "AIG", "ECL", "IT", "OXY",
        "A", "PH", "PPG", "CEG", "PCG", "WELL", "NDAQ", "NEM", "CPRT", "ODFL",
        "BIIB", "WDAY", "HES", "ILMN", "CTSH", "RMD", "PNC", "ROST", "MET", "MCHP",
        "IQV", "NUE", "COF", "HLT", "FDX", "STZ", "GEHC", "HCL", "NXPI", "FAST",
        "RCL", "DAL", "HOLX", "KR", "DG", "DHI", "LEN", "WST", "URI", "ULTA",
        "TSCO", "IR", "PODD", "XYL", "JBHT", "TRGP", "FSLR", "EG", "FICO", "DRI",
        "ACGL", "FIS", "INVH", "ED", "MOH", "STE", "ROK", "DLR", "IFF", "TSN",
        "ES", "AXON", "NOC", "TTWO", "GFS", "HIG", "STLD", "RF", "AVB", "BLDR",
        "EQR", "CHD", "MLM", "HPE", "KMI", "CNC", "OKE", "WBD", "SBAC", "PRU",
        "TRV", "WTW", "HBAN", "DVN", "BKR", "ALGN", "CDW", "MAA", "CFG", "EFX",
        "FERG", "ETR", "DOV", "APTV", "MPWR", "PPL", "DFS", "TER", "HWM", "SYY",
        "EIX", "WY", "KDP", "LH", "VMW", "OMC", "COO", "KEYS", "NTRS", "BALL",
        "CTRA", "ANSS", "CMS", "VMC", "EXR", "STT", "EBAY", "DLTR", "CVS", "TAP"
    ],
    "S&P 500": [
        "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "GOOG", "TSLA", "BRK-B", "LLY",
        "AVGO", "UNH", "JPM", "V", "XOM", "JNJ", "PG", "MA", "HD", "MRK", 
        "COST", "ABBV", "CVX", "PEP", "ADBE", "WMT", "CRM", "KO", "BAC", "TMO",
        "MCD", "ACN", "CSCO", "LIN", "AMD", "DIS", "WFC", "ABT", "CMCSA", "NFLX",
        "TXN", "COP", "INTC", "PM", "ORCL", "TMUS", "DHR", "CAT", "NKE", "VZ",
        "SPGI", "MS", "CB", "AMAT", "RTX", "INTU", "GE", "HON", "CL", "BMY",
        "AMGN", "AXP", "LOW", "UPS", "DE", "BKNG", "MDLZ", "SCHW", "ADP", "GILD",
        "SYK", "BLK", "GS", "ISRG", "ELV", "ADI", "REGN", "TJX", "VRTX", "ETN",
        "SBUX", "PLD", "NOW", "ZTS", "AON", "MMC", "LRCX", "CI", "MO", "BSX",
        "CME", "SO", "PANW", "FI", "DUK", "ITW", "UNP", "APD", "EOG", "CSX",
        "AMT", "PGR", "MPC", "MU", "ICE", "KLAC", "HCA", "EQIX", "PYPL", "FCX",
        "SNPS", "CDNS", "PXD", "GD", "CCI", "SLB", "MCK", "TFC", "NSC", "BDX",
        "USB", "EMR", "WM", "F", "MTD", "ORLY", "PSA", "PCAR", "AJG", "ROP",
        "IDXX", "PSX", "BX", "APH", "DXCM", "MNST", "CTAS", "CHTR", "ALL", "CMG",
        "YUM", "EXC", "AZO", "MRNA", "GIS", "O", "ADSK", "TT", "HSY", "AEP",
        "GM", "HUM", "VLO", "TDG", "GWW", "D", "MSCI", "MSI", "UBER", "DOW",
        "GPN", "SRE", "KMB", "VICI", "PAYX", "ABNB", "AIG", "ECL", "IT", "OXY",
        "A", "PH", "PPG", "CEG", "PCG", "WELL", "NDAQ", "NEM", "CPRT", "ODFL",
        "BIIB", "WDAY", "HES", "ILMN", "CTSH", "RMD", "PNC", "ROST", "MET", "MCHP",
        "IQV", "NUE", "COF", "HLT", "FDX", "STZ", "GEHC", "HCL", "NXPI", "FAST",
        "RCL", "DAL", "HOLX", "KR", "DG", "DHI", "LEN", "WST", "URI", "ULTA",
        "TSCO", "IR", "PODD", "XYL", "JBHT", "TRGP", "FSLR", "EG", "FICO", "DRI",
        "ACGL", "FIS", "INVH", "ED", "MOH", "STE", "ROK", "DLR", "IFF", "TSN",
        "ES", "AXON", "NOC", "TTWO", "GFS", "HIG", "STLD", "RF", "AVB", "BLDR",
        "EQR", "CHD", "MLM", "HPE", "KMI", "CNC", "OKE", "WBD", "SBAC", "PRU",
        "TRV", "WTW", "HBAN", "DVN", "BKR", "ALGN", "CDW", "MAA", "CFG", "EFX",
        "FERG", "ETR", "DOV", "APTV", "MPWR", "PPL", "DFS", "TER", "HWM", "SYY",
        "EIX", "WY", "KDP", "LH", "VMW", "OMC", "COO", "KEYS", "NTRS", "BALL",
        "CTRA", "ANSS", "CMS", "VMC", "EXR", "STT", "EBAY", "DLTR", "CVS", "TAP",
        "WAB", "WRB", "AWK", "LW", "PATH", "FE", "AMP", "SMCI", "HAL", "EPAM",
        "STX", "WAT", "TYL", "VTR", "ARE", "KHC", "FITB", "WMB", "NVR", "LPLA",
        "WCN", "ZBH", "PINS", "GL", "LULU", "BRO", "SIVB", "SEE", "MTB", "BAX",
        "ENPH", "PFG", "AKAM", "AVY", "FMC", "DECK", "SWK", "BG", "HBAN", "K",
        "DPZ", "BR", "L", "NTAP", "EL", "VTRS", "LUV", "NDSN", "PEAK", "TDY",
        "CPT", "GRMN", "MAS", "ALB", "JCI", "EXPD", "ABC", "MOS", "FANG", "LHX",
        "NWS", "NWSA", "LYB", "UAL", "SJM", "MKC", "JKHY", "CNP", "GPC", "RL",
        "CTLT", "IPG", "ZBRA", "QRVO", "WDC", "PKG", "IP", "PTC", "ETSY", "BBY",
        "HRL", "RE", "XYL", "EXPE", "PARA", "RJF", "CAH", "CF", "AIZ", "CLX"
    ],
    "Dow Jones": [
        "AAPL", "MSFT", "UNH", "GS", "HD", "MCD", "CAT", "V", "TRV", "JPM",
        "AMGN", "BA", "CRM", "HON", "JNJ", "PG", "AXP", "IBM", "MRK", "WMT",
        "DIS", "MMM", "CVX", "KO", "CSCO", "DOW", "NKE", "INTC", "VZ", "WBA"
    ],
    "NASDAQ-100": [
        "AAPL", "MSFT", "AMZN", "NVDA", "META", "TSLA", "GOOGL", "GOOG", "AVGO", "ADBE",
        "COST", "PEP", "CSCO", "AMD", "CMCSA", "TMUS", "NFLX", "INTC", "TXN", "QCOM", 
        "HON", "INTU", "AMAT", "ISRG", "BKNG", "SBUX", "MDLZ", "AMGN", "ADI", "PYPL",
        "REGN", "VRTX", "PANW", "KLAC", "LRCX", "MRNA", "SNPS", "CDNS", "ADP", "MU",
        "MELI", "ORLY", "MNST", "CRWD", "ASML", "CTAS", "FTNT", "MRVL", "MAR", "ABNB",
        "PCAR", "PAYX", "DXCM", "CPRT", "WDAY", "CTSH", "ODFL", "CHTR", "AEP", "BIIB",
        "KDP", "EXC", "KHC", "ROST", "NXPI", "FAST", "EA", "XEL", "DLTR",
        "IDXX", "GEHC", "BKR", "DASH", "VRSK", "FANG", "ANSS", "CSGP", "CEG", "TEAM",
        "ILMN", "WBD", "ADSK", "ALGN", "ON", "ZS", "ZM", "JD", "LCID", "RIVN",
        "CSX", "STLD", "WBA", "CDW", "ENPH", "DDOG", "TTWO", "EBAY", "SWKS",
        "PDD", "GILD", "MCHP", "CSGP", "DDOG", "TEAM", "VRSK", "GFS", "ROP", 
        "AZN", "PCAR", "VRTX", "DLTR", "NDAQ", "KHC", "EXC", "KDP", "ROST", "FANG", 
        "MRVL", "FTNT", "CTSH", "NXPI", "CHTR", "AEP", "ADSK", "CDNS", "MU", "CTAS", 
        "CRWD", "SNPS", "VRSN", "CPRT", "ODFL", "SIRI", "BKR", "ILMN", "LULU", "DXCM", 
        "MNST", "GEHC", "WDAY", "PAYX", "DASH", "ORLY", "BIIB", "MELI", "CEG",  
        "MTCH", "ANSS", "ALGN", "FAST", "CCEP", "RYAAY", "EA", "XEL", "OKTA", 
        "DOCU", "SWKS", "NTES", "ZS", "IDXX", "ZM", "ON", 
        "ADP", "BMRN", "CSX", "VRSK", "AMAT", "ABNB", "LCID", "DDOG", "MELI", "CTAS"
    ]
}

def analyze_ticker(ticker):
    """
    Analyze a single ticker and return its buy rating and details
    """
    try:
        from utils import safe_float_convert
        
        # Initialize stock analyzer for the ticker
        analyzer = StockAnalyzer(ticker)
        
        # Get basic info
        info = analyzer.get_company_info()
        company_name = info.get('shortName', ticker)
        
        # Get key financial metrics with safe conversion
        market_cap = info.get('marketCap', None)
        pe_ratio = safe_float_convert(info.get('trailingPE', None))
        eps = safe_float_convert(info.get('trailingEps', None))
        revenue = safe_float_convert(info.get('totalRevenue', None))
        dividend_yield = safe_float_convert(info.get('dividendYield', None))
        target_price = safe_float_convert(info.get('targetMeanPrice', None))
        
        # Get current price with error handling
        try:
            current_price = analyzer.get_current_price()
            if current_price is None:
                current_price = 0
        except:
            current_price = 0
            
        # Get price change with error handling
        try:
            price_change = analyzer.get_price_change()
            if price_change is None:
                price_change = (0, 0)
        except:
            price_change = (0, 0)
        
        # Additional data for detailed analysis
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        forward_pe = info.get('forwardPE', None)
        peg_ratio = info.get('pegRatio', None)
        profit_margin = info.get('profitMargins', None)
        
        # Get new metrics for enhanced analysis
        sector_data = analyzer.get_sector_performance()
        dividend_info = analyzer.get_dividend_info()
        earnings_info = analyzer.get_earnings_info()
        
        # Format metrics
        formatted_metrics = {
            'market_cap': format_large_number(market_cap) if market_cap else 'N/A',
            'pe_ratio': f"{pe_ratio:.2f}" if pe_ratio else 'N/A',
            'eps': f"${eps:.2f}" if eps else 'N/A',
            'revenue': format_large_number(revenue) if revenue else 'N/A',
            'dividend_yield': f"{dividend_yield*100:.2f}%" if dividend_yield else 'N/A',
            'target_price': f"${target_price:.2f}" if target_price else 'N/A',
            'current_price': f"${current_price:.2f}" if current_price else 'N/A',
            'sector': sector,
            'industry': industry,
            'forward_pe': f"{forward_pe:.2f}" if forward_pe else 'N/A',
            'peg_ratio': f"{peg_ratio:.2f}" if peg_ratio else 'N/A',
            'profit_margin': f"{profit_margin*100:.2f}%" if profit_margin else 'N/A'
        }
        
        # Add new metrics to the formatted metrics dictionary
        if sector_data:
            formatted_metrics['sector_rank'] = f"{sector_data.get('sector_rank')} of {sector_data.get('total_peers')}" if sector_data.get('sector_rank') and sector_data.get('total_peers') else 'N/A'
            
            # Apply safe float conversion to sector metrics
            sector_perf = safe_float_convert(sector_data.get('sector_performance_1y', 0))
            formatted_metrics['sector_performance_1y'] = f"{sector_perf:.2f}%" if sector_perf is not None else 'N/A'
            
            stock_perf = safe_float_convert(sector_data.get('stock_performance_1y', 0))
            formatted_metrics['stock_performance_1y'] = f"{stock_perf:.2f}%" if stock_perf is not None else 'N/A'
            
            market_outperf = safe_float_convert(sector_data.get('market_outperformance', 0))
            formatted_metrics['market_outperformance'] = f"{market_outperf:.2f}%" if market_outperf is not None else 'N/A'
        
        if dividend_info:
            # Apply safe float conversion to dividend metrics
            dividend_rate = safe_float_convert(dividend_info.get('dividend_rate', 0))
            formatted_metrics['dividend_rate'] = f"${dividend_rate:.2f}" if dividend_rate is not None else 'N/A'
            
            payout_ratio = safe_float_convert(dividend_info.get('payout_ratio', 0))
            formatted_metrics['payout_ratio'] = f"{payout_ratio:.2f}%" if payout_ratio is not None else 'N/A'
            
            dividend_growth = safe_float_convert(dividend_info.get('dividend_growth', 0))
            formatted_metrics['dividend_growth'] = f"{dividend_growth:.2f}%" if dividend_growth is not None else 'N/A'
        
        if earnings_info:
            # Format revenue for earnings info with safe conversion
            total_revenue = safe_float_convert(earnings_info.get('total_revenue'))
            if total_revenue is not None:
                try:
                    if abs(total_revenue) >= 1e9:
                        formatted_metrics['total_revenue'] = f"${total_revenue/1e9:.2f}B"
                    elif abs(total_revenue) >= 1e6:
                        formatted_metrics['total_revenue'] = f"${total_revenue/1e6:.2f}M"
                    else:
                        formatted_metrics['total_revenue'] = f"${total_revenue:.2f}"
                except Exception:
                    formatted_metrics['total_revenue'] = "N/A"
            else:
                formatted_metrics['total_revenue'] = "N/A"
            
            # Format net income for earnings info with safe conversion
            net_income = safe_float_convert(earnings_info.get('net_income'))
            if net_income is not None:
                try:
                    if abs(net_income) >= 1e9:
                        formatted_metrics['net_income'] = f"${net_income/1e9:.2f}B"
                    elif abs(net_income) >= 1e6:
                        formatted_metrics['net_income'] = f"${net_income/1e6:.2f}M"
                    else:
                        formatted_metrics['net_income'] = f"${net_income:.2f}"
                except Exception:
                    formatted_metrics['net_income'] = "N/A"
            else:
                formatted_metrics['net_income'] = "N/A"
            
            net_margin = safe_float_convert(earnings_info.get('net_margin', 0))
            formatted_metrics['net_margin'] = f"{net_margin:.2f}%" if net_margin is not None else 'N/A'
            formatted_metrics['next_earnings_date'] = earnings_info.get('next_earnings_date', 'N/A')
            formatted_metrics['sec_filings_url'] = earnings_info.get('sec_filings_url', 'N/A')
        
        # Calculate buy rating with error handling
        try:
            buy_rating, rating_components = analyzer.calculate_buy_rating()
            
            # Handle None results
            if buy_rating is None:
                buy_rating = 5.0
            if rating_components is None:
                rating_components = {
                    'Technical Analysis': {'score': 5.0, 'reason': 'Data not available'},
                    'Fundamental Analysis': {'score': 5.0, 'reason': 'Data not available'},
                    'Market Sentiment': {'score': 5.0, 'reason': 'Data not available'}
                }
                
            # Get the score breakdown from components
            technical_data = rating_components.get('Technical Analysis', {})
            fundamental_data = rating_components.get('Fundamental Analysis', {})
            sentiment_data = rating_components.get('Market Sentiment', {})
            
            # Extract individual scores
            technical_score = technical_data.get('score', 5.0) if isinstance(technical_data, dict) else 5.0
            fundamental_score = fundamental_data.get('score', 5.0) if isinstance(fundamental_data, dict) else 5.0
            sentiment_score = sentiment_data.get('score', 5.0) if isinstance(sentiment_data, dict) else 5.0
        except Exception as e:
            print(f"Error calculating buy rating for {ticker}: {e}")
            buy_rating = 5.0
            rating_components = {
                'Technical Analysis': {'score': 5.0, 'reason': 'Error in calculation'},
                'Fundamental Analysis': {'score': 5.0, 'reason': 'Error in calculation'},
                'Market Sentiment': {'score': 5.0, 'reason': 'Error in calculation'}
            }
            technical_score = 5.0
            fundamental_score = 5.0
            sentiment_score = 5.0
        
        # Generate analysis
        analysis = generate_analysis(ticker, buy_rating, technical_score, fundamental_score, sentiment_score, formatted_metrics)
        
        return {
            'ticker': ticker,
            'company_name': company_name,
            'buy_rating': buy_rating,
            'rating_components': rating_components,
            'analysis': analysis,
            'metrics': formatted_metrics
        }
    except Exception as e:
        # If there's an error, return None
        print(f"Error analyzing {ticker}: {str(e)}")
        return None

def generate_analysis(ticker, buy_rating, technical_score, fundamental_score, sentiment_score, metrics=None):
    """
    Generate analysis text based on the stock's scores and metrics
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    buy_rating : float
        Overall buy rating (1-10)
    technical_score : float
        Technical analysis score (1-10)
    fundamental_score : float
        Fundamental analysis score (1-10)
    sentiment_score : float
        Market sentiment score (1-10)
    metrics : dict, optional
        Dictionary of financial metrics for the stock
    
    Returns:
    --------
    str
        Detailed analysis text
    """
    # Determine strength and weakness areas
    strengths = []
    weaknesses = []
    
    if technical_score >= 7:
        strengths.append("strong technical indicators (bullish chart patterns, positive momentum)")
    elif technical_score <= 4:
        weaknesses.append("concerning technical signals (bearish patterns, negative momentum)")
        
    if fundamental_score >= 7:
        strengths.append("solid fundamentals (strong earnings growth, healthy balance sheet)")
    elif fundamental_score <= 4:
        weaknesses.append("weak fundamentals (poor financial health, declining margins)")
        
    if sentiment_score >= 7:
        strengths.append("positive market sentiment (analyst upgrades, institutional buying)")
    elif sentiment_score <= 4:
        weaknesses.append("negative market sentiment (analyst downgrades, institutional selling)")
    
    # Create the explanation based on the rating and identified strengths/weaknesses
    if buy_rating >= 7.5:
        strength_text = ", ".join(strengths) if strengths else "multiple positive factors"
        rating_text = f"**Strong Buy ({buy_rating:.1f}/10):** {ticker} presents a compelling investment case based on {strength_text}."
    elif buy_rating >= 6:
        strength_text = ", ".join(strengths) if strengths else "several positive indicators"
        rating_text = f"**Buy ({buy_rating:.1f}/10):** {ticker} shows favorable characteristics including {strength_text}."
    elif buy_rating >= 4:
        if strengths and weaknesses:
            rating_text = f"**Hold ({buy_rating:.1f}/10):** {ticker} shows mixed signals with {', '.join(strengths)} but also {', '.join(weaknesses)}."
        else:
            rating_text = f"**Hold ({buy_rating:.1f}/10):** {ticker} currently presents a balanced risk-reward profile."
    elif buy_rating >= 2.5:
        weakness_text = ", ".join(weaknesses) if weaknesses else "various concerning factors"
        rating_text = f"**Sell ({buy_rating:.1f}/10):** {ticker} faces challenges including {weakness_text}."
    else:
        weakness_text = ", ".join(weaknesses) if weaknesses else "significant negative indicators"
        rating_text = f"**Strong Sell ({buy_rating:.1f}/10):** {ticker} faces major headwinds including {weakness_text}."
    
    # Add detailed metrics if available
    detailed_analysis = ""
    if metrics:
        # Format PE ratio analysis
        pe_text = ""
        if metrics.get('pe_ratio') != 'N/A' and metrics.get('forward_pe') != 'N/A':
            try:
                pe_ratio_str = str(metrics.get('pe_ratio'))
                forward_pe_str = str(metrics.get('forward_pe'))
                
                if 'N/A' not in pe_ratio_str and 'N/A' not in forward_pe_str:
                    pe_ratio = float(pe_ratio_str.replace('%', ''))
                    forward_pe = float(forward_pe_str.replace('%', ''))
                    
                    if pe_ratio > 0 and forward_pe > 0:
                        if forward_pe < pe_ratio:
                            pe_text = f"The forward P/E ({metrics['forward_pe']}) is lower than the trailing P/E ({metrics['pe_ratio']}), potentially indicating projected earnings growth."
                        else:
                            pe_text = f"Current P/E ratio is {metrics['pe_ratio']} with a forward P/E of {metrics['forward_pe']}."
                        pe_text += " "
                else:
                    pe_text = "P/E ratio data available. "
            except Exception as e:
                print(f"Error formatting PE ratios: {e}")
                pe_text = ""
        elif metrics.get('pe_ratio') != 'N/A':
            pe_text = f"Current P/E ratio is {metrics['pe_ratio']}. "
        
        # Format market cap and sector
        cap_sector_text = ""
        if metrics.get('market_cap') != 'N/A':
            cap_sector_text += f"{ticker} has a market capitalization of {metrics['market_cap']}"
            if metrics.get('sector') != 'N/A':
                cap_sector_text += f" in the {metrics['sector']} sector."
            else:
                cap_sector_text += "."
            cap_sector_text += " "
        
        # Format profitability
        profit_text = ""
        if metrics.get('profit_margin') != 'N/A':
            try:
                profit_margin_str = str(metrics.get('profit_margin'))
                if 'N/A' not in profit_margin_str:
                    profit_margin = float(profit_margin_str.replace('%', ''))
                    if profit_margin > 15:
                        profit_text = f"The company shows an impressive profit margin of {metrics['profit_margin']}, indicating strong operational efficiency."
                    elif profit_margin > 0:
                        profit_text = f"With a profit margin of {metrics['profit_margin']}, the company is maintaining positive returns."
                    else:
                        profit_text = f"The company's current profit margin is {metrics['profit_margin']}, indicating profitability challenges."
                    profit_text += " "
            except Exception as e:
                print(f"Error formatting profit margin: {e}")
                pass
        
        # Format valuation
        valuation_text = ""
        if metrics.get('peg_ratio') != 'N/A':
            try:
                peg_ratio_str = str(metrics.get('peg_ratio'))
                if 'N/A' not in peg_ratio_str:
                    peg = float(peg_ratio_str)
                    if 0 < peg < 1:
                        valuation_text = f"With a PEG ratio of {metrics['peg_ratio']}, the stock appears potentially undervalued relative to its growth prospects."
                    elif peg >= 1:
                        valuation_text = f"The PEG ratio of {metrics['peg_ratio']} suggests the stock may be fairly valued to slightly overvalued."
            except Exception as e:
                print(f"Error formatting PEG ratio: {e}")
                pass
        
        # Format price target
        target_text = ""
        if metrics.get('target_price') != 'N/A' and metrics.get('current_price') != 'N/A':
            try:
                target_price_str = str(metrics.get('target_price'))
                current_price_str = str(metrics.get('current_price'))
                
                if 'N/A' not in target_price_str and 'N/A' not in current_price_str:
                    target = float(target_price_str.replace('$', ''))
                    current = float(current_price_str.replace('$', ''))
                    
                    if target > current:
                        upside = ((target / current) - 1) * 100
                        target_text = f"Analysts have a mean price target of {metrics['target_price']}, suggesting a {upside:.1f}% upside potential."
                    else:
                        downside = ((1 - target / current)) * 100
                        target_text = f"The mean analyst price target of {metrics['target_price']} indicates a potential {downside:.1f}% downside from the current price."
                    target_text += " "
            except Exception as e:
                print(f"Error formatting price target: {e}")
                pass
        
        # Format dividend info (enhanced)
        dividend_text = ""
        if metrics.get('dividend_yield') != 'N/A' and metrics.get('dividend_yield') != '0.00%':
            dividend_text = f"The stock offers a dividend yield of {metrics['dividend_yield']}"
            
            # Add dividend growth if available
            if metrics.get('dividend_growth', 'N/A') != 'N/A' and metrics.get('dividend_growth') != '0.00%':
                try:
                    div_growth_str = str(metrics.get('dividend_growth', '0'))
                    if div_growth_str != 'N/A':
                        div_growth = float(div_growth_str.replace('%', ''))
                        if div_growth > 0:
                            dividend_text += f" with a {metrics['dividend_growth']} year-over-year growth"
                except Exception as e:
                    print(f"Error formatting dividend growth: {e}")
                    pass
            
            # Add payout ratio if available
            if metrics.get('payout_ratio', 'N/A') != 'N/A' and metrics.get('payout_ratio') != '0.00%':
                dividend_text += f" and a payout ratio of {metrics['payout_ratio']}"
            
            dividend_text += ". "
        
        # Format sector performance comparison (new)
        sector_text = ""
        if metrics.get('sector_rank', 'N/A') != 'N/A':
            sector_text = f"The stock ranks {metrics['sector_rank']} in its sector. "
        
        if metrics.get('market_outperformance', 'N/A') != 'N/A':
            try:
                outperf_str = str(metrics.get('market_outperformance', '0'))
                if outperf_str != 'N/A' and 'N/A' not in outperf_str:
                    outperf = float(outperf_str.replace('%', ''))
                    if outperf > 10:
                        sector_text += f"It has significantly outperformed the market by {metrics['market_outperformance']}. "
                    elif outperf > 0:
                        sector_text += f"It has outperformed the market by {metrics['market_outperformance']}. "
                    elif outperf > -10:
                        sector_text += f"It has underperformed the market by {abs(outperf):.2f}%. "
                    else:
                        sector_text += f"It has significantly underperformed the market by {abs(outperf):.2f}%. "
            except Exception as e:
                print(f"Error formatting market outperformance: {e}")
                pass
        
        # Format revenue and income (new)
        financial_text = ""
        if metrics.get('total_revenue', 'N/A') != 'N/A' and metrics.get('net_income', 'N/A') != 'N/A':
            financial_text = f"Recent financials show revenue of {metrics['total_revenue']} with net income of {metrics['net_income']}. "
        elif metrics.get('total_revenue', 'N/A') != 'N/A':
            financial_text = f"Recent revenue reported at {metrics['total_revenue']}. "
        
        if metrics.get('net_margin', 'N/A') != 'N/A' and metrics.get('net_margin') != '0.00%':
            try:
                margin_str = str(metrics.get('net_margin', '0'))
                if margin_str != 'N/A' and 'N/A' not in margin_str:
                    margin = float(margin_str.replace('%', ''))
                    if margin > 15:
                        financial_text += f"The company maintains an excellent net margin of {metrics['net_margin']}. "
                    elif margin > 5:
                        financial_text += f"The company shows a solid net margin of {metrics['net_margin']}. "
                    elif margin > 0:
                        financial_text += f"The company has a modest net margin of {metrics['net_margin']}. "
                    else:
                        financial_text += f"The company currently shows a negative net margin of {metrics['net_margin']}. "
            except Exception as e:
                print(f"Error formatting net margin: {e}")
                pass
        
        # Format next earnings date (new)
        earnings_text = ""
        if metrics.get('next_earnings_date', 'N/A') != 'N/A':
            earnings_text = f"Next earnings report expected on {metrics['next_earnings_date']}. "
                
        # Combine all analysis components
        detailed_analysis = f"\n\n{cap_sector_text}{pe_text}{profit_text}{valuation_text}{target_text}{dividend_text}{sector_text}{financial_text}{earnings_text}"
        
    # Combine rating text with detailed analysis
    full_analysis = rating_text + detailed_analysis
    
    return full_analysis

def get_top_stocks(max_stocks=5, max_tickers=500, progress_callback=None, index_name="Fortune 500"):
    """
    Analyze stocks from the selected index and return the top stocks with highest buy ratings
    
    Parameters:
    -----------
    max_stocks : int
        Maximum number of top stocks to return
    max_tickers : int
        Maximum number of tickers to analyze (default is 500 for complete scan)
    progress_callback : function
        Callback function to update progress
    index_name : str
        Name of the stock index to analyze (must be a key in STOCK_INDICES)
    
    Returns:
    --------
    list
        List of top stock dictionaries sorted by buy rating
    """
    st.write(f"Scanning {index_name} companies for investment opportunities...")
    
    # Get tickers for the selected index (fallback to Fortune 500 if the index doesn't exist)
    tickers_to_analyze = STOCK_INDICES.get(index_name, STOCK_INDICES["Fortune 500"])
    
    # Show a progress bar
    progress_container = st.empty()
    progress_bar = progress_container.progress(0)
    
    analyzed_stocks = []
    total_tickers = len(tickers_to_analyze)
    completed = 0
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        future_to_ticker = {executor.submit(analyze_ticker, ticker): ticker for ticker in tickers_to_analyze}
        
        # Process results as they complete
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                result = future.result()
                if result:  # If analysis was successful
                    analyzed_stocks.append(result)
            except Exception as e:
                st.error(f"Error analyzing {ticker}: {str(e)}")
            
            # Update progress
            completed += 1
            progress_percentage = completed / total_tickers
            
            # Update progress bar or use callback
            if progress_callback:
                progress_callback(progress_percentage)
            else:
                progress_bar.progress(progress_percentage)
    
    # Remove the progress bar when done
    progress_container.empty()
    
    # Sort by buy rating
    sorted_stocks = sorted(analyzed_stocks, key=lambda x: x['buy_rating'], reverse=True)
    
    # Get top N unique stocks (prevent duplicates)
    top_stocks = []
    seen_tickers = set()
    
    for stock in sorted_stocks:
        ticker = stock['ticker']
        if ticker not in seen_tickers:
            top_stocks.append(stock)
            seen_tickers.add(ticker)
            
            # Stop when we have enough unique stocks
            if len(top_stocks) >= max_stocks:
                break
    
    return top_stocks

def display_power_plays():
    """
    Display the Power Plays page with top stock picks
    """
    # Header and introduction
    st.title("Power Plays 🚀")
    
    # Initialize session state variables if needed
    if 'power_plays_results' not in st.session_state:
        st.session_state.power_plays_results = None
    
    if 'power_plays_index' not in st.session_state:
        st.session_state.power_plays_index = "Fortune 500"
    
    # Conditional description based on whether we have results
    if st.session_state.power_plays_results is None:
        st.markdown("""
        <div style="background-color: rgba(17, 24, 39, 0.7); padding: 20px; border-radius: 10px; margin-bottom: 30px;">
        <p style="font-size: 18px; line-height: 1.6;">
        Power Plays delivers the five most compelling stock opportunities, ranked by AI-driven buy ratings. 
        Scanning hundreds of companies to find the best investment opportunities right now.
        </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background-color: rgba(17, 24, 39, 0.7); padding: 20px; border-radius: 10px; margin-bottom: 30px;">
        <p style="font-size: 18px; line-height: 1.6;">
        Power Plays delivers the five most compelling stock opportunities, ranked by AI-driven buy ratings.
        These top picks offer a snapshot of where the strongest buying signals are—so you can act fast, with confidence.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Dropdown for selecting stock index
    selected_index = st.selectbox(
        "Select stock index to analyze:", 
        options=list(STOCK_INDICES.keys()),
        index=list(STOCK_INDICES.keys()).index(st.session_state.power_plays_index)
    )
    
    # Update the session state if index changed
    if selected_index != st.session_state.power_plays_index:
        st.session_state.power_plays_index = selected_index
        st.session_state.power_plays_results = None
    
    # Add some space
    st.write("")
    
    # Button for analysis - show Run or Refresh based on state
    if st.session_state.power_plays_results is None:
        # Show Run Analysis button
        if st.button("Run Analysis", key="run_power_plays_button"):
            with st.spinner(f"Analyzing {selected_index} stocks to find the best opportunities..."):
                st.session_state.power_plays_results = get_top_stocks(
                    max_stocks=5, 
                    max_tickers=500,
                    index_name=selected_index
                )
    else:
        # Show Refresh Analysis button
        if st.button("Refresh Analysis", key="refresh_power_plays_button"):
            with st.spinner(f"Refreshing analysis for {selected_index}..."):
                st.session_state.power_plays_results = get_top_stocks(
                    max_stocks=5, 
                    max_tickers=500, 
                    index_name=selected_index
                )
    
    # Display results only if we have them
    top_stocks = st.session_state.power_plays_results
    
    if top_stocks is not None:
        # Display each top stock
        for i, stock in enumerate(top_stocks):
            ticker = stock['ticker']
            company_name = stock['company_name']
            buy_rating = stock['buy_rating']
            analysis = stock['analysis']
            
            # Create rank badge
            rank_badge = f"""
            <div style="display: inline-block; background-color: rgba(59, 130, 246, 0.8); 
                        color: white; border-radius: 50%; width: 30px; height: 30px; 
                        text-align: center; line-height: 30px; font-weight: bold; margin-right: 10px;">
                #{i+1}
            </div>
            """
            
            # Display ticker and company name separately without HTML
            col1, col2 = st.columns([1, 11])
            with col1:
                st.markdown(rank_badge, unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{ticker}**")
                st.markdown(f"### {company_name}")
            
            # Display buy rating
            color = ""
            if buy_rating >= 7:
                color = "green"
                rating_text = "BUY"
            elif buy_rating >= 4:
                color = "orange"
                rating_text = "HOLD"
            else:
                color = "red"
                rating_text = "SELL"
            
            # Rating display
            st.markdown(f"""
            <div style="display: flex; justify-content: center; margin: 20px 0;">
                <div style="display: flex; flex-direction: column; align-items: center; 
                           background-color: rgba(17, 24, 39, 0.7); border-radius: 12px; 
                           padding: 20px 30px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); 
                           border: 3px solid {color}; width: 180px;">
                    <div style="font-size: 42px; font-weight: bold; margin-bottom: 5px; 
                               text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3); color: white;">
                        {buy_rating:.1f}
                    </div>
                    <div style="font-size: 14px; color: #e5e7eb; text-transform: uppercase; 
                               letter-spacing: 1px; margin-bottom: 10px;">
                        BUY RATING
                    </div>
                    <div style="font-size: 22px; font-weight: bold; text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3); 
                               color: {color};">
                        {rating_text}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Split the analysis into rating and detailed analysis
            if "\n\n" in analysis:
                rating_part, detailed_part = analysis.split("\n\n", 1)
                # Display rating part
                st.markdown(rating_part, unsafe_allow_html=True)
                
                # Display detailed analysis
                if detailed_part:
                    st.markdown("### Financial Details")
                    detailed_parts = detailed_part.split(". ")
                    for part in detailed_parts:
                        if part.strip():  # Only add non-empty parts
                            st.markdown(f"• {part.strip()}.")
            else:
                # Fallback if analysis doesn't have the expected format
                st.markdown(analysis, unsafe_allow_html=True)
            
            # Add horizontal separator except for the last item
            if i < len(top_stocks) - 1:
                st.markdown("<hr style='margin-top: 30px; margin-bottom: 30px; border-color: rgba(59, 130, 246, 0.2);'>", unsafe_allow_html=True)
    
    # Add a button to go back to stock search
    st.write("")  # Add some spacing
    if st.button("Back to Stock Search", key="back_to_search_button"):
        # Clear power_plays_results and go back to the stock search page
        st.session_state.power_plays_results = None
        st.session_state.power_plays_view = False
        st.rerun()
    
    # Add vertical buffer at the bottom to push content away from footer
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)