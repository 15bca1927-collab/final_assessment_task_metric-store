from engine.executor import SemanticEngine

engine = SemanticEngine()

print("--- AVAILABLE METRICS IN CATALOG ---")
for m in engine.catalog.list_available_metrics():
    print(f"• {m['name']:<22} | Model: {m['model']:<20} | {m['description']}")

print("\n--- QUERY 1: Total AUM & Cash by Client Tier ---")
df1 = engine.query(
    metrics=["total_aum", "total_cash_held"],
    dimensions=["client_tier"]
)
print(df1.to_string(index=False))

print("\n--- QUERY 2: Net New Money & Fees by Advisor ---")
df2 = engine.query(
    metrics=["gross_deposits", "gross_withdrawals", "net_new_money", "total_fees_collected"],
    dimensions=["advisor_id"]
)
print(df2.to_string(index=False))
