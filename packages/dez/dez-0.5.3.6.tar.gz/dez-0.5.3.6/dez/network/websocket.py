import optparse, struct
from base64 import b64encode
from hashlib import sha1
from datetime import datetime
from dez.buffer import Buffer
from dez.json import encode, decode
from dez.network.server import SocketDaemon
from dez.network.client import SimpleClient

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def key2accept(key):
    return b64encode(sha1(key + GUID).digest())

def parse_frame(buf):
    """
    Parse a WebSocket frame. If there is not a complete frame in the
    buffer, return without modifying the buffer.

    Adapted from:
    http://www.cs.rpi.edu/~goldsd/docs/spring2012-csci4220/websocket-py.txt
    """
    payload_start = 2

    # try to pull first two bytes
    if len(buf) < 3:
        return
    b = ord(buf[0])
    fin = b & 0x80      # 1st bit
    # next 3 bits reserved
    opcode = b & 0x0f   # low 4 bits
    b2 = ord(buf[1])
    mask = b2 & 0x80    # high bit of the second byte
    length = b2 & 0x7f    # low 7 bits of the second byte

    # check that enough bytes remain
    if len(buf) < payload_start + 4:
        return
    elif length == 126:
        length, = struct.unpack(">H", buf[2:4])
        payload_start += 2
    elif length == 127:
        length, = struct.unpack(">I", buf[2:6])
        payload_start += 4

    if mask:
        mask_bytes = [ord(b) for b in buf[payload_start:payload_start + 4]]
        payload_start += 4

    # is there a complete frame in the buffer?
    if len(buf) < payload_start + length:
        return

    # remove leading bytes, decode if necessary, dispatch
    payload = buf[payload_start:payload_start + length]
    buf.move(payload_start + length)

    # use xor and mask bytes to unmask data
    if mask:
        unmasked = [mask_bytes[i % 4] ^ ord(b)
            for b, i in zip(payload, range(len(payload)))]
        payload = "".join([chr(c) for c in unmasked])

    return payload

class WebSocketProxy(object):
    def __init__(self, myhostname, myport, targethostname, targetport, b64=False, verbose=False):
        self.verbose = verbose
        self.target = {'host':targethostname, 'port':targetport, 'b64':b64}
        self.proxy = WebSocketDaemon(myhostname, myport, self._new_conn, b64, report_cb=self._report)

    def _report(self, data):
        if self.verbose:
            print "%s [WebSocketProxy] %s"%(datetime.now(), data)

    def _new_conn(self, conn):
        self._report("Connecting to TCP server")
        WebSocketProxyConnection(conn, self.target, self._report)

    def start(self):
        self._report("Proxy started")
        self.proxy.start()

class WebSocketProxyConnection(object):
    def __init__(self, client2ws, target, report_cb=lambda x:None):
        self.client2ws = client2ws
        self.report_cb = report_cb
        SimpleClient(target['b64']).connect(target['host'], target['port'], self._conn_server)

    def _conn_server(self, ws2server):
        self.report_cb("TCP connection ready")
        self.ws2server = ws2server
        self.ws2server.set_rmode_close_chunked(self.client2ws.write)
        self.client2ws.set_cb(self.ws2server.write)
        def do_nothing():pass
        def ws2server_close():
            self.report_cb("TCP server disconnected")
            self.report_cb("Closing client connection")
            self.client2ws.set_close_cb(do_nothing)
            self.client2ws.close()
        def client2ws_close():
            self.report_cb("Client disconnected")
            self.report_cb("Closing TCP connection")
            self.ws2server.set_close_cb(do_nothing)
            self.ws2server.close()
        self.ws2server.set_close_cb(ws2server_close)
        self.client2ws.set_close_cb(client2ws_close)
        self.report_cb("Connections linked")

class WebSocketDaemon(SocketDaemon):
    def __init__(self, hostname, port, cb, b64=False, cbargs=[], report_cb=lambda x:None, isJSON=False):
        SocketDaemon.__init__(self, hostname, port, cb, b64, cbargs)
        real_cb = self.cb
        def handshake_cb(conn):
            report_cb("Handshake initiated")
            WebSocketHandshake(conn, hostname, port, real_cb, report_cb, self.isJSON)
        self.cb = handshake_cb
        self.isJSON = isJSON

    def setJSON(self, isJSON=True):
        self.isJSON = isJSON

