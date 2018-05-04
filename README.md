# microAuth
=============================

### User authentication and management as a ready-to-go microservice.

#### Tired of reinventing the wheel every time you need user authentication on a new project?


Fill out a simple config file and have RESTful API endpoints for everything needed for account management. 

* Email verification and reset with Sendgrid (optional)
* Admin only endpoint to manage other user accounts
* Secure JWT based authentication, encryption with [argon2](https://github.com/P-H-C/phc-winner-argon2)
* Full usage documentation available at localhost:8000/documentation


## Get up and running in minutes

#### Production

1. Create a PostgreSQL instance on AWS _(or host your own)_.
2. Rename `default.env` to `.env`, and fill it out with your credentials.
3. Initialize the database with `python3 app/utils/init_db.py`. 
3. Build the project with `docker build -t microauth .`.
4. Run with `docker run -p 5000:5000 microauth` 

#### Running locally

1. After cloning, create a virtual environment with `python3 -m venv .venv/`. Activate it with `source .venv/bin/activate`.
2. Install dependencies with `pip3 install -r requirements.txt`
3. Rename `default.env` to `.env`, and fill it out _(and change `API_ENV` to `DEVELOPMENT`)_.
4. To run a PostgreSQL database in Docker, run `docker-compose up -d database`.
5. Initialize the database with `python3 app/utils/init_db.py`.
6. Run tests with `pytest`.
7. Run the application with `python3 app/main.py`.


## Configurationa



### Sendgrid

If you want to enable signup verification and password resets for your users, sign up for a [Sendgrid Account](https://sendgrid.com) and add your API Keys to `.env`. In Sendgrid create two template emails: one for the password resets and one for account verification. Copy the HTML from `email-templates` into Sengrid and add each template ID to `.env`.

## Javascript Usage

Want to use this application from a javascript project? Here's some starter code that should get you 95% of the way there. _(axios is a dependency)_.

```javascript

```


## Other

[Credit for the email template](https://github.com/leemunroe/responsive-html-email-template)
 
## Contributing 

Open to suggestions, pull requests, and feedback!

Possible future features:
* OAuth support.
* Revokable tokens.
* 2 Factor Authentication (with an authenticator app).

