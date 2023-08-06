import re
import json
import datetime

from cstock.base_engine import Engine
from cstock.model import Stock, ParserException

class YahooEngine(Engine):
    """
    Yahoo Engine transform stock id & parse data

    Example to get a csv file

    http://ichart.yahoo.com/table.csv?s=002475.sz&d=7&e=23&f=2014&a=6&b=23&c=2014
    """

    __slots__ = ['_url']

    DEFAULT_BASE_URL = "http://api.money.126.net/data/feed/%s,money.api"
