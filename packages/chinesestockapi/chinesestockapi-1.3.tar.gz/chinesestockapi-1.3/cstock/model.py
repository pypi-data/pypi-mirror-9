
class ParserException(Exception):
    pass


class Stock(object):
    
    # yesterday_close is yesterday close price
    # close is today close price

    # volume: unit of stock transacted
    # turnover: total transaction money

    __slots__ = [
        'name',
        'code',
        'date',
        'time',
        'price',
        'open',
        'close',
        'high',
        'low',
        'volume',
        'turnover',
        'yesterday_close',
    ]

    def __init__(self, **argvs):
        
        for (k, v) in argvs.items():
            setattr(self, k, v)

    def as_dict(self):
        result = {
            i: getattr(self, i, None)
            for i in self.__slots__
        }

        # dispose date and time because they are datetime class instance
        if result['date'] is not None:
            result['date'] = str(result['date'])

        if result['time'] is not None:
            result['time'] = str(result['time'])

        return result


__all__ = ['ParserException', 'Stock']
