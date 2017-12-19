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

from .models import Group
from .dto import GroupDTO


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
    def __init__(self, name, parent, request, orm_class, dto_class):
        super(Container, self).__init__()
        self.__name__ = name
        self.__parent__ = parent
        self.orm_class = orm_class
        self.dto_class = dto_class
        self.load_data(request)

    def load_data(self, request):
        data = request.dbsession.query(self.orm_class).all()
        for item in data:
            self[item.id] = self.dto_class(item)


class GroupContainer(Container):
    def __init__(self, name, parent, request):
        super(GroupContainer, self).__init__(name, parent, request, Group, GroupDTO)


root = Root('', None, 'My Site')


def bootstrap(request):
    if not root.values():
        root['login'] = LoginPage('login', root, 'Login Page')
        root['logout'] = LogoutPage('logout', root, 'Logout Page')
        root['register'] = RegistrationPage('register', root, 'Registration Page')
        root['addgroup'] = AddGroupPage('addgroup', root, 'Add Group Page')
        root['group'] = GroupContainer('group', root, request)
    return root