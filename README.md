# microAuth

## Tired of reinventing the wheel every time you need user authentication in a project?

Fill out a simple config file and have RESTful API endpoints for everything needed for account management.

### Example Usage

Sending a POST request to `/login` with the following JSON payload:
```JSON
{
	"emailAddress": "root@example.com",
	"password": "123456"
}
```

Example response:
```JSON
{
	"id": 1,
	"firstName": null,
	"lastName": null,
	"emailAddress": "root@example.com",
	"createdTime": "2018-06-05 18:51:10.954461",
	"modifiedTime": "2018-06-05 18:51:10.954615",
	"UUID": "6a14a972-0f3c-4c42-9ead-2376d158f108",
	"phoneNumber": null,
	"isVerified": true,
	"userRole": "ADMIN",
	"jwt": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjEsImV4cCI6MTUyODc5MzcyNn0.CgTQv1emsQvJD3fsoWcgfZQSt0BY6I0DRT_8gJGm5Lg"
}
```

The JWT Token should then be included as an `Authorization` header for any subsequent requests to `/account` or `/accounts`.

### Endpoints

```
POST /login
POST /signup

GET /account
PUT /account
DELETE /account

POST /validate-account/<token>
POST /reset-password/<emailAddress>
POST /confirm-reset/<token>

# Admin only
GET /accounts
GET /accounts/<id>
PUT /accounts/<id>
DELETE /accounts/<id>
```


### Running locally

_requires Python3.6+, Docker, and Docker-compose_

1.  Create a virtual environment with `python3 -m venv .venv/`. Activate it with `source .venv/bin/activate`
2.  Install dependencies with `pip3 install -r requirements.txt`
3.  Copy `default.env` to a new file `.env`
4.  Run `docker-compose up -d database` to run a PostgreSQL instance for testing and development.
5.  Run tests with `pytest` _(also initializes database)_.
6.  Run the application with `python3 app/main.py`

### Production

1.  Create a PostgreSQL RDS instance on AWS _(or host your own)_.
2.  Copy `default.env` to `.env`, fill it out with your credentials, and change `API_ENV` to `PRODUCTION`.
3.  Initialize the database with `python3 app/utils/init_db.py`
4.  Build the project with `docker build -t microauth .`
5.  Run with `docker run -p 5000:5000 -d microauth`


### Email Resets (Optional)

To enable signup verification and password resets for your users, sign up for a [Sendgrid Account](https://sendgrid.com) and add your API Key to `.env`.

[Credit for the email HTML templates](https://github.com/wildbit/postmark-templates)


#### Testing

Tests are always run against the local docker PostgreSQL instance. The database is re-initialized before each test, and after the last test is run.

#### Logging

Logs are written to stdout during testing/development, and to `/var/log/access.log` and `/var/log/error.log` inside the Docker container.
Logs are written in JSON format for easy analysis in tools like ElasticSearch/Kibana.
```json
{"levelname": "INFO", "message": "created app", "name": "create_app", "timestamp": "2018-06-05 23:49:17 UTC"}
{"levelname": "INFO", "message": "Goin' Fast @ http://0.0.0.0:5000", "timestamp": "2018-06-05 23:49:17 UTC"}
{"levelname": "INFO", "message": "Starting worker [13250]", "timestamp": "2018-06-05 23:49:17 UTC"}
{"levelname": "INFO", "method": "POST", "status": 200, "timestamp": "2018-06-05 23:49:20 UTC", "url": "http://localhost:5000/login"}
```

## Contributing

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Contributions are welcome and appreciated. Potential improvements include:

* Invalidate existing JWT tokens on password change/reset.
* 2FA with an authenticator app.
* OAuth support.
* Additional example documentation.

Run `pre-commit install` to enable Black formatting on commit.
