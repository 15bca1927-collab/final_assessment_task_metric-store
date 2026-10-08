# Wealth Management Semantic Layer & Metric Store

A centralized, governed Semantic Layer and Metric Store designed to eliminate **metric drift** across wealth management analytics. Business metrics (Assets Under Management, Net New Money, Advisory Fees) are codified declaratively in YAML and dynamically compiled into optimized SQL executed against an embedded analytical DuckDB warehouse.

---

## The Problem: Metric Drift in Wealth Management

In distributed analytics environments, business metrics often drift due to disparate ad-hoc SQL implementations across teams:
* **Inconsistent Logic:** Finance may define Net Inflow as `Deposits - Withdrawals`, whereas operations includes fee deductions, producing conflicting reports.
* **Repetitive Boilerplate:** Analysts constantly re-write complex multi-table joins and aggregation conditions across various BI tools.
* **Schema Coupling:** Upstream database changes break scattered ad-hoc queries across reports and dashboards.

This project resolves these issues by acting as a **single source of truth** between raw data storage and downstream consumption layers (REST APIs, BI tools, and CLIs).

---

## Architecture Overview

* **Storage Layer:** Embedded DuckDB analytical store (`data/warehouse.duckdb`) providing local columnar execution.
* **Semantic Catalog (`models/semantic/`):** Declarative YAML specifications mapping metric aggregations, dimensions, and join dependencies.
* **Compilation Engine (`engine/`):**
  * `catalog.py`: In-memory catalog parser and indexer.
  * `compiler.py`: Dynamic SQL compiler resolving join graphs (e.g., auto-joining `dim_accounts` only when account/advisor attributes are requested).
  * `executor.py`: Safe, read-only analytical execution engine with SQL dry-run capabilities.
* **Consumption Layer:**
  * `api.py`: FastAPI server serving governed metrics via JSON endpoints with SQL auditability.
  * `query_client.py`: Terminal analytics dashboard.
  * `tests/test_metrics.py`: Pytest verification and integration suite.

---

## Setup & Quickstart

### 1. Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install duckdb pyyaml pydantic pandas fastapi uvicorn tabulate pytest