import pandas as pd
from datetime import datetime, timedelta

def normalize_transaction_dt(df):
    """
    Normalize the 'TransactionDT' column values to a range between 0 and 1.

    Parameters:
    - df: DataFrame containing the transaction data.

    Returns:
    - df: DataFrame with normalized 'TransactionDT' column.
    """
    df["TransactionDT"] = df["TransactionDT"] / df["TransactionDT"].max()
    return df

def create_transaction_gr_timestamp(df):
    """
    Create 'transaction_gr_timestamp' and 'trans_created_timestamp' columns based on 'TransactionDT'.

    Parameters:
    - df: DataFrame containing the transaction data.

    Returns:
    - df: DataFrame with added 'transaction_gr_timestamp' and 'trans_created_timestamp' columns.
    """
    end_date = datetime.today()
    start_date = (end_date - timedelta(days=365)).timestamp()
    end_date = end_date.timestamp()

    # Calculate 'transaction_gr_timestamp' based on 'TransactionDT'
    df["transaction_gr_timestamp"] = pd.to_datetime(
        df["TransactionDT"].apply(lambda x: round(start_date + x * (end_date - start_date))),
        unit="s"
    )
    # Copy 'transaction_gr_timestamp' to create 'trans_created_timestamp'
    df["trans_created_timestamp"] = df["transaction_gr_timestamp"].copy()
    return df

def select_and_rename_columns(df):
    """
    Select specific columns and rename them to lowercase.

    Parameters:
    - df: DataFrame containing the transaction data.

    Returns:
    - df: DataFrame with selected columns and lowercase column names.
    """
    selected_columns = [
        "TransactionID", "ProductCD", "TransactionAmt", "P_emaildomain",
        "R_emaildomain", "card4", "M1", "M2", "M3", "trans_created_timestamp",
        "transaction_gr_timestamp", "isFraud"
    ]
    # Select specific columns and convert column names to lowercase
    df = df[selected_columns]
    df.columns = [x.lower() for x in df.columns]
    return df

def save_as_parquet(df, filename):
    """
    Save DataFrame as a Parquet file.

    Parameters:
    - df: DataFrame to be saved.
    - filename: Name of the output Parquet file.
    """
    df.to_parquet(filename)

# Read the CSV file
input_file = "raw_data/transactions.csv"
output_file = "raw_data/transactions.parquet"
data = pd.read_csv(input_file)

# Apply transformations
data = normalize_transaction_dt(data)
data = create_transaction_gr_timestamp(data)
data = select_and_rename_columns(data)

# Save as Parquet file
save_as_parquet(data, output_file)
