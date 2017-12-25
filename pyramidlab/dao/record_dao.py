from ..models import User, Group, Record


class RecordDAO:
    @staticmethod
    def create(session, author_login, title, content, group_id=None):
        author = session.query(User).filter(User.login == author_login).one()
        record = Record(author, title, content, group_id)
        session.add(record)
        session.flush()
        return record
