# Added a VAR into airflow: Key:weather_coordinates, Val:39.7456,-97.0892
# Added a Conection: http_weather_api, http: https://api.weather.gov/points/

import json
from datetime import datetime
import requests
from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator

# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "retries": 0,
    "start_date": datetime(2021, 1, 1),
    "queue": "default",
}

# Define the DAG
dag = DAG(
    dag_id="weather_checker",
    description="Check the weather",
    schedule_interval="0 0 * * 1",  # Schedule to run at midnight on Mondays
    default_args=default_args,
    catchup=False,
)

# Function to parse the response from the weather API
def parse_response(**context):
    # Pull the response from the previous task
    response_string = context.get("task_instance").xcom_pull(
        task_ids="get_location_metadata"
    )
    # Load the response as JSON
    json_response = json.loads(response_string)
    # Extract the forecast URL from the JSON response
    forecast_url = json_response.get("properties").get("forecast")
    # Push the forecast URL to XCom for the next task to use
    context.get("task_instance").xcom_push(key="forecast_url", value=forecast_url)

# Function to print the weather forecast
def print_forecast(**context):
    # Pull the forecast URL from XCom
    forecast_url = context.get("task_instance").xcom_pull(key="forecast_url")
    # Get the forecast data from the forecast URL
    response = requests.get(forecast_url).json()
    # Ensure the response contains the expected properties
    assert "properties" in response.keys()
    # Extract the forecast periods
    periods = response.get("properties").get("periods")
    # Print the forecast for each period
    for period in periods:
        period_name = period.get("name")
        forecast = period.get("detailedForecast")
        print(period_name + ": " + forecast)

# Define the tasks within the DAG
with dag:  # new syntax, automatically associates all tasks to the above DAG
    # Task to get location metadata from the weather API
    get_location_metadata = HttpOperator(
        task_id="get_location_metadata",
        http_conn_id="http_weather_api",
        method="GET",
        response_check=lambda response: "forecast" in response.text,
        endpoint="{{ var.value.weather_coordinates }}",
        do_xcom_push=True,  # Pushes response.text to XCom
    )

    # Task to parse the metadata response and extract the forecast URL
    parse_metadata_response = PythonOperator(
        task_id="parse_metadata_response",
        python_callable=parse_response,
        provide_context=True,
        do_xcom_push=True,
    )

    # Task to print the weekly weather forecast
    print_weekly_forecast = PythonOperator(
        task_id="print_weekly_forecast",
        python_callable=print_forecast,
        provide_context=True,
    )

    # Define the task dependencies
    get_location_metadata >> parse_metadata_response >> print_weekly_forecast
