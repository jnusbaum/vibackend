import logging
from . import utilities
from typing import Union, Dict, Tuple

"""Calculate the Psycho Social VI score

    An individual class instance is created for each individual set of base input data.

    Input Data:
    satisfaction with life
    energy level
    ability to handle everything needed
    optimism about the future
    sense of direction
    anxiety level
    needs being met
    meaningful relationships
    overall happiness
    overall stress level
    overall anxiety level
    overall satisfaction
    hours of sleep
    satisfaction of sleep
    satisfaction with love life
    satisfaction with sex life
    pet owner
    gratification from being pet owner
    satisfaction of time spent alone
    times meeting or speaking with friends
    total primary and secondary friends
    times meeting or speaking with non-close friends
    if have neighbor that can be relied on
    social satisfaction
    family life satisfaction
    work life balance satisfaction
    hours worked
    comparison of hours worked to desired
    gratification from work
    stress from work
    hours in car for work
    hours spent helping others
    gratification from helping others
    stress from helping others
    hours volunteering
    gratification from volunteering
    stress from volunteering
    hours spent in small group activities
    times spent in small group activities
    gratification from small group activities
    stress from small group activities
    hours spent in large group activities
    times spent in large group activities
    gratification from large group activities
    stress from large group activities
    combined small and large group activities
    combined hours of non-work activities
    average gratification from non-work activities
    average stress from non-work activities
    relationship status
"""

MaxPsychosocialPointsForThoseWithJobs: int = 365
MaxPsychosocialPointsForThoseWithoutJobs: int = 300

# 0,1-50,51-60,more than 60
HoursSpentWorkingJobPoints = utilities.PointsMap({'1': 0,
                                                  '2': 20,
                                                  '3': 15,
                                                  '4': 0})
# much less than I would like to work,a lot more than I would like to work
ComparisonOfHoursWorkedToDesiredPoints = utilities.PointsMap({'1': 0,
                                                              '2': 3,
                                                              '3': 5,
                                                              '4': 3,
                                                              '5': 0})
# No gratification at all, completely gratifying
GratificationFromWorkPoints = utilities.PointsMap({'1': 0,
                                                   '2': 0,
                                                   '3': 3,
                                                   '4': 3,
                                                   '5': 3,
                                                   '6': 10,
                                                   '7': 10,
                                                   '8': 10,
                                                   '9': 15,
                                                   '10': 15})
# no stress at all, very stressed out
StressFromWorkPoints = utilities.PointsMap({'1': 15,
                                            '2': 15,
                                            '3': 10,
                                            '4': 10,
                                            '5': 10,
                                            '6': 5,
                                            '7': 5,
                                            '8': 5,
                                            '9': 0,
                                            '10': 0})
# 0-5,6-10,11-15,more than 15
HoursSpentInCarForJobPoints = utilities.PointsMap({'1': 10,
                                                   '2': 5,
                                                   '3': 2,
                                                   '4': 0})
# Not at all difficult, Completely difficult
DifficultyPayingBillsPoints = utilities.PointsMap({'1': 10,
                                                   '2': 7,
                                                   '3': 5,
                                                   '4': 0,
                                                   '5': 0})
#
GratificationFromAllSocialEngagementPoints = utilities.PointsMap({1: 1,
                                                                  2: 3,
                                                                  3: 6,
                                                                  4: 9,
                                                                  5: 12,
                                                                  6: 14,
                                                                  7: 16,
                                                                  8: 18,
                                                                  9: 20,
                                                                  10: 20})
#
StressFromAllSocialEngagementPoints = utilities.PointsMap({1: 25,
                                                           2: 25,
                                                           3: 22,
                                                           4: 18,
                                                           5: 15,
                                                           6: 12,
                                                           7: 9,
                                                           8: 6,
                                                           9: 4,
                                                           10: 1})

CombinedSmallAndLargeGroupActivitiesPoints = utilities.PointsRange(((0, 0), (1, 5)), 10)
TotalHoursOfNonWorkActivitiesRange = utilities.PointsRange(((0, 0), (50, 15), (60, 10)), 5)

