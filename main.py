from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import random, string, json, pendulum, jwt
from flask_cors import CORS, cross_origin
from models import user
from models import db
import utils, accFunctions

configFile = json.loads(open("config.json").read())

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = utils.getDBConfig()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True
app.config["TESTING"] = True

CORS(app)
db.init_app(app)

@app.route("/signup", methods=["POST", "OPTIONS"])
@cross_origin()
def signup():

    try:
        res = json.loads(request.data) or None

        if not res:
            return custResponse(400, "data required for update")

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
        accData["authToken"] =  accFunctions.genToken(accId)

        # if configFile["SendGrid"]["useSendGrid"] == "True":
        #     try:
        #         utils.sendEmail(accData, "confirm")
        #     except:
        #         pass
        return custResponse(201, "Signup Successful", accData)

    except Exception as e:

        if app.config["DEBUG"] == True:
            print("*-*-*-*")
            print(e)
            return custResponse(500,{"Err": str(e)})
        else:
            return custResponse(500, "An unknown error occured.")


@app.route("/login", methods=["POST", "OPTIONS"])
@cross_origin()
def login():
    try:
        res = json.loads(request.data) or None

        if not res:
            return custResponse(400, "data required for update")

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
        accData["authToken"] =  accFunctions.genToken(accId)

        return custResponse(200, "Login Successful", accData)

    except Exception as e:

        if app.config["DEBUG"] == True:
            print("*-*-*-*")
            print(e)
            return custResponse(500,{"Err": str(e)})
        else:
            return custResponse(500, "An unknown error occured.")

@app.route("/account", methods=["GET", "PUT", "DELETE", "OPTIONS"])
@cross_origin()
def modifyAccount():

    try:

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

    except Exception as e:
        if app.config["DEBUG"] == True:
            print("*-*-*-*")
            print(e)
            return custResponse(500,{"Err": str(e)})
        else:
            return custResponse(500, "An unknown error occured.")

@app.route("/accounts", methods=["GET", "OPTIONS"])
@cross_origin()
def allAccounts():
    try:
        token = request.headers["Authorization"] or None

        if not token:
            return custResponse(401, "Unauthorized. Sign in required.")
        
        accId = accFunctions.getIdFromToken(token)

        if not accId or not accFunctions.isAdmin(accId):
            return custResponse(401, "Unauthorized. Invalid token.")

        results = [user.serialize() for user in user.query.all()]

        return jsonify(results)

    except Exception as e:
        if app.config["DEBUG"] == True:
            print("*-*-*-*")
            print(e)
            return custResponse(500,{"Err": str(e)})
        else:
            return custResponse(500, "An unknown error occured.")


# add same as above for put del on /accounts/id
@app.route("/accounts/<accId>", methods=["GET", "PUT", "DELETE", "OPTIONS"])
@cross_origin()
def manageAccounts(accId):

    try:
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
            
    except Exception as e:
        if app.config["DEBUG"] == True:
            print("*-*-*-*")
            print(e)
            return custResponse(500,{"Err": str(e)})
        else:
            return custResponse(500, "An unknown error occured.")

@app.route("/")
@cross_origin()
def index():
    return "Documentation available at https://github.com/Gingernaut/microAuth"

@app.route("/initreset/<email>", methods=["GET", "OPTIONS"])
@cross_origin()
def initReset(email):
    try:
        accId = accFunctions.getAccIdByEmail(str(email))
        accData = accFunctions.getAccData(accId)

        if accId:
            utils.sendEmail(accData, "reset")
            return custResponse(200, "Resetting Account")
        
        return custResponse(400, "Invalid email for reset")

    except Exception as e:
        if app.config["DEBUG"] == True:
            print("*-*-*-*")
            print(e)
            return custResponse(400,{"Err": str(e)})
        else:
            return custResponse(400, "Error resetting email.")


@app.route("/reset/<token>", methods=["GET", "OPTIONS"])
@cross_origin()
def reset(token):
    try:
        token = token.replace("*", ".")
        tokenData = jwt.decode(str(token), utils.JWT_SECRET, algorithms=[utils.JWT_ALGORITHM])
        accId = int(tokenData["userId"])

        accData = accFunctions.getAccData(accId)
        accData["authToken"] =  accFunctions.genToken(accId)

        return custResponse(200, "Resetting Account", accData)

    except Exception as e:
        if app.config["DEBUG"] == True:
            print("*-*-*-*")
            print(e)
            return custResponse(400,{"Err": str(e)})
        else:
            return custResponse(400, "Error resetting account.")

@app.route("/confirm/<token>", methods=["GET", "OPTIONS"])
@cross_origin()
def confirm(token):
    try:
        token = token.replace("*", ".")
        tokenData = jwt.decode(str(token), utils.JWT_SECRET, algorithms=[utils.JWT_ALGORITHM])
        accId = int(tokenData["userId"])
        payload = accFunctions.cleanPayload(accId, {"isValidated": True})

        if "Error" in payload:
            return custResponse(payload["errStat"], payload["Error"])

        accFunctions.updateAccount(payload)
        accData = accFunctions.getAccData(accId)
        return custResponse(200, "Successfully validated account.", accData)

    except Exception as e:
        if app.config["DEBUG"] == True:
            print("*-*-*-*")
            print(e)
            return custResponse(400,{"Err": str(e)})
        else:
            return custResponse(400, "Error validating account.")

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
        db.reflect()
        db.drop_all()
        db.create_all()
        # accFunctions.createAdmin() ## comment this out after your DB is initialized
        db.session.commit()
        app.run()
