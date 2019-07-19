import logging
from . import utilities
from typing import Union, Dict, Tuple

"""Calculate the Nutrition VI score

    An individual class instance is created for each individual set of base inpiut data.

    Input Data:
    if pain affected activities
        pain affected activities scale
    if other factors affected activities
        other factors affected activities scale
    if relied on others for help
        relied on others for help scale
    overall health scale
"""

# Not at all, Completely
PainInterferingWithLifePoints = utilities.PointsMap({'1': 20,
                                                     '2': 16,
                                                     '3': 14,
                                                     '4': 12,
                                                     '5': 10,
                                                     '6': 8,
                                                     '7': 6,
                                                     '8': 4,
                                                     '9': 2,
                                                     '10': 0})
# Not at all, Completely
HealthFactorsInterferingWithLifePoints = utilities.PointsMap({'1': 20,
                                                              '2': 16,
                                                              '3': 14,
                                                              '4': 12,
                                                              '5': 10,
                                                              '6': 8,
                                                              '7': 6,
                                                              '8': 4,
                                                              '9': 2,
                                                              '10': 0})
# Not at all, Completely
HowMuchRelianceOnOthersPoints = utilities.PointsMap({'1': 20,
                                                     '2': 16,
                                                     '3': 14,
                                                     '4': 12,
                                                     '5': 10,
                                                     '6': 8,
                                                     '7': 6,
                                                     '8': 4,
                                                     '9': 2,
                                                     '10': 0})
# Excellent, Poor
OverallPerceivedHealthPoints = utilities.PointsMap({'1': 20,
                                                    '2': 16,
                                                    '3': 12,
                                                    '4': 6,
                                                    '5': 0})


def name() -> str:
    return 'PERCEPTION'


def inputs() -> Tuple[str, ...]:
    return ('PainInterferedWithActivities',
            'OtherFactorsInterferedWithActivities',
            'ReliedOnOthersForHelp',
            'OverallHealth')


def vi_points(answers: Dict[str, str]) -> Dict[str, Union[int, Dict[str, Dict[str, int]]]]:
    logging.debug("calculating score for %s" % name())

    results = {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0,
               'COMPONENTS': {'PAINLIFE': {'POINTS': 0, 'MAXPOINTS': PainInterferingWithLifePoints.max(), 'MAXFORANSWERED': 0},
                              'HEALTHLIFE': {'POINTS': 0, 'MAXPOINTS': HealthFactorsInterferingWithLifePoints.max(), 'MAXFORANSWERED': 0},
                              'RELIEDOTHERS': {'POINTS': 0, 'MAXPOINTS': HowMuchRelianceOnOthersPoints.max(), 'MAXFORANSWERED': 0},
                              'PERCEIVEDHEALTH': {'POINTS': 0, 'MAXPOINTS': OverallPerceivedHealthPoints.max(), 'MAXFORANSWERED': 0}}}

    painAffectedActivities = utilities.strToKey(answers, 'PainInterferedWithActivities')
    results = utilities.subpts(painAffectedActivities, 'PAINLIFE', PainInterferingWithLifePoints, results)

    otherFactorsAffectedActivities = utilities.strToKey(answers, 'OtherFactorsInterferedWithActivities')
    results = utilities.subpts(otherFactorsAffectedActivities, 'HEALTHLIFE', HealthFactorsInterferingWithLifePoints,
                               results)

    reliedOnOthersForHelp = utilities.strToKey(answers, 'ReliedOnOthersForHelp')
    results = utilities.subpts(reliedOnOthersForHelp, 'RELIEDOTHERS', HowMuchRelianceOnOthersPoints, results)

    overallHealth = utilities.strToKey(answers, 'OverallHealth')
    results = utilities.subpts(overallHealth, 'PERCEIVEDHEALTH', OverallPerceivedHealthPoints, results)

    return results


