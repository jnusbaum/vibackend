class UserView:
    @classmethod
    def render(cls, user):
        dself = {'attributes': user.to_dict(with_lazy=True, exclude=['pword', 'id']),
                 'id': str(user.id),
                 'type': 'User',
                 'self': "/users",
                 'relationships': {
                     'results': "/users/results",
                     'answers': "/users/answers"
                 }}
        # convert birthdate to string in our format
        dself['attributes']['birth_date'] = dself['attributes']['birth_date'].strftime("%Y-%m-%d")
        if dself['attributes']['last_login']:
            dself['attributes']['last_login'] = dself['attributes']['last_login'].strftime("%Y-%m-%d-%H-%M-%S")
        return dself


class AnswerView:
    @classmethod
    def render(cls, answer):
        dself = {'attributes': answer.to_dict(with_lazy=True, exclude=['id', 'user']),
                 'id': str(answer.id),
                 'type': 'Answer',
                 'self': "/answers/{0}".format(answer.id),
                 'relationships': {
                     'user': "/answers/{0}/user".format(answer.id),
                     'results': "/answers/{0}/results".format(answer.id)
                 }}
        # convert time_received to string in our format
        dself['attributes']['time_received'] = dself['attributes']['time_received'].strftime("%Y-%m-%d-%H-%M-%S")
        return dself


class ResultComponentView:
    @classmethod
    def render(cls, result):
        dself = {'attributes': result.to_dict(with_lazy=True, exclude=['id', 'result', 'index_component']),
                 'id': str(result.id),
                 'type': 'ResultComponent',
                 'self': "/results/{0}/components/{1}".format(result.result.id, result.id),
                 'relationships': {
                     'result': "/results/{0}".format(result.result.id),
                 }}
        # add index component name as attribute
        dself['attributes']['name'] = result.name
        # add maxpoints from index as attribute
        dself['attributes']['maxpoints'] = result.index_component.maxpoints
        return dself


class ResultView:
    @classmethod
    def render(cls, result):
        dself = {'attributes': result.to_dict(with_lazy=True, exclude=['id', 'user', 'index']),
                 'id': str(result.id),
                 'type': 'Result',
                 'self': "/results/{0}".format(result.id),
                 'relationships': {
                     'user': "/users",
                     'answers': "/results/{0}/answers".format(result.id)
                 }
                 }
        # add index name as attribute
        dself['attributes']['name'] = result.name
        # add maxpoints from indexc as attribute
        dself['attributes']['maxpoints'] = result.index.maxpoints
        # convert time_generated to string in our format
        dself['attributes']['time_generated'] = dself['attributes']['time_generated'].strftime("%Y-%m-%d-%H-%M-%S")
        # noinspection PyTypeChecker
        dself['attributes']['result_components'] = [ResultComponentView.render(rc) for rc in result.result_components]
        return dself
