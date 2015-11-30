from sqlalchemy import Column, ForeignKey, Integer, String, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

import sqlalchemy
 
Base = declarative_base()

DBpath = "mysql://root:oigalera8458@localhost/restaurant_utf8"

engine = sqlalchemy.create_engine('mysql://root:oigalera8458@localhost')

#engine.execute("CREATE DATABASE restaurant_utf8 CHARACTER SET utf8 COLLATE utf8_general_ci")

class User(Base):
    __tablename__ = 'user' 

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(250, collation='utf8_bin'), nullable=False)
    email = Column(Unicode(250, collation='utf8_bin'), nullable=False)
    picture = Column(Unicode(250, collation='utf8_bin'))


class Restaurant(Base):
    __tablename__ = 'restaurant'
   
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(250, collation='utf8_bin'), nullable=False)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }
 
class MenuItem(Base):
    __tablename__ = 'menu_item'

    name =Column(Unicode(250, collation='utf8_bin'), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(Unicode(250, collation='utf8_bin'))
    price = Column(Unicode(250, collation='utf8_bin'))
    course = Column(Unicode(250, collation='utf8_bin'))
    restaurant_id = Column(Integer,ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'description'  : self.description,
           'id'           : self.id,
           'price'        : self.price,
           'course'       : self.course,
       }

####### Nao esquecer de mudar a senha do data base aqui.
engine = create_engine(DBpath)

Base.metadata.create_all(engine)
