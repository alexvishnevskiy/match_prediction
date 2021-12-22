from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from match_prediction.airflow.scripts.train import fit
from scripts.predict import predict
from airflow import DAG


default_args = {
    'owner': 'sashnevskiy',
    'depends_on_past': False,
    "start_date": datetime(2021, 12, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id = 'etl_process',
    default_args=default_args,
    description='DAG that trains model and predicts probabilities',
    #schedule_interval='@daily',
    schedule_interval='*/5 * * * *',
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
