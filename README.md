# Truth Layer – AI Fact Checking Agent

Truth Layer is a production-grade automated fact-checking engine designed to scan PDFs (e.g., marketing materials, whitepapers, financial reports), isolate quantitative claims, and audit them against live web evidence using generative AI.

## Technical Architecture
- **Text Extraction:** `pdfplumber` for structured textual processing.
- **Claims Analysis:** `gpt-4o-mini` extracts structured claims matching statistical parameters.
- **Live Search Verification:** Concurrent lookup protocol using DuckDuckGo Search APIs.
- **Cross-Referencing Engine:** JSON schema evaluation contrasting live snippets against claims.

## Quickstart Guide

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone [https://github.com/yourusername/truth-layer-agent.git](https://github.com/yourusername/truth-layer-agent.git)
   cd truth-layer-agent
