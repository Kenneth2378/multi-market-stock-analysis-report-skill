---
name: a-share-stock-report
description: Generate lightweight stock research PDF reports for A-shares, B-shares, Hong Kong stocks, and US stocks. Use when the user asks for stock analysis reports, recent three-month price action, valuation, fundamentals, news/sentiment, public price-volume inference, research judgment framework, PDF output, or quality_check.md validation.
---

# Multi-Market Stock Report

Use this skill when the user asks for stock research reports, especially lightweight PDF reports for A-shares, B-shares, Hong Kong stocks, and US stocks.

Default behavior must remain backward compatible: generate a lightweight PDF report plus `quality_check.md`.

Private workflows are not included in this public repository.

## Required stance

- Treat all market data as time-sensitive. Verify the latest available complete trading day, price, valuation, announcements, and financial results before writing the report.
- Include a clear disclaimer in every report: `仅供学习研究，不构成投资建议`.
- State the market, ticker, currency, latest complete trading day, time zone, and data-source limitations for each stock.
- Phrase `主力/资金动向` as `公开量价资金推断` or `public price-volume inference` from observable public signals only: price, volume, turnover, amplitude, gaps, high-volume up/down days, short interest, institutional ownership, support/resistance, and market context. Do not present it as confirmed account-level behavior.
- Use `研究判断 / 投资判断框架`, not direct transaction commands.
- Use `适合的研究场景`, not `适合的投资者`.
- Use `观察区间 / 风险参考区间`, not direct buy/sell zones.
- Cite data sources by name or link. Summarize facts in original wording. Do not copy full articles, long copyrighted passages, proprietary reports, paid data, API keys, cookies, account names, personal local paths, or private files.
- Do not output trading commands, follow-trade language, guaranteed-return language, target-return language, or direct transaction language.

## Workflow

### 1. Identify securities

- Resolve each company name to stock code, market, exchange suffix, and trading currency.
- Examples:
  - A股深市: `002698.SZ`, Eastmoney `0.002698`
  - A股沪市: `600845.SH`, Eastmoney `1.600845`
  - B股沪市: `900926.SH`, Eastmoney `1.900926`, usually USD-denominated
  - B股深市: `200xxx.SZ`, Eastmoney `0.200xxx`, usually HKD-denominated
  - 港股: `00241.HK` or `0241.HK`, commonly Eastmoney `116.00241`, Yahoo/StockAnalysis `0241.HK`
  - 美股: `TSLA`, `NVDA`, `AAPL`, Yahoo/StockAnalysis ticker symbols
- If sources disagree on ticker, market, currency, trading status, or latest data date, label the conflict and do not force a conclusion.

### 2. Gather current and historical market data

- Pull daily K-line data for at least the most recent three calendar months.
- Include date, open, close, high, low, volume, amount when available, amplitude, percent change, and turnover when available.
- Pull quote and valuation fields where available: latest complete close, prior close, intraday price if relevant, volume/amount, turnover, total market cap, float market cap, PE, PB, PS, and industry.
- For A股 and B股, a usable Eastmoney daily K-line pattern:

```text
https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=<SECID>&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=<YYYYMMDD>&end=<YYYYMMDD>
```

- A usable Eastmoney batch quote pattern:

```text
https://push2.eastmoney.com/api/qt/ulist.np/get?secids=<SECID1>,<SECID2>&fields=f12,f14,f2,f3,f4,f5,f6,f8,f9,f20,f21,f23,f100
```

- For 港股 and 美股, use reliable public alternatives when Eastmoney is incomplete or unstable: StockAnalysis, Yahoo Finance historical data, Nasdaq, NYSE, HKEX, company investor-relations pages, MarketWatch, Investing, AAStocks, Futu, or other public quote pages.
- Keep market-specific caveats in the report. For example, B股 liquidity may be low, 港股 turnover may differ by source, and 美股 latest data uses US market dates.

### 3. Numeric validation gate

Run this gate before generating the PDF, chart, `quality_check.md`, or final response:

