# vim:ts=4:sw=4:expandtab
"""A mongodb client library for Diesel"""

# needed to make diesel work with python 2.5
from __future__ import with_statement

import itertools
import struct
from collections import deque
from diesel import Client, call, sleep, send, receive, first, Loop, Application, ConnectionClosed
from bson import BSON, _make_c_string, decode_all
from bson.son import SON

_ZERO = "\x00\x00\x00\x00"
HEADER_SIZE = 16

class MongoOperationalError(Exception): pass

def _full_name(parent, child):
    return "%s.%s" % (parent, child)

class TraversesCollections(object):
    def __init__(self, name, client):
        self.name = name
        self.client = client

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, name):
        cls = self.client.collection_class or Collection
        return cls(_full_name(self.name, name), self.client)


class Db(TraversesCollections):
    pass

class Collection(TraversesCollections):
    def find(self, spec=None, fields=None, skip=0, limit=0):
        return MongoCursor(self.name, self.client, spec, fields, skip, limit)

    def update(self, spec, doc, upsert=False, multi=False, safe=True):
        return self.client.update(self.name, spec, doc, upsert, multi, safe)

    def insert(self, doc_or_docs, safe=True):
        return self.client.insert(self.name, doc_or_docs, safe)

    def delete(self, spec, safe=True):
        return self.client.delete(self.name, spec, safe)

class MongoClient(Client):
    collection_class = None

    def __init__(self, host='localhost', port=27017, **kw):
        Client.__init__(self, host, port, **kw)
        self._msg_id_counter = itertools.count(1)

    @property
    def _msg_id(self):
        return self._msg_id_counter.next()

    def _put_request_get_response(self, op, data):
        self._put_request(op, data)
        header = receive(HEADER_SIZE)
        length, id, to, code = struct.unpack('<4i', header)
        message = receive(length - HEADER_SIZE)
        cutoff = struct.calcsize('<iqii')
        flag, cid, start, numret = struct.unpack('<iqii', message[:cutoff])
        body = decode_all(message[cutoff:])
        return (cid, start, numret, body)

    def _put_request(self, op, data):
        req = struct.pack('<4i', HEADER_SIZE + len(data), self._msg_id, 0, op)
        send("%s%s" % (req, data))

    def _handle_response(self, cursor, resp):
        cid, start, numret, result = resp
        cursor.retrieved += numret
        cursor.id = cid
        if not cid or (cursor.retrieved == cursor.limit):
            cursor.finished = True
        return result

    @call
    def query(self, cursor):
        op = Ops.OP_QUERY
        c = cursor
        msg = Ops.query(c.col, c.spec, c.fields, c.skip, c.limit)
        resp = self._put_request_get_response(op, msg)
        return self._handle_response(cursor, resp)

    @call
    def get_more(self, cursor):
        limit = 0
        if cursor.limit:
            if cursor.limit > cursor.retrieved:
                limit = cursor.limit - cursor.retrieved
            else:
                cursor.finished = True
        if not cursor.finished:
            op = Ops.OP_GET_MORE
            msg = Ops.get_more(cursor.col, limit, cursor.id)
            resp = self._put_request_get_response(op, msg)
            return self._handle_response(cursor, resp)
        else:
            return []

    def _put_gle_command(self):
        msg = Ops.query('admin.$cmd', {'getlasterror' : 1}, 0, 0, -1)
        res = self._put_request_get_response(Ops.OP_QUERY, msg)
        _, _, _, r = res
        doc = r[0]
        if doc.get('err'):
            raise MongoOperationalError(doc['err'])
        return doc

    @call
    def update(self, col, spec, doc, upsert=False, multi=False, safe=True):
        data = Ops.update(col, spec, doc, upsert, multi)
        self._put_request(Ops.OP_UPDATE, data)
        if safe:
            return self._put_gle_command()

    @call
    def insert(self, col, doc_or_docs, safe=True):
        data = Ops.insert(col, doc_or_docs)
        self._put_request(Ops.OP_INSERT, data)
        if safe:
            return self._put_gle_command()

    @call
    def delete(self, col, spec, safe=True):
        data = Ops.delete(col, spec)
        self._put_request(Ops.OP_DELETE, data)
        if safe:
            return self._put_gle_command()

    @call
    def drop_database(self, name):
        return self._command(name, {'dropDatabase':1})

    @call
    def list_databases(self):
        result = self._command('admin', {'listDatabases':1})
        return [(d['name'], d['sizeOnDisk']) for d in result['databases']]

    @call
    def _command(self, dbname, command):
        msg = Ops.query('%s.$cmd' % dbname, command, None, 0, 1)
        resp = self._put_request_get_response(Ops.OP_QUERY, msg)
        cid, start, numret, result = resp
        if result:
            return result[0]
        else:
            return []

    def __getattr__(self, name):
        return Db(name, self)

