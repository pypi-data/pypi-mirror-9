import sys
import json
import types
import time
import requests
import logging
import platform
import webbrowser

try:
    import pandas
    HAS_PANDAS = True
    pandas.set_option('display.notebook_repr_html', True)
    pandas.set_option('display.max_columns', 300)
except ImportError:
    HAS_PANDAS = False

logger = logging.getLogger('elsen-python')
logger.setLevel(logging.WARNING)

#------------------------------------------------------------------------
# Types
#------------------------------------------------------------------------

# Actions
BUY = 'BUY'
SELL = 'SELL'

# Indicators
RSI = 'rsi'
SMA = 'sma'
EMA = 'ema'
MACD = 'macd'
BOLLINGERBAND = 'bollingerband'
TRAILING = 'trailing'
CROSS = 'cross'

# Full Exchanges
NYSE    = "NYSE"
NASDAQ  = "NASDAQ"
AMEX    = "AMEX"
SP900   = "SP900"

# Response codes
errnos = {
    -2: ('ERROR_QUEUED', 'Job has been queued'),
    -1: ('ERROR_PROCESSING', 'Job currently being processed'),
     0: ('ERROR_OK', 'Job finished with no errors'),
     1: ('ERROR_LONG', 'Job too large for resources'),
     2: ('ERROR_PARSE', 'Error parsing job details'),
     3: ('ERROR_NO_DATA', 'No data found'),
     4: ('ERROR_ALLOCATION_FAILED', 'Memory allocation error'),
     5: ('ERROR_SIMULATION', 'Simulation error'),
     6: ('ERROR_STATS', 'Error calculating job statistics'),
     7: ('ERROR_NO_ORDERS', 'No orders closed'),
     8: ('ERROR_DELETED', 'Strategy marked as deleted'),
     9: ('ERROR_FILTER_DNE', 'Filter does not exist'),
    10: ('ERROR_INDICATOR_DNE', 'Indicator does not exist'),
    13: ('ERROR_BACKTEST_FAILED', 'System failure. Someone at Elsen will contact you'),
}

#------------------------------------------------------------------------
# API
#------------------------------------------------------------------------

