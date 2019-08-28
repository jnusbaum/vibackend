

# set up pony
db.bind(provider='postgres', host=app.config['DBHOST'],
        database=app.config['DATABASE'],
        user=app.config['DBUSER'],
        password=app.config['DBPWD'],
        sslmode=app.config['DBSSLMODE'])
db.generate_mapping()


def str_to_datetime(ans: str) -> Union[datetime, None]:
    if ans:
        d = datetime.strptime(ans, "%Y-%m-%d-%H-%M-%S")
        # no tz info, assumed to be in UTC
        return d
    return None


@app.before_request
def before_request():
    # log actual full url of each call
    # saves having to correlate with uwsgi server logs
    logging.info("handling request to %s", request.url)


# Define our callback function to check if a token has been revoked or not
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)



#
# user methods
#



#
# answer methods
#

# get answer
@app.route('/answers/<int:answer_id>', methods=['GET'])
@jwt_required
def get_answer(answer_id):
    logging.info("in /answers/<answer_id>[GET]")
    user = check_user(('viuser',))
    answer = None
    try:
        answer = Answer[answer_id]
    except ObjectNotFound:
        # no answer with this id
        raise VI404Exception("No Answer with specified id.")

    if answer.user != user:
        # resource exists but is not owned by, and therefore not viewable by, user
        raise VI403Exception("User does not have permission.")

    ranswers = {'count': 1, 'data': [AnswerView.render(answer)]}
    return jsonify(ranswers)


# get results that used an answer
@app.route('/answers/<int:answer_id>/results', methods=['GET'])
@jwt_required
def get_answer_results(answer_id):
    logging.info("in /answers/<answer_id>/results[GET]")
    user = check_user(('viuser',))
    answer = None
    try:
        answer = Answer[answer_id]
    except ObjectNotFound:
        # no answer with this id
        raise VI404Exception("No Answer with specified id.")

    if answer.user != user:
        # resource exists but is not owned by, and therefore not viewable by, user
        raise VI403Exception("User does not have permission.")

    rresults = {'count': len(answer.results), 'data': [ResultView.render(r) for r in answer.results]}
    return jsonify(rresults)


#
# result methods
#


# get result
@app.route('/results/<int:result_id>', methods=['GET'])
@jwt_required
def get_result(result_id):
    logging.info("in /results/<result_id>[GET]")
    user = check_user(('viuser',))

    result = None
    try:
        result = Result[result_id]
    except ObjectNotFound:
        # no result with this id
        raise VI404Exception("No Result with specified id.")

    if result.user != user:
        # resource exists but is not owned by, and therefor enot viewable by, user
        raise VI403Exception("User does not have permission.")
    rresults = {'count': 1, 'data': [ResultView.render(result)]}
    return jsonify(rresults)


# get result component
@app.route('/results/<int:result_id>/components/<int:component_id>', methods=['GET'])
@jwt_required
def get_result_component(result_id, component_id):
    logging.info("in /results/%s/components/%s[GET]", result_id, component_id)
    # authenticate user
    user = check_user(('viuser',))
    result = None
    try:
        result = Result[result_id]
    except ObjectNotFound:
        # no result with this id
        raise VI404Exception("No Result with specified id.")
    if result.user != user:
        # resource exists but is not owned by, and therefor enot viewable by, user
        raise VI403Exception("User does not have permission.")
    component = None
    try:
        component = ResultComponent[component_id]
    except ObjectNotFound:
        # Component does not exist
        raise VIServiceException(404, "no ResultComponent with specified id")
    if component.result != result:
        raise VIServiceException(404, "no ResultComponent with specified id in this resource tree")
    rresults = {'count': 1, 'data': [ResultComponentView.render(component)]}
    return jsonify(rresults)


# get answers that went into a result
@app.route('/results/<int:result_id>/answers', methods=['GET'])
@jwt_required
def get_result_answers(result_id):
    logging.info("in /results/%s/answers[GET]", result_id)
    user = check_user(('viuser',))

    result = None
    try:
        result = Result[result_id]
    except ObjectNotFound:
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
@app.route('/statistics', methods=['GET'])
@jwt_required
def get_statistics():
    logging.info("in /statistics[GET]")
    trecv = datetime.utcnow()
    # authenticate user
    check_user(('viuser',))

    agerange = request.args.get('agerange')
    gender = request.args.get('gender')
    region = request.args.get('region')

    if agerange:
        if gender:
            # age range is string like "x-y"
            ages = agerange.split('-')
            dplus = date.today() - timedelta(days=int(ages[0]) * 365)
            dminus = date.today() - timedelta(days=int(ages[1]) * 365)
            # noinspection PyTypeChecker
            vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                         for r in Result for u in User
                         if r.user == u and u.gender == gender
                         and between(u.birth_date, dminus, dplus)
                         and r.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
        else:
            # age range is string like "x-y"
            ages = agerange.split('-')
            dplus = date.today() - timedelta(days=int(ages[0]) * 365)
            dminus = date.today() - timedelta(days=int(ages[1]) * 365)
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
                dplus = date.today() - timedelta(days=int(ages[0]) * 365)
                dminus = date.today() - timedelta(days=int(ages[1]) * 365)
                # noinspection PyTypeChecker
                vgs = select((r.name, avg(r.points), avg(r.maxforanswered))
                             for r in ResultComponent for u in User
                             if r.result.user == u and u.gender == gender
                             and between(u.birth_date, dminus, dplus)
                             and r.result.time_generated == max(r2.time_generated for r2 in Result if r2.user == u))[:]
            else:
                # age range is string like "x-y"
                ages = agerange.split('-')
                dplus = date.today() - timedelta(days=int(ages[0]) * 365)
                dminus = date.today() - timedelta(days=int(ages[1]) * 365)
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


if __name__ == '__main__':
    app.run(host=app.config['WWWHOST'],
            port=app.config['WWWPORT'])
