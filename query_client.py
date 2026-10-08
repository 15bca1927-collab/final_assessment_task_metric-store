from engine.executor import SemanticEngine
from tabulate import tabulate

def run_demo():
    engine = SemanticEngine()

    print("=" * 70)
    print(" WEALTH MANAGEMENT SEMANTIC LAYER / METRIC STORE")
    print("=" * 70)

    # Demo Query 1
    print("\n[SCENARIO 1] Executive View: Total AUM & Cash by Client Segment")
    sql1 = engine.get_sql(metrics=["total_aum", "total_cash_held"], dimensions=["client_tier"])
    print("\nCompiled SQL:\n" + "-" * 40)
    print(sql1)
    print("-" * 40)
    df1 = engine.query(metrics=["total_aum", "total_cash_held"], dimensions=["client_tier"])
    print(tabulate(df1, headers="keys", tablefmt="rounded_grid", floatfmt=",.2f"))

    # Demo Query 2
    print("\n[SCENARIO 2] Advisory Performance: Net Flows & Fee Capture by Advisor")
    sql2 = engine.get_sql(
        metrics=["gross_deposits", "gross_withdrawals", "net_new_money", "total_fees_collected"],
        dimensions=["advisor_id"],
        order_by="net_new_money DESC"
    )
    print("\nCompiled SQL:\n" + "-" * 40)
    print(sql2)
    print("-" * 40)
    df2 = engine.query(
        metrics=["gross_deposits", "gross_withdrawals", "net_new_money", "total_fees_collected"],
        dimensions=["advisor_id"],
        order_by="net_new_money DESC"
    )
    print(tabulate(df2, headers="keys", tablefmt="rounded_grid", floatfmt=",.2f"))

if __name__ == "__main__":
    run_demo()
