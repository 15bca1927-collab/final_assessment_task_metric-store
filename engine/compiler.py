from typing import List, Optional, Dict
from engine.catalog import MetricCatalog

class SQLCompiler:
    def __init__(self, catalog: MetricCatalog):
        self.catalog = catalog

    def compile(
        self,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[Dict[str, str]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> str:
        dimensions = dimensions or []
        filters = filters or {}

        if not metrics:
            raise ValueError("At least one metric must be requested.")

        # Determine target semantic model
        target_model_name = None
        for m in metrics:
            model = self.catalog.get_model_for_metric(m)
            if target_model_name is None:
                target_model_name = model["name"]
            elif target_model_name != model["name"]:
                raise ValueError(
                    f"Composite query across '{target_model_name}' and '{model['name']}' "
                    f"requires separate semantic queries."
                )

        model = self.catalog.models[target_model_name]
        source_table = model["source_table"]

        # Index joins and exposed dimensions
        joins = model.get("joins") or []
        needed_targets = set()
        dim_to_expr = {}

        for j in joins:
            target_table = j.get("target")
            for exp in j.get("exposed_dimensions", []):
                dim_name = exp.get("name")
                dim_expr = exp.get("expr")
                dim_to_expr[dim_name] = (target_table, dim_expr)

        # 1. Dimensions
        select_clauses = []
        group_by_indices = []
        col_idx = 1

        for dim in dimensions:
            if dim in dim_to_expr:
                target_tbl, expr = dim_to_expr[dim]
                needed_targets.add(target_tbl)
                select_clauses.append(f"{expr} AS {dim}")
            else:
                select_clauses.append(f"{dim}")
            group_by_indices.append(str(col_idx))
            col_idx += 1

        # 2. Metrics
        metric_defs = {m["name"]: m for m in model.get("metrics", [])}
        for m in metrics:
            m_def = metric_defs[m]
            m_type = m_def.get("type")
            if m_type == "sum":
                select_clauses.append(f"SUM({m_def['expr']}) AS {m}")
            elif m_type == "avg":
                select_clauses.append(f"ROUND(AVG({m_def['expr']}), 2) AS {m}")
            elif m_type == "custom":
                select_clauses.append(f"{m_def['sql']} AS {m}")
            else:
                select_clauses.append(f"COUNT(*) AS {m}")
            col_idx += 1

        # 3. Filters
        where_clauses = []
        for k, v in filters.items():
            if k in dim_to_expr:
                target_tbl, expr = dim_to_expr[k]
                needed_targets.add(target_tbl)
                where_clauses.append(f"{expr} = '{v}'")
            else:
                where_clauses.append(f"{k} = '{v}'")

        # 4. From and Joins
        from_clause = f"FROM {source_table}"
        for j in joins:
            if j.get("target") in needed_targets:
                j_type = j.get("type", "inner").upper()
                target = j.get("target")
                on_cond = j.get("on_condition") or j.get("on") or j.get(True)
                from_clause += f"\n{j_type} JOIN {target} ON {on_cond}"

        query = f"SELECT\n  " + ",\n  ".join(select_clauses) + f"\n{from_clause}"
        if where_clauses:
            query += f"\nWHERE " + " AND ".join(where_clauses)

        if group_by_indices:
            query += f"\nGROUP BY " + ", ".join(group_by_indices)

        if order_by:
            query += f"\nORDER BY {order_by}"
        elif group_by_indices:
            query += f"\nORDER BY 1 ASC"

        if limit:
            query += f"\nLIMIT {limit}"

        return query
