import duckdb
import pandas as pd
from typing import Dict, Any, List, Optional
from engine.catalog import MetricCatalog
from engine.compiler import SQLCompiler

class SemanticEngine:
    def __init__(self, db_path: str = "data/warehouse.duckdb"):
        self.db_path = db_path
        self.catalog = MetricCatalog()
        self.compiler = SQLCompiler(self.catalog)

    def query(
        self,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[Dict[str, str]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        sql = self.compiler.compile(
            metrics=metrics,
            dimensions=dimensions,
            filters=filters,
            order_by=order_by,
            limit=limit
        )
        con = duckdb.connect(self.db_path, read_only=True)
        try:
            df = con.execute(sql).fetchdf()
            return df
        finally:
            con.close()

    def get_sql(
        self,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[Dict[str, str]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> str:
        return self.compiler.compile(
            metrics=metrics,
            dimensions=dimensions,
            filters=filters,
            order_by=order_by,
            limit=limit
        )
