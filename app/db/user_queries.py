from models.user import User as UserModel
from typing import List
import pendulum


class UserQueries:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_user_by_id(self, user_id: int) -> UserModel:
        return self.db_session.query(UserModel).filter(UserModel.id == user_id).first()

    def get_user_by_email(self, user_email: str) -> UserModel:
        return (
            self.db_session.query(UserModel)
            .filter(UserModel.emailAddress == user_email.lower())
            .first()
        )

    def get_all_users(self) -> List[UserModel]:
        return self.db_session.query(UserModel).all()

    def create_user(self, user: UserModel) -> UserModel:
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def update_user(self, user: UserModel) -> UserModel:
        user.modifiedTime = pendulum.now("UTC")
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def delete_user(self, user_id: int):
        self.db_session.query(UserModel).filter_by(id=user_id).delete()
        self.db_session.commit()
