#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader

from scan_pdf_privacy import scan


MIN_CHARS = 3537
REQUIRED_LABELS = [
    "业务模式：", "赚钱能力：", "成长性：", "盈利质量：", "偿债与资产质量：", "治理与股东背景：",
    "估值水平：", "PE/PB口径差异：", "相对行业：", "历史位置：", "成长匹配：",
    "趋势：", "最新量价：", "公开资金流：", "量价推断：", "关键位：",
    "短期影响：", "公司催化：", "资本与群体情绪：", "突发风险：",
    "综合判断：", "证据链一：", "证据链二：", "证据链三：", "适合的研究场景：",
    "乐观情景：", "中性情景：", "悲观情景：", "观察条件：", "失效条件：", "方法论说明：",
    "重点跟踪：", "价格跟踪：", "主要数据来源", "仅供学习研究，不构成投资建议",
]


def validate(pdf: Path, pack: dict | None = None, html_path: Path | None = None) -> dict:
    reader = PdfReader(str(pdf))
    page_text = [(page.extract_text() or "") for page in reader.pages]
    text = "\n".join(page_text)
    missing = [label for label in REQUIRED_LABELS if label not in text]
    required_terms = (pack or {}).get("semantic", {}).get("required_terms", [])
    forbidden_terms = (pack or {}).get("semantic", {}).get("forbidden_terms", [])
    missing_terms = [term for term in required_terms if term not in text]
    forbidden_hits = [term for term in forbidden_terms if term in text]
    numeric_fail = [row.get("name", "未命名") for row in (pack or {}).get("numeric_validation", []) if row.get("status") != "PASS"]
    latest_day = (pack or {}).get("identity", {}).get("latest_complete_day")
    date_ok = not latest_day or latest_day in text
    privacy = scan(pdf)
    sparse_pages = [i + 1 for i, value in enumerate(page_text[:-1]) if len(value.strip()) < 120]
    forced_break = False
    if html_path and html_path.exists():
        forced_break = "break-before:page" in html_path.read_text(encoding="utf-8")
    passed = not any([missing, missing_terms, forbidden_hits, numeric_fail, not date_ok, privacy["hits"], sparse_pages, forced_break, len(text) < MIN_CHARS])
    return {
        "status": "PASS" if passed else "NEEDS_REVIEW",
        "pdf": pdf.name,
        "bytes": pdf.stat().st_size,
        "pages": len(reader.pages),
        "characters": len(text),
        "minimum_characters": MIN_CHARS,
        "missing_contract_items": missing,
        "missing_required_terms": missing_terms,
        "forbidden_term_hits": forbidden_hits,
        "numeric_failures": numeric_fail,
        "latest_complete_day_present": date_ok,
        "privacy": privacy,
        "sparse_nonfinal_pages": sparse_pages,
        "forced_page_break": forced_break,
    }


def quality_markdown(result: dict, pack: dict) -> str:
    ident = pack["identity"]
    rows = []
    for item in pack.get("numeric_validation", []):
        rows.append("| " + " | ".join(str(item.get(k, "")) for k in ["name", "raw", "source", "date", "unit", "formula", "calculated", "source_result", "difference", "status"]) + " |")
    return f'''# {ident['name']} 报告质量检查

- 股票：{ident['name']}（{ident['ticker']}）
- 市场：{ident['market']}；货币：{ident['currency']}
- 最新完整交易日：{ident['latest_complete_day']}（{ident['timezone']}）
- PDF文件：{'PASS' if result['bytes'] > 0 else 'FAIL'}（{result['bytes']} bytes）
- 旧版完整内容合同：{'PASS' if not result['missing_contract_items'] and result['characters'] >= result['minimum_characters'] else 'NEEDS_REVIEW'}；正文字符数：{result['characters']}（最低{result['minimum_characters']}）
- 语义一致性：{'PASS' if not result['missing_required_terms'] and not result['forbidden_term_hits'] else 'FAIL'}
- 数字验证：{'PASS' if not result['numeric_failures'] else 'FAIL'}
- PDF Privacy Scan：{result['privacy']['status']}；命中：{', '.join(result['privacy']['hits']) if result['privacy']['hits'] else '无'}
- 分页检查：{'PASS' if not result['sparse_nonfinal_pages'] and not result['forced_page_break'] else 'NEEDS_REVIEW'}
- 数据待核验字段：{', '.join(pack.get('pending_verification', [])) if pack.get('pending_verification') else '无'}

## 数字验证轨迹

| 指标 | 原始字段 | 数据源 | 日期 | 单位 | 公式 | 计算结果 | 来源结果 | 差异 | 结论 |
|---|---|---|---|---|---|---:|---:|---:|---|
{chr(10).join(rows)}

## 最终结论

**{result['status']}**
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--pack", type=Path)
    parser.add_argument("--html", type=Path)
    parser.add_argument("--quality-out", type=Path)
    args = parser.parse_args()
    pack = json.loads(args.pack.read_text(encoding="utf-8")) if args.pack else None
    result = validate(args.pdf, pack, args.html)
    if args.quality_out and pack:
        args.quality_out.write_text(quality_markdown(result, pack), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
