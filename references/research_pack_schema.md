# Research Pack Schema

Create one UTF-8 JSON research pack per stock, then run `scripts/generate_stock_report.py`. Do not bypass the pack or the validator.

Required top-level keys:

- `identity`: `name`, `ticker`, `market`, `currency`, `timezone`, `latest_complete_day`, `status`.
- `summary`: display values for `close`, `market_cap`, `pe_pb`, `period_return`.
- `chart`: equal-length `dates`, `close`, and `volume` arrays covering at least three calendar months in production.
- `sections`: every field required by `references/legacy_report_contract.md`.
- `sources`: at least three named sources or links.
- `numeric_validation`: validation trail rows with `name`, `raw`, `source`, `date`, `unit`, `formula`, `calculated`, `source_result`, `difference`, `status`.
- `semantic`: target-specific `required_terms` and `forbidden_terms`.
- `pending_verification`: must be empty for PASS.
- `disclaimer`: include `仅供学习研究，不构成投资建议`.

Use `tests/fixtures/legacy_contract/research_pack.json` as the structural example. The fixture is intentionally short and is for `--validate-only`; production PDFs must still meet the 3537-character depth gate.

Commands:

```text
python scripts/generate_stock_report.py --input research_pack.json --validate-only
python scripts/generate_stock_report.py --input research_pack.json --output-dir reports
python scripts/validate_report.py reports/name.pdf --pack research_pack.json --html reports/name.html
```
