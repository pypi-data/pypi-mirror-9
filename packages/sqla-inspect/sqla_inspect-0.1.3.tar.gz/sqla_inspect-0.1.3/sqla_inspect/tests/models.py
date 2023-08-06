# -*- coding: utf-8 -*-
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Date,
    Unicode,
)

from sqlalchemy.orm import (
    relationship,
    backref,
)


Base = declarative_base()


class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(25))

class Friend(Base):
    __tablename__ = 'friend'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(25))
    aka = Column(Unicode(25))

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(25))
    password = Column(
        Unicode(25),
        info={"export": {'exclude': True}}
    )

    parent_id = Column(ForeignKey(Parent.id))
    parent = relationship(
        Parent,
        backref="children",
        info={"export": {"label": u"Parent"}}
    )

    friend_id = Column(ForeignKey(Friend.id))
    friend = relationship(
        Friend,
        backref='friend',
        info={'export': {'related_key': 'aka'}}
    )

