# Architecture & Technical Know-How

How the Equity Dashboard is built, end to end. Read this before making changes so you understand *why* each piece works the way it does.

---

## 1. High-level shape

```
                    ┌─────────────────────────────┐
   Browser  ◄──────►│  equity-dashboard.html      │   single self-contained file
                    │  (UI + SVG charts + JS)     │   no build step, no frameworks
                    └──────────────┬──────────────┘
                                   │  fetch() JSON over HTTP
                    ┌──────────────▼──────────────┐
                    │  server.py  (Flask, :5000)  │   the analytical engine
                    │  build_company() etc.       │
                    └───┬─────────┬────────┬──────┘
                        │         │        │
              ┌─────────▼──┐  ┌───▼────┐  ┌▼──────────────┐
              │ yfinance   │  │ nse.py │  │ screener_web  │
              │ (Yahoo)    │  │ (NSE)  │  │ (Screener.in) │
              └────────────┘  └────────┘  └───────────────┘
```

- **One Flask process**, `threaded=True`, on `127.0.0.1:5000`.
- The frontend is **one HTML file** served at `/`. All rendering is client-side JavaScript; charts are hand-drawn SVG (no chart library). This keeps the whole UI in a single file with zero build tooling.
- All heavy logic lives in **`server.py`** and the data-client modules.

---

## 2. File-by-file

| File | Responsibility |
|---|---|
| **`server.py`** (~1600 lines) | Flask app + the engine. `build_company(sym)` assembles the entire per-stock payload: price, cash flows, working capital, quarters, **valuation**, **forensic ratios**, debt, **bank view**, **framework read**, scorecard, scenarios, personas, sector lens. Also serves `/api/search`, `/api/holdings`, `/api/framework`, `/api/research`, `/api/export`. |
| **`equity-dashboard.html`** (~1760 lines) | The UI. `renderCompany(c)` paints the single-stock dashboard; the Equity Holdings view has its own render/refresh/persist logic. `computeLive`, `materialDivergence`, `effVerdict`, `renderScorecard`, `renderBankView`, `renderDetail`, etc. |
| **`nse.py`** | NSE India client — price bundle, shareholding pattern (SEBI XBRL), promoter pledge, corporate actions/announcements. Uses a warmed `curl_cffi` session. |
| **`screener_web.py`** | Screener.in scraper. `fetch_quarterly` (13 quarters incl. bank NII/NPA), `fetch_financials` (deep annual history + balance-sheet/ratio fallbacks + deposits), `fetch_bank_npa` (standalone Gross/Net NPA). |
| **`screener.py`** | Parser for a **manually** exported Screener Excel (the "Data Sheet" quarters section). Used by the optional per-stock Excel upload. |
| **`sectors.py`** | The sector knowledge base — 22 buckets, each with `lens · keyMetrics · redFlags · deEmphasise · investorLens · feedGap`. `profile(sector_text, name)` classifies a company. |
| **`framework.py`** | Reads the investor's **audited-portfolio Excel** into JSON by symbol. Auto-locates the newest `*Consolidated_Master*.xlsx`; parses `Portfolio_Action_ALL` + `Valuation_ALL` (new schema) or `Verdict_Action` + `Valuation` (old). |

---

## 3. Data sources & their hard-won quirks

These findings cost real debugging time — respect them.

### Yahoo Finance (`yfinance`)
- Works from any IP; carries price + full cash-flow / balance-sheet / income statements + quarterly.
- **Free tier often omits the latest quarter** for Indian tickers → we build a consecutive series and gap-fill from Screener.
- **Can return a NaN for the latest (still-forming) price bar.** We take the last *valid* close and fall back to `fast_info`/`info`. A global `_json_safe()` also converts any stray NaN/Inf to `null` so one bad number can't break the whole JSON response.
- Statements are in **raw ₹** (not ₹ Crore). Screener values are in **₹ Cr**. Mixing them silently produces 10-million-fold errors — always convert (`/1e7`).

### NSE India (`nse.py`)
- JSON APIs block by **TLS fingerprint AND IP reputation**. `curl_cffi` with `impersonate="chrome"` defeats the TLS check, but **data-center IPs still get 403** — works from a residential IP.
- Shareholding split (promoter / FII / DII / retail) is parsed from the SEBI **`in-bse-shp` XBRL**; results from **`in-bse-fin`**.
- The public results feed lags (nothing newer than ~Dec-2024 from some environments), so quarter gap-fill relies on Screener, not NSE.

