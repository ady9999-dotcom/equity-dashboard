"""
Sector knowledge base — sector-specific analytical lenses, key metrics, red flags,
and which generic ratios to DE-EMPHASISE (so a bank isn't judged on EV/EBITDA, a
capex-phase utility isn't dinged for low FCF, a jeweller isn't flagged for high
inventory days). Encodes how the great long-term investors actually read each sector.

`profile(sector_text, name)` classifies a holding into a bucket and returns its lens.
"""

# Each bucket: lens · keyMetrics · redFlags · deEmphasise (generic ratios that mislead here)
# · investorLens · feedGap (what the price feed can't see → needs the research pass).
SECTORS = {
    "banks": {
        "bucket": "Banks & Lenders",
        "lens": "A bank is a spread-and-risk business — read it on book value and asset quality, not EV/EBITDA or leverage. Deposits are the moat.",
        "keyMetrics": ["NIM", "NII growth", "GNPA / NNPA", "PCR (provision coverage)", "slippage & credit cost", "CASA ratio", "RoA / RoE", "CRAR / CET-1", "advances & deposit growth"],
        "redFlags": ["rising GNPA / slippages", "falling CASA (costlier funds)", "credit-cost spike", "large restructured/ECL book", "governance or promoter issues"],
        "deEmphasise": ["EV/EBITDA", "current ratio", "D/E & 'leverage'", "EBITDA margin", "Altman Z-score", "interest coverage"],
        "investorLens": "Buffett: a low-cost deposit franchise (Amex, Wells) compounds for decades. Munger: avoid the bank that chases growth into bad loans.",
        "feedGap": "GNPA / NIM / CASA are NOT in the price feed — they come from the research pass & quarterly filings.",
    },
    "nbfc": {
        "bucket": "NBFCs & Financiers",
        "lens": "AUM growth × spread × credit cost, funded by wholesale money — so cost-of-funds and rate cycle matter more than for a bank.",
        "keyMetrics": ["AUM growth", "NIM / spread", "GNPA & credit cost", "cost of funds & ALM", "RoA / RoE", "CRAR", "borrowing mix"],
        "redFlags": ["asset-liability mismatch", "rising credit cost", "funding-access stress", "rapid unseasoned AUM growth", "sector-specific NPA (e.g. MFI)"],
        "deEmphasise": ["EV/EBITDA", "current ratio", "EBITDA margin", "'leverage' (it's the business model)"],
        "investorLens": "Munger: a lender's quality only shows in the next downturn. Damani/Jhunjhunwala: back the disciplined underwriter, not the fastest grower.",
        "feedGap": "Asset quality & ALM come from filings/research, not the price feed.",
    },
    "insurance": {
        "bucket": "Insurance",
        "lens": "Value on embedded value + new-business margin, not P/E. It's a long-duration liability book.",
        "keyMetrics": ["VNB margin", "APE growth", "persistency (13th/61st month)", "embedded value & VNB", "solvency ratio", "product mix (par/non-par/ULIP)"],
        "redFlags": ["falling persistency", "VNB-margin compression", "mis-selling / regulatory action", "solvency near floor"],
        "deEmphasise": ["EV/EBITDA", "P/E", "EBITDA margin", "current ratio"],
        "investorLens": "Buffett: insurance is float — underwriting discipline + investment of float is the whole game.",
        "feedGap": "VNB / persistency / EV are disclosed in results, not the price feed.",
    },
    "it": {
        "bucket": "IT Services",
        "lens": "A people-leveraged annuity business — $ revenue growth and margin, watched for AI disruption to the labour-arbitrage model.",
        "keyMetrics": ["$ revenue growth (CC)", "deal TCV / book-to-bill", "attrition", "utilization", "EBIT margin", "client concentration", "FX sensitivity"],
        "redFlags": ["soft TCV / weak deal wins", "rising attrition", "margin erosion", "top-client concentration", "structural AI / GenAI threat to headcount model"],
        "deEmphasise": ["capital intensity", "asset turnover", "D/E (they're net-cash)"],
        "investorLens": "Buffett: moat = switching costs + culture. Dalio: a USD-earner and rupee hedge, exposed to the global (US) demand cycle.",
        "feedGap": "TCV / attrition / deal commentary come from results & calls, not the price feed.",
    },
    "pharma": {
        "bucket": "Pharma & Healthcare",
        "lens": "Regulated IP + manufacturing — USFDA compliance is existential; a warning letter can halve earnings power overnight.",
        "keyMetrics": ["USFDA / regulatory status (483s, warning letters, import alerts)", "R&D productivity", "ANDA pipeline & approvals", "US price erosion", "API vs formulations mix", "complex-generics / biosimilars"],
        "redFlags": ["USFDA warning letter / import alert", "single-plant concentration", "US price erosion", "patent cliffs", "R&D that doesn't convert to approvals"],
        "deEmphasise": ["EV/EBITDA alone", "current ratio"],
        "investorLens": "Munger: invert — the regulatory landmine is what kills the thesis, not the P/E. Lynch: understand the pipeline before the story.",
        "feedGap": "USFDA status & pipeline come from regulatory sites & research, not the price feed.",
    },
    "metals": {
        "bucket": "Metals & Mining (cyclical)",
        "lens": "A price-taker — judge on through-cycle margins, cost-curve position, and leverage AT THE TROUGH, not spot earnings.",
        "keyMetrics": ["realisations vs cost curve", "capacity utilization", "net debt / EBITDA (at trough)", "capex intensity", "China oversupply", "global prices & spreads"],
        "redFlags": ["high leverage entering a downcycle", "expansion funded at cycle peak", "market cap < replacement cost with debt", "China dumping"],
        "deEmphasise": ["spot P/E (misleads at peaks & troughs)", "single-year EBITDA margin"],
        "investorLens": "Graham: buy near trough asset value with survivable leverage. Dalio: it's a bet on the global/China industrial cycle. Jhunjhunwala: cyclicals are about timing the turn.",
        "feedGap": "Cost-curve position & through-cycle margins need analysis beyond one year of ratios.",
    },
    "energy": {
        "bucket": "Energy / Oil & Gas",
        "lens": "Capital-intensive commodity + regulation — refining/marketing margins, crude, and the capex cycle drive it; value optionality (new energy) separately.",
        "keyMetrics": ["GRM (refining margin)", "crude realisations", "capex cycle & FCF turn", "debt / net-energy transition capex", "regulated vs market segments"],
        "redFlags": ["margin squeeze from crude/regulation", "value-destructive mega-capex", "over-leverage in a downcycle"],
        "deEmphasise": ["simple FCF-DCF (peak-capex years look terrible)", "spot P/E"],
        "investorLens": "Buffett (Oxy/Chevron): buy a low-cost operator with capital discipline. Dalio: crude regime is the hidden switch.",
        "feedGap": "GRM / segment splits / new-energy progress come from results & research.",
    },
    "utility": {
        "bucket": "Utilities & Power",
        "lens": "Regulated-return + capex-growth — leverage is STRUCTURAL and normal; low FCF in a build-out phase is a feature, not a flaw.",
        "keyMetrics": ["regulated RoE", "PLF / capacity utilization", "capex pipeline (RE transition)", "discom receivables", "debt funding cost", "capacity additions (GW)"],
        "redFlags": ["discom receivable stress", "adverse tariff / regulatory change", "capex without funding visibility", "stranded assets"],
        "deEmphasise": ["D/E & leverage (structural)", "FCF/PAT in capex phase", "EV/EBITDA alone", "capex/CFO"],
        "investorLens": "Dalio: a bond-like, rate-sensitive, policy-driven cash machine. Buffett (BHE): regulated utilities are a place to park capital at steady returns.",
        "feedGap": "Regulated RoE / PLF / receivables come from results, not the price feed.",
    },
    "fmcg": {
        "bucket": "FMCG / Consumer Staples",
        "lens": "A brand + distribution moat — the whole game is volume growth and pricing power; margins swing with input costs.",
        "keyMetrics": ["volume growth (vs value)", "gross margin & input costs", "A&P spend", "market share", "rural vs urban mix", "distribution reach"],
        "redFlags": ["sustained volume decline", "share loss to a new entrant", "input-cost squeeze without pricing power", "premiumisation stalling"],
        "deEmphasise": ["capital intensity", "'richly valued' (quality FMCG always looks expensive)"],
        "investorLens": "Buffett: See's/Coke — durable brand + pricing power + low capital = a compounding machine. Damani: back the consumption trend.",
        "feedGap": "Volume vs price split & market share come from results & calls.",
    },
    "retail": {
        "bucket": "Consumer Discretionary / Retail",
        "lens": "Same-store sales + disciplined store expansion + working-capital/format economics. High inventory can be NORMAL (e.g. jewellery).",
        "keyMetrics": ["SSSG (same-store sales growth)", "store additions", "inventory turns (sector-normal)", "gross margin", "footfall & ticket size", "format profitability"],
        "redFlags": ["SSSG deceleration", "margin pressure", "over-expansion / cannibalisation", "channel shift (online) unaddressed"],
        "deEmphasise": ["high inventory days (normal for jewellery/apparel)", "cash-conversion-cycle alarm", "'richly valued'"],
        "investorLens": "Damani (DMart): low-cost, high-turn, own-your-real-estate discipline. Lynch: the store you can see growing.",
        "feedGap": "SSSG / footfall come from results & calls, not the price feed.",
    },
    "capgoods": {
        "bucket": "Capital Goods / Engineering / Infra / Defence",
        "lens": "Order-book-driven — execution, working-capital lock-up, and government capex are the levers; policy is a primary driver.",
        "keyMetrics": ["order book & book-to-bill", "order inflows", "execution / revenue conversion", "working-capital days", "EBIT margin", "government-receivable risk"],
        "redFlags": ["order-inflow slowdown", "execution delays", "working-capital blowout", "government payment delays", "aggressive low-margin bids"],
        "deEmphasise": ["single-year P/E (lumpy)", "working-capital intensity (project businesses)"],
        "investorLens": "Ride the policy capex cycle (Make-in-India, defence indigenisation, railways) — but demand execution + a clean balance sheet.",
        "feedGap": "Order book & inflows come from results & calls, not the price feed.",
    },
    "auto": {
        "bucket": "Auto & Ancillaries",
        "lens": "Volume cycle × content-per-vehicle × the EV transition — plus raw-material and (for ancillaries) global exposure.",
        "keyMetrics": ["volume growth", "content per vehicle", "order book (ancillaries)", "EV mix & readiness", "raw-material spread", "export/global exposure"],
        "redFlags": ["losing platform/EV content", "demand-cycle downturn", "margin squeeze from commodities", "China/global auto slowdown (ancillaries)"],
        "deEmphasise": ["spot P/E at cycle extremes"],
        "investorLens": "Lynch: understand where content and EV share are going. Dalio: exposed to the global auto cycle.",
        "feedGap": "Content/vehicle & order books come from results & calls.",
    },
    "chemicals": {
        "bucket": "Chemicals",
        "lens": "Specialty vs commodity is everything — specialty = pricing power & stickiness; commodity = China-competition price-taker.",
        "keyMetrics": ["specialty vs commodity mix", "volume & realisation", "capacity & capex", "China oversupply exposure", "customer concentration", "end-market demand"],
        "redFlags": ["China dumping (commodity)", "customer concentration loss", "capex into a glut", "demand destruction in a key end-market"],
        "deEmphasise": ["spot margins in a downcycle"],
        "investorLens": "Munger: the specialty chemical with switching costs is wonderful; the commodity one is a China-priced treadmill.",
        "feedGap": "Specialty mix & end-market demand need research, not just ratios.",
    },
    "buildmat": {
        "bucket": "Building Materials",
        "lens": "Paints/adhesives = distribution moat + pricing; cement = regional capacity, utilization & pricing discipline.",
        "keyMetrics": ["volume growth", "dealer/distribution reach", "gross margin (input costs)", "capacity utilization (cement)", "regional pricing", "new-entrant share (e.g. Birla Opus)"],
        "redFlags": ["share loss to a well-funded new entrant", "pricing indiscipline (cement)", "input-cost squeeze", "demand slowdown (housing)"],
        "deEmphasise": ["'richly valued' (category leaders trade rich)"],
        "investorLens": "Buffett: a distribution moat competitors spend decades failing to cross is the real asset — but watch a deep-pocketed entrant.",
        "feedGap": "Volume/market-share & competitive dynamics come from results & channel checks.",
    },
    "logistics": {
        "bucket": "Logistics / Ports / Shipping",
        "lens": "Throughput × concession economics × the trade cycle; ports are quasi-infrastructure annuities, shipping is deeply cyclical.",
        "keyMetrics": ["cargo/throughput volume", "concession terms & tariffs", "trade-corridor exposure", "fleet/utilisation (shipping)", "freight-rate cycle (shipping)"],
        "redFlags": ["trade slowdown", "concession/regulatory change", "freight-rate collapse (shipping)", "customer concentration"],
        "deEmphasise": ["spot P/E (shipping cyclicality)"],
        "investorLens": "Ports: an infrastructure toll-road on trade (policy tailwind). Shipping: a cyclical — respect the freight cycle.",
        "feedGap": "Volumes & concession details come from results.",
    },
    "diversified": {
        "bucket": "Diversified / Holding Co.",
        "lens": "Value by sum-of-the-parts, apply a holdco discount, and scrutinise capital allocation & group governance.",
        "keyMetrics": ["SOTP of subsidiaries", "holdco discount", "capital-allocation track record", "group leverage & cross-holdings", "governance & related-party exposure"],
        "redFlags": ["value-destructive empire-building", "opaque related-party / group structure", "rising group leverage", "minority-unfriendly actions"],
        "deEmphasise": ["consolidated P/E (mixes unlike businesses)"],
        "investorLens": "Munger: complexity is a red flag; I like a business I can explain in a sentence. Value the parts, distrust the conglomerate premium.",
        "feedGap": "SOTP & subsidiary detail need consolidated-vs-standalone analysis.",
    },
    "realty": {
        "bucket": "Real Estate",
        "lens": "Value on NAV + pre-sales momentum; leverage and inventory are the cycle risks.",
        "keyMetrics": ["pre-sales / bookings", "NAV", "net debt", "inventory & unsold stock", "collections & cash flow", "new launches"],
        "redFlags": ["leverage + slowing pre-sales", "unsold inventory pile-up", "execution/approval delays"],
        "deEmphasise": ["P/E (lumpy revenue recognition)", "EBITDA margin"],
        "investorLens": "Graham: NAV with a survivable balance sheet. Cycle-aware: real estate is a leverage-and-liquidity game.",
        "feedGap": "Pre-sales & NAV come from results & disclosures.",
    },
    "telecom": {
        "bucket": "Telecom",
        "lens": "ARPU × subscribers, against heavy spectrum/capex obligations and leverage — a pricing-and-consolidation game.",
        "keyMetrics": ["ARPU", "subscriber mix & churn", "capex / subscriber", "spectrum obligations & AGR dues", "EBITDA & FCF", "net debt"],
        "redFlags": ["ARPU stagnation / price war", "spectrum & AGR liabilities vs cash flow", "unsustainable leverage", "negative net worth"],
        "deEmphasise": ["P/E (often loss-making)", "book value"],
        "investorLens": "Dalio: a regulated, leverage-heavy oligopoly — the regime is tariff + spectrum policy. Munger: avoid the one whose balance sheet can't survive the capex.",
        "feedGap": "ARPU / spectrum dues come from results & filings.",
    },
    "hospitals": {
        "bucket": "Hospitals",
        "lens": "Occupancy × ARPOB × bed additions — a capacity-and-clinical-quality business with regulatory exposure.",
        "keyMetrics": ["occupancy", "ARPOB (avg revenue/occupied bed)", "revenue & EBITDA per bed", "bed additions", "payer mix", "case mix"],
        "redFlags": ["over-expansion ahead of demand", "clinical/regulatory issues", "margin dilution from new beds", "payer-mix deterioration"],
        "deEmphasise": ["'richly valued' (quality hospital chains trade rich)"],
        "investorLens": "Buffett: a local-density network with pricing power compounds; watch capital discipline on expansion.",
        "feedGap": "Occupancy / ARPOB come from results.",
    },
    "hotels": {
        "bucket": "Hotels",
        "lens": "RevPAR (occupancy × ADR) and operating leverage through the travel cycle — asset-heavy, cyclical.",
        "keyMetrics": ["occupancy", "ADR (avg daily rate)", "RevPAR", "room additions (owned vs managed)", "FCF", "net debt"],
        "redFlags": ["down-cycle demand", "over-leverage into a downturn", "supply glut in key markets"],
        "deEmphasise": ["spot P/E (cyclical earnings)"],
        "investorLens": "Lynch: a cyclical — buy the quality operator in the down-cycle. Asset-light (managed) contracts are the higher-quality model.",
        "feedGap": "RevPAR / ADR / occupancy come from results.",
    },
    "exchanges": {
        "bucket": "Exchanges / AMCs / Capital-markets",
        "lens": "Volumes or AUM × take-rate, with enormous operating leverage and a regulatory moat — capital-light compounders, disruption-sensitive.",
        "keyMetrics": ["volumes / AUM growth", "take rate / yield", "revenue mix", "operating leverage & margin", "ROIC", "cash generation"],
        "redFlags": ["regulatory fee/yield cuts", "competitive disruption (passive, discount brokers)", "volume dependence"],
        "deEmphasise": ["capital intensity (they're capital-light)"],
        "investorLens": "Buffett/Munger: a toll-booth with a regulatory moat and near-zero capital needs — wonderful, if the yield holds.",
        "feedGap": "Yields / AUM flows come from results & regulator data.",
    },
    "generic": {
        "bucket": "General",
        "lens": "Standard quality-compounder lens: durable moat, high & rising ROIC, owner earnings, honest capital allocation, a price with some margin of safety.",
        "keyMetrics": ["revenue & earnings growth", "ROIC vs WACC", "FCF conversion", "net debt", "margins", "reinvestment runway"],
        "redFlags": ["ROIC falling below WACC structurally", "accounting/forensic red flags", "value-destructive capital allocation", "balance-sheet stress"],
        "deEmphasise": [],
        "investorLens": "Buffett/Munger: a wonderful business at a fair price, held for the long term.",
        "feedGap": "Qualitative moat & management quality come from research.",
    },
}

