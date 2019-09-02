import logging
import datetime
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from vidb.models import User, Result, ResultComponent
from app.views import ResultView, ResultComponentView, AnswerView
from app.api import bp
from app.api.errors import VI404Exception, VI403Exception
from app.auth.auth import check_user
from sqlalchemy.sql.expression import between


# get result
@bp.route('/results/<int:result_id>', methods=['GET'])
@jwt_required
def get_result(result_id):
    logging.info("in /results/<result_id>[GET]")
    user = check_user(('viuser',))

    result = Result.query.get(result_id)
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
    result = Result.query.get(result_id)
    if not result:
        # no result with this id
        raise VI404Exception("No Result with specified id.")
    if result.user != user:
        # resource exists but is not owned by, and therefor enot viewable by, user
        raise VI403Exception("User does not have permission.")
    component = ResultComponent.query.get(component_id)
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
    result = Result.query.get(result_id)
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
    trecv = datetime.datetime.utcnow()
    td = datetime.date.today()
    # authenticate user
    check_user(('viuser',))

    agerange = request.args.get('agerange')
    gender = request.args.get('gender')
    region = request.args.get('region')

    if agerange:
        if gender:
            # age range is string like "x-y"
            ages = agerange.split('-')
            dplus = td - datetime.timedelta(days=int(ages[0]) * 365)
            dminus = td - datetime.timedelta(days=int(ages[1]) * 365)
            # noinspection PyTypeChecker
            vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                         for r in Result for u in User
                         if r.user == u and u.gender == gender
                         and between(u.birth_date, dminus, dplus)
                         and r.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
        else:
            # age range is string like "x-y"
            ages = agerange.split('-')
            dplus = td - datetime.timedelta(days=int(ages[0]) * 365)
            dminus = td - datetime.timedelta(days=int(ages[1]) * 365)
            # noinspection PyTypeChecker
            vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                         for r in Result for u in User
                         if r.user == u
                         and between(u.birth_date, dminus, dplus)
                         and r.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
    else:
        if gender:
            # noinspection PyTypeChecker
            vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                         for r in Result for u in User
                         if r.user == u and u.gender == gender
                         and r.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
        else:
            # noinspection PyTypeChecker
            vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                         for r in Result for u in User
                         if r.user == u
                         and r.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]

    if vgs:
        result = {
            'type': 'Result',
            'attributes': {
                'maxforanswered': vgs[0][2],
                'maxpoints': 1000,
                'name': 'Vitality Index',
                'points': vgs[0][1],
                'time_generated': trecv.strftime("%Y-%m-%d-%H-%M-%S"),
                'result_components': []
            }
        }

        if agerange:
            if gender:
                # age range is string like "x-y"
                ages = agerange.split('-')
                dplus = td - datetime.timedelta(days=int(ages[0]) * 365)
                dminus = td - datetime.timedelta(days=int(ages[1]) * 365)
                # noinspection PyTypeChecker
                vgs = db.session.query(ResultComponent).join(User).filter_by(ResultComponent.gender == User.gender)
                vgs = vgs.filter_by(between(User.birth_date, dminus, dplus))
                for vg in vgs:
                    select((r.name, avg(r.points), avg(r.maxforanswered))
                             for r in ResultComponent for u in User
                             if r.result.user == u and u.gender == gender
                             and between(u.birth_date, dminus, dplus)
                             and r.result.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
            else:
                # age range is string like "x-y"
                ages = agerange.split('-')
                dplus = td - datetime.timedelta(days=int(ages[0]) * 365)
                dminus = td - datetime.timedelta(days=int(ages[1]) * 365)
                # noinspection PyTypeChecker
                vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                             for r in ResultComponent for u in User
                             if r.result.user == u
                             and between(u.birth_date, dminus, dplus)
                             and r.result.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
        else:
            if gender:
                # noinspection PyTypeChecker
                vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                             for r in ResultComponent for u in User
                             if r.result.user == u and u.gender == gender
                             and r.result.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
            else:
                # noinspection PyTypeChecker
                vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                             for r in ResultComponent for u in User
                             if r.result.user == u
                             and r.result.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]

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
