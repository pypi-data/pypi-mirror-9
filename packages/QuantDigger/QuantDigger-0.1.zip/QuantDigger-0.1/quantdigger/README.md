
QuantDigger
=======
QuantDigger��һ����Դ�Ĺ�Ʊ/�ڻ��ز��ܡ�

��װ
=======
 * ���鰲װ[Anaconda](http://continuum.io/downloads), ��������һ���Ը㶨������������
 * ����PYTHONPATH����������


������
=======
�����⣺
* Python 
* pandas 
* python-dateutil 
* matplotlib 
* numpy
* TA-Lib
* pyqt (��ѡ)
* tushare (��ѡ)

����DEMO
=======
~~~~{.python}
from quantdigger.kernel.engine.execute_unit import ExecuteUnit
from quantdigger.kernel.indicators.common import MA, BOLL
from quantdigger.kernel.engine.strategy import TradingStrategy, pcontract, stock
import plotting


class DemoStrategy(TradingStrategy):
    """ ������ """
    def __init__(self, pcontracts, exe):
        """ ��ʼ��ָ����� """
        super(DemoStrategy, self).__init__(pcontracts, exe)

        self.ma20 = MA(self, self.close, 20,'ma20', 'b', '1')
        self.ma10 = MA(self, self.close, 10,'ma10', 'y', '1')
        self.b_upper, self.b_middler, self.b_lower = BOLL(self, self.close, 10,'boll10', 'y', '1')
        #self.ma2 = NumberSeries(self)

    def on_tick(self):
        """ ���Ժ�������ÿ��Bar����һ�Ρ�""" 
        #self.ma2.update(average(self.open, 10))
        if self.ma10[1] < self.ma20[1] and self.ma10 > self.ma20:
            self.buy('d', self.open, 1) 
        elif self.position() > 0 and self.ma10[1] > self.ma20[1] and self.ma10 < self.ma20:
            self.sell('d', self.open, 1) 

        print self.position(), self.cash()
        print self.datetime, self.b_upper, self.b_middler, self.b_lower


# ���в���
begin_dt, end_dt = None, None
pcon = pcontract('SHFE', 'IF000', 'Minutes', 10)
#pcon = stock('600848')  ����tushareԶ�̼��ع�Ʊ����
simulator = ExecuteUnit(begin_dt, end_dt)
algo = DemoStrategy([pcon], simulator)
simulator.run()

# ��ʾ�ز���
plotting.plot_result(simulator.data[pcon],
            algo._indicators,
            algo.blotter.deal_positions,
            algo.blotter)
~~~~
���н��
=======
* main.py ���Իز����ź��ߺ��ʽ����ߡ�
  https://github.com/QuantFans/quantdigger/blob/master/figure_signal.png
  https://github.com/QuantFans/quantdigger/blob/master/figure_money.png
* mplot_demo.py  matplotlib��k�ߣ�ָ���ߵ�demo��
  https://github.com/QuantFans/quantdigger/blob/master/plot.png
* pyquant.py ����pyqt�� ������ipython��matplotlib��demo��
  https://github.com/QuantFans/quantdigger/blob/master/pyquant.png
