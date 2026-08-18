"""
NSE India client — pulls the data NSE serves cleanly as JSON.

NSE blocks non-browser callers two ways:
  1. TLS fingerprint  -> defeated by curl_cffi's `impersonate="chrome"`.
  2. IP reputation     -> datacenter / cloud IPs get 403 regardless. A normal
                          residential connection (your own PC) passes fine.

So every call here is wrapped: if NSE answers, you get authoritative NSE data;
if NSE 403s (e.g. running from a server/sandbox), the caller falls back to
yfinance. Run this file directly to self-test:  python nse.py
"""
import time

try:
    from curl_cffi import requests as creq
    _HAVE_CURL = True
except Exception:
    _HAVE_CURL = False

BASE = "https://www.nseindia.com"
_session = None
_last_warm = 0


def _get_session():
    """A warmed session with NSE cookies. Re-warms every few minutes."""
    global _session, _last_warm
    if not _HAVE_CURL:
        return None
    now = time.time()
    if _session is None or now - _last_warm > 240:
        _session = creq.Session(impersonate="chrome")
        _session.headers.update({
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*",
        })
        try:
            _session.get(BASE + "/", timeout=15)
            _session.get(BASE + "/get-quotes/equity?symbol=RELIANCE", timeout=15)
            _last_warm = now
        except Exception:
            return None
    return _session


def _api(path, referer=None, retries=2):
    """GET an NSE api path -> parsed JSON, or None if NSE is unreachable/blocked."""
    s = _get_session()
    if s is None:
        return None
    hdr = {"Referer": referer or (BASE + "/get-quotes/equity")}
    for attempt in range(retries + 1):
        try:
            r = s.get(BASE + path, headers=hdr, timeout=15)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (401, 403):
                # cookie expired or IP-blocked; re-warm once, then give up
                global _session
                _session = None
                if attempt < retries:
                    s = _get_session()
                    if s is None:
                        return None
                    continue
                return None
        except Exception:
            if attempt < retries:
                time.sleep(0.5)
                continue
            return None
    return None


def available():
    """True if NSE endpoints respond from this network."""
    d = quote("RELIANCE")
    return d is not None and d.get("priceInfo") is not None


# ---------------- endpoints ----------------
def quote(symbol):
    symbol = symbol.upper().strip()
    ref = f"{BASE}/get-quotes/equity?symbol={symbol}"
    return _api(f"/api/quote-equity?symbol={symbol}", ref)


def trade_info(symbol):
    symbol = symbol.upper().strip()
    ref = f"{BASE}/get-quotes/equity?symbol={symbol}"
    return _api(f"/api/quote-equity?symbol={symbol}&section=trade_info", ref)


def corporate_actions(symbol):
    symbol = symbol.upper().strip()
    return _api(f"/api/corporates-corporateActions?index=equities&symbol={symbol}",
                f"{BASE}/get-quotes/equity?symbol={symbol}")


def announcements(symbol):
    symbol = symbol.upper().strip()
    return _api(f"/api/corporate-announcements?index=equities&symbol={symbol}",
                f"{BASE}/get-quotes/equity?symbol={symbol}")


def board_meetings(symbol):
    symbol = symbol.upper().strip()
    return _api(f"/api/corporate-board-meetings?index=equities&symbol={symbol}",
                f"{BASE}/get-quotes/equity?symbol={symbol}")


def _fetch_text(url):
    """GET a raw text/XML URL through the warmed session, or None."""
    s = _get_session()
    if s is None:
        return None
    try:
        r = s.get(url, timeout=20)
        if r.status_code == 200:
            return r.text
    except Exception:
        return None
    return None


# summary members on the CategoryOfShareholdersAxis -> our buckets
_SHP_MAP = {
    "ShareholdingOfPromoterAndPromoterGroupMember": "promoter",
    "InstitutionsForeignMember": "fii",
    "InstitutionsDomesticMember": "dii",
    "NonInstitutionsMember": "retail",
    "PublicShareholdingMember": "public",
    "SharesHeldByNonPromoterNonPublicShareholdersMember": "nonPromNonPub",
}


