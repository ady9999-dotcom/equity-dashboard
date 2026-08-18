# Equity Dashboard — BSE / NSE

A long-horizon, value-investing analysis dashboard for Indian listed equities (NSE / BSE). It fetches live prices and filed financials, values each company with **sector-appropriate, through-cycle methods**, runs a **forensic-ratio screen**, applies a dedicated **bank / NBFC / FI module**, and reads every stock through a **four-lens investor committee** — then synthesises a Buy / Accumulate / Hold / Trim / Exit call with a margin-of-safety buy band.

It also has an **Equity Holdings** tab that ingests a Zerodha holdings CSV, matches it to your audited framework Excel, and shows both your dated verdict and a **live framework read** that recomputes each quarter as new results are filed.

> **Not investment advice.** Every output is decision-support only, for education. It is not SEBI-registered advice. You make all decisions and bear the outcome.

---

## Quick start

**Requirements:** Windows, Python 3.10+ (tested on 3.14).

1. Double-click **`run.bat`**. It finds Python, installs the libraries on first run, opens your browser, and starts the server.
2. The dashboard opens at **http://127.0.0.1:5000**.
3. Type a company name or ticker (e.g. *Reliance*, *Navin*, *Kotak*) and pick from the live suggestions.

Keep the black console window open while using the app; close it (or Ctrl+C) to stop.

Manual start (if you prefer):

```bash
pip install -r requirements.txt
python server.py
```

---

## What it does

| Area | What you get |
|---|---|
| **Live price & identity** | NSE/BSE price, exchange, market cap, 52-week range, P/E, P/B, dividend yield |
| **Cash & capital** | Operating cash flow, capex, FCF, cash balance; sources/uses of cash; capex-vs-OCF and cash-balance/FCF trends |
| **Working capital** | DSO / DIO / DPO / cash-conversion-cycle trend |
| **Quarterly** | Last ~8 quarters — revenue, EBITDA, interest, net profit, margins, QoQ (lenders show NII / NIM / GNPA / NNPA / RoA instead) |
| **Valuation** | Scenario intrinsic value (bear / base / bull), MoS buy band, reverse-DCF expectation test, action price bands |
| **Forensic screen** | ~40 diagnostic ratios in 7 categories, each tagged good / watch / bad with a plain-language read |
| **Bank / NBFC / FI view** | Gross/Net NPA, RoA, RoE, NIM, cost of funds, deposits, NII, fee-income share — the metrics that actually matter for a lender |
| **Decision scorecard** | 100-point score, confidence level, base/bull/bear/severe scenarios |
| **Investor committee** | Buffett · Munger · Graham · Lynch · Dalio · Institutional-Risk lenses, each with a stock-specific read |
| **Holdings tab** | Upload Zerodha CSV → per-holding verdict, conviction, MoS band, buy note (audited **and** live), synthesised with research/policy |

---

## Tech stack

- **Backend:** Python + Flask (`server.py`), single-process, threaded.
- **Frontend:** one self-contained HTML file (`equity-dashboard.html`) — no build step, self-drawn SVG charts.
- **Data:** Yahoo Finance (`yfinance`) for statements & price; NSE India APIs for corporate data & shareholding; Screener.in (public pages) for deep history, bank asset-quality and gap-fill. `curl_cffi` is used to defeat TLS fingerprinting.

See **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for the full technical build, and **[docs/FRAMEWORK.md](docs/FRAMEWORK.md)** for the investing methodology.

---

## Repository layout

```
server.py                 Flask backend — the analytical engine (valuation, forensic, bank, framework read)
equity-dashboard.html     Frontend — the entire UI + charts
nse.py                    NSE India client (price, shareholding, pledge, corporate calendar)
screener_web.py           Screener.in scraper (deep annual history, bank NPA, quarterly gap-fill)
screener.py               Parser for a manually-exported Screener Excel
sectors.py                Sector knowledge base (22 buckets, each with its own analytical lens)
framework.py              Reads your audited-portfolio Excel (Valuation_ALL / Portfolio_Action_ALL)
requirements.txt          Python dependencies
run.bat                   One-click Windows launcher
START_HERE.txt            Plain-language run instructions
docs/ARCHITECTURE.md      Technical know-how (how it's built)
docs/FRAMEWORK.md         Functional framework (the investing methodology)
CHANGELOG.md              Version history — reference this before enhancing
holdings_state.example.json  Template showing the holdings file shape
```

**Not in the repo (git-ignored, personal):** `holdings_state.json` (your real positions), `research_overlay.json` and `research_archive/` (research keyed to your holdings). The app recreates these locally.

---

## Data-source notes (important)

- **NSE JSON APIs** block by both TLS fingerprint *and* IP reputation. `curl_cffi` defeats the TLS check, but data-center/cloud IPs still get 403 — this works from a **residential IP** (your own PC). The public NSE results feed also lags.
- **Yahoo Finance** works everywhere and carries price + full statements, but its free tier can omit the latest quarter and occasionally returns a NaN for a still-forming price bar (handled).
- **Screener.in** company pages are public (no login) and carry ~12–13 consecutive quarters, deep annual history, and — on the **standalone** page — bank Gross/Net NPA.
- Metrics that live only in a company's results filing (exact NIM, CASA, PCR, CET1, slippage) are shown as **"check filings"** — never fabricated.

---

## License & copyright

**Copyright © 2026 ady ([github.com/ady9999-dotcom](https://github.com/ady9999-dotcom)). All rights reserved.**

Licensed under the **[PolyForm Noncommercial License 1.0.0](LICENSE.md)**.

- ✅ You may **view, run, study, modify and share** this project **for noncommercial purposes** (personal use, research, education, evaluation) — as long as you keep this copyright notice and the licence.
- 🚫 **Commercial use is not permitted** — you may not sell it, offer it as a paid product/service, pitch it commercially, or present it (or a derivative) as your own — **without a separate written licence** from the copyright holder.
- 📩 For commercial licensing, contact the copyright holder via the GitHub profile above.

Feedback and non-commercial experimentation are welcome — please open an issue.

> **Reminder:** this is decision-support software, provided **as-is with no warranty** (see the licence). It is **not investment advice**. Nothing here is a recommendation to buy or sell any security; you make all decisions and bear the outcome.
