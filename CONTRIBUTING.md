# Contributing

Thanks for looking! This is a personal project shared under a **noncommercial licence** — feedback, bug reports and small PRs are very welcome; commercial forks are not.

## What kind of help lands best

- **🐛 Bug reports** — a specific stock loads wrong, a chart breaks, an error in the console. Use the *Bug report* issue template.
- **💬 Feedback on a company's read** — "The dashboard says HOLD on PRAJIND but I'd argue TRIM because…" These are the most valuable — they sharpen the model. Use the *Feedback* template.
- **💡 Feature requests** — a metric you'd like added, a section that's confusing, a screen that's missing. Use the *Feature* template.
- **📖 Docs** — typos, unclear passages, missing details in [`docs/`](docs/) — a small PR is perfect.

Please **read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/FRAMEWORK.md`](docs/FRAMEWORK.md) first** — most "why does it work this way?" questions are answered there, and it helps you propose changes that fit the existing design.

## Running it locally

Windows: double-click `run.bat`. Manually: `pip install -r requirements.txt && python server.py` → open `http://127.0.0.1:5000`.

Requires Python 3.10+. The dashboard also uses a **residential internet connection** for NSE data — office / VPN networks may block it (Yahoo + Screener still work).

## Sending a pull request

1. **Open an issue first** for anything non-trivial so we agree on the direction (saves you re-work).
2. Fork → branch → small, focused commits with clear messages.
3. Keep changes **inside the framework** — read `docs/FRAMEWORK.md`; don't add "one-hammer" heuristics that value a cyclical on spot earnings, etc.
4. **Don't commit personal data.** `.gitignore` already excludes `holdings_state.json`, `research_overlay.json`, `research_archive/`, `framework_path.txt`, `*.csv`, `*.xlsx`. Double-check before pushing.
5. If you add or change a feature that a user would notice, add a dated entry to the top of [`CHANGELOG.md`](CHANGELOG.md).
6. Open the PR against `main` with a short *what & why*.

## Style / house rules

- **Python**: standard library first; add a dependency only if there's no reasonable alternative (and update `requirements.txt`). Match existing style — no unnecessary reformatting.
- **Frontend**: keep it **one self-contained HTML file**. No build step, no framework, no external scripts. SVG charts stay hand-drawn.
- **No fabrication.** If a data point isn't in the feed, show `—` or "check filings" — never invent a number.
- **Small PRs merge.** A 40-line PR that fixes one thing is far more likely to land than a 400-line rewrite.

## Licence for contributions

By opening a PR, you agree your contribution is licensed under the project's licence ([PolyForm Noncommercial 1.0.0](LICENSE.md)) and that you have the right to submit it.

## What this project is *not* trying to become

- A trading platform, an alerts service, or an order-routing tool.
- A generic "any market" dashboard — it is deliberately tuned for **BSE / NSE**.
- Investment advice. This is decision-support software.

## Code of conduct

Be kind, be specific, be short. Assume the other person has good intent. Discuss the code / the read, not the person. That's it.
