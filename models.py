from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Index, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(256), nullable=False, unique=True)
    pword = Column(String(256), nullable=False)
    first_name = Column(String(256), nullable=False)
    birth_date = Column(Date, nullable=False, index=True)
    gender = Column(String(8), nullable=False, default='Other', index=True)
    postal_code = Column(String(256), nullable=False, )
    role = Column(String(32), nullable=False, default='viuser')  # one of vivendor, viuser
    last_login = Column(DateTime, index=True)
    last_notification = Column(DateTime, index=True)
    # foreign keys
    # relationships
    results = relationship('Result', cascade="all, delete-orphan", back_populates='user', order_by="Result.time_generated.desc()")
    answers = relationship('Answer', cascade="all, delete-orphan", back_populates='user', order_by="Answer.time_received.desc(), Answer.question_name")
    tokens = relationship('Token', cascade="all, delete-orphan", back_populates='user')

# indexes
Index('user_idx_email_pword', User.email, User.pword)


class Token(Base):
    __tablename__ = 'token'
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(256), nullable=False, index=True)
    token_type = Column(String(10), nullable=False)
    revoked = Column(Boolean, nullable=False)
    expires = Column(DateTime, nullable=False)
    # foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    # relationships
    user = relationship('User', back_populates='tokens')


indexsubcomponent_question = Table('indexsubcomponent_question',
                                      Base.metadata,
                                      Column('indexsubcomponent_name', String(256), ForeignKey('indexsubcomponent.name'), nullable=False, index=True),
                                      Column('question_name', String(256), ForeignKey('question.name'), nullable=False, index=True)
                                      )


class Question(Base):
    __tablename__ = 'question'
    name = Column(String(256), primary_key=True)
    info = Column(String(2048), nullable=False, default='not yet')
    qtext = Column(String(2048), nullable=False, default='not yet')
    # foreign keys
    # relationships
    index_sub_components = relationship('IndexSubComponent', secondary=indexsubcomponent_question, back_populates='questions')
    answers = relationship('Answer', back_populates='question', order_by="Answer.user_id, Answer.time_received.desc(), Answer.question_name")


answer_result = Table('answer_result',
                      Base.metadata,
                      Column('answer_id', Integer, ForeignKey('answer.id'), index=True),
                      Column('result_id', Integer, ForeignKey('result.id'), index=True)
                      )


class Answer(Base):
    __tablename__ = 'answer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time_received = Column(DateTime, nullable=False)
    answer = Column(String(256), nullable=False)
    # foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    question_name = Column(String(256), ForeignKey('question.name'), nullable=False, index=True)
    # relationships
    user = relationship('User', back_populates='answers')
    question = relationship('Question', back_populates='answers')
    results = relationship('Result', secondary=answer_result, back_populates='answers')

# indexes
Index('answer_idx_user_question_time', Answer.user_id, Answer.question_name, Answer.time_received)


class Result(Base):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True, autoincrement=True)
    time_generated = Column(DateTime, nullable=False)
    points = Column(Integer, nullable=False)
    maxforanswered = Column(Integer, nullable=False)
    # foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    index_name = Column(String(256), ForeignKey('index.name'), nullable=False, index=True)
    # relationships
    user = relationship('User', back_populates='results')
    index = relationship('Index', back_populates='results')
    answers = relationship('Answer', secondary=answer_result, back_populates='results', order_by="Answer.time_received.desc(), Answer.question_name")
    result_components = relationship('ResultComponent', cascade="all, delete-orphan", back_populates='result', order_by="ResultComponent.id")

# indexes
Index('result_idx_user_index_time', Result.user_id, Result.index_name, Result.time_generated)


class ResultComponent(Base):
    __tablename__ = 'resultcomponent'
    id = Column(Integer, primary_key=True, autoincrement=True)
    points = Column(Integer)
    maxforanswered = Column(Integer)
    # foreign keys
    result_id = Column(Integer, ForeignKey('result.id'), nullable=False, index=True)
    indexcomponent_name = Column(String(256), ForeignKey('indexcomponent.name'), nullable=False, index=True)
    # relationships
    result = relationship('Result', back_populates='result_components')
    result_sub_components = relationship('ResultSubComponent', cascade="all, delete-orphan", back_populates='result_component', order_by="ResultSubComponent.id")
    index_component = relationship('IndexComponent', back_populates='result_components')


class ResultSubComponent(Base):
    __tablename__ = 'resultsubcomponent'
    id = Column(Integer, primary_key=True, autoincrement=True)
    points = Column(Integer)
    maxforanswered = Column(Integer)
    # foreign keys
    resultcomponent_id = Column(Integer, ForeignKey('resultcomponent.id'), nullable=False, index=True)
    indexsubcomponent_name = Column(String(256), ForeignKey('indexsubcomponent.name'), nullable=False, index=True)
    # relationships
    result_component = relationship('ResultComponent', back_populates='result_sub_components')
    index_sub_component = relationship('IndexSubComponent', back_populates='result_sub_components')


class Index(Base):
    __tablename__ = 'index'
    name = Column(String(256), primary_key=True)
    maxpoints = Column(Integer)
    # foreign keys
    # relationships
    index_components = relationship('IndexComponent', cascade="all, delete-orphan", back_populates='index', order_by="IndexComponent.name")
    results = relationship('Result', back_populates='index')


class IndexComponent(Base):
    __tablename__ = 'indexcomponent'
    name = Column(String(256), primary_key=True)
    maxpoints = Column(Integer)
    info = Column(String(2048))
    recommendation = Column(String(2048))
    # foreign keys
    index_name = Column(String(256), ForeignKey('index.name'), nullable=False, index=True)
    # relationships
    index = relationship('Index', back_populates='index_components')
    index_sub_components = relationship('IndexSubComponent', cascade="all, delete-orphan", back_populates='index_component', order_by="IndexSubComponent.name")
    result_components = relationship('ResultComponent', back_populates='index_component')


class IndexSubComponent(Base):
    __tablename__ = 'indexsubcomponent'
    name = Column(String(256), primary_key=True)
    maxpoints = Column(Integer)
    info = Column(String(2048))
    recommendation = Column(String(2048))
    # foreign keys
    indexcomponent_name = Column(String(256), ForeignKey('indexcomponent.name'), nullable=False, index=True)
    # relationships
    questions = relationship('Question', secondary=indexsubcomponent_question, back_populates='index_sub_components')
    index_component = relationship('IndexComponent', back_populates='index_sub_components')
    result_sub_components = relationship('ResultSubComponent', back_populates='index_sub_component')
