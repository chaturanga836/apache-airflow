import json
import uuid
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.PostgresHook import PostgresHook

def get_last_watermark(tenant_id, source_key):
    hook = PostgresHook(postgres_conn_id='postgres_default')
    sql = "SELECT last_value FROM watermark_states WHERE tenant_id = %s AND source_key = %s"
    result = hook.get_first(sql, parameters=(tenant_id, source_key))
    return result[0] if result else "0" # Default to 0 for new syncs

def sync_and_convert_logic(**kwargs):
    conf = kwargs['dag_run'].conf
    tenant_id = conf.get('tenant_id')
    source_key = conf.get('source_key')
    target_fiat = conf.get('target_fiat', 'LKR')

    # 1. Get Watermark
    last_val = get_last_watermark(tenant_id, source_key)
    print(f"Syncing {source_key} starting from watermark: {last_val}")

    # 2. MOCK EXTRACTION (Simulating ETH Wallet Data)
    # In reality, this would be a Web3.py call or Etherscan API
    raw_eth_data = [
        {"tx_hash": "0xabc1", "eth_amount": 0.5, "timestamp": "2026-03-29T10:00:00Z"},
        {"tx_hash": "0xabc2", "eth_amount": 1.2, "timestamp": "2026-03-29T14:00:00Z"},
    ]

    # 3. MOCK CONVERSION API (The "Silver" Enrichment)
    # Logic: Get unique days from timestamps and fetch 1 price per day
    mock_eth_price_lkr = 1200000 # Example: 1 ETH = 1.2M LKR
    
    silver_records = []
    for record in raw_eth_data:
        # Transformation Logic
        lkr_value = record['eth_amount'] * mock_eth_price_lkr
        
        silver_records.append({
            "tx_hash": record['tx_hash'],
            "eth_amount": record['eth_amount'],
            "fiat_value": lkr_value,
            "fiat_currency": target_fiat,
            "original_ts": record['timestamp']
        })

    return silver_records

def load_to_silver(**kwargs):
    ti = kwargs['ti']
    conf = kwargs['dag_run'].conf
    records = ti.xcom_pull(task_ids='process_data_task')
    
    hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # Bulk Insert into Silver Layer
    for rec in records:
        sql = """
            INSERT INTO silver_layer_all_tenants (id, tenant_id, workspace_id, source_key, data)
            VALUES (%s, %s, %s, %s, %s)
        """
        hook.run(sql, parameters=(
            str(uuid.uuid4()), 
            conf['tenant_id'], 
            conf['workspace_id'], 
            conf['source_key'], 
            json.dumps(rec)
        ))

    # 4. UPDATE WATERMARK
    # We use the timestamp of the last record processed
    new_watermark = records[-1]['original_ts']
    update_sql = """
        INSERT INTO watermark_states (tenant_id, workspace_id, source_key, last_value, value_type)
        VALUES (%s, %s, %s, %s, 'TIMESTAMP')
        ON CONFLICT (tenant_id, source_key) DO UPDATE SET last_value = EXCLUDED.last_value;
    """
    # Note: Ensure your DB has a UNIQUE constraint on (tenant_id, source_key) for ON CONFLICT
    hook.run(update_sql, parameters=(conf['tenant_id'], conf['workspace_id'], conf['source_key'], new_watermark))

with DAG(dag_id='eth_lkr_pipeline', start_date=datetime(2026, 1, 1), schedule=None) as dag:
    
    process = PythonOperator(task_id='process_data_task', python_callable=sync_and_convert_logic)
    load = PythonOperator(task_id='load_to_silver_task', python_callable=load_to_silver)

    process >> load