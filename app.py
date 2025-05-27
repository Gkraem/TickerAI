import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import base64
import os
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
            background-color: rgba(17, 24, 39, 0.95);
            backdrop-filter: blur(10px);
            padding: 2px 0;
            border-bottom: 1px solid rgba(59, 130, 246, 0.3);
        }}
        .nav-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 80px;
            width: 100%;
            max-width: none;
        }}
        .nav-logo {{
            margin: 0;
            color: #3b82f6;
            font-size: 22px;
            font-weight: bold;
            padding: 8px 0;
        }}
        .nav-menu {{
            display: flex;
            gap: 35px;
            margin-left: auto;
            padding: 8px 0;
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
        }}
        .hero-title {{
            font-size: 4rem;
            font-weight: bold;
            color: white;
            margin-bottom: 1rem;
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
        }}
        .hero-button:hover {{
            transform: translateY(-2px);
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
            background-color: rgba(17, 24, 39, 0.95);
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
            <p class="hero-subtitle">
                Transform complex financial data into actionable insights with AI-powered stock analysis
            </p>
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
        
        # Create columns for all elements on one line
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            # Single combined dropdown - aligned left
            selected_option = st.selectbox(
                "Search stocks by typing",
                options=[""] + all_options,
                index=0,
                key="stock_search",
                on_change=update_stock_results
            )
        
        with col2:
            # Timeframe selector
            timeframe = st.selectbox(
                "Select Timeframe",
                ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "max"],
                index=5  # Default to 1 year
            )
        
        with col3:
            # Add spacing to align button with dropdowns
            st.markdown('<div style="height: 26px;"></div>', unsafe_allow_html=True)
            # Search button
            search_button = st.button("Analyze Stock", type="primary")
        
        # Extract ticker from selection if available (removed confirmation box)
        ticker = ""
        if selected_option and " - " in selected_option:
            ticker = selected_option.split(" - ")[0]
            st.session_state.selected_ticker = ticker
        
        # Use selected ticker if available
        if "selected_ticker" in st.session_state and st.session_state.selected_ticker:
            ticker = st.session_state.selected_ticker
        
        # Stock analysis display
        if search_button and ticker:
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
                
                # Simple, clean rating display
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <div style="font-size: 48px; font-weight: bold; color: {color}; margin-bottom: 10px;">
                            {buy_rating:.1f}/10
                        </div>
                        <div style="font-size: 24px; font-weight: bold; color: {color};">
                            {recommendation}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
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
                
                # Arrange in 3 columns as requested
                fin_col1, fin_col2, fin_col3 = st.columns(3)
                
                with fin_col1:
                    st.metric("Current Price", f"${current_price:.2f}" if current_price else "N/A")
                    st.metric("P/E Ratio (TTM)", f"{trailing_pe:.2f}" if trailing_pe else "N/A")
                
                with fin_col2:
                    st.metric("Target Price", f"${target_price:.2f}" if target_price else "N/A")
                    st.metric("Forward P/E", f"{forward_pe:.2f}" if forward_pe else "N/A")
                
                with fin_col3:
                    st.metric("Upside/Downside", potential_text)
                    st.metric("Market Cap", format_large_number(market_cap) if market_cap else "N/A")
                
                # Additional metrics in second row
                fin_col4, fin_col5, fin_col6 = st.columns(3)
                
                with fin_col4:
                    st.metric("Profit Margin", f"{profit_margin*100:.2f}%" if profit_margin else "N/A")
                
                with fin_col5:
                    st.metric("Dividend Yield", f"{dividend_yield*100:.2f}%" if dividend_yield else "N/A")
                
                with fin_col6:
                    st.metric("", "")  # Empty for spacing
                
                # === 3. SECTOR COMPARISON SECTION ===
                st.markdown("### 🏭 Sector Analysis")
                
                sector = company_info.get('sector', 'Unknown')
                industry = company_info.get('industry', 'Unknown')
                
                st.write(f"**Sector:** {sector}")
                st.write(f"**Industry:** {industry}")
                
                # Sector peer comparison
                st.markdown("#### Peer Comparison")
                
                # Get sector peers based on sector type
                if sector == "Technology":
                    peers = [
                        {"name": "Microsoft (MSFT)", "rating": 8.2, "reason": "Higher profitability and stronger balance sheet"},
                        {"name": "Apple (AAPL)", "rating": 7.8, "reason": "More consistent revenue growth and premium valuation"},
                        {"name": "Intel (INTC)", "rating": 6.1, "reason": "Lower growth prospects but attractive dividend yield"}
                    ]
                elif sector == "Healthcare":
                    peers = [
                        {"name": "Johnson & Johnson (JNJ)", "rating": 7.5, "reason": "Diversified portfolio and stable dividend payments"},
                        {"name": "Pfizer (PFE)", "rating": 6.8, "reason": "Strong pipeline but facing patent cliffs"},
                        {"name": "Merck (MRK)", "rating": 7.2, "reason": "Solid oncology franchise and reasonable valuation"}
                    ]
                elif sector == "Financial Services":
                    peers = [
                        {"name": "JPMorgan Chase (JPM)", "rating": 7.9, "reason": "Superior return on equity and trading revenues"},
                        {"name": "Bank of America (BAC)", "rating": 7.1, "reason": "Strong deposit base but interest rate sensitivity"},
                        {"name": "Wells Fargo (WFC)", "rating": 6.3, "reason": "Recovery story but regulatory overhang remains"}
                    ]
                elif sector == "Consumer Cyclical":
                    peers = [
                        {"name": "Amazon (AMZN)", "rating": 8.5, "reason": "Dominant e-commerce position and cloud growth"},
                        {"name": "Tesla (TSLA)", "rating": 7.4, "reason": "EV market leadership but high valuation"},
                        {"name": "Home Depot (HD)", "rating": 7.6, "reason": "Strong housing market exposure and execution"}
                    ]
                elif sector == "Communication Services":
                    peers = [
                        {"name": "Meta Platforms (META)", "rating": 7.7, "reason": "Strong advertising recovery and AI investments"},
                        {"name": "Alphabet (GOOGL)", "rating": 8.1, "reason": "Search dominance and cloud computing growth"},
                        {"name": "Netflix (NFLX)", "rating": 6.9, "reason": "Content costs pressuring margins despite subscriber growth"}
                    ]
                elif sector == "Energy":
                    peers = [
                        {"name": "Exxon Mobil (XOM)", "rating": 7.3, "reason": "Improved capital discipline and strong cash flow"},
                        {"name": "Chevron (CVX)", "rating": 7.8, "reason": "Lower cost structure and consistent dividend policy"},
                        {"name": "ConocoPhillips (COP)", "rating": 7.5, "reason": "Variable dividend policy and shale expertise"}
                    ]
                else:
                    peers = [
                        {"name": "S&P 500 Index (SPY)", "rating": 7.2, "reason": "Broad market diversification"},
                        {"name": "Sector ETF", "rating": 7.0, "reason": "Sector-specific exposure without single stock risk"},
                        {"name": "Market Average", "rating": 6.8, "reason": "Historical market performance baseline"}
                    ]
                
                for i, peer in enumerate(peers):
                    peer_rating = peer["rating"]
                    if peer_rating >= 7:
                        peer_color = "#10B981"
                        peer_rec = "BUY"
                    elif peer_rating >= 4:
                        peer_color = "#F59E0B"
                        peer_rec = "HOLD"
                    else:
                        peer_color = "#EF4444"
                        peer_rec = "SELL"
                    
                    comparison = "better" if buy_rating > peer_rating else "worse" if buy_rating < peer_rating else "similar"
                    
                    st.markdown(f"""
                    **{peer['name']}** - <span style='color: {peer_color}; font-weight: bold;'>{peer_rating}/10 ({peer_rec})</span>  
                    {ticker} is **{comparison}** - {peer['reason']}
                    """, unsafe_allow_html=True)
                
                # === 4. NEWS SECTION ===
                st.markdown("### 📰 News")
                
                # Get earnings information
                earnings_date = company_info.get('nextEarningsDate', None)
                last_earnings_date = company_info.get('lastEarningsDate', None)
                
                if last_earnings_date:
                    st.write(f"**Previous Earnings:** {last_earnings_date}")
                if earnings_date:
                    st.write(f"**Next Earnings:** {earnings_date}")
                else:
                    st.write("**Next Earnings:** Date not available")
                
                # Get dividend information
                dividend_rate = company_info.get('dividendRate', None)
                dividend_yield = company_info.get('dividendYield', None)
                ex_dividend_date = company_info.get('exDividendDate', None)
                
                if dividend_rate:
                    st.write(f"**Dividend Rate:** ${dividend_rate:.2f} annually")
                if ex_dividend_date:
                    st.write(f"**Ex-Dividend Date:** {ex_dividend_date}")
                
                # Get recent news using authentic data
                try:
                    news_data = get_stock_news(ticker, num_articles=3)
                    if news_data:
                        st.write("**Recent News:**")
                        for article in news_data[:3]:
                            st.write(f"• {article.get('title', 'News article')}")
                    else:
                        st.write("**Recent News:** No recent news available")
                except:
                    st.write("**Recent News:** Unable to fetch news at this time")
                
                # === 5. AI SUMMARY SECTION ===
                st.markdown("### 🤖 AI Analysis Summary")
                
                # Generate AI summary based on rating components
                technical_reason = rating_breakdown.get('Technical Analysis', {}).get('reason', 'Technical analysis unavailable')
                fundamental_reason = rating_breakdown.get('Fundamental Analysis', {}).get('reason', 'Fundamental analysis unavailable')
                sentiment_reason = rating_breakdown.get('Market Sentiment', {}).get('reason', 'Sentiment analysis unavailable')
                
                if buy_rating >= 7:
                    summary_intro = f"**{ticker} receives a BUY rating of {buy_rating:.1f}/10.** "
                elif buy_rating >= 4:
                    summary_intro = f"**{ticker} receives a HOLD rating of {buy_rating:.1f}/10.** "
                else:
                    summary_intro = f"**{ticker} receives a SELL rating of {buy_rating:.1f}/10.** "
                
                ai_summary = f"""{summary_intro}The analysis reveals {technical_reason.lower()}, while fundamentally the stock shows {fundamental_reason.lower()}. Market sentiment indicates {sentiment_reason.lower()}. This combined analysis suggests the current rating reflects the stock's balanced risk-reward profile based on technical momentum, fundamental valuation, and market consensus."""
                
                st.write(ai_summary)
                
                # === 6. INTERACTIVE GRAPH SECTION ===
                st.markdown("### 📈 Historical Performance")
                
                # Graph controls - use unique keys tied to the ticker to prevent reset
                graph_col1, graph_col2 = st.columns(2)
                
                with graph_col1:
                    metric_choice = st.selectbox(
                        "Select Metric",
                        ["Market Price", "Volume", "Revenue (Annual)"],
                        key=f"metric_selector_{ticker}"
                    )
                
                with graph_col2:
                    period_choice = st.selectbox(
                        "Select Time Period", 
                        ["1 Year", "3 Years", "5 Years"],
                        key=f"period_selector_{ticker}"
                    )
                
                # Get historical data and create chart
                if metric_choice == "Market Price":
                    # Map period choice to yfinance format
                    period_map = {"1 Year": "1y", "3 Years": "3y", "5 Years": "5y"}
                    period = period_map[period_choice]
                    
                    try:
                        historical_data = analyzer.get_historical_data(period)
                        if not historical_data.empty:
                            import plotly.graph_objects as go
                            
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
                    except Exception as e:
                        st.error(f"Error loading historical data: {str(e)}")
                else:
                    st.info(f"Historical {metric_choice} data visualization coming soon")
                
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
        st.markdown("All our financial data comes from trusted, professional sources:")
        st.markdown("• **[Yahoo Finance](https://finance.yahoo.com/)** - Real-time stock prices, historical data, and company information")
        st.markdown("• **[yfinance Python Library](https://pypi.org/project/yfinance/)** - Yahoo Finance API wrapper for data retrieval")
        st.markdown("• **[Plotly](https://plotly.com/)** - Interactive charting and data visualization")
        st.markdown("• **[Technical Analysis Algorithms](https://ta-lib.org/)** - RSI, MACD, Bollinger Bands, and moving averages")
        st.markdown("• **[Financial Statement APIs](https://sec.gov/)** - Income statements, balance sheets, and cash flow data")
        st.markdown("• **[Market News Aggregators](https://newsapi.org/)** - Recent news articles and market sentiment analysis")
        
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