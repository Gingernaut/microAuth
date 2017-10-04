# microAuth

### User authentication and management as a ready-to-go Docker microservice.

Tired of reinventing the wheel every time you need user authentication on a new project? Fill out a simple config file and have RESTful API endpoints for everything needed for account management. 


* Email verification and reset with Sendgrid (optional)
* Admin only endpoint to manage other user accounts
* JWT based authentication, encryption with [argon2](https://github.com/P-H-C/phc-winner-argon2)
* Built with Python3, Flask, gunicorn, AWS RDS, and the Sendgrid API. 

## Usage

#### Endpoints without the `Authorization` Header

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
{
    "UUID": "e41b9c87-d9f3-4059-961f-5cc699f7d001",
    "authToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjUsImV4cCI6MTUwNzY4NTc2MH0.vCKaZwSkC0uVUr55yI8udR6j-Ba_LSx4XEpOGItrrG4",
    "createdDate": "Wed, 04 Oct 2017 01:36:00 GMT",
    "emailAddress": "sampl2@email.com",
    "firstName": "Erlich",
    "id": 5,
    "isValidated": false,
    "lastName": "Bachman",
    "message": "Signup Successful",
    "modifiedDate": "Wed, 04 Oct 2017 01:36:00 GMT",
    "phoneNumber": null,
    "status": 201,
    "userRole": "USER"
}
```


`/login/ HTTP Method: POST`

```json
{
    "emailAddress": "sample@email.com",
    "password": "123456"
}
```

Response 

```json
{
    "UUID": "aaebe556-66b4-4120-844c-909d2f6c3420",
    "authToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjEsImV4cCI6MTUwNzY5Mjc0OX0.GEZXpsbNorhCnhXRmq3O0uFBDRSsPXrvq7dEcOMYbDk",
    "createdDate": "Wed, 04 Oct 2017 00:57:43 GMT",
    "emailAddress": "root@root.com",
    "firstName": null,
    "id": 1,
    "isValidated": true,
    "lastName": null,
    "message": "Login Successful",
    "modifiedDate": "Wed, 04 Oct 2017 00:57:43 GMT",
    "phoneNumber": null,
    "status": 200,
    "userRole": "ADMIN"
}
```



#### `Authorization` Header Required

`/account/`
```
    - PUT: Updates the account.
    - GET: Gets all the information about the account
    - DELETE: Deletes the account
```

#### `Authorization` Header Required, account type must be Admin
`/accounts/`
```
    - GET: Gets all information for all accounts
```

`/accounts/:userID/`
```
    - `PUT`: Updates the users account
    - `GET`: Retrieves all the information about the account
    - `DELETE`: Deletes the account
```

## Running

After filling out the config file, you only need two commands to run the project as a docker image:
```bash
docker build -t microauth .
docker run -p 5000:5000 microauth
```

## Configuration

Rename default.json to config.json and fill it out. 
You'll need to have  a PostreSQL database instance running to connect to (This was developed and tested using AWS RDS).

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
        "SendGridAPIKey": "",
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

### Sendgrid

If you don't need or want email verification and reset, set `useSendGrid` to `false`. Otherwise, sign up for a [Sendgrid Account](https://sendgrid.com) and fill out your API Keys. Create two template emails (one for the reset email, and one for the account verficiation. Copy the HTML from `emailTemplates` into Sengrid and add the template ID to the config file.

## Javascript Usage

Here is some starter code that you can use to hit the API endpoints and get your data ( axios is a dependency).

```javascript
const axios = require('axios')

const baseInstance = function () {
  return axios.create({
    baseURL: 'http://localhost:5000/',
    headers: {
      Authorization: // get your user token 
    }
  })
}

const accFunctions = {

  login: function (payload) {
    let HTTP = baseInstance()
    return HTTP.post('login', {
      emailAddress: payload.emailAddress,
      password: payload.password
    })
      .then(res => {
        if (res.status === 200) {
          console.log(res.data)
        } else {
          console.log('invalid response code ', res.status)
        }
      })
  },
  signup: function (payload) {
    let HTTP = baseInstance()
    return HTTP.post('signup', {
      emailAddress: payload.emailAddress,
      password: payload.password,
      firstName: payload.firstName, // optional
      lastName: payload.lastName // optional
    })
      .then(res => {
        if (res.status === 201) {
          console.log(res.data)
        } else {
          console.log('invalid response code ', res.status)
        }
      })
  },
  getOwnData: function () {
    let HTTP = baseInstance()
    return HTTP.get('account')
      .then(res => {
        if (res.status === 200) {
          console.log(res.data)
        } else {
          console.log('invalid response code ', res.status)
        }
      })
  },
  updateAcc: function (payload) {
    let HTTP = baseInstance()
    return HTTP.put('account', payload)
      .then(res => {
        if (res.status === 200) {
          console.log(res.data)
        } else {
          console.log(' response code ', res.status)
        }
      })
  },
  deleteAcc: function () {
    let HTTP = baseInstance()
    return HTTP.delete('account')
      .then(res => {
        if (res.status === 200) {
          console.log('account deleted')
        } else {
          console.log('invalid response code ', res.status)
        }
      })
  },
  getAccounts: function (id = null) {
    if (store.getters.userRole === 'ADMIN') {
      let HTTP = baseInstance()
      if (id) {
        return HTTP.get('accounts/' + id)
      } else {
        return HTTP.get('accounts')
      }
    }
  },
  confirmToken: function (token) {
    let HTTP = baseInstance()
    return HTTP.get('confirm/' + token)
      .then(res => {
        console.log(res.data)
      })
  },
  initReset: function (email) {
    let HTTP = baseInstance()
    return HTTP.get('initreset/' + email)
  },
  confirmReset: function (token) {
    let HTTP = baseInstance()
    return HTTP.get('reset/' + token)
      .then(res => {
        console.log(res.data)
      })
  }
}
```


## Other

[Email template source](https://github.com/leemunroe/responsive-html-email-template)
 
## Contributing 

Open to suggestions, pull requests, and feedback!

Possible future features (would love some PR's here):
* add endpoint to resend confirmation email.
* Flask database migration setup.
* OAuth support.
* Revokable tokens.
* 2 Factor Authentication (with an authenticator app).
* Continue adding documentation.
* Restructure project and set up Flask blueprints for future. additions.
* Automatic detection if db initialization is needed.

