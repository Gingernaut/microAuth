# microAuth

hug-cli 'create admin' local function

### User authentication and management as a ready-to-go Docker microservice.

Tired of reinventing the wheel every time you need user authentication on a new project? Fill out a simple config file and have RESTful API endpoints for everything needed for account management. 


* Email verification and reset with Sendgrid (optional)
* Admin only endpoint to manage other user accounts
* JWT based authentication, encryption with [argon2](https://github.com/P-H-C/phc-winner-argon2)
* Full usage documentation available at localhost:8000/documentation


## Usage


## Running

After filling out the config file, you only need two commands to run the project as a docker image:
```bash
docker build -t microauth .
docker run -p 5000:5000 microauth
```

## Configuration



### Sendgrid

If you want to enable email reset and signup for your users, sign up for a [Sendgrid Account](https://sendgrid.com) and fill out your API Keys. Create two template emails (one for the reset email, and one for the account verification. Copy the HTML from `emailTemplates` into Sengrid and add each template ID to the config file.

## Javascript Usage

Here is some starter code that you can use to hit the API endpoints and get your data ( axios is a dependency).


## Other

[Email template source](https://github.com/leemunroe/responsive-html-email-template)
 
## Contributing 

Open to suggestions, pull requests, and feedback!

Possible future features (would love some PR's here):
* OAuth support.
* Revokable tokens.
* 2 Factor Authentication (with an authenticator app).