TimesMeetingOrSpeakingWithFriendPoints = utilities.PointsRange(((0, 0), (2, 5)), 10)
TotalPrimaryAndSecondaryFriendsPoints = utilities.PointsRange(((0, 0), (2, 5)), 10)
SocialSatisfactionRange = utilities.PointsRange(((2, 0), (5, 10), (8, 15)), 20)
PointsIncreaseForMeetingOrSpeakingWithNonCloseFriends = 5

CommunityCohesionVIPoints: int = 5

EmotionalEnrichmentRange = utilities.PointsRange(((2, 0), (5, 10), (8, 20)), 30)
# 0-3,4-6,7-10,more than 10
HoursOfSleepPoints = utilities.PointsMap({'1': 0,
                                          '2': 0,
                                          '3': 5,
                                          '4': 10,
                                          '5': 5})
# need much more than I get,get more than I really need
SatisfactionOfSleepPoints = utilities.PointsMap({'1': 0,
                                                 '2': 5,
                                                 '3': 10,
                                                 '4': 5,
                                                 '5': 0})
# almost never, all of the time
SatisfactionWithLifePoints = utilities.PointsMap({'1': 1,
                                                  '2': 2,
                                                  '3': 3,
                                                  '4': 4,
                                                  '5': 5,
                                                  '6': 6,
                                                  '7': 7,
                                                  '8': 8,
                                                  '9': 9,
                                                  '10': 10})
# almost never, all of the time
EnergyLevelPoints = utilities.PointsMap({'1': 1,
                                         '2': 2,
                                         '3': 3,
                                         '4': 4,
                                         '5': 5,
                                         '6': 6,
                                         '7': 7,
                                         '8': 8,
                                         '9': 9,
                                         '10': 10})
# almost never, all of the time
AbilityToHandleEverythingNeededPoints = utilities.PointsMap({'1': 1,
                                                             '2': 2,
                                                             '3': 3,
                                                             '4': 4,
                                                             '5': 5,
                                                             '6': 6,
                                                             '7': 7,
                                                             '8': 8,
                                                             '9': 9,
                                                             '10': 10})
# almost never, all of the time
OptimismAboutTheFuturePoints = utilities.PointsMap({'1': 1,
                                                    '2': 2,
                                                    '3': 3,
                                                    '4': 4,
                                                    '5': 5,
                                                    '6': 6,
                                                    '7': 7,
                                                    '8': 8,
                                                    '9': 9,
                                                    '10': 10})
# almost never, all of the time
SenseOfDirectionPoints = utilities.PointsMap({'1': 1,
                                              '2': 2,
                                              '3': 3,
                                              '4': 4,
                                              '5': 5,
                                              '6': 6,
                                              '7': 7,
                                              '8': 8,
                                              '9': 9,
                                              '10': 10})
# almost never, all of the time
anxietyLevelPoints = utilities.PointsMap({'1': 10,
                                          '2': 9,
                                          '3': 8,
                                          '4': 7,
                                          '5': 6,
                                          '6': 5,
                                          '7': 4,
                                          '8': 3,
                                          '9': 2,
                                          '10': 1})
# almost never, all of the time
NeedsBeingMetPoints = utilities.PointsMap({'1': 1,
                                           '2': 2,
                                           '3': 3,
                                           '4': 4,
                                           '5': 5,
                                           '6': 6,
                                           '7': 7,
                                           '8': 8,
                                           '9': 9,
                                           '10': 10})
# almost never, all of the time
MeaningfulRelationshipsPoints = utilities.PointsMap({'1': 1,
                                                     '2': 2,
                                                     '3': 3,
                                                     '4': 4,
                                                     '5': 5,
                                                     '6': 6,
                                                     '7': 7,
                                                     '8': 8,
                                                     '9': 9,
                                                     '10': 10})

# not happy at all, completely happy
OverallHappinessPoints = utilities.PointsMap({'1': 1,
                                              '2': 2,
                                              '3': 3,
                                              '4': 4,
                                              '5': 5,
                                              '6': 6,
                                              '7': 7,
                                              '8': 8,
                                              '9': 9,
                                              '10': 10})
