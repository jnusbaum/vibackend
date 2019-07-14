import logging
from typing import List, Dict, Union
from . import Exercise
from . import Medical
from . import Nutrition
from . import Social
from . import Perception

ConstituentModules = (Exercise, Medical, Nutrition, Social, Perception)


def sectionNames() -> List[str]:
    return [x.name() for x in ConstituentModules]


def inputs() -> List[str]:
    xinputs = set()
    for x in ConstituentModules:
        xinputs.update(x.inputs())
    return list(xinputs)


def vi_points(answers: Dict[str, str]) -> Dict[str, Union[int, Dict[str, Dict[str, Union[int, Dict[str, Dict[str, int]]]]]]]:
    # construct point calculators
    score = {'INDEX': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0, 'COMPONENTS': {}}
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

