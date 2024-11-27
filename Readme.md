# Credit Approval System

This is a Django-based credit approval system that integrates with Celery for background task processing and uses Redis as the message broker.

## Prerequisites

Before running the project, make sure you have the following installed:

- **Docker**: [Download Docker](https://www.docker.com/get-started)
- **Docker Compose**: This should come with Docker Desktop if you are on Windows/Mac. On Linux, you can install it separately.

## Project Setup

### 1. Clone the repository

First, clone the project repository:

```bash
git clone <repository-url>
cd credit_approval_system
```

Set the environment variables
```bash
cp .env.example .env
```

### 2. Build and run the Docker containers
You can use Docker Compose to build and start the application, including the web server, database, Redis, and Celery worker.

Build the containers
Run the following command to build the Docker containers:

This will pull the necessary images for the web server, Redis, and any other dependencies.

- Start the containers
   To start the containers, use:

    ```bash
    docker-compose up
    ```
This will bring up the web, db, and redis services.

### 3. Running commands inside the web container
After your containers are up and running, you can execute various commands within the web container using Docker Compose.

-  Create migrations
    To create new migrations, run:
    
    ```bash
        docker-compose run web python manage.py makemigrations
    ```

- This will create migration files for any changes you make to the Django models.

-  Apply migrations
    To apply migrations to the database, run:

    ``` bash
    docker-compose run web python manage.py migrate
    ```
- This will apply any pending migrations to the database.

-  Enter the Django shell
    To enter the Django shell, run:

    ``` bash
    docker-compose run web python manage.py shell
    ```
- This will drop you into an interactive Python shell where you can interact with your Django project.

### 4. Running background tasks with Celery
-  Starting the Celery worker
To start the Celery worker, run the following command:
    ``` bash
    docker-compose run web celery -A credit_approval_system worker --loglevel=info
    ```

- Triggering a task inside the Django shell
In the Django shell, you can trigger a Celery task like this:
    ``` python
    from loans.tasks import ingest_data
    ingest_data.delay()
    ```

- This will send the ingest_data task to the Celery worker for processing in the background.