from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator
from datetime import datetime, timedelta
from ingestion.scripts.api_ingestion import fetch_data_from_api, upload_to_s3
from processing.utils.data_transformations import process_data

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'complex_data_pipeline',
    default_args=default_args,
    description='A complex data pipeline with real-time and batch processing',
    schedule_interval=timedelta(minutes=30),
)

create_bucket = S3CreateBucketOperator(
    task_id='create_bucket',
    bucket_name='{{ dag_run.conf["bucket_name"] }}',
    region_name='us-west-2',
    dag=dag,
)

ingest_data = PythonOperator(
    task_id='ingest_data_from_api',
    python_callable=fetch_data_from_api,
    op_args=['{{ dag_run.conf["api_url"] }}'],
    dag=dag,
)

process_data_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    dag=dag,
)

upload_to_s3_task = PythonOperator(
    task_id='upload_to_s3',
    python_callable=upload_to_s3,
    op_args=['{{ ti.xcom_pull(task_ids="process_data") }}', '{{ dag_run.conf["bucket_name"] }}', 'processed_data.json'],
    dag=dag,
)

# Task Dependencies
create_bucket >> ingest_data >> process_data_task >> upload_to_s3_task