# no stress at all, very stressed out
OverallStressLevelPoints = utilities.PointsMap({'1': 10,
                                                '2': 9,
                                                '3': 8,
                                                '4': 7,
                                                '5': 6,
                                                '6': 5,
                                                '7': 4,
                                                '8': 3,
                                                '9': 2,
                                                '10': 1})
# no anxiety at all, very anxious
OverallAnxietyLevelPoints = utilities.PointsMap({'1': 10,
                                                 '2': 9,
                                                 '3': 8,
                                                 '4': 7,
                                                 '5': 6,
                                                 '6': 5,
                                                 '7': 4,
                                                 '8': 3,
                                                 '9': 2,
                                                 '10': 1})
# not at all satisfied,completely satisfied
OverallSatisfactionPoints = utilities.PointsMap({'1': 1,
                                                 '2': 2,
                                                 '3': 3,
                                                 '4': 4,
                                                 '5': 5,
                                                 '6': 6,
                                                 '7': 7,
                                                 '8': 8,
                                                 '9': 9,
                                                 '10': 10})


def name() -> str:
    return 'SOCIAL'


def inputs() -> Tuple[str, ...]:
    return ('GoodAboutLife', 'EnergyLevel', 'HandleEverythingNeeded', 'OptimisticAboutFuture', 'SenseOfDirection',
            'AnxietyLevel',
            'NeedsBeingMet', 'MeaningfulRelationships', 'OverallHappiness', 'OverallStressLevel', 'OverallAnxietyLevel',
            'OverallLifeSatisfaction',
            'SleepTime', 'SatisfactionSleep', 'RelationshipSatisfaction', 'PhysicalSatisfaction', 'PetOwner',
            'GratificationPetOwner',
            'SatisfactionTimeAlone', 'InRelationship', 'TimesMeetingSpeakingFriends', 'TotalPrimarySecondaryFriends',
            'TimesMeetingSpeakingNonCloseFriends', 'HaveNeighborThatCanBeReliedOn', 'SocialSatisfaction',
            'FamilySatisfaction',
            'BalanceSatisfaction', 'HoursWorked', 'ComparisonHoursWorkedToDesired', 'GratificationFromWork',
            'StressFromWork', 'HoursInCarForWork',
            'DifficultyPayingBills', 'HoursHelpingFriendsFamily', 'GratificationHelpingFriendsFamily',
            'StressHelpingFriendsFamily',
            'HoursVolunteering', 'GratificationVolunteering', 'StressVolunteering', 'HoursSmallGroupActivities',
            'TimesSmallGroupActivities',
            'GratificationSmallGroupActivities', 'StressSmallGroupActivities', 'HoursLargeGroupActivities',
            'TimesLargeGroupActivities',
            'GratificationLargeGroupActivities', 'StressLargeGroupActivities')


