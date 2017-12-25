from sqlalchemy import Table, Text, Column, ForeignKey, Integer, String, DateTime

from sqlalchemy.orm import relationship

from .user_group import User

from .meta import Base

from datetime import datetime


class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, nullable=True)
    date = Column(DateTime)
    title = Column(Text)
    content = Column(Text)

    author = relationship("User", back_populates='records')

    def __init__(self, author, title, content, author_group_id=None):
        self.author = author
        self.group_id = author_group_id
        self.date = datetime.now()
        self.title = title
        self.content = content


User.records = relationship("Record", order_by=Record.id, back_populates='author')