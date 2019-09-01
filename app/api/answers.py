import logging
from flask import jsonify
from flask_jwt_extended import jwt_required
from vidb.models import Answer
from app.views import ResultView, AnswerView
from app.api import bp
from app.errors.handlers import VI404Exception, VI403Exception
from app.auth.auth import check_user


# get answer
@bp.route('/answers/<int:answer_id>', methods=['GET'])
@jwt_required
def get_answer(answer_id):
    logging.info("in /answers/<answer_id>[GET]")
    user = check_user(('viuser',))
    answer = Answer.query.get(answer_id)
    if not answer:
        # no answer with this id
        raise VI404Exception("No Answer with specified id.")

    if answer.user != user:
        # resource exists but is not owned by, and therefore not viewable by, user
        raise VI403Exception("User does not have permission.")

    ranswers = {'count': 1, 'data': [AnswerView.render(answer)]}
    return jsonify(ranswers)


# get results that used an answer
@bp.route('/answers/<int:answer_id>/results', methods=['GET'])
@jwt_required
def get_answer_results(answer_id):
    logging.info("in /answers/<answer_id>/results[GET]")
    user = check_user(('viuser',))
    answer = Answer.query.get(answer_id)
    if not answer:
        # no answer with this id
        raise VI404Exception("No Answer with specified id.")

    if answer.user != user:
        # resource exists but is not owned by, and therefore not viewable by, user
        raise VI403Exception("User does not have permission.")

    rresults = {'count': len(answer.results), 'data': [ResultView.render(r) for r in answer.results]}
    return jsonify(rresults)
