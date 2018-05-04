# microAuth
=============================

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
POST /confirm-email/:token
POST /reset-password/:emailAddress


# Admin only
GET /accounts
GET /accounts/:id
PUT /accounts/:id
DELETE /accounts/:id
```

## Get up and running in minutes

#### Running locally

1. After cloning, create a virtual environment with `python3 -m venv .venv/`. Activate it with `source .venv/bin/activate`.
2. Install dependencies with `pip3 install -r requirements.txt`
3. Rename `default.env` to `.env`.
4. Run `docker-compose up -d database` to run a PostgreSQL instance in Docker.
5. Run tests with `pytest`.
6. Run the application with `python3 app/main.py`.

#### Production

1. Create a PostgreSQL instance on AWS _(or host your own)_.
2. Rename `default.env` to `.env`, fill it out with your credentials, and change `API_ENV` to `PRODUCTION`.
3. Initialize the database with `python3 app/utils/init_db.py`. 
3. Build the project with `docker build -t microauth .`.
4. Run with `docker run -p 5000:5000 -d microauth`.

## Configuration



### Sendgrid

If you want to enable signup verification and password resets for your users, sign up for a [Sendgrid Account](https://sendgrid.com) and add your API Keys to `.env`. In Sendgrid create two template emails: one for the password resets and one for account verification. Copy the HTML from `email-templates` into Sengrid and add each template ID to `.env`.

## Javascript Usage

Want to use this application from a javascript project? Here's some starter code that should get you 95% there. _(axios is a dependency)_.

```javascript

```


## Other

[Credit for the email HTML template](https://github.com/leemunroe/responsive-html-email-template)
 
## Contributing 

Contributions are welcome and appreciated. Potential improvements include:

* OAuth support.
* Revokable tokens.
* 2 Factor Authentication (with an authenticator app).

