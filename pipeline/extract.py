import os
from google.cloud import bigquery

# We need to pull the raw ethereum data from somewhere to feed the model.
# Using BigQuery public datasets to build our initial "bronze" parquet layer.
# Make sure to run `gcloud auth application-default login` before running this!

BRONZE_DIR = os.path.join(os.path.dirname(__file__), "../data/bronze")

def extract_blocks(client, start_block, end_block):
    print(f"Extracting blocks {start_block} to {end_block}...")
    query = f"""
    SELECT 
        number as block_number,
        timestamp as block_timestamp,
        base_fee_per_gas as base_fee_per_gas_wei
    FROM `bigquery-public-data.crypto_ethereum.blocks`
    WHERE number BETWEEN {start_block} AND {end_block}
    """
    df = client.query(query).to_dataframe()
    
    out_path = os.path.join(BRONZE_DIR, "blocks", f"blocks_{start_block}_{end_block}.parquet")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_parquet(out_path, index=False)
    print(f"Saved {len(df)} blocks.")

def extract_transactions(client, start_block, end_block):
    print(f"Extracting txs {start_block} to {end_block}...")
    # Grabbing just the fields we actually need for the behavioral features
    query = f"""
    SELECT 
        block_number,
        block_timestamp,
        from_address,
        to_address,
        value as value_wei,
        gas_price as effective_gas_price_wei,
        receipt_status as status,
        SUBSTR(input, 1, 10) as method_selector
    FROM `bigquery-public-data.crypto_ethereum.transactions`
    WHERE block_number BETWEEN {start_block} AND {end_block}
    """
    df = client.query(query).to_dataframe()
    
    out_path = os.path.join(BRONZE_DIR, "transactions", f"txs_{start_block}_{end_block}.parquet")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_parquet(out_path, index=False)
    print(f"Saved {len(df)} transactions.")

if __name__ == "__main__":
    # TODO: need to wire this up to a state tracker so we don't redownload blocks
    try:
        bq_client = bigquery.Client()
        # Just grabbing a 10-block slice for testing
        extract_blocks(bq_client, 19000000, 19000010)
        extract_transactions(bq_client, 19000000, 19000010)
    except Exception as e:
        print("BQ Error (did you set up auth?) ->", e)
