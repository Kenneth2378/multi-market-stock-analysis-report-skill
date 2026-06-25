#!/usr/bin/env python3
"""Collect public Eastmoney evidence for an A-share or B-share research pack."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path


CHINA_TZ = dt.timezone(dt.timedelta(hours=8), name="Asia/Shanghai")


def parse_ticker(value: str) -> tuple[str, str, str]:
    token = value.strip().upper()
    if "." in token:
        code, suffix = token.split(".", 1)
    else:
        code = token
        suffix = "SH" if code.startswith(("5", "6", "9")) else "SZ"
    if len(code) != 6 or not code.isdigit() or suffix not in {"SH", "SZ"}:
        raise ValueError("ticker must look like 600845.SH, 000938.SZ, or a six-digit code")
    secid = ("1." if suffix == "SH" else "0.") + code
    return code, suffix, secid


def fetch_json(url: str, retries: int = 3) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 stock-research-skill"})
    last_error = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
            time.sleep(attempt + 1)
    curl = shutil.which("curl")
    if curl:
        result = subprocess.run(
            [curl, "-fsSL", "--max-time", "45", "-A", "Mozilla/5.0 stock-research-skill", url],
            capture_output=True, timeout=50,
        )
        if result.returncode == 0:
            return json.loads(result.stdout.decode("utf-8"))
    raise RuntimeError(f"public source request failed: {type(last_error).__name__}") from last_error


def source_urls(code: str, suffix: str, secid: str, begin: str, end: str) -> dict[str, str]:
    market_code = suffix + code
    filter_value = urllib.parse.quote(f'(SECURITY_CODE="{code}")', safe="()=")
    return {
        "kline": f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg={begin}&end={end}",
        "quote": f"https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f84,f85,f116,f117,f162,f164,f167,f170",
        "finance_summary": f"https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_LICO_FN_CPD&columns=ALL&filter={filter_value}&pageNumber=1&pageSize=12",
        "profile": f"https://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/CompanySurveyAjax?code={market_code}",
        "announcements": f"https://np-anotice-stock.eastmoney.com/api/security/ann?sr=-1&page_size=20&page_index=1&ann_type=A&client_source=web&stock_list={code}",
        "balance": f"https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_DMSK_FN_BALANCE&columns=ALL&filter={filter_value}&pageNumber=1&pageSize=12",
        "cashflow": f"https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_DMSK_FN_CASHFLOW&columns=ALL&filter={filter_value}&pageNumber=1&pageSize=12",
        "income": f"https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_DMSK_FN_INCOME&columns=ALL&filter={filter_value}&pageNumber=1&pageSize=12",
        "fundflow": f"https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?lmt=30&klt=101&secid={secid}&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63",
    }


def parse_klines(payload: dict) -> list[dict]:
    lines = (payload.get("data") or {}).get("klines") or []
    rows = []
    for line in lines:
        values = line.split(",")
        rows.append({
            "date": values[0], "open": float(values[1]), "close": float(values[2]),
            "high": float(values[3]), "low": float(values[4]), "volume": float(values[5]),
            "amount": float(values[6]), "amplitude": float(values[7]),
            "pct_change": float(values[8]), "change": float(values[9]), "turnover": float(values[10]),
        })
    return rows


def normalized_summary(rows: list[dict], quote: dict) -> dict:
    if len(rows) < 2:
        raise ValueError("fewer than two complete trading days were returned")
    latest, prior, start = rows[-1], rows[-2], rows[0]
    closes = [row["close"] for row in rows]
    shares = quote.get("f84")
    market_cap = latest["close"] * shares if isinstance(shares, (int, float)) else None
    return {
        "latest": latest,
        "prior_close": prior["close"],
        "period_start": start,
        "period_return_pct": (latest["close"] / start["close"] - 1) * 100,
        "day_return_recalculated_pct": (latest["close"] / prior["close"] - 1) * 100,
        "period_high": max(rows, key=lambda row: row["high"]),
        "period_low": min(rows, key=lambda row: row["low"]),
        "ma20": sum(closes[-20:]) / min(20, len(closes)),
        "ma60": sum(closes[-60:]) / min(60, len(closes)),
        "average_amount": sum(row["amount"] for row in rows) / len(rows),
        "average_turnover": sum(row["turnover"] for row in rows) / len(rows),
        "top_volume_days": sorted(rows, key=lambda row: row["volume"], reverse=True)[:3],
        "total_shares": shares,
        "market_cap_recalculated": market_cap,
        "quote_fields_raw": quote,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--name")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    code, suffix, secid = parse_ticker(args.ticker)
    today = dt.datetime.now(CHINA_TZ).date()
    end_date = dt.date.fromisoformat(args.end) if args.end else today
    start_date = dt.date.fromisoformat(args.start) if args.start else end_date - dt.timedelta(days=110)
    urls = source_urls(code, suffix, secid, start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
    raw, source_errors = {}, {}
    for key, url in urls.items():
        try:
            raw[key] = fetch_json(url)
        except Exception as exc:
            if key in {"kline", "quote"}:
                raise RuntimeError(f"required public source failed: {key}") from exc
            raw[key] = {}
            source_errors[key] = str(exc)
    rows = [row for row in parse_klines(raw["kline"]) if row["date"] <= end_date.isoformat()]
    now = dt.datetime.now(CHINA_TZ)
    if end_date == now.date() and now.time() < dt.time(16, 0):
        rows = [row for row in rows if row["date"] != end_date.isoformat()]
    quote = raw["quote"].get("data") or {}
    name = args.name or quote.get("f58") or code
    is_sh_b = suffix == "SH" and code.startswith("9")
    is_sz_b = suffix == "SZ" and code.startswith("2")
    currency = "USD" if is_sh_b else "HKD" if is_sz_b else "RMB"
    evidence = {
        "identity": {"name": name, "ticker": f"{code}.{suffix}", "secid": secid, "currency": currency, "timezone": "Asia/Shanghai"},
        "collected_at": now.isoformat(timespec="seconds"),
        "latest_complete_day": rows[-1]["date"] if rows else None,
        "source_urls": urls,
        "source_errors": source_errors,
        "market_history": rows,
        "normalized": normalized_summary(rows, quote),
        "financial_summary": (raw["finance_summary"].get("result") or {}).get("data") or [],
        "income_statements": (raw["income"].get("result") or {}).get("data") or [],
        "balance_sheets": (raw["balance"].get("result") or {}).get("data") or [],
        "cashflow_statements": (raw["cashflow"].get("result") or {}).get("data") or [],
        "company_profile": raw["profile"],
        "announcements": (raw["announcements"].get("data") or {}).get("list") or [],
        "public_fundflow": (raw["fundflow"].get("data") or {}).get("klines") or [],
        "limitations": ["聚合接口仅作为公开证据入口，定期报告和重大事项必须回到法定披露核验。", "公开资金流字段不得表述为已确认的账户级行为。"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
