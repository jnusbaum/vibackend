import logging
from . import utilities
from typing import Tuple, Dict, Union


"""Calculate the Major Conditions VI score

    An individual class instance is created for each individual set of base inpiut data.
    
    Input Data:
    number of conditions
    number managed by doctor
    number managed by lifestyle
    affect on life
"""
PointDecreasePerMajorCondition = -10
PointIncreaseForDoctorTreatingCondition = 5
PointIncreaseForMangingConditionsWithMedicationandLifestyle = 3
MaxStartingMajorConditionsPoints = 110

# Not at all, Completely
AffectOnLifeFromConditionsPoints = utilities.PointsMap({'1': 0,
                                                        '2': -5,
                                                        '3': -10,
                                                        '4': -15,
                                                        '5': -20,
                                                        '6': -25,
                                                        '7': -30,
                                                        '8': -35,
                                                        '9': -40,
                                                        '10': -45})
# 5 or less, more than 5
NumberMedicationsPoints = utilities.PointsMap({'1': 0,
                                               '2': -20})

"""Calculate the Blood Pressure VI score

    Input data is provided in a dictionary. This class looks for the following keys in the dict:

        SystolicBloodPressure
        DiastolicBloodPressure
"""
SystolicRange = utilities.PointsRange(((120, 10), (140, 8), (160, 6)), 2, False)
DiastolicRange = utilities.PointsRange(((80, 10), (90, 6), (100, 3)), 0, False)

"""Calculate the Cholesterol VI score

    Input data is provided in a dictionary. This class looks for the following keys in the dict:

        HDLCholesterol
        LDLCholesterol
        Triglycerides
"""
LDLRange = utilities.PointsRange(((70, 10), (100, 9), (130, 8), (160, 5), (190, 2)), 0, False)
HDLRange = utilities.PointsRange(((40, 3), (60, 6)), 10, False)
TriRange = utilities.PointsRange(((100, 20), (150, 15), (200, 10), (500, 5)), 0, False)

"""Calculate the Resting heart Rate VI score

    An individual class instance is created for each individual set of base inpiut data.
    
    Input Data:
    resting heart rate
"""
RHRRange = utilities.PointsRange(((60, 10), (65, 9), (70, 8), (75, 7), (80, 6), (85, 5), (90, 3), (95, 1)), 0, False)

"""Calculate the Tobacco VI score

    An individual class instance is created for each individual set of base inpiut data.
    
    Input Data:
    if used tobacco in last 7 days
    if used tobacco in last 6 months
"""
PointDecreaseForTobaccoUsePast7Days = -40
PointDecreaseForTobaccoUsePast60Days = -20

"""Calculate the Body Mass Index VI score

    An individual class instance is created for each individual set of base input data.
    
    Input data is provided in a dictionary. This class looks for the following keys in the dict:

    BirthDate
    Height
    Weight
"""

"""Calculate the Body Mass Index VI score

    An individual class instance is created for each individual set of base input data.
    
   This class looks for the following keys in the dict:

        BirthDate
        Height
        Weight
"""
BMIConstant = 703
BMIAgeThreshold = 70

# lookup tables for VI points based on BMI, use bisect to lookup
AboveBMIThresholdAgeRange = utilities.PointsRange(((15, 0),
                                                   (16, 8),
                                                   (17, 18),
                                                   (18.5, 32),
                                                   (25, 40),
                                                   (26.5, 37),
                                                   (28, 34),
                                                   (29, 30),
                                                   (30, 26),
                                                   (32, 22),
                                                   (34, 18),
                                                   (36, 14),
                                                   (38, 10),
                                                   (40, 8)), 0, False)

BelowBMIThresholdAgeRange = utilities.PointsRange(((15, 0),
                                                   (16, 12),
                                                   (17, 24),
                                                   (18.5, 36),
                                                   (25, 40),
                                                   (26.5, 36),
                                                   (28, 32),
                                                   (29, 28),
                                                   (30, 24),
                                                   (33, 20),
                                                   (34, 16),
                                                   (36, 12),
                                                   (38, 8),
                                                   (40, 4)), 0, False)


def name() -> str:
    return 'MEDICAL'


def inputs() -> Tuple[str, ...]:
    return ('BirthDate',
              'Height',
              'Weight'
              'NumberOfConditions',
              'ConditionsManagedByDoctor',
              'ConditionsManagedByLifestyle',
              'ConditionsAffectOnLife',
              'NumberMedications',
              'SystolicBloodPressure',
              'DiastolicBloodPressure',
              'LDLCholesterol',
              'HDLCholesterol',
              'Triglycerides',
              'RestingHeartRate',
              'UsedTobaccoInPast7Days',
              'UsedTobaccoInPast6Months')


