import logging
from . import utilities
from typing import Tuple, Dict, Union

"""Calculate the Exercise VI score

    An individual class instance is created for each individual set of base inpiut data.
    
    Input Data:
    age
    minutes of vigorous activity
    minutes of moderate activity
    days exercised
    days of resistance exercise
    sets of resistance exercise per day
    days of flexibility exercise
    days of flexibility activity
    days of balance and agility exercise
    non-sedentary hours per day
"""

# 0,1,2,3,4,more than 4
DaysPhysicalActivityPoints = utilities.PointsMap({'1': 0,
                                                  '2': 12,
                                                  '3': 18,
                                                  '4': 23,
                                                  '5': 27,
                                                  '6': 30})
# 0,1,more than 1
DaysResistanceExercisePoints = utilities.PointsMap({'1': 0,
                                                    '2': 8,
                                                    '3': 15})
# 0,1,2,3,more than 3
SetsResistanceExercisePoints = utilities.PointsMap({'1': 0,
                                                    '2': 6,
                                                    '3': 9,
                                                    '4': 12,
                                                    '5': 15})
# 0,1,2,more than 2
DaysFlexibilityExercisePoints = utilities.PointsMap({'1': 0,
                                                     '2': 8,
                                                     '3': 12,
                                                     '4': 15})

# 0,1-10,11-20,more than 20
MinutesFlexibilityActivityPoints = utilities.PointsMap({'1': 0,
                                                        '2': 8,
                                                        '3': 12,
                                                        '4': 15})
# 0,1,more than 1
DaysBalanceAndAgilityExercisePoints = utilities.PointsMap({'1': 0,
                                                           '2': 8,
                                                           '3': 15})
# 0,1-20,21-40,more than 40
MinutesBalanceAndAgilityActivityPoints = utilities.PointsMap({'1': 0,
                                                              '2': 8,
                                                              '3': 12,
                                                              '4': 15})
# 0,1,2-3,more than 3
NonSedentaryBehaviorPoints = utilities.PointsMap({'1': 0,
                                                  '2': 10,
                                                  '3': 20,
                                                  '4': 30})

ActivityLevelAgeThreshold = 65
MaxExerciseActivityPointsAvailable = 150
VIActivityGoalVigorousUnderSixtyfive = 180
VIActivityGoalVigorousSixtyfivePlus = 90
VIActivityGoalModerate = 300
VIActivityGoalVigorousCombinedUnderSixtyFive = 120
VIActivityGoalModerateCombinedUnderSixtyFive = 180
VIActivityGoalVigorousCombinedSixtyFivePlus = 60
VIActivityGoalModerateCombinedSixtyFivePlus = 180


def name() -> str:
    return 'EXERCISE'


def inputs() -> Tuple[str, ...]:
    return ('BirthDate', 'MinutesVigorousExercise', 'MinutesModerateExercise',
              'DaysPhysicalActivity', 'DaysResistanceExercise', 'SetsResistanceExercise', 'DaysFlexibilityExercise',
              'MinutesFlexibilityActivity', 'DaysBalanceAgilityExercise', 'MinutesBalanceAgilityActivity',
              'AverageHoursNonSedentary')


