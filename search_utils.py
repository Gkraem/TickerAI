"""
Stock Search Utilities
Extracted search functionality without Streamlit configuration conflicts
"""

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
    {"ticker": "GS", "name": "Goldman Sachs Group Inc."},
    {"ticker": "MS", "name": "Morgan Stanley"},
    {"ticker": "C", "name": "Citigroup Inc."},
    {"ticker": "BLK", "name": "BlackRock Inc."},
    {"ticker": "SCHW", "name": "Charles Schwab Corporation"},
    {"ticker": "AXP", "name": "American Express Company"},
    {"ticker": "COF", "name": "Capital One Financial Corp."},
    {"ticker": "V", "name": "Visa Inc."},
    {"ticker": "MA", "name": "Mastercard Inc."},
    {"ticker": "PYPL", "name": "PayPal Holdings Inc."},
    {"ticker": "SQ", "name": "Block Inc."},
    {"ticker": "PNC", "name": "PNC Financial Services Group"},
    {"ticker": "USB", "name": "U.S. Bancorp"},
    {"ticker": "TFC", "name": "Truist Financial Corporation"},
    {"ticker": "MTB", "name": "M&T Bank Corporation"},
    {"ticker": "KEY", "name": "KeyCorp"},
    {"ticker": "CFG", "name": "Citizens Financial Group Inc."},
    
    # Healthcare & Pharmaceuticals
    {"ticker": "UNH", "name": "UnitedHealth Group Inc."},
    {"ticker": "JNJ", "name": "Johnson & Johnson"},
    {"ticker": "PFE", "name": "Pfizer Inc."},
    {"ticker": "CVS", "name": "CVS Health Corporation"},
    {"ticker": "ABBV", "name": "AbbVie Inc."},
    {"ticker": "BMY", "name": "Bristol-Myers Squibb Company"},
    {"ticker": "MRK", "name": "Merck & Co. Inc."},
    {"ticker": "LLY", "name": "Eli Lilly and Company"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific Inc."},
    {"ticker": "ABT", "name": "Abbott Laboratories"},
    {"ticker": "DHR", "name": "Danaher Corporation"},
    {"ticker": "SYK", "name": "Stryker Corporation"},
    {"ticker": "BSX", "name": "Boston Scientific Corporation"},
    {"ticker": "MDT", "name": "Medtronic plc"},
    {"ticker": "ZBH", "name": "Zimmer Biomet Holdings Inc."},
    {"ticker": "BAX", "name": "Baxter International Inc."},
    {"ticker": "BDX", "name": "Becton Dickinson and Company"},
    {"ticker": "EW", "name": "Edwards Lifesciences Corporation"},
    {"ticker": "ISRG", "name": "Intuitive Surgical Inc."},
    {"ticker": "BIIB", "name": "Biogen Inc."},
    {"ticker": "MRNA", "name": "Moderna Inc."},
    {"ticker": "REGN", "name": "Regeneron Pharmaceuticals Inc."},
    {"ticker": "ILMN", "name": "Illumina Inc."},
    {"ticker": "BMRN", "name": "BioMarin Pharmaceutical Inc."},
    
    # Energy
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
    {"ticker": "OVV", "name": "Ovintiv Inc."},
    
    # Consumer Staples
    {"ticker": "PG", "name": "Procter & Gamble Company"},
    {"ticker": "KO", "name": "Coca-Cola Company"},
    {"ticker": "PEP", "name": "PepsiCo Inc."},
    {"ticker": "UL", "name": "Unilever PLC"},
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
    {"ticker": "MKC", "name": "McCormick & Company Inc."},
    {"ticker": "MDLZ", "name": "Mondelez International Inc."},
    {"ticker": "KHC", "name": "Kraft Heinz Company"},
    
    # Retail
    {"ticker": "WMT", "name": "Walmart Inc."},
    {"ticker": "TGT", "name": "Target Corporation"},
    {"ticker": "COST", "name": "Costco Wholesale Corporation"},
    {"ticker": "HD", "name": "Home Depot Inc."},
    {"ticker": "LOW", "name": "Lowe's Companies Inc."},
    {"ticker": "TJX", "name": "TJX Companies Inc."},
    {"ticker": "BKNG", "name": "Booking Holdings Inc."},
    {"ticker": "MCD", "name": "McDonald's Corporation"},
    {"ticker": "SBUX", "name": "Starbucks Corporation"},
    {"ticker": "NKE", "name": "Nike Inc."},
    {"ticker": "LULU", "name": "Lululemon Athletica Inc."},
    {"ticker": "BBY", "name": "Best Buy Co. Inc."},
    {"ticker": "EBAY", "name": "eBay Inc."},
    {"ticker": "ETSY", "name": "Etsy Inc."},
    {"ticker": "SHOP", "name": "Shopify Inc."},
    
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
    
    # Real Estate & REITs
    {"ticker": "AMT", "name": "American Tower Corporation"},
    {"ticker": "PLD", "name": "Prologis Inc."},
    {"ticker": "CCI", "name": "Crown Castle Inc."},
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
    {"ticker": "MAA", "name": "Mid-America Apartment Communities Inc."},
    {"ticker": "CPT", "name": "Camden Property Trust"},
    {"ticker": "HST", "name": "Host Hotels & Resorts Inc."},
    {"ticker": "RHP", "name": "Ryman Hospitality Properties Inc."},
    {"ticker": "SLG", "name": "SL Green Realty Corp."},
    {"ticker": "BXP", "name": "Boston Properties Inc."},
    {"ticker": "VTR", "name": "Ventas Inc."},
    {"ticker": "WELL", "name": "Welltower Inc."},
    
    # Materials & Chemicals
    {"ticker": "LIN", "name": "Linde plc"},
    {"ticker": "APD", "name": "Air Products and Chemicals Inc."},
    {"ticker": "SHW", "name": "Sherwin-Williams Company"},
    {"ticker": "ECL", "name": "Ecolab Inc."},
    {"ticker": "DD", "name": "DuPont de Nemours Inc."},
    {"ticker": "DOW", "name": "Dow Inc."},
    {"ticker": "LYB", "name": "LyondellBasell Industries N.V."},
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
    
    # Telecommunications & Media
    {"ticker": "T", "name": "AT&T Inc."},
    {"ticker": "VZ", "name": "Verizon Communications Inc."},
    {"ticker": "TMUS", "name": "T-Mobile US Inc."},
    {"ticker": "CMCSA", "name": "Comcast Corporation"},
    {"ticker": "CHTR", "name": "Charter Communications Inc."},
    {"ticker": "DIS", "name": "Walt Disney Company"},
    {"ticker": "PARA", "name": "Paramount Global"},
    {"ticker": "WBD", "name": "Warner Bros. Discovery Inc."},
    {"ticker": "FOX", "name": "Fox Corporation"},
    {"ticker": "FOXA", "name": "Fox Corporation"},
    {"ticker": "LYV", "name": "Live Nation Entertainment Inc."},
    {"ticker": "SONY", "name": "Sony Group Corporation"},
    {"ticker": "SPOT", "name": "Spotify Technology S.A."},
    
    # Utilities
    {"ticker": "NEE", "name": "NextEra Energy Inc."},
    {"ticker": "DUK", "name": "Duke Energy Corporation"},
    {"ticker": "SO", "name": "Southern Company"},
    {"ticker": "D", "name": "Dominion Energy Inc."},
    {"ticker": "EXC", "name": "Exelon Corporation"},
    {"ticker": "AEP", "name": "American Electric Power Company Inc."},
    {"ticker": "XEL", "name": "Xcel Energy Inc."},
    {"ticker": "SRE", "name": "Sempra Energy"},
    {"ticker": "PCG", "name": "PG&E Corporation"},
    {"ticker": "ED", "name": "Consolidated Edison Inc."},
    
    # Chinese/International Stocks
    {"ticker": "BABA", "name": "Alibaba Group Holding Limited"},
    {"ticker": "JD", "name": "JD.com Inc."},
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
    {"ticker": "NVO", "name": "Novo Nordisk A/S"},
    
    # High Growth & Tech
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
    {"ticker": "PINS", "name": "Pinterest Inc."},
    {"ticker": "SNAP", "name": "Snap Inc."},
]

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