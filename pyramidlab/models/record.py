from sqlalchemy import Table, Text, Column, ForeignKey, Integer, String, DateTime

from sqlalchemy.orm import relationship

from .user_group import User

from .meta import Base


class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, nullable=True)
    date = Column(DateTime)
    title = Column(Text)
    content = Column(Text)

    author = relationship("User", back_populates='records')

    def __init__(self, author_user_id, author_group_id, date, title, content):
        self.user_id = author_user_id
        self.group_id = author_group_id
        self.date = date
        self.title = title
        self.content = content


User.records = relationship("Record", order_by=Record.id, back_populates='author')
