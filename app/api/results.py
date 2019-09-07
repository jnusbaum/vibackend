import logging
from datetime import datetime, date, timedelta
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from vidb.models import User, Result, ResultComponent, IndexComponent
from app import db
from app.api.views import ResultView, ResultComponentView, AnswerView
from app.api import bp
from app.api.errors import VI404Exception, VI403Exception
from app.auth.auth import check_user
from sqlalchemy import func
from sqlalchemy.orm import joinedload

# get result
@bp.route('/results/<int:result_id>', methods=['GET'])
@jwt_required
def get_result(result_id):
    logging.info("in /results/<result_id>[GET]")
    user = check_user(('viuser',))

    result = db.session.query(Result).get(result_id)
    if not result:
        # no result with this id
        raise VI404Exception("No Result with specified id.")

    if result.user != user:
        # resource exists but is not owned by, and therefor enot viewable by, user
        raise VI403Exception("User does not have permission.")
    rresults = {'count': 1, 'data': [ResultView.render(result)]}
    return jsonify(rresults)


# get result component
@bp.route('/results/<int:result_id>/components/<int:component_id>', methods=['GET'])
@jwt_required
def get_result_component(result_id, component_id):
    logging.info("in /results/%s/components/%s[GET]", result_id, component_id)
    # authenticate user
    user = check_user(('viuser',))
    result = db.session.query(Result).get(result_id)
    if not result:
        # no result with this id
        raise VI404Exception("No Result with specified id.")
    if result.user != user:
        # resource exists but is not owned by, and therefor enot viewable by, user
        raise VI403Exception("User does not have permission.")
    component = db.session.query(ResultComponent).get(component_id)
    if not component:
        # Component does not exist
        raise VI404Exception("no ResultComponent with specified id")
    if component.result != result:
        raise VI404Exception("no ResultComponent with specified id in this resource tree")
    rresults = {'count': 1, 'data': [ResultComponentView.render(component)]}
    return jsonify(rresults)


# get answers that went into a result
@bp.route('/results/<int:result_id>/answers', methods=['GET'])
@jwt_required
def get_result_answers(result_id):
    logging.info("in /results/%s/answers[GET]", result_id)
    user = check_user(('viuser',))
    result = db.session.query(Result).options(joinedload(Result.answers)).get(result_id)
    if not result:
        # no result with this id
        raise VI404Exception("No Result with specified id.")

    if result.user != user:
        # resource exists but is not owned by, and therefor enot viewable by, user
        raise VI403Exception("User does not have permission.")

    ranswers = {'count': len(result.answers), 'data': [AnswerView.render(a) for a in result.answers]}
    return jsonify(ranswers)


#
# statistics methods
#

# provide average vi for certain criteria
# age, gender, location, component
# noinspection PyTypeChecker
@bp.route('/statistics', methods=['GET'])
@jwt_required
def get_statistics():
    logging.info("in /statistics[GET]")
    trecv = datetime.utcnow()
    td = date.today()
    # authenticate user
    user = check_user(('viuser',))

    agerange = request.args.get('agerange')
    gender = request.args.get('gender')
    region = request.args.get('region')

    result = None
    vgs = db.session.query(func.avg(Result.points), func.avg(Result.maxforanswered)).join(User)
    if gender:
        vgs = vgs.filter(User.gender == gender)
    if agerange:
        # age range is string like "x-y"
        ages = agerange.split('-')
        dplus = td - timedelta(days=int(ages[0]) * 365)
        dminus = td - timedelta(days=int(ages[1]) * 365)
        vgs = vgs.filter(User.birth_date.between(dminus, dplus))
    vg = vgs.filter(Result.time_generated == db.session.query(func.max(Result.time_generated)).filter(
        Result.user_id == User.id).correlate(User)).first()
    if vg:
        result = {
            'type': 'Result',
            'attributes': {
                'maxforanswered': vg[1],
                'maxpoints': 1000,
                'name': 'Vitality Index',
                'points': vg[0],
                'time_generated': trecv.strftime("%Y-%m-%d-%H-%M-%S"),
                'result_components': []
            }
        }

        vgs = db.session.query(IndexComponent.name, func.avg(ResultComponent.points),
                            func.avg(ResultComponent.maxforanswered)).join(Result).join(User).join(
            IndexComponent).group_by(IndexComponent.name)
        if agerange:
            # age range is string like "x-y"
            ages = agerange.split('-')
            dplus = td - timedelta(days=int(ages[0]) * 365)
            dminus = td - timedelta(days=int(ages[1]) * 365)
            vgs = vgs.filter(User.birth_date.between(dminus, dplus))

        if gender:
            vgs = vgs.filter(User.gender == gender)

        vgs = vgs.filter(Result.time_generated == db.session.query(func.max(Result.time_generated)).filter(
            Result.user_id == User.id).correlate(User))

        for vg in vgs:
            rc = {
                'type': 'ResultComponent',
                'attributes': {
                    'maxforanswered': vg[2],
                    'name': vg[0],
                    'points': vg[1]
                }
            }
            result['attributes']['result_components'].append(rc)

        return jsonify({'count': 1, 'data': [result]})
    else:
        return jsonify({'count': 0, 'data': []})
