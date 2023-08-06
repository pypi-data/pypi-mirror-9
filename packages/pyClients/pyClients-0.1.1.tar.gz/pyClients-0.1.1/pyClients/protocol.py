import time
import struct
import socket
import logging

GET = 0
POST = 1
SUS = 2
RESP = 3

RESP_TIPO_OK = 1
RESP_TIPO_FAIL = 2

RESP_CODIGO_101 = 1
RESP_CODIGO_102 = 2
RESP_CODIGO_103 = 3
RESP_CODIGO_104 = 4
RESP_CODIGO_201 = 1
RESP_CODIGO_202 = 2
RESP_CODIGO_203 = 3
RESP_CODIGO_204 = 4
RESP_CODIGO_205 = 5
RESP_CODIGO_206 = 6

SUS_OP_FUENTE = 0
SUS_OP_CONS = 1
SUS_OP_DEL = 2

GET_OP_NORMAL = 0
GET_OP_TM = 1
ALL_SOURCES = 0

# mensaje len
HEADER_LEN = 4
RESP_LEN = 4


logging.basicConfig(level=logging.INFO)

class Socket():
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket()
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((socket.gethostbyname(host), port))

    def send_all(self, msg):
        totalsent = 0
        msg_len = len(msg)
        logging.info("Enviando {} bytes".format(msg_len))
        logging.info("MSG: {}".format(msg))
        while totalsent < msg_len:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent += sent
        logging.info("Envie todos los datos que tenia")

    def recive_all(self, msg_len):
        chunks = []
        bytes_recd = 0
        while bytes_recd < msg_len:
            chunk = self.sock.recv(min(msg_len - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError('socket connection broken')
            chunks.append(chunk)
            bytes_recd += len(chunk)
        return b''.join(chunks)


class BaseClient:
    def __init__(self):
        self.sock = Socket()
        self.id = None

    def connect_server(self, host, port):
        self.sock.connect(host, port)

    def send_sus(self, op, data):
        msg = struct.pack('!3H', SUS, len(data), op) + data.encode()
        self.sock.send_all(msg)

    def send_post(self, data):
        fmt = '!3HL'

        msg = struct.pack(fmt, POST, len(data), self.id,
                int(time.time())) + data

        self.sock.send_all(msg)

    def send_get(self, op, idDestino, tm_inicio=0, tm_fin=0):
        fmt = '!5H'
        data = ""
        if (tm_inicio != 0 or tm_fin != 0):
            data = str(tm_inicio) + ';' 'tm_fin'
        if self.id is None:
            id = 0
        else:
            id = self.id

        msg = struct.pack(fmt, GET, len(data), idDestino, op, id) + data.encode()
        self.sock.send_all(msg)

    def send_resp(self, tipo, codigo, data):
        fmt = '!4H'
        msg = struct.pack(fmt, RESP, len(data), tipo, codigo) + data.encode()
        self.sock.send_all(msg)

    def recive_header(self):
        return struct.unpack('!2H', self.sock.recive_all(HEADER_LEN))

    def recive_resp(self, dlen):
        fmt = '!2H'

        tipo, codigo = struct.unpack(fmt, self.sock.recive_all(RESP_LEN))
        datos = struct.unpack(str(dlen) + 's', self.sock.recive_all(dlen))[0]

        return tipo, codigo, datos

    def recive_response(self):
        opcode, dlen = self.recive_header()
        tipo, codigo, datos = self.recive_resp(dlen)
        return tipo, codigo, datos

