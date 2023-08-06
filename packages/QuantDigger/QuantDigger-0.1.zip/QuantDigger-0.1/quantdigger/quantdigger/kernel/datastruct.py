# -*- coding: utf8 -*-

#from flufl.enum import Enum
from quantdigger.errors import PeriodTypeError
from quantdigger import util

class Position(object):
    """docstring for Position"""
    def __init__(self, order, transaction):
        self.order = order
        self.transaction = transaction
        self.quantity = transaction.quantity

    @property
    def datetime(self):
        return self.transaction.datetime

    @property
    def price(self):
        """ 成交价格""" 
        return self.transaction.price

    @property
    def assure_ratio(self):
        """ 保证金比例 """ 
        return self.transaction.assure_ratio

    #def order_time(self):
        #return self.order.datetime

    #def order_price(self):
        #pass

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(util.time2int(self.datetime))
            return self._hash

    def __str__(self):
        rst = """
                Position:
                   datetime - %s
                   price - %f
                   quantity - %d
               """ % (str(self.datetime), self.price, self.quantity)
        return rst


class Bar(object):
    """docstring for Bar"""
    def __init__(self, dt, open, close, high, low, vol):
        self.datetime = dt
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = vol


class Transaction(object):
    """ 成交记录 """
    def __init__(self, order=None):
        if order:
            self.contract = order.contract
            self.direction = order.direction
            self.price = order.price
            self.quantity = order.quantity
            self.kpp = order.kpp
            self.datetime = order.datetime
            self.type = order.type
            self.id = order.id
        self.commission = 0
        self.assure_ratio = 1

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.id)
            return self._hash

    
class OrderID(object):
    """docstring for OrderID"""
    order_id = 0
    def __init__(self, id):
        self.id = id

    @classmethod
    def next_order_id(cls):
        """docstring for next_order_id""" 
        cls.order_id += 1
        return OrderID(cls.order_id)

    def __eq__(self, v):
        return self.id == v.id

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __ne__(self, other):
        return self.id != other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id
        

class Order(object):
    """ 订单 """
    def __init__(self, dt, contract, type_, kpp, direction, price, quantity):
        """     
        Args:
            dt (datetime): 下单日期和时间
            contract (Contract): 合约
            type_ (str): 下单方式，限价单('limit'), 市价单('market')
            kpp (str): 开仓('k'), 或平仓('p')
            direction (str): 多头('d'), 或空头('k')
            price (float): 价格
            amount (int): 数量
        
        Returns:
            int. The result
        Raises:
        """
        self.contract = contract
        self.direction = direction
        self.price = price
        self.quantity = quantity
        self.kpp = kpp
        self.datetime = dt
        self.type = type_
        self.id = OrderID.next_order_id()

    def print_order(self):
        #print "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % \
            #(self.symbol, self.order_type, self.quantity, self.direction)
        pass

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.id)
            return self._hash

    
class Contract(object):
    """ 合约 """
    def __init__(self, exch_type, code):
        self.exch_type = exch_type  # 用'stock'表示中国股市
        self.code = code

    def __str__(self):
        """""" 
        return "%s-%s" % (self.exch_type, self.code)

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.__str__())
            return self._hash


class Period(object):
    """ 周期 """
    #class Type(Enum):
        #MilliSeconds = "MilliSeconds" 
        #Seconds = "Seconds" 
        #Minutes = "Minutes" 
        #Hours = "Hours" 
        #Days = "Days" 
        #Months = "Months" 
        #Seasons = "Seasons" 
        #Years = "Years" 
    periods = ["MilliSeconds", "Seconds", "Minutes", "Hours",
               "Days", "Months", "Seasons", "Years"]    
    def __init__(self, type_, length):
        if type_ not in self.periods:
            raise PeriodTypeError
        self._type = type_
        self._length = length

    @property
    def type(self):
        return self._type

    @property
    def length(self):
        return self._length


    def __str__(self):
        return "%s-%d" % (self._type, self._length)

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.__str__())
            return self._hash


class PContract(object):
    def __init__(self, contract, period):
        self.contract = contract
        self.period = period

    def __str__(self):
        """ return string like 'SHEF-IF000-Minutes-10'  """
        return "%s-%s" % (self.contract, self.period)

    def __hash__(self):
        if hasattr(self, '_hash'):
            return self._hash
        else:
            self._hash =  hash(self.__str__())
            return self._hash
