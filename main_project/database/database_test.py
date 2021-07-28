from datetime import datetime

from sqlalchemy import  create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
import sqlalchemy
print("Версия SQLAlchemy:", sqlalchemy.__version__)

engine = create_engine('sqlite:///data.db', echo=True)

pool_recycle = 7200

metadata = MetaData()
users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('nickname', String),
    Column('password', String)
)

users_history_table = Table('history', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', ForeignKey('users.id')),
    Column('ip_address', String),
    Column('last_time', DateTime)
)

users_contacts = Table('contacts', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', ForeignKey('users.id')),
    Column('id_contact', ForeignKey('users.id'))
)

metadata.create_all(engine)

class User:
    def __init__(self, nickname, password):
        self.nickname = nickname
        self.password = password

class History:
    def __init__(self, user_id, ip_address, last_time):
        self.user_id = user_id
        self.ip_address = ip_address
        self.last_time = last_time

class Contacts:
    def __init__(self, user_id, id_contact):
        self.user_id = user_id
        self.id_contact = id_contact


u = mapper(User, users_table)
h = mapper(History, users_history_table)
c = mapper(Contacts, users_contacts)


# Пример добавления юзера в БД

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
session.add(User("Fedor", "gaga1414"))
session.commit()

# Пример фиксации в журнале посещения последнего времени активности юзера (history)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
session.add(History(12,"123.44.24.22", datetime.now()))
session.commit()

# Пример добавления id в контакты

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
session.add(Contacts(12,88))
session.commit()