def vi_points(answers: Dict[str, str]) -> Dict[str, Union[int, Dict[str, Dict[str, int]]]]:
    logging.info("calculating score for %s" % name())

    results = {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0,
               'COMPONENTS': {'BMI': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'MEDCONDS': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'NUMMEDS': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'SYS': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'DIA': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'LDL': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'HDL': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'TRI': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'RHR': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'TOBACCO7': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0},
                              'TOBACCO180': {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0}}}

    bmi = None
    bdate = utilities.strToDate(answers['BirthDate'])
    height = utilities.strToInt(answers['Height'])
    weight = utilities.strToInt(answers['Weight'])
    if bdate is not None and height is not None and weight is not None:
        age = utilities.ageFromBirthDate(bdate)
        bmi = (weight / (height * height)) * BMIConstant
        logging.info('bmi = %f', bmi)
        if age <= BMIAgeThreshold:
            results = utilities.subpts(bmi, 'BMI', BelowBMIThresholdAgeRange, results)
        else:
            results = utilities.subpts(bmi, 'BMI', AboveBMIThresholdAgeRange, results)
    else:
        # get max
        results = utilities.subpts(bmi, 'BMI', AboveBMIThresholdAgeRange, results)

    logging.debug('starting medical conditions score at %d', MaxStartingMajorConditionsPoints)

    results['COMPONENTS']['MEDCONDS']['MAXPOINTS'] = MaxStartingMajorConditionsPoints
    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['MEDCONDS']['MAXPOINTS']

    numberOfConditions = utilities.strToInt(answers['NumberOfConditions'])
    if numberOfConditions is not None:
        # number of conditions is answered
        results['COMPONENTS']['MEDCONDS']['MAXFORANSWERED'] = results['COMPONENTS']['MEDCONDS']['MAXPOINTS']
        results['MAXFORANSWERED'] = results['MAXFORANSWERED'] + results['COMPONENTS']['MEDCONDS']['MAXFORANSWERED']
        results['COMPONENTS']['MEDCONDS']['POINTS'] = MaxStartingMajorConditionsPoints

        #
        if numberOfConditions > 0:
            # they have at least one condition and we use the rest of the answers
            # subtractor so no change to max and maxforanswered
            results['COMPONENTS']['MEDCONDS']['POINTS'] = results['COMPONENTS']['MEDCONDS']['POINTS'] + \
                                                          (numberOfConditions * PointDecreasePerMajorCondition)

            # add back if managed by lifestyle
            managedByLifestyle = utilities.strToInt(answers['ConditionsManagedByLifestyle'])
            if managedByLifestyle is not None:
                results['COMPONENTS']['MEDCONDS']['POINTS'] = results['COMPONENTS']['MEDCONDS']['POINTS'] + \
                                                              (
                                                                      managedByLifestyle * PointIncreaseForMangingConditionsWithMedicationandLifestyle)

            # add back if managed by Dr
            managedByDr = utilities.strToInt(answers['ConditionsManagedByDoctor'])
            if managedByDr is not None:
                results['COMPONENTS']['MEDCONDS']['POINTS'] = results['COMPONENTS']['MEDCONDS']['POINTS'] + \
                                                              (managedByDr * PointIncreaseForDoctorTreatingCondition)

            # subtractor so no change to max and maxforanswered
            affectOnLife = utilities.strToKey(answers['ConditionsAffectOnLife'])
            if affectOnLife is not None:
                results['COMPONENTS']['MEDCONDS']['POINTS'] = results['COMPONENTS']['MEDCONDS']['POINTS'] + \
                                                              AffectOnLifeFromConditionsPoints.points(affectOnLife)

        results['POINTS'] = results['POINTS'] + results['COMPONENTS']['MEDCONDS']['POINTS']

    # number of medications taken
    numberMedications = utilities.strToKey(answers['NumberMedications'])
    results = utilities.subpts(numberMedications, 'NUMMEDS', NumberMedicationsPoints, results)

    # blood pressure
    systolic = utilities.strToInt(answers['SystolicBloodPressure'])
    results = utilities.subpts(systolic, 'SYS', SystolicRange, results)

    diastolic = utilities.strToInt(answers['DiastolicBloodPressure'])
    results = utilities.subpts(diastolic, 'DIA', DiastolicRange, results)

    # cholesterol
    tldl = utilities.strToInt(answers['LDLCholesterol'])
    results = utilities.subpts(tldl, 'LDL', LDLRange, results)

    thdl = utilities.strToInt(answers['HDLCholesterol'])
    results = utilities.subpts(thdl, 'HDL', HDLRange, results)

    ttri = utilities.strToInt(answers['Triglycerides'])
    results = utilities.subpts(ttri, 'TRI', TriRange, results)

    # resting heart rate
    restingHeartRate = utilities.strToInt(answers['RestingHeartRate'])
    results = utilities.subpts(restingHeartRate, 'RHR', RHRRange, results)

    # tobacco use
    # these are subtractions so MAX and MAXFORANSWERED stay at the default 0
    usedTobaccoInPast7Days = utilities.strToBool(answers['UsedTobaccoInPast7Days'])
    # have to check for None here as that indicates no answer, False is valid answer
    if usedTobaccoInPast7Days is not None:
        if usedTobaccoInPast7Days:
            results['COMPONENTS']['TOBACCO7']['POINTS'] = PointDecreaseForTobaccoUsePast7Days
            logging.info('score decreased by %d for Tobacco7', results['COMPONENTS']['TOBACCO7']['POINTS'])
            results['POINTS'] = results['POINTS'] + results['COMPONENTS']['TOBACCO7']['POINTS']

    usedTobaccoInPast6Months = utilities.strToBool(answers['UsedTobaccoInPast6Months'])
    # have to check for None here as that indicates no answer, False is valid answer
    if usedTobaccoInPast6Months is not None:
        if usedTobaccoInPast6Months:
            results['COMPONENTS']['TOBACCO180']['POINTS'] = PointDecreaseForTobaccoUsePast60Days
            logging.info('score decreased by %d for Tobacco180', results['COMPONENTS']['TOBACCO180']['POINTS'])
            results['POINTS'] = results['POINTS'] + results['COMPONENTS']['TOBACCO180']['POINTS']

    return results

