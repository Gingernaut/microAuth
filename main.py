from flask import Flask, jsonify, request
import random, string, json, pendulum
from models import user
from models import db
import utils, accFunctions

configFile = json.loads(open("config.json").read())

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = utils.getDBConfig()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True
app.config["TESTING"] = True

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

    if accFunctions.accountExists(postEmail):
        return custResponse(400, "An account with this email address already exists.")

    if postFName:
        postFName = postFName.title()

    if postLName:
        postLName = postLName.title()

    encryptedPass = utils.encryptPass(postPass)

    payload = {
        "emailAddress": postEmail,
        "password": encryptedPass,
        "firstName": postFName,
        "lastName": postLName
    }

    accId = accFunctions.createAccount(payload)

    if not accId:
        return custResponse(500, "Account creation failed.")

    accData = accFunctions.getAccData(accId)
    accData["token"] =  accFunctions.genToken(accId)
    
    return custResponse(201, "Signup Successful", accData)

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

    accId = accFunctions.signin(postEmail, postPass)

    if not accId:
        return custResponse(400, "Login failed. Incorrect email or password")

    accData = accFunctions.getAccData(accId)
    accData["token"] =  accFunctions.genToken(accId)

    return custResponse(200, "Login Successful", accData)


@app.route("/account", methods=["GET", "PUT", "DELETE"])
def modifyAccount():

    token = request.headers["Authorization"] or None
    if not token:
        return custResponse(401, "Unauthorized. Sign in required.")
    
    accId = accFunctions.getIdFromToken(token)
    if not accId:
        return custResponse(401, "Unauthorized. Invalid token.")

    if request.method == "GET":
        data = accFunctions.getAccData(accId)
        return custResponse(200, "Account access successful", data)

    elif request.method == "PUT":
        putData = json.loads(request.data) or None
        if not putData:
            return custResponse(400, "data required for update")

        payload = accFunctions.cleanPayload(accId, putData)

        if "Error" in payload:
            return custResponse(payload["errStat"], payload["Error"])

        accFunctions.updateAccount(payload)
        newData = accFunctions.getAccData(accId)

        return custResponse(200, "Success", newData)


    elif request.method == "DELETE":
        
        result = accFunctions.deleteAccount(accId)

        if result == True:
            return custResponse(200,"Account deleted.")
        else:
            return custResponse(500, "Account deletion failed.")

@app.route("/accounts", methods=["GET"])
def allAccounts():

    token = request.headers["Authorization"] or None

    if not token:
        return custResponse(401, "Unauthorized. Sign in required.")
    
    accId = accFunctions.getIdFromToken(token)

    if not accId or not accFunctions.isAdmin(accId):
        return custResponse(401, "Unauthorized. Invalid token.")

    results = [user.serialize() for user in user.query.all()]
    return jsonify(results)


# add same as above for put del on /accounts/id
@app.route("/accounts/<accId>", methods=["GET", "PUT", "DELETE"])
def manageAccounts(accId):

    token = request.headers["Authorization"] or None

    if not token:
        return custResponse(401, "Unauthorized. Sign in required.")
    
    authUserId= accFunctions.getIdFromToken(token)

    if not authUserId or not accFunctions.isAdmin(authUserId):
        return custResponse(401, "Unauthorized. Invalid token.")

    if request.method == "GET":

        data = accFunctions.getAccData(accId)
        return custResponse(200, "Account access successful", data)

    elif request.method == "PUT":

        putData = json.loads(request.data) or None
        if not putData:
            return custResponse(400, "data required for update")

        payload = accFunctions.cleanPayload(accId, putData)
        if "Error" in payload:
            return custResponse(payload["errStat"], payload["Error"])
        
        if "userRole" in putData:
            payload["userRole"] = putData["userRole"].upper()

        accFunctions.updateAccount(payload)
        newData = accFunctions.getAccData(accId)

        return custResponse(200, "Success", newData)
    
    elif request.method == "DELETE":
        
        result = accFunctions.deleteAccount(accId)

        if result == True:
            return custResponse(200,"Account deleted.")
        else:
            return custResponse(500, "Account deletion failed.")


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
        "status": code,
        "message": message
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
            accFunctions.createAdmin()
            db.session.commit()
            app.run(host="0.0.0.0")
