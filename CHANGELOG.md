# Changelog

All notable changes to the Equity Dashboard. Reference the latest version here before starting any enhancement, so you build on what exists rather than re-deriving it.

Format: this project uses simple dated, semantic-ish versions. Newest first.

---

## [1.1.1] — 2026-08-20 — Resilient data fetch

- `resolve_ticker` now **retries with a short backoff** (3 attempts) when Yahoo
  returns an empty frame under rate-limiting — a transient blip no longer looks
  like "no such stock".
- On failure the API returns **HTTP 503 with a clear "temporary hiccup, try again
  in a few seconds" message** (was a misleading 404 "check the symbol").
- The frontend surfaces the backend's honest message instead of a bare "HTTP 404"
  and flags transient failures for retry.

---

## [1.1.0] — 2026-08-18 — Public-repo polish

Docs & repo hygiene only — no functional changes to the app.

- README: badges row, hero image, and a 6-panel visual feature tour.
- Added `docs/screenshots/` (drop in `01-hero.png` … `07-forensic-tabs.png`).
- Issue templates: Bug report · Feature request · Feedback on a company's read.
- Blank-issue disabled with contact links to `docs/ARCHITECTURE.md` and `CHANGELOG.md`.
- `CONTRIBUTING.md` — how to help, house rules, and a reminder to keep personal data out.
- `docs/POSTS.md` — draft launch posts for Reddit / Hacker News / LinkedIn / X.

---

## [1.0.0] — 2026-08-20 — First complete, working version

The initial full build. Everything below is live and verified in-browser.

### Core dashboard
- Single-company view: live NSE/BSE price, exchange, market cap, P/E, P/B, dividend yield, 52-week range.
- Cash & capital: operating cash flow, capex, FCF, cash balance; sources/uses of cash; capex-vs-OCF and cash-balance/FCF 5-year trends.
- Working-capital cycle: DSO / DIO / DPO / cash-conversion-cycle trend (Screener day-ratio fallback).
- Quarterly performance: last ~8 quarters — revenue, EBITDA, interest, net profit, margins, QoQ; auto gap-fill from Screener when Yahoo omits a quarter.
- **Live typeahead search** across all NSE/BSE names via Yahoo search (works from any IP), with curated-list fallback; keyboard navigation; reflects renames/demergers so it never suggests a dead ticker.

### Valuation engine (framework-aligned, audited 20/20 vs the Excel bands)
- Through-cycle **normalisation** of earnings (trough/peak detection; Screener deep annual history, recent-window capped).
- **Sector-appropriate multiples anchored to the firm's own forward multiple**, disciplined by a per-bucket P/E band.
- Method by type: financials → best-of P/B + normalised EPS + ROE-scaled book, market-clamped; cyclicals → mid-cycle EV/EBITDA; holdcos → −20% discount; others → normalised earnings power.
- **Scenario band** (bear/base/bull), **MoS buy band**, **action price bands**, **reverse-DCF** expectation test.
- Verdict philosophy: valuation richness is never an outright sell; cyclicals/financials never trim on valuation.

### Dynamic framework read
- Live `frameworkRead` per stock — verdict · conviction 1–5 · basis · long-term qualification · MoS buy band · plain-language buy note — recomputed each quarter. Verdict does **not** go Exit from the forensic screen (confirmed red flags come from research).

### Forensic engine
- ~40 diagnostic ratios in 7 categories, each good/watch/bad/na with a plain-language read; a **screen, not a verdict**.
- India-governance items surfaced as "check filings" (never fabricated); Screener back-fills net-debt / invested-capital / working-capital gaps.

### Bank / NBFC / FI module
- `bankView`: Gross/Net NPA (standalone Screener, dated), deposits, NII, interest income/expense, fee-income share, RoA, RoE, NIM (est.), cost of funds (est.), NII-YoY, 8-quarter series.
- Bank-specific **Key Ratios** (replaces the industrial set); bank-aware **quarterly** table/panel (NII/NIM/NPA instead of EBITDA).
- Filings-only metrics (exact NIM, CASA, PCR, CET1, slippage) honestly flagged.

### Decision scorecard, scenarios, confidence
- 100-point decision scorecard, HIGH/MEDIUM/LOW confidence, base/bull/bear/severe scenarios; the three proxy rows are fed by the research overlay when present.

### Investor committee (personas)
- Buffett · Munger · Graham · Lynch · Dalio · Institutional-Risk lenses, each with a **stock-specific** read. Dalio and Institutional-Risk give position-*sizing* calls that vary by leverage/cyclicality/quality (not fixed labels).

### Shareholding & corporate data
- Shareholding pattern (promoter / FII / DII / retail) + promoter pledge from NSE SEBI XBRL; institutional QoQ change; promoter-holding trend (with clean "no promoter" handling).
- Corporate calendar & disclosures: corporate actions (deduped) + recent announcements **hyperlinked to the NSE filing PDF**.

### Equity Holdings tab
- Upload Zerodha CSV → match to the audited framework Excel → per-holding verdict, conviction, **MoS buy band + buy note** (audited **and** live framework read).
- Refresh (live quant) + Research (news/policy overlay) → synthesised final verdict; "⚡ Material issue" filter for genuine quant-vs-research contradictions.
- Persistence via `holdings_state.json`; Excel export of the consolidated reading.
- `framework.py` auto-locates the newest `*Consolidated_Master*.xlsx`, parses the new `Portfolio_Action_ALL` + `Valuation_ALL` schema (old schema fallback), tolerates the file being open in Excel.

### Robustness
- NaN-safe JSON (`_json_safe`) so one bad number can't break a response; price uses the last valid close with fallbacks.
- Move/rename-safe (all data files anchored to the script folder; `run.bat` uses `%~dp0`).
- `PYTHONIOENCODING=utf-8` set in `run.bat` (Windows console).

### Documentation & repo
- README, docs/ARCHITECTURE.md (technical), docs/FRAMEWORK.md (methodology), this CHANGELOG.
- `.gitignore` keeps personal data (`holdings_state.json`, `research_overlay.json`, `research_archive/`) out of git; `holdings_state.example.json` documents the shape.

---

## How to version future work

- **Patch** (1.0.**x**): bug fixes, small tweaks, calibration.
- **Minor** (1.**x**.0): a new feature or module that doesn't break existing behaviour.
- **Major** (**x**.0.0): a change that reworks how something fundamental behaves (e.g. a new valuation methodology).

For each release: add a dated section at the top of this file, list what changed by area, and note anything that needs re-testing. Then commit with a message like `v1.1.0: <summary>` and, optionally, tag it (`git tag v1.1.0`).
