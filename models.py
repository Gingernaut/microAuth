from flask_sqlalchemy import SQLAlchemy
import uuid, pendulum, jwt, json
configFile = json.loads(open('config.json').read())
JWT_SECRET = configFile["Security"]["JWT_SECRET"]
JWT_ALGORITHM = configFile["Security"]["JWT_ALGORITHM"]

db = SQLAlchemy()

class user(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.BigInteger, primary_key=True)
    firstName = db.Column(db.String(50), nullable=True, default=None)
    lastName = db.Column(db.String(50), nullable=True, default=None)
    emailAddress = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    createdDate = db.Column(db.DateTime, nullable=False, default=pendulum.utcnow)
    modifiedDate = db.Column(db.DateTime, nullable=False, default=pendulum.utcnow)
    UUID = db.Column(db.String(36), nullable=False, default=uuid.uuid4())
    phoneNumber = db.Column(db.String(14), nullable=True, default=None)
    isValidated = db.Column(db.Boolean, nullable=False, default=False)
    userRole = db.Column(db.String(10), nullable=False,default="USER")

    def serialize(self):
        return {
            "id" : self.id,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "emailAddress": self.emailAddress,
            "createdDate": self.createdDate,
            "modifiedDate": self.modifiedDate,
            "UUID": self.UUID,
            "phoneNumber": self.phoneNumber,
            "isValidated": self.isValidated,
            "userRole": self.userRole
        }

    def __repr__(self):
        return self.serialize()

    def __str__(self):
        return str(self.id) + " " + self.emailAddress

    def genToken(self):
        payload = {
            "userId": self.id,
            "exp": pendulum.utcnow().add(weeks=1)
        }
        return str(jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM).decode("utf-8"))