### Screener.in (`screener_web.py`)
- Company pages are **public, no login**, server-rendered. Carry ~12–13 consecutive quarters and 10+ years of annual data.
- **Bank asset quality (Gross/Net NPA %) is on the STANDALONE page**, not the consolidated one (`fetch_bank_npa` fetches standalone). Consolidated omits it.
- Quarterly NPA on Screener can **lag 1–2 quarters** (latest columns blank) → we take the last non-blank value and label its quarter.
- Screener's "Financing Margin %" for banks is **negative** (it nets provisions) — it is *not* NIM and is deliberately not used as one.
- Numbers carry `%`, commas, `&nbsp;` — the parser strips all of these.

---

## 4. The valuation engine (the core, in `build_company`)

This is the most important and most iterated piece. It follows the "no single hammer" rule from the value framework.

### 4.1 Through-cycle normalisation
Valuing a *trough* year on trailing numbers is the classic error (e.g. Praj: latest NI ₹24 Cr vs ~₹250 Cr normal → trailing P/E 204×). So:
- Build a recent-window earnings series (prefers Screener's deep annual `npHist`, capped to ~6 years so a *growth* company isn't dragged down by tiny old years).
- If trailing NI is a clear **trough** (`< 0.6 ×` median, revenue intact) or **peak** (`> 1.6 ×`), value on the **mid-cycle** (median) earnings, not spot.

### 4.2 Sector-appropriate, market-anchored multiples
- `_PE_BANDS` gives a (low, base, high) P/E per sector bucket.
- But the fair multiple is **anchored to the firm's own forward multiple** (`price / forwardEps`), disciplined by the sector band — so IV never diverges wildly from what the market actually pays. This was the fix that stopped the model from mis-valuing premium names (DMART) and hybrids (ITC).

