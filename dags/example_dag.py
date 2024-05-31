# Import the necessary modules from Airflow
from airflow import DAG
from datetime import datetime, timedelta
# Import the BashOperator from Airflow
from airflow.operators.bash_operator import BashOperator

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',  # Owner of the DAG
    'retries': 3,        # Number of retries in case of failure
    'retry_delay': timedelta(minutes=5),  # Delay between retries
    'do_xcom_push': False # Disable XCom push by default
}

# Define the DAG
dag = DAG(
    dag_id='example_dag',  # Unique identifier for the DAG
    description='Just an example DAG',  # Description of the DAG
    start_date=datetime(2021, 1, 1),  # Start date of the DAG
    schedule_interval='0 0 * * *',  # Cron expression for scheduling (daily at midnight)
    catchup=False,  # If False, the DAG will not backfill
    default_args=default_args  # Apply default arguments to the DAG
)

# Define a BashOperator task to print "Hello"
task_1 = BashOperator(
    task_id='hello_task',  # Unique identifier for this task
    bash_command='echo "Hello"',  # Bash command to execute
    dag=dag  # Reference to the DAG this task belongs to
)

# Define a BashOperator task to send a curl request to http://example.com
task_2 = BashOperator(
    task_id='curl_task',  # Unique identifier for this task
    bash_command='curl http://example.com',  # Bash command to execute
    dag=dag  # Reference to the DAG this task belongs to
)

# Set task_2 to run after task_1
task_1 >> task_2

# Set task_2 and task_3 to run after task_1, and task_4 to run after both task_2 and task_3
#task_1 >> [task_2, task_3] >> task_4

# Another way to set task_2 to run after task_1 using set_downstream method
#task_1.set_downstream(task_2)

# Another way to set task_2 to run after task_1 using set_upstream method
#task_2.set_upstream(task_1)