import logging
from . import utilities
from typing import Tuple, Dict, Union


"""Calculate the Nutrition VI score

    An individual class instance is created for each individual set of base inpiut data.
    
    Input Data:
    gender
    number of fruit servings
    number of vegetable servings
    
    number of eight ounce drinks
    number of caffeinated drinks
    number of water drinks
    number of alcoholic drinks
"""

FruitAndVegServingsMap = {'1': {'1': 0, '2': 5, '3': 10, '4': 15, '5': 20},
                          '2': {'1': 5, '2': 10, '3': 15, '4': 20, '5': 25},
                          '3': {'1': 10, '2': 15, '3': 20, '4': 25, '5': 30}}
FruitAndVegServingsMapMax = 30
# 0,1-2, more than 2
FruitServingsPoints = utilities.PointsMap({'1': 0,
                                           '2': 10,
                                           '3': 20})
# 0,1-2,3-4,5-6,more than 6
VegetableServingsPoints = utilities.PointsMap({'1': 0,
                                               '2': 10,
                                               '3': 20,
                                               '4': 25,
                                               '5': 30})
# 0-3,4-5.6-7,more than 7
EightOunceDrinksPoints = utilities.PointsMap({'1': 0,
                                              '2': 0,
                                              '3': 5,
                                              '4': 8,
                                              '5': 10})
# 0-2,3-5,6-8,more than 8
WaterServingsPoints = utilities.PointsMap({'1': 0,
                                           '2': 5,
                                           '3': 8,
                                           '4': 10})
# 0-2,3-5,6-8,more than 8
CaffeinatedDrinksPoints = utilities.PointsMap({'1': 0,
                                               '2': -5,
                                               '3': -8,
                                               '4': -10})
# 0-2,3-4,more than 4 (male)
AlcoholicDrinksMalePoints = utilities.PointsMap({'1':0,
                                                 '2': -8,
                                                 '3': -10})
# 0-1,2-3,more than 3 (female)
AlcoholicDrinksFemalePoints = utilities.PointsMap({'1': 0,
                                                   '2': -8,
                                                   '3': -10})


def name() -> str:
    return 'NUTRITION'


def inputs() -> Tuple[str, ...]:
    return ('Gender','NumberFruitServings','NumberVegetableServings','NumberDrinks','NumberCaffeinatedDrinks','NumberWaterDrinks','NumberAlcoholicDrinks')


def vi_points(answers: Dict[str, str]) -> Dict[str, Union[int, Dict[str, Dict[str, int]]]]:
    logging.debug("calculating score for %s" % name())

    results = {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0,
               'COMPONENTS': {'NUMFRUITSSERVS': {'POINTS': 0, 'MAXPOINTS': FruitServingsPoints.max(), 'MAXFORANSWERED': 0},
                              'NUMVEGSERVS': {'POINTS': 0, 'MAXPOINTS': VegetableServingsPoints.max(), 'MAXFORANSWERED': 0},
                              'NUMFRUITANDVEG': {'POINTS': 0, 'MAXPOINTS': FruitAndVegServingsMapMax, 'MAXFORANSWERED': 0},
                              'NUMDRINKS': {'POINTS': 0, 'MAXPOINTS': EightOunceDrinksPoints.max(), 'MAXFORANSWERED': 0},
                              'NUMCAFDRINKS': {'POINTS': 0, 'MAXPOINTS': CaffeinatedDrinksPoints.max(), 'MAXFORANSWERED': 0},
                              'NUMWATERDRINKS': {'POINTS': 0, 'MAXPOINTS': WaterServingsPoints.max(), 'MAXFORANSWERED': 0},
                              'NUMALCDRINKS': {'POINTS': 0, 'MAXPOINTS': AlcoholicDrinksMalePoints.max(), 'MAXFORANSWERED': 0}}}

    numberOfFruitServings  = utilities.strToKey(answers['NumberFruitServings'])
    results = utilities.subpts(numberOfFruitServings, 'NUMFRUITSSERVS', FruitServingsPoints, results)

    numberOfVegServings = utilities.strToKey(answers['NumberVegetableServings'])
    results = utilities.subpts(numberOfVegServings, 'NUMVEGSERVS', VegetableServingsPoints, results)

    # special case
    if numberOfFruitServings is not None and numberOfVegServings is not None:
        results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['NUMFRUITANDVEG']['MAXPOINTS']
        results['COMPONENTS']['NUMFRUITANDVEG']['MAXFORANSWERED'] = results['COMPONENTS']['NUMFRUITANDVEG']['MAXPOINTS']
        results['MAXFORANSWERED'] = results['MAXFORANSWERED'] + results['COMPONENTS']['NUMFRUITANDVEG']['MAXFORANSWERED']
        results['COMPONENTS']['NUMFRUITANDVEG']['POINTS'] = FruitAndVegServingsMap[numberOfFruitServings][numberOfVegServings]
        logging.debug("score increased by total of %d for %s", results['COMPONENTS']['NUMFRUITANDVEG']['POINTS'], 'NUMFRUITANDVEG')
        results['POINTS'] = results['POINTS'] + results['COMPONENTS']['NUMFRUITANDVEG']['POINTS']

    numberOfEightOunceDrinks = utilities.strToKey(answers['NumberDrinks'])
    results = utilities.subpts(numberOfEightOunceDrinks, 'NUMDRINKS', EightOunceDrinksPoints, results)

    numberOfWaterServings = utilities.strToKey(answers['NumberWaterDrinks'])
    results = utilities.subpts(numberOfWaterServings, 'NUMWATERDRINKS', WaterServingsPoints, results)

    numberOfCaffeinatedDrinks = utilities.strToKey(answers['NumberCaffeinatedDrinks'])
    results = utilities.subpts(numberOfCaffeinatedDrinks, 'NUMCAFDRINKS', CaffeinatedDrinksPoints, results)

    numberOfAlcoholicDrinks = utilities.strToKey(answers['NumberAlcoholicDrinks'])
    isMale = utilities.isMale(answers['Gender'])
    if isMale is not None:
        if isMale:
            results = utilities.subpts(numberOfAlcoholicDrinks, 'NUMALCDRINKS', AlcoholicDrinksMalePoints, results)
        else:
            results['COMPONENTS']['NUMFRUITANDVEG']['MAXPOINTS'] = AlcoholicDrinksFemalePoints.max()
            results = utilities.subpts(numberOfAlcoholicDrinks, 'NUMALCDRINKS', AlcoholicDrinksFemalePoints, results)
    else:
        results = utilities.subpts(numberOfAlcoholicDrinks, 'NUMALCDRINKS', AlcoholicDrinksMalePoints, results)

    return results