### 4.3 Method by business type
- **Financials** → best-of {justified P/B, normalised EPS × 12–18, ROE-scaled book}, then **clamped to 0.80–1.15 × price**. A generic model cannot out-value a lender, so it flags only clear gaps and otherwise defers to the market (reproducing the framework's near-universal HOLD-add for banks).
- **Commodity / regulated cyclicals** (metals, energy, utilities, realty) → mid-cycle **EV/EBITDA** at the firm's own multiple, minus net debt.
- **Holding companies** → a −20% conglomerate discount.
- **Everything else** (compounders, capital goods, pharma, auto, chemicals) → normalised earnings power.

### 4.4 Outputs
- **Scenario band**: bear / base / bull IV.
- **MoS buy band**: ~10–15% below fair (`accumulate → fairLow`).
- **Action price bands & zone**: STRONG ADD / ACCUMULATE / HOLD (fair) / HOLD (rich) / Expensive. Valuation richness is **never** an outright sell — a rich quality name is "hold, don't add"; cyclicals & financials never emit a valuation-trim (the framework's "don't trim into a cyclical upturn").
- **Reverse-DCF** expectation test: solves for the FCF growth the price implies → Conservative / Reasonable / Demanding / Unrealistic.

> **Audit target:** the model is validated to match the framework Excel's `Valuation_ALL` **verdict distribution** (all HOLD/accumulate, no false TRIMs) — not exact rupee IVs. It passed 20/20 on the tested basket.

---

## 5. The dynamic framework read

`build_company` emits `frameworkRead` — the framework's structured record, **recomputed live** (so it updates each quarter):
- **verdict** (Add/Accumulate/Hold from the price-band zone),
- **conviction 1–5** (mapped from the 100-pt scorecard — *not* the raw forensic bad-count, which over-fires),
- **basis** (DD-live / P-live),
- **long-term qualification** (YES / YES-cyclical / YES-watch / CONDITIONAL, from through-cycle ROE & sector),
- **MoS buy band** and a plain-language **buy note**.

Key discipline: the live read never goes to Exit from the forensic *screen*. A **confirmed** red flag (fraud, audit qualification, warning letter) is a research/news finding — the two-agent model below.

---

## 6. The forensic engine (`build_forensic`)

~40 diagnostic ratios in 7 categories (Earnings Quality, Working-Capital Forensics, Capital Efficiency, Debt & Stress, Hidden Balance-Sheet Risk, Management Behaviour, India Governance). Each is tagged good / watch / bad / na with a plain-language interpretation.

- It is a **screen, not a verdict.** Several ratios read "bad" for perfectly healthy companies (capex-phase FCF, structural utility leverage). So a bad-ratio count is *never* used to trigger a sell.
- India-governance items (promoter pledge, RPTs, contingent liabilities, auditor qualifications, subsidiary drag, promoter remuneration) are **not in any price feed** → surfaced as "check filings", never fabricated.
- Screener's stated numbers back-fill gaps (net debt, invested capital → ROIC, working-capital day-ratios) with a "· via Screener" tag.

---

## 7. The bank / NBFC / FI module

Lenders need a different engine (EBITDA, current ratio, inventory days are meaningless).

- `bankView` (only for financials) carries: Gross/Net NPA (+ as-of quarter), deposits, interest income, interest expense, **NII**, fee-income share, RoA, RoE, **NIM (est.)** = annualised NII ÷ total assets, **cost of funds (est.)**, NII-YoY, and an 8-quarter series.
- The **Key Ratios** card is *replaced* with a bank set for financials (RoA, RoE, NIM, CoF, GNPA, NNPA, fee %, NII growth, P/B, book value, P/E, div yield).
- The **quarterly** table/panel are bank-aware: NII · NII% · Gross NPA · Net NPA · Net Profit instead of EBITDA columns.
- Metrics that require the filing (exact NIM on earning assets, CASA, PCR, CET1, slippage) are honestly flagged, not invented.

---

## 8. Two-agent architecture (quant + research)

The app is the **quant agent** (numbers, valuation, forensic screen — runs on every Refresh). It cannot run an LLM. The **research agent** is Claude with web search, which writes `research_overlay.json` (per-symbol revised verdict + policy/news context). The 🔬 Research button loads it and the final verdict = synthesis:

```
effVerdict(h) = research-revised verdict (qual + policy + news)  IF present
              → else the live quant verdict
              → else the dated Excel verdict
```

Example: HIKAL quant read = TRIM, but the confirmed fraud disclosure (research) overrides to EXIT — the numbers alone can't see the news.

---

## 9. The Equity Holdings tab

- Upload a **Zerodha holdings CSV** → parsed in-browser (flexible header detection).
- Each holding is matched by symbol to the **audited framework Excel** (`framework.py` → `/api/framework`) → dated verdict, MoS buy band, buy note.
- **Refresh** fetches `/api/company` per holding (concurrency 4) → the live quant read + `frameworkRead`.
- **Research** loads the overlay → synthesised final call + a "⚡ Material issue" filter for genuine quant-vs-research contradictions.
- Persisted to **`holdings_state.json`** via `/api/holdings` (GET/POST) so reopening restores the last saved portfolio.

---

## 10. API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /` | serves `equity-dashboard.html` (anchored to the script's own folder — move/rename-safe) |
| `GET /api/search?q=` | typeahead across NSE/BSE via Yahoo search (works from any IP), curated-list fallback |
| `GET /api/company/<sym>` | the full per-stock payload (everything above), NaN-sanitised |
| `GET/POST /api/holdings` | restore / persist the holdings portfolio (`holdings_state.json`) |
| `GET /api/framework` | the audited-portfolio Excel parsed by symbol (auto-locates newest master) |
| `GET /api/research` | the research/policy overlay (auto-archived per date) |
| `POST /api/screener` | parse an uploaded Screener Excel → quarterly series |
| `POST /api/export` | build an `.xlsx` of the consolidated holdings reading |

---

## 11. Portability & known limitations

- **Move/rename-safe:** all data files are read relative to `server.py` (`os.path.abspath(__file__)`), and `run.bat` uses `%~dp0`. The one external path is `framework.py`'s pointer to the audited Excel (override with `EQUITY_FRAMEWORK_XLSX`).
- **Residential IP needed** for live NSE data; otherwise Yahoo + Screener carry the load.
- **Valuation is a coarse model**, not a human analyst — it matches verdict *direction*, not exact rupee IVs; a few premium franchises (ADANIPORTS, DMART) get a conservative base IV (verdict still HOLD). The audited Excel remains authoritative for holdings.
- **Console encoding:** set `PYTHONIOENCODING=utf-8` (run.bat does) or Windows cp1252 chokes on ₹ / × / − in output.

See **[FRAMEWORK.md](FRAMEWORK.md)** for the investing methodology and **[../CHANGELOG.md](../CHANGELOG.md)** for the build history.
