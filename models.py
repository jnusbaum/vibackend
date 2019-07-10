from datetime import datetime, date
from pony.orm import *

db = Database()


# vivendors can create new users and login users, cannot look at any data
# viuser can create and look at their data
class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    email = Required(str, unique=True)
    pword = Required(LongStr)
    results = Set('Result')
    answers = Set('Answer')
    tokens = Set('Token')
    first_name = Required(str)
    birth_date = Required(date, index=True)
    gender = Required(str, default='Other', index=True)
    postal_code = Required(str)
    role = Required(str, default='viuser')  # one of vivendor, viuser
    last_login = Optional(datetime, index=True)
    last_notification = Optional(datetime, index=True)
    composite_index(email, pword)


class Token(db.Entity):
    id = PrimaryKey(int, auto=True)
    jti = Required(LongStr, index=True)
    token_type = Required(str)
    user = Required(User, index=True)
    revoked = Required(bool)
    expires = Required(datetime)


class Question(db.Entity):
    name = PrimaryKey(str)
    answers = Set('Answer')
    info = Required(LongStr, default="not yet")
    index_sub_components = Set('IndexSubComponent')
    qtext = Required(LongStr, default="not yet")

    @property
    def indexes(self):
        return self.index_sub_components.index_component.index


class Answer(db.Entity):
    id = PrimaryKey(int, auto=True)
    results = Set('Result')
    question = Required(Question)
    time_received = Required(datetime)
    answer = Required(str)
    user = Required(User)
    composite_index(user, question, time_received)

    @property
    def indexes(self):
        return self.question.indexes


class Result(db.Entity):
    id = PrimaryKey(int, auto=True)
    result_components = Set('ResultComponent')
    answers = Set(Answer)
    time_generated = Required(datetime)
    points = Required(int)
    maxforanswered = Required(int)
    index = Required('VIndex')
    user = Required(User)
    composite_index(user, index, time_generated)

    @property
    def name(self):
        return self.index.name

    @property
    def maxpoints(self):
        return self.index.maxpoints


class ResultComponent(db.Entity):
    id = PrimaryKey(int, auto=True)
    result = Required(Result)
    result_sub_components = Set('ResultSubComponent')
    points = Required(int)
    maxforanswered = Required(int)
    index_component = Required('IndexComponent')

    @property
    def name(self):
        return self.index_component.name

    @property
    def maxpoints(self):
        return self.index_component.maxpoints


class ResultSubComponent(db.Entity):
    id = PrimaryKey(int, auto=True)
    result_component = Required(ResultComponent)
    points = Required(int)
    maxforanswered = Required(int)
    index_sub_component = Required('IndexSubComponent')

    @property
    def name(self):
        return self.index_sub_component.name

    @property
    def maxpoints(self):
        return self.index_sub_component.maxpoints


class VIndex(db.Entity):
    name = PrimaryKey(str)
    maxpoints = Required(int)
    index_components = Set('IndexComponent')
    results = Set(Result)

    @property
    def questions(self):
        return self.index_components.index_sub_components.questions


class IndexComponent(db.Entity):
    name = PrimaryKey(str)
    maxpoints = Required(int)
    index = Required(VIndex)
    index_sub_components = Set('IndexSubComponent')
    result_components = Set(ResultComponent)
    info = Required(LongStr)
    recommendation = Required(LongStr)

    @property
    def questions(self):
        return self.index_sub_components.questions


class IndexSubComponent(db.Entity):
    name = PrimaryKey(str)
    maxpoints = Required(int)
    index_component = Required(IndexComponent)
    result_sub_components = Set(ResultSubComponent)
    info = Required(LongStr)
    recommendation = Required(LongStr)
    questions = Set(Question)
