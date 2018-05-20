# microAuth

### User authentication and management as a ready-to-go microservice.

#### Tired of reinventing the wheel every time you need user authentication on a new project?

Fill out a simple config file and have RESTful API endpoints for everything you need.

* Email verification and reset with Sendgrid _(optional)_.
* Admin only endpoints to manage other user accounts.
* JWT based authentication, encryption with [argon2](https://github.com/P-H-C/phc-winner-argon2)

### Endpoints

```
POST /login
POST /signup
GET /account
PUT /account
DELETE /account

POST /confirm-account/<token>
POST /reset-password/<emailAddress>
POST /confirm-reset/<token>

# Admin only
GET /accounts
GET /accounts/<id>
PUT /accounts/<id>
DELETE /accounts/<id>
```

## Get up and running in minutes

#### Running locally

_requires Python3.6+, Docker, and Docker-compose_

1.  Create a virtual environment with `python3 -m venv .venv/`. Activate it with `source .venv/bin/activate`.
2.  Install dependencies with `pip3 install -r requirements.txt`
3.  Copy `default.env` to `.env`.
4.  Run `docker-compose up -d database` to run a PostgreSQL instance for testing and development.
5.  Run tests with `pytest`.
6.  Run the application with `python3 app/main.py`.

#### Production

1.  Create a PostgreSQL RDS instance on AWS _(or host your own)_.
2.  Copy `default.env` to `.env`, fill it out with your credentials, and change `API_ENV` to `PRODUCTION`.
3.  Initialize the database with `python3 app/utils/init_db.py`.
4.  Build the project with `docker build -t microauth .`.
5.  Run with `docker run -p 5000:5000 -d microauth`.

### Configuration

Settings can be changed in `app/config.py` on a per-environment basis if needed.

### Email Resets

If you want to enable signup verification and password resets for your users, sign up for a [Sendgrid Account](https://sendgrid.com) and add your API Key to `.env`.

_[Credit for the email HTML templates](https://github.com/wildbit/postmark-templates)_

#### Implementation details


## Usage

You should proxy your user's requests through your own server before hitting these endpoints (instead of having user's browsers use these endpoints directly).


#### Testing

Tests are always run against the local docker PostgreSQL instance. The database is re-initialized before each test, and after the last test is run.

## Contributing

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Contributions are welcome and appreciated. Potential improvements include:

* OAuth support.
* Revokable tokens.
* 2 Factor Authentication (with an authenticator app).

Run `pre-commit install` to enable Black formatting on commit.
