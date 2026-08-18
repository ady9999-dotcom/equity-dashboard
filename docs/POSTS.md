# Launch posts — copy, tune, paste

Tuned for each platform. Attach the hero screenshot (`docs/screenshots/01-hero.png`) wherever possible — it 5–10× the click-through.

**One golden rule everywhere:** don't ask for stars, ask for **feedback on a specific thing**. Stars come as a byproduct.

---

## 1) Reddit — r/IndianStockMarket

**Title:**
`I built a value-investing dashboard for BSE/NSE stocks — would love your feedback on the reads`

**Body:**
> Been building this for a few months as a personal project — a dashboard that pulls live prices + filed financials and runs sector-appropriate valuation (not "one hammer" DCF for everything), a forensic ratio screen, a proper bank/NBFC view, and a 4-lens investor committee (Buffett/Munger/Graham/Lynch/Dalio).
>
> It's now open on GitHub for anyone to try — noncommercial licence, private-data-safe (holdings never leave your PC).
>
> **What I'd genuinely like feedback on:** *do the reads match what you'd say?* I've calibrated the valuation engine against my own audited framework and it currently agrees on ~20/20 names I tested (Praj → Hold, Kotak → Hold-add, Hindalco → Hold, ITC → Accumulate, etc.), but I'd love you to try 2–3 stocks *you* know well and tell me where it's off.
>
> 🔗 https://github.com/ady9999-dotcom/equity-dashboard
> Runs on Windows, `run.bat` handles the setup. Not investment advice, obviously — decision-support only.
>
> Happy to answer any "why does it value X this way?" question — the methodology is in `docs/FRAMEWORK.md`.

**Best posting time:** weekend morning IST, or a weekday evening (post-market). Not during market hours.

**Other subreddits (tune the ask):**
- **r/IndiaInvestments** — *read the self-promo rules first.* Lead with "I built this and want feedback"; do **not** lead with the repo link. This sub is strict.
- **r/StockMarketIndia** — same body, shorter.
- **r/algotrading** — reframe: *"open-source Python engine for Indian equity fundamentals (Screener/Yahoo/NSE) — sector-aware valuation, bank NPA parsing, forensic ratios. Not for trading — for long-horizon selection. Feedback / issues welcome."*

**Don't** post to more than 2 subs in the same 24 hours — it flags as spam.

---

## 2) Hacker News — Show HN

**Title (very important — keep it short and specific):**
`Show HN: Value-investing dashboard for Indian equities (Python + one HTML file)`

**Body (kept under 500 characters — HN prefers minimal):**
> Personal project I built to audit my own Indian-equity holdings. Pulls live NSE/BSE data (Yahoo + Screener + NSE APIs via curl_cffi), values each stock with sector-appropriate methods (P/B for lenders, mid-cycle EV/EBITDA for cyclicals, normalised P/E for compounders, market-anchored), a forensic-ratio screen, and a dedicated bank/NBFC/FI module. Frontend is one self-contained HTML file, no build.
>
> Would love feedback on the valuation reads. Repo: https://github.com/ady9999-dotcom/equity-dashboard

**When to post:** a Tuesday, Wednesday or Thursday, 7–9am US Eastern (5:30–7:30pm IST). Post once — do NOT repost.

**Prep before posting:** be ready to answer questions in-thread for 3–4 hours. HN engagement dies fast if the author doesn't respond.

---

## 3) LinkedIn

Two versions — a longer "project post" and a shorter "in-passing" one.

### 3a) Full post (use once, when you launch)

