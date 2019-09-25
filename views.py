from vidb.models import *


class UserView:
    @classmethod
    def render(cls, user: User):
        dself = {'attributes': {'email': user.email,
                                'first_name': user.first_name,
                                'birth_date': user.birth_date.strftime("%Y-%m-%d"),
                                'gender': user.gender,
                                'postal_code': user.postal_code,
                                'role': user.role,
                                'last_login': user.last_login.strftime("%Y-%m-%d-%H-%M-%S") if user.last_login else None,
                                'last_notification': user.last_notification.strftime("%Y-%m-%d-%H-%M-%S") if user.last_notification else None
                                },
                 'id': str(user.id),
                 'type': 'User',
                 'self': "/users",
                 'relationships': {
                     'results': "/users/results",
                     'answers': "/users/answers"
                     }
                 }
        return dself


class AnswerView:
    @classmethod
    def render(cls, answer: Answer):
        dself = {'attributes': {'time_received': answer.time_received.strftime("%Y-%m-%d-%H-%M-%S"),
                                'answer': answer.answer,
                                'question': answer.question_name
                                },
                 'id': str(answer.id),
                 'type': 'Answer',
                 'self': "/answers/{0}".format(answer.id),
                 'relationships': {
                     'user': "/answers/{0}/user".format(answer.id),
                     'results': "/answers/{0}/results".format(answer.id)
                     }
                 }
        return dself


class ResultComponentView:
    @classmethod
    def render(cls, rc: ResultComponent):
        dself = {'attributes': {'points': rc.points,
                                'maxforanswered': rc.maxforanswered,
                                'name': rc.indexcomponent_name,
                                'maxpoints': rc.index_component.maxpoints
                                },
                 'id': str(rc.id),
                 'type': 'ResultComponent',
                 'self': "/results/{0}/components/{1}".format(rc.result_id, rc.id),
                 'relationships': {
                     'result': "/results/{0}".format(rc.result_id)
                     }
                 }
        return dself


class ResultView:
    @classmethod
    def render(cls, result: Result):
        dself = {'attributes': {'time_generated': result.time_generated.strftime("%Y-%m-%d-%H-%M-%S"),
                                'points': result.points,
                                'maxforanswered': result.maxforanswered,
                                'maxpoints': result.index.maxpoints,
                                'result_components': [ResultComponentView.render(rc) for rc in result.result_components],
                                'name': result.index_name
                                },
                 'id': str(result.id),
                 'type': 'Result',
                 'self': "/results/{0}".format(result.id),
                 'relationships': {
                     'user': "/users",
                     'answers': "/results/{0}/answers".format(result.id)
                    }
                 }
        return dself
