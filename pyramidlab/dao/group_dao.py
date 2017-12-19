from ..models import Group


class GroupDAO:
    @staticmethod
    def get_by_name(session, name):
        query = session.query(Group)
        return query.filter(Group.name == name).first()

    @staticmethod
    def create(session, group):
        session.add(group)

