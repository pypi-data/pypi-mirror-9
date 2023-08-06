from palm.palm import ProtoBase, is_string, RepeatedSequence, ProtoValueError

_PB_type = type
_PB_finalizers = []


class RpbErrorResp(ProtoBase):
    _required = [1, 2]
    _field_map = {'errcode': 2, 'errmsg': 1}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['errmsg', 'errcode']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_errmsg(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'errmsg')
            self._cache[1] = r
        return r

    def _establish_parentage_errmsg(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_errmsg), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_errmsg
                v._pbf_establish_parent_callback = self._establish_parentage_errmsg

    def _set_errmsg(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_errmsg(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field errmsg"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_errmsg(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_errmsg(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "errmsg"

    errmsg = property(_get_errmsg, _set_errmsg, _del_errmsg)

    @property
    def errmsg__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def errmsg__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_errmsg(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_errmsg)


    def _get_errcode(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_uint32, 'errcode')
            self._cache[2] = r
        return r

    def _establish_parentage_errcode(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_errcode), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_errcode
                v._pbf_establish_parent_callback = self._establish_parentage_errcode

    def _set_errcode(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_errcode(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field errcode"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_uint32

    def _mod_errcode(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_uint32

    def _del_errcode(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "errcode"

    errcode = property(_get_errcode, _set_errcode, _del_errcode)

    @property
    def errcode__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def errcode__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_errcode(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_errcode)


TYPE_RpbErrorResp = RpbErrorResp
_PB_finalizers.append('RpbErrorResp')

class RpbGetClientIdResp(ProtoBase):
    _required = [1]
    _field_map = {'client_id': 1}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['client_id']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_client_id(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'client_id')
            self._cache[1] = r
        return r

    def _establish_parentage_client_id(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_client_id), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_client_id
                v._pbf_establish_parent_callback = self._establish_parentage_client_id

    def _set_client_id(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_client_id(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field client_id"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_client_id(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_client_id(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "client_id"

    client_id = property(_get_client_id, _set_client_id, _del_client_id)

    @property
    def client_id__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def client_id__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_client_id(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_client_id)


TYPE_RpbGetClientIdResp = RpbGetClientIdResp
_PB_finalizers.append('RpbGetClientIdResp')

class RpbSetClientIdReq(ProtoBase):
    _required = [1]
    _field_map = {'client_id': 1}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['client_id']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_client_id(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'client_id')
            self._cache[1] = r
        return r

    def _establish_parentage_client_id(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_client_id), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_client_id
                v._pbf_establish_parent_callback = self._establish_parentage_client_id

    def _set_client_id(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_client_id(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field client_id"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_client_id(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_client_id(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "client_id"

    client_id = property(_get_client_id, _set_client_id, _del_client_id)

    @property
    def client_id__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def client_id__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_client_id(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_client_id)


TYPE_RpbSetClientIdReq = RpbSetClientIdReq
_PB_finalizers.append('RpbSetClientIdReq')

class RpbGetServerInfoResp(ProtoBase):
    _required = []
    _field_map = {'node': 1, 'server_version': 2}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['node', 'server_version']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_node(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'node')
            self._cache[1] = r
        return r

    def _establish_parentage_node(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_node), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_node
                v._pbf_establish_parent_callback = self._establish_parentage_node

    def _set_node(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_node(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field node"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_node(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_node(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "node"

    node = property(_get_node, _set_node, _del_node)

    @property
    def node__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def node__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_node(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_node)


    def _get_server_version(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'server_version')
            self._cache[2] = r
        return r

    def _establish_parentage_server_version(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_server_version), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_server_version
                v._pbf_establish_parent_callback = self._establish_parentage_server_version

    def _set_server_version(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_server_version(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field server_version"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_server_version(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_server_version(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "server_version"

    server_version = property(_get_server_version, _set_server_version, _del_server_version)

    @property
    def server_version__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def server_version__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_server_version(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_server_version)


TYPE_RpbGetServerInfoResp = RpbGetServerInfoResp
_PB_finalizers.append('RpbGetServerInfoResp')

class RpbGetReq(ProtoBase):
    _required = [1, 2]
    _field_map = {'pr': 4, 'head': 8, 'key': 2, 'if_modified': 7, 'notfound_ok': 6, 'bucket': 1, 'r': 3, 'basic_quorum': 5, 'deletedvclock': 9}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['bucket', 'key', 'r', 'pr', 'basic_quorum', 'notfound_ok', 'if_modified', 'head', 'deletedvclock']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_bucket(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'bucket')
            self._cache[1] = r
        return r

    def _establish_parentage_bucket(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_bucket), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_bucket
                v._pbf_establish_parent_callback = self._establish_parentage_bucket

    def _set_bucket(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_bucket(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field bucket"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "bucket"

    bucket = property(_get_bucket, _set_bucket, _del_bucket)

    @property
    def bucket__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def bucket__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_bucket(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_bucket)


    def _get_key(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'key')
            self._cache[2] = r
        return r

    def _establish_parentage_key(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_key), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_key
                v._pbf_establish_parent_callback = self._establish_parentage_key

    def _set_key(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_key(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field key"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "key"

    key = property(_get_key, _set_key, _del_key)

    @property
    def key__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def key__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_key(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_key)


    def _get_r(self):
        if 3 in self._cache:
            r = self._cache[3]
        else:
            r = self._buf_get(3, ProtoBase.TYPE_uint32, 'r')
            self._cache[3] = r
        return r

    def _establish_parentage_r(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_r), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_r
                v._pbf_establish_parent_callback = self._establish_parentage_r

    def _set_r(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_r(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field r"
            raise ProtoValueError(list_assign_error)
        self._cache[3] = v
        self._mods[3] = ProtoBase.TYPE_uint32

    def _mod_r(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[3] = ProtoBase.TYPE_uint32

    def _del_r(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 3 in self._cache:
            del self._cache[3]
        if 3 in self._mods:
            del self._mods[3]
        self._buf_del(3)

    _pb_field_name_3 = "r"

    r = property(_get_r, _set_r, _del_r)

    @property
    def r__exists(self):
        return 3 in self._mods or self._buf_exists(3)

    @property
    def r__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_r(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(3)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(3)

    _pbf_finalizers.append(_finalize_r)


    def _get_pr(self):
        if 4 in self._cache:
            r = self._cache[4]
        else:
            r = self._buf_get(4, ProtoBase.TYPE_uint32, 'pr')
            self._cache[4] = r
        return r

    def _establish_parentage_pr(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_pr), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_pr
                v._pbf_establish_parent_callback = self._establish_parentage_pr

    def _set_pr(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_pr(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field pr"
            raise ProtoValueError(list_assign_error)
        self._cache[4] = v
        self._mods[4] = ProtoBase.TYPE_uint32

    def _mod_pr(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[4] = ProtoBase.TYPE_uint32

    def _del_pr(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 4 in self._cache:
            del self._cache[4]
        if 4 in self._mods:
            del self._mods[4]
        self._buf_del(4)

    _pb_field_name_4 = "pr"

    pr = property(_get_pr, _set_pr, _del_pr)

    @property
    def pr__exists(self):
        return 4 in self._mods or self._buf_exists(4)

    @property
    def pr__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_pr(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(4)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(4)

    _pbf_finalizers.append(_finalize_pr)


    def _get_basic_quorum(self):
        if 5 in self._cache:
            r = self._cache[5]
        else:
            r = self._buf_get(5, ProtoBase.TYPE_bool, 'basic_quorum')
            self._cache[5] = r
        return r

    def _establish_parentage_basic_quorum(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_basic_quorum), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_basic_quorum
                v._pbf_establish_parent_callback = self._establish_parentage_basic_quorum

    def _set_basic_quorum(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_basic_quorum(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field basic_quorum"
            raise ProtoValueError(list_assign_error)
        self._cache[5] = v
        self._mods[5] = ProtoBase.TYPE_bool

    def _mod_basic_quorum(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[5] = ProtoBase.TYPE_bool

    def _del_basic_quorum(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 5 in self._cache:
            del self._cache[5]
        if 5 in self._mods:
            del self._mods[5]
        self._buf_del(5)

    _pb_field_name_5 = "basic_quorum"

    basic_quorum = property(_get_basic_quorum, _set_basic_quorum, _del_basic_quorum)

    @property
    def basic_quorum__exists(self):
        return 5 in self._mods or self._buf_exists(5)

    @property
    def basic_quorum__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_basic_quorum(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(5)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(5)

    _pbf_finalizers.append(_finalize_basic_quorum)


    def _get_notfound_ok(self):
        if 6 in self._cache:
            r = self._cache[6]
        else:
            r = self._buf_get(6, ProtoBase.TYPE_bool, 'notfound_ok')
            self._cache[6] = r
        return r

    def _establish_parentage_notfound_ok(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_notfound_ok), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_notfound_ok
                v._pbf_establish_parent_callback = self._establish_parentage_notfound_ok

    def _set_notfound_ok(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_notfound_ok(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field notfound_ok"
            raise ProtoValueError(list_assign_error)
        self._cache[6] = v
        self._mods[6] = ProtoBase.TYPE_bool

    def _mod_notfound_ok(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[6] = ProtoBase.TYPE_bool

    def _del_notfound_ok(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 6 in self._cache:
            del self._cache[6]
        if 6 in self._mods:
            del self._mods[6]
        self._buf_del(6)

    _pb_field_name_6 = "notfound_ok"

    notfound_ok = property(_get_notfound_ok, _set_notfound_ok, _del_notfound_ok)

    @property
    def notfound_ok__exists(self):
        return 6 in self._mods or self._buf_exists(6)

    @property
    def notfound_ok__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_notfound_ok(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(6)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(6)

    _pbf_finalizers.append(_finalize_notfound_ok)


    def _get_if_modified(self):
        if 7 in self._cache:
            r = self._cache[7]
        else:
            r = self._buf_get(7, ProtoBase.TYPE_bytes, 'if_modified')
            self._cache[7] = r
        return r

    def _establish_parentage_if_modified(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_if_modified), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_if_modified
                v._pbf_establish_parent_callback = self._establish_parentage_if_modified

    def _set_if_modified(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_if_modified(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field if_modified"
            raise ProtoValueError(list_assign_error)
        self._cache[7] = v
        self._mods[7] = ProtoBase.TYPE_bytes

    def _mod_if_modified(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[7] = ProtoBase.TYPE_bytes

    def _del_if_modified(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 7 in self._cache:
            del self._cache[7]
        if 7 in self._mods:
            del self._mods[7]
        self._buf_del(7)

    _pb_field_name_7 = "if_modified"

    if_modified = property(_get_if_modified, _set_if_modified, _del_if_modified)

    @property
    def if_modified__exists(self):
        return 7 in self._mods or self._buf_exists(7)

    @property
    def if_modified__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_if_modified(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(7)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(7)

    _pbf_finalizers.append(_finalize_if_modified)


    def _get_head(self):
        if 8 in self._cache:
            r = self._cache[8]
        else:
            r = self._buf_get(8, ProtoBase.TYPE_bool, 'head')
            self._cache[8] = r
        return r

    def _establish_parentage_head(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_head), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_head
                v._pbf_establish_parent_callback = self._establish_parentage_head

    def _set_head(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_head(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field head"
            raise ProtoValueError(list_assign_error)
        self._cache[8] = v
        self._mods[8] = ProtoBase.TYPE_bool

    def _mod_head(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[8] = ProtoBase.TYPE_bool

    def _del_head(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 8 in self._cache:
            del self._cache[8]
        if 8 in self._mods:
            del self._mods[8]
        self._buf_del(8)

    _pb_field_name_8 = "head"

    head = property(_get_head, _set_head, _del_head)

    @property
    def head__exists(self):
        return 8 in self._mods or self._buf_exists(8)

    @property
    def head__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_head(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(8)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(8)

    _pbf_finalizers.append(_finalize_head)


    def _get_deletedvclock(self):
        if 9 in self._cache:
            r = self._cache[9]
        else:
            r = self._buf_get(9, ProtoBase.TYPE_bool, 'deletedvclock')
            self._cache[9] = r
        return r

    def _establish_parentage_deletedvclock(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_deletedvclock), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_deletedvclock
                v._pbf_establish_parent_callback = self._establish_parentage_deletedvclock

    def _set_deletedvclock(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_deletedvclock(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field deletedvclock"
            raise ProtoValueError(list_assign_error)
        self._cache[9] = v
        self._mods[9] = ProtoBase.TYPE_bool

    def _mod_deletedvclock(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[9] = ProtoBase.TYPE_bool

    def _del_deletedvclock(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 9 in self._cache:
            del self._cache[9]
        if 9 in self._mods:
            del self._mods[9]
        self._buf_del(9)

    _pb_field_name_9 = "deletedvclock"

    deletedvclock = property(_get_deletedvclock, _set_deletedvclock, _del_deletedvclock)

    @property
    def deletedvclock__exists(self):
        return 9 in self._mods or self._buf_exists(9)

    @property
    def deletedvclock__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_deletedvclock(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(9)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(9)

    _pbf_finalizers.append(_finalize_deletedvclock)


TYPE_RpbGetReq = RpbGetReq
_PB_finalizers.append('RpbGetReq')

class RpbGetResp(ProtoBase):
    _required = []
    _field_map = {'content': 1, 'vclock': 2, 'unchanged': 3}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['content', 'vclock', 'unchanged']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    class Repeated_content(RepeatedSequence):
        class pb_subtype(object):
            def __get__(self, instance, cls):
                return TYPE_RpbContent
        pb_subtype = pb_subtype()


    TYPE_Repeated_content = Repeated_content


    @property
    def content__stream(self):
        if 1 in self._cache:
            def acc(v):
                v_ = lambda: v
                return v_
            return [acc(v) for v in self._cache[1]]
        return self._get_repeated(1, self.TYPE_Repeated_content, "content", lazy=True)

    def _get_content(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, self.TYPE_Repeated_content, 'content')
            self._cache[1] = r
        return r

    def _establish_parentage_content(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_content), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_content
                v._pbf_establish_parent_callback = self._establish_parentage_content

    def _set_content(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_content(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field content"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = self.TYPE_Repeated_content

    def _mod_content(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = self.TYPE_Repeated_content

    def _del_content(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "content"

    content = property(_get_content, _set_content, _del_content)

    @property
    def content__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def content__type(self):
        return self.TYPE_Repeated_content

    def _finalize_content(cls):
        if is_string(cls.TYPE_Repeated_content):
            cls._pbf_strings.append(1)
        elif _PB_type(cls.TYPE_Repeated_content) is _PB_type:
            assert issubclass(cls.TYPE_Repeated_content, RepeatedSequence)
            if is_string(cls.TYPE_Repeated_content.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_content)


    def _get_vclock(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'vclock')
            self._cache[2] = r
        return r

    def _establish_parentage_vclock(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_vclock), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_vclock
                v._pbf_establish_parent_callback = self._establish_parentage_vclock

    def _set_vclock(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_vclock(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field vclock"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_vclock(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_vclock(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "vclock"

    vclock = property(_get_vclock, _set_vclock, _del_vclock)

    @property
    def vclock__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def vclock__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_vclock(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_vclock)


    def _get_unchanged(self):
        if 3 in self._cache:
            r = self._cache[3]
        else:
            r = self._buf_get(3, ProtoBase.TYPE_bool, 'unchanged')
            self._cache[3] = r
        return r

    def _establish_parentage_unchanged(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_unchanged), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_unchanged
                v._pbf_establish_parent_callback = self._establish_parentage_unchanged

    def _set_unchanged(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_unchanged(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field unchanged"
            raise ProtoValueError(list_assign_error)
        self._cache[3] = v
        self._mods[3] = ProtoBase.TYPE_bool

    def _mod_unchanged(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[3] = ProtoBase.TYPE_bool

    def _del_unchanged(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 3 in self._cache:
            del self._cache[3]
        if 3 in self._mods:
            del self._mods[3]
        self._buf_del(3)

    _pb_field_name_3 = "unchanged"

    unchanged = property(_get_unchanged, _set_unchanged, _del_unchanged)

    @property
    def unchanged__exists(self):
        return 3 in self._mods or self._buf_exists(3)

    @property
    def unchanged__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_unchanged(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(3)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(3)

    _pbf_finalizers.append(_finalize_unchanged)


TYPE_RpbGetResp = RpbGetResp
_PB_finalizers.append('RpbGetResp')

class RpbPutReq(ProtoBase):
    _required = [1, 4]
    _field_map = {'return_head': 11, 'vclock': 3, 'key': 2, 'if_not_modified': 9, 'bucket': 1, 'content': 4, 'w': 5, 'if_none_match': 10, 'dw': 6, 'return_body': 7, 'pw': 8}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['bucket', 'key', 'vclock', 'content', 'w', 'dw', 'return_body', 'pw', 'if_not_modified', 'if_none_match', 'return_head']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_bucket(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'bucket')
            self._cache[1] = r
        return r

    def _establish_parentage_bucket(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_bucket), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_bucket
                v._pbf_establish_parent_callback = self._establish_parentage_bucket

    def _set_bucket(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_bucket(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field bucket"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "bucket"

    bucket = property(_get_bucket, _set_bucket, _del_bucket)

    @property
    def bucket__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def bucket__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_bucket(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_bucket)


    def _get_key(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'key')
            self._cache[2] = r
        return r

    def _establish_parentage_key(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_key), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_key
                v._pbf_establish_parent_callback = self._establish_parentage_key

    def _set_key(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_key(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field key"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "key"

    key = property(_get_key, _set_key, _del_key)

    @property
    def key__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def key__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_key(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_key)


    def _get_vclock(self):
        if 3 in self._cache:
            r = self._cache[3]
        else:
            r = self._buf_get(3, ProtoBase.TYPE_bytes, 'vclock')
            self._cache[3] = r
        return r

    def _establish_parentage_vclock(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_vclock), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_vclock
                v._pbf_establish_parent_callback = self._establish_parentage_vclock

    def _set_vclock(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_vclock(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field vclock"
            raise ProtoValueError(list_assign_error)
        self._cache[3] = v
        self._mods[3] = ProtoBase.TYPE_bytes

    def _mod_vclock(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[3] = ProtoBase.TYPE_bytes

    def _del_vclock(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 3 in self._cache:
            del self._cache[3]
        if 3 in self._mods:
            del self._mods[3]
        self._buf_del(3)

    _pb_field_name_3 = "vclock"

    vclock = property(_get_vclock, _set_vclock, _del_vclock)

    @property
    def vclock__exists(self):
        return 3 in self._mods or self._buf_exists(3)

    @property
    def vclock__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_vclock(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(3)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(3)

    _pbf_finalizers.append(_finalize_vclock)


    def _get_content(self):
        if 4 in self._cache:
            r = self._cache[4]
        else:
            r = self._buf_get(4, TYPE_RpbContent, 'content')
            self._cache[4] = r
        return r

    def _establish_parentage_content(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_content), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_content
                v._pbf_establish_parent_callback = self._establish_parentage_content

    def _set_content(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_content(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field content"
            raise ProtoValueError(list_assign_error)
        self._cache[4] = v
        self._mods[4] = TYPE_RpbContent

    def _mod_content(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[4] = TYPE_RpbContent

    def _del_content(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 4 in self._cache:
            del self._cache[4]
        if 4 in self._mods:
            del self._mods[4]
        self._buf_del(4)

    _pb_field_name_4 = "content"

    content = property(_get_content, _set_content, _del_content)

    @property
    def content__exists(self):
        return 4 in self._mods or self._buf_exists(4)

    @property
    def content__type(self):
        return TYPE_RpbContent

    def _finalize_content(cls):
        if is_string(TYPE_RpbContent):
            cls._pbf_strings.append(4)
        elif _PB_type(TYPE_RpbContent) is _PB_type:
            assert issubclass(TYPE_RpbContent, RepeatedSequence)
            if is_string(TYPE_RpbContent.pb_subtype):
                cls._pbf_strings.append(4)

    _pbf_finalizers.append(_finalize_content)


    def _get_w(self):
        if 5 in self._cache:
            r = self._cache[5]
        else:
            r = self._buf_get(5, ProtoBase.TYPE_uint32, 'w')
            self._cache[5] = r
        return r

    def _establish_parentage_w(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_w), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_w
                v._pbf_establish_parent_callback = self._establish_parentage_w

    def _set_w(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_w(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field w"
            raise ProtoValueError(list_assign_error)
        self._cache[5] = v
        self._mods[5] = ProtoBase.TYPE_uint32

    def _mod_w(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[5] = ProtoBase.TYPE_uint32

    def _del_w(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 5 in self._cache:
            del self._cache[5]
        if 5 in self._mods:
            del self._mods[5]
        self._buf_del(5)

    _pb_field_name_5 = "w"

    w = property(_get_w, _set_w, _del_w)

    @property
    def w__exists(self):
        return 5 in self._mods or self._buf_exists(5)

    @property
    def w__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_w(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(5)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(5)

    _pbf_finalizers.append(_finalize_w)


    def _get_dw(self):
        if 6 in self._cache:
            r = self._cache[6]
        else:
            r = self._buf_get(6, ProtoBase.TYPE_uint32, 'dw')
            self._cache[6] = r
        return r

    def _establish_parentage_dw(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_dw), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_dw
                v._pbf_establish_parent_callback = self._establish_parentage_dw

    def _set_dw(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_dw(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field dw"
            raise ProtoValueError(list_assign_error)
        self._cache[6] = v
        self._mods[6] = ProtoBase.TYPE_uint32

    def _mod_dw(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[6] = ProtoBase.TYPE_uint32

    def _del_dw(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 6 in self._cache:
            del self._cache[6]
        if 6 in self._mods:
            del self._mods[6]
        self._buf_del(6)

    _pb_field_name_6 = "dw"

    dw = property(_get_dw, _set_dw, _del_dw)

    @property
    def dw__exists(self):
        return 6 in self._mods or self._buf_exists(6)

    @property
    def dw__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_dw(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(6)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(6)

    _pbf_finalizers.append(_finalize_dw)


    def _get_return_body(self):
        if 7 in self._cache:
            r = self._cache[7]
        else:
            r = self._buf_get(7, ProtoBase.TYPE_bool, 'return_body')
            self._cache[7] = r
        return r

    def _establish_parentage_return_body(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_return_body), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_return_body
                v._pbf_establish_parent_callback = self._establish_parentage_return_body

    def _set_return_body(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_return_body(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field return_body"
            raise ProtoValueError(list_assign_error)
        self._cache[7] = v
        self._mods[7] = ProtoBase.TYPE_bool

    def _mod_return_body(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[7] = ProtoBase.TYPE_bool

    def _del_return_body(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 7 in self._cache:
            del self._cache[7]
        if 7 in self._mods:
            del self._mods[7]
        self._buf_del(7)

    _pb_field_name_7 = "return_body"

    return_body = property(_get_return_body, _set_return_body, _del_return_body)

    @property
    def return_body__exists(self):
        return 7 in self._mods or self._buf_exists(7)

    @property
    def return_body__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_return_body(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(7)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(7)

    _pbf_finalizers.append(_finalize_return_body)


    def _get_pw(self):
        if 8 in self._cache:
            r = self._cache[8]
        else:
            r = self._buf_get(8, ProtoBase.TYPE_uint32, 'pw')
            self._cache[8] = r
        return r

    def _establish_parentage_pw(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_pw), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_pw
                v._pbf_establish_parent_callback = self._establish_parentage_pw

    def _set_pw(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_pw(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field pw"
            raise ProtoValueError(list_assign_error)
        self._cache[8] = v
        self._mods[8] = ProtoBase.TYPE_uint32

    def _mod_pw(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[8] = ProtoBase.TYPE_uint32

    def _del_pw(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 8 in self._cache:
            del self._cache[8]
        if 8 in self._mods:
            del self._mods[8]
        self._buf_del(8)

    _pb_field_name_8 = "pw"

    pw = property(_get_pw, _set_pw, _del_pw)

    @property
    def pw__exists(self):
        return 8 in self._mods or self._buf_exists(8)

    @property
    def pw__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_pw(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(8)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(8)

    _pbf_finalizers.append(_finalize_pw)


    def _get_if_not_modified(self):
        if 9 in self._cache:
            r = self._cache[9]
        else:
            r = self._buf_get(9, ProtoBase.TYPE_bool, 'if_not_modified')
            self._cache[9] = r
        return r

    def _establish_parentage_if_not_modified(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_if_not_modified), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_if_not_modified
                v._pbf_establish_parent_callback = self._establish_parentage_if_not_modified

    def _set_if_not_modified(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_if_not_modified(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field if_not_modified"
            raise ProtoValueError(list_assign_error)
        self._cache[9] = v
        self._mods[9] = ProtoBase.TYPE_bool

    def _mod_if_not_modified(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[9] = ProtoBase.TYPE_bool

    def _del_if_not_modified(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 9 in self._cache:
            del self._cache[9]
        if 9 in self._mods:
            del self._mods[9]
        self._buf_del(9)

    _pb_field_name_9 = "if_not_modified"

    if_not_modified = property(_get_if_not_modified, _set_if_not_modified, _del_if_not_modified)

    @property
    def if_not_modified__exists(self):
        return 9 in self._mods or self._buf_exists(9)

    @property
    def if_not_modified__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_if_not_modified(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(9)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(9)

    _pbf_finalizers.append(_finalize_if_not_modified)


    def _get_if_none_match(self):
        if 10 in self._cache:
            r = self._cache[10]
        else:
            r = self._buf_get(10, ProtoBase.TYPE_bool, 'if_none_match')
            self._cache[10] = r
        return r

    def _establish_parentage_if_none_match(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_if_none_match), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_if_none_match
                v._pbf_establish_parent_callback = self._establish_parentage_if_none_match

    def _set_if_none_match(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_if_none_match(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field if_none_match"
            raise ProtoValueError(list_assign_error)
        self._cache[10] = v
        self._mods[10] = ProtoBase.TYPE_bool

    def _mod_if_none_match(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[10] = ProtoBase.TYPE_bool

    def _del_if_none_match(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 10 in self._cache:
            del self._cache[10]
        if 10 in self._mods:
            del self._mods[10]
        self._buf_del(10)

    _pb_field_name_10 = "if_none_match"

    if_none_match = property(_get_if_none_match, _set_if_none_match, _del_if_none_match)

    @property
    def if_none_match__exists(self):
        return 10 in self._mods or self._buf_exists(10)

    @property
    def if_none_match__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_if_none_match(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(10)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(10)

    _pbf_finalizers.append(_finalize_if_none_match)


    def _get_return_head(self):
        if 11 in self._cache:
            r = self._cache[11]
        else:
            r = self._buf_get(11, ProtoBase.TYPE_bool, 'return_head')
            self._cache[11] = r
        return r

    def _establish_parentage_return_head(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_return_head), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_return_head
                v._pbf_establish_parent_callback = self._establish_parentage_return_head

    def _set_return_head(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_return_head(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field return_head"
            raise ProtoValueError(list_assign_error)
        self._cache[11] = v
        self._mods[11] = ProtoBase.TYPE_bool

    def _mod_return_head(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[11] = ProtoBase.TYPE_bool

    def _del_return_head(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 11 in self._cache:
            del self._cache[11]
        if 11 in self._mods:
            del self._mods[11]
        self._buf_del(11)

    _pb_field_name_11 = "return_head"

    return_head = property(_get_return_head, _set_return_head, _del_return_head)

    @property
    def return_head__exists(self):
        return 11 in self._mods or self._buf_exists(11)

    @property
    def return_head__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_return_head(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(11)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(11)

    _pbf_finalizers.append(_finalize_return_head)


TYPE_RpbPutReq = RpbPutReq
_PB_finalizers.append('RpbPutReq')

class RpbPutResp(ProtoBase):
    _required = []
    _field_map = {'content': 1, 'vclock': 2, 'key': 3}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['content', 'vclock', 'key']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    class Repeated_content(RepeatedSequence):
        class pb_subtype(object):
            def __get__(self, instance, cls):
                return TYPE_RpbContent
        pb_subtype = pb_subtype()


    TYPE_Repeated_content = Repeated_content


    @property
    def content__stream(self):
        if 1 in self._cache:
            def acc(v):
                v_ = lambda: v
                return v_
            return [acc(v) for v in self._cache[1]]
        return self._get_repeated(1, self.TYPE_Repeated_content, "content", lazy=True)

    def _get_content(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, self.TYPE_Repeated_content, 'content')
            self._cache[1] = r
        return r

    def _establish_parentage_content(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_content), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_content
                v._pbf_establish_parent_callback = self._establish_parentage_content

    def _set_content(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_content(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field content"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = self.TYPE_Repeated_content

    def _mod_content(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = self.TYPE_Repeated_content

    def _del_content(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "content"

    content = property(_get_content, _set_content, _del_content)

    @property
    def content__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def content__type(self):
        return self.TYPE_Repeated_content

    def _finalize_content(cls):
        if is_string(cls.TYPE_Repeated_content):
            cls._pbf_strings.append(1)
        elif _PB_type(cls.TYPE_Repeated_content) is _PB_type:
            assert issubclass(cls.TYPE_Repeated_content, RepeatedSequence)
            if is_string(cls.TYPE_Repeated_content.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_content)


    def _get_vclock(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'vclock')
            self._cache[2] = r
        return r

    def _establish_parentage_vclock(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_vclock), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_vclock
                v._pbf_establish_parent_callback = self._establish_parentage_vclock

    def _set_vclock(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_vclock(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field vclock"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_vclock(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_vclock(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "vclock"

    vclock = property(_get_vclock, _set_vclock, _del_vclock)

    @property
    def vclock__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def vclock__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_vclock(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_vclock)


    def _get_key(self):
        if 3 in self._cache:
            r = self._cache[3]
        else:
            r = self._buf_get(3, ProtoBase.TYPE_bytes, 'key')
            self._cache[3] = r
        return r

    def _establish_parentage_key(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_key), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_key
                v._pbf_establish_parent_callback = self._establish_parentage_key

    def _set_key(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_key(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field key"
            raise ProtoValueError(list_assign_error)
        self._cache[3] = v
        self._mods[3] = ProtoBase.TYPE_bytes

    def _mod_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[3] = ProtoBase.TYPE_bytes

    def _del_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 3 in self._cache:
            del self._cache[3]
        if 3 in self._mods:
            del self._mods[3]
        self._buf_del(3)

    _pb_field_name_3 = "key"

    key = property(_get_key, _set_key, _del_key)

    @property
    def key__exists(self):
        return 3 in self._mods or self._buf_exists(3)

    @property
    def key__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_key(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(3)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(3)

    _pbf_finalizers.append(_finalize_key)


TYPE_RpbPutResp = RpbPutResp
_PB_finalizers.append('RpbPutResp')

class RpbDelReq(ProtoBase):
    _required = [1, 2]
    _field_map = {'pr': 7, 'vclock': 4, 'rw': 3, 'key': 2, 'bucket': 1, 'r': 5, 'w': 6, 'dw': 9, 'pw': 8}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['bucket', 'key', 'rw', 'vclock', 'r', 'w', 'pr', 'pw', 'dw']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_bucket(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'bucket')
            self._cache[1] = r
        return r

    def _establish_parentage_bucket(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_bucket), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_bucket
                v._pbf_establish_parent_callback = self._establish_parentage_bucket

    def _set_bucket(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_bucket(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field bucket"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "bucket"

    bucket = property(_get_bucket, _set_bucket, _del_bucket)

    @property
    def bucket__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def bucket__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_bucket(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_bucket)


    def _get_key(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'key')
            self._cache[2] = r
        return r

    def _establish_parentage_key(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_key), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_key
                v._pbf_establish_parent_callback = self._establish_parentage_key

    def _set_key(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_key(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field key"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "key"

    key = property(_get_key, _set_key, _del_key)

    @property
    def key__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def key__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_key(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_key)


    def _get_rw(self):
        if 3 in self._cache:
            r = self._cache[3]
        else:
            r = self._buf_get(3, ProtoBase.TYPE_uint32, 'rw')
            self._cache[3] = r
        return r

    def _establish_parentage_rw(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_rw), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_rw
                v._pbf_establish_parent_callback = self._establish_parentage_rw

    def _set_rw(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_rw(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field rw"
            raise ProtoValueError(list_assign_error)
        self._cache[3] = v
        self._mods[3] = ProtoBase.TYPE_uint32

    def _mod_rw(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[3] = ProtoBase.TYPE_uint32

    def _del_rw(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 3 in self._cache:
            del self._cache[3]
        if 3 in self._mods:
            del self._mods[3]
        self._buf_del(3)

    _pb_field_name_3 = "rw"

    rw = property(_get_rw, _set_rw, _del_rw)

    @property
    def rw__exists(self):
        return 3 in self._mods or self._buf_exists(3)

    @property
    def rw__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_rw(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(3)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(3)

    _pbf_finalizers.append(_finalize_rw)


    def _get_vclock(self):
        if 4 in self._cache:
            r = self._cache[4]
        else:
            r = self._buf_get(4, ProtoBase.TYPE_bytes, 'vclock')
            self._cache[4] = r
        return r

    def _establish_parentage_vclock(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_vclock), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_vclock
                v._pbf_establish_parent_callback = self._establish_parentage_vclock

    def _set_vclock(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_vclock(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field vclock"
            raise ProtoValueError(list_assign_error)
        self._cache[4] = v
        self._mods[4] = ProtoBase.TYPE_bytes

    def _mod_vclock(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[4] = ProtoBase.TYPE_bytes

    def _del_vclock(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 4 in self._cache:
            del self._cache[4]
        if 4 in self._mods:
            del self._mods[4]
        self._buf_del(4)

    _pb_field_name_4 = "vclock"

    vclock = property(_get_vclock, _set_vclock, _del_vclock)

    @property
    def vclock__exists(self):
        return 4 in self._mods or self._buf_exists(4)

    @property
    def vclock__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_vclock(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(4)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(4)

    _pbf_finalizers.append(_finalize_vclock)


    def _get_r(self):
        if 5 in self._cache:
            r = self._cache[5]
        else:
            r = self._buf_get(5, ProtoBase.TYPE_uint32, 'r')
            self._cache[5] = r
        return r

    def _establish_parentage_r(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_r), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_r
                v._pbf_establish_parent_callback = self._establish_parentage_r

    def _set_r(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_r(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field r"
            raise ProtoValueError(list_assign_error)
        self._cache[5] = v
        self._mods[5] = ProtoBase.TYPE_uint32

    def _mod_r(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[5] = ProtoBase.TYPE_uint32

    def _del_r(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 5 in self._cache:
            del self._cache[5]
        if 5 in self._mods:
            del self._mods[5]
        self._buf_del(5)

    _pb_field_name_5 = "r"

    r = property(_get_r, _set_r, _del_r)

    @property
    def r__exists(self):
        return 5 in self._mods or self._buf_exists(5)

    @property
    def r__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_r(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(5)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(5)

    _pbf_finalizers.append(_finalize_r)


    def _get_w(self):
        if 6 in self._cache:
            r = self._cache[6]
        else:
            r = self._buf_get(6, ProtoBase.TYPE_uint32, 'w')
            self._cache[6] = r
        return r

    def _establish_parentage_w(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_w), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_w
                v._pbf_establish_parent_callback = self._establish_parentage_w

    def _set_w(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_w(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field w"
            raise ProtoValueError(list_assign_error)
        self._cache[6] = v
        self._mods[6] = ProtoBase.TYPE_uint32

    def _mod_w(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[6] = ProtoBase.TYPE_uint32

    def _del_w(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 6 in self._cache:
            del self._cache[6]
        if 6 in self._mods:
            del self._mods[6]
        self._buf_del(6)

    _pb_field_name_6 = "w"

    w = property(_get_w, _set_w, _del_w)

    @property
    def w__exists(self):
        return 6 in self._mods or self._buf_exists(6)

    @property
    def w__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_w(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(6)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(6)

    _pbf_finalizers.append(_finalize_w)


    def _get_pr(self):
        if 7 in self._cache:
            r = self._cache[7]
        else:
            r = self._buf_get(7, ProtoBase.TYPE_uint32, 'pr')
            self._cache[7] = r
        return r

    def _establish_parentage_pr(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_pr), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_pr
                v._pbf_establish_parent_callback = self._establish_parentage_pr

    def _set_pr(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_pr(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field pr"
            raise ProtoValueError(list_assign_error)
        self._cache[7] = v
        self._mods[7] = ProtoBase.TYPE_uint32

    def _mod_pr(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[7] = ProtoBase.TYPE_uint32

    def _del_pr(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 7 in self._cache:
            del self._cache[7]
        if 7 in self._mods:
            del self._mods[7]
        self._buf_del(7)

    _pb_field_name_7 = "pr"

    pr = property(_get_pr, _set_pr, _del_pr)

    @property
    def pr__exists(self):
        return 7 in self._mods or self._buf_exists(7)

    @property
    def pr__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_pr(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(7)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(7)

    _pbf_finalizers.append(_finalize_pr)


    def _get_pw(self):
        if 8 in self._cache:
            r = self._cache[8]
        else:
            r = self._buf_get(8, ProtoBase.TYPE_uint32, 'pw')
            self._cache[8] = r
        return r

    def _establish_parentage_pw(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_pw), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_pw
                v._pbf_establish_parent_callback = self._establish_parentage_pw

    def _set_pw(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_pw(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field pw"
            raise ProtoValueError(list_assign_error)
        self._cache[8] = v
        self._mods[8] = ProtoBase.TYPE_uint32

    def _mod_pw(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[8] = ProtoBase.TYPE_uint32

    def _del_pw(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 8 in self._cache:
            del self._cache[8]
        if 8 in self._mods:
            del self._mods[8]
        self._buf_del(8)

    _pb_field_name_8 = "pw"

    pw = property(_get_pw, _set_pw, _del_pw)

    @property
    def pw__exists(self):
        return 8 in self._mods or self._buf_exists(8)

    @property
    def pw__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_pw(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(8)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(8)

    _pbf_finalizers.append(_finalize_pw)


    def _get_dw(self):
        if 9 in self._cache:
            r = self._cache[9]
        else:
            r = self._buf_get(9, ProtoBase.TYPE_uint32, 'dw')
            self._cache[9] = r
        return r

    def _establish_parentage_dw(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_dw), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_dw
                v._pbf_establish_parent_callback = self._establish_parentage_dw

    def _set_dw(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_dw(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field dw"
            raise ProtoValueError(list_assign_error)
        self._cache[9] = v
        self._mods[9] = ProtoBase.TYPE_uint32

    def _mod_dw(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[9] = ProtoBase.TYPE_uint32

    def _del_dw(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 9 in self._cache:
            del self._cache[9]
        if 9 in self._mods:
            del self._mods[9]
        self._buf_del(9)

    _pb_field_name_9 = "dw"

    dw = property(_get_dw, _set_dw, _del_dw)

    @property
    def dw__exists(self):
        return 9 in self._mods or self._buf_exists(9)

    @property
    def dw__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_dw(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(9)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(9)

    _pbf_finalizers.append(_finalize_dw)


TYPE_RpbDelReq = RpbDelReq
_PB_finalizers.append('RpbDelReq')

class RpbListBucketsResp(ProtoBase):
    _required = []
    _field_map = {'buckets': 1}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['buckets']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    class Repeated_buckets(RepeatedSequence):
        class pb_subtype(object):
            def __get__(self, instance, cls):
                return ProtoBase.TYPE_bytes
        pb_subtype = pb_subtype()


    TYPE_Repeated_buckets = Repeated_buckets


    def _get_buckets(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, self.TYPE_Repeated_buckets, 'buckets')
            self._cache[1] = r
        return r

    def _establish_parentage_buckets(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_buckets), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_buckets
                v._pbf_establish_parent_callback = self._establish_parentage_buckets

    def _set_buckets(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_buckets(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field buckets"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = self.TYPE_Repeated_buckets

    def _mod_buckets(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = self.TYPE_Repeated_buckets

    def _del_buckets(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "buckets"

    buckets = property(_get_buckets, _set_buckets, _del_buckets)

    @property
    def buckets__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def buckets__type(self):
        return self.TYPE_Repeated_buckets

    def _finalize_buckets(cls):
        if is_string(cls.TYPE_Repeated_buckets):
            cls._pbf_strings.append(1)
        elif _PB_type(cls.TYPE_Repeated_buckets) is _PB_type:
            assert issubclass(cls.TYPE_Repeated_buckets, RepeatedSequence)
            if is_string(cls.TYPE_Repeated_buckets.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_buckets)


TYPE_RpbListBucketsResp = RpbListBucketsResp
_PB_finalizers.append('RpbListBucketsResp')

class RpbListKeysReq(ProtoBase):
    _required = [1]
    _field_map = {'bucket': 1}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['bucket']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_bucket(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'bucket')
            self._cache[1] = r
        return r

    def _establish_parentage_bucket(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_bucket), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_bucket
                v._pbf_establish_parent_callback = self._establish_parentage_bucket

    def _set_bucket(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_bucket(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field bucket"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "bucket"

    bucket = property(_get_bucket, _set_bucket, _del_bucket)

    @property
    def bucket__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def bucket__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_bucket(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_bucket)


TYPE_RpbListKeysReq = RpbListKeysReq
_PB_finalizers.append('RpbListKeysReq')

class RpbListKeysResp(ProtoBase):
    _required = []
    _field_map = {'keys': 1, 'done': 2}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['keys', 'done']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    class Repeated_keys(RepeatedSequence):
        class pb_subtype(object):
            def __get__(self, instance, cls):
                return ProtoBase.TYPE_bytes
        pb_subtype = pb_subtype()


    TYPE_Repeated_keys = Repeated_keys


    def _get_keys(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, self.TYPE_Repeated_keys, 'keys')
            self._cache[1] = r
        return r

    def _establish_parentage_keys(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_keys), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_keys
                v._pbf_establish_parent_callback = self._establish_parentage_keys

    def _set_keys(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_keys(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field keys"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = self.TYPE_Repeated_keys

    def _mod_keys(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = self.TYPE_Repeated_keys

    def _del_keys(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "keys"

    keys = property(_get_keys, _set_keys, _del_keys)

    @property
    def keys__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def keys__type(self):
        return self.TYPE_Repeated_keys

    def _finalize_keys(cls):
        if is_string(cls.TYPE_Repeated_keys):
            cls._pbf_strings.append(1)
        elif _PB_type(cls.TYPE_Repeated_keys) is _PB_type:
            assert issubclass(cls.TYPE_Repeated_keys, RepeatedSequence)
            if is_string(cls.TYPE_Repeated_keys.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_keys)


    def _get_done(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bool, 'done')
            self._cache[2] = r
        return r

    def _establish_parentage_done(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_done), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_done
                v._pbf_establish_parent_callback = self._establish_parentage_done

    def _set_done(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_done(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field done"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bool

    def _mod_done(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bool

    def _del_done(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "done"

    done = property(_get_done, _set_done, _del_done)

    @property
    def done__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def done__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_done(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_done)


TYPE_RpbListKeysResp = RpbListKeysResp
_PB_finalizers.append('RpbListKeysResp')

class RpbGetBucketReq(ProtoBase):
    _required = [1]
    _field_map = {'bucket': 1}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['bucket']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_bucket(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'bucket')
            self._cache[1] = r
        return r

    def _establish_parentage_bucket(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_bucket), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_bucket
                v._pbf_establish_parent_callback = self._establish_parentage_bucket

    def _set_bucket(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_bucket(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field bucket"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "bucket"

    bucket = property(_get_bucket, _set_bucket, _del_bucket)

    @property
    def bucket__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def bucket__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_bucket(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_bucket)


TYPE_RpbGetBucketReq = RpbGetBucketReq
_PB_finalizers.append('RpbGetBucketReq')

class RpbGetBucketResp(ProtoBase):
    _required = [1]
    _field_map = {'props': 1}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['props']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_props(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, TYPE_RpbBucketProps, 'props')
            self._cache[1] = r
        return r

    def _establish_parentage_props(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_props), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_props
                v._pbf_establish_parent_callback = self._establish_parentage_props

    def _set_props(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_props(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field props"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = TYPE_RpbBucketProps

    def _mod_props(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = TYPE_RpbBucketProps

    def _del_props(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "props"

    props = property(_get_props, _set_props, _del_props)

    @property
    def props__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def props__type(self):
        return TYPE_RpbBucketProps

    def _finalize_props(cls):
        if is_string(TYPE_RpbBucketProps):
            cls._pbf_strings.append(1)
        elif _PB_type(TYPE_RpbBucketProps) is _PB_type:
            assert issubclass(TYPE_RpbBucketProps, RepeatedSequence)
            if is_string(TYPE_RpbBucketProps.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_props)


TYPE_RpbGetBucketResp = RpbGetBucketResp
_PB_finalizers.append('RpbGetBucketResp')

class RpbSetBucketReq(ProtoBase):
    _required = [1, 2]
    _field_map = {'bucket': 1, 'props': 2}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['bucket', 'props']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_bucket(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'bucket')
            self._cache[1] = r
        return r

    def _establish_parentage_bucket(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_bucket), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_bucket
                v._pbf_establish_parent_callback = self._establish_parentage_bucket

    def _set_bucket(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_bucket(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field bucket"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "bucket"

    bucket = property(_get_bucket, _set_bucket, _del_bucket)

    @property
    def bucket__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def bucket__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_bucket(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_bucket)


    def _get_props(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, TYPE_RpbBucketProps, 'props')
            self._cache[2] = r
        return r

    def _establish_parentage_props(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_props), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_props
                v._pbf_establish_parent_callback = self._establish_parentage_props

    def _set_props(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_props(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field props"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = TYPE_RpbBucketProps

    def _mod_props(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = TYPE_RpbBucketProps

    def _del_props(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "props"

    props = property(_get_props, _set_props, _del_props)

    @property
    def props__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def props__type(self):
        return TYPE_RpbBucketProps

    def _finalize_props(cls):
        if is_string(TYPE_RpbBucketProps):
            cls._pbf_strings.append(2)
        elif _PB_type(TYPE_RpbBucketProps) is _PB_type:
            assert issubclass(TYPE_RpbBucketProps, RepeatedSequence)
            if is_string(TYPE_RpbBucketProps.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_props)


TYPE_RpbSetBucketReq = RpbSetBucketReq
_PB_finalizers.append('RpbSetBucketReq')

class RpbMapRedReq(ProtoBase):
    _required = [1, 2]
    _field_map = {'request': 1, 'content_type': 2}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['request', 'content_type']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_request(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'request')
            self._cache[1] = r
        return r

    def _establish_parentage_request(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_request), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_request
                v._pbf_establish_parent_callback = self._establish_parentage_request

    def _set_request(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_request(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field request"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_request(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_request(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "request"

    request = property(_get_request, _set_request, _del_request)

    @property
    def request__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def request__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_request(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_request)


    def _get_content_type(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'content_type')
            self._cache[2] = r
        return r

    def _establish_parentage_content_type(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_content_type), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_content_type
                v._pbf_establish_parent_callback = self._establish_parentage_content_type

    def _set_content_type(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_content_type(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field content_type"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_content_type(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_content_type(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "content_type"

    content_type = property(_get_content_type, _set_content_type, _del_content_type)

    @property
    def content_type__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def content_type__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_content_type(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_content_type)


TYPE_RpbMapRedReq = RpbMapRedReq
_PB_finalizers.append('RpbMapRedReq')

class RpbMapRedResp(ProtoBase):
    _required = []
    _field_map = {'phase': 1, 'done': 3, 'response': 2}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['phase', 'response', 'done']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_phase(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_uint32, 'phase')
            self._cache[1] = r
        return r

    def _establish_parentage_phase(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_phase), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_phase
                v._pbf_establish_parent_callback = self._establish_parentage_phase

    def _set_phase(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_phase(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field phase"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_uint32

    def _mod_phase(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_uint32

    def _del_phase(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "phase"

    phase = property(_get_phase, _set_phase, _del_phase)

    @property
    def phase__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def phase__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_phase(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_phase)


    def _get_response(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'response')
            self._cache[2] = r
        return r

    def _establish_parentage_response(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_response), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_response
                v._pbf_establish_parent_callback = self._establish_parentage_response

    def _set_response(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_response(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field response"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_response(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_response(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "response"

    response = property(_get_response, _set_response, _del_response)

    @property
    def response__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def response__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_response(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_response)


    def _get_done(self):
        if 3 in self._cache:
            r = self._cache[3]
        else:
            r = self._buf_get(3, ProtoBase.TYPE_bool, 'done')
            self._cache[3] = r
        return r

    def _establish_parentage_done(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_done), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_done
                v._pbf_establish_parent_callback = self._establish_parentage_done

    def _set_done(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_done(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field done"
            raise ProtoValueError(list_assign_error)
        self._cache[3] = v
        self._mods[3] = ProtoBase.TYPE_bool

    def _mod_done(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[3] = ProtoBase.TYPE_bool

    def _del_done(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 3 in self._cache:
            del self._cache[3]
        if 3 in self._mods:
            del self._mods[3]
        self._buf_del(3)

    _pb_field_name_3 = "done"

    done = property(_get_done, _set_done, _del_done)

    @property
    def done__exists(self):
        return 3 in self._mods or self._buf_exists(3)

    @property
    def done__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_done(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(3)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(3)

    _pbf_finalizers.append(_finalize_done)


TYPE_RpbMapRedResp = RpbMapRedResp
_PB_finalizers.append('RpbMapRedResp')

class RpbIndexReq(ProtoBase):
    _required = [1, 2, 3]
    _field_map = {'index': 2, 'range_min': 5, 'range_max': 6, 'bucket': 1, 'key': 4, 'qtype': 3}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['bucket', 'index', 'qtype', 'key', 'range_min', 'range_max']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))
    
    # Enumeration: IndexQueryType
        
    eq = 0
        
    range = 1
        
    TYPE_IndexQueryType = ProtoBase.TYPE_int32
        
    _IndexQueryType__map = {1: 'range', 0: 'eq'}
        
    @classmethod
    def get_IndexQueryType_name(cls, v):
        return cls._IndexQueryType__map[v]
    
    def _get_bucket(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'bucket')
            self._cache[1] = r
        return r

    def _establish_parentage_bucket(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_bucket), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_bucket
                v._pbf_establish_parent_callback = self._establish_parentage_bucket

    def _set_bucket(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_bucket(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field bucket"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "bucket"

    bucket = property(_get_bucket, _set_bucket, _del_bucket)

    @property
    def bucket__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def bucket__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_bucket(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_bucket)


    def _get_index(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'index')
            self._cache[2] = r
        return r

    def _establish_parentage_index(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_index), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_index
                v._pbf_establish_parent_callback = self._establish_parentage_index

    def _set_index(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_index(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field index"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_index(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_index(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "index"

    index = property(_get_index, _set_index, _del_index)

    @property
    def index__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def index__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_index(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_index)


    def _get_qtype(self):
        if 3 in self._cache:
            r = self._cache[3]
        else:
            r = self._buf_get(3, RpbIndexReq.TYPE_IndexQueryType, 'qtype')
            self._cache[3] = r
        return r

    def _establish_parentage_qtype(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_qtype), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_qtype
                v._pbf_establish_parent_callback = self._establish_parentage_qtype

    def _set_qtype(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_qtype(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field qtype"
            raise ProtoValueError(list_assign_error)
        self._cache[3] = v
        self._mods[3] = RpbIndexReq.TYPE_IndexQueryType

    def _mod_qtype(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[3] = RpbIndexReq.TYPE_IndexQueryType

    def _del_qtype(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 3 in self._cache:
            del self._cache[3]
        if 3 in self._mods:
            del self._mods[3]
        self._buf_del(3)

    _pb_field_name_3 = "qtype"

    qtype = property(_get_qtype, _set_qtype, _del_qtype)

    @property
    def qtype__exists(self):
        return 3 in self._mods or self._buf_exists(3)

    @property
    def qtype__type(self):
        return RpbIndexReq.TYPE_IndexQueryType

    def _finalize_qtype(cls):
        if is_string(RpbIndexReq.TYPE_IndexQueryType):
            cls._pbf_strings.append(3)
        elif _PB_type(RpbIndexReq.TYPE_IndexQueryType) is _PB_type:
            assert issubclass(RpbIndexReq.TYPE_IndexQueryType, RepeatedSequence)
            if is_string(RpbIndexReq.TYPE_IndexQueryType.pb_subtype):
                cls._pbf_strings.append(3)

    _pbf_finalizers.append(_finalize_qtype)


    def _get_key(self):
        if 4 in self._cache:
            r = self._cache[4]
        else:
            r = self._buf_get(4, ProtoBase.TYPE_bytes, 'key')
            self._cache[4] = r
        return r

    def _establish_parentage_key(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_key), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_key
                v._pbf_establish_parent_callback = self._establish_parentage_key

    def _set_key(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_key(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field key"
            raise ProtoValueError(list_assign_error)
        self._cache[4] = v
        self._mods[4] = ProtoBase.TYPE_bytes

    def _mod_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[4] = ProtoBase.TYPE_bytes

    def _del_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 4 in self._cache:
            del self._cache[4]
        if 4 in self._mods:
            del self._mods[4]
        self._buf_del(4)

    _pb_field_name_4 = "key"

    key = property(_get_key, _set_key, _del_key)

    @property
    def key__exists(self):
        return 4 in self._mods or self._buf_exists(4)

    @property
    def key__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_key(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(4)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(4)

    _pbf_finalizers.append(_finalize_key)


    def _get_range_min(self):
        if 5 in self._cache:
            r = self._cache[5]
        else:
            r = self._buf_get(5, ProtoBase.TYPE_bytes, 'range_min')
            self._cache[5] = r
        return r

    def _establish_parentage_range_min(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_range_min), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_range_min
                v._pbf_establish_parent_callback = self._establish_parentage_range_min

    def _set_range_min(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_range_min(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field range_min"
            raise ProtoValueError(list_assign_error)
        self._cache[5] = v
        self._mods[5] = ProtoBase.TYPE_bytes

    def _mod_range_min(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[5] = ProtoBase.TYPE_bytes

    def _del_range_min(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 5 in self._cache:
            del self._cache[5]
        if 5 in self._mods:
            del self._mods[5]
        self._buf_del(5)

    _pb_field_name_5 = "range_min"

    range_min = property(_get_range_min, _set_range_min, _del_range_min)

    @property
    def range_min__exists(self):
        return 5 in self._mods or self._buf_exists(5)

    @property
    def range_min__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_range_min(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(5)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(5)

    _pbf_finalizers.append(_finalize_range_min)


    def _get_range_max(self):
        if 6 in self._cache:
            r = self._cache[6]
        else:
            r = self._buf_get(6, ProtoBase.TYPE_bytes, 'range_max')
            self._cache[6] = r
        return r

    def _establish_parentage_range_max(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_range_max), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_range_max
                v._pbf_establish_parent_callback = self._establish_parentage_range_max

    def _set_range_max(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_range_max(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field range_max"
            raise ProtoValueError(list_assign_error)
        self._cache[6] = v
        self._mods[6] = ProtoBase.TYPE_bytes

    def _mod_range_max(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[6] = ProtoBase.TYPE_bytes

    def _del_range_max(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 6 in self._cache:
            del self._cache[6]
        if 6 in self._mods:
            del self._mods[6]
        self._buf_del(6)

    _pb_field_name_6 = "range_max"

    range_max = property(_get_range_max, _set_range_max, _del_range_max)

    @property
    def range_max__exists(self):
        return 6 in self._mods or self._buf_exists(6)

    @property
    def range_max__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_range_max(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(6)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(6)

    _pbf_finalizers.append(_finalize_range_max)


TYPE_RpbIndexReq = RpbIndexReq
_PB_finalizers.append('RpbIndexReq')

class RpbIndexResp(ProtoBase):
    _required = []
    _field_map = {'keys': 1}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['keys']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    class Repeated_keys(RepeatedSequence):
        class pb_subtype(object):
            def __get__(self, instance, cls):
                return ProtoBase.TYPE_bytes
        pb_subtype = pb_subtype()


    TYPE_Repeated_keys = Repeated_keys


    def _get_keys(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, self.TYPE_Repeated_keys, 'keys')
            self._cache[1] = r
        return r

    def _establish_parentage_keys(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_keys), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_keys
                v._pbf_establish_parent_callback = self._establish_parentage_keys

    def _set_keys(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_keys(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field keys"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = self.TYPE_Repeated_keys

    def _mod_keys(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = self.TYPE_Repeated_keys

    def _del_keys(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "keys"

    keys = property(_get_keys, _set_keys, _del_keys)

    @property
    def keys__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def keys__type(self):
        return self.TYPE_Repeated_keys

    def _finalize_keys(cls):
        if is_string(cls.TYPE_Repeated_keys):
            cls._pbf_strings.append(1)
        elif _PB_type(cls.TYPE_Repeated_keys) is _PB_type:
            assert issubclass(cls.TYPE_Repeated_keys, RepeatedSequence)
            if is_string(cls.TYPE_Repeated_keys.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_keys)


TYPE_RpbIndexResp = RpbIndexResp
_PB_finalizers.append('RpbIndexResp')

class RpbContent(ProtoBase):
    _required = [1]
    _field_map = {'last_mod_usecs': 8, 'links': 6, 'deleted': 11, 'vtag': 5, 'charset': 3, 'value': 1, 'indexes': 10, 'last_mod': 7, 'usermeta': 9, 'content_encoding': 4, 'content_type': 2}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['value', 'content_type', 'charset', 'content_encoding', 'vtag', 'links', 'last_mod', 'last_mod_usecs', 'usermeta', 'indexes', 'deleted']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_value(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'value')
            self._cache[1] = r
        return r

    def _establish_parentage_value(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_value), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_value
                v._pbf_establish_parent_callback = self._establish_parentage_value

    def _set_value(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_value(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field value"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_value(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_value(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "value"

    value = property(_get_value, _set_value, _del_value)

    @property
    def value__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def value__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_value(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_value)


    def _get_content_type(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'content_type')
            self._cache[2] = r
        return r

    def _establish_parentage_content_type(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_content_type), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_content_type
                v._pbf_establish_parent_callback = self._establish_parentage_content_type

    def _set_content_type(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_content_type(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field content_type"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_content_type(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_content_type(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "content_type"

    content_type = property(_get_content_type, _set_content_type, _del_content_type)

    @property
    def content_type__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def content_type__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_content_type(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_content_type)


    def _get_charset(self):
        if 3 in self._cache:
            r = self._cache[3]
        else:
            r = self._buf_get(3, ProtoBase.TYPE_bytes, 'charset')
            self._cache[3] = r
        return r

    def _establish_parentage_charset(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_charset), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_charset
                v._pbf_establish_parent_callback = self._establish_parentage_charset

    def _set_charset(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_charset(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field charset"
            raise ProtoValueError(list_assign_error)
        self._cache[3] = v
        self._mods[3] = ProtoBase.TYPE_bytes

    def _mod_charset(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[3] = ProtoBase.TYPE_bytes

    def _del_charset(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 3 in self._cache:
            del self._cache[3]
        if 3 in self._mods:
            del self._mods[3]
        self._buf_del(3)

    _pb_field_name_3 = "charset"

    charset = property(_get_charset, _set_charset, _del_charset)

    @property
    def charset__exists(self):
        return 3 in self._mods or self._buf_exists(3)

    @property
    def charset__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_charset(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(3)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(3)

    _pbf_finalizers.append(_finalize_charset)


    def _get_content_encoding(self):
        if 4 in self._cache:
            r = self._cache[4]
        else:
            r = self._buf_get(4, ProtoBase.TYPE_bytes, 'content_encoding')
            self._cache[4] = r
        return r

    def _establish_parentage_content_encoding(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_content_encoding), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_content_encoding
                v._pbf_establish_parent_callback = self._establish_parentage_content_encoding

    def _set_content_encoding(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_content_encoding(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field content_encoding"
            raise ProtoValueError(list_assign_error)
        self._cache[4] = v
        self._mods[4] = ProtoBase.TYPE_bytes

    def _mod_content_encoding(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[4] = ProtoBase.TYPE_bytes

    def _del_content_encoding(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 4 in self._cache:
            del self._cache[4]
        if 4 in self._mods:
            del self._mods[4]
        self._buf_del(4)

    _pb_field_name_4 = "content_encoding"

    content_encoding = property(_get_content_encoding, _set_content_encoding, _del_content_encoding)

    @property
    def content_encoding__exists(self):
        return 4 in self._mods or self._buf_exists(4)

    @property
    def content_encoding__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_content_encoding(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(4)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(4)

    _pbf_finalizers.append(_finalize_content_encoding)


    def _get_vtag(self):
        if 5 in self._cache:
            r = self._cache[5]
        else:
            r = self._buf_get(5, ProtoBase.TYPE_bytes, 'vtag')
            self._cache[5] = r
        return r

    def _establish_parentage_vtag(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_vtag), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_vtag
                v._pbf_establish_parent_callback = self._establish_parentage_vtag

    def _set_vtag(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_vtag(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field vtag"
            raise ProtoValueError(list_assign_error)
        self._cache[5] = v
        self._mods[5] = ProtoBase.TYPE_bytes

    def _mod_vtag(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[5] = ProtoBase.TYPE_bytes

    def _del_vtag(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 5 in self._cache:
            del self._cache[5]
        if 5 in self._mods:
            del self._mods[5]
        self._buf_del(5)

    _pb_field_name_5 = "vtag"

    vtag = property(_get_vtag, _set_vtag, _del_vtag)

    @property
    def vtag__exists(self):
        return 5 in self._mods or self._buf_exists(5)

    @property
    def vtag__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_vtag(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(5)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(5)

    _pbf_finalizers.append(_finalize_vtag)


    class Repeated_links(RepeatedSequence):
        class pb_subtype(object):
            def __get__(self, instance, cls):
                return TYPE_RpbLink
        pb_subtype = pb_subtype()


    TYPE_Repeated_links = Repeated_links


    @property
    def links__stream(self):
        if 6 in self._cache:
            def acc(v):
                v_ = lambda: v
                return v_
            return [acc(v) for v in self._cache[6]]
        return self._get_repeated(6, self.TYPE_Repeated_links, "links", lazy=True)

    def _get_links(self):
        if 6 in self._cache:
            r = self._cache[6]
        else:
            r = self._buf_get(6, self.TYPE_Repeated_links, 'links')
            self._cache[6] = r
        return r

    def _establish_parentage_links(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_links), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_links
                v._pbf_establish_parent_callback = self._establish_parentage_links

    def _set_links(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_links(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field links"
            raise ProtoValueError(list_assign_error)
        self._cache[6] = v
        self._mods[6] = self.TYPE_Repeated_links

    def _mod_links(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[6] = self.TYPE_Repeated_links

    def _del_links(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 6 in self._cache:
            del self._cache[6]
        if 6 in self._mods:
            del self._mods[6]
        self._buf_del(6)

    _pb_field_name_6 = "links"

    links = property(_get_links, _set_links, _del_links)

    @property
    def links__exists(self):
        return 6 in self._mods or self._buf_exists(6)

    @property
    def links__type(self):
        return self.TYPE_Repeated_links

    def _finalize_links(cls):
        if is_string(cls.TYPE_Repeated_links):
            cls._pbf_strings.append(6)
        elif _PB_type(cls.TYPE_Repeated_links) is _PB_type:
            assert issubclass(cls.TYPE_Repeated_links, RepeatedSequence)
            if is_string(cls.TYPE_Repeated_links.pb_subtype):
                cls._pbf_strings.append(6)

    _pbf_finalizers.append(_finalize_links)


    def _get_last_mod(self):
        if 7 in self._cache:
            r = self._cache[7]
        else:
            r = self._buf_get(7, ProtoBase.TYPE_uint32, 'last_mod')
            self._cache[7] = r
        return r

    def _establish_parentage_last_mod(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_last_mod), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_last_mod
                v._pbf_establish_parent_callback = self._establish_parentage_last_mod

    def _set_last_mod(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_last_mod(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field last_mod"
            raise ProtoValueError(list_assign_error)
        self._cache[7] = v
        self._mods[7] = ProtoBase.TYPE_uint32

    def _mod_last_mod(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[7] = ProtoBase.TYPE_uint32

    def _del_last_mod(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 7 in self._cache:
            del self._cache[7]
        if 7 in self._mods:
            del self._mods[7]
        self._buf_del(7)

    _pb_field_name_7 = "last_mod"

    last_mod = property(_get_last_mod, _set_last_mod, _del_last_mod)

    @property
    def last_mod__exists(self):
        return 7 in self._mods or self._buf_exists(7)

    @property
    def last_mod__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_last_mod(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(7)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(7)

    _pbf_finalizers.append(_finalize_last_mod)


    def _get_last_mod_usecs(self):
        if 8 in self._cache:
            r = self._cache[8]
        else:
            r = self._buf_get(8, ProtoBase.TYPE_uint32, 'last_mod_usecs')
            self._cache[8] = r
        return r

    def _establish_parentage_last_mod_usecs(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_last_mod_usecs), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_last_mod_usecs
                v._pbf_establish_parent_callback = self._establish_parentage_last_mod_usecs

    def _set_last_mod_usecs(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_last_mod_usecs(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field last_mod_usecs"
            raise ProtoValueError(list_assign_error)
        self._cache[8] = v
        self._mods[8] = ProtoBase.TYPE_uint32

    def _mod_last_mod_usecs(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[8] = ProtoBase.TYPE_uint32

    def _del_last_mod_usecs(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 8 in self._cache:
            del self._cache[8]
        if 8 in self._mods:
            del self._mods[8]
        self._buf_del(8)

    _pb_field_name_8 = "last_mod_usecs"

    last_mod_usecs = property(_get_last_mod_usecs, _set_last_mod_usecs, _del_last_mod_usecs)

    @property
    def last_mod_usecs__exists(self):
        return 8 in self._mods or self._buf_exists(8)

    @property
    def last_mod_usecs__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_last_mod_usecs(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(8)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(8)

    _pbf_finalizers.append(_finalize_last_mod_usecs)


    class Repeated_usermeta(RepeatedSequence):
        class pb_subtype(object):
            def __get__(self, instance, cls):
                return TYPE_RpbPair
        pb_subtype = pb_subtype()


    TYPE_Repeated_usermeta = Repeated_usermeta


    @property
    def usermeta__stream(self):
        if 9 in self._cache:
            def acc(v):
                v_ = lambda: v
                return v_
            return [acc(v) for v in self._cache[9]]
        return self._get_repeated(9, self.TYPE_Repeated_usermeta, "usermeta", lazy=True)

    def _get_usermeta(self):
        if 9 in self._cache:
            r = self._cache[9]
        else:
            r = self._buf_get(9, self.TYPE_Repeated_usermeta, 'usermeta')
            self._cache[9] = r
        return r

    def _establish_parentage_usermeta(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_usermeta), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_usermeta
                v._pbf_establish_parent_callback = self._establish_parentage_usermeta

    def _set_usermeta(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_usermeta(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field usermeta"
            raise ProtoValueError(list_assign_error)
        self._cache[9] = v
        self._mods[9] = self.TYPE_Repeated_usermeta

    def _mod_usermeta(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[9] = self.TYPE_Repeated_usermeta

    def _del_usermeta(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 9 in self._cache:
            del self._cache[9]
        if 9 in self._mods:
            del self._mods[9]
        self._buf_del(9)

    _pb_field_name_9 = "usermeta"

    usermeta = property(_get_usermeta, _set_usermeta, _del_usermeta)

    @property
    def usermeta__exists(self):
        return 9 in self._mods or self._buf_exists(9)

    @property
    def usermeta__type(self):
        return self.TYPE_Repeated_usermeta

    def _finalize_usermeta(cls):
        if is_string(cls.TYPE_Repeated_usermeta):
            cls._pbf_strings.append(9)
        elif _PB_type(cls.TYPE_Repeated_usermeta) is _PB_type:
            assert issubclass(cls.TYPE_Repeated_usermeta, RepeatedSequence)
            if is_string(cls.TYPE_Repeated_usermeta.pb_subtype):
                cls._pbf_strings.append(9)

    _pbf_finalizers.append(_finalize_usermeta)


    class Repeated_indexes(RepeatedSequence):
        class pb_subtype(object):
            def __get__(self, instance, cls):
                return TYPE_RpbPair
        pb_subtype = pb_subtype()


    TYPE_Repeated_indexes = Repeated_indexes


    @property
    def indexes__stream(self):
        if 10 in self._cache:
            def acc(v):
                v_ = lambda: v
                return v_
            return [acc(v) for v in self._cache[10]]
        return self._get_repeated(10, self.TYPE_Repeated_indexes, "indexes", lazy=True)

    def _get_indexes(self):
        if 10 in self._cache:
            r = self._cache[10]
        else:
            r = self._buf_get(10, self.TYPE_Repeated_indexes, 'indexes')
            self._cache[10] = r
        return r

    def _establish_parentage_indexes(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_indexes), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_indexes
                v._pbf_establish_parent_callback = self._establish_parentage_indexes

    def _set_indexes(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_indexes(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field indexes"
            raise ProtoValueError(list_assign_error)
        self._cache[10] = v
        self._mods[10] = self.TYPE_Repeated_indexes

    def _mod_indexes(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[10] = self.TYPE_Repeated_indexes

    def _del_indexes(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 10 in self._cache:
            del self._cache[10]
        if 10 in self._mods:
            del self._mods[10]
        self._buf_del(10)

    _pb_field_name_10 = "indexes"

    indexes = property(_get_indexes, _set_indexes, _del_indexes)

    @property
    def indexes__exists(self):
        return 10 in self._mods or self._buf_exists(10)

    @property
    def indexes__type(self):
        return self.TYPE_Repeated_indexes

    def _finalize_indexes(cls):
        if is_string(cls.TYPE_Repeated_indexes):
            cls._pbf_strings.append(10)
        elif _PB_type(cls.TYPE_Repeated_indexes) is _PB_type:
            assert issubclass(cls.TYPE_Repeated_indexes, RepeatedSequence)
            if is_string(cls.TYPE_Repeated_indexes.pb_subtype):
                cls._pbf_strings.append(10)

    _pbf_finalizers.append(_finalize_indexes)


    def _get_deleted(self):
        if 11 in self._cache:
            r = self._cache[11]
        else:
            r = self._buf_get(11, ProtoBase.TYPE_bool, 'deleted')
            self._cache[11] = r
        return r

    def _establish_parentage_deleted(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_deleted), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_deleted
                v._pbf_establish_parent_callback = self._establish_parentage_deleted

    def _set_deleted(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_deleted(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field deleted"
            raise ProtoValueError(list_assign_error)
        self._cache[11] = v
        self._mods[11] = ProtoBase.TYPE_bool

    def _mod_deleted(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[11] = ProtoBase.TYPE_bool

    def _del_deleted(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 11 in self._cache:
            del self._cache[11]
        if 11 in self._mods:
            del self._mods[11]
        self._buf_del(11)

    _pb_field_name_11 = "deleted"

    deleted = property(_get_deleted, _set_deleted, _del_deleted)

    @property
    def deleted__exists(self):
        return 11 in self._mods or self._buf_exists(11)

    @property
    def deleted__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_deleted(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(11)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(11)

    _pbf_finalizers.append(_finalize_deleted)


TYPE_RpbContent = RpbContent
_PB_finalizers.append('RpbContent')

class RpbPair(ProtoBase):
    _required = [1]
    _field_map = {'value': 2, 'key': 1}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['key', 'value']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_key(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'key')
            self._cache[1] = r
        return r

    def _establish_parentage_key(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_key), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_key
                v._pbf_establish_parent_callback = self._establish_parentage_key

    def _set_key(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_key(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field key"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "key"

    key = property(_get_key, _set_key, _del_key)

    @property
    def key__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def key__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_key(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_key)


    def _get_value(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'value')
            self._cache[2] = r
        return r

    def _establish_parentage_value(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_value), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_value
                v._pbf_establish_parent_callback = self._establish_parentage_value

    def _set_value(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_value(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field value"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_value(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_value(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "value"

    value = property(_get_value, _set_value, _del_value)

    @property
    def value__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def value__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_value(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_value)


TYPE_RpbPair = RpbPair
_PB_finalizers.append('RpbPair')

class RpbLink(ProtoBase):
    _required = []
    _field_map = {'tag': 3, 'bucket': 1, 'key': 2}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['bucket', 'key', 'tag']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_bucket(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_bytes, 'bucket')
            self._cache[1] = r
        return r

    def _establish_parentage_bucket(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_bucket), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_bucket
                v._pbf_establish_parent_callback = self._establish_parentage_bucket

    def _set_bucket(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_bucket(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field bucket"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_bytes

    def _mod_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_bytes

    def _del_bucket(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "bucket"

    bucket = property(_get_bucket, _set_bucket, _del_bucket)

    @property
    def bucket__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def bucket__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_bucket(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_bucket)


    def _get_key(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bytes, 'key')
            self._cache[2] = r
        return r

    def _establish_parentage_key(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_key), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_key
                v._pbf_establish_parent_callback = self._establish_parentage_key

    def _set_key(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_key(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field key"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bytes

    def _mod_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bytes

    def _del_key(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "key"

    key = property(_get_key, _set_key, _del_key)

    @property
    def key__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def key__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_key(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_key)


    def _get_tag(self):
        if 3 in self._cache:
            r = self._cache[3]
        else:
            r = self._buf_get(3, ProtoBase.TYPE_bytes, 'tag')
            self._cache[3] = r
        return r

    def _establish_parentage_tag(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_tag), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_tag
                v._pbf_establish_parent_callback = self._establish_parentage_tag

    def _set_tag(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_tag(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field tag"
            raise ProtoValueError(list_assign_error)
        self._cache[3] = v
        self._mods[3] = ProtoBase.TYPE_bytes

    def _mod_tag(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[3] = ProtoBase.TYPE_bytes

    def _del_tag(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 3 in self._cache:
            del self._cache[3]
        if 3 in self._mods:
            del self._mods[3]
        self._buf_del(3)

    _pb_field_name_3 = "tag"

    tag = property(_get_tag, _set_tag, _del_tag)

    @property
    def tag__exists(self):
        return 3 in self._mods or self._buf_exists(3)

    @property
    def tag__type(self):
        return ProtoBase.TYPE_bytes

    def _finalize_tag(cls):
        if is_string(ProtoBase.TYPE_bytes):
            cls._pbf_strings.append(3)
        elif _PB_type(ProtoBase.TYPE_bytes) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bytes, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bytes.pb_subtype):
                cls._pbf_strings.append(3)

    _pbf_finalizers.append(_finalize_tag)


TYPE_RpbLink = RpbLink
_PB_finalizers.append('RpbLink')

class RpbBucketProps(ProtoBase):
    _required = []
    _field_map = {'allow_mult': 2, 'n_val': 1}
    
    def __init__(self, _pbf_buf='', _pbf_parent_callback=None, **kw):
        self._pbf_parent_callback = _pbf_parent_callback
        self._cache = {}
        self._pbf_establish_parent_callback = None
        ProtoBase.__init__(self, _pbf_buf, **kw)

    @classmethod
    def _pbf_finalize(cls):
        for c in cls._pbf_finalizers:
            c(cls)
        del cls._pbf_finalizers

    @classmethod
    def fields(cls):
        return ['n_val', 'allow_mult']

    def modified(self):
        return self._evermod

    def __contains__(self, item):
        try:
            return getattr(self, '%s__exists' % item)
        except AttributeError:
            return False

    _pbf_strings = []
    _pbf_finalizers = []

    def __str__(self):
        return '\n'.join('%s: %s' % (f, repr(getattr(self, '_get_%s' % f)())) for f in self.fields()
                          if getattr(self, '%s__exists' % f))

    def _get_n_val(self):
        if 1 in self._cache:
            r = self._cache[1]
        else:
            r = self._buf_get(1, ProtoBase.TYPE_uint32, 'n_val')
            self._cache[1] = r
        return r

    def _establish_parentage_n_val(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_n_val), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_n_val
                v._pbf_establish_parent_callback = self._establish_parentage_n_val

    def _set_n_val(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_n_val(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field n_val"
            raise ProtoValueError(list_assign_error)
        self._cache[1] = v
        self._mods[1] = ProtoBase.TYPE_uint32

    def _mod_n_val(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[1] = ProtoBase.TYPE_uint32

    def _del_n_val(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 1 in self._cache:
            del self._cache[1]
        if 1 in self._mods:
            del self._mods[1]
        self._buf_del(1)

    _pb_field_name_1 = "n_val"

    n_val = property(_get_n_val, _set_n_val, _del_n_val)

    @property
    def n_val__exists(self):
        return 1 in self._mods or self._buf_exists(1)

    @property
    def n_val__type(self):
        return ProtoBase.TYPE_uint32

    def _finalize_n_val(cls):
        if is_string(ProtoBase.TYPE_uint32):
            cls._pbf_strings.append(1)
        elif _PB_type(ProtoBase.TYPE_uint32) is _PB_type:
            assert issubclass(ProtoBase.TYPE_uint32, RepeatedSequence)
            if is_string(ProtoBase.TYPE_uint32.pb_subtype):
                cls._pbf_strings.append(1)

    _pbf_finalizers.append(_finalize_n_val)


    def _get_allow_mult(self):
        if 2 in self._cache:
            r = self._cache[2]
        else:
            r = self._buf_get(2, ProtoBase.TYPE_bool, 'allow_mult')
            self._cache[2] = r
        return r

    def _establish_parentage_allow_mult(self, v):
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            if v._pbf_parent_callback:
                assert (v._pbf_parent_callback == self._mod_allow_mult), "subobjects can only have one parent--use copy()?"
            else:
                v._pbf_parent_callback = self._mod_allow_mult
                v._pbf_establish_parent_callback = self._establish_parentage_allow_mult

    def _set_allow_mult(self, v, modifying=True):
        self._evermod = modifying or self._evermod
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if isinstance(v, (ProtoBase, RepeatedSequence)):
            self._establish_parentage_allow_mult(v)
        elif isinstance(v, list):
            list_assign_error = "Can't assign list to repeated field allow_mult"
            raise ProtoValueError(list_assign_error)
        self._cache[2] = v
        self._mods[2] = ProtoBase.TYPE_bool

    def _mod_allow_mult(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        self._mods[2] = ProtoBase.TYPE_bool

    def _del_allow_mult(self):
        self._evermod = True
        if self._pbf_parent_callback:
            self._pbf_parent_callback()
        if 2 in self._cache:
            del self._cache[2]
        if 2 in self._mods:
            del self._mods[2]
        self._buf_del(2)

    _pb_field_name_2 = "allow_mult"

    allow_mult = property(_get_allow_mult, _set_allow_mult, _del_allow_mult)

    @property
    def allow_mult__exists(self):
        return 2 in self._mods or self._buf_exists(2)

    @property
    def allow_mult__type(self):
        return ProtoBase.TYPE_bool

    def _finalize_allow_mult(cls):
        if is_string(ProtoBase.TYPE_bool):
            cls._pbf_strings.append(2)
        elif _PB_type(ProtoBase.TYPE_bool) is _PB_type:
            assert issubclass(ProtoBase.TYPE_bool, RepeatedSequence)
            if is_string(ProtoBase.TYPE_bool.pb_subtype):
                cls._pbf_strings.append(2)

    _pbf_finalizers.append(_finalize_allow_mult)


TYPE_RpbBucketProps = RpbBucketProps
_PB_finalizers.append('RpbBucketProps')


for cname in _PB_finalizers:
    eval(cname)._pbf_finalize()

del _PB_finalizers
