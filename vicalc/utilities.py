from typing import Dict, Tuple, Union
from datetime import datetime, date
import logging


class PointsRange(object):
    def __init__(self, rng: Tuple[Tuple[float, int], ...], default: int, inclusive: bool = True) -> None:
        self.range = rng
        self.default = default
        self._max: int = -1000
        self.inclusive = inclusive
        for val, pts in self.range:
            if pts > self._max:
                self._max = pts
        if self.default > self._max:
            self._max = self.default

    def max(self) -> int:
        return self._max

    def points(self, val: int) -> int:
        for lim, pts in self.range:
            if self.inclusive:
                if val <= lim:
                    return pts
            else:
                if val < lim:
                    return pts
        return self.default


class PointsMap(object):

    def __init__(self, points: Dict[Union[str, int], int]) -> None:
        self._points = points
        self._max: int = -1000
        for pts in self._points.values():
            if pts > self._max:
                self._max = pts

    def max(self) -> int:
        return self._max

    def points(self, val: str) -> int:
        # let this throw KeyError if no mapping
        return self._points[val]


# answer handlers
def yesNoToBool(ans: str) -> Union[bool, None]:
    if ans:
        if ans in ('Yes', 'yes'):
            return True
        elif ans in ('No', 'no'):
            return False
    return None


def strToBool(ans: str) -> Union[bool, None]:
    if ans:
        if ans in ('1', 'Yes', 'yes', 'True', 'true'):
            return True
        elif ans in ('0', 'No', 'no', 'False', 'false'):
            return False
    return None


def strToInt(ans: str) -> Union[int, None]:
    if ans:
        return int(ans)
    return None


def strToDate(ans: str) -> Union[date, None]:
    if ans:
        return datetime.strptime(ans, "%Y-%m-%d").date()
    return None


def strToDatetime(ans: str) -> Union[datetime, None]:
    import datetime
    if ans:
        d = datetime.datetime.strptime(ans, "%Y-%m-%d-%H-%M-%S")
        # assumed to be in UTC
        return d
    return None


def strToIndex(ans: str) -> Union[int, None]:
    if ans:
        return int(ans)
    return None


def strToKey(ans: str) -> Union[str, None]:
    if ans:
        return ans
    return None


# birth date handlers
def ageFromBirthDate(born: date) -> int:
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def isMale(gender: str) -> Union[bool, None]:
    if gender:
        return gender in ('Male', 'male')
    return None


ValType = Union[int, float, str, None]
ResultsType = Dict[str, Union[int, Dict[str, Dict[str, int]]]]
MapType = Union[PointsRange, PointsMap]


def subpts(val: ValType, name: str, ptscls: MapType, results: ResultsType) -> ResultsType:
    pts:int  = 0
    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS'][name]['MAXPOINTS']
    if val is not None:
        results['COMPONENTS'][name]['MAXFORANSWERED'] = results['COMPONENTS'][name]['MAXPOINTS']
        results['MAXFORANSWERED'] = results['MAXFORANSWERED'] + results['COMPONENTS'][name]['MAXFORANSWERED']
        try:
            pts = ptscls.points(val)
        except (KeyError, IndexError) as error:
            # val not legal index to points
            # log warning but continue execution
            # no points assigned
            logging.error("Illegal value %s input for %s" % (str(val), name))
        else:
            results['COMPONENTS'][name]['POINTS'] = pts
            logging.debug("score increased by total of %d for %s", results['COMPONENTS'][name]['POINTS'], name)
            results['POINTS'] = results['POINTS'] + results['COMPONENTS'][name]['POINTS']

    return results


def subptscond(val: ValType, cond: bool, name: str, ptscls: MapType, results: ResultsType) -> ResultsType:
    pts: int = 0
    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS'][name]['MAXPOINTS']
    if cond:
        results['COMPONENTS'][name]['MAXFORANSWERED'] = results['COMPONENTS'][name]['MAXPOINTS']
        results['MAXFORANSWERED'] = results['MAXFORANSWERED'] + results['COMPONENTS'][name]['MAXFORANSWERED']
        try:
            pts = ptscls.points(val)
        except (KeyError, IndexError) as error:
            logging.error("Illegal value %s input for %s" % (str(val), name))
        else:
            results['COMPONENTS'][name]['POINTS'] = pts
            logging.debug("score increased by total of %d for %s", results['COMPONENTS'][name]['POINTS'], name)
            results['POINTS'] = results['POINTS'] + results['COMPONENTS'][name]['POINTS']
    return results


def subptsanswered(val: ValType, name: str, ptscls: MapType, results: ResultsType) -> ResultsType:
    pts: int = 0
    results['COMPONENTS'][name]['MAXFORANSWERED'] = results['COMPONENTS'][name]['MAXPOINTS']
    results['MAXFORANSWERED'] = results['MAXFORANSWERED'] + results['COMPONENTS'][name]['MAXFORANSWERED']
    try:
        pts = ptscls.points(val)
    except (KeyError, IndexError) as error:
        logging.error("Illegal value %s input for %s" % (str(val), name))
    else:
        results['COMPONENTS'][name]['POINTS'] = ptscls.points(val)
        logging.debug("score increased by total of %d for %s", results['COMPONENTS'][name]['POINTS'], name)
        results['POINTS'] = results['POINTS'] + results['COMPONENTS'][name]['POINTS']
    return results