# keyword -> bucket (checked against sector text + company name; order matters, first hit wins)
_RULES = [
    (r"\bbank\b|hdfc bank|icici bank|axis bank|kotak.*bank|sbin|state bank", "banks"),
    (r"insural|life insurance|sbilife|hdfclife|general insurance|insurance", "insurance"),
    (r"exchange|asset management|\bamc\b|hdfc amc|uti amc|nippon life|\bmcx\b|\bcams\b|kfin|angel one|central depository|cdsl", "exchanges"),
    (r"hotel|resort|indian hotels|itchotels|itc hotels|lemon tree|chalet|hospitality", "hotels"),
    (r"hospital|apollo hosp|max health|fortis|narayana|healthcare deliver|diagnostic", "hospitals"),
    (r"telecom|bharti airtel|vodafone|idea cell|ttml|tata teleservices|indus tower", "telecom"),
    (r"nbfc|financ|fin services|pfc|hudco|irfc|jiofin|bajfinance|bajaj fin|shriram|muthoot|chola|l&tf|ltf\b", "nbfc"),
    (r"software|infotech|technolog|\bit\b|wipro|infosys|tcs|hcl|persistent|mphasis|ltim|coforge", "it"),
    (r"pharma|healthcare|life scien|laborator|biocon|cipla|divis|laurus|zydus|sun pharma|drug|medical|polymed|viyash", "pharma"),
    (r"steel|metal|mining|aluminium|hindalco|coal|vedanta|jindal|nmdc|sail", "metals"),
    (r"oil|gas|petroleum|energy.*(oil|gas)|reliance|ongc|gail|bpcl|ioc|refiner", "energy"),
    (r"power|utilit|electric|ntpc|nhpc|tatapower|adanien|adaniensol|powergrid|torrent power|jsw energy", "utility"),
    (r"fmcg|consumer.*(staple|defensive)|household|personal care|itc\b|marico|dabur|nestle|hindustan unilever|colgate|britannia|godrej cons|tata consum|balrampur|sugar", "fmcg"),
    (r"retail|jewel|titan|dmart|avenue super|trent|footwear|apparel|redington", "retail"),
    (r"capital goods|engineer|infrastructure|defence|defense|construction|larsen|\blt\b|polycab|grindwell|supreme|rvnl|siemens|abb|bhel|cummins|railway", "capgoods"),
    (r"auto|automobile|vehicle|motherson|msumi|maruti|tata motors|eicher|tvs|bajaj auto|hero|bosch|ancillary", "auto"),
    (r"chemical|balamines|pidilite|srf|pi indus|hikal|upl|deepak|aarti|epl\b|packaging", "chemicals"),
    (r"paint|cement|building material|asian paint|ultratech|ambuja|acc|berger|grasim", "buildmat"),
    (r"telecom|bharti airtel|vodafone|idea|ttml|tata teleservices|indus tower", "telecom"),
    (r"hospital|apollo hosp|max health|fortis|narayana|healthcare deliver", "hospitals"),
    (r"hotel|resort|indian hotels|itchotels|itc hotels|lemon tree|chalet|hospitality", "hotels"),
    (r"exchange|\bamc\b|asset management|\bbse\b|\bnse\b|mcx|cams|kfin|angel one|nippon life|hdfc amc|uti amc|central depository|cdsl", "exchanges"),
    (r"logistic|port|shipping|adaniports|\bsci\b|container|blue dart", "logistics"),
    (r"real estate|realty|dlf|oberoi|godrej prop|prestige|lodha", "realty"),
    (r"diversified|holding|conglomerate|adanient|grasim|bajaj holding", "diversified"),
]

import re as _re


def profile(sector_text, name=""):
    blob = f"{sector_text or ''} {name or ''}".lower()
    for pat, key in _RULES:
        if _re.search(pat, blob):
            p = dict(SECTORS[key])
            p["key"] = key
            return p
    p = dict(SECTORS["generic"])
    p["key"] = "generic"
    return p