class Elsen(object):

    """
    Elsen API

    Example:

        >>> auth_token = "your auth token"
        >>> elsen = Elsen(access_token=auth_token)
    """

    def __init__(self, url=None, verify=True):
        self.token = None
        self.url = url or "https://api.elsen.co/v1/"
        self.verify = verify

    def docs(self):
        """
        Open the Elsen API documentation in the browser.
        """
        webbrowser.open_new_tab("https://api.elsen.co/docs")

    def _get(self, endpoint, item=None, request=None, token=True):
        item = item or ''
        request = request or {}

        if token:
            req = dict(request.items() + {'token': self.token}.items())
            response = requests.get(self.url + endpoint + '/' + item,
                                    params=req, verify=self.verify)
        else:
            response = requests.get(self.url + endpoint + '/' + item,
                                    params=request, verify=self.verify)

        if response.status_code != 200:
            raise JavascriptException("Server exception: " + response.text)
        else:
            return response.json()

    def add_application(self, email, app_id):
        """
        Create an application.
        """

        request = {
            'email': email,
            'title': app_id
        }
        response = requests.put(self.url + "apps", params=request,
                                verify=self.verify)

        logging.debug(json.dumps(request, indent=4))

        if response.status_code != 201:
            raise JavascriptException("Server exception: " + response.text)
        else:
            return response.json()

    def get_appliations(self, app_id):
        """
        Get list of available applications
        """
        assert isinstance(app_id, str)
        response = requests.put(
            self.url + "apps/" + app_id, verify=self.verify)

        if response.status_code != 200:
            raise JavascriptException("Server exception: " + response.text)
        else:
            return response.json()

    def get_exchanges(self):
        """
        Get list of available exchanges
        """
        response =  self._get('exchanges', item=None, request={})
        return response['exchanges']

    def get_indices(self):
        """
        Get list of available indices
        """
        response = self._get('indices', item=None, request={})
        return response['indices']

    def get_benchmarks(self):
        """
        Get list of available benchmarks
        """
        return self._get('benchmarks', item=None, request={})

    def add_user(self, app_id, username, password, first_name=None, last_name=None, email=None):
        """
        Add a user profile (login, password) to a given application.
        """
        assert isinstance(app_id, str)
        assert isinstance(username, str)
        assert isinstance(password, str)
        request = {
            'app_id': app_id,
            'username': username,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        }
        response = requests.put(self.url + "users", params=request)

        if response.status_code != 201:
            raise JavascriptException("Server exception: " + response.text)
        else:
            return response.json()['id']

    def authenticate(self, app_id, username, password, first_name=None, last_name=None, email=None):
        """
        Authenticate a user and associated application.

        Example:

            >>> elsen.authenticate(
            >>>     app_id     = 'your application id',
            >>>     username   = 'your username',
            >>>     password   = 'your password')

        """
        assert isinstance(app_id, str)
        assert isinstance(username, str)
        assert isinstance(password, str)
        auth = {
            'app_id': app_id,
            'username': username,
            'password': password
        }
        response = requests.get(self.url + "access", params=auth,
                                verify=self.verify)

        if response.status_code != 200:
            raise JavascriptException("Server exception: " + response.text)

        try:
            self.token = response.json()['token']
        except AttributeError, ValueError:
            raise JavascriptException("Could not authenticate: " +
                    response.text)

    def search_filters(self, phrase):
        """
        Search for a filter by phrase in text description

        >>> elsen.search_filters('oil')

        """
        assert isinstance(phrase, str)
        results = []
        for flt in self.get_filters():
            if phrase.lower() in (flt.name + " " + flt.short_desc.lower()):
                results += [flt]
        return results

    def common_filters(self, n=25):
        assert isinstance(n, int)
        assert n >= 0
        return sorted(self.get_filters(), key=lambda x: x.count(),
                reverse=True)[0:n]

    def get_filters(self, filters=None):
        """
        Get list of available filters for use in strategies.

        Example:

            >>> elsen.get_filters('currentprice')
            >>> elsen.get_filters(['currentprice', 'avgvol30'])
        """

        if isinstance(filters, (list, types.NoneType)):
            request = {
                'token': self.token,
                'filters': ','.join(filters) if filters else None
            }
            response = requests.get(self.url + "filters", params=request,
                                    verify=self.verify)
            filters = response.json()['filters']
            return [FilterType(self, data) for data in filters]

        elif isinstance(filters, basestring):
            request = {
                'token': self.token,
                'filters': filters
            }
            response = requests.get(self.url + "filters", params=request,
                                    verify=self.verify)
            data = response.json()['filters']
            if len(data) == 1:
                return FilterType(self, data[0])
            else:
                return []

    def get_indicators(self, indicators=None):
        """
        Get list of available indicators for use in strategy creation

        Example:

            >>> elsen.get_indicators('rsi')
            >>> elsen.get_indicators(['rsi', 'sma'])
        """
        if isinstance(indicators, (list, types.NoneType)):
            request = {
                'token': self.token,
                'indicators': ','.join(indicators) if indicators else None
            }
            response = requests.get(self.url + "indicators", params=request,
                                    verify=self.verify)
            indicator_list = response.json()['indicators']
            return [IndicatorType(self, data, data['name']) for data in indicator_list]

        elif isinstance(indicators, basestring):
            request = {
                'token': self.token,
                'indicators': indicators
            }
            response = requests.get(self.url + "indicators", params=request,
                                    verify=self.verify)
            data = response.json()['indicators']
            if len(data) == 1:
                return IndicatorType(self, data[0], data[0]['name'])
            else:
                return []

    def setup_strategy(self, universe, indicators, filters, interval,
            periodsBetweenBuySell=None, priority=None, accountsize=None):
        """
        Setup a strategy.
        """
        strategy = {
            'token': self.token,
            'universe': universe,
            'indicators': json.dumps([indicator.json() for indicator in indicators]),
            'filters': json.dumps([filter.json() for filter in filters]),
        }

        if interval is not None:
            strategy['interval'] = interval

        if accountsize is not None:
            strategy['accountsize'] = accountsize

        if priority is not None:
            strategy['priority'] = accountsize

        if periodsBetweenBuySell is not None:
            strategy['periodsBetweenBuySell'] = periodsBetweenBuySell

        logger.debug(json.dumps(strategy, indent=4))

        response = requests.put(self.url + "strategies", params=strategy,
                                verify=self.verify)

        if response.status_code != 201:
            raise JavascriptException("Server exception: " + response.text)
        return Strategy(self, response.json())

    def setup_backtest(self, strategy, start, end, title=None, tags=None):
        """
        Setup a backtest.
        """
        assert isinstance(strategy, Strategy)
        backtest = {
            'token': self.token,
            'start': start,
            'end': end,
            'strategy': strategy.id,
            'title': title,
            'tags': ','.join(tags) if tags else None
        }
        logger.debug(json.dumps(backtest, indent=4))

        response = requests.put(self.url + "backtests", params=backtest,
                                verify=self.verify)
        assert response.status_code == 201
        # print json.dumps(backtest, indent=4)
        if response.status_code != 201:
            raise JavascriptException("Server exception: " + response.text)
        return Backtest(self, response.json())

    def detailsfor(self, backtestid):
        """
        Get the details for an existing backtest.

        >>> detailsfor('your backtest id')
        """
        bs = Backtest(self, data={'id': backtestid})
        return bs.details()

