# ai-airflow

This repository contains an implementation of a data pipeline using Apache Airflow, showcasing examples and architectural details for efficient task management and orchestration.

## Summary

Apache Airflow is a powerful tool for orchestrating complex computational workflows. It uses Directed Acyclic Graphs (DAGs) to manage task dependencies and execution order. This README provides an overview of Airflow's components, including the web server, scheduler, executor, worker, metadata database, and triggerer, along with detailed examples and architectural diagrams for both single-node and multi-node setups.

![image](https://github.com/glauberss2007/ai-airflow/assets/22028539/e44cefe0-6ceb-49ad-ab9f-9023ea4a72af)


## Prerequisites


## Directed Acyclic Graph (DAG)

A DAG is a collection of all the tasks you want to run, organized in a way that reflects their relationships and dependencies.

![image](https://github.com/glauberss2007/ai-airflow/assets/22028539/fa903d7e-8085-4983-b667-ad1a17429bee)

- **DAG**: A collection of tasks with directional dependencies.
- **Operator**: Describes a single task in your pipeline.
- **Task**: An instance of an Operator.

## Example I

### Components

1. **Web Server**:
    - Built with Flask and Gunicorn.
    - Serves the Airflow UI.
    - Runs as its own process.
    - Starts via the `airflow webserver` command.

2. **Scheduler**:
    - Monitors all tasks and DAGs.
    - Triggers task instances when their dependencies are met.
    - Starts via the `airflow scheduler` command.
    - Checks whether tasks can run every minute by default.
    - Uses the configured Executor to run tasks.

3. **Executor**:
    - Defines how tasks are executed.
    - Locally (on the scheduler process), e.g., SequentialExecutor.
    - Remotely (on a pool of workers), e.g., CeleryExecutor.

4. **Worker**:
    - A process that executes tasks assigned by the Executor.
    - Local execution (not recommended) runs on the scheduler.
    - Remote execution runs on a Celery worker, for example.
    - Instance type and queues can be varied for specific work.

5. **Metadata Database**:
    - Stores Airflow's metadata (DAGs, Users, Tasks, Variables, Connections).
    - Compatible with any database that works with SqlAlchemy.

6. **Triggerer**:
    - A process that executes deferred tasks (triggers).

### Architecture

#### Single Node

![image](https://github.com/glauberss2007/ai-airflow/assets/22028539/db655bcf-2983-403c-abf2-24242bff5e98)

Standalone installation:

```
# Create a new directory for Airflow training and navigate into it
mkdir airflow-project && cd airflow-project

# Create a Python virtual environment named 'airflow-venv'
python3 -m venv airflow-venv

# Activate the virtual environment
source ./airflow-venv/bin/activate

# Extract the major and minor version of Python being used
export airflow_python_version=$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)

# Set the constraint URL for installing Airflow with compatible dependencies based on the Python version
export constraint_url="https://raw.githubusercontent.com/apache/airflow/constraints-2.9.1/constraints-${airflow_python_version}.txt"

# Install Apache Airflow version 2.9.1 with the specified constraints
pip install apache-airflow==2.9.1 --constraint "${constraint_url}"

# Set the AIRFLOW_HOME environment variable to the current directory
export AIRFLOW_HOME=$(pwd)

# Disable loading example DAGs provided by Airflow
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Create a directory named 'dags' to store DAG files
mkdir dags

# Copy an example DAG file into the 'dags' directory from the parent directory
cp ../dags/example_dag.py dags/

# Start Airflow in standalone mode, which sets up the Airflow environment and runs the webserver and scheduler
airflow standalone
```

## Example II - Weather Checker DAG
### Multi Node

![image](https://github.com/glauberss2007/ai-airflow/assets/22028539/c9f13339-a812-4336-b228-61288e8acdaf)

This repository contains a `docker-compose.yml` configuration to set up an Apache Airflow environment using Docker Compose. This setup includes all necessary services and their dependencies to run Airflow smoothly. It includes:

- **x-airflow-common:**
  - **Image:** Uses the specified Airflow image (`apache/airflow:2.9.1` by default).
  - **Environment Variables:** Configures the Airflow executor, database connection, Celery backend, broker URL, and other essential settings.
  - **Volumes:** Mounts local directories for DAGs, logs, configs, and plugins.
  - **Dependencies:** Requires Redis and PostgreSQL services to be healthy before starting.

- **PostgreSQL (`postgres`):**
  - **Image:** `postgres:13`
  - **Environment Variables:** Sets the database user, password, and database name.
  - **Volumes:** Stores PostgreSQL data.
  - **Healthcheck:** Checks the availability of the PostgreSQL service.

- **Redis (`redis`):**
  - **Image:** `redis:7.2-bookworm`
  - **Expose:** Exposes port 6379.
  - **Healthcheck:** Checks the availability of the Redis service.

- **Airflow Webserver (`airflow-webserver`):**
  - **Extends:** `x-airflow-common`
  - **Command:** Starts the webserver.
  - **Ports:** Maps port 8080.
  - **Healthcheck:** Checks the health of the webserver.
  - **Depends On:** Depends on `airflow-init` service to complete successfully.

- **Airflow Scheduler (`airflow-scheduler`):**
  - **Extends:** `x-airflow-common`
  - **Command:** Starts the scheduler.
  - **Healthcheck:** Checks the health of the scheduler.
  - **Depends On:** Depends on `airflow-init` service to complete successfully.

- **Airflow Worker (`airflow-worker`):**
  - **Extends:** `x-airflow-common`
  - **Command:** Starts the Celery worker.
  - **Healthcheck:** Checks the health of the worker.
  - **Depends On:** Depends on `airflow-init` service to complete successfully.

- **Airflow Triggerer (`airflow-triggerer`):**
  - **Extends:** `x-airflow-common`
  - **Command:** Starts the triggerer.
  - **Healthcheck:** Checks the health of the triggerer.
  - **Depends On:** Depends on `airflow-init` service to complete successfully.

- **Airflow Initialization (`airflow-init`):**
  - **Extends:** `x-airflow-common`
  - **Entrypoint:** Bash.
  - **Command:** Initializes directories, adjusts permissions, checks system resources, and runs database migrations.
  - **Environment:** Additional environment variables for database migration and web user creation.

- **Airflow CLI (`airflow-cli`):**
  - **Extends:** `x-airflow-common`
  - **Command:** Provides a command-line interface for debugging and administrative tasks.
  - **Profiles:** Debug profile.

- **Flower (`flower`):**
  - **Extends:** `x-airflow-common`
  - **Command:** Starts the Flower monitoring tool for Celery.
  - **Ports:** Maps port 5555.
  - **Healthcheck:** Checks the health of the Flower service.
  - **Depends On:** Depends on `airflow-init` service to complete successfully.
  - **Profiles:** Flower profile.

- **postgres-db-volume:** Defines a volume for storing PostgreSQL data.

Execute this command in the base folder (the place with .env and composer file):

```
# Append the current user's UID to the .env file for Docker to use
echo -e "AIRFLOW_UID=$(id -u)" >> .env

# Initialize the Airflow database by running the 'airflow-init' service defined in the Docker Compose file
docker-compose up airflow-init

# Start all services defined in the Docker Compose file, including the Airflow webserver and scheduler
docker-compose up

# The default username and password for Airflow's web UI
# user: airflow
# password: airflow

# Clean up the Docker environment by stopping and removing containers, networks, volumes, and orphan containers
docker compose down --volumes --remove-orphans

```

### Key Concepts

- **Variables**: Stored in the database and accessible to all DAGs.
- **Connection**: Object stored in the database to reach outside systems.
- **XCom**: Allows communication between tasks in a DAG.
- **SimpleHttpOperator**: An operator used to call an HTTP endpoint.
- **Context**: An instance of an Operator.

This example demonstrates how to set up a DAG for checking the weather using various Airflow concepts like variables, connections, and operators.

## Example III - Query DAGs


```
# Metastore container
docker exec -it $POSTGRES_CONTAINER psql -h postgres -U airflow 
#password is "airflow"
```

## References

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow DAG Concepts](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html)
- [Using Airflow Executors](https://airflow.apache.org/docs/apache-airflow/stable/executor/index.html)
- [Airflow Scheduler Documentation](https://airflow.apache.org/docs/apache-airflow/stable/scheduler.html)
- [Flask Documentation](https://flask.palletsprojects.com/en/2.0.x/)
- [Gunicorn Documentation](https://docs.gunicorn.org/en/stable/)

---

By following the structure and examples provided in this repository, you can effectively set up and manage data pipelines using Apache Airflow, ensuring smooth and efficient task orchestration and execution.