def _parse_shp_xbrl(text):
    """Parse a SEBI shareholding-pattern XBRL into {bucket: pct 0-100}."""
    from xml.etree import ElementTree as ET
    ln = lambda x: x.split('}')[-1]
    try:
        root = ET.fromstring(text.encode('utf-8'))
    except Exception:
        return {}
    ctx = {}
    for c in root.iter():
        if ln(c.tag) != 'context':
            continue
        mems = [m for m in c.iter() if ln(m.tag) == 'explicitMember']
        cat = [m for m in mems if 'CategoryOfShareholdersAxis' in (m.attrib.get('dimension') or '')]
        if len(mems) == 1 and cat and cat[0].text:
            ctx[c.attrib.get('id')] = cat[0].text.strip().split(':')[-1]
    out = {}
    for el in root.iter():
        if ln(el.tag) == 'ShareholdingAsAPercentageOfTotalNumberOfShares':
            cr = el.attrib.get('contextRef')
            bucket = _SHP_MAP.get(ctx.get(cr, ''))
            if bucket and el.text:
                try:
                    out[bucket] = round(float(el.text) * 100, 2)
                except ValueError:
                    pass
    return out


def _num(s):
    try:
        return float(str(s).replace(',', '').strip())
    except (TypeError, ValueError):
        return None


def shareholding(symbol):
    """
    Promoter / FII / DII / Retail split + promoter-holding trend, from NSE's
    shareholding-pattern filings. Returns None if NSE is unreachable.
    """
    symbol = symbol.upper().strip()
    ref = f"{BASE}/get-quotes/equity?symbol={symbol}"
    master = _api(f"/api/corporate-share-holdings-master?index=equities&symbol={symbol}", ref)
    if not isinstance(master, list) or not master:
        return None
    latest = master[0]
    split = {}
    if latest.get("xbrl"):
        xml = _fetch_text(latest["xbrl"])
        if xml:
            split = _parse_shp_xbrl(xml)
    # previous quarter's split -> quarter-over-quarter FII/DII/retail change
    prev, prev_date = {}, None
    if len(master) > 1 and master[1].get("xbrl"):
        pxml = _fetch_text(master[1]["xbrl"])
        if pxml:
            prev = _parse_shp_xbrl(pxml)
            prev_date = master[1].get("date")

    def chg(key):
        a, b = split.get(key), prev.get(key)
        return round(a - b, 2) if (a is not None and b is not None) else None
    # promoter-holding trend from the master rows (pr_and_prgrp per quarter)
    trend = []
    for row in master[:6]:
        p = _num(row.get("pr_and_prgrp"))
        if p is not None and row.get("date"):
            trend.append({"date": row["date"], "promoter": round(p, 2)})
    trend.reverse()
    out = {
        "date": latest.get("date"),
        "promoter": split.get("promoter", _num(latest.get("pr_and_prgrp"))),
        "fii": split.get("fii"),
        "dii": split.get("dii"),
        "retail": split.get("retail"),
        "public": split.get("public", _num(latest.get("public_val"))),
        "nonPromNonPub": split.get("nonPromNonPub"),
        "promoterTrend": trend,
        "prevDate": prev_date,
        "fiiChange": chg("fii"),
        "diiChange": chg("dii"),
        "retailChange": chg("retail"),
        "promoterChange": chg("promoter"),
        "source": "NSE",
    }
    return out


def pledge(symbol):
    """Promoter pledge / encumbrance from NSE pledge disclosures, or None."""
    symbol = symbol.upper().strip()
    ref = f"{BASE}/get-quotes/equity?symbol={symbol}"
    d = _api(f"/api/corporate-pledgedata?index=equities&symbol={symbol}", ref)
    if not isinstance(d, dict) or not d.get("data"):
        return None
    r = d["data"][0]
    return {
        "promoterHolding": _num(r.get("percPromoterHolding")),
        "pledgedPct": _num(r.get("percSharesPledged")),   # % of promoter shares pledged/encumbered
        "asOf": r.get("shp"),
        "source": "NSE",
    }


