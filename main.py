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
        return custResponse(400, "Login failed. Incorrect email or password")

    token = utils.genToken(accId)

    return custResponse(200, "Login Successful",  {"token": token })

@app.route("/account", methods=["GET", "PUT", "DELETE"])
def modifyAccount():

    token = request.headers["Authorization"] or None

    if not token:
        return custResponse(401, "Unauthorized. Sign in required.")
    
    accId = utils.getIdFromToken(token)

    if not accId:
        return custResponse(401, "Unauthorized. Invalid token.")

    if request.data:
        res = json.loads(request.data)

    if request.method == 'GET':

        data = utils.getAccData(accId)
        return custResponse(200, "Account access successful", data)

    elif request.method == 'PUT':

        return "hi"

    elif request.method == 'DELETE':

        return "oh nooooo"

@app.route("/accounts", methods=["GET"])
def allAccounts():

    token = request.headers["Authorization"] or None

    if not token:
        return custResponse(401, "Unauthorized. Sign in required.")
    
    accId = utils.getIdFromToken(token)

    if not accId or not utils.isAdmin(accId):
        return custResponse(401, "Unauthorized. Invalid token.")

    results = [user.serialize() for user in user.query.all()]
    return jsonify(results)


# add same as above for put del on /accounts/id


@app.route("/")
def index():

    return """
        Available endpoints: \n
                \n
        /signup \n
        /login  \n
        /account \n
            """

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
            drop()
            db.create_all()
            utils.createAdmin()
            db.session.commit()
            app.run(host="0.0.0.0")
