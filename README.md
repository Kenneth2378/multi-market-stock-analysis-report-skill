# Multi-Market Stock Report Skill

Codex skill name: `a-share-stock-report`

This project was previously introduced as **Multi-Market Stock Report Skill**. The Codex skill name remains `a-share-stock-report`.

本项目早期曾以 **Multi-Market Stock Report Skill** 介绍；为兼容老用户，Codex 调用名仍为 `a-share-stock-report`。

一个用于生成 A股、B股、港股和美股股票研究 PDF 报告的 Codex Skill，覆盖基本面、估值、技术面、公开量价资金推断、消息情绪和研究判断框架。仅供学习研究，不构成投资建议。

A Codex Skill for generating lightweight PDF stock research reports across A-shares, B-shares, Hong Kong stocks, and US stocks, covering fundamentals, valuation, technical analysis, public price-volume inference, news sentiment, and a research judgment framework. For research and learning only. Not investment advice.

If this skill is useful, please consider giving it a Star.
如果这个 Skill 对你有帮助，欢迎点一个 Star 支持。

Private workflows are not included in this public repository.

## Backward Compatibility

- Existing prompts continue to work.
- The default behavior remains a lightweight stock research PDF report.
- The public Codex skill name remains `a-share-stock-report`.
- Each report should generate a sibling `quality_check.md`.

## Public Community Scope

This public version supports:

- Lightweight stock research PDF reports.
- A-share, B-share, Hong Kong stock, and US stock research.
- Recent three-month price and volume chart.
- Fundamentals, valuation, technical analysis, news/sentiment, and public price-volume inference.
- Research judgment and methodology.
- Observation conditions, invalidation conditions, and risk warnings.
- Numeric validation gate.
- `quality_check.md`.
- Data-source citation, copyright boundary, disclaimer, and private-information protection.

## Example Reports

- A-share example: 中际旭创
- US stock example: NVIDIA
- Stable income example: 京沪高铁

## What This Skill Generates

- PDF stock research report.
- Recent 3-month chart.
- Fundamentals.
- Valuation.
- Technical analysis.
- Public price-volume inference.
- Research judgment framework.
- Observation and invalidation conditions.
- Risk disclaimer.
- `quality_check.md`.

## Features

- Resolve stock names, codes, markets, and trading currencies.
- Gather recent market data and financial information.
- Analyze fundamentals, valuation, technical structure, news, sentiment, and observable public price-volume signals.
- Add an evidence-based research judgment with methodology, scenarios, observation conditions, and invalidation conditions.
- Generate Chinese PDF reports with charts.
- Include data sources and risk disclaimers.
- Support market-specific caveats for A股、B股、港股、美股.

## Numeric Validation Gate

Before producing the final report, the Skill should validate:

- `price x share count = market cap`, with unit and currency checks.
- Latest close, prior close, intraday price, and after-hours price are not mixed.
- YoY, QoQ, and period return are recalculated from source numbers.
- Units are consistent across 亿、万亿、million、billion、trillion.
- PE, PB, PS, market cap, and share-count source bases are stated.
- If data conflicts, label the conflict and do not force a conclusion.
- If key data cannot be verified, write `数据待核验`.

## Installation

Copy this folder into your Codex skills directory:

```text
~/.codex/skills/a-share-stock-report
```

Then restart Codex.

## Example Prompts

```text
用 a-share-stock-report skill 分析伊泰B股
```

```text
用 a-share-stock-report skill 分析比亚迪
```

```text
用 a-share-stock-report skill 分析中际旭创
```

```text
用 a-share-stock-report skill 分析特斯拉
```

```text
用 a-share-stock-report skill 分析 NVDA
```

## Supported Markets

| Market | Examples | Currency Notes |
| --- | --- | --- |
| A股 | `300308.SZ`, `600030.SH` | RMB |
| B股 | `900948.SH`, `200xxx.SZ` | Usually USD for Shanghai B-shares and HKD for Shenzhen B-shares |
| 港股 | `09988.HK`, `00763.HK` | HKD |
| 美股 | `TSLA`, `NVDA`, `AAPL` | USD |

## Data And Copyright

This skill may use public market and financial sources such as Eastmoney, StockAnalysis, Yahoo Finance, company announcements, CNINFO, HKEXnews, SEC filings, company investor-relations pages, exchange filings, and financial media.

Reports should cite sources and summarize facts in original wording. Do not copy full articles, long copyrighted passages, proprietary research reports, paid data, API keys, cookies, account information, or personal local paths.

## Disclaimer

Reports generated with this skill are for research and learning only. They do not constitute investment advice or any recommendation to buy, sell, or hold securities.
