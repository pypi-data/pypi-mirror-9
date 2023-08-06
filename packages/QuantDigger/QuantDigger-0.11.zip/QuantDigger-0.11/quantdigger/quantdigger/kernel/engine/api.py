from abc import ABCMeta, abstractmethod
#from quantdigger.kernel.datastruct import Contract

class Trader(object):

    __metaclass__ = ABCMeta

    """docstring for Trader"""
    def __init__(self, arg):
        pass

    @abstractmethod
    def connect(self):
        """docstring for """ 
        pass

    @abstractmethod
    def register_handlers(self, handlers):
        """docstring for """ 
        pass

    def query_instrument(self, contract, cbk=None, syn=False):
        """ 合约查询 """ 
        self._query_instrument(contract)

    def query_depth_marketdata(self, contract, cbk=None, syn=False):
        """ 深度行情数据 """ 
        self._query_depth_marketdata(contract)

    def query_trading_account(self, cbk=None, syn=False):
        """ 查询资金账户 """ 
        self._query_trading_account()

    def query_position(self, cbk=None, syn=False):
        """ 查询投资者持仓""" 
        self._query_position()

    def insert_order(self, order, cbk=None, syn=False):
        """ 下单请求    
        
        Args:
            order (Order): 订单。
        """
        self._insert_order(order)

    def cancel_order(self, contract_id, cbk=None, syn=False):
        """ 撤单操作请求 """ 
        self._cancel_order(contract_id)

    @abstractmethod
    def _query_instrument(self, contract):
        """ 合约查询 """ 
        pass

    @abstractmethod
    def _query_depth_marketdata(self, contract):
        """ 深度行情数据 """ 
        pass

    @abstractmethod
    def _query_trading_account(self):
        """ 查询资金账户 """ 
        pass

    @abstractmethod
    def _query_position(self):
        """ 查询投资者持仓""" 
        pass

    @abstractmethod
    def _insert_order(self, order):
        """ 下单请求    
        
        Args:
            order (Order): 订单。
        """
        pass

    @abstractmethod
    def _cancel_order(self, contract_id):
        """ 撤单操作请求 """ 
        pass
    
    
class CtpTraderAPI(object):
    """docstring for CtpTrader"""
    def __init__(self):
        pass

    def connect(self):
        """docstring for connect""" 
        pass

    def query_instrument(self, contract):
        """ 合约查询 """ 
        pass

    def query_depth_marketdata(self, contract):
        """ 深度行情数据 """ 
        pass

    def query_trading_account(self):
        """ 查询资金账户 """ 
        pass

    def query_position(self):
        """ 查询投资者持仓""" 
        pass

    def insert_order(self, contract_id, direction, buy_or_sell, price, volume):
        """ 下单请求    
        
        Args:
            contract_id (int): 合约编号
            direction (str): 交易方向
            buy_or_sell (str): 开平仓标志
            price (float): 价格
            volume (int): 成交量
        
        Returns:
            int. The result
        Raises:
        """
        pass

    def cancel_order(self, contract_id):
        """ 撤单操作请求 """ 
        pass

    #virtual void login(const char *broker_id, const char *user_id, const char *password, bool syn) = 0;
    #virtual void logout(const char *broker_id, const char *user_id, bool syn) = 0;
	#///投资者结算结果查询
    #virtual void qrySettlementInfo(const char *broker_id, 
                                   #const char *investor_id, 
                                   #const char* trading_day,
                                   #bool syn) = 0;
	#///投资者结算结果确认
	#virtual void settlementInfoConfirm(bool syn) = 0;

    #/// 注册前置地址
    #virtual void registerFront(char *pszFrontAddress, bool syn) = 0;

    

class SimulateTrader(Trader):
    """ 模拟交易下单接口 """
    def __init__(self):
        #self.exch = exchange
        pass

    def connect(self):
        """docstring for connect""" 
        pass

    def register_handlers(self, handlers):
        """docstring for register_handlers""" 
        pass

    def _query_instrument(self, contract):
        """ 合约查询 """ 
        pass

    def _query_depth_marketdata(self, contract):
        """ 深度行情数据 """ 
        pass

    def _query_trading_account(self):
        """ 查询资金账户 """ 
        pass

    def _query_position(self):
        """ 查询投资者持仓""" 
        pass

    def _insert_order(self, order):
        """ 下单请求    
        
        Args:
            order (Order): 订单。
        """

    def _cancel_order(self, contract_id):
        """ 撤单操作请求 """ 
        pass