class WebSocketHandshake(object):
    def __init__(self, conn, hostname, port, cb, report_cb=lambda x:None, isJSON=False):
        self.hostname = hostname
        self.port = port
        self.cb = cb
        self.report_cb = report_cb
        self.conn = conn
        self.conn.set_rmode_delimiter('\r\n', self._recv_action)
        self.isJSON = isJSON

    def _handshake_error(self, data):
        self.report_cb(data)
        self.report_cb("Connection closed")
        self.conn.close()

    def _recv_action(self, data):
        self.report_cb("Processing action line")
        tokens = data.split(' ')
        if len(tokens) != 3:
            return self._handshake_error("Invalid action line")
        self.path = tokens[1]
        self.conn.set_rmode_delimiter('\r\n\r\n', self._recv_headers)

    def _recv_headers(self, data):
        self.report_cb("Processing headers")
        lines = data.split('\r\n')
        self.headers = {}
        for line in lines:
            header = line.split(': ', 1)
            if len(header) != 2:
                return self._handshake_error("Invalid headers")
            self.headers.__setitem__(*header)
        for required_header in ['Host', 'Origin', 'Sec-WebSocket-Key']:
            if required_header not in self.headers:
                return self._handshake_error("Missing header: %s"%(required_header,))
        response_headers = [
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "WebSocket-Origin: %s"%(self.headers['Origin'],),
            "WebSocket-Location: ws://%s:%s%s"%(self.hostname, self.port, self.path),
            "Sec-WebSocket-Accept: %s"%(key2accept(self.headers['Sec-WebSocket-Key']),)
        ]
        self.conn.write("HTTP/1.1 101 Web Socket Protocol Handshake\r\n%s\r\n\r\n"%("\r\n".join(response_headers),))
        self.report_cb("Handshake complete")
        self.cb(WebSocketConnection(self.conn, self.report_cb, self.isJSON))

class WebSocketConnection(object):
    def __init__(self, conn, report_cb=lambda x:None, isJSON=False):
        self.buff = Buffer()
        self.isJSON = isJSON
        self.conn = conn
        self.conn.halt_read()
        self.report_cb = report_cb
        self.report_cb("Client connection ready")

    def _recv(self, data):
        self.report_cb('Data received:"%s"'%(data,))
        self.buff += data
        payload = parse_frame(self.buff)
        if payload:
            try:
                self.report_cb('Payload parsed:"%s"'%(payload.decode("utf-8"),))
            except UnicodeDecodeError, e: # connection closed
                self.report_cb('Closing connection: %s'%(e,))
                return self.close()
            if self.isJSON:
                try:
                    payload = decode(payload)
                except ValueError, e: # connection closed
                    self.report_cb('Closing connection: %s'%(e,))
                    return self.close()
            self.cb(payload)

    def set_close_cb(self, cb, cbargs=[]):
        self.conn.set_close_cb(cb, cbargs)

    def set_cb(self, cb):
        self.cb = cb
        self.conn.set_rmode_close_chunked(self._recv)

    def write(self, data):
        if self.isJSON:
            data = encode(data)
        self.report_cb('Data sent:"%s"'%(data))
        dl = len(data)
        if dl < 126:
            lenchars = chr(dl)
        elif dl < 65536: # 2 bytes
            lenchars = chr(126) + struct.pack("=H", dl)[::-1]
        else: # 8 bytes
            lenchars = chr(127) + struct.pack("=Q", dl)[::-1]
        self.conn.write(chr(0x81) + lenchars + data.encode("utf-8"))

    def close(self):
        self.conn.close()

def startwebsocketproxy():
    parser = optparse.OptionParser('dez_websocket_proxy [DOMAIN] [PORT]')
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="verbose output")
    options, args = parser.parse_args()
    try:
        hostname, port = args
    except:
        print '\ndez_websocket_proxy is run with two arguments: the hostname and port of the server being proxied to. For example:\n\ndez_websocket_proxy mydomain.com 5555\n\nwill run a WebSocket server that listens for connections on port 81 and proxies them to a TCP server at mydomain.com:5555.'
        return
    try:
        port = int(port)
    except:
        print '\nThe second argument must be an integer. The command should look like this:\n\ndez_websocket_proxy mydomain.com 5555\n\nTry again!'
        return
    try:
        proxy = WebSocketProxy('localhost', 81, hostname, port, verbose=options.verbose)
    except:
        print '\nPermission denied to use port %s. Depending on how your system is set up, you may need root privileges to run the proxy.'%(port)
        return
    print 'running WebSocket server on port 81'
    print 'proxying to %s:%s'%(hostname, port)
    proxy.start()