class Ops(object):
    ASCENDING = 1
    DESCENDING = -1
    OP_UPDATE = 2001
    OP_INSERT = 2002
    OP_GET_BY_OID = 2003
    OP_QUERY = 2004
    OP_GET_MORE = 2005
    OP_DELETE = 2006
    OP_KILL_CURSORS = 2007

    @staticmethod
    def query(col, spec, fields, skip, limit):
        data = [
            _ZERO, 
            _make_c_string(col), 
            struct.pack('<ii', skip, limit),
            BSON.encode(spec or {}),
        ]
        if fields:
            if type(fields) == dict:
                data.append(BSON.encode(fields))
            else:
                data.append(BSON.encode(dict.fromkeys(fields, 1)))
        return "".join(data)

    @staticmethod
    def get_more(col, limit, id):
        data = _ZERO
        data += _make_c_string(col)
        data += struct.pack('<iq', limit, id)
        return data

    @staticmethod
    def update(col, spec, doc, upsert, multi):
        colname = _make_c_string(col)
        flags = 0
        if upsert:
            flags |= 1 << 0
        if multi:
            flags |= 1 << 1
        fmt = '<i%dsi' % len(colname)
        part = struct.pack(fmt, 0, colname, flags)
        return "%s%s%s" % (part, BSON.encode(spec), BSON.encode(doc))

    @staticmethod
    def insert(col, doc_or_docs):
        try:
            doc_or_docs.fromkeys
            doc_or_docs = [doc_or_docs]
        except AttributeError:
            pass
        doc_data = "".join(BSON.encode(doc) for doc in doc_or_docs)
        colname = _make_c_string(col)
        return "%s%s%s" % (_ZERO, colname, doc_data)

    @staticmethod
    def delete(col, spec):
        colname = _make_c_string(col)
        return "%s%s%s%s" % (_ZERO, colname, _ZERO, BSON.encode(spec))

class MongoIter(object):
    def __init__(self, cursor):
        self.cursor = cursor
        self.cache = deque()

    def next(self):
        try:
            return self.cache.popleft()
        except IndexError:
            more = self.cursor.more()
            if not more:
                raise StopIteration()
            else:
                self.cache.extend(more)
                return self.next()
        
class MongoCursor(object):
    def __init__(self, col, client, spec, fields, skip, limit):
        self.col = col
        self.client = client
        self.spec = spec
        self.fields = fields
        self.skip = skip
        self.limit = limit
        self.id = None
        self.retrieved = 0
        self.finished = False
        self._query_additions = []

    def more(self):
        if not self.retrieved:
            self._touch_query()
        if not self.id and not self.finished:
            return self.client.query(self)
        elif not self.finished:
            return self.client.get_more(self)

    def all(self):
        return list(self)

    def __iter__(self):
        return MongoIter(self)

    def one(self):
        all = self.all()
        la = len(all)
        if la == 1:
            res = all[0]
        elif la == 0:
            res = None
        else:
            raise ValueError("Cursor returned more than 1 record")
        return res

    def count(self):
        if self.retrieved:
            raise ValueError("can't count an already started cursor")
        db, col = self.col.split('.', 1)
        l = [('count', col), ('query', self.spec)]
        if self.skip:
            l.append(('skip', self.skip))
        if self.limit:
            l.append(('limit', self.limit))

        command = SON(l)
        result = self.client._command(db, command)
        return int(result.get('n', 0))

    def sort(self, name, direction):
        if self.retrieved:
            raise ValueError("can't sort an already started cursor")
        key = SON()
        key[name] = direction
        self._query_additions.append(('sort', key))
        return self

    def _touch_query(self):
        if self._query_additions:
            spec = SON({'$query': self.spec or {}})
            for k, v in self._query_additions:
                if k == 'sort':
                    ordering = spec.setdefault('$orderby', SON())
                    ordering.update(v)
            self.spec = spec
        
    def __enter__(self):
        return self

    def __exit__(self, *args, **params):
        if self.id and not self.finished:
            raise RuntimeError("need to cleanup cursor!")

class RawMongoClient(Client):
    "A mongodb client that does the bare minimum to push bits over the wire."

    @call
    def send(self, data, respond=False):
        """Send raw mongodb data and optionally yield the server's response."""
        send(data)
        if not respond:
            return ''
        else:
            header = receive(HEADER_SIZE)
            length, id, to, opcode = struct.unpack('<4i', header)
            body = receive(length - HEADER_SIZE)
            return header + body

class MongoProxy(object):
    ClientClass = RawMongoClient

    def __init__(self, backend_host, backend_port):
        self.backend_host = backend_host
        self.backend_port = backend_port

    def __call__(self, addr):
        """A persistent client<--proxy-->backend connection handler."""
        try:
            backend = None
            while True:
                header = receive(HEADER_SIZE)
                info = struct.unpack('<4i', header)
                length, id, to, opcode = info
                body = receive(length - HEADER_SIZE)
                resp, info, body = self.handle_request(info, body)
                if resp is not None:
                    # our proxy will respond without talking to the backend
                    send(resp)
                else:
                    # pass the (maybe modified) request on to the backend
                    length, id, to, opcode = info
                    is_query = opcode in [Ops.OP_QUERY, Ops.OP_GET_MORE]
                    payload = header + body
                    (backend, resp) = self.from_backend(payload, is_query, backend)
                    self.handle_response(resp)
        except ConnectionClosed:
            if backend:
                backend.close()

    def handle_request(self, info, body):
        length, id, to, opcode = info
        print "saw request with opcode", opcode
        return None, info, body

    def handle_response(self, response):
        send(response)

    def from_backend(self, data, respond, backend=None):
        if not backend:
            backend = self.ClientClass()
            backend.connect(self.backend_host, self.backend_port)
        resp = backend.send(data, respond)
        return (backend, resp)
