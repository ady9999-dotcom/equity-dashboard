# The Investing Framework (Functional Methodology)

This is the *investing* thinking the dashboard implements — the "why" behind every verdict. It is the software realisation of two source documents:

- **Portfolio_Framework.docx** — the value-investing audit & action framework (the master methodology).
- **Banks_NBFC_Ratios.docx** — the financial-institution ratio library and valuation rules.

> **Not investment advice.** This describes an analytical process. Every output is decision-support only; a human decides and executes.

---

## 1. Philosophy

A **long-horizon (10-year+) value framework** for a concentrated portfolio. It privileges four primary decision drivers and de-weights price momentum to a *timing* input only:

1. **Intrinsic value & margin of safety**
2. **Operating performance**
3. **Forward guidance**
4. **Government policy / macro tailwinds**

Core promise, per holding: (a) does this business deserve a decade of ownership? (b) what is it worth, and where is the margin of safety? (c) at today's price, policy and filed results — buy more, hold, trim, or exit? It refuses to answer from memory, sentiment, or price action alone.

Two non-negotiables the software honours:
- **No fabrication.** If filed data is unavailable, say so (e.g. "check filings") — never invent a number.
- **Audit before publish.** Surprising outputs are cross-checked and rectified before they're shown (the valuation engine was re-audited three times against the Excel bands before shipping).

---

## 2. The four-lens investor committee

Every stock is read through four documented reasoning frames — as lenses, not impersonations. Tension is preserved, not averaged.

| Lens | Question it forces | Output |
|---|---|---|
| **Graham** | Where is the margin of safety? Downside if wrong? | Conservative value; refuses to buy above the MoS band |
| **Buffett** | Durable moat? Owner-earnings, ROIC vs WACC? | Quality verdict; great business ≠ great price |
| **Munger** | Invert — what would destroy this? Bad incentives? | Failure-mode / value-trap catalogue |
| **Dalio** | What macro/policy regime? Which way do the winds blow? | Regime map + **position-sizing** call |

The dashboard adds two more practical lenses:
- **Lynch** — growth at a reasonable price, a story you can explain.
- **Institutional Risk** — position construction (Vanguard/BlackRock/Blackstone tradition): a **weight** call driven by leverage, cyclicality and factor-correlation.

> Dalio and Institutional-Risk give **sizing/weight** calls (how *big* a position), not buy/sell. "Underweight" or "Cap the weight" means *reduce toward a risk-appropriate size if oversized or correlated* — not exit.

---

## 3. Sector-appropriate valuation (the "no single hammer" rule)

Using the wrong metric produces dangerous verdicts. The engine enforces:

| Business type | Correct method | Never do |
|---|---|---|
| **Banks / NBFCs / FIs** | Price-to-(adjusted)-book, RoE-driven; assess on NIM, GNPA/NNPA, credit cost, RoA, capital adequacy | EV/EBITDA or current ratio |
| **Cyclicals** (metals, commodities, upstream energy) | **Mid-cycle** (normalised) earnings; through-cycle EV/EBITDA | Capitalise *peak* earnings |
| **Compounders / consumer / quality** | Normalised P/E + reverse-DCF sanity + owner-earnings | Ignore that price can ruin a great business |
| **Holding companies** | Sum-of-the-parts + a holdco discount | Take the consolidated P/E at face value |

