from ..models import User


class UserDAO:
    @staticmethod
    def get_by_login(session, login):
        query = session.query(User)
        return query.filter(User.login == login).first()

    @staticmethod
    def create_user(session, user):
        session.add(user)

