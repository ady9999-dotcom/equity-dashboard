"""
Auto-fetch quarterly financials from Screener.in company pages (public, no login).

Screener renders the full "Quarterly Results" table server-side at
  https://www.screener.in/company/<SYMBOL>/consolidated/   (falls back to standalone)
with ~12-13 CONSECUTIVE quarters (Sales, Operating Profit = EBITDA, Interest, Net
Profit) — including the Sep-2025 quarter Yahoo drops. We fetch and parse it to fill
quarterly gaps automatically. Values are in ₹ Crore. Cached in-process for the session.
"""
import re
import time

try:
    from curl_cffi import requests as creq
    _HAVE = True
except Exception:
    _HAVE = False

_MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
           "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
_CACHE = {}          # symbol -> (timestamp, parsed)
_TTL = 6 * 3600      # 6 hours


def _num(s):
    s = re.sub(r"<[^>]+>", "", s).replace(",", "").replace("%", "").replace("\xa0", " ").strip()
    if s in ("", "-", "—"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse(html):
    # find the QUARTERLY table = the <table> whose month-year headers span VARIED months
    # (the annual P&L table also uses "Mon YYYY" but all its months are March).
    tb = None
    cols = []
    for cand in re.findall(r"<table[^>]*>(.*?)</table>", html, re.S):
        heads = re.findall(r"<th[^>]*>\s*([A-Za-z]{3}\s+20\d{2})\s*</th>", cand)
        parsed = []
        for h in heads:
            m = re.match(r"([A-Za-z]{3})\s+(\d{4})", h)
            if m and m.group(1).lower() in _MONTHS:
                parsed.append((int(m.group(2)), _MONTHS[m.group(1).lower()]))
        months = {mo for _, mo in parsed}
        if len(parsed) >= 8 and len(months) >= 2:   # many headers, varied months = quarterly
            tb, cols = cand, parsed
            break
    if not tb or not cols:
        return None
    data = {}
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", tb, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if not cells:
            continue
        label = re.sub(r"<[^>]+>", "", cells[0]).replace("\xa0", " ").strip().lower()
        vals = [_num(c) for c in cells[1:]]
        if label.startswith("sales") or label.startswith("revenue"):
            data["rev"] = vals                       # banks: revenue = total interest income earned
        elif label.startswith("operating profit"):
            data["ebitda"] = vals
        elif label.startswith("financing profit"):   # banks: spread (NII − opex) proxy
            data["finprofit"] = vals
        elif label.startswith("financing margin"):   # banks: financing-margin %, a NIM proxy
            data["finmargin"] = vals
        elif label.startswith("interest"):
            data["interest"] = vals                  # banks: interest expended
        elif label.startswith("other income"):
            data["otherinc"] = vals
        elif label.startswith("net profit"):
            data["np"] = vals
        elif label.startswith("gross npa"):
            data["gnpa"] = vals
        elif label.startswith("net npa"):
            data["nnpa"] = vals
    if "rev" not in data:
        return None
    out = []
    for idx, (y, mo) in enumerate(cols):
        def g(k):
            v = data.get(k)
            return v[idx] if (v and idx < len(v)) else None
        rev, intr = g("rev"), g("interest")
        nii = (rev - intr) if (rev is not None and intr is not None) else None   # bank NII proxy
        out.append({"y": y, "m": mo, "rev": rev, "ebitda": g("ebitda"),
                    "interest": intr, "np": g("np"),
                    "finProfit": g("finprofit"), "finMargin": g("finmargin"),
                    "otherIncome": g("otherinc"), "gnpa": g("gnpa"), "nnpa": g("nnpa"),
                    "nii": nii})
    return out


def _section(html, sid):
    """Return the HTML of the <section id=sid ...>…</section> block, or ''."""
    i = html.find('id="' + sid + '"')
    if i < 0:
        return ""
    j = html.find("</section>", i)
    return html[i:(j if j > 0 else len(html))]


def _latest_col(section_html, label_res):
    """
    In a Screener statement section, return the value in the LAST (most-recent)
    data column for the first row whose label matches any regex in label_res.
    Screener orders columns oldest→newest, so the last column is the latest year.
    Returns a float in the section's native units (₹ Cr, days, or %), or None.
    """
    # how many header year-columns does this table have?
    heads = re.findall(r'<th[^>]*>\s*([A-Za-z]{3}\s+20\d{2}|TTM)\s*</th>', section_html)
    ncol = len(heads)
    if ncol == 0:
        return None
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", section_html, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if not cells:
            continue
        label = re.sub(r"<[^>]+>", "", cells[0]).replace("\xa0", " ").strip().lower()
        if any(re.search(p, label) for p in label_res):
            vals = [_num(c) for c in cells[1:1 + ncol]]
            vals = [v for v in vals if v is not None]
            # prefer the last real number (latest reported year), skip a trailing TTM
            # only when it duplicates; simplest robust choice = last non-None
            return vals[-1] if vals else None
    return None


def _row_series(section_html, label_res):
    """Full oldest→newest numeric series for the first matching row (annual columns
    only, excluding a trailing TTM). Returns [] if not found."""
    heads = re.findall(r'<th[^>]*>\s*([A-Za-z]{3}\s+20\d{2}|TTM)\s*</th>', section_html)
    ncol = len(heads)
    n_annual = sum(1 for h in heads if h != "TTM")
    if ncol == 0:
        return []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", section_html, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if not cells:
            continue
        label = re.sub(r"<[^>]+>", "", cells[0]).replace("\xa0", " ").strip().lower()
        if any(re.search(p, label) for p in label_res):
            vals = [_num(c) for c in cells[1:1 + ncol]]
            # drop the trailing TTM column so we keep clean fiscal-year points
            if ncol > n_annual:
                vals = vals[:n_annual]
            return [v for v in vals if v is not None]
    return []


def fetch_bank_npa(symbol):
    """Latest Gross/Net NPA % for a bank/NBFC from Screener's STANDALONE quarters table
    (asset quality is a standalone regulatory disclosure; the consolidated page omits it).
    Returns {gnpa, nnpa, asOf 'MM/YYYY'} using the most recent non-blank column, or None."""
    if not _HAVE:
        return None
    symbol = symbol.upper().strip()
    ck = "NPA:" + symbol
    hit = _CACHE.get(ck)
    if hit and (time.time() - hit[0] < _TTL):
        return hit[1]
    out = None
    try:
        s = creq.Session(impersonate="chrome")
        r = s.get(f"https://www.screener.in/company/{symbol}/", timeout=20)   # standalone
        if r.status_code == 200:
            sec = _section(r.text, "quarters")
            heads = re.findall(r'<th[^>]*>\s*([A-Za-z]{3}\s+20\d{2})\s*</th>', sec)

            def _series(label_res):
                for row in re.findall(r"<tr[^>]*>(.*?)</tr>", sec, re.S):
                    cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
                    if not cells:
                        continue
                    lbl = re.sub(r"<[^>]+>", "", cells[0]).replace("\xa0", " ").strip().lower()
                    if any(re.search(p, lbl) for p in label_res):
                        return [_num(c) for c in cells[1:1 + len(heads)]]
                return []
            gs, ns = _series([r"^gross npa"]), _series([r"^net npa"])
            gnpa = nnpa = asof = None
            for i, h in enumerate(heads):
                if i < len(gs) and gs[i] is not None:
                    gnpa, asof = gs[i], h
                if i < len(ns) and ns[i] is not None:
                    nnpa = ns[i]
            if gnpa is not None or nnpa is not None:
                out = {"gnpa": gnpa, "nnpa": nnpa, "asOf": asof}
    except Exception:
        out = None
    _CACHE[ck] = (time.time(), out)
    return out


def fetch_financials(symbol):
    """
    Return latest-FY STATED values from Screener (balance sheet, cash flow, ratios),
    used only as a FALLBACK for values the primary feed couldn't compute. Every
    value here is a number Screener itself displays — nothing is inferred.
    Keys (₹ Cr unless noted): cfo, borrowings, reserves, equityCapital, netWorth,
    roce (%), dso/dio/dpo/ccc/wcDays (days). Cached per session. None on failure.
    """
    if not _HAVE:
        return None
    symbol = symbol.upper().strip()
    ck = "FIN:" + symbol
    hit = _CACHE.get(ck)
    if hit and (time.time() - hit[0] < _TTL):
        return hit[1]
    out = None
    try:
        s = creq.Session(impersonate="chrome")
        html = None
        for path in (f"/company/{symbol}/consolidated/", f"/company/{symbol}/"):
            try:
                r = s.get("https://www.screener.in" + path, timeout=20)
                if r.status_code == 200 and 'id="balance-sheet"' in r.text:
                    html = r.text
                    break
            except Exception:
                continue
        if html:
            bs = _section(html, "balance-sheet")
            cf = _section(html, "cash-flow")
            rt = _section(html, "ratios")
            pl = _section(html, "profit-loss")
            borrowings = _latest_col(bs, [r"^borrowing"])
            reserves = _latest_col(bs, [r"^reserves"])
            eqcap = _latest_col(bs, [r"^equity capital"])
            deposits = _latest_col(bs, [r"^deposits"])          # banks/NBFC funding franchise
            cfo = _latest_col(cf, [r"cash from operating"])
            nw = (reserves + eqcap) if (reserves is not None and eqcap is not None) else None
            out = {
                "borrowings": borrowings, "reserves": reserves, "equityCapital": eqcap,
                "deposits": deposits, "netWorth": nw, "cfo": cfo,
                "roce": _latest_col(rt, [r"^roce"]),
                "dso": _latest_col(rt, [r"debtor days"]),
                "dio": _latest_col(rt, [r"inventory days"]),
                "dpo": _latest_col(rt, [r"days payable"]),
                "ccc": _latest_col(rt, [r"cash conversion"]),
                "wcDays": _latest_col(rt, [r"working capital days"]),
                # deep annual history (₹ Cr, oldest→newest) — for through-cycle normalisation
                "npHist": _row_series(pl, [r"^net profit"]),
                "opHist": _row_series(pl, [r"^operating profit"]),
                "salesHist": _row_series(pl, [r"^sales", r"^revenue"]),
            }
            if not any(v is not None for v in out.values()):
                out = None
    except Exception:
        out = None
    _CACHE[ck] = (time.time(), out)
    return out


def fetch_quarterly(symbol):
    """Return [{y,m,rev,ebitda,interest,np}, …] from Screener, or None. Cached per session."""
    if not _HAVE:
        return None
    symbol = symbol.upper().strip()
    hit = _CACHE.get(symbol)
    if hit and (time.time() - hit[0] < _TTL):
        return hit[1]
    result = None
    try:
        s = creq.Session(impersonate="chrome")
        for path in (f"/company/{symbol}/consolidated/", f"/company/{symbol}/"):
            try:
                r = s.get("https://www.screener.in" + path, timeout=20)
                if r.status_code == 200:
                    parsed = _parse(r.text)
                    if parsed:
                        result = parsed
                        break
            except Exception:
                continue
    except Exception:
        result = None
    _CACHE[symbol] = (time.time(), result)
    return result


if __name__ == "__main__":
    for sym in ("ADANIPORTS", "RELIANCE", "TITAN"):
        q = fetch_quarterly(sym)
        print(sym, "->", len(q) if q else None, "quarters",
              (q[-3:] if q else ""))