```
I've been building this in evenings and weekends for a few months, and I've finally put it up.

It's a value-investing analysis dashboard for Indian equities (BSE / NSE) — the kind of tool I wanted for auditing my own long-horizon portfolio.

What it does:
📊 Live price + filed financials for any NSE/BSE company
💰 Sector-appropriate valuation (P/B for banks, mid-cycle for cyclicals, normalised for compounders — no "one hammer" DCF)
🔍 40+ diagnostic forensic ratios, tagged good/watch/concern
🏦 A dedicated bank/NBFC view (NIM, GNPA, cost of funds, deposits — not EBITDA)
🧠 A four-lens investor committee: Buffett · Munger · Graham · Lynch · Dalio
📈 A 100-point decision scorecard with bear/base/bull scenarios
📂 Uploads your Zerodha CSV → per-holding verdict + MoS buy band + buy note

Built with Python + one self-contained HTML file. No build step, no login, personal data never leaves your PC.

The methodology is documented in full (docs/FRAMEWORK.md) — heavily influenced by classical value investing and disciplined for Indian markets.

Open under a noncommercial licence — free to try, learn from, and adapt for personal use.

🔗 https://github.com/ady9999-dotcom/equity-dashboard

If you invest in Indian equities and try it, I'd genuinely love to hear where the reads land vs your own view — that's the feedback that sharpens the engine.

(Decision-support only — not investment advice.)

#IndianStockMarket #ValueInvesting #NSE #BSE #OpenSource #FinTech
```

### 3b) Short passing mention (use in a comment or a follow-up week)

```
Sharing a side project — a value-investing dashboard for BSE/NSE that I built to audit my own portfolio. Sector-appropriate valuation, forensic screens, bank module, four-lens committee. Open under a noncommercial licence.

If you invest in Indian equities and want to kick the tyres, feedback appreciated → https://github.com/ady9999-dotcom/equity-dashboard
```

**LinkedIn tip:** attach the hero screenshot as the image (not a link preview) — LinkedIn's algorithm rewards native images far more than link cards.

---

## 4) X / Twitter (bonus)

Thread format works best. Post the hero image with tweet 1; each subsequent tweet a screenshot from `docs/screenshots/`.

**Tweet 1:**
> I built a value-investing dashboard for Indian equities (BSE / NSE).
>
> Sector-appropriate valuation, forensic screens, a proper bank/NBFC view, and a four-lens investor committee.
>
> Open on GitHub — noncommercial licence. Feedback wanted. 🧵
>
> https://github.com/ady9999-dotcom/equity-dashboard

**Tweet 2** (attach `02-cash-and-working-capital.png`):
> Live cash & capital view for any NSE/BSE name — 5-yr capex vs OCF, cash-balance/FCF, and the working-capital cycle. Not from memory — from the latest filed numbers.

**Tweet 3** (attach `04-valuation-debt-forensic.png`):
> The valuation isn't a single "DCF" — it's *sector-appropriate*. P/B for lenders, mid-cycle EV/EBITDA for cyclicals, normalised P/E for compounders, anchored to the firm's own market multiple. Scenario band, not a single point.

**Tweet 4** (attach `05-decision-scorecard.png`):
> 100-point decision scorecard with base/bull/bear/severe scenarios. Business-quality, management and sector rows fold in a research overlay when present.

**Tweet 5** (attach `07-forensic-tabs.png`):
> ~40 diagnostic forensic ratios, 7 categories, each tagged good/watch/concern with a plain-language read. A screen, not a verdict — never sells a name on a lone bad ratio.

**Tweet 6** (close):
> Full technical writeup and the investing framework are in the repo. If you audit Indian equities, try 2-3 you know well and open an issue with your view — that's the feedback that sharpens it.
>
> https://github.com/ady9999-dotcom/equity-dashboard

---

## Cadence

Don't do everything in one day. A realistic sequence:

- **Day 0:** LinkedIn full post.
- **Day 2:** Reddit — one sub only (r/IndianStockMarket).
- **Day 5:** X/Twitter thread.
- **Day 7:** if a Redditor engaged well, reply with a genuine follow-up thanking them.
- **Day 10:** a second Reddit sub (r/StockMarketIndia or r/IndiaInvestments with the rules-respecting angle).
- **Day 14:** Show HN — but only once you've absorbed feedback and the repo is in strong shape.

Between posts, **update `CHANGELOG.md`** with any small improvements you make from the feedback. Users notice a repo that's alive.
