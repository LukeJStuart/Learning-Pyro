import random
import time
import Pyro4


@Pyro4.expose
class StockMarket(object):
    def __init__(self, marketname, symbols):
        self._name = marketname
        self._symbols = symbols

    def quotes(self):
        while True:
            symbol = random.choice(self.symbols)
            yield symbol, round(random.uniform(5, 150), 2)
            time.sleep(random.random()/2.0)

    @property
    def name(self):
        return self._name

    @property
    def symbols(self):
        return self._symbols


if (__name__ == '__main__'):
    nasdaq = StockMarket("NASDAQ", ["AAPL", "CSCO", "MSFT", "GOOG"])
    newyork = StockMarket("NYSE", ["IBM", "HPQ", "BP"])
    # Notice that to ensure tidy cleanup of connection resources, the daemon
    # and the name server are both used as context managers in a with
    # statement.
    with Pyro4.Daemon() as daemon:
        nasdaq_uri = daemon.register(nasdaq)
        newyork_uri = daemon.register(newyork)
        with Pyro4.locateNS() as ns:
            ns.register('example.stockmarket.nasdaq', nasdaq_uri)
            ns.register('example.stockmarket.newyork', newyork_uri)
        print('Stockmarkets available.')
        daemon.requestLoop()
