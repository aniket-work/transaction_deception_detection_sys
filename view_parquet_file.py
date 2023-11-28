import pandas as pd

# Read the Parquet file
parquet_file = "raw_data/transactions.parquet"
data = pd.read_parquet(parquet_file)

# Print the column names to check for exact names
print(data.columns)

# Perform filtering based on the exact column names
selected_columns = [
    "transactionid",
    "transactionamt",
    "p_emaildomain",
    "isfraud"
]

if all(col in data.columns for col in selected_columns):
    selected_data = data[selected_columns]
    print(selected_data.head())
else:
    print("Column names do not match. Please adjust the column names for filtering.")


# Filter based on conditions
fraudulent_transactions = data[data["isfraud"] == 1]
print(fraudulent_transactions.head())
