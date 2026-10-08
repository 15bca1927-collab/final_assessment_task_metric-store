import pytest
from engine.executor import SemanticEngine

@pytest.fixture
def engine():
    return SemanticEngine()

def test_catalog_metrics_loaded(engine):
    metrics = engine.catalog.list_available_metrics()
    assert len(metrics) == 7
    metric_names = [m["name"] for m in metrics]
    assert "total_aum" in metric_names
    assert "net_new_money" in metric_names

def test_aum_aggregation_query(engine):
    df = engine.query(
        metrics=["total_aum"],
        dimensions=["client_tier"]
    )
    assert not df.empty
    assert "client_tier" in df.columns
    assert "total_aum" in df.columns
    assert df["total_aum"].sum() > 0

def test_joined_dimension_filter(engine):
    df = engine.query(
        metrics=["net_new_money"],
        dimensions=["advisor_id"],
        filters={"client_tier": "HighNetWorth"}
    )
    assert not df.empty
    assert "advisor_id" in df.columns
    assert "net_new_money" in df.columns

def test_invalid_metric_raises_error(engine):
    with pytest.raises(ValueError, match="not defined in semantic catalog"):
        engine.query(metrics=["non_existent_metric"])

def test_sql_dry_run_generation(engine):
    sql = engine.get_sql(
        metrics=["gross_deposits", "gross_withdrawals"],
        dimensions=["advisor_id"]
    )
    assert "SELECT" in sql
    assert "FROM fct_transactions" in sql
    assert "JOIN dim_accounts" in sql
    assert "GROUP BY" in sql
