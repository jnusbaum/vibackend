from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    pword = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(256), nullable=False)
    birth_date = db.Column(db.Date, nullable=False, index=True)
    gender = db.Column(db.String(8), nullable=False, default='Other', index=True)
    postal_code = db.Column(db.String(256), nullable=False, )
    role = db.Column(db.String(32), nullable=False, default='viuser')  # one of vivendor, viuser
    last_login = db.Column(db.DateTime, index=True)
    last_notification = db.Column(db.DateTime, index=True)
    # foreign keys
    # relationships
    results = db.relationship('Result', cascade="all, delete-orphan", back_populates='user', order_by="Result.time_generated.desc()")
    answers = db.relationship('Answer', cascade="all, delete-orphan", back_populates='user', order_by="Answer.time_received.desc(), Answer.question_name")
    tokens = db.relationship('Token', cascade="all, delete-orphan", back_populates='user')

# indexes
db.Index('user_idx_email_pword', User.email, User.pword)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(256), nullable=False, index=True)
    token_type = db.Column(db.String(10), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    # relationships
    user = db.relationship('User', back_populates='tokens')


indexsubcomponent_question = db.Table('indexsubcomponent_question',
                                      db.Model.metadata,
                                      db.Column('indexsubcomponent_name', db.String(256), db.ForeignKey('indexsubcomponent.name'), nullable=False, index=True),
                                      db.Column('question_name', db.String(256), db.ForeignKey('question.name'), nullable=False, index=True)
                                      )


class Question(db.Model):
    __tablename__ = 'question'
    name = db.Column(db.String(256), primary_key=True)
    info = db.Column(db.String(2048), nullable=False, default='not yet')
    qtext = db.Column(db.String(2048), nullable=False, default='not yet')
    # foreign keys
    # relationships
    index_sub_components = db.relationship('IndexSubComponent', secondary=indexsubcomponent_question, back_populates='questions')
    answers = db.relationship('Answer', back_populates='question', order_by="Answer.user_id, Answer.time_received.desc(), Answer.question_name")


answer_result = db.Table('answer_result',
                      db.Model.metadata,
                      db.Column('answer_id', db.Integer, db.ForeignKey('answer.id'), index=True),
                      db.Column('result_id', db.Integer, db.ForeignKey('result.id'), index=True)
                      )


class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_received = db.Column(db.DateTime, nullable=False)
    answer = db.Column(db.String(256), nullable=False)
    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    question_name = db.Column(db.String(256), db.ForeignKey('question.name'), nullable=False, index=True)
    # relationships
    user = db.relationship('User', back_populates='answers')
    question = db.relationship('Question', back_populates='answers')
    results = db.relationship('Result', secondary=answer_result, back_populates='answers')

# indexes
db.Index('answer_idx_user_question_time', Answer.user_id, Answer.question_name, Answer.time_received)


class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_generated = db.Column(db.DateTime, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    maxforanswered = db.Column(db.Integer, nullable=False)
    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    index_name = db.Column(db.String(256), db.ForeignKey('index.name'), nullable=False, index=True)
    # relationships
    user = db.relationship('User', back_populates='results')
    index = db.relationship('Index', back_populates='results')
    answers = db.relationship('Answer', secondary=answer_result, back_populates='results', order_by="Answer.time_received.desc(), Answer.question_name")
    result_components = db.relationship('ResultComponent', cascade="all, delete-orphan", back_populates='result', order_by="ResultComponent.id")

# indexes
db.Index('result_idx_user_index_time', Result.user_id, Result.index_name, Result.time_generated)


class ResultComponent(db.Model):
    __tablename__ = 'resultcomponent'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    points = db.Column(db.Integer)
    maxforanswered = db.Column(db.Integer)
    # foreign keys
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False, index=True)
    indexcomponent_name = db.Column(db.String(256), db.ForeignKey('indexcomponent.name'), nullable=False, index=True)
    # relationships
    result = db.relationship('Result', back_populates='result_components')
    result_sub_components = db.relationship('ResultSubComponent', cascade="all, delete-orphan", back_populates='result_component', order_by="ResultSubComponent.id")
    index_component = db.relationship('IndexComponent', back_populates='result_components')


class ResultSubComponent(db.Model):
    __tablename__ = 'resultsubcomponent'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    points = db.Column(db.Integer)
    maxforanswered = db.Column(db.Integer)
    # foreign keys
    resultcomponent_id = db.Column(db.Integer, db.ForeignKey('resultcomponent.id'), nullable=False, index=True)
    indexsubcomponent_name = db.Column(db.String(256), db.ForeignKey('indexsubcomponent.name'), nullable=False, index=True)
    # relationships
    result_component = db.relationship('ResultComponent', back_populates='result_sub_components')
    index_sub_component = db.relationship('IndexSubComponent', back_populates='result_sub_components')


class Index(db.Model):
    __tablename__ = 'index'
    name = db.Column(db.String(256), primary_key=True)
    maxpoints = db.Column(db.Integer)
    # foreign keys
    # relationships
    index_components = db.relationship('IndexComponent', cascade="all, delete-orphan", back_populates='index', order_by="IndexComponent.name")
    results = db.relationship('Result', back_populates='index')


class IndexComponent(db.Model):
    __tablename__ = 'indexcomponent'
    name = db.Column(db.String(256), primary_key=True)
    maxpoints = db.Column(db.Integer)
    info = db.Column(db.String(2048))
    recommendation = db.Column(db.String(2048))
    # foreign keys
    index_name = db.Column(db.String(256), db.ForeignKey('index.name'), nullable=False, index=True)
    # relationships
    index = db.relationship('Index', back_populates='index_components')
    index_sub_components = db.relationship('IndexSubComponent', cascade="all, delete-orphan", back_populates='index_component', order_by="IndexSubComponent.name")
    result_components = db.relationship('ResultComponent', back_populates='index_component')


class IndexSubComponent(db.Model):
    __tablename__ = 'indexsubcomponent'
    name = db.Column(db.String(256), primary_key=True)
    maxpoints = db.Column(db.Integer)
    info = db.Column(db.String(2048))
    recommendation = db.Column(db.String(2048))
    # foreign keys
    indexcomponent_name = db.Column(db.String(256), db.ForeignKey('indexcomponent.name'), nullable=False, index=True)
    # relationships
    questions = db.relationship('Question', secondary=indexsubcomponent_question, back_populates='index_sub_components')
    index_component = db.relationship('IndexComponent', back_populates='index_sub_components')
    result_sub_components = db.relationship('ResultSubComponent', back_populates='index_sub_component')