def quarterly_filings(symbol):
    """Map (year, month of quarter-end) -> (xbrl_url, is_consolidated) for quarterly results."""
    from datetime import datetime
    symbol = symbol.upper().strip()
    ref = f"{BASE}/get-quotes/equity?symbol={symbol}"
    d = _api(f"/api/corporates-financial-results?index=equities&symbol={symbol}&period=Quarterly", ref)
    if not isinstance(d, list):
        return {}
    out = {}
    for f in d:
        td = f.get("toDate")
        if not td:
            continue
        try:
            dt = datetime.strptime(td, "%d-%b-%Y")
        except ValueError:
            continue
        key = (dt.year, dt.month)
        cons = f.get("consolidated") == "Consolidated"
        prev = out.get(key)
        if prev is None or (cons and not prev[1]):
            out[key] = (f.get("xbrl"), cons)
    return out


def parse_quarterly_xbrl(xml):
    """Extract {rev, pat, interest, ebitda} (absolute ₹) for the 3-month quarter, or None."""
    from xml.etree import ElementTree as ET
    from datetime import datetime
    ln = lambda x: x.split('}')[-1]
    try:
        root = ET.fromstring(xml.encode('utf-8'))
    except Exception:
        return None
    # contexts: id -> (start, end, duration_days) for duration contexts
    ctx = {}
    for c in root.iter():
        if ln(c.tag) != 'context':
            continue
        sd = ed = None
        for p in c.iter():
            t = ln(p.tag)
            if t == 'startDate':
                sd = p.text
            elif t == 'endDate':
                ed = p.text
        if sd and ed:
            try:
                d0 = datetime.strptime(sd, '%Y-%m-%d')
                d1 = datetime.strptime(ed, '%Y-%m-%d')
                ctx[c.attrib.get('id')] = (d0, d1, (d1 - d0).days)
            except ValueError:
                pass
    # the quarterly context = ~3-month duration with the latest end date
    q = None
    for cid, (d0, d1, dur) in ctx.items():
        if 80 <= dur <= 100 and (q is None or d1 > ctx[q][1]):
            q = cid
    if not q:
        return None

    def getval(tag):
        for el in root.iter():
            if ln(el.tag) == tag and el.attrib.get('contextRef') == q and el.text:
                try:
                    return float(el.text)
                except ValueError:
                    pass
        return None

    rev = getval('RevenueFromOperations')
    pat = getval('ProfitLossForPeriod')
    fin = getval('FinanceCosts')
    dep = getval('DepreciationDepletionAndAmortisationExpense')
    pbt = getval('ProfitBeforeTax')
    if rev is None or pat is None:
        return None
    ebitda = (pbt + fin + dep) if (pbt is not None and fin is not None and dep is not None) else None
    return {"rev": rev, "pat": pat, "interest": fin, "ebitda": ebitda}


def quarter_for(symbol, year, month, _filings_cache={}):
    """Fetch & parse the quarterly result for a specific quarter-end (year, month), or None."""
    filings = _filings_cache.get(symbol)
    if filings is None:
        filings = quarterly_filings(symbol)
        _filings_cache[symbol] = filings
    fil = filings.get((year, month))
    if not fil or not fil[0]:
        return None
    xml = _fetch_text(fil[0])
    if not xml:
        return None
    return parse_quarterly_xbrl(xml)


def price_bundle(symbol):
    """Normalized price + 52w + basic identity from NSE, or None."""
    d = quote(symbol)
    if not d or not d.get("priceInfo"):
        return None
    pi = d["priceInfo"]
    info = d.get("info", {})
    meta = d.get("metadata", {})
    wk = pi.get("weekHighLow", {}) or {}
    return {
        "price": pi.get("lastPrice"),
        "prevClose": pi.get("previousClose"),
        "high52": wk.get("max"),
        "low52": wk.get("min"),
        "name": info.get("companyName"),
        "sector": meta.get("industry") or meta.get("pdSectorInd"),
        "series": info.get("activeSeries", ["EQ"])[0] if info.get("activeSeries") else "EQ",
        "source": "NSE",
    }


if __name__ == "__main__":
    print("curl_cffi installed:", _HAVE_CURL)
    print("NSE reachable from here:", available())
    pb = price_bundle("RELIANCE")
    print("price_bundle:", pb)