For every valued stock the framework produces three outputs plus a sanity read:
- **Conservative IV** (bear-case worth, where Graham is comfortable),
- **Fair IV** (base case),
- **Margin-of-Safety Buy Band** (≈10–15% below fair — above it: hold, don't add; below it: accumulate),
- **Reverse-DCF read** — what growth the current price already assumes.

---

## 4. Verdict taxonomy, conviction, basis, long-term qualification

**Verdicts:** Add · Accumulate · Hold · Trim · Reduce · Exit.
- *Add* — deploy now (price in/below the MoS band).
- *Accumulate* — buy in tranches on weakness toward the band.
- *Hold* — keep; don't add above the band, don't sell (the default for a sound business at a full price).
- *Trim / Reduce* — discipline / concentration / weakening thesis (not broken).
- *Exit* — thesis broken, or a **confirmed** forensic / governance red flag.

**Conviction 1–5:** 5 = anchor, highest conviction; 3 = sound but watchful; 1 = must-act / must-exit.

**Basis code (the honesty layer):** DD = full deep-dive · Q# = valued on a filed quarter · FY## = filed annual + structural read · V = action verified vs filings/news · P = provisional structural view · ID = identity unresolved.

**Long-term qualification:** YES · YES (cyclical — qualifies but manage through the cycle) · CONDITIONAL (qualifies only if a stated risk resolves) · NO (fails — exit/trim regardless of price).

The dashboard's **live framework read** computes all of these dynamically each quarter (see ARCHITECTURE §5).

---

## 5. Quality & forensic screens

Balance-sheet strength, cash-flow quality (CFO vs PAT), leverage, promoter pledge, dilution, governance. Beneish / Piotroski / Altman where data allows.

- These are **screens, not verdicts.** A single "bad" ratio is common in healthy businesses and never triggers a sell on its own.
- A **CONFIRMED** forensic red flag — a disclosed revenue-recognition irregularity, a regulatory forensic audit, a USFDA warning letter, an audit qualification — **is a must-sell** that overrides any recovery narrative. These are detected by the **research agent** (news/filings), not the automated ratio screen.

---

## 6. The financial-institution module (banks / NBFCs / FIs)

"When I say banks, I mean banks, NBFCs and financial institutions." A lender is a spread-and-risk business; most industrial ratios are meaningless.

**What matters, in order (from the ratio library):**
1. Asset quality → 2. Provision adequacy → 3. Risk-adjusted yield → 4. Funding franchise → 5. Capital strength → 6. Liquidity/ALM → 7. RoA → 8. Sustainable RoE → 9. Incremental returns → 10. Valuation. *Only then* a verdict.

**Shown in the app** (live from Screener): Gross NPA, Net NPA, RoA, RoE, NIM (est.), cost of funds (est.), deposits (funding base), NII and its growth, fee-income share.

**Valuation:** P/B + residual-income / RoE framework — *never* EV/EBITDA. The key question is turned around: *"what sustainable RoE, growth and cost of equity must be true for this P/B to be justified?"*

**A critical forensic principle:** a *falling* GNPA is **not** proof of improving health — it must be reconciled with slippages, write-offs, restructuring, Stage-2 migration, provisions and capital consumption. The app flags this and shows the metrics it can; the rest (CASA, PCR, CET1, slippage) are marked "check filings".

---

## 7. Policy & macro overlay

Each holding is mapped to the government-policy themes and macro signals that drive it (e.g. ethanol blending, PLI, infrastructure capex, GST changes). **Correlated clusters** — holdings that share one hidden driver (a monsoon, a crude regime, one policy) — are flagged so they're sized as **one bet**, not mistaken for diversification. Indian policy announcements are treated as a primary, strategic, long-term driver.

---

## 8. The mandatory self-audit (before any output)

Seven checks run before anything is published: **consistency · completeness · assumptions · blind-spots · feasibility · scope · non-hallucination.** If any fails, the deficiency is disclosed rather than a polished-but-flawed answer shipped. This is why the valuation engine was iterated and re-audited until it matched the framework's verdict distribution.

---

## 9. How the framework maps to app features

| Framework output | App feature |
|---|---|
| Conservative / Fair / Bull IV | Scenario band (bear/base/bull) |
| MoS Buy Band (10–15% below fair) | Price-band engine (`accumulate` zone) |
| Reverse-DCF read | `iv.expectation` |
| Verdict (Add…Exit) | Price-band zone + holdings `computeLive`, synthesised with research |
| Conviction 1–5 | Mapped from the 100-point scorecard |
| Basis code | DD-live / P-live |
| Long-term qualification | From through-cycle ROE + sector |
| Buy note (plain language) | Generated from the zone |
| Four-lens committee | Personas |
| Quality / forensic screens | Forensic engine (a screen, not a verdict) |
| Policy / macro + clusters | Sector lens + research overlay |
| Bank valuation & ratios | Bank module |

Both layers coexist in the Holdings tab: your **audited Excel** call (human judgment, dated) *and* the **live framework read** (recomputed each quarter). The audited call stays authoritative; the live read shows how the numbers have moved.

---

## 10. Honest limitations

- Not registered advice; decision-support only.
- Quality depends on **live data** — statement prices go stale within days.
- Coverage is phased; until deep-dived, a holding's verdict is a provisional read (basis **P**).
- Forensic scores are often partial (full Beneish/Piotroski/Altman needs data not always public) — confirmed red flags are always acted on.
- Valuation is judgment, not precision; the reverse-DCF shows the assumptions so you can disagree.
- An automated engine can still err — the self-audit and your own review are the mitigations.
