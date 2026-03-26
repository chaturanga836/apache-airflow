from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import time

def extract_data(**kwargs):
    conf = kwargs['dag_run'].conf
    source = conf.get('source_type', 'unknown')
    conn_id = conf.get('connection_id', 'no_id')
    print(f"--- STEP 1: EXTRACTION ---")
    print(f"Connecting to {source} using {conn_id}...")
    time.sleep(2) # Simulate network latency
    # In a real scenario, this would save a file to MinIO
    return {"raw_records": 100, "status": "stored_in_bronze"}

def transform_and_enrich(**kwargs):
    conf = kwargs['dag_run'].conf
    ti = kwargs['ti']
    extract_info = ti.xcom_pull(task_ids='extract_step')
    
    mapping = conf.get('mapping_strategy', {})
    enrichment = conf.get('enrichment_type', 'none')
    
    print(f"--- STEP 2: TRANSFORMATION & ENRICHMENT ---")
    print(f"Applying Mapping: {mapping}")
    if enrichment == 'fiat_conversion':
        print("Fetching ETH prices and converting to LKR...")
        time.sleep(3)
    
    print(f"Transformed {extract_info['raw_records']} records successfully.")
    return {"status": "stored_in_silver"}

with DAG(
    dag_id='universal_ingestor',
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=['testing', 'multi-tenant']
) as dag:

    extract = PythonOperator(
        task_id='extract_step',
        python_callable=extract_data
    )

    transform = PythonOperator(
        task_id='transform_step',
        python_callable=transform_and_enrich
    )

    extract >> transform