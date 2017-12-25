from ..models import Group


class GroupDAO:
    @staticmethod
    def get_by_name(session, name):
        query = session.query(Group)
        return query.filter(Group.name == name).first()

    @staticmethod
    def get_by_id(session, group_id):
        query = session.query(Group)
        return query.filter(Group.id == group_id).first()

    @staticmethod
    def create(session, group):
        session.add(group)
        session.flush()
        return group.id

    @staticmethod
    def has_user(session, group_id, user_login):
        query = session.query(Group)
        return query.filter(Group.users.any(login=user_login))\
            .filter(Group.id == group_id).one_or_none() is not None
