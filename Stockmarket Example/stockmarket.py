import random
import time
import Pyro4
import Pyro4.naming
import Pyro4.core
import os

# Setting necessary thing/s to make multiplexing work
Pyro4.config.SERVERTYPE = 'multiplex'
Pyro4.config.POLLTIMEOUT = 3


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


def existsNS():
    try:
        Pyro4.locateNS()
    except Pyro4.errors.NamingError:
        print('Pyro name server not found, stating a new one')
        nameserverUri, nameserverDaemon, broadcastServer = \
            Pyro4.naming.startNS()
        return nameserverDaemon
    return None


if (__name__ == '__main__'):
    nasdaq = StockMarket("NASDAQ", ["AAPL", "CSCO", "MSFT", "GOOG"])
    newyork = StockMarket("NYSE", ["IBM", "HPQ", "BP"])
    # Notice that to ensure tidy cleanup of connection resources, the daemon
    # and the name server are both used as context managers in a with
    # statement.
    stocksDaemon = Pyro4.core.Daemon()
    nasdaq_uri = stocksDaemon.register(nasdaq)
    newyork_uri = stocksDaemon.register(newyork)
    nameserverDaemon = existsNS()
    if (nameserverDaemon is not None):
        nameserverDaemon.nameserver.register('example.stockmarket.nasdaq',
                                             nasdaq_uri)
        nameserverDaemon.nameserver.register('example.stockmarket.newyork',
                                             newyork_uri)
        stocksDaemon.combine(nameserverDaemon)
        # stocksDaemon.combine(broadcastServer)
    else:
        ns = Pyro4.locateNS()
        ns.register('example.stockmarket.nasdaq', nasdaq_uri)
        ns.register('example.stockmarket.newyork', newyork_uri)
    print('Stockmarkets available.')
    stocksDaemon.requestLoop()