def vi_points(answers: Dict[str, str]) -> Dict[str, Union[int, Dict[str, Dict[str, int]]]]:
    logging.debug("calculating score for %s" % name())

    results = {'POINTS': 0, 'MAXPOINTS': 0, 'MAXFORANSWERED': 0,
               'COMPONENTS': {'WORKCOMP': {'POINTS': 0, 'MAXPOINTS': ComparisonOfHoursWorkedToDesiredPoints.max(), 'MAXFORANSWERED': 0},
                              'WORKGRAT': {'POINTS': 0, 'MAXPOINTS': GratificationFromWorkPoints.max(), 'MAXFORANSWERED': 0},
                              'WORKCAR': {'POINTS': 0, 'MAXPOINTS': HoursSpentInCarForJobPoints.max(), 'MAXFORANSWERED': 0},
                              'WORKHOURS': {'POINTS': 0, 'MAXPOINTS': HoursSpentWorkingJobPoints.max(), 'MAXFORANSWERED': 0},
                              'WORKSTRESS': {'POINTS': 0, 'MAXPOINTS': StressFromWorkPoints.max(), 'MAXFORANSWERED': 0},
                              'GROUPEVENTS': {'POINTS': 0, 'MAXPOINTS': CombinedSmallAndLargeGroupActivitiesPoints.max(), 'MAXFORANSWERED': 0},
                              'NONWORKACTIVITIES': {'POINTS': 0, 'MAXPOINTS': TotalHoursOfNonWorkActivitiesRange.max(), 'MAXFORANSWERED': 0},
                              'NONWORKGRAT': {'POINTS': 0, 'MAXPOINTS': GratificationFromAllSocialEngagementPoints.max(), 'MAXFORANSWERED': 0},
                              'NONWORKSTRESS': {'POINTS': 0, 'MAXPOINTS': StressFromAllSocialEngagementPoints.max(), 'MAXFORANSWERED': 0},
                              'FINSTRESS': {'POINTS': 0, 'MAXPOINTS': DifficultyPayingBillsPoints.max(), 'MAXFORANSWERED': 0},
                              'PRINETWORK': {'POINTS': 0, 'MAXPOINTS': TimesMeetingOrSpeakingWithFriendPoints.max(), 'MAXFORANSWERED': 0},
                              'TOTALNETWORK': {'POINTS': 0, 'MAXPOINTS': TotalPrimaryAndSecondaryFriendsPoints.max(), 'MAXFORANSWERED': 0},
                              'COMMUNITYCOH': {'POINTS': 0, 'MAXPOINTS': CommunityCohesionVIPoints, 'MAXFORANSWERED': 0},
                              'COMMUNITYINTER': {'POINTS': 0, 'MAXPOINTS': PointsIncreaseForMeetingOrSpeakingWithNonCloseFriends, 'MAXFORANSWERED': 0},
                              'SOCIALSAT': {'POINTS': 0, 'MAXPOINTS': SocialSatisfactionRange.max(), 'MAXFORANSWERED': 0},
                              'EMOTIONALENRICH': {'POINTS': 0, 'MAXPOINTS': EmotionalEnrichmentRange.max(), 'MAXFORANSWERED': 0},
                              'SLEEPHOURS': {'POINTS': 0, 'MAXPOINTS': HoursOfSleepPoints.max(), 'MAXFORANSWERED': 0},
                              'SLEEPSAT': {'POINTS': 0, 'MAXPOINTS': SatisfactionOfSleepPoints.max(), 'MAXFORANSWERED': 0},
                              'LIFESAT': {'POINTS': 0, 'MAXPOINTS': SatisfactionWithLifePoints.max(), 'MAXFORANSWERED': 0},
                              'ENERGYLVL': {'POINTS': 0, 'MAXPOINTS': EnergyLevelPoints.max(), 'MAXFORANSWERED': 0},
                              'LIFECONTROL': {'POINTS': 0, 'MAXPOINTS': AbilityToHandleEverythingNeededPoints.max(), 'MAXFORANSWERED': 0},
                              'OPTIMISM': {'POINTS': 0, 'MAXPOINTS': OptimismAboutTheFuturePoints.max(), 'MAXFORANSWERED': 0},
                              'DIRECTION': {'POINTS': 0, 'MAXPOINTS': SenseOfDirectionPoints.max(), 'MAXFORANSWERED': 0},
                              'ANXIETYLVL': {'POINTS': 0, 'MAXPOINTS': anxietyLevelPoints.max(), 'MAXFORANSWERED': 0},
                              'NEEDSMET': {'POINTS': 0, 'MAXPOINTS': NeedsBeingMetPoints.max(), 'MAXFORANSWERED': 0},
                              'RELATIONSHIPS': {'POINTS': 0, 'MAXPOINTS': MeaningfulRelationshipsPoints.max(), 'MAXFORANSWERED': 0},
                              'OVERALLHAPPY': {'POINTS': 0, 'MAXPOINTS': OverallHappinessPoints.max(), 'MAXFORANSWERED': 0},
                              'OVERALLSTRESS': {'POINTS': 0, 'MAXPOINTS': OverallStressLevelPoints.max(), 'MAXFORANSWERED': 0},
                              'OVERALLANXIETY': {'POINTS': 0, 'MAXPOINTS': OverallAnxietyLevelPoints.max(), 'MAXFORANSWERED': 0},
                              'OVERALLSAT': {'POINTS': 0, 'MAXPOINTS': OverallSatisfactionPoints.max(), 'MAXFORANSWERED': 0}}}

    # Work Engagement
    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['WORKHOURS']['MAXPOINTS']
    hoursWorked = utilities.strToKey(answers, 'HoursWorked')

    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['WORKCOMP']['MAXPOINTS']
    comparisonOfHoursWorkedToDesired = utilities.strToKey(answers, 'ComparisonHoursWorkedToDesired')

    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['WORKGRAT']['MAXPOINTS']
    gratificationFromWork = utilities.strToKey(answers, 'GratificationFromWork')

    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['WORKCAR']['MAXPOINTS']
    hoursInCarForWork = utilities.strToKey(answers, 'HoursInCarForWork')

    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['WORKSTRESS']['MAXPOINTS']
    stressFromWork = utilities.strToKey(answers, 'StressFromWork')

    if hoursWorked is not None:
        results = utilities.subptsanswered(hoursWorked, 'WORKHOURS', HoursSpentWorkingJobPoints, results)

        if hoursWorked in ('2', '3', '4'):
            if gratificationFromWork is not None:
                results = utilities.subptsanswered(gratificationFromWork, 'WORKGRAT', GratificationFromWorkPoints,
                                                   results)

            if hoursInCarForWork is not None:
                results = utilities.subptsanswered(hoursInCarForWork, 'WORKCAR', HoursSpentInCarForJobPoints, results)

            if stressFromWork is not None:
                results = utilities.subptsanswered(stressFromWork, 'WORKSTRESS', StressFromWorkPoints, results)

    if comparisonOfHoursWorkedToDesired is not None:
        results = utilities.subptsanswered(comparisonOfHoursWorkedToDesired, 'WORKCOMP',
                                           ComparisonOfHoursWorkedToDesiredPoints, results)

    # Non-work Engagement
    totalHoursSpentInNonWorkActivities = 0
    stressDenom = 0
    gratDenom = 0
    combinedGratificationScale = 0
    combinedStressScale = 0
    combinedSmallAndLargeGroupEvents = 0
    smallOrLargeGroupEventsAnswered = False
    hoursAnswered = False

    hoursSpentHelpingOthers = utilities.strToInt(answers, 'HoursHelpingFriendsFamily')
    if hoursSpentHelpingOthers is not None:
        totalHoursSpentInNonWorkActivities += hoursSpentHelpingOthers
        hoursAnswered = True
        if hoursSpentHelpingOthers > 0:
            # Include gratification and stress scales into average
            gratificationFromHelpingOthers = utilities.strToInt(answers, 'GratificationHelpingFriendsFamily')
            if gratificationFromHelpingOthers is not None:
                gratDenom += 1
                combinedGratificationScale += gratificationFromHelpingOthers

            stressFromHelpingOthers = utilities.strToInt(answers, 'StressHelpingFriendsFamily')
            if stressFromHelpingOthers is not None:
                stressDenom += 1
                combinedStressScale += stressFromHelpingOthers

    hoursVolunteering = utilities.strToInt(answers, 'HoursVolunteering')
    if hoursVolunteering is not None:
        totalHoursSpentInNonWorkActivities += hoursVolunteering
        hoursAnswered = True
        if hoursVolunteering > 0:
            # Include gratification and stress scales into average
            gratificationFromVolunteering = utilities.strToInt(answers, 'GratificationVolunteering')
            if gratificationFromVolunteering is not None:
                gratDenom += 1
                combinedGratificationScale += gratificationFromVolunteering

            stressFromVolunteering = utilities.strToInt(answers, 'StressVolunteering')
            if stressFromVolunteering is not None:
                stressDenom += 1
                combinedStressScale += stressFromVolunteering

    timesSpentInSmallGroupActivities = utilities.strToInt(answers, 'TimesSmallGroupActivities')
    if timesSpentInSmallGroupActivities is not None:
        smallOrLargeGroupEventsAnswered = True
        combinedSmallAndLargeGroupEvents += timesSpentInSmallGroupActivities
        if timesSpentInSmallGroupActivities > 0:
            # Include gratification and stress scales into average
            gratificationFromSmallGroupActivities = utilities.strToInt(answers, 'GratificationSmallGroupActivities')
            if gratificationFromSmallGroupActivities is not None:
                gratDenom += 1
                combinedGratificationScale += gratificationFromSmallGroupActivities

            stressFromSmallGroupActivities = utilities.strToInt(answers, 'StressSmallGroupActivities')
            if stressFromSmallGroupActivities is not None:
                stressDenom += 1
                combinedStressScale += stressFromSmallGroupActivities

            # include hours
            hoursSpentInSmallGroupActivities = utilities.strToInt(answers, 'HoursSmallGroupActivities')
            if hoursSpentInSmallGroupActivities is not None:
                totalHoursSpentInNonWorkActivities += hoursSpentInSmallGroupActivities
                hoursAnswered = True

    timesSpentInLargeGroupActivities = utilities.strToInt(answers, 'TimesLargeGroupActivities')
    if timesSpentInLargeGroupActivities is not None:
        smallOrLargeGroupEventsAnswered = True
        combinedSmallAndLargeGroupEvents += timesSpentInLargeGroupActivities
        if timesSpentInLargeGroupActivities > 0:
            # Include gratification and stress scales into average
            gratificationFromLargeGroupActivities = utilities.strToInt(answers, 'GratificationLargeGroupActivities')
            if gratificationFromLargeGroupActivities is not None:
                gratDenom += 1
                combinedGratificationScale += gratificationFromLargeGroupActivities

            stressFromLargeGroupActivities = utilities.strToInt(answers, 'StressLargeGroupActivities')
            if stressFromLargeGroupActivities is not None:
                stressDenom += 1
                combinedStressScale += stressFromLargeGroupActivities

            # include hours
            hoursSpentInLargeGroupActivities = utilities.strToInt(answers, 'HoursLargeGroupActivities')
            if hoursSpentInLargeGroupActivities is not None:
                totalHoursSpentInNonWorkActivities += hoursSpentInLargeGroupActivities
                hoursAnswered = True

    # Small and Large Group Events VI Subscore
    results = utilities.subptscond(combinedSmallAndLargeGroupEvents, smallOrLargeGroupEventsAnswered, 'GROUPEVENTS',
                                   CombinedSmallAndLargeGroupActivitiesPoints, results)

    # Total time spent in non-work activities VI Subscore
    results = utilities.subptscond(totalHoursSpentInNonWorkActivities, hoursAnswered, 'NONWORKACTIVITIES',
                                   TotalHoursOfNonWorkActivitiesRange, results)

    # Gratification from all non-work activities VI Subscore
    if gratDenom > 0:
        results = utilities.subpts(int(round(combinedGratificationScale / gratDenom)), 'NONWORKGRAT',
                                   GratificationFromAllSocialEngagementPoints, results)
    else:
        results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['NONWORKGRAT']['MAXPOINTS']

    # Stress from all non-work activities VI Subscore
    if stressDenom > 0:
        results = utilities.subpts(int(round(combinedStressScale / stressDenom)), 'NONWORKSTRESS',
                                   StressFromAllSocialEngagementPoints, results)
    else:
        results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['NONWORKSTRESS']['MAXPOINTS']

    # Financial
    difficultyPayingBills = utilities.strToKey(answers, 'DifficultyPayingBills')
    results = utilities.subpts(difficultyPayingBills, 'FINSTRESS', DifficultyPayingBillsPoints, results)

    # Social Network
    timesMeetingOrSpeakingWithFriend = utilities.strToInt(answers, 'TimesMeetingSpeakingFriends')
    results = utilities.subpts(timesMeetingOrSpeakingWithFriend, 'PRINETWORK', TimesMeetingOrSpeakingWithFriendPoints,
                               results)

    totalPrimaryAndSecondaryFriends = utilities.strToInt(answers, 'TotalPrimarySecondaryFriends')
    results = utilities.subpts(totalPrimaryAndSecondaryFriends, 'TOTALNETWORK', TotalPrimaryAndSecondaryFriendsPoints,
                               results)

    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['COMMUNITYCOH']['MAXPOINTS']
    haveNeighborThatCanBeReliedOn = utilities.strToBool(answers, 'HaveNeighborThatCanBeReliedOn')  # bool
    if haveNeighborThatCanBeReliedOn is not None:
        results['COMPONENTS']['COMMUNITYCOH']['MAXFORANSWERED'] = results['COMPONENTS']['COMMUNITYCOH']['MAXPOINTS']
        results['MAXFORANSWERED'] = results['MAXFORANSWERED'] + results['COMPONENTS']['COMMUNITYCOH']['MAXFORANSWERED']
        if haveNeighborThatCanBeReliedOn:
            results['COMPONENTS']['COMMUNITYCOH']['POINTS'] = results['COMPONENTS']['COMMUNITYCOH']['MAXPOINTS']
            logging.debug("score increased by %d for %s", results['COMPONENTS']['COMMUNITYCOH']['POINTS'],
                         'COMMUNITYCOH')
            results['POINTS'] = results['POINTS'] + results['COMPONENTS']['COMMUNITYCOH']['POINTS']

    logging.info('answer for non close friends - %s', answers['TimesMeetingSpeakingNonCloseFriends'])
    timesMeetingOrSpeakingWithNonCloseFriends = utilities.strToBool(answers, 'TimesMeetingSpeakingNonCloseFriends')
    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['COMMUNITYINTER']['MAXPOINTS']
    if timesMeetingOrSpeakingWithNonCloseFriends is not None:
        results['COMPONENTS']['COMMUNITYINTER']['MAXFORANSWERED'] = results['COMPONENTS']['COMMUNITYINTER']['MAXPOINTS']
        results['MAXFORANSWERED'] = results['MAXFORANSWERED'] + results['COMPONENTS']['COMMUNITYINTER']['MAXFORANSWERED']
        if timesMeetingOrSpeakingWithNonCloseFriends:
            results['COMPONENTS']['COMMUNITYINTER']['POINTS'] = PointsIncreaseForMeetingOrSpeakingWithNonCloseFriends
            logging.debug('score increased by %d for CommunityInteraction', results['COMPONENTS']['COMMUNITYINTER']['POINTS'])
            results['POINTS'] = results['POINTS'] + results['COMPONENTS']['COMMUNITYINTER']['POINTS']

    satisfactionTotal = 0
    satisfactionDenom = 0
    socialSatisfaction = utilities.strToInt(answers, 'SocialSatisfaction')
    if socialSatisfaction is not None:
        satisfactionTotal += socialSatisfaction
        satisfactionDenom += 1
    familyLifeSatisfaction = utilities.strToInt(answers, 'FamilySatisfaction')
    if familyLifeSatisfaction is not None:
        satisfactionTotal += familyLifeSatisfaction
        satisfactionDenom += 1
    workLifeBalanceSatisfaction = utilities.strToInt(answers, 'BalanceSatisfaction')
    if workLifeBalanceSatisfaction is not None:
        satisfactionTotal += workLifeBalanceSatisfaction
        satisfactionDenom += 1
    if satisfactionDenom > 0:
        results = utilities.subpts(satisfactionTotal / satisfactionDenom, 'SOCIALSAT', SocialSatisfactionRange, results)
    else:
        results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['SOCIALSAT']['MAXPOINTS']

    runningTotal = 0
    denominatorCount = 0
    emotionalAnswered = False

    # Emotionally Enriching Experiences
    inRelationShip = utilities.strToInt(answers, 'InRelationship')
    if inRelationShip is not None:
        emotionalAnswered = True
        if inRelationShip > 1:
            # Love life / relationship
            satisfactionWithLoveLife = utilities.strToInt(answers, 'RelationshipSatisfaction')
            if satisfactionWithLoveLife is not None:
                runningTotal += satisfactionWithLoveLife
                denominatorCount += 1

            # Sex life
            satisfactionWithSexLife = utilities.strToInt(answers, 'PhysicalSatisfaction')
            if satisfactionWithSexLife is not None:
                runningTotal += satisfactionWithSexLife
                denominatorCount += 1

    # Pet Owner
    petOwner = utilities.strToBool(answers, 'PetOwner')  # bool
    if petOwner is not None:
        emotionalAnswered = True
        if petOwner:
            gratificationFromBeingPetOwner = utilities.strToInt(answers, 'GratificationPetOwner')
            if gratificationFromBeingPetOwner is not None:
                runningTotal += gratificationFromBeingPetOwner
                denominatorCount += 1

    # Alone time
    satisfactionOfTimeSpentAlone = utilities.strToInt(answers, 'SatisfactionTimeAlone')
    if satisfactionOfTimeSpentAlone is not None:
        emotionalAnswered = True
        runningTotal += satisfactionOfTimeSpentAlone
        denominatorCount += 1
    if denominatorCount > 0:
        results = utilities.subptscond(runningTotal / denominatorCount, emotionalAnswered, 'EMOTIONALENRICH',
                                       EmotionalEnrichmentRange, results)
    else:
        results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS']['EMOTIONALENRICH']['MAXPOINTS']

    # Sleep
    hoursOfSleep = utilities.strToKey(answers, 'SleepTime')
    results = utilities.subpts(hoursOfSleep, 'SLEEPHOURS', HoursOfSleepPoints, results)

    satisfactionOfSleep = utilities.strToKey(answers, 'SatisfactionSleep')
    results = utilities.subpts(satisfactionOfSleep, 'SLEEPSAT', SatisfactionOfSleepPoints, results)

    # Quality Of Life
    satisfactionWithLife = utilities.strToKey(answers, 'GoodAboutLife')
    results = utilities.subpts(satisfactionWithLife, 'LIFESAT', SatisfactionWithLifePoints, results)

    energyLevel = utilities.strToKey(answers, 'EnergyLevel')
    results = utilities.subpts(energyLevel, 'ENERGYLVL', EnergyLevelPoints, results)

    abilityToHandleEverythingNeeded = utilities.strToKey(answers, 'HandleEverythingNeeded')
    results = utilities.subpts(abilityToHandleEverythingNeeded, 'LIFECONTROL', AbilityToHandleEverythingNeededPoints,
                               results)

    optimismAboutTheFuture = utilities.strToKey(answers, 'OptimisticAboutFuture')
    results = utilities.subpts(optimismAboutTheFuture, 'OPTIMISM', OptimismAboutTheFuturePoints, results)

    senseOfDirection = utilities.strToKey(answers, 'SenseOfDirection')
    results = utilities.subpts(senseOfDirection, 'DIRECTION', SenseOfDirectionPoints, results)

    anxietyLevel = utilities.strToKey(answers, 'AnxietyLevel')
    results = utilities.subpts(anxietyLevel, 'ANXIETYLVL', anxietyLevelPoints, results)

    needsBeingMet = utilities.strToKey(answers, 'NeedsBeingMet')
    results = utilities.subpts(needsBeingMet, 'NEEDSMET', NeedsBeingMetPoints, results)

    meaningfulRelationships = utilities.strToKey(answers, 'MeaningfulRelationships')
    results = utilities.subpts(meaningfulRelationships, 'RELATIONSHIPS', MeaningfulRelationshipsPoints, results)

    overallHappiness = utilities.strToKey(answers, 'OverallHappiness')
    results = utilities.subpts(overallHappiness, 'OVERALLHAPPY', OverallHappinessPoints, results)

    overallStressLevel = utilities.strToKey(answers, 'OverallStressLevel')
    results = utilities.subpts(overallStressLevel, 'OVERALLSTRESS', OverallStressLevelPoints, results)

    overallAnxietyLevel = utilities.strToKey(answers, 'OverallAnxietyLevel')
    results = utilities.subpts(overallAnxietyLevel, 'OVERALLANXIETY', OverallAnxietyLevelPoints, results)

    overallSatisfaction = utilities.strToKey(answers, 'OverallLifeSatisfaction')
    results = utilities.subpts(overallSatisfaction, 'OVERALLSAT', OverallSatisfactionPoints, results)

    # scale score
    if hoursWorked is not None and hoursWorked in ('2', '3', '4'):
        logging.debug("scaling score for working client")
        results['POINTS'] = round(
            (results['POINTS'] / MaxPsychosocialPointsForThoseWithJobs) * MaxPsychosocialPointsForThoseWithoutJobs)
    results['MAXFORANSWERED'] = round(
        (results['MAXFORANSWERED'] / MaxPsychosocialPointsForThoseWithJobs) * MaxPsychosocialPointsForThoseWithoutJobs)
    results['MAXPOINTS'] = round(
        (results['MAXPOINTS'] / MaxPsychosocialPointsForThoseWithJobs) * MaxPsychosocialPointsForThoseWithoutJobs)

    return results

