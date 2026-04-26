#dags/hudi_elt_pipeline.py
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import datetime

with DAG(
    dag_id='hudi_elt_pipeline',  # <--- This must match Postman exactly
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=['hudi', 'elt']
) as dag:
    trigger_test = EmptyOperator(task_id='trigger_test')