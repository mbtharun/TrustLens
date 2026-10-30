import pyarrow.parquet as pq
from collections import Counter

PATH = "data/benchmark/data/test-00000-of-00001.parquet"

table = pq.read_table(PATH)
print("Rows:", table.num_rows)
print("Columns:", table.column_names)
print("Schema:")
print(table.schema)

df = table.to_pandas()
for col in df.columns:
    if df[col].dtype == object and df[col].map(lambda v: isinstance(v, str)).all() and df[col].nunique() < 50:
        print(f"\nValue counts for '{col}':")
        print(df[col].value_counts())

print("\nFirst row (non-image fields):")
print({k: v for k, v in df.iloc[0].items() if not isinstance(v, dict) and not isinstance(v, bytes)})