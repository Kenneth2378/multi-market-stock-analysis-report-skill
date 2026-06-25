#!/usr/bin/env python3
"""Create a non-PASS research-pack draft from collected public evidence."""

import argparse
import json
from pathlib import Path


PLACEHOLDER = "数据待核验：请基于公司定期报告、公告和可复算公开数据完成公司专属分析。"


def draft_pack(evidence: dict) -> dict:
    identity = evidence["identity"]
    normalized = evidence["normalized"]
    latest = normalized["latest"]
    ticker = identity["ticker"]
    market = "上交所" if ticker.endswith(".SH") else "深交所"
    dates = [row["date"] for row in evidence["market_history"]]
    closes = [row["close"] for row in evidence["market_history"]]
    volumes = [row["volume"] for row in evidence["market_history"]]
    return {
        "identity": {
            "name": identity["name"], "ticker": ticker, "market": market,
            "currency": identity["currency"], "timezone": identity["timezone"],
            "latest_complete_day": evidence["latest_complete_day"], "status": PLACEHOLDER,
        },
        "summary": {
            "close": f"{latest['close']:.2f} {identity['currency']}",
            "market_cap": str(normalized.get("market_cap_recalculated") or "数据待核验"),
            "pe_pb": "数据待核验", "period_return": f"{normalized['period_return_pct']:.2f}%",
        },
        "chart": {"dates": dates, "close": closes, "volume": volumes},
        "sections": {
            "core_conclusion": [PLACEHOLDER, PLACEHOLDER, PLACEHOLDER],
            "fundamentals": {key: PLACEHOLDER for key in ["业务模式", "赚钱能力", "成长性", "盈利质量", "偿债与资产质量", "治理与股东背景"]},
            "valuation": {key: PLACEHOLDER for key in ["估值水平", "PE/PB口径差异", "相对行业", "历史位置", "成长匹配"]},
            "technical": {key: PLACEHOLDER for key in ["趋势", "最新量价", "公开资金流", "量价推断", "关键位"]},
            "sentiment": {key: PLACEHOLDER for key in ["短期影响", "公司催化", "资本与群体情绪", "突发风险", "补充核验"]},
            "judgment": {key: PLACEHOLDER for key in ["综合判断", "证据链一", "证据链二", "证据链三", "适合的研究场景", "乐观情景", "中性情景", "悲观情景", "观察条件", "失效条件", "方法论说明"]},
            "risks": {"重点跟踪": PLACEHOLDER, "价格跟踪": PLACEHOLDER},
        },
        "sources": [f"东方财富公开行情与财务接口（{ticker}）", "公司年度报告（待核验）", "公司最新季度报告及交易所公告（待核验）"],
        "numeric_validation": [],
        "semantic": {"required_terms": [identity["name"], ticker], "forbidden_terms": []},
        "pending_verification": ["公司身份与交易状态", "年度及季度财务数据", "估值及同业比较", "公告催化机制", "全部数字复算轨迹"],
        "disclaimer": "仅供学习研究，不构成投资建议",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    pack = draft_pack(evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
