from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/opt/airflow/scripts/')
from fetch_stock_data import fetch_and_store

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='stock_data_pipeline',
    default_args=default_args,
    schedule_interval='@hourly',
    catchup=False
) as dag:

    fetch_and_store_task = PythonOperator(
        task_id='fetch_and_store_stock_data',
        python_callable=fetch_and_store
    )

    fetch_and_store_task
