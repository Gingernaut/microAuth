from models.reset import PasswordReset


class PasswordResetQueries:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_reset_by_id(self, reset_id: int) -> PasswordReset:
        return (
            self.db_session.query(PasswordReset)
            .filter(PasswordReset.id == reset_id)
            .first()
        )

    def create_reset(self, user_id: int) -> PasswordReset:
        reset = PasswordReset(user_id)
        self.db_session.add(reset)
        self.db_session.commit()
        self.db_session.refresh(reset)
        return reset

    def invalidate_resets_for_user(self, user_id: int):
        self.db_session.query(PasswordReset).filter_by(userId=user_id).update(
            {"isValid": False}
        )
        self.db_session.commit()
