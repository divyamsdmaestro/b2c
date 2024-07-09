# IIHT B2C Backend


## Prerequisites
1. Python3.11.1 & Pipenv
2. Virtualenv
3. Docker & Docker Compose


## Getting Started

### Initial Steps
1. Create a virtual environment in the project root using `virtualenv -p python3 .venv`.
2. Activate the environment & install the packages inside `Pipfile` file using `Pipenv`.
3. Use [pre-commit](https://pre-commit.com/) to maintain code integrity. Run: `pre-commit install`.
4. Set the necessary `.env` file on the project root. Use `.envs.example` as reference.

### Basic Development
1. Run the app using `python manage.py init_app && python manage.py runserver`.
2. The app will be running on `http://localhost:8000/`. Now just follow the regular dev process.
3. Other management commands can be run using `python manage.py <command>`.

### Advanced Development
Advanced development is just using async and cache operations. The app uses celery and redis
respectively for the same to handle load and other stuff.

The app is configured in a way to run these operations & tasks on the main thread even if
these services are not available. Just change the necessary environment variables
in the `.env` file to configure the same.

Docker is configured to get these services up and running in no time. Just follow the
given steps to get started

1. Initial config: `cd docker/deployment/scripts/ && ./init.sh`.
2. Use the `docker-compose` files in the directory to run the necessary services.
3. Command: `docker-compose -f <file>.yml up --build --force-recreate`.
4. Note that during advanced development, docker has to be used for running django/backend. Else the services cannot communicate.

Useful commands:
1. `docker-compose -f docker/deployment/app.yml run backend python manage.py shell_plus --bpython`.
2. `docker-compose -f docker/deployment/app.yml run -p 8000:8000 backend python manage.py runserver 0.0.0.0:8000`.

Note:
1. Visit `docs/` for more documentation.
2. Take a look at `init_app` management command. Used to set up all the necessary databases before app run.
