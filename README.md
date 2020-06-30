# flask app

## Prerequisites

- Postgresql 12

- ## Ubuntu

      ```
      sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

      sudo apt-get update
      sudo apt-get install postgresql-12 postgis pgadmin4 postgresql-client-12 postgresql-12-postgis-3-scripts postgresql-client-common  postgresql-common

      pg_ctlcluster 12 main start
      ```

#### Configure remote Connection

      ```
      sudo nano /etc/postgresql/12/main/postgresql.conf

      Uncomment line 59 and change the Listen address to accept connections within your networks.

      # Listen on all interfaces
      listen_addresses = '*'

      sudo systemctl restart postgresql
      netstat  -tunelp | grep 5432
      ```

- ## Arch Linux

      ```
      $ yay -S postgresql
      $ yay -S postgis # extension

      $ sudo -iu postgres

      [postgres]$ initdb --locale=en_US.UTF-8 -E UTF8 -D /var/lib/postgres/data

      [postgres]$ exit

      $ sudo systemctl enable postgresql.service
      $ sudo systemctl start postgresql.service
      ```

### Create User

    ```
    sudo -u postgres createuser --interactive
    ```

### Create Database and Use Extensions

    ```
    createdb db_name

    psql -d db_name

    > CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    ```

<hr />

## Flask

### Install dependencies

```
pipenv install
```

### Generate environment on another machine

1. List all the dependencies to a file

```
pip freeze > requirements.txt
```

2. Install from `requirements.txt` file

```
pip install -r requirements.txt
```

### Update Env Credentials & Set up database

Apply the migration to the database:

```
flask db upgrade
```

# Celery

### Developmemt

Run a celery worker in another terminal

```
celery worker -A celery_worker.celery --loglevel=info
```

The `-A` option gives Celery the application module and the Celery instance, and `--loglevel=info` makes the logging more verbose, which can sometimes be useful in diagnosing problems.

### Production

<https://docs.celeryproject.org/en/latest/userguide/daemonizing.html#usage-systemd>

<hr />

# Docker

Requires `docker` and `docker-compose`

### Build the image

```
# To run in the foreground
docker-compose up

# To run in the background(detached mode) and tail the logs
docker-compose up -d
docker-compose logs -f

# Subsequent builds (if you change docker file)
docker-compose build
docker-compose up
or
docker-compose up --build

# Kill(remove volume)
docker-compose down -v
```

- Up on running for the first time, the container will be created and the database initialized(with extensions as well)
- Subsequent times you run, the database will already be initialized
- Deleting the container removes the content

### Run only database container

```
docker run --name pg-db-docker-demo -p 5432:5432 -d \
   -e POSTGRES_PASSWORD=<db-password> \
   -e POSTGRES_USER=<db-user> \
   -e POSTGRES_DB=<db-name> \
   -v postgres_data:/var/lib/postgresql/data \
   postgres:12.3-alpine
```

#### Setup database(manually)

```
# Create database
docker exec -it pg-db-docker-demo createdb -U <username> test-db

# Access database
docker exec -it pg-db-docker-demo psql -U <username> -d test-db
```

## References

- <https://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#running-the-celery-worker-server>
- <http://slides.skien.cc/flask-hacks-and-best-practices/>
- <https://docs.docker.com/compose/>
- <https://nickjanetakis.com/blog/dockerize-a-flask-celery-and-redis-application-with-docker-compose>
- <https://stackoverflow.com/questions/45323271/how-to-run-selenium-with-chrome-in-docker>
- <http://codeomitted.com/flask-sqlalchemy-many-to-many-self-referential/>
- http://byatool.com/uncategorized/sqlalchemy-self-referential-many-to-many/