#------------------------------------------------------------------------
# Strategies
#------------------------------------------------------------------------

class Strategy(object):

    """
    Strategy object.
    """

    def __init__(self, parent, data):
        self._parent = parent
        self._data = data
        self.id = data['id']
        self.short = data['short']

    def __repr__(self):
        return "<<Strategy: " + self.short + ">>"


class Backtest(object):

    """
    Backtest object.
    """

    def __init__(self, parent, data):
        self._parent = parent
        self._data = data
        self.id = data['id']

        self._cache = None
        self._completed = False

    def details(self):
        # Cache the results
        if self._cache != None:
            return self._cache
        else:
            params = {'token': self._parent.token}
            response = requests.get(self._parent.url + "backtests/" + self.id,
                                    params=params, verify=self._parent.verify)
            assert response.status_code == 200
            details = response.json()
            if details['backtest']['error'] >= 0:
                self._cache = details
            return details

    def status_key(self):
        """
        Status Key
        """
        try:
            return self.details()['backtest']['status_key']
        except TypeError:
            return ''

    def error_code(self):
        """
        Error
        """
        try:
            return int(self.details()['backtest']['error'])
        except TypeError:
            return ''

    def alpha(self):
        """
        Alpha
        """
        try:
            return float(self.details()['backtest']['alpha'])
        except TypeError:
            return ''

    def beta(self):
        """
        Beta
        """
        try:
            return float(self.details()['backtest']['beta'])
        except TypeError:
            return ''

    def sharpe(self):
        """
        Sharpe ratio
        """
        try:
            return float(self.details()['backtest']['sharperatio'])
        except TypeError:
            return ''

    def drawdown(self):
        """
        Drawdown
        """
        try:
            return float(self.details()['backtest']['drawdown'])
        except TypeError:
            return ''

    def returns(self):
        """
        Return in dollars for backtest
        """
        return float(self.details()['backtest']['return'])

    def trades(self, trades=None):
        """
        Get all individuals trades that a backtest made.
        """

        request = {
            'token': self._parent.token,
        }
        response = self._parent._get("backtests", item=self.id + "/trades",
                                     request=request)
        return Trades(self._parent, response)

    def join(self, interval=5, block=True, timing=False, timeout=None):
        """
        Join on the backtest and yielding the results when the server responds
        with the finished results.

        interval
            Period in seconds to poll for backtest results.

        block
            Either block until backtest finished or return None if non-
            blocking.

        timing
            Print the total time for backtest.

        timeout
            Stop waiting after a set period of seconds.
        """
        logger.debug('Waiting on backtest: %s', self.id)

        time1 = time.time()
        while not self._completed:
            resp = self.details()
            errcode = resp['backtest']['error']

            delta = time.time() - time1
            if timeout and (delta > timeout):
                raise BacktestTimeout()

            if errcode < 0:
                if timing:
                    print 'Waiting for backtest to complete.'
                if block:
                    time.sleep(interval)
                else:
                    return None
            elif errcode == 0:
                time2 = time.time()
                diff = time2 - time1
                minutes, seconds = diff // 60, diff % 60
                self._completed = True
                if timing:
                    print 'Backtest took %s minutes %s seconds' % (minutes,
                                                                   seconds)

                logger.debug('Finished backtest: %s', self.id)
                logger.debug(
                    'Backtest details: %s', json.dumps(resp, indent=4))
                return resp
            else:
                raise BacktestError('Backtest failed with: %s' % (errnos[errcode],))

    def to_json(self, indent=4):
        """
        Convert a backtest results into JSON
        """
        return json.dumps(self.details(), indent=indent)

    def to_numpy(self):
        """
        Convert a backtest results into a numpy array.
        """
        raise NotImplementedError

    def to_dataframe(self):
        """
        Convert a backtest results into a dataframe object.
        """
        if HAS_PANDAS:
            vals = self.details()['backtest'].values()
            keys = self.details()['backtest'].keys()
            return pandas.DataFrame([vals], columns=keys)
        else:
            raise Exception("Requires the pandas library")

    def __repr__(self):
        return "<<Backtest: " + self.id + ">>"