1. Validate `price x share count = market cap`; check unit and currency consistency.
2. Do not mix latest close, prior close, intraday price, and after-hours price. Label each price basis clearly.
3. Recalculate YoY, QoQ, and period return from source numbers.
4. Check unit consistency for 亿、万亿、million、billion、trillion.
5. State the source basis for PE, PB, PS, total market cap, float market cap, and share count.
6. If two sources conflict, label the conflict and do not force a conclusion.
7. If key data cannot be verified, write `数据待核验`. Do not invent data.
8. Public price-volume inference must be written as inference only, not real account behavior.
9. Do not output trading commands, follow-trade language, guaranteed-return language, target-return language, or direct transaction language.

Every numeric validation item must leave a reproducible trail in `quality_check.md`:

- raw field
- data source
- date
- unit
- formula
- calculated result
- source result
- difference ratio
- `PASS` / `NEEDS_REVIEW` / `FAIL`

If the numeric validation gate fails, mark the output as `NEEDS_REVIEW` and clearly state what needs review.

### 4. Gather fundamentals and news

- Verify latest annual report and latest quarterly report from company announcements, exchange filings, CNINFO, HKEXnews, SEC filings, company investor-relations pages, Eastmoney/F10, Sina Finance, StockAnalysis, or another public source.
- Capture revenue, YoY growth, net profit attributable to parent, gross margin/net margin when available, operating cash flow, total assets/equity/liabilities or leverage, and major governance/shareholder notes.
- Check recent company announcements and major news. Prefer dated, sourceable facts over vague market rumors.
- For copyrighted news and research reports, use short summaries and source names/links only. Avoid reproducing large excerpts or full tables unless the source license clearly permits it.

### 5. Compute technical summary

- For the three-month window, compute start close, latest close, period return, period high/low with dates, 20-day MA, 60-day MA when available, average turnover or volume, average transaction amount when available, top high-volume days, and a simple 14-day RSI if helpful.
- Interpret structure as public price-volume inference:
  - High-volume rise followed by failure to hold: possible short-term distribution or speculative retreat.
  - High-volume breakout with continued elevated turnover: strong capital contest and possible active-money participation.
  - High-volume down days after a high platform: high-position disagreement and possible profit-taking.
  - Shrinking volume near support: possible stabilization, but require follow-up confirmation.
- For US stocks, include large-cap context where useful: index weight, institutional ownership, short interest trend, options/event volatility, and major earnings/news catalysts.

### 6. Form the research judgment framework

- Add a `研究判断与方法论` section to every report. This section is a research conclusion, not a buy/sell command.
- The judgment must be evidence-based and explain the reasoning chain. Avoid vague labels such as `看好` or `谨慎` without support.
- Use this framework:
  - Fundamental direction: revenue/profit trend, margin trend, cash-flow quality, balance-sheet risk, governance quality.
  - Valuation position: PE/PB/PS/EV metrics where available, historical range, peer comparison, and whether growth can justify valuation.
  - Price/volume confirmation: trend, support/resistance, volume behavior, high-volume up/down days, and whether price confirms the fundamental story.
  - Catalyst and sentiment: earnings, policy, product cycle, industry theme, analyst/institution view, and crowd sentiment where sourceable.
  - Risk-reward framing: upside/base/downside scenarios and the trigger that would invalidate the judgment.
- Use clear non-transaction language:
  - `综合判断`: e.g. `偏积极但需等待确认`, `中性观察`, `高波动成长跟踪`, `风险偏高需复核`.
  - `适合的研究场景`: growth, value, dividend, event-driven, short-term observation, long-term tracking.
  - `观察条件`: what must happen before the view improves.
  - `失效条件`: what would make the view wrong.
  - `方法论说明`: which signals carried the most weight and why.
- If the user asks for buy/sell zones, phrase them as observation zones or risk reference zones with clear caveats, not as direct orders.

### 7. Report structure

Follow this Chinese outline unless the user asks otherwise:

