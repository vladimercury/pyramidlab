from sqlalchemy import Table, Text, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .meta import Base

import bcrypt

user_groups = Table('user_group', Base.metadata,
                    Column('user_id', ForeignKey('users.id'), primary_key=True),
                    Column('group_id', ForeignKey('groups.id'), primary_key=True)
                    )


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(30))
    last_name = Column(String(30))
    login = Column(String(30))
    password = Column(String(64))

    # many to many BlogPost<->Keyword
    groups = relationship('Group',
                          secondary=user_groups,
                          back_populates='users')

    def __init__(self, login, password, first_name, last_name):
        self.login = login
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.first_name = first_name
        self.last_name = last_name

    def match_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    users = relationship('User',
                         secondary=user_groups,
                         back_populates='groups')

    def __init__(self, name):
        self.name = name