class IndicatorType(object):

    """
    Abstract indicator
    """

    def __init__(self, parent, data, name):
        self._parent = parent
        self._data = data
        self.name = name
        self.display_name = data['display_name']
        if data['short_desc']:
            self.short_desc = data['short_desc'].encode('ascii', 'ignore')
        else:
            self.short_desc = 'No description.'

    def inputs(self):
        """
        Return the data inputs for the indicator.
        """
        return self._data['inputs']

    def __str__(self):
        return self.short_desc

    def __repr__(self):
        return "<<Indicator: " + self.name + ">>"


class FilterType(object):

    """
    Abstract filter

    >>> flt.name
    'currentprice'
    >>> flt.short_desc
    Real time price of a security or the most recent listed.
    >>> flt.count
    9414
    """

    def __init__(self, parent, data):
        self._parent = parent
        self._data = data
        self.name = data['name']
        if data['short_desc']:
            self.short_desc = data['short_desc'].encode('ascii', 'ignore')
        else:
            self.short_desc = ''
        self.sources = data['sources']

    def max(self):
        """
        Get the maximum possible value of a filter.
        """
        return float(self._data['maxvalue'])

    def min(self):
        """
        Get the maximum possible value of a filter.
        """
        return float(self._data['minvalue'])

    def mid(self):
        """
        Get the median range of the value of a filter.
        """
        return (self.max() - self.min())/2

    def count(self):
        """
        Get the number of symbols associated with this fundamental.
        """
        return self._data['distinctnames']

    def __str__(self):
        return self.short_desc

    def __repr__(self):
        return ("<<Filter: name=" + self.name + " "
                + "desc='" + str(self.short_desc) + "' "
                + "count=" + str(self.count()) + ">>")


class Indicator(object):

    """
    Indicator paramter to a strategy.

    >>> ind.name
    'rsi'
    >>> ind.inputs
    """

    def __init__(self, action, name, **inputs):
        assert (action is BUY) or (action is SELL)
        self.action = action
        self.name = name
        self.inputs = inputs

    def json(self):
        query = {
            'action': self.action,
            'name': self.name,
        }
        query.update(self.inputs)
        return query


