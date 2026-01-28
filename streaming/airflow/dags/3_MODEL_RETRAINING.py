import json
import requests
import time
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

SPARK_MASTER_URL = "http://spark-master:6066"
SUBMIT_ENDPOINT = f"{SPARK_MASTER_URL}/v1/submissions/create"

def submit_spark_job(**context):
    """
    Submit training job to Spark Master via REST API.
    This runs the driver on a Spark Worker (cluster mode).
    The Worker must have access to /models/text/train.py.
    """
    payload = {
        "action": "CreateSubmissionRequest",
        "appArgs": ["--model_idx", "0", "--metric_type", "eval_f1_harmful"],
        "appResource": "/models/text/train.py",
        "clientSparkVersion": "3.5.0",
        "environmentVariables": {
            "ENABLE_MLFLOW": "true",
            "MLFLOW_TRACKING_URI": "http://mlflow:5000",
             # Ensure workers can find modules
            "PYTHONPATH": "/models" 
        },
        "mainClass": "org.apache.spark.deploy.PythonRunner",
        "sparkProperties": {
            "spark.master": "spark://spark-master:7077",
            "spark.submit.deployMode": "cluster",
            "spark.app.name": "TikTok_Text_Retraining",
            # We need to ensure the worker uses its python env with libraries
            "spark.pyspark.python": "python3",
            "spark.pyspark.driver.python": "python3"
        }
    }
    
    print(f"Submitting job to {SUBMIT_ENDPOINT}...")
    try:
        response = requests.post(SUBMIT_ENDPOINT, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            submission_id = data["submissionId"]
            print(f"Job submitted successfully! ID: {submission_id}")
            context['ti'].xcom_push(key='submission_id', value=submission_id)
            return submission_id
        else:
            raise Exception(f"Submission failed: {data.get('message')}")
            
    except Exception as e:
        print(f"Error submitting job: {e}")
        raise

def wait_for_job_completion(**context):
    """
    Poll Spark Master for job status until finished.
    """
    submission_id = context['ti'].xcom_pull(key='submission_id', task_ids='submit_training_job')
    if not submission_id:
        raise Exception("No submission ID found!")
        
    status_url = f"{SPARK_MASTER_URL}/v1/submissions/status/{submission_id}"
    
    print(f"Monitoring job {submission_id}...")
    
    while True:
        try:
            response = requests.get(status_url)
            response.raise_for_status()
            data = response.json()
            
            driver_state = data.get("driverState")
            print(f"Current State: {driver_state}")
            
            if driver_state == "FINISHED":
                print("Job finished successfully!")
                break
            elif driver_state in ["FAILED", "ERROR", "KILLED", "UNKNOWN"]:
                raise Exception(f"Job failed with state: {driver_state}")
            
            # Wait before next check
            time.sleep(10)
            
        except requests.exceptions.RequestException as e:
            print(f"Error checking status: {e}")
            # Don't fail immediately on network blip
            time.sleep(10)

with DAG(
    '3_MODEL_RETRAINING',
    default_args=default_args,
    description='Retrain models via Spark Cluster and register to MLflow',
    schedule_interval='@daily',
    start_date=days_ago(1),
    tags=['tiktok', 'mlops', 'training'],
    catchup=False,
) as dag:

    check_new_data = BashOperator(
        task_id='check_new_data',
        bash_command='echo "Checking new data... OK."',
    )

    submit_training_job = PythonOperator(
        task_id='submit_training_job',
        python_callable=submit_spark_job,
    )

    monitor_training_job = PythonOperator(
        task_id='monitor_training_job',
        python_callable=wait_for_job_completion,
    )
    
    notify_success = BashOperator(
        task_id='notify_success',
        bash_command='echo "Retraining pipeline completed successfully."',
    )

    check_new_data >> submit_training_job >> monitor_training_job >> notify_success
