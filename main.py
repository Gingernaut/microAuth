from flask import Flask, jsonify, request
from models import user
from models import db
import random, string, json
import utils

configFile = json.loads(open('config.json').read())

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = utils.getDBConfig()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['DEBUG'] = True
app.config['TESTING'] = True

db.init_app(app)

@app.route("/drop")
def drop():
    db.reflect()
    db.drop_all()
    db.session.commit()
    return "dropped"

@app.route("/signup", methods=["POST"])
def signup():

    # try:
    res = json.loads(request.data)

    postFName = res.get("firstName", None)
    postLName = res.get("lastName", None)
    postEmail = res.get("emailAddress")
    postPass = res.get("password")

    if not utils.isValidEmail(postEmail):
        return custResponse(400, "Invalid email address.")

    if not utils.isValidPass(postPass):
        return custResponse(400, "Invalid password. Must be at least " + configFile["Security"]["minPassLength"] + " characters long.")

    if utils.accountExists(postEmail):
        return custResponse(400, "An account with this email address already exists.")

    if postFName:
        postFName = postFName.title().trim()

    if postLName:
        postLName = postLName.title().trim()

    encryptedPass = utils.encryptPass(postPass)

    payload = {
        "emailAddress": postEmail,
        "password": encryptedPass,
        "firstName": postFName,
        "lastName": postLName
    }

    accId = utils.createAccount(payload)

    if not accId:
        return custResponse(500, "Account creation failed.")

    token = utils.genToken(accId)
    
    return custResponse(201, "Signup Successful", {"token": token })

    # except Exception as e:
    #     print("*-*-*-*")
    #     print(e)
    #     return custResponse(500, str(e)) #replace with unkown error if debug is false


@app.route("/login", methods=["POST"])
def login():
    res = json.loads(request.data)

    postEmail = res.get("emailAddress")
    postPass = res.get("password")

    if not utils.isValidEmail(postEmail):
        return custResponse(400, "Invalid email address.")

    if not utils.isValidPass(postPass):
        return custResponse(400, "Invalid password. Must be at least " + configFile["Security"]["minPassLength"] + " characters long.")

    accId = utils.signin(postEmail, postPass)

    if not accId:
        return custResponse(400, "No Account exists with for " + postEmail + ".")

    accData = utils.getAccData(accId)

    return custResponse(200, "Login Successful", accData)

@app.route("/account", methods=["GET", "PUT", "DELETE"])
def modifyAccount():

    ## authenticate user

    if request.method == 'GET':
        return "ECHO: GET\n"

    elif request.method == 'PUT':
        return "ECHO: PUT\n"

    elif request.method == 'DELETE':
        return "ECHO: DELETE"

@app.route("/accounts", methods=["GET"])
def allAccounts():

    # If an admin account

    results = [user.serialize() for user in user.query.all()]
    return jsonify(results)


# add same as above for put del on /accounts/id


@app.route("/")
def index():

    return "hello there"

@app.errorhandler(404)
def custResponse(code=404, message="Error: Not Found", data=None):

    message = {
        'status': code,
        'message': message
    }

    if data:
        for k, v in data.items():
            message[k] = v

    resp = jsonify(message)
    resp.status_code = code

    return resp

if __name__ == "__main__":
        with app.app_context():
            # drop()
            db.create_all()
            db.session.commit()
            app.run(host="0.0.0.0")