def vi_points(answers: Dict[str, str]) -> Dict[str, Union[int, Dict[str, Dict[str, int]]]]:
    logging.info("calculating score for %s" % name())

    results = {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0,
               'COMPONENTS': {'EXERCISE': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'DAYSEX': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'DAYSRES': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'SETSRES': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'DAYSFLEX': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'MINSFLEX': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'DAYSBAL': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'MINSBAL': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'HOURSNONSED': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0}}}

    results['COMPONENTS']['EXERCISE']['MAXPOINTS'] = MaxExerciseActivityPointsAvailable
    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['EXERCISE']['MAXPOINTS']
    # answer should be int
    minsExercised = utilities.strToInt(answers['MinutesPhysicalActivity'])
    if minsExercised:
        results['COMPONENTS']['EXERCISE']['MAXFORANSWERED'] = results['COMPONENTS']['EXERCISE']['MAXPOINTS']
        results['MAXFORANSWERED'] = results['MAXFORANSWERED'] + results['COMPONENTS']['EXERCISE']['MAXFORANSWERED']

        if minsExercised > 0:
            bdate = utilities.strToDate(answers['BirthDate'])
            minutesVigorousActivity = utilities.strToInt(answers['MinutesVigorousExercise'])
            minutesModerateActivity = utilities.strToInt(answers['MinutesModerateExercise'])
            if bdate is not None and minutesVigorousActivity is not None and minutesModerateActivity is not None:
                age = utilities.ageFromBirthDate(bdate)

                # Determine if any of the VI Ultimate GOAL LEVEL thresholds have been met)
                if age < ActivityLevelAgeThreshold:
                    if minutesVigorousActivity >= VIActivityGoalVigorousUnderSixtyfive:
                        # Vigorous GOAL Met, return full points
                        logging.info("vigorous goal met, score increased by %d", MaxExerciseActivityPointsAvailable)
                        results['COMPONENTS']['EXERCISE']['POINTS'] = MaxExerciseActivityPointsAvailable
                        results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                    elif minutesModerateActivity >= VIActivityGoalModerate:
                        # Moderate GOAL Met, return full points
                        logging.info("moderate goal met, score increased by %d", MaxExerciseActivityPointsAvailable)
                        results['COMPONENTS']['EXERCISE']['POINTS'] = MaxExerciseActivityPointsAvailable
                        results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                    elif (minutesVigorousActivity >= VIActivityGoalVigorousCombinedUnderSixtyFive) and (
                            minutesModerateActivity >= VIActivityGoalModerateCombinedUnderSixtyFive):
                        # Combined GOAL Met, return full points
                        logging.info("combined goal met, score increased by %d", MaxExerciseActivityPointsAvailable)
                        results['COMPONENTS']['EXERCISE']['POINTS'] = MaxExerciseActivityPointsAvailable
                        results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                    else:
                        # no ULTIMATE GOAL level was achieved, determine highest level reached;
                        percentVigorousMet = minutesVigorousActivity / VIActivityGoalVigorousUnderSixtyfive
                        percentModerateMet = minutesModerateActivity / VIActivityGoalModerate
                        percentCombinedVigorousMet = minutesVigorousActivity / VIActivityGoalVigorousCombinedUnderSixtyFive
                        percentCombinedModerateMet = minutesModerateActivity / VIActivityGoalModerateCombinedUnderSixtyFive
                        percentCombinedMet = (percentCombinedVigorousMet + percentCombinedModerateMet) / 2

                        if percentVigorousMet > percentModerateMet:
                            if percentVigorousMet > percentCombinedMet:
                                expts = round(MaxExerciseActivityPointsAvailable * percentVigorousMet)
                                logging.info("no goal met, using %% vigorous, score increased by %d", expts)
                                results['COMPONENTS']['EXERCISE']['POINTS'] = expts
                                results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                            else:
                                expts = round(MaxExerciseActivityPointsAvailable * percentCombinedMet)
                                logging.info("no goal met, using %% combined, score increased by %d", expts)
                                results['COMPONENTS']['EXERCISE']['POINTS'] = expts
                                results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                        else:
                            if percentModerateMet > percentCombinedMet:
                                expts = round(MaxExerciseActivityPointsAvailable * percentCombinedMet)
                                logging.info("no goal met, using %% moderate, score increased by %d", expts)
                                results['COMPONENTS']['EXERCISE']['POINTS'] = expts
                                results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                            else:
                                expts = round(MaxExerciseActivityPointsAvailable * percentCombinedMet)
                                logging.info("no goal met, using %% combined, score increased by %d", expts)
                                results['COMPONENTS']['EXERCISE']['POINTS'] = expts
                                results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                else:
                    if minutesVigorousActivity >= VIActivityGoalVigorousSixtyfivePlus:
                        # Vigorous GOAL Met, return full points
                        logging.info("vigorous goal met, score increased by %d", MaxExerciseActivityPointsAvailable)
                        results['COMPONENTS']['EXERCISE']['POINTS'] = MaxExerciseActivityPointsAvailable
                        results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                    elif minutesModerateActivity >= VIActivityGoalModerate:
                        # Moderate GOAL Met, return full points
                        logging.info("moderate goal met, score increased by %d", MaxExerciseActivityPointsAvailable)
                        results['COMPONENTS']['EXERCISE']['POINTS'] = MaxExerciseActivityPointsAvailable
                        results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                    elif (minutesVigorousActivity >= VIActivityGoalVigorousCombinedSixtyFivePlus) and (
                            minutesModerateActivity >= VIActivityGoalModerateCombinedSixtyFivePlus):
                        # Combined GOAL Met, return full points
                        logging.info("combined goal met, score increased by %d", MaxExerciseActivityPointsAvailable)
                        results['COMPONENTS']['EXERCISE']['POINTS'] = MaxExerciseActivityPointsAvailable
                        results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                    else:
                        # No ULTIMATE GOAL level was achieved, determine highest level reached;
                        percentVigorousMet = minutesVigorousActivity / VIActivityGoalVigorousSixtyfivePlus
                        percentModerateMet = minutesModerateActivity / VIActivityGoalModerate

                        percentCombinedVigorousMet = minutesVigorousActivity / VIActivityGoalVigorousCombinedSixtyFivePlus
                        percentCombinedModerateMet = minutesModerateActivity / VIActivityGoalModerateCombinedSixtyFivePlus
                        percentCombinedMet = (percentCombinedVigorousMet + percentCombinedModerateMet) / 2

                        if percentVigorousMet > percentModerateMet:
                            if percentVigorousMet > percentCombinedMet:
                                expts = round(MaxExerciseActivityPointsAvailable * percentVigorousMet)
                                logging.info("no goal met, using %% vigorous, score increased by %d", expts)
                                results['COMPONENTS']['EXERCISE']['POINTS'] = expts
                                results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                            else:
                                expts = round(MaxExerciseActivityPointsAvailable * percentCombinedMet)
                                logging.info("no goal met, using %% combined, score increased by %d", expts)
                                results['COMPONENTS']['EXERCISE']['POINTS'] = expts
                                results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                        else:
                            if percentModerateMet > percentCombinedMet:
                                expts = round(MaxExerciseActivityPointsAvailable * percentModerateMet)
                                logging.info("no goal met, using %% moderate, score increased by %d", expts)
                                results['COMPONENTS']['EXERCISE']['POINTS'] = expts
                                results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']
                            else:
                                expts = round(MaxExerciseActivityPointsAvailable * percentCombinedMet)
                                logging.info("no goal met, using %% combined, score increased by %d", expts)
                                results['COMPONENTS']['EXERCISE']['POINTS'] = expts
                                results['POINTS'] = results['POINTS'] + results['COMPONENTS']['EXERCISE']['POINTS']

    daysExercised = utilities.strToKey(answers['DaysPhysicalActivity'])
    results = utilities.subpts(daysExercised, 'DAYSEX', DaysPhysicalActivityPoints, results)

    daysOfResistanceExercise = utilities.strToKey(answers['DaysResistanceExercise'])
    results = utilities.subpts(daysOfResistanceExercise, 'DAYSRES', DaysResistanceExercisePoints, results)

    setsOfResistanceExercisePerDay = utilities.strToKey(answers['SetsResistanceExercise'])
    results = utilities.subpts(setsOfResistanceExercisePerDay, 'SETSRES', SetsResistanceExercisePoints, results)

    daysOfFlexibilityExercise = utilities.strToKey(answers['DaysFlexibilityExercise'])
    results = utilities.subpts(daysOfFlexibilityExercise, 'DAYSFLEX', DaysFlexibilityExercisePoints, results)

    minutesOfFlexibilityActivity = utilities.strToKey(answers['MinutesFlexibilityActivity'])
    results = utilities.subpts(minutesOfFlexibilityActivity, 'MINSFLEX', MinutesFlexibilityActivityPoints, results)

    daysOfBalanceAndAgilityExercise = utilities.strToKey(answers['DaysBalanceAgilityExercise'])
    results = utilities.subpts(daysOfBalanceAndAgilityExercise, 'DAYSBAL', DaysBalanceAndAgilityExercisePoints, results)

    minutesOfBalanceAndAgilityActivity = utilities.strToKey(answers['MinutesBalanceAgilityActivity'])
    results = utilities.subpts(minutesOfBalanceAndAgilityActivity, 'MINSBAL', MinutesBalanceAndAgilityActivityPoints,
                               results)

    nonSedentaryHoursPerDay = utilities.strToKey(answers['AverageHoursNonSedentary'])
    results = utilities.subpts(nonSedentaryHoursPerDay, 'HOURSNONSED', NonSedentaryBehaviorPoints, results)

    return results
