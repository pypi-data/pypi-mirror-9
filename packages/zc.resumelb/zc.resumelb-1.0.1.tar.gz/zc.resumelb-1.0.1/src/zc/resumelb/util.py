from struct import pack, unpack
from marshal import loads, dumps, dump, load

import errno
import gevent.queue
import logging
import socket
import tempfile

logger = logging.getLogger(__name__)

disconnected_errors = (errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN,
                       errno.ESHUTDOWN, errno.ECONNABORTED)

class Disconnected(Exception):
    pass

def read_message(sock):
    data = ''
    while len(data) < 8:
        try:
            received = sock.recv(8-len(data))
        except socket.error, err:
            if err.args[0] in disconnected_errors:
                logger.debug("read_message disconnected %s %r", sock, err)
                raise Disconnected()
            else:
                raise

        if not received:
            if data:
                logger.info("read_message disconnected (l) %r", sock)
            raise Disconnected()
        data += received

    rno, l = unpack(">II", data)

    data = ''
    while len(data) < l:
        received = sock.recv(l-len(data))
        if not received:
            logger.info("read_message disconnected (d) %r", sock)
            raise Disconnected()
        data += received

    return rno, loads(data)

def write_message(sock, rno, *a):
    to_send = []
    for data in a:
        data = dumps(data)
        to_send.append(pack(">II", rno, len(data)))
        to_send.append(data)

    data = ''.join(to_send)
    while data:
        try:
            sent = sock.send(data)
        except socket.error, err:
            if err.args[0] in disconnected_errors or sock.closed:
                logger.debug("write_message disconnected %s", sock)
                raise Disconnected()
            else:
                raise
        data = data[sent:]

SEND_SIZE = 1 << 16
KEEP_ALIVE = pack(">II", 0, 1) + 'N'
def writer(writeq, sock, multiplexer):
    get = writeq.get
    write_message_ = write_message
    timeout = multiplexer.write_keepalive_interval
    Empty = gevent.queue.Empty
    send = sock.send
    dumps_ = dumps
    pack_ = pack
    while 1:
        try:
            rno, data = get(True, timeout)
        except Empty:
            data = KEEP_ALIVE
        else:
            to_send = []
            append = to_send.append
            nsend = 0
            while 1:
                data = dumps_(data)
                append(pack_(">II", rno, len(data)))
                append(data)
                nsend += len(data) + 8
                if nsend > SEND_SIZE:
                    break
                try:
                    rno, data = get(False)
                except Empty:
                    break
            data = ''.join(to_send)

        while data:
            try:
                sent = send(data)
            except socket.error, err:
                if err.args[0] in disconnected_errors or sock.closed:
                    logger.debug("write_message disconnected %s", sock)
                    multiplexer.disconnected()
                    return
                else:
                    raise
            data = data[sent:]


queue_size_bytes = 99999

class ByteSizedQueue(gevent.queue.Queue):

    __size = 0

    def _get(self):
        item = super(ByteSizedQueue, self)._get()
        if item:
            self.__size -= len(item)
        return item

    def _put(self, item):
        super(ByteSizedQueue, self)._put(item)
        if item:
            self.__size += len(item)

    def qsize(self):
        return self.__size or super(ByteSizedQueue, self).qsize()

class BufferedQueue:

    buffer = None

    def __init__(self):
        self.queue = ByteSizedQueue(queue_size_bytes)
        self._put = self.queue.put
        self.get = self.queue.get

    def put(self, data):
        try:
            self._put(data, False, .001)
        except gevent.queue.Full:
            self.queue = queue = Buffer(self.queue)
            self._put = queue.put
            self.close = queue.close
            queue.put(data)

    def qsize(self):
        return self.queue.qsize()

    def close(self):
        pass

class Buffer:

    size = size_bytes = read_position = write_position = 0

    def __init__(self, queue):
        self.queue = queue
        self.file = tempfile.TemporaryFile(suffix='.rlbob')

    def qsize(self):
        return self.queue.qsize() + self.size_bytes

    def close(self):
        # Close the queue.  There are 2 possibilities:

        # 1. The file buffer is non-empty and there's a greenlet
        #    emptying it.  (See the feed greenlet in the put method.)
        #    The greenlet is blocked puting data in the underlying
        #    queue.  We can set size to -1, marking us as closed and
        #    close the file. The greenlet will check sise before
        #    trying trying to read the file again.

        # 2. The file bugger is empty and there's no running greenlet.
        #    We can set the size to -1 and close the file.

        # In either case, we'll empty the underying queue, both for
        # cleanliness and to unblock a greenlet, if there is one, so
        # it can die a normal death,

        if self.size < 0:
            return # already closed

        self.size = -1
        self.file.close()

        queue = self.queue
        while queue.qsize():
            queue.get()
        self.size_bytes = 0

    def put(self, data, block=False, timeout=None):
        if self.size < 0:
            return # closed

        file = self.file
        file.seek(self.write_position)
        dump(data, file)
        self.write_position = file.tell()
        if data:
            self.size_bytes += len(data)
        self.size += 1
        if self.size == 1:

            @gevent.spawn
            def feed():
                queue = self.queue
                while self.size > 0:
                    file.seek(self.read_position)
                    data = load(file)
                    self.read_position = file.tell()
                    queue.put(data)
                    if self.size > 0:
                        # We check the size here, in case the queue was closed
                        if data:
                            self.size_bytes -= len(data)
                        self.size -= 1
                    else:
                        assert self.size == -1


class Worker:

    ReadQueue = gevent.queue.Queue

    write_keepalive_interval = None

    def connected(self, socket, addr=None):
        if addr is None:
            addr = socket.getpeername()
        logger.info('worker connected %s', addr)
        self.addr = addr
        self.readers = {}
        self.write_queue = writeq = ByteSizedQueue(queue_size_bytes)
        gevent.Greenlet.spawn(writer, writeq, socket, self)
        self.put = writeq.put
        self.is_connected = True
        self.socket = socket
        return self.readers

    def __len__(self):
        return len(self.readers)

    def start(self, rno):
        readq = self.ReadQueue()
        self.readers[rno] = readq.put
        return readq

    def end(self, rno):
        try:
            queue = self.readers.pop(rno)
        except KeyError:
            return # previously cancelled

    def put_disconnected(self, *a, **k):
        raise Disconnected()

    def disconnected(self):
        logger.info('worker disconnected %s', self.addr)
        self.is_connected = False
        for put in self.readers.itervalues():
            put(None)
        self.socket.close()

        self.put = self.put_disconnected

class LBWorker(Worker):

    write_keepalive_interval = 0.1

    ReadQueue = BufferedQueue

    def connected(self, socket, addr=None):
        self.queues = {}
        return Worker.connected(self, socket, addr)

    def start(self, rno):
        self.queues[rno] = queue = Worker.start(self, rno)
        return queue

    def end(self, rno):
        try:
            queue = self.readers.pop(rno)
        except KeyError:
            return # previously cancelled
        self.queues.pop(rno).close()
