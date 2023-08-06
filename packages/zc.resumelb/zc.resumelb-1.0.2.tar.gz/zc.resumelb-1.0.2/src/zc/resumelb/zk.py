##############################################################################
#
# Copyright Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""ZooKeeper integration
"""
import gevent
import gevent.pool
import gevent.pywsgi
import gevent.server
import gevent.socket
import json
import logging
import os
import re
import signal
import socket
import sys
import time
import zc.parse_addr
import zc.zk

def worker(app, global_conf, zookeeper, path, loggers=None, address=':0',
           threads=None, backdoor=False, description=None, version=None,
           run=True, **kw):
    """Paste deploy server runner
    """
    if loggers:
        if re.match(r'\d+$', loggers):
            logging.basicConfig(level=int(loggers))
        elif loggers in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
            logging.basicConfig(level=getattr(logging, loggers))
        else:
            import ZConfig
            ZConfig.configureLoggers(loggers)

    zk = zc.zk.ZooKeeper(zookeeper)
    address = zc.parse_addr.parse_addr(address)
    from zc.resumelb.worker import Worker

    worker = Worker(app, address, threads=threads and int(threads),
                    **kw)

    # Set up notification of settings changes.
    settings = zk.properties(path)
    watcher = gevent.get_hub().loop.async()
    watcher.start(lambda : worker.update_settings(settings))
    settings(lambda _: watcher.send())

    registration_data = {}
    if backdoor == 'true':
        from gevent import backdoor
        bd = backdoor.BackdoorServer(('127.0.0.1', 0), locals())
        bd.start()
        registration_data['backdoor'] = '127.0.0.1:%s' % bd.server_port
        worker.__bd = bd

    if description:
        registration_data['description'] = description

    if version:
        registration_data['version'] = version

    zk.register_server(path+'/providers', worker.addr, **registration_data)
    worker.zk = zk
    worker.__zksettings = settings

    def shutdown():
        zk.close()
        worker.shutdown()

    gevent.signal(signal.SIGTERM, shutdown)

    if run:
        try:
            worker.server.serve_forever()
        finally:
            logging.getLogger(__name__+'.worker').info('exiting')
            zk.close()
    else:
        gevent.sleep(.01)
        return worker

class WSGIServer(gevent.pywsgi.WSGIServer):

    def __init__(self, *args, **kw):
        self.__socket_timeout = kw.pop('socket_timeout')
        gevent.pywsgi.WSGIServer.__init__(self, *args, **kw)

    def handle(self, socket, address):
        socket.settimeout(self.__socket_timeout)
        return gevent.pywsgi.WSGIServer.handle(self, socket, address)

def _resolve(path):
    rcmod, rcexpr = path.split(':')
    __import__(rcmod)
    rcmod = sys.modules[rcmod]
    return eval(rcexpr, rcmod.__dict__)

def lbmain(args=None, run=True):
    """%prog [options] zookeeper_connection path

    Run a resume-based load balancer on addr.
    """
    if args is None:
        args = sys.argv[1:]
    elif isinstance(args, str):
        args = args.split()
        run = False
    import optparse
    parser = optparse.OptionParser(lbmain.__doc__)
    parser.add_option(
        '-a', '--address', default=':0',
        help="Address to listed on for web requests"
        )
    parser.add_option(
        '-b', '--backlog', type='int',
        help="Server backlog setting.")
    parser.add_option(
        '-d', '--backdoor', action='store_true',
        help="Run a backdoor server. Use with caution!")
    parser.add_option(
        '-e', '--disconnect-message',
        help="Path to error page to use when a request is lost due to "
        "worker disconnection"
        )
    parser.add_option(
        '-L', '--logger-configuration',
        help=
        "Read logger configuration from the given configuration file path.\n"
        "\n"
        "The configuration file must be in ZConfig logger configuration syntax."
        "\n"
        "Alternatively, you can give a Python logger level name or number."
        )
    parser.add_option('-l', '--access-logger', help='Access-log logger name.')
    parser.add_option(
        '-m', '--max-connections', type='int',
        help="Maximum number of simultanious accepted connections.")
    parser.add_option(
        '-r', '--request-classifier', default='zc.resumelb.lb:host_classifier',
        help="Request classification function (module:expr)"
        )
    parser.add_option(
        '-p', '--pool-factory', default='zc.resumelb.lb:Pool',
        help=
        "Callable which creates a pool (module:expr)."
        " Will be called with settings as keyword arguments."
        )
    parser.add_option(
        '-s', '--status-server',
        help=("Run a status server for getting pool information. "
              "The argument is a unix-domain socket path to listen on."))
    parser.add_option(
        '-t', '--socket-timeout', type='float', default=99.,
        help=('HTTP socket timeout.'))
    parser.add_option(
        '-v', '--single-version', action='store_true',
        help=('Only use a single worker version.'))

    try:
        options, args = parser.parse_args(args)
        if len(args) != 2:
            print 'Error: must supply a zookeeper connection string and path.'
            parser.parse_args(['-h'])
        zookeeper, path = args
    except SystemExit:
        if run:
            raise
        else:
            return

    if options.logger_configuration:
        logger_config = options.logger_configuration
        if re.match(r'\d+$', logger_config):
            logging.basicConfig(level=int(logger_config))
        elif logger_config in ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'):
            logging.basicConfig(level=getattr(logging, logger_config))
        else:
            import ZConfig
            with open(logger_config) as f:
                ZConfig.configureLoggers(f.read())

    zk = zc.zk.ZooKeeper(zookeeper)
    worker_path = zk.resolve(path+'/workers/providers')
    addrs = zk.children(worker_path)
    request_classifier = _resolve(options.request_classifier)
    pool_factory = _resolve(options.pool_factory)

    disconnect_message = options.disconnect_message
    if disconnect_message:
        with open(disconnect_message) as f:
            disconnect_message = f.read()
    else:
        disconnect_message = zc.resumelb.lb.default_disconnect_message

    from zc.resumelb.lb import LB
    lb = LB(map(zc.parse_addr.parse_addr, ()),
            request_classifier, disconnect_message,
            pool_factory=pool_factory,
            single_version=options.single_version)


    to_send = [[]]
    # Set up notification of address changes.
    awatcher = gevent.get_hub().loop.async()
    @awatcher.start
    def _():
        lb.set_worker_addrs(to_send[0])

    if options.single_version or pool_factory != zc.resumelb.lb.Pool:
        @addrs
        def get_addrs(a):
            to_send[0] = dict(
                (zc.parse_addr.parse_addr(addr),
                 zk.get_properties(
                     worker_path + '/' + addr).get('version')
                 )
                for addr in addrs)
            awatcher.send()
    else:
        @addrs
        def get_addrs(a):
            to_send[0] = map(zc.parse_addr.parse_addr, addrs)
            awatcher.send()

    # Set up notification of address changes.
    settings = zk.properties(path)
    swatcher = gevent.get_hub().loop.async()
    swatcher.start(lambda : lb.update_settings(settings))
    settings(lambda a: swatcher.send())

    lb.zk = zk
    lb.__zk = addrs, settings

    # Now, start a wsgi server
    addr = zc.parse_addr.parse_addr(options.address)
    if options.max_connections:
        spawn= gevent.pool.Pool(options.max_connections)
    else:
        spawn = 'default'

    if options.access_logger:
        accesslog = AccessLog(options.access_logger)
    else:
        accesslog = None

    server = WSGIServer(
        addr, lb.handle_wsgi, backlog=options.backlog,
        spawn=spawn, log=accesslog, socket_timeout=options.socket_timeout)
    server.start()

    registration_data = {}
    if options.backdoor:
        from gevent import backdoor
        bd = backdoor.BackdoorServer(('127.0.0.1', 0), locals())
        bd.start()
        registration_data['backdoor'] = '127.0.0.1:%s' % bd.server_port

    status_server = None
    if options.status_server:
        def status(socket, addr):
            pool = lb.pool
            status = pool.status()
            writer = socket.makefile('w')
            writer.write(json.dumps(status) + '\n')
            writer.close()
            socket.close()

        status_server_address = options.status_server
        if os.path.exists(status_server_address):
            os.remove(status_server_address)
        sock = gevent.socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(status_server_address)
        sock.listen(5)
        status_server = gevent.server.StreamServer(sock, status)
        status_server.start()

    zk.register_server(path+'/providers', (addr[0], server.server_port),
                       **registration_data)

    def shutdown():
        zk.close()
        server.close()
        if status_server is not None:
            status_server.close()
        lb.shutdown()

    gevent.signal(signal.SIGTERM, shutdown)

    if run:
        try:
            server.serve_forever()
        finally:
            logging.getLogger(__name__+'.lbmain').info('exiting')
            zk.close()
    else:
        gevent.sleep(.01)
        return lb, server

class AccessLog:

    def __init__(self, logger):
        self.write = logging.getLogger(logger).info

worker_format = '%30s%8s%8s%8s'
def get_lb_status(args=None):
    if args is None:
        args = sys.argv[1:]

    for addr in args:
        print 'status for', addr
        status_socket = gevent.socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        status_socket.connect(addr)
        status_file = status_socket.makefile()
        status = json.loads(status_file.read())
        status_file.close()
        status_socket.close()
        workers = status['workers']
        if workers:
            now = time.time()
            print '  backlog: %s, mean backlog: %.1f' % (
                status['backlog'], status['mean_backlog'])
            print '  workers: %s, mean backlog per worker: %.1f' % (
                len(workers), status['mean_backlog'] / len(workers),
                )
            print
            print worker_format % (
                'worker', 'backlog', 'mean bl', 'age')
            for name, bl, mbl, start in sorted(workers):
                print worker_format % (
                    name, bl, "%.1f" % mbl,
                    ("%.1f" % (now-start) if start is not None else '-'))
        else:
            print 'This load-balancer has no workers!'
