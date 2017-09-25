# microAuth

### User authentication and management as a ready-to-go Docker microservice.

Tired of reinventing the wheel every time you need user authentication on a new project? Fill out a simple config file and have RESTful API endpoints for everything needed for account management. 


* Email verification and reset with Sendgrid (optional)
* Admin only endpoint to manage other user accounts
* JWT based authentication, encryption with [argon2](https://github.com/P-H-C/phc-winner-argon2)
* Built with Python3, Flask, gunicorn, AWS RDS, and the Sendgrid API. 


## Usage

`/signup/  HTTP Method: POST`

```json
{
    "firstName": "Erlich",
    "lastName": "Bachman",
    "emailAddress": "sample@email.com",
    "password": "123456"
}
```
Response

```json

```

`/login/ HTTP Method: POST`

```json
{
    "emailAddress": "sample@email.com",
    "password": "123456"
}
```


Response
```

```

### Authorization Header Required

`/account/`

    - PUT: Updates the account.
    - GET: Gets all the information about the account
    - DELETE: Deletes the account


#### Admin Endpoints
`/accounts/`

    - GET: Gets all information for all accounts

`/accounts/:userID/`
    - `PUT`: Updates the users account
    - `GET`: Retrieves all the information about the account
    - `DELETE`: Deletes the account

## Configuration

Rename default.json to config.json and fill it out. 
Create a Postres RDS instance.
```json
{
    "Security": {
        "JWT_SECRET": "Custom_long_string",
        "JWT_ALGORITHM": "HS256",
        "initEmail": "root@root.com",
        "initPass": "1234567",
        "tokenTTL_Days": 7,
        "minPassLength": 6
    },
    "SendGrid": {
        "useSendgrid": true,
        "SendGridAPIKEY": "",
        "SendGridFromEmail": "example@company.com",
        "SendGridFromName": "Example Company",
        "SendGridResetTemplate": "",
        "SendGridConfirmTemplate": ""
    },
    "Database": {
        "dbName": "",
        "dbUrl": "url.rds.amazonaws.com",
        "dbUser": "",
        "dbPass": "",
        "dbPort": 5432
    },
    "General": {
        "hostAddress": "yourwebsite.com"
    }
}
```




Key Generator: http://www.miniwebtool.com/django-secret-key-generator/



## Sendgrid

First 

Copy and paste the provided emailTemplate.html file in userApp to your Sendgrid Template, and use that ID in the config.json file.

## Other


[Email template source](https://github.com/leemunroe/responsive-html-email-template)


## Contributing 

Open to suggestions, pull requests, and feedback!

Possible future updates:
* OAuth support
* Revokable tokens
* 2 Factor Authentication
