from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import forget
from pyramid.view import forbidden_view_config
from pyramid.view import view_config

from .models import Group, Record, User
from .dao import GroupDAO, UserDAO, RecordDAO


class Folder(dict):
    def __init__(self, name, parent, title):
        self.__name__ = name
        self.__parent__ = parent
        self.title = title


class Root(Folder):
    __acl__ = (
        (Allow, Authenticated, ALL_PERMISSIONS),
    )


class Page(object):
    def __init__(self, name, parent, title):
        self.__name__ = name
        self.__parent__ = parent
        self.title = title


class LoginPage(Page):
    pass


class LogoutPage(Page):
    pass


class RegistrationPage(Page):
    pass


class AddGroupPage(Page):
    pass


class Container(dict):
    def __init__(self, name, parent, title, db_session, orm_class, child_class):
        super(Container, self).__init__()
        self.__name__ = name
        self.__parent__ = parent
        self.title = title
        self.orm_class = orm_class
        self.child_class = child_class
        self.load_items(db_session)

    def load_items(self, db_session):
        self.clear()
        data = db_session.query(self.orm_class).all()
        for item in data:
            self.put(item, db_session)

    def put(self, item, db_session):
        self[str(item.id)] = self.child_class(self, item, db_session)


class GroupPage(Page):
    def __init__(self, parent, group: Group, *args):
        super(GroupPage, self).__init__(str(group.id), parent, group.name)


class RecordPage(Page):
    def __init__(self, parent, record: Record, *args):
        super(RecordPage, self).__init__(str(record.id), parent, record.title)
        self.date = record.date
        self.content = record.content
        self.author = record.author


class GroupRecordContainer(Container):
    def __init__(self, parent, group: Group, db_session):
        super(GroupRecordContainer, self).__init__(str(group.id), parent, group.name, db_session, Record, RecordPage)
        self.id = group.id
        self.users = group.users

    def load_items(self, db_session):
        self.clear()
        data = db_session.query(self.orm_class).filter_by(group_id=self.__name__).all()
        for item in data:
            self.put(item, db_session)

    def update_users(self, db_session):
        group = GroupDAO.get_by_id(db_session, self.__name__)
        self.users = group.users


class GroupContainer(Container):
    def __init__(self, name, parent, title, db_session):
        super(GroupContainer, self).__init__(name, parent, title, db_session, Group, GroupRecordContainer)


class UserPage(Page):
    def __init__(self, parent, user: User, *args):
        super(UserPage, self).__init__(str(user.id), parent, user.first_name + " " + user.last_name)
        self.id = user.id
        self.groups = user.groups
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.login = user.login


class UserContainer(Container):
    def __init__(self, name, parent, title, db_session):
        super(UserContainer, self).__init__(name, parent, title, db_session, User, UserPage)


root = Root('', None, 'My Site')


def bootstrap(request):
    if not root.values():
        root['login'] = LoginPage('login', root, 'Login Page')
        root['logout'] = LogoutPage('logout', root, 'Logout Page')
        root['register'] = RegistrationPage('register', root, 'Registration Page')
        root['addgroup'] = AddGroupPage('addgroup', root, 'Add Group Page')
        root['groups'] = GroupContainer('groups', root, 'Groups', request.dbsession)
        root['users'] = UserContainer('users', root, 'Users', request.dbsession)
    return root
