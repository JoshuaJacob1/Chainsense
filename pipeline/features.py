import duckdb

def build_wallet_features(con, tx_table, blocks_table):
    """
    Step 2: Basic ML features extraction.
    We need to collapse raw transactions into a 1D vector per wallet.
    Features: volume, contract call ratio, tx count, gas fee stats, etc.
    """
    
    # Simple selector categories for intent shares
    # (these are hex signatures for common eth methods)
    transfer_sigs = "('0xa9059cbb', '0x23b872dd')"
    swap_sigs = "('0x3593564c', '0x791ac947', '0x7ff36ab5')"
    
    query = f"""
    WITH base_tx AS (
        SELECT 
            t.from_address AS wallet,
            date_trunc('hour', t.block_timestamp) AS hour,
            t.status,
            t.to_address,
            t.method_selector,
            CAST(t.effective_gas_price_wei AS DOUBLE) AS gas_price,
            (c.address IS NOT NULL) AS is_contract_call
        FROM {tx_table} t
        LEFT JOIN contracts_table c ON c.address = t.to_address
    ),
    wallet_agg AS (
        SELECT 
            wallet,
            COUNT(*) as tx_count,
            AVG(CASE WHEN status = 0 THEN 1.0 ELSE 0.0 END) as failed_tx_ratio,
            AVG(CASE WHEN is_contract_call THEN 1.0 ELSE 0.0 END) as contract_ratio,
            AVG(CASE WHEN method_selector IN {transfer_sigs} THEN 1.0 ELSE 0.0 END) as transfer_share,
            AVG(CASE WHEN method_selector IN {swap_sigs} THEN 1.0 ELSE 0.0 END) as swap_share,
            median(gas_price) as median_gas
        FROM base_tx
        GROUP BY 1
    )
    SELECT * FROM wallet_agg
    """
    
    return con.execute(query).df()

if __name__ == "__main__":
    # Test script stuff
    print("Testing feature extraction...")
    # conn = duckdb.connect("local_data.db")
    # df = build_wallet_features(conn, "raw_txs", "raw_blocks")
    # print(df.head())
