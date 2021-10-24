from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, ARRAY
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Date
from config import DATABASE_CONN

engine = create_engine(DATABASE_CONN)

conn = engine.connect()
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)

    messages = relationship('Message', back_populates='creator')


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(256))
    creator_id = Column(Integer, ForeignKey('users.id'))

    creator = relationship('User', back_populates='messages')


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    interrogations = relationship('Interrogation', back_populates='subject')

    def __repr__(self):
        return "id='%s', name='%s', interrogations='%s'" % (
            self.id, self.name, self.interrogations)


class Interrogation(Base):
    __tablename__ = "interrogations"
    id = Column(Integer, primary_key=True)
    name = Column(String(126))
    date = Column(Date, index=True)

    subject_id = Column(Integer, ForeignKey('subjects.id'))

    subject = relationship('Subject', back_populates='interrogations')

    def __repr__(self):
        return "id='%s', name='%s', date='%s', subject_id=%s" % (
            self.id, self.name, self.date, self.subject_id)


Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)


db: Session = Session()

# sub = Subject(name="Algebra")

# interro = Interrogation(
#     name='1 interro', date="2021-10-24", subject=sub, subject_id=2)

# db.add(sub)
# db.add(interro)
# db.commit()