class Filter(object):

    """
    Filter parameter to a strategy.

    There are four classes of filter setups:

    ranked range
        (name, rank_order [asc|desc], rank_type [numeric|percent], rank_min, rank_max)

    range
        has params (name, min, max)

    exact
        has params (name, exact)

    contains
        has params (name, contains)
    """

    def __init__(self, name, min=None, max=None,  rank_order=None,
            rank_min=None, rank_max=None, rank_type=None, contains=None, exact=None):
        self.name = name
        self.min = min
        self.max = max
        self.rank_min = rank_min
        self.rank_max = rank_max
        self.rank_order = rank_order
        self.rank_type = rank_type
        self.contains = contains
        self.exact = exact

    def json(self):
        query = {
            'name': self.name,
        }
        
        if self.min is not None:
        	query['min'] = self.min

        if self.max is not None:
        	query['max'] = self.max
        
        if self.rank_order:
            query['rank_order'] = self.rank_order

        if self.rank_type:
            query['rank_type'] = self.rank_type

        if self.rank_min is not None:
            query['rank_min'] = self.rank_min

        if self.rank_max is not None:
            query['rank_max'] = self.rank_max

        if self.contains:
            query['contains'] = self.contains

        if self.exact is not None:
            query['exact'] = self.exact

        return query


class Trades(object):

    """
    Backtest trades
    """

    def __init__(self, parent, data):
        self._parent = parent
        self._data = data

    def to_dataframe(self):
        """
        Convert a backtest trades into a dataframe object.
        """
        def action_mapper(series):
            if series['action'] == 1:
                return 'BUY'
            elif series['action'] == -1:
                return 'SELL'

        if HAS_PANDAS:
            df = pandas.DataFrame(self._data)
            df['action'] = df.apply(action_mapper, axis=1)
            return df
        else:
            raise Exception("Requires the pandas library")


#------------------------------------------------------------------------
# Utils
#------------------------------------------------------------------------

def symbol(indicator, exchange=NYSE):
    """
    Return the securiy symbol

    >>> symbol('AAPL')
    >>> symbol('AAPL', exchange=NYSE)
    """
    assert isinstance(indicator, str)
    return exchange + indicator

def sid(ident):
    """
    Lookup security object by security id
    """
    raise NotImplementedError

def join_all(backtests, timing=False, default=None):

    """
    Wait for a list of backtests to all complete before yielding their results.
    """
    time1 = time.time()
    assert isinstance(backtests, list)
    pending = list(enumerate(backtests))
    finished = []
    try:
        # print 'Waiting for backtests to complete.'
        while len(pending) > 0:
            (ix, btest) = pending.pop(0)
            if btest.join(block=False) is not None:
                print 'Finished backtest: ', ix
                finished.append((ix, btest))
            else:
                # print 'Still waiting on Backtest: %i' % ix
                pending.append((ix, btest))
            time.sleep(0.2)
    except (KeyboardInterrupt, SystemExit):
        pending.append((ix, btest))
        for (ix, btest) in pending:
            print 'Backtest never finished: (%i, %s)', (ix, btest.id)
    finally:
        time2 = time.time()
        diff = time2 - time1
        minutes, seconds = diff // 60, diff % 60
        if timing:
            print 'Backtest took %s minutes %s seconds' % (minutes, seconds)
        return finished



#------------------------------------------------------------------------
# Exceptions
#------------------------------------------------------------------------

class BacktestTimeout(Exception):

    def __init__(self):
        pass

    def __str__(self):
        return 'Backtest Timeout'


class BacktestError(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class JavascriptException(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


#------------------------------------------------------------------------
# Support
#------------------------------------------------------------------------

def enable_debugging():
    import _version

    LOG_FILENAME = 'elsen-python.log'

    handler = logging.FileHandler(LOG_FILENAME)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(levelname)s] %(asctime)s   %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger('elsen-python')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    platform_info()
    logger.debug('Elsen-Python Version: %s', _version.get_versions())

def linux_distribution():
  try:
    return platform.linux_distribution()
  except:
    return "N/A"

def platform_info():
    logger.debug("""Python version: %s
    dist: %s
    linux_distribution: %s
    system: %s
    machine: %s
    platform: %s
    uname: %s
    version: %s
    mac_ver: %s
    """ % (
    sys.version.split('\n'),
    str(platform.dist()),
    linux_distribution(),
    platform.system(),
    platform.machine(),
    platform.platform(),
    platform.uname(),
    platform.version(),
    platform.mac_ver(),
    ))
