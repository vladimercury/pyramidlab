from pyramid.view import view_config, notfound_view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPUnauthorized, HTTPForbidden, HTTPFound
from pyramid.security import forget, remember
from pyramid.response import Response
from pyramid.location import lineage
from sqlalchemy.exc import DBAPIError

from .dao import UserDAO, GroupDAO
from .models import User, Group
from .resources import Root, LoginPage, LogoutPage, RegistrationPage, AddGroupPage, Container, GroupContainer


class BlogViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.parents = reversed(list(lineage(context)))

    @view_config(renderer='templates/container.jinja2', context=GroupContainer, permission='view')
    def container(self):
        return dict(page_title="Group List")

    @view_config(renderer='templates/root.jinja2', context=Root, permission='view')
    def root(self):
        page_title = 'Quick Tutorial: Root'
        return dict(page_title=page_title)

    @view_config(renderer='templates/login.jinja2', context=LoginPage)
    def login(self):
        message = ''
        post = self.request.POST
        if 'submit' in post:
            login = post.get('login', '')
            password = post.get('password', '')

            try:
                user = UserDAO.get_by_login(self.request.dbsession, login)
            except DBAPIError as dbe:
                return Response("Database Error: " + str(dbe), content_type='text/plain', status=500)

            if user and user.match_password(password):
                headers = remember(self.request, login)
                return HTTPFound(location='/', headers=headers)
            else:
                message = "Login Failed"
        elif self.request.authenticated_userid:
            return HTTPFound(location='/')
        return dict(message=message)

    @view_config(renderer='templates/register.jinja2', context=RegistrationPage)
    def register(self):
        message = ''
        post = self.request.POST
        if 'submit' in post:
            login = post.get('login', '')
            password = post.get('password', '')
            first_name = post.get('firstname', '')
            last_name = post.get('lastname', '')

            user = User(login, password, first_name, last_name)
            try:
                existing_user = UserDAO.get_by_login(self.request.dbsession, login)
            except DBAPIError as dbe:
                return Response("Database Error: " + str(dbe), content_type='text/plain', status=500)

            if existing_user:
                message = "User already exists"
            else:
                try:
                    UserDAO.create_user(self.request.dbsession, user)
                except DBAPIError as dbe:
                    return Response("Database Error: " + str(dbe), content_type='text/plain', status=500)

                headers = remember(self.request, login)
                return HTTPFound(location='/', headers=headers)
        elif self.request.authenticated_userid:
            return HTTPFound(location='/')
        return dict(message=message)

    @view_config(context=LogoutPage)
    def logout(self):
        if self.request.authenticated_userid:
            headers = forget(self.request)
            return HTTPFound('/login', headers=headers)
        return HTTPFound('/login')

    @view_config(renderer='templates/addgroup.jinja2', context=AddGroupPage, permission='view')
    def add_group(self):
        message = ''
        post = self.request.POST
        if 'submit' in post:
            name = post.get('name', '')

            group = Group(name)
            try:
                user = UserDAO.get_by_login(self.request.dbsession, self.request.authenticated_userid)
                existing_group = GroupDAO.get_by_name(self.request.dbsession, name)
            except DBAPIError as dbe:
                return Response("Database Error: " + str(dbe), content_type='text/plain', status=500)

            if existing_group:
                message = "Group already exists"
            else:
                group.users.append(user)
                try:
                    GroupDAO.create(self.request.dbsession, group)
                except DBAPIError as dbe:
                    return Response("Database Error: " + str(dbe), content_type='text/plain', status=500)

                # return HTTPFound(location='/')
                message = "Group created"
        return dict(message=message)

    @forbidden_view_config()
    def forbidden_view(self):
        if self.request.authenticated_userid is None:
            return HTTPFound('/login')
        else:
            return HTTPForbidden()

    @notfound_view_config(renderer='templates/404.jinja2')
    def notfound_view(self):
        self.request.response.status = 404
        return {}
