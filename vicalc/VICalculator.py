import logging

import Exercise
import Medical
import Nutrition
import Social
import Perception

ConstituentModules = (Exercise, Medical, Nutrition, Social, Perception)


def section_names():
    return [x.name() for x in ConstituentModules]


def inputs():
    inputs = set()
    for x in ConstituentModules:
        inputs.update(x.inputs())
    return list(inputs)


def vi_points(answers):
    # construct point calculators
    score = {}
    score['INDEX'] = 0
    score['MAXPOINTS'] = 0
    score['MAXFORANSWERED'] = 0
    score['COMPONENTS'] = {}
    for constituent in ConstituentModules:
        name = constituent.name()
        logging.info('calculating index for %s', name)
        cscore = constituent.vi_points(answers)
        logging.info('score for %s = %s', name, cscore['POINTS'])
        score['COMPONENTS'][name] = cscore
        score['INDEX'] = score['INDEX'] + cscore['POINTS']
        score['MAXPOINTS'] = score['MAXPOINTS'] + cscore['MAXPOINTS']
        score['MAXFORANSWERED'] = score['MAXFORANSWERED'] + cscore['MAXFORANSWERED']

    logging.info('vitality index = %s', score['INDEX'])
    return score

