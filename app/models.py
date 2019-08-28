from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    pword = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    birth_Date = db.Column(db.Date, nullable=False, index=True)
    gender = db.Column(db.Text, nullable=False, default='Other', index=True)
    postal_code = db.Column(db.Text, nullable=False, )
    role = db.Column(db.Text, nullable=False, default='viuser')  # one of vivendor, viuser
    last_login = db.Column(db.DateTime, index=True)
    last_notification = db.Column(db.DateTime, index=True)
    results = db.relationship('Result', back_populates='user')
    answers = db.relationship('Answer', back_populates='user')
    tokens = db.relationship('Token', back_populates='user')

    db.composite_index(email, pword)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.Text, nullable=False, index=True)
    token_type = db.Column(db.Text, nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates="tokens")


class Question(db.Model):
    name = db.Column(db.Text, primary_key=True)
    answers = db.relationship('Answer')
    info = db.Column(db.Text, nullable=False, default="not yet")
    index_sub_components = db.relationship('IndexSubComponent')
    qtext = db.Column(db.Text, nullable=False, default="not yet")

    @property
    def indexes(self):
        return self.index_sub_components.index_component.index


answer_result = db.Table('answer_result',
                      db.Model.metadata,
                      db.Column('answer_id', db.Integer, db.ForeignKey('answers.id')),
                      db.Column('result_id', db.Integer, db.ForeignKey('results.id'))
                      )


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    results = db.relationship('Result')
    question = db.Column(Question, nullable=False)
    time_received = db.Column(db.DateTime, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    user_id = db.Column(User, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates="answers")

    db.composite_index(user, question, time_received)

    @property
    def indexes(self):
        return self.question.indexes


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_components = db.relationship('ResultComponent')
    answers = db.relationship(Answer)
    time_generated = db.Column(db.DateTime, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    maxforanswered = db.Column(db.Integer, nullable=False)
    index = db.Column('Index', nullable=False)
    user_id = db.Column(User, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates="results")

    db.composite_index(user, index, time_generated)

    @property
    def name(self):
        return self.index.name

    @property
    def maxpoints(self):
        return self.index.maxpoints


class ResultComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(Result)
    result_sub_components = db.relationship('ResultSubComponent')
    points = db.Column(db.Integer)
    maxforanswered = db.Column(db.Integer)
    index_component = db.Column('IndexComponent')

    @property
    def name(self):
        return self.index_component.name

    @property
    def maxpoints(self):
        return self.index_component.maxpoints


class ResultSubComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_component = db.Column(ResultComponent)
    points = db.Column(db.Integer)
    maxforanswered = db.Column(db.Integer)
    index_sub_component = db.Column('IndexSubComponent')

    @property
    def name(self):
        return self.index_sub_component.name

    @property
    def maxpoints(self):
        return self.index_sub_component.maxpoints


class Index(db.Model):
    name = db.Column(db.Text, primary_key=True)
    maxpoints = db.Column(db.Integer)
    index_components = db.relationship('IndexComponent')
    results = db.relationship(Result)

    @property
    def questions(self):
        return self.index_components.index_sub_components.questions


class IndexComponent(db.Model):
    name = db.Column(db.Text, primary_key=True)
    maxpoints = db.Column(db.Integer)
    index = db.Column(Index)
    index_sub_components = db.relationship('IndexSubComponent')
    result_components = db.relationship(ResultComponent)
    info = db.Column(db.Text)
    recommendation = db.Column(db.Text)

    @property
    def questions(self):
        return self.index_sub_components.questions


class IndexSubComponent(db.Model):
    name = db.Column(db.Text, primary_key=True)
    maxpoints = db.Column(db.Integer)
    index_component = db.Column(IndexComponent)
    result_sub_components = db.relationship(ResultSubComponent)
    info = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    questions = db.relationship(Question)
    