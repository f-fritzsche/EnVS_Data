import pandas as pd

FILE = "input/GenerationCapacities.csv"

df = pd.read_csv(FILE)

# Find all rows that have "data_version,Target year,Market_Node" = "ERAA 2025 final,2035,DE00"
df_2035 = df[(df["data_version"] == "ERAA 2025 final") & (df["Target year"] == 2035) & (df["Market_Node"] == "DE00")]

print(df_2035)