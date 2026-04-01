import json
import uuid
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
# UPDATED: The modern, correct import path for Airflow 2.x
from airflow.providers.postgres.hooks.postgres import PostgresHook

def get_last_watermark(conn_id, tenant_id, source_key):
    hook = PostgresHook(postgres_conn_id=conn_id)
    sql = "SELECT last_value FROM watermark_states WHERE tenant_id = %s AND source_key = %s"
    result = hook.get_first(sql, parameters=(tenant_id, source_key))
    return result[0] if result else "0"

def sync_and_convert_logic(**kwargs):
    conf = kwargs['dag_run'].conf
    # Validation: Ensure required params exist
    if not conf:
        raise ValueError("No configuration provided in DagRun")

    tenant_id = conf.get('tenant_id')
    source_key = conf.get('source_key')
    target_fiat = conf.get('target_fiat', 'LKR')
    target_conn_id = conf.get('target_conn_id', 'etl_db_conn')

    # 1. Get Watermark
    last_val = get_last_watermark(target_conn_id, tenant_id, source_key)
    print(f"Syncing {source_key} starting from watermark: {last_val}")

    # 2. MOCK EXTRACTION
    raw_eth_data = [
        {"tx_hash": "0xabc1", "eth_amount": 0.5, "timestamp": "2026-03-29T10:00:00Z"},
        {"tx_hash": "0xabc2", "eth_amount": 1.2, "timestamp": "2026-03-29T14:00:00Z"},
    ]

    # 3. MOCK CONVERSION
    mock_eth_price_lkr = 1200000 
    
    silver_records = []
    for record in raw_eth_data:
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
    
    if not records:
        print("No new records to process.")
        return

    target_conn_id = conf.get('target_conn_id', 'etl_db_conn')
    hook = PostgresHook(postgres_conn_id=target_conn_id)
    
    # Use a single connection for the batch to be efficient
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
    new_watermark = records[-1]['original_ts']
    update_sql = """
        INSERT INTO watermark_states (tenant_id, workspace_id, source_key, last_value, value_type)
        VALUES (%s, %s, %s, %s, 'TIMESTAMP')
        ON CONFLICT (tenant_id, source_key) DO UPDATE SET last_value = EXCLUDED.last_value;
    """
    hook.run(update_sql, parameters=(conf['tenant_id'], conf['workspace_id'], conf['source_key'], new_watermark))

with DAG(
    dag_id='eth_lkr_pipeline', 
    start_date=datetime(2026, 1, 1), 
    schedule=None,
    catchup=False  # Good practice for manual/on-demand DAGs
) as dag:
    
    process = PythonOperator(task_id='process_data_task', python_callable=sync_and_convert_logic)
    load = PythonOperator(task_id='load_to_silver_task', python_callable=load_to_silver)

    process >> load