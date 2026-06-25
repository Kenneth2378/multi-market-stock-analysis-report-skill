# quality_check.md Schema

Every generated stock report must include a sibling `quality_check.md`.

Generate the file through `scripts/validate_report.py` or the validator called by `scripts/generate_stock_report.py`. Do not hand-author a PASS result.

## Required Status Fields

- Stock name
- Ticker
- Market
- Currency
- Latest complete trading day
- Price basis consistency
- Market cap validation
- Return recalculation validation
- Three-month period return validation
- Valuation metric sources
- Chart file exists
- PDF file exists and is non-empty
- Disclaimer exists
- Data sources exist
- Forbidden transaction or promotion language scan
- Semantic consistency scan
- Research depth gate
- Legacy report content contract: fundamentals 6, valuation 5, technical/price-volume 5, news/sentiment 4, and full judgment framework
- PDF Privacy Scan
- Data pending verification fields
- Final Conclusion: `PASS` / `NEEDS_REVIEW` / `FAIL`

## PDF Privacy Scan

Record all of the following:

- PDF export method
- PDF text extractor
- Privacy keyword list
- Hit list
- Whether `file-scheme` path markers were found
- Whether Windows drive path markers were found
- Whether user directory markers were found
- PDF Privacy Scan: `PASS` / `FAIL`

The scan must use final extracted PDF text and the hard gate:

```text
python scripts/scan_pdf_privacy.py path/to/report.pdf
```

Do not rely only on HTML, SVG, browser flags, or raw zlib stream scans. If the command returns non-zero, the generated report cannot be marked `PASS`.

Minimum privacy keywords:

```text
file://
D:/
D:\
D:\CodeX
C:/
C:\
C:\Users
/Users/
\Users\
api_key
token
cookie
secret
password
```

## Final Conclusion Rule

- If PDF privacy scan hits any privacy keyword: `Final Conclusion` must be `FAIL` or `NEEDS_REVIEW`.
- If PDF privacy scan passes but data pending verification fields remain: `Final Conclusion` must be `NEEDS_REVIEW`.
- If any company, exchange/board, risk-label, industry, catalyst, scenario, or risk statement is mismatched: `Final Conclusion` must be `FAIL`.
- If the report only lists announcements, omits key financial depth, lacks peer/historical valuation context without explanation, or uses generic scenarios: `Final Conclusion` must be `NEEDS_REVIEW`.
- If any required legacy-contract item lacks target-specific facts, numbers, interpretation, or source trail: `Final Conclusion` must be `NEEDS_REVIEW`.
- A report materially less substantive than the supplied legacy benchmark cannot be `PASS` merely because headings or keywords are present.
- Section presence or file existence alone never proves content quality.
- `Final Conclusion: PASS` is allowed only when privacy, forbidden-language, numeric, semantic, research-depth, and key-data verification gates all pass.
