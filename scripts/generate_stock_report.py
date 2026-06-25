#!/usr/bin/env python3
import argparse
import html
import json
import shutil
import subprocess
from pathlib import Path
from string import Template

from validate_report import quality_markdown, validate


SECTION_KEYS = {
    "fundamentals": ["业务模式", "赚钱能力", "成长性", "盈利质量", "偿债与资产质量", "治理与股东背景"],
    "valuation": ["估值水平", "PE/PB口径差异", "相对行业", "历史位置", "成长匹配"],
    "technical": ["趋势", "最新量价", "公开资金流", "量价推断", "关键位"],
    "sentiment": ["短期影响", "公司催化", "资本与群体情绪", "突发风险", "补充核验"],
    "judgment": ["综合判断", "证据链一", "证据链二", "证据链三", "适合的研究场景", "乐观情景", "中性情景", "悲观情景", "观察条件", "失效条件", "方法论说明"],
    "risks": ["重点跟踪", "价格跟踪"],
}


def require_pack(pack: dict) -> None:
    identity = pack.get("identity", {})
    for key in ["name", "ticker", "market", "currency", "timezone", "latest_complete_day", "status"]:
        if not identity.get(key):
            raise ValueError(f"identity.{key} is required")
    sections = pack.get("sections", {})
    if not sections.get("core_conclusion"):
        raise ValueError("sections.core_conclusion is required")
    for group, keys in SECTION_KEYS.items():
        values = sections.get(group, {})
        for key in keys:
            if not values.get(key):
                raise ValueError(f"sections.{group}.{key} is required")
    if len(pack.get("sources", [])) < 3:
        raise ValueError("at least three sources are required")
    if len(pack.get("chart", {}).get("dates", [])) < 2:
        raise ValueError("chart requires at least two observations")
    if pack.get("pending_verification"):
        raise ValueError("pending_verification must be empty before PASS generation")
    if "数据待核验" in json.dumps(sections, ensure_ascii=False):
        raise ValueError("research sections still contain 数据待核验 placeholders")
    failures = [x.get("name") for x in pack.get("numeric_validation", []) if x.get("status") != "PASS"]
    if not pack.get("numeric_validation") or failures:
        raise ValueError(f"numeric validation is incomplete: {failures}")


def paragraphs(values: dict, keys: list[str]) -> str:
    return "".join(f"<p><b>{html.escape(key)}：</b>{html.escape(str(values[key]))}</p>" for key in keys)


def chart_svg(pack: dict, path: Path) -> None:
    chart = pack["chart"]
    dates, closes, volumes = chart["dates"], chart["close"], chart["volume"]
    w, h, ml, mr, mt = 1000, 390, 70, 25, 38
    ph, vh = 215, 78
    pmin, pmax, vmax = min(closes), max(closes), max(volumes)
    x = lambda i: ml + i * (w - ml - mr) / max(1, len(dates) - 1)
    y = lambda v: mt + (pmax - v) * ph / max(.001, pmax - pmin)
    points = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(closes))
    bars = "".join(f'<rect x="{x(i)-3:.1f}" y="{mt+ph+28+vh-v/vmax*vh:.1f}" width="6" height="{v/vmax*vh:.1f}" fill="#607d9b" opacity=".65"/>' for i, v in enumerate(volumes))
    labels = "".join(f'<text x="{x(i):.1f}" y="370" text-anchor="middle">{dates[i]}</text>' for i in [0, len(dates)//2, len(dates)-1])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><style>text{{font:14px Microsoft YaHei;fill:#52606d}}.t{{font:bold 19px Microsoft YaHei;fill:#172b4d}}</style><rect width="100%" height="100%" fill="white"/><text x="{ml}" y="24" class="t">{html.escape(pack['identity']['name'])} 近三个月价格与成交量（{html.escape(pack['identity']['currency'])}）</text><polyline points="{points}" fill="none" stroke="#2457c5" stroke-width="3"/>{bars}{labels}<text x="{w-mr}" y="24" text-anchor="end">最新完整交易日：{pack['identity']['latest_complete_day']}</text></svg>'''
    path.write_text(svg, encoding="utf-8")


def find_browser(value: str | None) -> Path:
    candidates = [
        value,
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("msedge"), shutil.which("microsoft-edge"), shutil.which("chrome"),
        shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)
    raise FileNotFoundError("Chrome or Edge was not found")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--browser")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    pack = json.loads(args.input.read_text(encoding="utf-8"))
    require_pack(pack)
    if args.validate_only:
        print("research pack: PASS")
        return 0
    out = args.output_dir or args.input.parent
    out.mkdir(parents=True, exist_ok=True)
    identity, sections, summary = pack["identity"], pack["sections"], pack["summary"]
    safe_name = identity["name"].replace("*", "")
    date_token = identity["latest_complete_day"].replace("-", "")
    stem = f"{safe_name}_截至{date_token}_股票分析报告"
    chart_path = out / f"{safe_name}_截至{date_token}_近三月量价图.svg"
    html_path, pdf_path = out / f"{stem}.html", out / f"{stem}.pdf"
    quality_path = out / f"{safe_name}_quality_check.md"
    chart_svg(pack, chart_path)
    cards = "<div class=\"grid\">" + "".join(f'<div class="card">{html.escape(label)}<b>{html.escape(str(summary[key]))}</b></div>' for label, key in [("收盘价", "close"), ("总市值", "market_cap"), ("PE / PB", "pe_pb"), ("近三月收益", "period_return")]) + "</div>"
    template = Template((Path(__file__).parent.parent / "templates" / "report_template.html").read_text(encoding="utf-8"))
    rendered = template.safe_substitute(
        title=html.escape(f"{identity['name']}（{identity['ticker']}）股票分析报告"),
        meta=html.escape(f"市场：{identity['market']}｜币种：{identity['currency']}｜{identity['status']}｜最新完整交易日：{identity['latest_complete_day']}｜{identity['timezone']}"),
        disclaimer=html.escape(pack["disclaimer"]), summary_cards=cards,
        core="".join(f"<p>{html.escape(str(x))}</p>" for x in sections["core_conclusion"]),
        fundamentals=paragraphs(sections["fundamentals"], SECTION_KEYS["fundamentals"]),
        valuation=paragraphs(sections["valuation"], SECTION_KEYS["valuation"]),
        technical=paragraphs(sections["technical"], SECTION_KEYS["technical"]),
        sentiment=paragraphs(sections["sentiment"], SECTION_KEYS["sentiment"]),
        judgment=paragraphs(sections["judgment"], SECTION_KEYS["judgment"]),
        risks=paragraphs(sections["risks"], SECTION_KEYS["risks"]),
        sources="<ul>" + "".join(f"<li>{html.escape(str(x))}</li>" for x in pack["sources"]) + "</ul>",
        chart_name=html.escape(chart_path.name),
    )
    html_path.write_text(rendered, encoding="utf-8")
    browser = find_browser(args.browser)
    subprocess.run([str(browser), "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()], check=True, capture_output=True, timeout=120)
    result = validate(pdf_path, pack, html_path)
    quality_path.write_text(quality_markdown(result, pack), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