1. `一、核心结论`
2. `二、基本面分析`
   - 业务模式
   - 赚钱能力
   - 成长性
   - 偿债与资产质量
   - 现金流质量
   - 公司治理与股东背景
3. `三、估值面分析`
   - PE/PB/PS and relative industry position
   - historical valuation position
   - multi-metric valuation view
   - growth/price match
   - dividend suitability if relevant
4. `四、技术面与近三个月公开量价资金推断`
5. `五、消息与市场情绪`
6. `六、研究判断与方法论`
   - comprehensive judgment
   - evidence chain
   - suitable research scenario
   - upside/base/downside scenarios
   - observation and invalidation conditions
7. `七、风险提示与跟踪要点`
8. `主要数据来源`

### 8. Chart and PDF output

- Generate one recent-three-month price/volume chart per stock. A simple line chart for closing price plus volume bars is sufficient; label the latest data date.
- Show the trading currency on the chart/report: RMB, USD, or HKD.
- Prefer a stable local pipeline:
  - Build a static HTML report with Chinese fonts such as Microsoft YaHei/SimHei/SimSun.
  - Embed the local chart image.
  - Export to PDF with local Chrome or Edge headless printing.
- If the workspace is read-only, request filesystem approval before creating report files.
- Save one PDF per stock with clear Chinese filenames, for example `中际旭创_股票分析报告.pdf`, `阿里健康_股票分析报告.pdf`, or `特斯拉_股票分析报告.pdf`.
- Generate a sibling quality check file such as `workspace/reports/中际旭创_quality_check.md`.

### PDF Privacy Requirement

When exporting HTML to PDF, the browser default header and footer must be disabled.

If using Chrome or Edge headless printing, use a header/footer-free export option such as:

```text
--no-pdf-header-footer
```

If using Playwright or Puppeteer, set:

```text
displayHeaderFooter: false
```

After PDF generation, extract PDF text with a reliable parser such as `pypdf`, `PyMuPDF`, `pdfminer.six`, `pdftotext`, or `mutool`, and scan for local paths or credential-like keywords:

```text
file://
D:/
D:\CodeX
C:/
C:\Users
/Users/
api_key
token
cookie
secret
password
```

If any local path or credential-like keyword is found in the generated PDF, `quality_check.md` must mark the privacy scan as `FAIL` or `NEEDS_REVIEW`. Do not mark the privacy scan as `PASS`.


## Quality checks

Every report must include a `quality_check.md` file.

Minimum fields:

- 股票名称、ticker、市场、货币
- 最新完整交易日
- 价格口径是否一致
- 市值计算是否通过
- 涨跌幅计算是否通过
- 三个月区间涨幅是否通过
- 估值指标来源
- 图表文件是否存在
- PDF 文件是否存在且非空
- 是否包含免责声明
- 是否包含数据来源
- 是否发现本地路径、账号、API key、cookie 或隐私信息
- 是否出现禁止词或交易诱导语
- 每个数字校验的原始字段、数据来源、日期、单位、公式、计算结果、来源结果、差异比例和结论
- 数据冲突字段、冲突来源、暂采用口径
- 数据待核验字段
- 最终结论: `PASS` / `NEEDS_REVIEW` / `FAIL`

Before final response:

- Confirm all requested PDFs exist and have nonzero file sizes.
- Confirm each report states the latest market data date.
- Confirm each report has a chart, core conclusion, fundamentals, valuation, technical/public price-volume inference, news/sentiment, research judgment/methodology, risks, and data sources.
- Confirm each research judgment is supported by concrete evidence and includes observation conditions plus invalidation conditions.
- Confirm each report states market, ticker, currency, latest complete trading day, and source limitations if any.
- Confirm the report includes the disclaimer: `仅供学习研究，不构成投资建议`.
- Confirm the report does not expose personal paths, account names, credentials, screenshots, API keys, cookies, tokens, or private files.
- Confirm data sources are cited by name or link, and source content is summarized rather than copied at length.
- If `quality_check.md` is not `PASS`, tell the user what must be reviewed.
- Keep the final response short and link generated PDF files.
