from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, Date, DateTime, Boolean, ForeignKey, Table

base = declarative_base()

class User(base):
    id = Column(Integer, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    pword = Column(Text, nullable=False)
    first_name = Column(Text, nullable=False)
    birth_date = Column(Date, nullable=False, index=True)
    gender = Column(Text, nullable=False, default='Other', index=True)
    postal_code = Column(Text, nullable=False, )
    role = Column(Text, nullable=False, default='viuser')  # one of vivendor, viuser
    last_login = Column(DateTime, index=True)
    last_notification = Column(DateTime, index=True)
    results = relationship('Result', back_populates='user')
    answers = relationship('Answer', back_populates='user')
    tokens = relationship('Token', back_populates='user')

    composite_index(email, pword)


class Token(base):
    id = Column(Integer, primary_key=True)
    jti = Column(Text, nullable=False, index=True)
    token_type = Column(Text, nullable=False)
    revoked = Column(Boolean, nullable=False)
    expires = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates="tokens")


class Question(base):
    name = Column(Text, primary_key=True)
    answers = relationship('Answer')
    info = Column(Text, nullable=False, default="not yet")
    index_sub_components = relationship('IndexSubComponent')
    qtext = Column(Text, nullable=False, default="not yet")

    @property
    def indexes(self):
        return self.index_sub_components.index_component.index


answer_result = Table('answer_result',
                      base.metadata,
                      Column('answer_id', Integer, ForeignKey('answers.id')),
                      Column('result_id', Integer, ForeignKey('results.id'))
                      )


class Answer(base):
    id = Column(Integer, primary_key=True)
    results = relationship('Result')
    question = Column(Question, nullable=False)
    time_received = Column(DateTime, nullable=False)
    answer = Column(Text, nullable=False)
    user_id = Column(User, ForeignKey('users.id'))
    user = relationship('User', back_populates="answers")

    composite_index(user, question, time_received)

    @property
    def indexes(self):
        return self.question.indexes


class Result(base):
    id = Column(Integer, primary_key=True)
    result_components = relationship('ResultComponent')
    answers = relationship(Answer)
    time_generated = Column(DateTime, nullable=False)
    points = Column(Integer, nullable=False)
    maxforanswered = Column(Integer, nullable=False)
    index = Column('Index', nullable=False)
    user_id = Column(User, ForeignKey('users.id'))
    user = relationship('User', back_populates="results")

    composite_index(user, index, time_generated)

    @property
    def name(self):
        return self.index.name

    @property
    def maxpoints(self):
        return self.index.maxpoints


class ResultComponent(base):
    id = Column(Integer, primary_key=True)
    result = Column(Result)
    result_sub_components = relationship('ResultSubComponent')
    points = Column(Integer)
    maxforanswered = Column(Integer)
    index_component = Column('IndexComponent')

    @property
    def name(self):
        return self.index_component.name

    @property
    def maxpoints(self):
        return self.index_component.maxpoints


class ResultSubComponent(base):
    id = Column(Integer, primary_key=True)
    result_component = Column(ResultComponent)
    points = Column(Integer)
    maxforanswered = Column(Integer)
    index_sub_component = Column('IndexSubComponent')

    @property
    def name(self):
        return self.index_sub_component.name

    @property
    def maxpoints(self):
        return self.index_sub_component.maxpoints


class Index(base):
    name = Column(Text, primary_key=True)
    maxpoints = Column(Integer)
    index_components = relationship('IndexComponent')
    results = relationship(Result)

    @property
    def questions(self):
        return self.index_components.index_sub_components.questions


class IndexComponent(base):
    name = Column(Text, primary_key=True)
    maxpoints = Column(Integer)
    index = Column(Index)
    index_sub_components = relationship('IndexSubComponent')
    result_components = relationship(ResultComponent)
    info = Column(Text)
    recommendation = Column(Text)

    @property
    def questions(self):
        return self.index_sub_components.questions


class IndexSubComponent(base):
    name = Column(Text, primary_key=True)
    maxpoints = Column(Integer)
    index_component = Column(IndexComponent)
    result_sub_components = relationship(ResultSubComponent)
    info = Column(Text)
    recommendation = Column(Text)
    questions = relationship(Question)
