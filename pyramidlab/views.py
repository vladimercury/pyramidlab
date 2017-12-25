from pyramid.view import view_config, notfound_view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPUnauthorized, HTTPForbidden, HTTPFound
from pyramid.security import forget, remember
from pyramid.response import Response
from pyramid.location import lineage
from sqlalchemy.exc import DBAPIError

from .dao import UserDAO, GroupDAO, RecordDAO
from .models import User, Group
from .resources import *


class BlogViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.parents = reversed(list(lineage(context)))

    @view_config(renderer='templates/group_blog.jinja2', context=GroupRecordContainer, permission='view')
    def group_record_container(self):
        user_id = self.request.authenticated_userid
        db_session = self.request.dbsession
        post = self.request.POST
        if 'submit' in post:
            action = post.get('action', '')
            if action == 'join':
                UserDAO.join_group(db_session, user_id, self.context.id)
            elif action == 'leave':
                UserDAO.leave_group(db_session, user_id, self.context.id)
            elif action == 'post':
                title = post.get('post_title')
                content = post.get('post_content')
                record = RecordDAO.create(db_session, user_id, title, content, self.context.id)
                self.context.put(record, db_session)
        in_group = GroupDAO.has_user(self.request.dbsession, self.context.id, user_id)
        self.request.dbsession.expunge_all()
        return dict(
            page_title=self.context.title,
            in_group=in_group
        )

    @view_config(renderer='templates/user_blog.jinja2', context=UserPage, permission='view')
    def user_record_container(self):
        user_id = self.context.id
        db_session = self.request.dbsession
        user = UserDAO.get_by_id(db_session, user_id)
        return dict(
            user=user
        )

    @view_config(renderer='templates/container.jinja2', context=GroupContainer, permission='view')
    def group_container(self):
        return dict(page_title="Group List")

    @view_config(renderer='templates/container.jinja2', context=UserContainer, permission='view')
    def user_container(self):
        return dict(page_title="User List")

    @view_config(renderer='templates/root.jinja2', context=Root, permission='view')
    def root(self):
        user_id = self.request.authenticated_userid
        db_session = self.request.dbsession
        user = UserDAO.get_by_login(db_session, user_id)
        post = self.request.POST
        if 'submit' in post:
            action = post.get('action', '')
            if action == 'post':
                title = post.get('post_title')
                content = post.get('post_content')
                RecordDAO.create(db_session, user_id, title, content)
            self.request.dbsession.expunge_all()
            user = UserDAO.get_by_login(db_session, user_id)
        return dict(user=user)

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
            db_session = self.request.dbsession
            name = post.get('name', '')

            group = Group(name)
            try:
                user = UserDAO.get_by_login(db_session, self.request.authenticated_userid)
                existing_group = GroupDAO.get_by_name(db_session, name)
            except DBAPIError as dbe:
                return Response("Database Error: " + str(dbe), content_type='text/plain', status=500)

            if existing_group:
                message = "Group already exists"
            else:
                group.users.append(user)
                try:
                    GroupDAO.create(db_session, group)
                    group_container = self.request.root['groups']
                    group_container.put(group, db_session)
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
