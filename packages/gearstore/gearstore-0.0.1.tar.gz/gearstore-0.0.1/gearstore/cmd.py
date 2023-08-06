# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging
import socket
import threading

from gearstore import stocker
from gearstore.store import sqla


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('servers', nargs='+', help='Servers to connect to, '
                        ' format of host/port')
    parser.add_argument('--sqlalchemy-dsn', help='SQLAlchemy DSN to store in')
    parser.add_argument('--polling_interval', default=5, help='How many'
                        ' seconds to wait for new jobs from Gearman before'
                        ' polling database directly.')

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('gearstore')

    stkr = stocker.Stocker(
        client_id=socket.gethostname(), dsn=args.sqlalchemy_dsn)
    stkr.registerStoreFunction()

    for s in args.servers:
        if '/' in s:
            (host, port) = s.split('/', 2)
            stkr.addServer(host, port)
        else:
            stkr.addServer(s)

    stkr.waitForServer()
    log.info('Connected to server(s)')
    new_stuff = threading.Event()

    def _stock():
        while True:
            stkr.stock()
            log.debug("returned from stock")
            new_stuff.set()

    def _ship():
        while True:
            stkr.ship()
            log.debug("returned from ship")
            new_stuff.clear()
            new_stuff.wait(args.polling_interval)

    stock_thread = threading.Thread(target=_stock)
    ship_thread = threading.Thread(target=_ship)
    log.debug("Starting stocker thread")
    stock_thread.start()
    log.debug("Starting shipper thread")
    ship_thread.start()
    stock_thread.join()


def init_schema():
    parser = argparse.ArgumentParser()
    parser.add_argument('sqlalchemy_dsn', help='SQLAlchemy DSN of database to '
                        ' initialize')

    args = parser.parse_args()

    store = sqla.Store(args.sqlalchemy_dsn)
    store.initialize_schema()
