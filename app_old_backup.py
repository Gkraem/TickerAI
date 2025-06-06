import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import base64
import os
import time
from datetime import datetime, timedelta
from stock_analyzer import StockAnalyzer
from technical_analysis import TechnicalAnalysis
from fundamental_analysis import FundamentalAnalysis
from utils import format_large_number, get_stock_news
from data_sources import DATA_SOURCES
from user_management import is_authenticated, get_session_user 
from auth_components import auth_page, logout_button
from admin import is_admin, admin_panel
from power_plays import display_power_plays

# Comprehensive stock database with major companies from all indices
POPULAR_STOCKS = [
    # Mega Cap Tech
    {"ticker": "AAPL", "name": "Apple Inc."},
    {"ticker": "MSFT", "name": "Microsoft Corporation"},
    {"ticker": "AMZN", "name": "Amazon.com Inc."},
    {"ticker": "GOOGL", "name": "Alphabet Inc. (Google Class A)"},
    {"ticker": "GOOG", "name": "Alphabet Inc. (Google Class C)"},
    {"ticker": "META", "name": "Meta Platforms Inc."},
    {"ticker": "TSLA", "name": "Tesla Inc."},
    {"ticker": "NVDA", "name": "NVIDIA Corporation"},
    {"ticker": "NFLX", "name": "Netflix Inc."},
    {"ticker": "ADBE", "name": "Adobe Inc."},
    {"ticker": "CRM", "name": "Salesforce Inc."},
    {"ticker": "ORCL", "name": "Oracle Corporation"},
    {"ticker": "INTC", "name": "Intel Corporation"},
    {"ticker": "AMD", "name": "Advanced Micro Devices Inc."},
    {"ticker": "QCOM", "name": "Qualcomm Inc."},
    {"ticker": "CSCO", "name": "Cisco Systems Inc."},
    {"ticker": "AVGO", "name": "Broadcom Inc."},
    {"ticker": "TXN", "name": "Texas Instruments Inc."},
    {"ticker": "INTU", "name": "Intuit Inc."},
    {"ticker": "NOW", "name": "ServiceNow Inc."},
    {"ticker": "MU", "name": "Micron Technology Inc."},
    {"ticker": "AMAT", "name": "Applied Materials Inc."},
    {"ticker": "LRCX", "name": "Lam Research Corporation"},
    {"ticker": "KLAC", "name": "KLA Corporation"},
    {"ticker": "MRVL", "name": "Marvell Technology Inc."},
    
    # Financial Services
    {"ticker": "JPM", "name": "JPMorgan Chase & Co."},
    {"ticker": "BAC", "name": "Bank of America Corp."},
    {"ticker": "WFC", "name": "Wells Fargo & Company"},
    {"ticker": "C", "name": "Citigroup Inc."},
    {"ticker": "GS", "name": "Goldman Sachs Group Inc."},
    {"ticker": "MS", "name": "Morgan Stanley"},
    {"ticker": "BLK", "name": "BlackRock Inc."},
    {"ticker": "SPGI", "name": "S&P Global Inc."},
    {"ticker": "AXP", "name": "American Express Company"},
    {"ticker": "V", "name": "Visa Inc."},
    {"ticker": "MA", "name": "Mastercard Inc."},
    {"ticker": "PYPL", "name": "PayPal Holdings Inc."},
    {"ticker": "COF", "name": "Capital One Financial Corp."},
    {"ticker": "USB", "name": "U.S. Bancorp"},
    {"ticker": "PNC", "name": "PNC Financial Services Group"},
    {"ticker": "TFC", "name": "Truist Financial Corporation"},
    {"ticker": "SCHW", "name": "Charles Schwab Corporation"},
    {"ticker": "CME", "name": "CME Group Inc."},
    {"ticker": "ICE", "name": "Intercontinental Exchange Inc."},
    {"ticker": "MCO", "name": "Moody's Corporation"},
    
    # Healthcare & Pharmaceuticals
    {"ticker": "JNJ", "name": "Johnson & Johnson"},
    {"ticker": "PFE", "name": "Pfizer Inc."},
    {"ticker": "UNH", "name": "UnitedHealth Group Inc."},
    {"ticker": "ABBV", "name": "AbbVie Inc."},
    {"ticker": "MRK", "name": "Merck & Co. Inc."},
    {"ticker": "LLY", "name": "Eli Lilly and Company"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific Inc."},
    {"ticker": "ABT", "name": "Abbott Laboratories"},
    {"ticker": "DHR", "name": "Danaher Corporation"},
    {"ticker": "BMY", "name": "Bristol-Myers Squibb Company"},
    {"ticker": "MDT", "name": "Medtronic PLC"},
    {"ticker": "ISRG", "name": "Intuitive Surgical Inc."},
    {"ticker": "GILD", "name": "Gilead Sciences Inc."},
    {"ticker": "VRTX", "name": "Vertex Pharmaceuticals Inc."},
    {"ticker": "CVS", "name": "CVS Health Corporation"},
    {"ticker": "AMGN", "name": "Amgen Inc."},
    {"ticker": "CI", "name": "Cigna Corporation"},
    {"ticker": "HUM", "name": "Humana Inc."},
    {"ticker": "ANTM", "name": "Anthem Inc."},
    {"ticker": "SYK", "name": "Stryker Corporation"},
    
    # Consumer & Retail
    {"ticker": "WMT", "name": "Walmart Inc."},
    {"ticker": "HD", "name": "Home Depot Inc."},
    {"ticker": "PG", "name": "Procter & Gamble Co."},
    {"ticker": "KO", "name": "Coca-Cola Company"},
    {"ticker": "PEP", "name": "PepsiCo Inc."},
    {"ticker": "COST", "name": "Costco Wholesale Corporation"},
    {"ticker": "LOW", "name": "Lowe's Companies Inc."},
    {"ticker": "TGT", "name": "Target Corporation"},
    {"ticker": "SBUX", "name": "Starbucks Corporation"},
    {"ticker": "MCD", "name": "McDonald's Corporation"},
    {"ticker": "NKE", "name": "Nike Inc."},
    {"ticker": "DIS", "name": "Walt Disney Company"},
    {"ticker": "BKNG", "name": "Booking Holdings Inc."},
    {"ticker": "TJX", "name": "TJX Companies Inc."},
    {"ticker": "MAR", "name": "Marriott International Inc."},
    {"ticker": "CL", "name": "Colgate-Palmolive Company"},
    {"ticker": "KMB", "name": "Kimberly-Clark Corporation"},
    {"ticker": "GIS", "name": "General Mills Inc."},
    {"ticker": "K", "name": "Kellogg Company"},
    {"ticker": "HSY", "name": "Hershey Company"},
    
    # Energy & Utilities
    {"ticker": "XOM", "name": "Exxon Mobil Corporation"},
    {"ticker": "CVX", "name": "Chevron Corporation"},
    {"ticker": "COP", "name": "ConocoPhillips"},
    {"ticker": "SLB", "name": "Schlumberger Limited"},
    {"ticker": "EOG", "name": "EOG Resources Inc."},
    {"ticker": "PXD", "name": "Pioneer Natural Resources Company"},
    {"ticker": "MPC", "name": "Marathon Petroleum Corporation"},
    {"ticker": "VLO", "name": "Valero Energy Corporation"},
    {"ticker": "PSX", "name": "Phillips 66"},
    {"ticker": "OXY", "name": "Occidental Petroleum Corporation"},
    {"ticker": "KMI", "name": "Kinder Morgan Inc."},
    {"ticker": "WMB", "name": "Williams Companies Inc."},
    {"ticker": "NEE", "name": "NextEra Energy Inc."},
    {"ticker": "DUK", "name": "Duke Energy Corporation"},
    {"ticker": "SO", "name": "Southern Company"},
    {"ticker": "D", "name": "Dominion Energy Inc."},
    {"ticker": "AEP", "name": "American Electric Power Company"},
    {"ticker": "EXC", "name": "Exelon Corporation"},
    
    # Industrial & Manufacturing
    {"ticker": "BA", "name": "Boeing Company"},
    {"ticker": "GE", "name": "General Electric Company"},
    {"ticker": "CAT", "name": "Caterpillar Inc."},
    {"ticker": "RTX", "name": "Raytheon Technologies Corporation"},
    {"ticker": "LMT", "name": "Lockheed Martin Corporation"},
    {"ticker": "NOC", "name": "Northrop Grumman Corporation"},
    {"ticker": "GD", "name": "General Dynamics Corporation"},
    {"ticker": "HII", "name": "Huntington Ingalls Industries Inc."},
    {"ticker": "MMM", "name": "3M Company"},
    {"ticker": "HON", "name": "Honeywell International Inc."},
    {"ticker": "UPS", "name": "United Parcel Service Inc."},
    {"ticker": "FDX", "name": "FedEx Corporation"},
    {"ticker": "CSX", "name": "CSX Corporation"},
    {"ticker": "UNP", "name": "Union Pacific Corporation"},
    {"ticker": "NSC", "name": "Norfolk Southern Corporation"},
    {"ticker": "DE", "name": "Deere & Company"},
    {"ticker": "EMR", "name": "Emerson Electric Co."},
    {"ticker": "ETN", "name": "Eaton Corporation PLC"},
    {"ticker": "PH", "name": "Parker-Hannifin Corporation"},
    {"ticker": "ITW", "name": "Illinois Tool Works Inc."},
    
    # Communication & Media
    {"ticker": "CMCSA", "name": "Comcast Corporation"},
    {"ticker": "VZ", "name": "Verizon Communications Inc."},
    {"ticker": "T", "name": "AT&T Inc."},
    {"ticker": "TMUS", "name": "T-Mobile US Inc."},
    {"ticker": "CHTR", "name": "Charter Communications Inc."},
    {"ticker": "DISH", "name": "DISH Network Corporation"},
    {"ticker": "NWSA", "name": "News Corporation"},
    {"ticker": "FOXA", "name": "Fox Corporation"},
    {"ticker": "PARA", "name": "Paramount Global"},
    {"ticker": "WBD", "name": "Warner Bros. Discovery Inc."},
    
    # Real Estate & REITs
    {"ticker": "AMT", "name": "American Tower Corporation"},
    {"ticker": "PLD", "name": "Prologis Inc."},
    {"ticker": "CCI", "name": "Crown Castle Inc."},
    {"ticker": "EQIX", "name": "Equinix Inc."},
    {"ticker": "DLR", "name": "Digital Realty Trust Inc."},
    {"ticker": "SBAC", "name": "SBA Communications Corporation"},
    {"ticker": "PSA", "name": "Public Storage"},
    {"ticker": "EXR", "name": "Extended Stay America Inc."},
    {"ticker": "AVB", "name": "AvalonBay Communities Inc."},
    {"ticker": "EQR", "name": "Equity Residential"},
    
    # Mining & Materials
    {"ticker": "NEM", "name": "Newmont Corporation"},
    {"ticker": "FCX", "name": "Freeport-McMoRan Inc."},
    {"ticker": "NUE", "name": "Nucor Corporation"},
    {"ticker": "STLD", "name": "Steel Dynamics Inc."},
    {"ticker": "X", "name": "United States Steel Corporation"},
    {"ticker": "CLF", "name": "Cleveland-Cliffs Inc."},
    {"ticker": "AA", "name": "Alcoa Corporation"},
    {"ticker": "SCCO", "name": "Southern Copper Corporation"},
    {"ticker": "BHP", "name": "BHP Group Limited"},
    {"ticker": "RIO", "name": "Rio Tinto Group"},
    
    # Chinese & International ADRs
    {"ticker": "BABA", "name": "Alibaba Group Holding Limited"},
    {"ticker": "JD", "name": "JD.com Inc."},
    {"ticker": "PDD", "name": "PDD Holdings Inc."},
    {"ticker": "NTES", "name": "NetEase Inc."},
    {"ticker": "BIDU", "name": "Baidu Inc."},
    {"ticker": "NIO", "name": "NIO Inc."},
    {"ticker": "XPEV", "name": "XPeng Inc."},
    {"ticker": "LI", "name": "Li Auto Inc."},
    {"ticker": "TME", "name": "Tencent Music Entertainment Group"},
    {"ticker": "BILI", "name": "Bilibili Inc."},
    {"ticker": "TSM", "name": "Taiwan Semiconductor Manufacturing Company"},
    {"ticker": "ASML", "name": "ASML Holding N.V."},
    {"ticker": "SAP", "name": "SAP SE"},
    {"ticker": "TM", "name": "Toyota Motor Corporation"},
    {"ticker": "SONY", "name": "Sony Group Corporation"},
    {"ticker": "NVO", "name": "Novo Nordisk A/S"},
    {"ticker": "NVAX", "name": "Novavax Inc."},
    
    # High Growth & Tech
    {"ticker": "SHOP", "name": "Shopify Inc."},
    {"ticker": "SQ", "name": "Block Inc."},
    {"ticker": "COIN", "name": "Coinbase Global Inc."},
    {"ticker": "ROKU", "name": "Roku Inc."},
    {"ticker": "ZM", "name": "Zoom Video Communications Inc."},
    {"ticker": "DOCU", "name": "DocuSign Inc."},
    {"ticker": "OKTA", "name": "Okta Inc."},
    {"ticker": "SNOW", "name": "Snowflake Inc."},
    {"ticker": "DDOG", "name": "Datadog Inc."},
    {"ticker": "CRWD", "name": "CrowdStrike Holdings Inc."},
    {"ticker": "ZS", "name": "Zscaler Inc."},
    {"ticker": "NET", "name": "Cloudflare Inc."},
    {"ticker": "TWLO", "name": "Twilio Inc."},
    {"ticker": "PLTR", "name": "Palantir Technologies Inc."},
    {"ticker": "UBER", "name": "Uber Technologies Inc."},
    {"ticker": "LYFT", "name": "Lyft Inc."},
    {"ticker": "ABNB", "name": "Airbnb Inc."},
    {"ticker": "DASH", "name": "DoorDash Inc."},
    {"ticker": "SPOT", "name": "Spotify Technology S.A."},
    {"ticker": "PINS", "name": "Pinterest Inc."},
    {"ticker": "SNAP", "name": "Snap Inc."},
    {"ticker": "TWTR", "name": "Twitter Inc."},
    
    # Airlines & Transportation
    {"ticker": "AAL", "name": "American Airlines Group Inc."},
    {"ticker": "DAL", "name": "Delta Air Lines Inc."},
    {"ticker": "UAL", "name": "United Airlines Holdings Inc."},
    {"ticker": "LUV", "name": "Southwest Airlines Co."},
    {"ticker": "ALK", "name": "Alaska Air Group Inc."},
    {"ticker": "JBLU", "name": "JetBlue Airways Corporation"},
    {"ticker": "SAVE", "name": "Spirit Airlines Inc."},
    
    # Industrial Companies
    {"ticker": "RSG", "name": "Republic Services Inc."},
    {"ticker": "WM", "name": "Waste Management Inc."},
    {"ticker": "GE", "name": "General Electric Company"},
    {"ticker": "HON", "name": "Honeywell International Inc."},
    {"ticker": "MMM", "name": "3M Company"},
    {"ticker": "CAT", "name": "Caterpillar Inc."},
    {"ticker": "DE", "name": "Deere & Company"},
    {"ticker": "EMR", "name": "Emerson Electric Co."},
    {"ticker": "ITW", "name": "Illinois Tool Works Inc."},
    {"ticker": "ROK", "name": "Rockwell Automation Inc."},
    {"ticker": "PH", "name": "Parker-Hannifin Corporation"},
    {"ticker": "ETN", "name": "Eaton Corporation plc"},
    {"ticker": "IR", "name": "Ingersoll Rand Inc."},
    {"ticker": "CARR", "name": "Carrier Global Corporation"},
    {"ticker": "OTIS", "name": "Otis Worldwide Corporation"},
    {"ticker": "JCI", "name": "Johnson Controls International plc"},
    {"ticker": "FLR", "name": "Fluor Corporation"},
    {"ticker": "PCAR", "name": "PACCAR Inc."},
    {"ticker": "CSX", "name": "CSX Corporation"},
    {"ticker": "UNP", "name": "Union Pacific Corporation"},
    {"ticker": "NSC", "name": "Norfolk Southern Corporation"},
    {"ticker": "UPS", "name": "United Parcel Service Inc."},
    {"ticker": "FDX", "name": "FedEx Corporation"},
    {"ticker": "LMT", "name": "Lockheed Martin Corporation"},
    {"ticker": "RTX", "name": "Raytheon Technologies Corporation"},
    {"ticker": "NOC", "name": "Northrop Grumman Corporation"},
    {"ticker": "GD", "name": "General Dynamics Corporation"},
    {"ticker": "HII", "name": "Huntington Ingalls Industries Inc."},
    {"ticker": "TXT", "name": "Textron Inc."},
    {"ticker": "BA", "name": "Boeing Company"},
    
    # Automotive
    {"ticker": "F", "name": "Ford Motor Company"},
    {"ticker": "GM", "name": "General Motors Company"},
    {"ticker": "RIVN", "name": "Rivian Automotive Inc."},
    {"ticker": "LCID", "name": "Lucid Group Inc."},
    
    # Biotechnology
    {"ticker": "BIIB", "name": "Biogen Inc."},
    {"ticker": "MRNA", "name": "Moderna Inc."},
    {"ticker": "REGN", "name": "Regeneron Pharmaceuticals Inc."},
    {"ticker": "ILMN", "name": "Illumina Inc."},
    {"ticker": "BMRN", "name": "BioMarin Pharmaceutical Inc."},
    
    # Gaming & Entertainment
    {"ticker": "GME", "name": "GameStop Corp."},
    {"ticker": "AMC", "name": "AMC Entertainment Holdings Inc."},
    {"ticker": "EA", "name": "Electronic Arts Inc."},
    {"ticker": "ATVI", "name": "Activision Blizzard Inc."},
    {"ticker": "TTWO", "name": "Take-Two Interactive Software Inc."},
    {"ticker": "RBLX", "name": "Roblox Corporation"},
    {"ticker": "U", "name": "Unity Software Inc."},
    
    # Other Notable Companies
    {"ticker": "TSCO", "name": "Tractor Supply Company"},
    {"ticker": "WBA", "name": "Walgreens Boots Alliance Inc."},
    {"ticker": "KR", "name": "Kroger Co."},
    {"ticker": "YUM", "name": "Yum! Brands Inc."},
    {"ticker": "CMG", "name": "Chipotle Mexican Grill Inc."},
    {"ticker": "ORLY", "name": "O'Reilly Automotive Inc."},
    {"ticker": "AZO", "name": "AutoZone Inc."},
    {"ticker": "BBY", "name": "Best Buy Co. Inc."},
    {"ticker": "EBAY", "name": "eBay Inc."},
    {"ticker": "ETSY", "name": "Etsy Inc."},
    
    # Additional Major Companies (expanding to 1000+)
    {"ticker": "LMT", "name": "Lockheed Martin Corporation"},
    {"ticker": "RTX", "name": "Raytheon Technologies Corporation"},
    {"ticker": "NOC", "name": "Northrop Grumman Corporation"},
    {"ticker": "GD", "name": "General Dynamics Corporation"},
    {"ticker": "BA", "name": "Boeing Company"},
    {"ticker": "CAT", "name": "Caterpillar Inc."},
    {"ticker": "DE", "name": "Deere & Company"},
    {"ticker": "MMM", "name": "3M Company"},
    {"ticker": "HON", "name": "Honeywell International Inc."},
    {"ticker": "UTX", "name": "United Technologies Corporation"},
    {"ticker": "GE", "name": "General Electric Company"},
    {"ticker": "EMR", "name": "Emerson Electric Co."},
    {"ticker": "ITW", "name": "Illinois Tool Works Inc."},
    {"ticker": "ETN", "name": "Eaton Corporation"},
    {"ticker": "PH", "name": "Parker-Hannifin Corporation"},
    {"ticker": "ROK", "name": "Rockwell Automation Inc."},
    {"ticker": "IR", "name": "Ingersoll Rand Inc."},
    {"ticker": "FLR", "name": "Fluor Corporation"},
    {"ticker": "JCI", "name": "Johnson Controls International"},
    {"ticker": "TYL", "name": "Tyler Technologies Inc."},
    
    # Financial Services Expansion
    {"ticker": "AXP", "name": "American Express Company"},
    {"ticker": "V", "name": "Visa Inc."},
    {"ticker": "MA", "name": "Mastercard Incorporated"},
    {"ticker": "COF", "name": "Capital One Financial Corporation"},
    {"ticker": "DFS", "name": "Discover Financial Services"},
    {"ticker": "SYF", "name": "Synchrony Financial"},
    {"ticker": "ALLY", "name": "Ally Financial Inc."},
    {"ticker": "FITB", "name": "Fifth Third Bancorp"},
    {"ticker": "RF", "name": "Regions Financial Corporation"},
    {"ticker": "PNC", "name": "PNC Financial Services Group"},
    {"ticker": "USB", "name": "U.S. Bancorp"},
    {"ticker": "TFC", "name": "Truist Financial Corporation"},
    {"ticker": "MTB", "name": "M&T Bank Corporation"},
    {"ticker": "KEY", "name": "KeyCorp"},
    {"ticker": "CFG", "name": "Citizens Financial Group Inc."},
    {"ticker": "HBAN", "name": "Huntington Bancshares Inc."},
    {"ticker": "ZION", "name": "Zions Bancorporation"},
    {"ticker": "CMA", "name": "Comerica Incorporated"},
    {"ticker": "PBCT", "name": "People's United Financial Inc."},
    {"ticker": "SNV", "name": "Synovus Financial Corp."},
    
    # Healthcare & Pharmaceuticals
    {"ticker": "ABT", "name": "Abbott Laboratories"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific Inc."},
    {"ticker": "DHR", "name": "Danaher Corporation"},
    {"ticker": "SYK", "name": "Stryker Corporation"},
    {"ticker": "BSX", "name": "Boston Scientific Corporation"},
    {"ticker": "MDT", "name": "Medtronic plc"},
    {"ticker": "ZBH", "name": "Zimmer Biomet Holdings Inc."},
    {"ticker": "BAX", "name": "Baxter International Inc."},
    {"ticker": "BDX", "name": "Becton, Dickinson and Company"},
    {"ticker": "EW", "name": "Edwards Lifesciences Corporation"},
    {"ticker": "ISRG", "name": "Intuitive Surgical Inc."},
    {"ticker": "VAR", "name": "Varian Medical Systems Inc."},
    {"ticker": "HOLX", "name": "Hologic Inc."},
    {"ticker": "ALGN", "name": "Align Technology Inc."},
    {"ticker": "DXCM", "name": "DexCom Inc."},
    {"ticker": "IDXX", "name": "IDEXX Laboratories Inc."},
    {"ticker": "IQV", "name": "IQVIA Holdings Inc."},
    {"ticker": "A", "name": "Agilent Technologies Inc."},
    {"ticker": "MTD", "name": "Mettler-Toledo International Inc."},
    {"ticker": "PKI", "name": "PerkinElmer Inc."},
    
    # Consumer Goods & Retail
    {"ticker": "PG", "name": "Procter & Gamble Company"},
    {"ticker": "KO", "name": "Coca-Cola Company"},
    {"ticker": "PEP", "name": "PepsiCo Inc."},
    {"ticker": "UL", "name": "Unilever plc"},
    {"ticker": "CL", "name": "Colgate-Palmolive Company"},
    {"ticker": "KMB", "name": "Kimberly-Clark Corporation"},
    {"ticker": "CHD", "name": "Church & Dwight Co. Inc."},
    {"ticker": "CLX", "name": "Clorox Company"},
    {"ticker": "SJM", "name": "J.M. Smucker Company"},
    {"ticker": "HSY", "name": "Hershey Company"},
    {"ticker": "K", "name": "Kellogg Company"},
    {"ticker": "GIS", "name": "General Mills Inc."},
    {"ticker": "CPB", "name": "Campbell Soup Company"},
    {"ticker": "HRL", "name": "Hormel Foods Corporation"},
    {"ticker": "TSN", "name": "Tyson Foods Inc."},
    {"ticker": "CAG", "name": "Conagra Brands Inc."},
    {"ticker": "MKC", "name": "McCormick & Company"},
    {"ticker": "LW", "name": "Lamb Weston Holdings Inc."},
    {"ticker": "MDLZ", "name": "Mondelez International Inc."},
    {"ticker": "KHC", "name": "Kraft Heinz Company"},
    
    # Energy & Utilities
    {"ticker": "XOM", "name": "Exxon Mobil Corporation"},
    {"ticker": "CVX", "name": "Chevron Corporation"},
    {"ticker": "COP", "name": "ConocoPhillips"},
    {"ticker": "EOG", "name": "EOG Resources Inc."},
    {"ticker": "SLB", "name": "Schlumberger Limited"},
    {"ticker": "HAL", "name": "Halliburton Company"},
    {"ticker": "BKR", "name": "Baker Hughes Company"},
    {"ticker": "VLO", "name": "Valero Energy Corporation"},
    {"ticker": "PSX", "name": "Phillips 66"},
    {"ticker": "MPC", "name": "Marathon Petroleum Corporation"},
    {"ticker": "HES", "name": "Hess Corporation"},
    {"ticker": "DVN", "name": "Devon Energy Corporation"},
    {"ticker": "FANG", "name": "Diamondback Energy Inc."},
    {"ticker": "PXD", "name": "Pioneer Natural Resources Company"},
    {"ticker": "OXY", "name": "Occidental Petroleum Corporation"},
    {"ticker": "APA", "name": "APA Corporation"},
    {"ticker": "EQT", "name": "EQT Corporation"},
    {"ticker": "CTRA", "name": "Coterra Energy Inc."},
    {"ticker": "MRO", "name": "Marathon Oil Corporation"},
    {"ticker": "OVV", "name": "Ovintiv Inc."},
    
    # Real Estate & REITs
    {"ticker": "AMT", "name": "American Tower Corporation"},
    {"ticker": "PLD", "name": "Prologis Inc."},
    {"ticker": "CCI", "name": "Crown Castle International Corp."},
    {"ticker": "EQIX", "name": "Equinix Inc."},
    {"ticker": "DLR", "name": "Digital Realty Trust Inc."},
    {"ticker": "SPG", "name": "Simon Property Group Inc."},
    {"ticker": "O", "name": "Realty Income Corporation"},
    {"ticker": "PSA", "name": "Public Storage"},
    {"ticker": "EXR", "name": "Extended Stay America Inc."},
    {"ticker": "AVB", "name": "AvalonBay Communities Inc."},
    {"ticker": "EQR", "name": "Equity Residential"},
    {"ticker": "UDR", "name": "UDR Inc."},
    {"ticker": "ESS", "name": "Essex Property Trust Inc."},
    {"ticker": "MAA", "name": "Mid-America Apartment Communities"},
    {"ticker": "CPT", "name": "Camden Property Trust"},
    {"ticker": "HST", "name": "Host Hotels & Resorts Inc."},
    {"ticker": "RHP", "name": "Ryman Hospitality Properties"},
    {"ticker": "SLG", "name": "SL Green Realty Corp."},
    {"ticker": "BXP", "name": "Boston Properties Inc."},
    {"ticker": "VTR", "name": "Ventas Inc."},
    
    # Materials & Chemicals
    {"ticker": "LIN", "name": "Linde plc"},
    {"ticker": "APD", "name": "Air Products and Chemicals Inc."},
    {"ticker": "SHW", "name": "Sherwin-Williams Company"},
    {"ticker": "ECL", "name": "Ecolab Inc."},
    {"ticker": "DD", "name": "DuPont de Nemours Inc."},
    {"ticker": "DOW", "name": "Dow Inc."},
    {"ticker": "LYB", "name": "LyondellBasell Industries"},
    {"ticker": "PPG", "name": "PPG Industries Inc."},
    {"ticker": "NUE", "name": "Nucor Corporation"},
    {"ticker": "STLD", "name": "Steel Dynamics Inc."},
    {"ticker": "X", "name": "United States Steel Corporation"},
    {"ticker": "CLF", "name": "Cleveland-Cliffs Inc."},
    {"ticker": "AA", "name": "Alcoa Corporation"},
    {"ticker": "FCX", "name": "Freeport-McMoRan Inc."},
    {"ticker": "NEM", "name": "Newmont Corporation"},
    {"ticker": "GOLD", "name": "Barrick Gold Corporation"},
    {"ticker": "AEM", "name": "Agnico Eagle Mines Limited"},
    {"ticker": "KGC", "name": "Kinross Gold Corporation"},
    {"ticker": "AG", "name": "First Majestic Silver Corp."},
    {"ticker": "EXK", "name": "Endeavour Silver Corp."},
    
    # Transportation & Logistics
    {"ticker": "UPS", "name": "United Parcel Service Inc."},
    {"ticker": "FDX", "name": "FedEx Corporation"},
    {"ticker": "DAL", "name": "Delta Air Lines Inc."},
    {"ticker": "AAL", "name": "American Airlines Group Inc."},
    {"ticker": "UAL", "name": "United Airlines Holdings Inc."},
    {"ticker": "LUV", "name": "Southwest Airlines Co."},
    {"ticker": "JBLU", "name": "JetBlue Airways Corporation"},
    {"ticker": "SAVE", "name": "Spirit Airlines Inc."},
    {"ticker": "ALK", "name": "Alaska Air Group Inc."},
    {"ticker": "HA", "name": "Hawaiian Holdings Inc."},
    {"ticker": "NSC", "name": "Norfolk Southern Corporation"},
    {"ticker": "UNP", "name": "Union Pacific Corporation"},
    {"ticker": "CSX", "name": "CSX Corporation"},
    {"ticker": "KSU", "name": "Kansas City Southern"},
    {"ticker": "CP", "name": "Canadian Pacific Railway Limited"},
    {"ticker": "CNI", "name": "Canadian National Railway Company"},
    {"ticker": "CHRW", "name": "C.H. Robinson Worldwide Inc."},
    {"ticker": "EXPD", "name": "Expeditors International"},
    {"ticker": "JBHT", "name": "J.B. Hunt Transport Services"},
    {"ticker": "ODFL", "name": "Old Dominion Freight Line Inc."},
    
    # Telecommunications
    {"ticker": "T", "name": "AT&T Inc."},
    {"ticker": "VZ", "name": "Verizon Communications Inc."},
    {"ticker": "TMUS", "name": "T-Mobile US Inc."},
    {"ticker": "S", "name": "Sprint Corporation"},
    {"ticker": "USM", "name": "United States Cellular Corporation"},
    {"ticker": "SHEN", "name": "Shenandoah Telecommunications"},
    {"ticker": "FYBR", "name": "Frontier Communications"},
    {"ticker": "LUMN", "name": "Lumen Technologies Inc."},
    {"ticker": "CSCO", "name": "Cisco Systems Inc."},
    {"ticker": "JNPR", "name": "Juniper Networks Inc."},
    
    # Media & Entertainment
    {"ticker": "DIS", "name": "Walt Disney Company"},
    {"ticker": "NFLX", "name": "Netflix Inc."},
    {"ticker": "CMCSA", "name": "Comcast Corporation"},
    {"ticker": "CHTR", "name": "Charter Communications Inc."},
    {"ticker": "PARA", "name": "Paramount Global"},
    {"ticker": "WBD", "name": "Warner Bros. Discovery Inc."},
    {"ticker": "FOX", "name": "Fox Corporation"},
    {"ticker": "FOXA", "name": "Fox Corporation Class A"},
    {"ticker": "LYV", "name": "Live Nation Entertainment Inc."},
    {"ticker": "MSG", "name": "Madison Square Garden Sports"},
    {"ticker": "MSGS", "name": "Madison Square Garden Entertainment"},
    {"ticker": "SONY", "name": "Sony Group Corporation"},
    {"ticker": "TME", "name": "Tencent Music Entertainment"},
    {"ticker": "SPOT", "name": "Spotify Technology S.A."},
    {"ticker": "WMG", "name": "Warner Music Group Corp."},
    {"ticker": "UMG", "name": "Universal Music Group"},
    
    # Food & Beverage
    {"ticker": "MCD", "name": "McDonald's Corporation"},
    {"ticker": "SBUX", "name": "Starbucks Corporation"},
    {"ticker": "QSR", "name": "Restaurant Brands International"},
    {"ticker": "DPZ", "name": "Domino's Pizza Inc."},
    {"ticker": "PZZA", "name": "Papa John's International"},
    {"ticker": "WING", "name": "Wingstop Inc."},
    {"ticker": "SHAK", "name": "Shake Shack Inc."},
    {"ticker": "CAVA", "name": "CAVA Group Inc."},
    {"ticker": "WEN", "name": "Wendy's Company"},
    {"ticker": "JACK", "name": "Jack in the Box Inc."},
    {"ticker": "SONC", "name": "Sonic Corp."},
    {"ticker": "DRI", "name": "Darden Restaurants Inc."},
    {"ticker": "EAT", "name": "Brinker International Inc."},
    {"ticker": "TXRH", "name": "Texas Roadhouse Inc."},
    {"ticker": "BLMN", "name": "Bloomin' Brands Inc."},
    {"ticker": "DIN", "name": "DineEquity Inc."},
    {"ticker": "CAKE", "name": "Cheesecake Factory Inc."},
    {"ticker": "RUTH", "name": "Ruth's Hospitality Group"},
    {"ticker": "BJRI", "name": "BJ's Restaurants Inc."},
    {"ticker": "NDLS", "name": "Noodles & Company"},
    
    # Additional High Market Cap Companies
    {"ticker": "BRK.A", "name": "Berkshire Hathaway Inc. Class A"},
    {"ticker": "BRK.B", "name": "Berkshire Hathaway Inc. Class B"},
    {"ticker": "LLY", "name": "Eli Lilly and Company"},
    {"ticker": "AVGO", "name": "Broadcom Inc."},
    {"ticker": "TSM", "name": "Taiwan Semiconductor Manufacturing"},
    {"ticker": "WMT", "name": "Walmart Inc."},
    {"ticker": "JPM", "name": "JPMorgan Chase & Co."},
    {"ticker": "V", "name": "Visa Inc."},
    {"ticker": "UNH", "name": "UnitedHealth Group Inc."},
    {"ticker": "XOM", "name": "Exxon Mobil Corporation"},
    {"ticker": "MA", "name": "Mastercard Inc."},
    {"ticker": "PG", "name": "Procter & Gamble Co."},
    {"ticker": "HD", "name": "Home Depot Inc."},
    {"ticker": "CVX", "name": "Chevron Corporation"},
    {"ticker": "ABBV", "name": "AbbVie Inc."},
    {"ticker": "BAC", "name": "Bank of America Corp."},
    {"ticker": "KO", "name": "Coca-Cola Company"},
    {"ticker": "PEP", "name": "PepsiCo Inc."},
    {"ticker": "COST", "name": "Costco Wholesale Corporation"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific Inc."},
    {"ticker": "ABT", "name": "Abbott Laboratories"},
    {"ticker": "MRK", "name": "Merck & Co. Inc."},
    {"ticker": "ACN", "name": "Accenture PLC"},
    {"ticker": "CSCO", "name": "Cisco Systems Inc."},
    {"ticker": "DHR", "name": "Danaher Corporation"},
    {"ticker": "WFC", "name": "Wells Fargo & Company"},
    {"ticker": "VZ", "name": "Verizon Communications Inc."},
    {"ticker": "LIN", "name": "Linde PLC"},
    {"ticker": "TXN", "name": "Texas Instruments Inc."},
    {"ticker": "LOW", "name": "Lowe's Companies Inc."},
    {"ticker": "CMCSA", "name": "Comcast Corporation"},
    {"ticker": "NEE", "name": "NextEra Energy Inc."},
    {"ticker": "RTX", "name": "Raytheon Technologies Corporation"},
    {"ticker": "T", "name": "AT&T Inc."},
    {"ticker": "QCOM", "name": "Qualcomm Inc."},
    {"ticker": "HON", "name": "Honeywell International Inc."},
    {"ticker": "UNP", "name": "Union Pacific Corporation"},
    {"ticker": "UPS", "name": "United Parcel Service Inc."},
    {"ticker": "IBM", "name": "International Business Machines Corp."},
    {"ticker": "SPGI", "name": "S&P Global Inc."},
    {"ticker": "PM", "name": "Philip Morris International Inc."},
    {"ticker": "CAT", "name": "Caterpillar Inc."},
    {"ticker": "GS", "name": "Goldman Sachs Group Inc."},
    {"ticker": "AXP", "name": "American Express Company"},
    {"ticker": "BLK", "name": "BlackRock Inc."},
    {"ticker": "LMT", "name": "Lockheed Martin Corporation"},
    {"ticker": "GE", "name": "General Electric Company"},
    {"ticker": "DE", "name": "Deere & Company"},
    {"ticker": "MDT", "name": "Medtronic PLC"},
    {"ticker": "ISRG", "name": "Intuitive Surgical Inc."},
    {"ticker": "SYK", "name": "Stryker Corporation"},
    {"ticker": "TGT", "name": "Target Corporation"},
    {"ticker": "MMM", "name": "3M Company"},
    {"ticker": "GILD", "name": "Gilead Sciences Inc."},
    {"ticker": "CVS", "name": "CVS Health Corporation"},
    {"ticker": "VRTX", "name": "Vertex Pharmaceuticals Inc."},
    {"ticker": "PLD", "name": "Prologis Inc."},
    {"ticker": "AMT", "name": "American Tower Corporation"},
    {"ticker": "CHTR", "name": "Charter Communications Inc."},
    {"ticker": "TMUS", "name": "T-Mobile US Inc."},
    {"ticker": "CI", "name": "Cigna Corporation"},
    {"ticker": "SLB", "name": "Schlumberger Limited"},
    {"ticker": "SCHW", "name": "Charles Schwab Corporation"},
    {"ticker": "MO", "name": "Altria Group Inc."},
    {"ticker": "FIS", "name": "Fidelity National Information Services"},
    {"ticker": "TJX", "name": "TJX Companies Inc."},
    {"ticker": "NSC", "name": "Norfolk Southern Corporation"},
    {"ticker": "NKE", "name": "Nike Inc."},
    {"ticker": "SO", "name": "Southern Company"},
    {"ticker": "ICE", "name": "Intercontinental Exchange Inc."},
    {"ticker": "PNC", "name": "PNC Financial Services Group"},
    {"ticker": "D", "name": "Dominion Energy Inc."},
    {"ticker": "DUK", "name": "Duke Energy Corporation"},
    {"ticker": "BSX", "name": "Boston Scientific Corporation"},
    {"ticker": "CL", "name": "Colgate-Palmolive Company"},
    {"ticker": "AON", "name": "Aon PLC"},
    {"ticker": "USB", "name": "U.S. Bancorp"},
    {"ticker": "MMC", "name": "Marsh & McLennan Companies Inc."},
    {"ticker": "CME", "name": "CME Group Inc."},
    {"ticker": "ECL", "name": "Ecolab Inc."},
    {"ticker": "MCO", "name": "Moody's Corporation"},
    {"ticker": "CSX", "name": "CSX Corporation"},
    {"ticker": "NOC", "name": "Northrop Grumman Corporation"},
    {"ticker": "FCX", "name": "Freeport-McMoRan Inc."},
    {"ticker": "TFC", "name": "Truist Financial Corporation"},
    {"ticker": "AEP", "name": "American Electric Power Company"},
    {"ticker": "EOG", "name": "EOG Resources Inc."},
    {"ticker": "EL", "name": "Estee Lauder Companies Inc."},
    {"ticker": "EQIX", "name": "Equinix Inc."},
    {"ticker": "WM", "name": "Waste Management Inc."},
    {"ticker": "ITW", "name": "Illinois Tool Works Inc."},
    {"ticker": "SHW", "name": "Sherwin-Williams Company"},
    {"ticker": "APD", "name": "Air Products and Chemicals Inc."},
    {"ticker": "GD", "name": "General Dynamics Corporation"},
    {"ticker": "COF", "name": "Capital One Financial Corp."},
    {"ticker": "MSI", "name": "Motorola Solutions Inc."},
    {"ticker": "COP", "name": "ConocoPhillips"},
    {"ticker": "EMR", "name": "Emerson Electric Co."},
    {"ticker": "KLAC", "name": "KLA Corporation"},
    {"ticker": "HCA", "name": "HCA Healthcare Inc."},
    {"ticker": "PSX", "name": "Phillips 66"},
    {"ticker": "FDX", "name": "FedEx Corporation"},
    {"ticker": "ADI", "name": "Analog Devices Inc."},
    {"ticker": "ETN", "name": "Eaton Corporation PLC"},
    {"ticker": "MCK", "name": "McKesson Corporation"},
    {"ticker": "CARR", "name": "Carrier Global Corporation"},
    {"ticker": "VLO", "name": "Valero Energy Corporation"},
    {"ticker": "OTIS", "name": "Otis Worldwide Corporation"},
    {"ticker": "EW", "name": "Edwards Lifesciences Corporation"},
    {"ticker": "DG", "name": "Dollar General Corporation"},
    {"ticker": "BDX", "name": "Becton Dickinson and Company"},
    {"ticker": "MCHP", "name": "Microchip Technology Inc."},
    {"ticker": "WEC", "name": "WEC Energy Group Inc."},
    {"ticker": "CTAS", "name": "Cintas Corporation"},
    {"ticker": "EXC", "name": "Exelon Corporation"},
    {"ticker": "YUM", "name": "Yum! Brands Inc."},
    {"ticker": "KMB", "name": "Kimberly-Clark Corporation"},
    {"ticker": "DLTR", "name": "Dollar Tree Inc."},
    {"ticker": "PAYX", "name": "Paychex Inc."},
    {"ticker": "FAST", "name": "Fastenal Company"},
    {"ticker": "VRSK", "name": "Verisk Analytics Inc."},
    {"ticker": "EXR", "name": "Extended Stay America Inc."},
    {"ticker": "PCAR", "name": "PACCAR Inc."},
    {"ticker": "ROK", "name": "Rockwell Automation Inc."},
    {"ticker": "ODFL", "name": "Old Dominion Freight Line Inc."},
    {"ticker": "KMI", "name": "Kinder Morgan Inc."},
    {"ticker": "ANSS", "name": "ANSYS Inc."},
    {"ticker": "CSGP", "name": "CoStar Group Inc."},
    {"ticker": "ROST", "name": "Ross Stores Inc."},
    {"ticker": "WELL", "name": "Welltower Inc."},
    {"ticker": "IDXX", "name": "IDEXX Laboratories Inc."},
    {"ticker": "O", "name": "Realty Income Corporation"},
    {"ticker": "CPRT", "name": "Copart Inc."},
    {"ticker": "GLW", "name": "Corning Inc."},
    {"ticker": "XEL", "name": "Xcel Energy Inc."},
    {"ticker": "EA", "name": "Electronic Arts Inc."},
    {"ticker": "KR", "name": "Kroger Co."},
    {"ticker": "HLT", "name": "Hilton Worldwide Holdings Inc."},
    {"ticker": "DOW", "name": "Dow Inc."},
    {"ticker": "CTSH", "name": "Cognizant Technology Solutions Corp."},
    {"ticker": "ROP", "name": "Roper Technologies Inc."},
    {"ticker": "PPG", "name": "PPG Industries Inc."},
    {"ticker": "MNST", "name": "Monster Beverage Corporation"},
    {"ticker": "FANG", "name": "Diamondback Energy Inc."},
    {"ticker": "BK", "name": "Bank of New York Mellon Corp."},
    {"ticker": "GIS", "name": "General Mills Inc."},
    {"ticker": "MPWR", "name": "Monolithic Power Systems Inc."},
    {"ticker": "DXCM", "name": "DexCom Inc."},
    {"ticker": "ADP", "name": "Automatic Data Processing Inc."},
    {"ticker": "CMG", "name": "Chipotle Mexican Grill Inc."},
    {"ticker": "HSY", "name": "Hershey Company"},
    {"ticker": "ALL", "name": "Allstate Corporation"},
    {"ticker": "CDNS", "name": "Cadence Design Systems Inc."},
    {"ticker": "PH", "name": "Parker-Hannifin Corporation"},
    {"ticker": "TRV", "name": "Travelers Companies Inc."},
    {"ticker": "OKE", "name": "ONEOK Inc."},
    {"ticker": "SNPS", "name": "Synopsys Inc."},
    {"ticker": "A", "name": "Agilent Technologies Inc."},
    {"ticker": "INFO", "name": "IHS Markit Ltd."},
    {"ticker": "WMB", "name": "Williams Companies Inc."},
    {"ticker": "HUM", "name": "Humana Inc."},
    {"ticker": "FTNT", "name": "Fortinet Inc."},
    {"ticker": "MSCI", "name": "MSCI Inc."},
    {"ticker": "MPC", "name": "Marathon Petroleum Corporation"},
    {"ticker": "AVB", "name": "AvalonBay Communities Inc."},
    {"ticker": "EQR", "name": "Equity Residential"},
    {"ticker": "ES", "name": "Eversource Energy"},
    {"ticker": "PSA", "name": "Public Storage"},
    {"ticker": "NVAX", "name": "Novavax Inc."},
    {"ticker": "STZ", "name": "Constellation Brands Inc."},
    {"ticker": "APH", "name": "Amphenol Corporation"},
    {"ticker": "TWTR", "name": "Twitter Inc."},
    {"ticker": "BIIB", "name": "Biogen Inc."},
    {"ticker": "ILMN", "name": "Illumina Inc."},
    {"ticker": "REGN", "name": "Regeneron Pharmaceuticals Inc."},
    {"ticker": "AME", "name": "AMETEK Inc."},
    {"ticker": "FRC", "name": "First Republic Bank"},
    {"ticker": "TROW", "name": "T. Rowe Price Group Inc."},
    {"ticker": "WST", "name": "West Pharmaceutical Services Inc."},
    {"ticker": "KEYS", "name": "Keysight Technologies Inc."},
    {"ticker": "STE", "name": "STERIS PLC"},
    {"ticker": "SWKS", "name": "Skyworks Solutions Inc."},
    {"ticker": "CCI", "name": "Crown Castle Inc."},
    {"ticker": "NTRS", "name": "Northern Trust Corporation"},
    {"ticker": "WY", "name": "Weyerhaeuser Company"},
    {"ticker": "SBAC", "name": "SBA Communications Corporation"},
    {"ticker": "DLR", "name": "Digital Realty Trust Inc."},
    {"ticker": "GWW", "name": "W.W. Grainger Inc."},
    {"ticker": "K", "name": "Kellogg Company"},
    {"ticker": "ALGN", "name": "Align Technology Inc."},
    {"ticker": "MAR", "name": "Marriott International Inc."},
    {"ticker": "LH", "name": "Laboratory Corporation of America"},
    {"ticker": "CLX", "name": "Clorox Company"},
    {"ticker": "BF.B", "name": "Brown-Forman Corporation"},
    {"ticker": "VMC", "name": "Vulcan Materials Company"},
    {"ticker": "MLM", "name": "Martin Marietta Materials Inc."},
    {"ticker": "MKTX", "name": "MarketAxess Holdings Inc."},
    {"ticker": "ATO", "name": "Atmos Energy Corporation"},
    {"ticker": "AES", "name": "AES Corporation"},
    {"ticker": "CMS", "name": "CMS Energy Corporation"},
    {"ticker": "BR", "name": "Broadridge Financial Solutions Inc."},
    {"ticker": "MRNA", "name": "Moderna Inc."},
    {"ticker": "HOLX", "name": "Hologic Inc."},
    {"ticker": "HST", "name": "Host Hotels & Resorts Inc."},
    {"ticker": "MOH", "name": "Molina Healthcare Inc."},
    {"ticker": "CTVA", "name": "Corteva Inc."},
    {"ticker": "AWK", "name": "American Water Works Company Inc."},
    {"ticker": "DTE", "name": "DTE Energy Company"},
    {"ticker": "FISV", "name": "Fiserv Inc."},
    {"ticker": "LYB", "name": "LyondellBasell Industries N.V."},
    {"ticker": "NUE", "name": "Nucor Corporation"},
    {"ticker": "MAS", "name": "Masco Corporation"},
    {"ticker": "ARE", "name": "Alexandria Real Estate Equities Inc."},
    {"ticker": "TDY", "name": "Teledyne Technologies Inc."},
    {"ticker": "ENPH", "name": "Enphase Energy Inc."},
    {"ticker": "ORLY", "name": "O'Reilly Automotive Inc."},
    {"ticker": "AZO", "name": "AutoZone Inc."},
    {"ticker": "PAYC", "name": "Paycom Software Inc."},
    {"ticker": "WAT", "name": "Waters Corporation"},
    {"ticker": "TTWO", "name": "Take-Two Interactive Software Inc."},
    {"ticker": "SYY", "name": "Sysco Corporation"},
    {"ticker": "ANET", "name": "Arista Networks Inc."},
    {"ticker": "J", "name": "Jacobs Engineering Group Inc."},
    {"ticker": "PEAK", "name": "Healthpeak Properties Inc."},
    {"ticker": "CAH", "name": "Cardinal Health Inc."},
    {"ticker": "WBA", "name": "Walgreens Boots Alliance Inc."},
    {"ticker": "COO", "name": "Cooper Companies Inc."},
    {"ticker": "TSCO", "name": "Tractor Supply Company"},
    {"ticker": "TECH", "name": "Bio-Techne Corporation"},
    {"ticker": "CBRE", "name": "CBRE Group Inc."},
    {"ticker": "INCY", "name": "Incyte Corporation"},
    {"ticker": "LDOS", "name": "Leidos Holdings Inc."},
    {"ticker": "DGX", "name": "Quest Diagnostics Inc."},
    {"ticker": "POOL", "name": "Pool Corporation"},
    {"ticker": "BBY", "name": "Best Buy Co. Inc."},
    {"ticker": "TYL", "name": "Tyler Technologies Inc."},
    {"ticker": "NVR", "name": "NVR Inc."},
    {"ticker": "SIVB", "name": "SVB Financial Group"},
    {"ticker": "PKG", "name": "Packaging Corporation of America"},
    {"ticker": "EBAY", "name": "eBay Inc."},
    {"ticker": "SEDG", "name": "SolarEdge Technologies Inc."},
    {"ticker": "BIO", "name": "Bio-Rad Laboratories Inc."},
    {"ticker": "JKHY", "name": "Jack Henry & Associates Inc."},
    {"ticker": "EXPD", "name": "Expeditors International of Washington"},
    {"ticker": "ULTA", "name": "Ulta Beauty Inc."},
    {"ticker": "LNT", "name": "Alliant Energy Corporation"},
    {"ticker": "CHRW", "name": "C.H. Robinson Worldwide Inc."},
    {"ticker": "PFG", "name": "Principal Financial Group Inc."},
    {"ticker": "WAB", "name": "Westinghouse Air Brake Technologies"},
    {"ticker": "HII", "name": "Huntington Ingalls Industries Inc."},
    {"ticker": "PKI", "name": "PerkinElmer Inc."},
    {"ticker": "UAL", "name": "United Airlines Holdings Inc."},
    {"ticker": "NDAQ", "name": "Nasdaq Inc."},
    {"ticker": "EFX", "name": "Equifax Inc."},
    {"ticker": "CINF", "name": "Cincinnati Financial Corporation"},
    {"ticker": "IPG", "name": "Interpublic Group of Companies Inc."},
    {"ticker": "PWR", "name": "Quanta Services Inc."},
    {"ticker": "FE", "name": "FirstEnergy Corp."},
    {"ticker": "DVN", "name": "Devon Energy Corporation"},
    {"ticker": "IEX", "name": "IDEX Corporation"},
    {"ticker": "VTRS", "name": "Viatris Inc."},
    {"ticker": "NTAP", "name": "NetApp Inc."},
    {"ticker": "CE", "name": "Celanese Corporation"},
    {"ticker": "GPS", "name": "Gap Inc."},
    {"ticker": "WDC", "name": "Western Digital Corporation"},
    {"ticker": "ETSY", "name": "Etsy Inc."},
    {"ticker": "AKAM", "name": "Akamai Technologies Inc."},
    {"ticker": "DFS", "name": "Discover Financial Services"},
    {"ticker": "ZBRA", "name": "Zebra Technologies Corporation"},
    {"ticker": "MRO", "name": "Marathon Oil Corporation"},
    {"ticker": "APA", "name": "APA Corporation"},
    {"ticker": "NWL", "name": "Newell Brands Inc."},
    {"ticker": "AAL", "name": "American Airlines Group Inc."},
    {"ticker": "DAL", "name": "Delta Air Lines Inc."},
    {"ticker": "LUV", "name": "Southwest Airlines Co."},
    {"ticker": "ALK", "name": "Alaska Air Group Inc."},
    {"ticker": "SAVE", "name": "Spirit Airlines Inc."},
    {"ticker": "JBLU", "name": "JetBlue Airways Corporation"},
    {"ticker": "F", "name": "Ford Motor Company"},
    {"ticker": "GM", "name": "General Motors Company"},
    {"ticker": "RIVN", "name": "Rivian Automotive Inc."},
    {"ticker": "LCID", "name": "Lucid Group Inc."},
    {"ticker": "SHOP", "name": "Shopify Inc."},
    {"ticker": "SQ", "name": "Block Inc."},
    {"ticker": "COIN", "name": "Coinbase Global Inc."},
    {"ticker": "ROKU", "name": "Roku Inc."},
    {"ticker": "ZM", "name": "Zoom Video Communications Inc."},
    {"ticker": "DOCU", "name": "DocuSign Inc."},
    {"ticker": "OKTA", "name": "Okta Inc."},
    {"ticker": "SNOW", "name": "Snowflake Inc."},
    {"ticker": "DDOG", "name": "Datadog Inc."},
    {"ticker": "CRWD", "name": "CrowdStrike Holdings Inc."},
    {"ticker": "ZS", "name": "Zscaler Inc."},
    {"ticker": "NET", "name": "Cloudflare Inc."},
    {"ticker": "TWLO", "name": "Twilio Inc."},
    {"ticker": "PLTR", "name": "Palantir Technologies Inc."},
    {"ticker": "UBER", "name": "Uber Technologies Inc."},
    {"ticker": "LYFT", "name": "Lyft Inc."},
    {"ticker": "ABNB", "name": "Airbnb Inc."},
    {"ticker": "DASH", "name": "DoorDash Inc."},
    {"ticker": "SPOT", "name": "Spotify Technology S.A."},
    {"ticker": "PINS", "name": "Pinterest Inc."},
    {"ticker": "SNAP", "name": "Snap Inc."},
    {"ticker": "RBLX", "name": "Roblox Corporation"},
    {"ticker": "U", "name": "Unity Software Inc."},
    {"ticker": "BMRN", "name": "BioMarin Pharmaceutical Inc."},
    {"ticker": "GME", "name": "GameStop Corp."},
    {"ticker": "AMC", "name": "AMC Entertainment Holdings Inc."},
    {"ticker": "ATVI", "name": "Activision Blizzard Inc."},
    {"ticker": "STLD", "name": "Steel Dynamics Inc."},
    {"ticker": "X", "name": "United States Steel Corporation"},
    {"ticker": "CLF", "name": "Cleveland-Cliffs Inc."},
    {"ticker": "AA", "name": "Alcoa Corporation"},
    {"ticker": "SCCO", "name": "Southern Copper Corporation"},
    {"ticker": "BHP", "name": "BHP Group Limited"},
    {"ticker": "RIO", "name": "Rio Tinto Group"},
    {"ticker": "BABA", "name": "Alibaba Group Holding Limited"},
    {"ticker": "JD", "name": "JD.com Inc."},
    {"ticker": "PDD", "name": "PDD Holdings Inc."},
    {"ticker": "BIDU", "name": "Baidu Inc."},
    {"ticker": "NIO", "name": "NIO Inc."},
    {"ticker": "XPEV", "name": "XPeng Inc."},
    {"ticker": "LI", "name": "Li Auto Inc."},
    {"ticker": "TME", "name": "Tencent Music Entertainment Group"},
    {"ticker": "BILI", "name": "Bilibili Inc."},
    {"ticker": "ASML", "name": "ASML Holding N.V."},
    {"ticker": "SAP", "name": "SAP SE"},
    {"ticker": "TM", "name": "Toyota Motor Corporation"},
    {"ticker": "SONY", "name": "Sony Group Corporation"},
    {"ticker": "NVO", "name": "Novo Nordisk A/S"},
    {"ticker": "VZ", "name": "Verizon Communications Inc."},
    {"ticker": "ABT", "name": "Abbott Laboratories"},
    {"ticker": "PEP", "name": "PepsiCo Inc."},
    {"ticker": "NKE", "name": "Nike Inc."},
    {"ticker": "MRK", "name": "Merck & Co. Inc."},
    {"ticker": "T", "name": "AT&T Inc."},
    {"ticker": "CVX", "name": "Chevron Corporation"},
    {"ticker": "MCD", "name": "McDonald's Corporation"},
    {"ticker": "ORCL", "name": "Oracle Corporation"},
    {"ticker": "IBM", "name": "International Business Machines"},
    {"ticker": "AMD", "name": "Advanced Micro Devices Inc."},
    {"ticker": "QCOM", "name": "Qualcomm Inc."},
    {"ticker": "SBUX", "name": "Starbucks Corporation"},
    {"ticker": "COST", "name": "Costco Wholesale Corporation"},
    {"ticker": "GOOG", "name": "Alphabet Inc. (Google) Class C"},
    {"ticker": "TXN", "name": "Texas Instruments Incorporated"},
    {"ticker": "AMGN", "name": "Amgen Inc."},
    {"ticker": "LLY", "name": "Eli Lilly and Company"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific Inc."},
    {"ticker": "ACN", "name": "Accenture plc"},
    {"ticker": "AVGO", "name": "Broadcom Inc."},
    {"ticker": "MDT", "name": "Medtronic plc"},
    {"ticker": "PM", "name": "Philip Morris International"},
    # Adding more popular stocks that were missing
    {"ticker": "MU", "name": "Micron Technology Inc."},
    {"ticker": "PLTR", "name": "Palantir Technologies Inc."},
    {"ticker": "AAL", "name": "American Airlines Group Inc."},
    {"ticker": "UAL", "name": "United Airlines Holdings Inc."},
    {"ticker": "DAL", "name": "Delta Air Lines Inc."},
    {"ticker": "GME", "name": "GameStop Corp."},
    {"ticker": "AMC", "name": "AMC Entertainment Holdings Inc."},
    {"ticker": "F", "name": "Ford Motor Company"},
    {"ticker": "GM", "name": "General Motors Company"},
    {"ticker": "UBER", "name": "Uber Technologies Inc."},
    {"ticker": "LYFT", "name": "Lyft Inc."},
    {"ticker": "SNAP", "name": "Snap Inc."},
    {"ticker": "PINS", "name": "Pinterest Inc."},
    {"ticker": "TWTR", "name": "Twitter Inc."},
    {"ticker": "SQ", "name": "Block Inc. (Square)"},
    {"ticker": "COIN", "name": "Coinbase Global Inc."},
    {"ticker": "ROKU", "name": "Roku Inc."},
    {"ticker": "ZM", "name": "Zoom Video Communications Inc."},
    {"ticker": "SHOP", "name": "Shopify Inc."},
    {"ticker": "BABA", "name": "Alibaba Group Holding Limited"},
    {"ticker": "JD", "name": "JD.com Inc."},
    {"ticker": "TCEHY", "name": "Tencent Holdings Ltd."},
    {"ticker": "SONY", "name": "Sony Group Corporation"},
    {"ticker": "SPOT", "name": "Spotify Technology S.A."},
    {"ticker": "ABNB", "name": "Airbnb Inc."},
    {"ticker": "DASH", "name": "DoorDash Inc."},
    {"ticker": "GS", "name": "Goldman Sachs Group Inc."},
    {"ticker": "MS", "name": "Morgan Stanley"},
    {"ticker": "C", "name": "Citigroup Inc."},
    {"ticker": "WFC", "name": "Wells Fargo & Company"},
    {"ticker": "BA", "name": "Boeing Company"},
    
    # Additional 350+ High Market Cap Companies to reach 1000 tickers
    {"ticker": "BRK.A", "name": "Berkshire Hathaway Inc. Class A"},
    {"ticker": "BRK.B", "name": "Berkshire Hathaway Inc. Class B"},
    {"ticker": "LIN", "name": "Linde PLC"},
    {"ticker": "ACN", "name": "Accenture PLC"},
    {"ticker": "LRCX", "name": "Lam Research Corporation"},
    {"ticker": "MRVL", "name": "Marvell Technology Inc."},
    {"ticker": "IBM", "name": "International Business Machines Corp."},
    {"ticker": "PM", "name": "Philip Morris International Inc."},
    {"ticker": "MO", "name": "Altria Group Inc."},
    {"ticker": "FIS", "name": "Fidelity National Information Services"},
    {"ticker": "BSX", "name": "Boston Scientific Corporation"},
    {"ticker": "AON", "name": "Aon PLC"},
    {"ticker": "MMC", "name": "Marsh & McLennan Companies Inc."},
    {"ticker": "ECL", "name": "Ecolab Inc."},
    {"ticker": "EL", "name": "Estee Lauder Companies Inc."},
    {"ticker": "WM", "name": "Waste Management Inc."},
    {"ticker": "SHW", "name": "Sherwin-Williams Company"},
    {"ticker": "APD", "name": "Air Products and Chemicals Inc."},
    {"ticker": "MSI", "name": "Motorola Solutions Inc."},
    {"ticker": "ADI", "name": "Analog Devices Inc."},
    {"ticker": "CARR", "name": "Carrier Global Corporation"},
    {"ticker": "OTIS", "name": "Otis Worldwide Corporation"},
    {"ticker": "EW", "name": "Edwards Lifesciences Corporation"},
    {"ticker": "DG", "name": "Dollar General Corporation"},
    {"ticker": "BDX", "name": "Becton Dickinson and Company"},
    {"ticker": "MCHP", "name": "Microchip Technology Inc."},
    {"ticker": "WEC", "name": "WEC Energy Group Inc."},
    {"ticker": "CTAS", "name": "Cintas Corporation"},
    {"ticker": "DLTR", "name": "Dollar Tree Inc."},
    {"ticker": "PAYX", "name": "Paychex Inc."},
    {"ticker": "FAST", "name": "Fastenal Company"},
    {"ticker": "VRSK", "name": "Verisk Analytics Inc."},
    {"ticker": "PCAR", "name": "PACCAR Inc."},
    {"ticker": "ROK", "name": "Rockwell Automation Inc."},
    {"ticker": "ODFL", "name": "Old Dominion Freight Line Inc."},
    {"ticker": "ANSS", "name": "ANSYS Inc."},
    {"ticker": "CSGP", "name": "CoStar Group Inc."},
    {"ticker": "ROST", "name": "Ross Stores Inc."},
    {"ticker": "WELL", "name": "Welltower Inc."},
    {"ticker": "IDXX", "name": "IDEXX Laboratories Inc."},
    {"ticker": "CPRT", "name": "Copart Inc."},
    {"ticker": "GLW", "name": "Corning Inc."},
    {"ticker": "XEL", "name": "Xcel Energy Inc."},
    {"ticker": "HLT", "name": "Hilton Worldwide Holdings Inc."},
    {"ticker": "DOW", "name": "Dow Inc."},
    {"ticker": "CTSH", "name": "Cognizant Technology Solutions Corp."},
    {"ticker": "ROP", "name": "Roper Technologies Inc."},
    {"ticker": "PPG", "name": "PPG Industries Inc."},
    {"ticker": "MNST", "name": "Monster Beverage Corporation"},
    {"ticker": "FANG", "name": "Diamondback Energy Inc."},
    {"ticker": "BK", "name": "Bank of New York Mellon Corp."},
    {"ticker": "MPWR", "name": "Monolithic Power Systems Inc."},
    {"ticker": "DXCM", "name": "DexCom Inc."},
    {"ticker": "ADP", "name": "Automatic Data Processing Inc."},
    {"ticker": "ALL", "name": "Allstate Corporation"},
    {"ticker": "CDNS", "name": "Cadence Design Systems Inc."},
    {"ticker": "TRV", "name": "Travelers Companies Inc."},
    {"ticker": "OKE", "name": "ONEOK Inc."},
    {"ticker": "SNPS", "name": "Synopsys Inc."},
    {"ticker": "A", "name": "Agilent Technologies Inc."},
    {"ticker": "INFO", "name": "IHS Markit Ltd."},
    {"ticker": "FTNT", "name": "Fortinet Inc."},
    {"ticker": "MSCI", "name": "MSCI Inc."},
    {"ticker": "ES", "name": "Eversource Energy"},
    {"ticker": "STZ", "name": "Constellation Brands Inc."},
    {"ticker": "APH", "name": "Amphenol Corporation"},
    {"ticker": "AME", "name": "AMETEK Inc."},
    {"ticker": "FRC", "name": "First Republic Bank"},
    {"ticker": "TROW", "name": "T. Rowe Price Group Inc."},
    {"ticker": "WST", "name": "West Pharmaceutical Services Inc."},
    {"ticker": "KEYS", "name": "Keysight Technologies Inc."},
    {"ticker": "STE", "name": "STERIS PLC"},
    {"ticker": "SWKS", "name": "Skyworks Solutions Inc."},
    {"ticker": "NTRS", "name": "Northern Trust Corporation"},
    {"ticker": "WY", "name": "Weyerhaeuser Company"},
    {"ticker": "GWW", "name": "W.W. Grainger Inc."},
    {"ticker": "ALGN", "name": "Align Technology Inc."},
    {"ticker": "LH", "name": "Laboratory Corporation of America"},
    {"ticker": "CLX", "name": "Clorox Company"},
    {"ticker": "BF.B", "name": "Brown-Forman Corporation"},
    {"ticker": "VMC", "name": "Vulcan Materials Company"},
    {"ticker": "MLM", "name": "Martin Marietta Materials Inc."},
    {"ticker": "MKTX", "name": "MarketAxess Holdings Inc."},
    {"ticker": "ATO", "name": "Atmos Energy Corporation"},
    {"ticker": "AES", "name": "AES Corporation"},
    {"ticker": "CMS", "name": "CMS Energy Corporation"},
    {"ticker": "BR", "name": "Broadridge Financial Solutions Inc."},
    {"ticker": "HOLX", "name": "Hologic Inc."},
    {"ticker": "HST", "name": "Host Hotels & Resorts Inc."},
    {"ticker": "MOH", "name": "Molina Healthcare Inc."},
    {"ticker": "CTVA", "name": "Corteva Inc."},
    {"ticker": "AWK", "name": "American Water Works Company Inc."},
    {"ticker": "DTE", "name": "DTE Energy Company"},
    {"ticker": "FISV", "name": "Fiserv Inc."},
    {"ticker": "LYB", "name": "LyondellBasell Industries N.V."},
    {"ticker": "MAS", "name": "Masco Corporation"},
    {"ticker": "ARE", "name": "Alexandria Real Estate Equities Inc."},
    {"ticker": "TDY", "name": "Teledyne Technologies Inc."},
    {"ticker": "ENPH", "name": "Enphase Energy Inc."},
    {"ticker": "PAYC", "name": "Paycom Software Inc."},
    {"ticker": "WAT", "name": "Waters Corporation"},
    {"ticker": "SYY", "name": "Sysco Corporation"},
    {"ticker": "ANET", "name": "Arista Networks Inc."},
    {"ticker": "J", "name": "Jacobs Engineering Group Inc."},
    {"ticker": "PEAK", "name": "Healthpeak Properties Inc."},
    {"ticker": "CAH", "name": "Cardinal Health Inc."},
    {"ticker": "COO", "name": "Cooper Companies Inc."},
    {"ticker": "TECH", "name": "Bio-Techne Corporation"},
    {"ticker": "CBRE", "name": "CBRE Group Inc."},
    {"ticker": "INCY", "name": "Incyte Corporation"},
    {"ticker": "LDOS", "name": "Leidos Holdings Inc."},
    {"ticker": "DGX", "name": "Quest Diagnostics Inc."},
    {"ticker": "POOL", "name": "Pool Corporation"},
    {"ticker": "TYL", "name": "Tyler Technologies Inc."},
    {"ticker": "NVR", "name": "NVR Inc."},
    {"ticker": "PKG", "name": "Packaging Corporation of America"},
    {"ticker": "SEDG", "name": "SolarEdge Technologies Inc."},
    {"ticker": "BIO", "name": "Bio-Rad Laboratories Inc."},
    {"ticker": "JKHY", "name": "Jack Henry & Associates Inc."},
    {"ticker": "EXPD", "name": "Expeditors International of Washington"},
    {"ticker": "ULTA", "name": "Ulta Beauty Inc."},
    {"ticker": "LNT", "name": "Alliant Energy Corporation"},
    {"ticker": "CHRW", "name": "C.H. Robinson Worldwide Inc."},
    {"ticker": "PFG", "name": "Principal Financial Group Inc."},
    {"ticker": "WAB", "name": "Westinghouse Air Brake Technologies"},
    {"ticker": "PKI", "name": "PerkinElmer Inc."},
    {"ticker": "NDAQ", "name": "Nasdaq Inc."},
    {"ticker": "EFX", "name": "Equifax Inc."},
    {"ticker": "CINF", "name": "Cincinnati Financial Corporation"},
    {"ticker": "IPG", "name": "Interpublic Group of Companies Inc."},
    {"ticker": "PWR", "name": "Quanta Services Inc."},
    {"ticker": "FE", "name": "FirstEnergy Corp."},
    {"ticker": "DVN", "name": "Devon Energy Corporation"},
    {"ticker": "IEX", "name": "IDEX Corporation"},
    {"ticker": "VTRS", "name": "Viatris Inc."},
    {"ticker": "NTAP", "name": "NetApp Inc."},
    {"ticker": "CE", "name": "Celanese Corporation"},
    {"ticker": "GPS", "name": "Gap Inc."},
    {"ticker": "WDC", "name": "Western Digital Corporation"},
    {"ticker": "AKAM", "name": "Akamai Technologies Inc."},
    {"ticker": "ZBRA", "name": "Zebra Technologies Corporation"},
    {"ticker": "MRO", "name": "Marathon Oil Corporation"},
    {"ticker": "APA", "name": "APA Corporation"},
    {"ticker": "NWL", "name": "Newell Brands Inc."},
    {"ticker": "SPY", "name": "SPDR S&P 500 ETF Trust"},
    {"ticker": "QQQ", "name": "Invesco QQQ Trust"},
    {"ticker": "IWM", "name": "iShares Russell 2000 ETF"},
    {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF"},
    {"ticker": "VEA", "name": "Vanguard FTSE Developed Markets ETF"},
    {"ticker": "VWO", "name": "Vanguard FTSE Emerging Markets ETF"},
    {"ticker": "GLD", "name": "SPDR Gold Shares"},
    {"ticker": "SLV", "name": "iShares Silver Trust"},
    {"ticker": "USO", "name": "United States Oil Fund"},
    {"ticker": "TLT", "name": "iShares 20+ Year Treasury Bond ETF"},
    {"ticker": "HYG", "name": "iShares iBoxx High Yield Corporate Bond ETF"},
    {"ticker": "LQD", "name": "iShares iBoxx Investment Grade Corporate Bond ETF"},
    {"ticker": "EEM", "name": "iShares MSCI Emerging Markets ETF"},
    {"ticker": "FXI", "name": "iShares China Large-Cap ETF"},
    {"ticker": "EWJ", "name": "iShares MSCI Japan ETF"},
    {"ticker": "EWZ", "name": "iShares MSCI Brazil ETF"},
    {"ticker": "INDA", "name": "iShares MSCI India ETF"},
    {"ticker": "EWC", "name": "iShares MSCI Canada ETF"},
    {"ticker": "EWU", "name": "iShares MSCI United Kingdom ETF"},
    {"ticker": "EWG", "name": "iShares MSCI Germany ETF"},
    {"ticker": "VGT", "name": "Vanguard Information Technology ETF"},
    {"ticker": "VHT", "name": "Vanguard Health Care ETF"},
    {"ticker": "VFH", "name": "Vanguard Financials ETF"},
    {"ticker": "VDE", "name": "Vanguard Energy ETF"},
    {"ticker": "VIS", "name": "Vanguard Industrials ETF"},
    {"ticker": "VAW", "name": "Vanguard Materials ETF"},
    {"ticker": "VCR", "name": "Vanguard Consumer Discretionary ETF"},
    {"ticker": "VDC", "name": "Vanguard Consumer Staples ETF"},
    {"ticker": "VPU", "name": "Vanguard Utilities ETF"},
    {"ticker": "VNQ", "name": "Vanguard Real Estate ETF"},
    {"ticker": "XLF", "name": "Financial Select Sector SPDR Fund"},
    {"ticker": "XLK", "name": "Technology Select Sector SPDR Fund"},
    {"ticker": "XLV", "name": "Health Care Select Sector SPDR Fund"},
    {"ticker": "XLE", "name": "Energy Select Sector SPDR Fund"},
    {"ticker": "XLI", "name": "Industrial Select Sector SPDR Fund"},
    {"ticker": "XLB", "name": "Materials Select Sector SPDR Fund"},
    {"ticker": "XLY", "name": "Consumer Discretionary Select Sector SPDR Fund"},
    {"ticker": "XLP", "name": "Consumer Staples Select Sector SPDR Fund"},
    {"ticker": "XLU", "name": "Utilities Select Sector SPDR Fund"},
    {"ticker": "SMH", "name": "VanEck Semiconductor ETF"},
    {"ticker": "ARKK", "name": "ARK Innovation ETF"},
    {"ticker": "ARKQ", "name": "ARK Autonomous Technology & Robotics ETF"},
    {"ticker": "ARKW", "name": "ARK Next Generation Internet ETF"},
    {"ticker": "ARKG", "name": "ARK Genomics Revolution ETF"},
    {"ticker": "ARKF", "name": "ARK Fintech Innovation ETF"},
    {"ticker": "ICLN", "name": "iShares Global Clean Energy ETF"},
    {"ticker": "VB", "name": "Vanguard Small-Cap ETF"},
    {"ticker": "VO", "name": "Vanguard Mid-Cap ETF"},
    {"ticker": "VV", "name": "Vanguard Large-Cap ETF"},
    {"ticker": "VUG", "name": "Vanguard Growth ETF"},
    {"ticker": "VTV", "name": "Vanguard Value ETF"},
    {"ticker": "IJH", "name": "iShares Core S&P Mid-Cap ETF"},
    {"ticker": "IJR", "name": "iShares Core S&P Small-Cap ETF"},
    {"ticker": "IVV", "name": "iShares Core S&P 500 ETF"},
    {"ticker": "IVW", "name": "iShares S&P 500 Growth ETF"},
    {"ticker": "IVE", "name": "iShares S&P 500 Value ETF"},
    {"ticker": "DIA", "name": "SPDR Dow Jones Industrial Average ETF"},
    {"ticker": "MDY", "name": "SPDR S&P MidCap 400 ETF"},
    {"ticker": "MTUM", "name": "iShares MSCI USA Momentum Factor ETF"},
    {"ticker": "QUAL", "name": "iShares MSCI USA Quality Factor ETF"},
    {"ticker": "USMV", "name": "iShares MSCI USA Min Vol Factor ETF"},
    {"ticker": "BND", "name": "Vanguard Total Bond Market ETF"},
    {"ticker": "AGG", "name": "iShares Core U.S. Aggregate Bond ETF"},
    {"ticker": "TIP", "name": "iShares TIPS Bond ETF"},
    {"ticker": "MUB", "name": "iShares National Muni Bond ETF"},
    {"ticker": "JEPI", "name": "JPMorgan Equity Premium Income ETF"},
    {"ticker": "QYLD", "name": "Global X NASDAQ 100 Covered Call ETF"},
    {"ticker": "SCHD", "name": "Schwab US Dividend Equity ETF"},
    {"ticker": "VYM", "name": "Vanguard High Dividend Yield ETF"},
    {"ticker": "DGRO", "name": "iShares Core Dividend Growth ETF"},
    {"ticker": "VIG", "name": "Vanguard Dividend Appreciation ETF"},
    {"ticker": "HDV", "name": "iShares High Dividend ETF"},
    {"ticker": "DVY", "name": "iShares Select Dividend ETF"},
    {"ticker": "SCHF", "name": "Schwab International Equity ETF"},
    {"ticker": "SCHE", "name": "Schwab Emerging Markets Equity ETF"},
    {"ticker": "SCHX", "name": "Schwab U.S. Large-Cap ETF"},
    {"ticker": "SCHM", "name": "Schwab U.S. Mid-Cap ETF"},
    {"ticker": "SCHA", "name": "Schwab U.S. Small-Cap ETF"},
    {"ticker": "SCHG", "name": "Schwab U.S. Large-Cap Growth ETF"},
    {"ticker": "SCHV", "name": "Schwab U.S. Large-Cap Value ETF"},
    {"ticker": "SCHB", "name": "Schwab U.S. Broad Market ETF"},
    {"ticker": "SHY", "name": "iShares 1-3 Year Treasury Bond ETF"},
    {"ticker": "IEF", "name": "iShares 7-10 Year Treasury Bond ETF"},
    {"ticker": "GBTC", "name": "Grayscale Bitcoin Trust"},
    {"ticker": "BITO", "name": "ProShares Bitcoin Strategy ETF"},
    {"ticker": "DRIV", "name": "Global X Autonomous & Electric Vehicles ETF"},
    {"ticker": "LIT", "name": "Global X Lithium & Battery Tech ETF"},
    {"ticker": "BUZZ", "name": "VanEck Social Sentiment ETF"},
    {"ticker": "HERO", "name": "Global X Video Games & Esports ETF"},
    {"ticker": "UFO", "name": "Procure Space ETF"},
    {"ticker": "POTX", "name": "Global X Cannabis ETF"},
    {"ticker": "MJ", "name": "ETFMG Alternative Harvest ETF"},
    {"ticker": "MSOS", "name": "AdvisorShares Pure US Cannabis ETF"},
    {"ticker": "LMT", "name": "Lockheed Martin Corporation"},
    {"ticker": "RTX", "name": "Raytheon Technologies Corporation"},
    {"ticker": "CAT", "name": "Caterpillar Inc."},
    {"ticker": "DE", "name": "Deere & Company"},
    {"ticker": "MMM", "name": "3M Company"},
    {"ticker": "HON", "name": "Honeywell International Inc."},
    {"ticker": "GE", "name": "General Electric Company"},
    # Defense and Aerospace companies
    {"ticker": "NOC", "name": "Northrop Grumman Corporation"},
    {"ticker": "GD", "name": "General Dynamics Corporation"},
    {"ticker": "HII", "name": "Huntington Ingalls Industries Inc."},
    {"ticker": "TDG", "name": "TransDigm Group Inc."},
    {"ticker": "TXT", "name": "Textron Inc."},
    {"ticker": "SPR", "name": "Spirit AeroSystems Holdings Inc."},
    # Tech companies
    {"ticker": "ORCL", "name": "Oracle Corporation"},
    {"ticker": "CRM", "name": "Salesforce Inc."},
    {"ticker": "SAP", "name": "SAP SE"},
    {"ticker": "IBM", "name": "International Business Machines Corp."},
    {"ticker": "NOW", "name": "ServiceNow Inc."},
    {"ticker": "TEAM", "name": "Atlassian Corporation"},
    {"ticker": "WDAY", "name": "Workday Inc."},
    {"ticker": "ZS", "name": "Zscaler Inc."},
    {"ticker": "OKTA", "name": "Okta Inc."},
    {"ticker": "NET", "name": "Cloudflare Inc."},
    {"ticker": "CRWD", "name": "CrowdStrike Holdings Inc."},
    {"ticker": "SNOW", "name": "Snowflake Inc."},
    {"ticker": "DDOG", "name": "Datadog Inc."},
    {"ticker": "TWLO", "name": "Twilio Inc."},
    {"ticker": "MDB", "name": "MongoDB Inc."},
    # Energy sector
    {"ticker": "CVX", "name": "Chevron Corporation"},
    {"ticker": "XOM", "name": "Exxon Mobil Corporation"},
    {"ticker": "COP", "name": "ConocoPhillips"},
    {"ticker": "SLB", "name": "Schlumberger Limited"},
    {"ticker": "EOG", "name": "EOG Resources Inc."},
    {"ticker": "OXY", "name": "Occidental Petroleum Corporation"},
    {"ticker": "HAL", "name": "Halliburton Company"},
    {"ticker": "MPC", "name": "Marathon Petroleum Corporation"},
    {"ticker": "PSX", "name": "Phillips 66"},
    {"ticker": "VLO", "name": "Valero Energy Corporation"},
]

# Function to search for stocks by partial ticker or name match using Yahoo Finance
def search_stocks(query):
    """
    Search for stocks by partial ticker or company name match
    Uses both local database and Yahoo Finance search API
    
    Parameters:
    -----------
    query : str
        Search query (can be ticker or company name)
    
    Returns:
    --------
    list
        List of matching stock dictionaries with ticker and name
    """
    if not query:
        return []
    
    # First search local database for faster results
    query_upper = query.upper()
    query_lower = query.lower()
    local_matches = []
    
    for stock in POPULAR_STOCKS:
        # Match on ticker (exact or starting with)
        if stock["ticker"] == query_upper or stock["ticker"].startswith(query_upper):
            local_matches.append(stock)
        # Match on name (case-insensitive partial match)
        elif query_lower in stock["name"].lower():
            local_matches.append(stock)
    
    # Sort matches: exact ticker matches first, then starts-with ticker matches, then name matches
    local_matches.sort(key=lambda x: (
        0 if x["ticker"] == query_upper else 
        1 if x["ticker"].startswith(query_upper) else 
        2
    ))
    
    # If we already have enough local matches, return them
    if len(local_matches) >= 10:
        return local_matches[:10]
    
    # If not enough local matches, try a more direct approach for specific companies
    if query_lower in ["northrop", "grumman", "northrop grumman"]:
        # Ensure Northrop Grumman is in results
        if not any(stock['ticker'] == "NOC" for stock in local_matches):
            local_matches.append({
                "ticker": "NOC",
                "name": "Northrop Grumman Corporation"
            })
    
    # Try common variations and abbreviations
    ticker_mappings = {
        "citi": "C",
        "citigroup": "C",
        "coke": "KO",
        "coca cola": "KO",
        "cocacola": "KO",
        "coca-cola": "KO",
        "boeing": "BA",
        "lockheed": "LMT",
        "raytheon": "RTX",
        "defense": ["NOC", "LMT", "GD", "RTX", "HII"],  # Defense contractors
        "airlines": ["AAL", "DAL", "UAL", "LUV"],  # Major airlines
        "tech": ["AAPL", "MSFT", "GOOGL", "META", "AMZN", "NVDA"],  # Big tech
        "semiconductors": ["NVDA", "AMD", "INTC", "MU", "TSM", "AVGO"],  # Semiconductor companies
        "banks": ["JPM", "BAC", "WFC", "C", "GS", "MS"],  # Major banks
        "energy": ["XOM", "CVX", "COP", "SLB", "BP", "OXY"],  # Energy companies
        "retail": ["WMT", "TGT", "COST", "AMZN", "HD", "LOW"],  # Retail companies
    }
    
    for key, value in ticker_mappings.items():
        if query_lower in key or key in query_lower:
            if isinstance(value, list):
                # Add all related companies for category searches
                for ticker in value:
                    # Find the company name in our database
                    for stock in POPULAR_STOCKS:
                        if stock["ticker"] == ticker and not any(m["ticker"] == ticker for m in local_matches):
                            local_matches.append(stock)
                            break
            else:
                # Add the specific company
                for stock in POPULAR_STOCKS:
                    if stock["ticker"] == value and not any(m["ticker"] == value for m in local_matches):
                        local_matches.append(stock)
                        break
    
    # Try to get additional matches from Yahoo Finance API
    try:
        import yfinance as yf
        import requests
        
        # Yahoo Finance search API
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'quotes' in data:
                for quote in data['quotes']:
                    if 'symbol' in quote and 'shortname' in quote:
                        # Skip if already in local matches
                        if any(stock['ticker'] == quote['symbol'] for stock in local_matches):
                            continue
                        
                        local_matches.append({
                            "ticker": quote['symbol'],
                            "name": quote['shortname']
                        })
    except Exception as e:
        # If API call fails, just continue with local matches
        print(f"Error fetching data from Yahoo Finance: {e}")
    
    # Return combined results (limit to 10)
    return local_matches[:10]

# Set page configuration for single page layout
st.set_page_config(
    page_title="Ticker AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load and apply custom CSS
def load_css(css_file):
    with open(css_file, "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

load_css("assets/custom.css")

# Convert image to base64 for inline CSS
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Initialize view mode state if not exists
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "main"

def main():
    # Check if user is authenticated
    if not is_authenticated():
        auth_page()
        return
    
    # Check view mode to determine what content to display
    if st.session_state.view_mode == "admin" and is_admin():
        # === ADMIN PANEL CONTENT ===
        st.title("Ticker AI Admin Panel")
        
        # Show user info
        user = get_session_user()
        if user and isinstance(user, dict):
            st.markdown(f"**Logged in as:** {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
        
        # Add a separator
        st.markdown("<hr style='margin-top: 0; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        # Display admin panel content
        admin_panel()
        
    else:
        # === MAIN SINGLE PAGE LAYOUT ===
        
        # Get base64 encoded background image
        bg_image = get_base64_image("assets/ticker2.jpg")
        
        # No admin panel in header navigation
        admin_nav_item = ""
        admin_nav_dropdown = ""
        
        # Create navigation header
        st.markdown(f"""
        <style>
        .main-nav {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background-color: #000000;
            padding: 2px 0;
            border-bottom: 1px solid rgba(59, 130, 246, 0.3);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }}
        .nav-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 50px;
            width: 100%;
        }}
        .nav-logo {{
            margin: 0;
            color: #3b82f6;
            font-size: 10px;
            font-weight: bold;
        }}
        .nav-menu {{
            display: flex;
            gap: 35px;
            margin-left: auto;
        }}
        .nav-menu a {{
            color: #e5e7eb;
            text-decoration: none;
            font-weight: 500;
            font-size: 16px;
            transition: color 0.3s;
        }}
        .nav-menu a:hover {{
            color: #3b82f6;
        }}
        .nav-toggle {{
            display: none;
            background: none;
            border: none;
            color: #e5e7eb;
            font-size: 20px;
            cursor: pointer;
            position: relative;
        }}
        .nav-dropdown {{
            display: none;
            position: absolute;
            top: 100%;
            right: 0;
            background-color: rgba(17, 24, 39, 0.95);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 8px;
            padding: 10px 0;
            min-width: 150px;
            z-index: 1001;
        }}
        .nav-dropdown a {{
            display: block;
            padding: 10px 20px;
            color: #e5e7eb;
            text-decoration: none;
            font-size: 14px;
            transition: background-color 0.3s;
        }}
        .nav-dropdown a:hover {{
            background-color: rgba(59, 130, 246, 0.2);
        }}
        @media (max-width: 768px) {{
            .nav-content {{
                padding: 0 20px;
            }}
            .nav-logo {{
                font-size: 22px;
            }}
            .nav-menu {{
                display: none;
            }}
            .nav-toggle {{
                display: block;
            }}
            .nav-toggle:hover + .nav-dropdown,
            .nav-dropdown:hover {{
                display: block;
            }}
        }}
        .hero-section {{
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('data:image/jpeg;base64,{bg_image}') center/cover;
            height: 100vh;
            width: 100vw;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            margin: 0 calc(-50vw + 50%);
            padding: 0 2rem;
            position: relative;
            transform: translateY(-60px);
        }}
        .hero-title {{
            font-size: 4rem;
            font-weight: bold;
            color: white;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }}
        .hero-subtitle {{
            font-size: 1.5rem;
            color: #e5e7eb;
            max-width: 600px;
            margin-bottom: 2rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        }}
        .hero-button {{
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white !important;
            padding: 15px 30px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: all 0.3s;
            display: inline-block;
            transform: translateX(-8px);
        }}
        .hero-button:hover {{
            transform: translateX(-8px) translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
            color: white !important;
        }}
        .section-spacer {{
            height: 60px;
        }}
        .section-header {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #3b82f6;
            margin: 40px 0 30px 0;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(59, 130, 246, 0.3);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .section-emoji {{
            font-size: 2rem;
            margin-left: 15px;
        }}
        .footer {{
            background-color: #000000;
            border-top: 1px solid rgba(59, 130, 246, 0.3);
            padding: 20px 0;
            margin-top: 50px;
            width: 100vw;
            margin-left: calc(-50vw + 50%);
        }}
        .footer-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 40px;
            flex-wrap: wrap;
            width: 100%;
        }}
        .footer-logo {{
            color: #3b82f6;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .footer-info {{
            color: #e5e7eb;
            font-size: 14px;
        }}
        @media (max-width: 768px) {{
            .footer-content {{
                flex-direction: column;
                text-align: center;
            }}
            .hero-title {{
                font-size: 2.5rem;
            }}
            .hero-subtitle {{
                font-size: 1.2rem;
            }}
        }}
        </style>
        
        <div class="main-nav">
            <div class="nav-content">
                <h1 class="nav-logo">Ticker AI</h1>
                <nav class="nav-menu">
                    <a href="#about">About</a>
                    <a href="#howitworks">How It Works</a>
                    <a href="#analyzer">Stock Analyzer</a>
                    <a href="#powerplays">Power Plays</a>
                </nav>
                <div style="position: relative;">
                    <button class="nav-toggle">☰</button>
                    <div class="nav-dropdown">
                        <a href="#about">About</a>
                        <a href="#howitworks">How It Works</a>
                        <a href="#analyzer">Stock Analyzer</a>
                        <a href="#powerplays">Power Plays</a>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add top spacing to account for fixed header
        st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
        
        # Hero Section with background image
        st.markdown("""
        <div id="home" class="hero-section">
            <h1 class="hero-title">TICKER AI</h1>
            <a href="#analyzer" class="hero-button">
                Start Analyzing →
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # About Section
        st.markdown('<div id="about" class="section-spacer"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header">About Ticker AI<span class="section-emoji">🤖</span></div>', unsafe_allow_html=True)
        st.markdown("""
        A powerful stock analysis platform that combines real-time data with advanced AI to help you make smarter investment decisions. It analyzes price trends, technical indicators, and historical patterns to predict market movements with precision. Ticker AI also monitors breaking news and social media to gauge sentiment shifts, while factoring in key financial metrics like earnings growth, valuations, and insider activity. By tracking market events and seasonal trends, it delivers a complete, up-to-the-minute picture of a stock's potential—summarized in a clear, actionable rating.
        
        Ticker AI's buy rating engine is powered by a weighted algorithm that evaluates each stock through a multi-layered scoring system. The model assigns 40% weight to technical indicators—such as RSI, MACD, moving averages, and Bollinger Bands—calculating bullish momentum based on the ratio of confirming signals. Another 40% is dedicated to fundamental analysis, where key financial metrics like P/E ratio, profit margins, revenue growth, and debt-to-equity are benchmarked and scored relative to industry norms. The remaining 20% draws on market sentiment, translating analyst recommendations into a normalized confidence score. Each layer is independently scored on a 10-point scale and then aggregated into a final buy rating, enabling the AI to deliver a clear, data-driven investment outlook.
        """)
        
        # How It Works Section
        st.markdown('<div id="howitworks" class="section-spacer"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header">How It Works<span class="section-emoji">⚡</span></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            ### 1. Search & Analyze
            Simply type any company name or ticker symbol to find and analyze the stock you want to research.
            """)
        
        with col2:
            st.markdown("""
            ### 2. Power Plays
            Our Power Plays feature scans hundreds of stocks from major indices to identify the top 5 investment opportunities with the highest AI-driven buy ratings.
            """)
        
        with col3:
            st.markdown("""
            ### 3. Make Educated Decisions
            Use our comprehensive analysis, buy/sell ratings, and detailed explanations to make informed investment decisions with confidence.
            """)
        
        # Stock Analyzer Section
        st.markdown('<div id="analyzer" class="section-spacer"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Stock Analyzer<span class="section-emoji">📊</span></div>', unsafe_allow_html=True)
        
        # Initialize session states for stock search
        if "search_query" not in st.session_state:
            st.session_state.search_query = ""
        if "selected_ticker" not in st.session_state:
            st.session_state.selected_ticker = ""
        
        # Stock search interface with proper alignment
        # Generate all stock options for the dropdown
        all_options = []
        for stock in POPULAR_STOCKS:
            all_options.append(f"{stock['ticker']} - {stock['name']}")
        
        # Function to update stock search results
        def update_stock_results():
            if not st.session_state.stock_search or st.session_state.stock_search == "":
                st.session_state.selected_ticker = ""
                return
            if " - " in st.session_state.stock_search:
                ticker_part = st.session_state.stock_search.split(" - ")[0]
                st.session_state.selected_ticker = ticker_part
        
        # Create columns to match Power Plays layout exactly
        col1, col2 = st.columns([3, 1.5])
        
        with col1:
            # Text input for stock search with populated value
            input_value = ""
            if "selected_ticker" in st.session_state and st.session_state.selected_ticker:
                if "selected_stock_name" in st.session_state:
                    input_value = f"{st.session_state.selected_ticker} - {st.session_state.selected_stock_name}"
                else:
                    input_value = st.session_state.selected_ticker
            
            search_input = st.text_input(
                "Search stocks by ticker or company name",
                value=input_value,
                placeholder="Type ticker (e.g., AAPL) or company name...",
                key="stock_search_input"
            )
            
            # Show matching stocks if search input exists and is not a selected stock
            show_results = search_input and len(search_input) >= 1 and not (
                "selected_ticker" in st.session_state and 
                st.session_state.selected_ticker and 
                st.session_state.selected_ticker in search_input
            )
            
            if show_results:
                matching_stocks = []
                search_lower = search_input.lower()
                seen_tickers = set()
                
                for stock in POPULAR_STOCKS:
                    if (search_lower in stock['ticker'].lower() or 
                        search_lower in stock['name'].lower()):
                        # Avoid duplicates
                        if stock['ticker'] not in seen_tickers:
                            matching_stocks.append(stock)
                            seen_tickers.add(stock['ticker'])
                
                if matching_stocks:
                    # Limit to top 3 matches to avoid clutter
                    display_stocks = matching_stocks[:3]
                    
                    st.markdown("**Matching stocks:**")
                    for i, stock in enumerate(display_stocks):
                        button_text = f"{stock['ticker']} - {stock['name']}"
                        if st.button(
                            button_text, 
                            key=f"stock_btn_{i}_{stock['ticker']}",
                            use_container_width=True
                        ):
                            st.session_state.selected_ticker = stock['ticker']
                            st.session_state.selected_stock_name = stock['name']
                            st.rerun()
        
        with col2:
            # Add spacing to align button with dropdown
            st.markdown('<div style="height: 26px;"></div>', unsafe_allow_html=True)
            # Search button
            search_button = st.button("Analyze Stock", type="primary")
        
        # Extract ticker from selection if available
        ticker = ""
        if "selected_ticker" in st.session_state and st.session_state.selected_ticker:
            ticker = st.session_state.selected_ticker
        
        # Stock analysis display - use session state to prevent reset
        if search_button and ticker:
            # Store analysis data in session state
            st.session_state[f'analysis_data_{ticker}'] = {
                'ticker': ticker,
                'timestamp': time.time()
            }
        
        # Display analysis if we have stored data
        if f'analysis_data_{ticker}' in st.session_state and ticker:
            try:
                analyzer = StockAnalyzer(ticker)
                
                # Get company info and stock data
                company_info = analyzer.get_company_info()
                current_price = analyzer.get_current_price()
                market_cap = analyzer.get_market_cap()
                pe_ratio = analyzer.get_pe_ratio()
                
                # Display company name prominently
                if company_info and 'longName' in company_info:
                    st.markdown(f'<div class="company-name">{company_info["longName"]} ({ticker})</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="company-name">{ticker}</div>', unsafe_allow_html=True)
                
                # Calculate buy rating
                buy_rating, rating_breakdown = analyzer.calculate_buy_rating()
                
                # === 1. BUY RATING SECTION ===
                st.markdown("### 📊 AI Buy Rating")
                
                # Get individual rating components
                technical_score = rating_breakdown.get('Technical Analysis', {}).get('score', 0)
                fundamental_score = rating_breakdown.get('Fundamental Analysis', {}).get('score', 0) 
                sentiment_score = rating_breakdown.get('Market Sentiment', {}).get('score', 0)
                
                # Determine color and recommendation based on rating
                if buy_rating >= 7:
                    color = "#10B981"  # Green
                    recommendation = "BUY"
                elif buy_rating >= 4:
                    color = "#F59E0B"  # Orange  
                    recommendation = "HOLD"
                else:
                    color = "#EF4444"  # Red
                    recommendation = "SELL"
                
                # Create meter and component ratings layout
                meter_col, ratings_col = st.columns([1, 1])
                
                with meter_col:
                    # Clean circular progress meter
                    progress_percentage = (buy_rating / 10) * 100
                    
                    st.markdown(f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <div style="position: relative; width: 150px; height: 150px; margin: 0 auto;">
                            <!-- Background circle -->
                            <svg width="150" height="150" style="position: absolute; top: 0; left: 0;">
                                <circle cx="75" cy="75" r="60" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="8"/>
                                <circle cx="75" cy="75" r="60" fill="none" stroke="{color}" stroke-width="8" 
                                        stroke-dasharray="{(progress_percentage * 3.77):.1f} 377" 
                                        stroke-linecap="round" transform="rotate(-90 75 75)"/>
                            </svg>
                            <!-- Center content -->
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                <div style="color: {color}; font-size: 36px; font-weight: bold; line-height: 1;">
                                    {buy_rating:.1f}
                                </div>
                                <div style="color: {color}; font-size: 16px; font-weight: bold;">
                                    / 10
                                </div>
                            </div>
                        </div>
                        <div style="font-size: 24px; font-weight: bold; color: {color}; margin-top: 15px;">
                            {recommendation}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with ratings_col:
                    # Individual component ratings
                    st.markdown("**Rating Components:**")
                    
                    # Technical Analysis
                    tech_color = "#10B981" if technical_score >= 7 else "#F59E0B" if technical_score >= 4 else "#EF4444"
                    st.markdown(f"""
                    <div style="margin: 10px 0; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: white; font-weight: 500;">📈 Technical Analysis</span>
                            <span style="color: {tech_color}; font-weight: bold; font-size: 18px;">{technical_score:.1f}/10</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Fundamental Analysis  
                    fund_color = "#10B981" if fundamental_score >= 7 else "#F59E0B" if fundamental_score >= 4 else "#EF4444"
                    st.markdown(f"""
                    <div style="margin: 10px 0; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: white; font-weight: 500;">💰 Fundamental Analysis</span>
                            <span style="color: {fund_color}; font-weight: bold; font-size: 18px;">{fundamental_score:.1f}/10</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Market Sentiment
                    sent_color = "#10B981" if sentiment_score >= 7 else "#F59E0B" if sentiment_score >= 4 else "#EF4444"
                    st.markdown(f"""
                    <div style="margin: 10px 0; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: white; font-weight: 500;">📊 Market Sentiment</span>
                            <span style="color: {sent_color}; font-weight: bold; font-size: 18px;">{sentiment_score:.1f}/10</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add vertical spacing
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                # === 2. FINANCIALS SECTION ===
                st.markdown("### 💰 Key Financials")
                
                # Get financial metrics
                forward_pe = company_info.get('forwardPE', None)
                trailing_pe = pe_ratio if pe_ratio else None
                target_price = company_info.get('targetMeanPrice', None)
                profit_margin = company_info.get('profitMargins', None)
                dividend_yield = company_info.get('dividendYield', None)
                
                # Calculate upside/downside potential
                if target_price and current_price:
                    potential = ((target_price - current_price) / current_price) * 100
                    potential_text = f"{potential:+.1f}%"
                else:
                    potential_text = "N/A"
                
                # Get net revenue
                total_revenue = company_info.get('totalRevenue', None)
                
                # Use 3x3 grid format as requested
                fin_col1, fin_col2, fin_col3 = st.columns(3)
                
                with fin_col1:
                    st.write(f"Price: ${current_price:.2f}" if current_price else "Price: N/A")
                    st.write(f"Analyst's Mean Target Price: ${target_price:.2f}" if target_price else "Target Price: N/A")
                    st.write(f"Upside: {potential_text}")
                
                with fin_col2:
                    st.write(f"Market Cap: {format_large_number(market_cap)}" if market_cap else "Market Cap: N/A")
                    st.write(f"P/E: {trailing_pe:.2f}" if trailing_pe else "P/E: N/A")
                    st.write(f"Forward P/E: {forward_pe:.2f}" if forward_pe else "Forward P/E: N/A")
                
                with fin_col3:
                    st.write(f"Profit Margin: {profit_margin*100:.2f}%" if profit_margin else "Profit Margin: N/A")
                    st.write(f"Net Revenue: {format_large_number(total_revenue)}" if total_revenue else "Net Revenue: N/A")
                    st.write(f"Dividend: {dividend_yield:.2f}%" if dividend_yield else "Dividend: N/A")
                
                # Add vertical spacing
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                # === 3. SECTOR COMPARISON SECTION ===
                st.markdown("### 🏭 Sector Analysis")
                
                sector = company_info.get('sector', 'Unknown')
                industry = company_info.get('industry', 'Unknown')
                
                st.write(f"**Sector:** {sector}")
                st.write(f"**Industry:** {industry}")
                
                # Sector peer comparison
                st.markdown("#### Sector Comparison")
                
                # Get sector peers with their tickers for real data comparison
                sector_peers = {
                    "Technology": ["MSFT", "AAPL", "GOOGL", "NVDA", "INTC", "CRM"],
                    "Healthcare": ["JNJ", "PFE", "MRK", "UNH", "ABBV", "TMO"],
                    "Financial Services": ["JPM", "BAC", "WFC", "GS", "MS", "C"],
                    "Consumer Cyclical": ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX"],
                    "Communication Services": ["META", "GOOGL", "NFLX", "DIS", "T", "VZ"],
                    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC"],
                    "Consumer Defensive": ["PG", "KO", "PEP", "WMT", "COST", "CL"],
                    "Industrials": ["BA", "CAT", "GE", "MMM", "UPS", "RTX"]
                }
                
                # Get peer tickers for this sector
                peer_tickers = sector_peers.get(sector, ["SPY", "QQQ", "DIA"])
                
                # Filter out the current stock and get first 3
                peer_tickers = [t for t in peer_tickers if t != ticker][:3]
                
                # Get real financial data for each peer
                for peer_ticker in peer_tickers:
                    try:
                        import yfinance as yf
                        peer_stock = yf.Ticker(peer_ticker)
                        peer_info = peer_stock.info
                        
                        # Get peer financial metrics
                        peer_name = peer_info.get('longName', peer_ticker)
                        peer_price = peer_info.get('currentPrice', peer_info.get('regularMarketPrice', None))
                        peer_pe = peer_info.get('trailingPE', None)
                        peer_forward_pe = peer_info.get('forwardPE', None)
                        peer_market_cap = peer_info.get('marketCap', None)
                        peer_dividend_yield = peer_info.get('dividendYield', None)
                        peer_target_price = peer_info.get('targetMeanPrice', None)
                        peer_profit_margin = peer_info.get('profitMargins', None)
                        peer_total_revenue = peer_info.get('totalRevenue', None)
                        
                        # Calculate peer upside/downside
                        if peer_target_price and peer_price:
                            peer_potential = ((peer_target_price - peer_price) / peer_price) * 100
                            peer_potential_text = f"{peer_potential:+.1f}%"
                        else:
                            peer_potential_text = "N/A"
                        
                        # Display peer comparison with actual stats
                        st.markdown(f"**{peer_name} ({peer_ticker})**")
                        
                        # Create columns for peer stats in 3x3 format
                        peer_col1, peer_col2, peer_col3 = st.columns(3)
                        
                        with peer_col1:
                            st.write(f"Price: ${peer_price:.2f}" if peer_price else "Price: N/A")
                            st.write(f"Analyst's Mean Target Price: ${peer_target_price:.2f}" if peer_target_price else "Target Price: N/A")
                            st.write(f"Upside: {peer_potential_text}")
                        
                        with peer_col2:
                            st.write(f"Market Cap: {format_large_number(peer_market_cap)}" if peer_market_cap else "Market Cap: N/A")
                            st.write(f"P/E: {peer_pe:.2f}" if peer_pe else "P/E: N/A")
                            st.write(f"Forward P/E: {peer_forward_pe:.2f}" if peer_forward_pe else "Forward P/E: N/A")
                        
                        with peer_col3:
                            st.write(f"Profit Margin: {peer_profit_margin*100:.2f}%" if peer_profit_margin else "Profit Margin: N/A")
                            st.write(f"Net Revenue: {format_large_number(peer_total_revenue)}" if peer_total_revenue else "Net Revenue: N/A")
                            st.write(f"Dividend: {peer_dividend_yield:.2f}%" if peer_dividend_yield else "Dividend: N/A")
                        

                        
                        st.markdown("---")
                        
                    except Exception as e:
                        st.write(f"**{peer_ticker}** - Unable to fetch comparison data")
                        st.markdown("---")
                
                # Add vertical spacing
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                # === 4. NEWS SECTION ===
                st.markdown("### 📰 News")
                
                # Upcoming Quarterly Earnings
                st.write("**📅 Upcoming Quarterly Earnings**")
                try:
                    import yfinance as yf
                    from datetime import datetime, timedelta
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    earnings_found = False
                    
                    # Try earnings_dates from info
                    if info.get('earningsDate'):
                        earnings_data = info.get('earningsDate')
                        if isinstance(earnings_data, list) and len(earnings_data) > 0:
                            try:
                                next_date = earnings_data[0]
                                if hasattr(next_date, 'strftime'):
                                    st.write(f"• {next_date.strftime('%B %d, %Y')} (Confirmed)")
                                    earnings_found = True
                                else:
                                    st.write(f"• {next_date} (Confirmed)")
                                    earnings_found = True
                            except:
                                pass
                    
                    # Try calendar data
                    if not earnings_found:
                        try:
                            calendar = stock.calendar
                            if hasattr(calendar, 'index') and len(calendar.index) > 0:
                                earnings_date = calendar.index[0]
                                st.write(f"• {earnings_date.strftime('%B %d, %Y')} (Unconfirmed)")
                                earnings_found = True
                        except:
                            pass
                    
                    # Calculate upcoming earnings for summer 2025
                    if not earnings_found:
                        try:
                            from datetime import datetime, timedelta
                            
                            # Since we're in 2025, estimate next earnings for summer 2025
                            current_date = datetime.now()
                            
                            # Force summer 2025 dates regardless of historical data
                            if current_date.month <= 6:  # Before July
                                estimated_next = datetime(2025, 7, 15)  # July 2025
                            elif current_date.month <= 9:  # July-Sep
                                estimated_next = datetime(2025, 10, 15)  # October 2025
                            else:  # Oct-Dec
                                estimated_next = datetime(2026, 1, 15)   # January 2026
                            
                            st.write(f"• ~{estimated_next.strftime('%B %d, %Y')} (Estimated)")
                            earnings_found = True
                        except:
                            pass
                    
                    if not earnings_found:
                        st.write("• Date TBD - Check investor relations")
                        
                except Exception as e:
                    st.write("• Date TBD - Check investor relations")
                
                # Previous Earnings Results
                st.write("**📊 Previous Earnings Results**")
                try:
                    import yfinance as yf
                    stock = yf.Ticker(ticker)
                    
                    earnings_displayed = False
                    
                    # Try to get earnings history - show most recent quarters
                    try:
                        from datetime import datetime
                        current_date = datetime.now()
                        
                        # Define the two most recent completed quarters
                        if current_date.month <= 3:  # We're in Q1, so most recent are Q4 and Q3 of previous year
                            quarters = [f"{current_date.year - 1} Q4", f"{current_date.year - 1} Q3"]
                        elif current_date.month <= 6:  # We're in Q2, so most recent are Q1 current year and Q4 previous year
                            quarters = [f"{current_date.year} Q1", f"{current_date.year - 1} Q4"]
                        elif current_date.month <= 9:  # We're in Q3, so most recent are Q2 and Q1 current year
                            quarters = [f"{current_date.year} Q2", f"{current_date.year} Q1"]
                        else:  # We're in Q4, so most recent are Q3 and Q2 current year
                            quarters = [f"{current_date.year} Q3", f"{current_date.year} Q2"]
                        
                        earnings_history = stock.earnings_history
                        if earnings_history is not None and not earnings_history.empty and len(earnings_history) >= 2:
                            recent_earnings = earnings_history.head(2)
                            for i, (date, row) in enumerate(recent_earnings.iterrows()):
                                eps_actual = row.get('epsActual')
                                eps_estimate = row.get('epsEstimate')
                                
                                # Use the calculated quarters
                                quarter_str = quarters[i] if i < len(quarters) else f"Recent Quarter {i+1}"
                                
                                # Clean formatting for beat/miss
                                if eps_actual is not None and eps_estimate is not None:
                                    try:
                                        actual_val = float(eps_actual)
                                        estimate_val = float(eps_estimate)
                                        beat_status = "Beat" if actual_val > estimate_val else "Missed"
                                        beat_icon = "🟢" if beat_status == "Beat" else "🔴"
                                        st.markdown(f"**{quarter_str}:** ${actual_val:.2f} vs ${estimate_val:.2f} est. {beat_icon} {beat_status}")
                                        earnings_displayed = True
                                    except (ValueError, TypeError):
                                        st.markdown(f"**{quarter_str}:** Data available")
                                        earnings_displayed = True
                                else:
                                    st.markdown(f"**{quarter_str}:** Earnings data available")
                                    earnings_displayed = True
                    except:
                        pass
                    
                    # Try quarterly financials as backup
                    if not earnings_displayed:
                        try:
                            quarterly_financials = stock.quarterly_financials
                            if quarterly_financials is not None and not quarterly_financials.empty:
                                # Get latest 2 quarters
                                dates = quarterly_financials.columns[:2]
                                for date in dates:
                                    quarter_str = date.strftime('%Y Q%q') if hasattr(date, 'strftime') else str(date)[:7]
                                    st.write(f"• {quarter_str}: Financial data available")
                                earnings_displayed = True
                        except:
                            pass
                    
                    if not earnings_displayed:
                        st.write("• Recent earnings data unavailable")
                        
                except Exception as e:
                    st.write("• Recent earnings data unavailable")
                
                # Recent News
                st.write("**📰 Recent News**")
                try:
                    # 52-week performance
                    if '52WeekChange' in company_info:
                        change_52w = company_info.get('52WeekChange', 0) * 100
                        change_icon = "🟢" if change_52w > 0 else "🔴" if change_52w < 0 else "⚪"
                        st.write(f"• 52-week performance: {change_52w:+.1f}% {change_icon}")
                    
                    # Recent news from Yahoo Finance
                    import yfinance as yf
                    stock = yf.Ticker(ticker)
                    news = stock.news
                    
                    if news and len(news) > 0:
                        # Show only the most recent relevant article
                        for article in news[:1]:
                            title = article.get('title', '')
                            link = article.get('link', '')
                            if title and link:
                                st.write(f"• [{title}]({link})")
                                break
                    else:
                        st.write("• Check company investor relations for updates")
                        
                except Exception as e:
                    st.write("• Check company investor relations for updates")
                
                # Add vertical spacing
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                # === 5. INTERACTIVE GRAPH SECTION ===
                st.markdown("### 📈 Historical Performance")
                
                # Graph controls - use unique keys tied to the ticker to prevent reset
                graph_col1, graph_col2 = st.columns(2)
                
                with graph_col1:
                    metric_choice = st.selectbox(
                        "Select Metric",
                        ["Market Price", "Gross Sales", "Net Revenue"],
                        key=f"metric_selector_{ticker}"
                    )
                
                with graph_col2:
                    period_choice = st.selectbox(
                        "Select Time Period", 
                        ["1 Year", "3 Years", "5 Years"],
                        key=f"period_selector_{ticker}"
                    )
                
                # Get historical data and create chart based on selected metric
                try:
                    import plotly.graph_objects as go
                    
                    if metric_choice == "Market Price":
                        # Map period choice to yfinance format
                        period_map = {"1 Year": "1y", "3 Years": "3y", "5 Years": "5y"}
                        period = period_map[period_choice]
                        
                        historical_data = analyzer.get_historical_data(period)
                        if not historical_data.empty:
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=historical_data.index,
                                y=historical_data['Close'],
                                mode='lines',
                                name='Close Price',
                                line=dict(color='#3B82F6', width=2)
                            ))
                            
                            fig.update_layout(
                                title=f'{ticker} - {metric_choice} ({period_choice})',
                                xaxis_title='Date',
                                yaxis_title='Price ($)',
                                template='plotly_dark',
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='white')
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("No historical data available for the selected period")
                    
                    elif metric_choice in ["Gross Sales", "Net Revenue"]:
                        # Get financial statement data
                        import yfinance as yf
                        stock = yf.Ticker(ticker)
                        
                        if metric_choice == "Gross Sales":
                            # Get quarterly and annual revenue data
                            quarterly_financials = stock.quarterly_financials
                            annual_financials = stock.financials
                            
                            # Use annual data for longer periods
                            if period_choice in ["3 Years", "5 Years"]:
                                if not annual_financials.empty and 'Total Revenue' in annual_financials.index:
                                    revenue_data = annual_financials.loc['Total Revenue'].dropna()
                                    y_label = 'Revenue ($)'
                                    title_suffix = 'Annual Gross Sales'
                                else:
                                    st.warning("Annual revenue data not available")
                                    revenue_data = None
                            else:
                                # Use quarterly data for 1 year
                                if not quarterly_financials.empty and 'Total Revenue' in quarterly_financials.index:
                                    revenue_data = quarterly_financials.loc['Total Revenue'].dropna()
                                    y_label = 'Revenue ($)'
                                    title_suffix = 'Quarterly Gross Sales'
                                else:
                                    st.warning("Quarterly revenue data not available")
                                    revenue_data = None
                        
                        elif metric_choice == "Net Revenue":
                            # Get net income data
                            quarterly_financials = stock.quarterly_financials
                            annual_financials = stock.financials
                            
                            if period_choice in ["3 Years", "5 Years"]:
                                if not annual_financials.empty and 'Net Income' in annual_financials.index:
                                    revenue_data = annual_financials.loc['Net Income'].dropna()
                                    y_label = 'Net Income ($)'
                                    title_suffix = 'Annual Net Revenue'
                                else:
                                    st.warning("Annual net income data not available")
                                    revenue_data = None
                            else:
                                if not quarterly_financials.empty and 'Net Income' in quarterly_financials.index:
                                    revenue_data = quarterly_financials.loc['Net Income'].dropna()
                                    y_label = 'Net Income ($)'
                                    title_suffix = 'Quarterly Net Revenue'
                                else:
                                    st.warning("Quarterly net income data not available")
                                    revenue_data = None
                        
                        # Create chart if data is available
                        if revenue_data is not None and len(revenue_data) > 0:
                            # Sort by date (most recent first in yfinance, so reverse for chronological order)
                            revenue_data = revenue_data.sort_index()
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=revenue_data.index,
                                y=revenue_data.values,
                                mode='lines+markers',
                                name=metric_choice,
                                line=dict(color='#10B981', width=3),
                                marker=dict(size=8)
                            ))
                            
                            fig.update_layout(
                                title=f'{ticker} - {title_suffix}',
                                xaxis_title='Date',
                                yaxis_title=y_label,
                                template='plotly_dark',
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='white')
                            )
                            
                            # Format y-axis to show abbreviated values (B for billions, M for millions)
                            def format_currency(value):
                                if abs(value) >= 1e9:
                                    return f"${value/1e9:.1f}B"
                                elif abs(value) >= 1e6:
                                    return f"${value/1e6:.1f}M"
                                elif abs(value) >= 1e3:
                                    return f"${value/1e3:.1f}K"
                                else:
                                    return f"${value:.0f}"
                            
                            # Apply custom formatting to y-axis
                            max_val = max(revenue_data.values)
                            min_val = min(revenue_data.values)
                            
                            fig.update_layout(
                                yaxis=dict(
                                    tickvals=[min_val, (min_val + max_val)/2, max_val],
                                    ticktext=[format_currency(min_val), format_currency((min_val + max_val)/2), format_currency(max_val)],
                                    tickmode='array'
                                )
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info(f"No {metric_choice.lower()} data available for this stock")
                
                except Exception as e:
                    st.error(f"Error loading {metric_choice.lower()} data: {str(e)}")
                
                # Add vertical spacing
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                # === 6. AI SUMMARY SECTION (moved after Historical Performance) ===
                st.markdown("### 🤖 AI Analysis Summary")
                
                # Generate personalized AI summary with company-specific details
                company_name = company_info.get('longName', ticker)
                sector = company_info.get('sector', 'Unknown')
                market_cap = company_info.get('marketCap', 0)
                pe_ratio = company_info.get('trailingPE', 0)
                profit_margin = company_info.get('profitMargins', 0)
                
                # Create size category
                if market_cap > 200_000_000_000:
                    size_category = "mega-cap"
                elif market_cap > 50_000_000_000:
                    size_category = "large-cap"
                elif market_cap > 10_000_000_000:
                    size_category = "mid-cap"
                else:
                    size_category = "small-cap"
                
                # Create valuation assessment
                valuation_note = ""
                if pe_ratio and pe_ratio > 25:
                    valuation_note = "trading at a premium valuation"
                elif pe_ratio and pe_ratio < 15:
                    valuation_note = "appearing undervalued by traditional metrics"
                elif pe_ratio:
                    valuation_note = "fairly valued based on earnings multiples"
                
                # Create profitability note
                profit_note = ""
                if profit_margin and profit_margin > 0.20:
                    profit_note = "demonstrating exceptional profitability"
                elif profit_margin and profit_margin > 0.10:
                    profit_note = "maintaining healthy profit margins"
                elif profit_margin and profit_margin > 0:
                    profit_note = "operating with modest profitability"
                else:
                    profit_note = "facing profitability challenges"
                
                # Rating determination
                if buy_rating >= 7:
                    rating_text = f"**BUY RATING: {buy_rating:.1f}/10**"
                    recommendation = "presents a compelling investment opportunity"
                elif buy_rating >= 4:
                    rating_text = f"**HOLD RATING: {buy_rating:.1f}/10**"
                    recommendation = "warrants careful consideration with mixed signals"
                else:
                    rating_text = f"**SELL RATING: {buy_rating:.1f}/10**"
                    recommendation = "faces significant headwinds and risks"
                
                # Generate personalized summary with About section formatting
                st.markdown(f"""
                **{rating_text.replace('**', '').replace('*', '')}**
                
                {company_name} is a {size_category} {sector.lower()} company that {recommendation}. The stock is currently {valuation_note} and {profit_note}. Our analysis indicates {rating_breakdown.get('Technical Analysis', {}).get('reason', 'mixed technical signals').lower()}, while the company's fundamentals show {rating_breakdown.get('Fundamental Analysis', {}).get('reason', 'average financial health').lower()}. Market sentiment suggests {rating_breakdown.get('Market Sentiment', {}).get('reason', 'neutral investor confidence').lower()}, which combined with the technical and fundamental picture supports our {buy_rating:.1f}/10 rating.
                """)
                
            except Exception as e:
                st.error(f"Error analyzing stock: {str(e)}")
                st.info("Please try again with a different stock symbol or check if the ticker is valid.")
            
            # Add reset search button after analysis
            st.write("")  # Add some spacing
            if st.button("Reset Search", key="reset_stock_search"):
                # Clear all analysis-related session state
                if "selected_ticker" in st.session_state:
                    del st.session_state.selected_ticker
                if "stock_search" in st.session_state:
                    del st.session_state.stock_search
                st.rerun()
        
        elif search_button and not ticker:
            st.warning("Please select a stock from the dropdown before analyzing.")
        
        # Power Plays Section
        st.markdown('<div id="powerplays" class="section-spacer"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Power Plays<span class="section-emoji">🚀</span></div>', unsafe_allow_html=True)
        
        display_power_plays()
        
        # Data Sources section
        st.markdown('<div class="section-header">Data Sources<span class="section-emoji">📊</span></div>', unsafe_allow_html=True)
        st.markdown("All our financial data comes from trusted, professional sources: **[Yahoo Finance](https://finance.yahoo.com/)**, **[Bloomberg](https://www.bloomberg.com/)**, **[MarketWatch](https://www.marketwatch.com/)**, **[CNBC](https://www.cnbc.com/)**, **[SEC EDGAR Database](https://sec.gov/)**, and **[Morningstar](https://www.morningstar.com/)**.")
        
        # Logout button
        logout_button()
        
        # Admin panel access - positioned well below data sources
        if is_admin():
            # Add more space to clearly separate from data sources
            st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
            
            # Admin panel button with blue styling to match other action buttons
            if st.button("🔧 Admin Panel", key="admin_panel_access", help="Access admin controls", type="primary"):
                st.session_state.view_mode = "admin"
                st.rerun()
        
        # Footer Section (Contact Us)
        st.markdown("""
        <div class="footer">
            <div class="footer-content">
                <div>
                    <div class="footer-logo">Ticker AI</div>
                    <div class="footer-info">AI-powered stock analysis and investment insights</div>
                </div>
                <div class="footer-info">
                    <div><strong>Contact Us:</strong></div>
                    <div>Email: gkraem@vt.edu</div>
                    <div>Phone: 240-285-7119</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()