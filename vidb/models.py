from app import db
from sqlalchemy.ext.hybrid import hybrid_property


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    pword = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    birth_Date = db.Column(db.Date, nullable=False, index=True)
    gender = db.Column(db.Text, nullable=False, default='Other', index=True)
    postal_code = db.Column(db.Text, nullable=False, )
    role = db.Column(db.Text, nullable=False, default='viuser')  # one of vivendor, viuser
    last_login = db.Column(db.DateTime, index=True)
    last_notification = db.Column(db.DateTime, index=True)
    # foreign keys
    # relationships
    results = db.relationship('Result', back_populates='user')
    answers = db.relationship('Answer', back_populates='user')
    tokens = db.relationship('Token', back_populates='user')

# indexes
db.Index('user_idx_email_pword', User.email, User.pword)


class Token(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.Text, nullable=False, index=True)
    token_type = db.Column(db.Text, nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    # relationships
    user = db.relationship('User', back_populates='tokens')



indexsubcomponent_question = db.Table('indexsubcomponent_question',
                                      db.Model.metadata,
                                      db.Column('indexsubcomponent_name', db.Text, db.ForeignKey('indexsubcomponent.name'), nullable=False, index=True),
                                      db.Column('question_name', db.Text, db.ForeignKey('question.name'), nullable=False, index=True)
                                      )


class Question(db.Model):
    __tablename__ = 'question'
    name = db.Column(db.Text, primary_key=True)
    info = db.Column(db.Text, nullable=False, default='not yet')
    qtext = db.Column(db.Text, nullable=False, default='not yet')
    # foreign keys
    # relationships
    index_sub_components = db.relationship('IndexSubComponent', secondary=indexsubcomponent_question, back_populates='questions')
    answers = db.relationship('Answer', back_populates='question')

    @hybrid_property
    def indexes(self):
        return self.index_sub_components.index_component.index


answer_result = db.Table('answer_result',
                      db.Model.metadata,
                      db.Column('answer_id', db.Integer, db.ForeignKey('answer.id'), index=True),
                      db.Column('result_id', db.Integer, db.ForeignKey('result.id'), index=True)
                      )


class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_received = db.Column(db.DateTime, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    question_name = db.Column(db.Text, db.ForeignKey('question.name'), nullable=False, index=True)
    # relationships
    user = db.relationship('User', back_populates='answers')
    question = db.relationship('Question', back_populates='answers')
    results = db.relationship('Result', secondary=answer_result, back_populates='answers')

    @hybrid_property
    def indexes(self):
        return self.question.indexes

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
    index_name = db.Column(db.Text, db.ForeignKey('index.name'), nullable=False, index=True)
    # relationships
    user = db.relationship('User', back_populates='answers')
    index = db.relationship('Index', back_populates='results')
    answers = db.relationship('Answer', secondary=answer_result, back_populates='results')
    result_components = db.relationship('ResultComponent', back_populates='result')

    @hybrid_property
    def name(self):
        return self.index.name

    @hybrid_property
    def maxpoints(self):
        return self.index.maxpoints

# indexes
db.Index('result_idx_user_index_time', Result.user_id, Result.index_name, Result.time_generated)


class ResultComponent(db.Model):
    __tablename__ = 'resultcomponent'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    points = db.Column(db.Integer)
    maxforanswered = db.Column(db.Integer)
    # foreign keys
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False, index=True)
    indexcomponent_name = db.Column(db.Text, db.ForeignKey('indexcomponent.name'), nullable=False, index=True)
    # relationships
    result = db.relationship('Result', back_populates='result_components')
    result_sub_components = db.relationship('ResultSubComponent', back_populates='result_component')
    index_component = db.relationship('IndexComponent', back_populates='result_components')

    @hybrid_property
    def name(self):
        return self.index_component.name

    @hybrid_property
    def maxpoints(self):
        return self.index_component.maxpoints


class ResultSubComponent(db.Model):
    __tablename__ = 'resultsubcomponent'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    points = db.Column(db.Integer)
    maxforanswered = db.Column(db.Integer)
    # foreign keys
    resultcomponent_id = db.Column(db.Integer, db.ForeignKey('resultcomponent.id'), nullable=False, index=True)
    indexsubcomponent_name = db.Column(db.Text, db.ForeignKey('indexsubcomponent.name'), nullable=False, index=True)
    # relationships
    result_component = db.relationship('ResultComponent', back_populates='result_sub_components')
    db.relationship('IndexSubComponent', secondary=indexsubcomponent_question, back_populates='questions')

    @hybrid_property
    def name(self):
        return self.index_sub_component.name

    @hybrid_property
    def maxpoints(self):
        return self.index_sub_component.maxpoints


class Index(db.Model):
    __tablename__ = 'index'
    name = db.Column(db.Text, primary_key=True)
    maxpoints = db.Column(db.Integer)
    # foreign keys
    # relationships
    index_components = db.relationship('IndexComponent', back_populates='index')
    results = db.relationship('Result', back_populates='index')

    @hybrid_property
    def questions(self):
        return self.index_components.index_sub_components.questions


class IndexComponent(db.Model):
    __tablename__ = 'indexcomponent'
    name = db.Column(db.Text, primary_key=True)
    maxpoints = db.Column(db.Integer)
    info = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    # foreign keys
    index_name = db.Column(db.Text, db.ForeignKey('index.name'), nullable=False, index=True)
    # relationships
    index_sub_components = db.relationship('IndexSubComponent', back_populates='index_component')
    result_components = db.relationship('ResultComponent', back_populates='index_component')

    @hybrid_property
    def questions(self):
        return self.index_sub_components.questions


class IndexSubComponent(db.Model):
    __tablename__ = 'indexsubcomponent'
    name = db.Column(db.Text, primary_key=True)
    maxpoints = db.Column(db.Integer)
    info = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    # foreign keys
    indexcomponent_name = db.Column(db.Text, db.ForeignKey('indexcomponent.name'), nullable=False, index=True)
    # relationships
    questions = db.relationship('Question', secondary=indexsubcomponent_question, back_populates='index_sub_components')
    index_component = db.relationship('IndexComponent', back_populates='index_sub_components')
    result_sub_components = db.relationship('ResultSubComponent', back_populates='index_sub_component')
