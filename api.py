from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from engine.executor import SemanticEngine

app = FastAPI(
    title="Wealth Management Semantic Metric Store",
    version="1.0.0",
    description="A centralized semantic layer for financial metrics, ensuring governed metrics without ad-hoc SQL drift."
)

engine = SemanticEngine()

class MetricQueryRequest(BaseModel):
    metrics: List[str]
    dimensions: Optional[List[str]] = []
    filters: Optional[Dict[str, str]] = {}
    order_by: Optional[str] = None
    limit: Optional[int] = 100

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "Wealth Semantic Layer",
        "metrics_registered": len(engine.catalog.list_available_metrics())
    }

@app.get("/api/v1/metrics")
def list_metrics():
    """Retrieve catalog of all governed business metrics."""
    return {
        "total_metrics": len(engine.catalog.list_available_metrics()),
        "metrics": engine.catalog.list_available_metrics()
    }

@app.post("/api/v1/query")
def execute_metric_query(req: MetricQueryRequest):
    """
    Execute a governed metric query.
    Compiles declarative metric requests into executable SQL dynamically.
    """
    try:
        compiled_sql = engine.get_sql(
            metrics=req.metrics,
            dimensions=req.dimensions,
            filters=req.filters
        )
        
        df = engine.query(
            metrics=req.metrics,
            dimensions=req.dimensions,
            filters=req.filters,
            order_by=req.order_by,
            limit=req.limit
        )

        # Convert NaN/inf to clean types for JSON serialization
        records = df.to_dict(orient="records")

        return {
            "status": "success",
            "metrics": req.metrics,
            "dimensions": req.dimensions,
            "row_count": len(records),
            "compiled_sql": compiled_sql,
            "data": records
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine execution error: {str(e)}")

@app.post("/api/v1/sql/dry-run")
def preview_sql(req: MetricQueryRequest):
    """Generate the compiled SQL without executing it against the warehouse."""
    try:
        compiled_sql = engine.get_sql(
            metrics=req.metrics,
            dimensions=req.dimensions,
            filters=req.filters
        )
        return {
            "status": "success",
            "compiled_sql": compiled_sql
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
