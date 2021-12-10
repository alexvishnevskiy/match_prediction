from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator, task
from scripts.train import fit
from scripts.predict import predict
from airflow import DAG


default_args = {
    'owner': 'sashnevskiy',
    'depends_on_past': True,
    "start_date": datetime(2015, 6, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id = 'etl_process',
    default_args=default_args,
    description='DAG that train model and predict probabilities',
    #schedule_interval='@daily',
    schedule_interval='*/5 * * * *',
    start_date=datetime(2021, 12, 7),
    catchup=False,
    tags=['etl_process'],
) as dag:

    training = PythonOperator(
        task_id='training',
        python_callable=fit,
        )

    prediction = PythonOperator(
        task_id='prediction',
        python_callable=predict,
    )

    training >> prediction
