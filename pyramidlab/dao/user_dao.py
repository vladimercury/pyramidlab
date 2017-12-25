from ..models import User, Group, Record


class UserDAO:
    @staticmethod
    def get_by_id(session, user_id):
        query = session.query(User)
        return query.get(user_id)

    @staticmethod
    def get_by_login(session, login):
        query = session.query(User)
        return query.filter(User.login == login).one()

    @staticmethod
    def create_user(session, user):
        session.add(user)

    @staticmethod
    def join_group(session, user_login, group_id):
        user = UserDAO.get_by_login(session, user_login)
        group = session.query(Group).get(group_id)
        user.groups.append(group)
        session.flush()

    @staticmethod
    def leave_group(session, user_login, group_id):
        user = UserDAO.get_by_login(session, user_login)
        group = session.query(Group).get(group_id)
        user.groups.remove(group)
        session.flush()