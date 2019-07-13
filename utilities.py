
class PointsRange(object):
    def __init__(self, rng, default, inclusive=True):
        self.range = rng
        self.default = default
        self._max = -1000
        self.inclusive = inclusive
        for val, pts in self.range:
            if pts > self._max:
                self._max = pts
        if self.default > self._max:
            self._max = self.default
            
    def max(self):
        return self._max
        
    def points(self, val):
        for lim, pts in self.range:
            if self.inclusive:
                if val <= lim:
                    return pts
            else:
                if val < lim:
                    return pts
        return self.default


class PointsIndex(object):
    def __init__(self, points, default):
        self._points = points
        self.default = default
        self._max = -1000
        for pts in self._points:
            if pts > self._max:
                self._max = pts
        if self.default > self._max:
            self._max = self.default
                
    def max(self):
        return self._max
        
    def points(self, val):
        val = val-1
        if val < len(self._points):
            return self._points[val]
        else:
            return self.default
                

class PointsMap(object):
    _max: int

    def __init__(self, points):
        self._points = points
        self._max = -1000
        for pts in self._points.values():
            if pts > self._max:
                self._max = pts
                
    def max(self):
        return self._max
        
    def points(self, val):
        # let this throw KeyError if no mapping
        return self._points[val]

# answer handlers
def yesNoToBool(ans):
    if ans:
        if ans in ('Yes', 'yes'):
            return True
        elif ans in ('No', 'no'):
            return False
    return None

def strToBool(ans):
    if ans:
        if ans in ('1', 'Yes', 'yes', 'True', 'true'):
            return True
        elif ans in ('0', 'No', 'no', 'False', 'false'):
            return False
    return None

def strToInt(ans):
    if ans:
        return int(ans)
    return None

def strToDate(ans):
    import datetime
    if ans:
        return datetime.datetime.strptime(ans, "%Y-%m-%d").date()
    return None

def strToDatetime(ans):
    import datetime
    if ans:
        d = datetime.datetime.strptime(ans, "%Y-%m-%d-%H-%M-%S")
        # assumed to be in UTC
        d.replace(tzinfo=datetime.timezone.utc)
        return d
    return None

def strToIndex(ans):
    if ans:
        return int(ans)
    return None

def strToKey(ans):
    if ans:
        return ans
    return None

# birth date handlers
def ageFromBirthDate(born):
    import datetime
    today = datetime.date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
def isMale(gender):
    if gender:
        return gender in ('Male', 'male')
    return None
    

def subpts(val, name, ptscls, results):
    import logging
    results['COMPONENTS'][name]['MAXPOINTS'] = ptscls.max()
    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS'][name]['MAXPOINTS']
    if val is not None:
        results['COMPONENTS'][name]['MAXFORANSWERED'] = results['COMPONENTS'][name]['MAXPOINTS']
        results['MAXFORANSWERED'] = results['MAXFORANSWERED'] + results['COMPONENTS'][name]['MAXFORANSWERED']
        results['COMPONENTS'][name]['POINTS'] = ptscls.points(val)
        logging.info("score increased by total of %d for %s", results['COMPONENTS'][name]['POINTS'], name)
        results['POINTS'] = results['POINTS'] + results['COMPONENTS'][name]['POINTS']
    return results

def subptscond(val, cond, name, ptscls, results):
    import logging
    results['COMPONENTS'][name]['MAXPOINTS'] = ptscls.max()
    results['MAXPOINTS'] = results['MAXPOINTS'] + results['COMPONENTS'][name]['MAXPOINTS']
    if cond:
        results['COMPONENTS'][name]['MAXFORANSWERED'] = results['COMPONENTS'][name]['MAXPOINTS']
        results['MAXFORANSWERED'] = results['MAXFORANSWERED'] + results['COMPONENTS'][name]['MAXFORANSWERED']
        results['COMPONENTS'][name]['POINTS'] = ptscls.points(val)
        logging.info("score increased by total of %d for %s", results['COMPONENTS'][name]['POINTS'], name)
        results['POINTS'] = results['POINTS'] + results['COMPONENTS'][name]['POINTS']
    return results

def subptsanswered(val, name, ptscls, results):
    import logging
    results['COMPONENTS'][name]['MAXFORANSWERED'] = results['COMPONENTS'][name]['MAXPOINTS']
    results['MAXFORANSWERED'] = results['MAXFORANSWERED'] + results['COMPONENTS'][name]['MAXFORANSWERED']
    results['COMPONENTS'][name]['POINTS'] = ptscls.points(val)
    logging.info("score increased by total of %d for %s", results['COMPONENTS'][name]['POINTS'], name)
    results['POINTS'] = results['POINTS'] + results['COMPONENTS'][name]['POINTS']
    return results

