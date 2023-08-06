import operator
import unicodedata

from collections import defaultdict
from uuid import uuid4
from unicodedata import normalize
from .commons import BaseDatabaseBackend


_in_memory_states = {}
DEFAULT_LIMIT = 10000000


class DatabaseBackend(BaseDatabaseBackend):

    def _post_init(self):
        if self.name not in _in_memory_states:
            _in_memory_states[self.name] = defaultdict(list)

    def reset(self, st):
        _in_memory_states[self.name] = defaultdict(list)

    def load_fixture(self, st, fixture_dict):
        for name in st._lists:
            list_name = st._lists[name]['name_plural']
            _in_memory_states[self.name][list_name] = fixture_dict.get(list_name) or []

    def create(self, st, list_name, *args, **kw):
        _in_memory_states[self.name]
        _new_obj_fn = st._lists[list_name]['new_obj_fn']
        return _copy(self._upsert(st, list_name, _new_obj_fn(*args, **kw)))

    def update_one(self, st, list_name, _id, **kw):
        _not_found_cls = st._lists[list_name]['not_found_cls']
        _w = ('eq', '_id', _id)
        result = self.update_many(st, list_name, _w=_w, **kw)
        if result['total']:
            return result['items'][0]
        else:
            raise _not_found_cls(_id=_id)

    def update_many(self, st, list_name, _w, **kw):
        filter_ = parse_wt(_w)
        ret = {'total': 0, 'items': []}
        for struct in self._find(st, list_name, filter_).get('items', []):
            struct.update(kw)
            supdated = self._upsert(st, list_name, struct)
            ret['items'].append(supdated)
            ret['total'] += 1
        return ret

    def get_one(self, st, list_name, _w):
        result = self.get_many(st, list_name, _w, limit=1)
        _not_found_cls = st._lists[list_name]['not_found_cls']
        if result['total']:
            return result['items'][0]
        else:
            raise _not_found_cls(_w=_w)

    def get_many(self, st, list_name, _w, limit=DEFAULT_LIMIT, offset=0, order_by=('_id', 'desc')):
        filter_ = parse_wt(_w)
        return _limit(_order(self._find(st, list_name, filter_), order_by), limit, offset)

    def _find_one(self, st, list_name, filter_=lambda x: True, apply_=lambda x: x):
        r = self._find(st, list_name, filter_, apply_)
        return r['items'][0] if r['total'] else None

    def _find(self, st, list_name, filter_=lambda x: True, apply_=lambda x: x):
        _state = _in_memory_states[self.name]
        _lname = st._lists[list_name]['name_plural']

        r = {}
        r['items'] = [apply_(_copy(d)) for d in _state[_lname] if filter_(d)]
        r['total'] = len(r['items'])
        r['_lname'] = _lname
        return r

    def _upsert(self, st, list_name, d):
        _state = _in_memory_states[self.name]
        _lname = st._lists[list_name]['name_plural']

        # ensure unique _id
        if '_id' not in d:
            d['_id'] = _new_id()

        i = _index_of(_state[_lname], d)
        if i is not None:
            # update
            d['v'] += 1  # new version
            _state[_lname][i] = d
        else:
            # insert
            d['v'] = 0  # initial version
            _state[_lname].append(d)
        return d


def _index_of(list_, d):
    _id_list = [x['_id'] for x in list_]
    if d['_id'] in _id_list:
        return _id_list.index(d['_id'])


def _copy(d):
    def _copy_list(l):
        r = []
        for i in l:
            if isinstance(i, dict):
                r.append(_copy_dict(i))
            elif isinstance(i, list):
                r.append(_copy_list(i))
            else:
                r.append(i)
        return r

    def _copy_dict(d):
        r = {}
        for i, j in d.items():
            if isinstance(j, dict):
                r[i] = _copy_dict(j)
            elif isinstance(j, list):
                r[i] = _copy_list(j)
            else:
                r[i] = j
        return r

    """ Create a new dict from d """
    return _copy_dict(d)


def _new_id(*args, **kwargs):
    if len(args) > 0:
        return args[0]
    if "_id" in kwargs:
        return kwargs["_id"]
    return uuid4().hex


def _normalize_and_lower(value):
    return normalize('NFKD', value.lower())\
        .encode('ascii', 'ignore')\
        .decode('utf-8')


def _limit(find_result_, limit, offset):
    r = _copy(find_result_)
    count = [len(r['items']) + 1, ]
    if limit:
        count.append(limit + offset)
    r['items'] = r['items'][offset:min(count)]
    r['_limit'] = limit
    r['_offset'] = offset
    return r


def _order(find_result_, order_by=()):
    r = _copy(find_result_)

    def _strip_accents(s):
        return ''.join(
            c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn')

    def _skey(s):
        return _strip_accents(s.lower())

    def _get_order_key(oname):
        if oname == '_id':
            return lambda x: x.get('_id')

    # def _datetime(key):
    #     # def _unify_timezone(value):
    #     #     d = Delorean(datetime=value, timezone='UTC')
    #     #     d.shift('UTC')
    #     #     return d.datetime

    #     def _f(x):
    #         value = x.get(key, Datetime2.min)
    #         if value:
    #             return value
    #         return Datetime2.min
    #     return _f
    # _defined_orders = {
    #     # users orders
    #     ('users', 'name'): lambda x: _skey(x.get('name', '')),
    #     ('users', 'email'): lambda x: _skey(x.get('email', '')),
    #     # recruitments orders
    #     ('recruitments', 'name'): lambda x: x.get('name'),
    #     # applicants orders
    #     ('applicants', 'name'): lambda x: _skey(x.get('name') or x.get('email') or ''),
    #     # clients orders
    #     ('clients', '_id'): lambda x: x.get('_id'),
    #     ('clients', 'name'): lambda x: x.get('name'),
    # }

    oby = list(order_by)
    list_ = find_result_['items']
    while oby:
        d_ = oby.pop()
        f_ = oby.pop()
        reverse_ = d_.startswith('d')
        key_ = _get_order_key(f_)  # _defined_orders.get((lname, f_))
        list_ = sorted(list_, key=key_, reverse=reverse_)
    r['items'] = list_
    r['_order_by'] = order_by
    return r


def parse_wt(wt, fmap=None):
    _fmap = fmap or {}

    def _x_f(obj, field):
        if field in _fmap:
            return _fmap[field](obj[field])
        else:
            return obj.get(field)

    def _get_normalized_values(obj, field, value):
        v_normalized = value
        if hasattr(obj[field], 'lower'):
            cobj = _copy(obj)
            cobj[field] = _normalize_and_lower(cobj[field])
            v_normalized = _normalize_and_lower(v_normalized)
            return cobj, v_normalized
        return obj, v_normalized

    def _eq(field, value):
        def _filter(obj):
            return _x_f(obj, field) == value

        def _filter_embed(obj):
            emb_key, emb_field = field.split('.')
            return value in [_x_f(d, emb_field) for d in obj.get(emb_key, [])]
        return _filter_embed if '.' in field else _filter

    def _field_value_predicate(field, value, _operator):
        return lambda obj: _operator(_x_f(obj, field), value)

    def _value_field_predicate(field, value, _operator):
        return lambda obj: _operator(value, _x_f(obj, field))

    def _missing(field, value):
        return lambda obj: operator.is_(_x_f(obj, field), None)

    def _contains(field, value):
        def _filter(obj):
            if obj[field] is not None:
                obj_normalized, v_normalized = _get_normalized_values(obj, field, value)
                if hasattr(v_normalized, 'split'):
                    return all([v_n in _x_f(obj_normalized, field) for v_n in v_normalized.split(" ")])
                return v_normalized in _x_f(obj_normalized, field)
            return False
        return _filter

    def _ncontains(field, value):
        def _filter(obj):
            if obj[field] is not None:
                obj_normalized, v_normalized = _get_normalized_values(obj, field, value)
                if hasattr(v_normalized, 'split'):
                    return not all([v_n in _x_f(obj_normalized, field) for v_n in v_normalized.split(" ")])
                return v_normalized not in _x_f(obj_normalized, field)
            return False
        return _filter

    def _in(field, value):
        return lambda obj: operator.contains(value, _x_f(obj, field))

    def _nin(field, value):
        return lambda obj: operator.not_(operator.contains(value, _x_f(obj, field)))

    def _and(wts):
        _filters = [parse_wt(_wt, fmap=fmap) for _wt in wts]

        def _filter(obj):
            return all([_f(obj) for _f in _filters])
        return _filter

    def _or(wts):
        _filters = [parse_wt(_wt, fmap=fmap) for _wt in wts]

        def _filter(obj):
            return any([_f(obj) for _f in _filters])
        return _filter

    def _startswith(field, value):
        return lambda obj: _x_f(obj, field).startswith(value) if hasattr(_x_f(obj, field), 'startswith') else False

    if wt[0] == 'eq':
        return _eq(wt[1], wt[2])
    elif wt[0] == 'neq':
        return _field_value_predicate(wt[1], wt[2], _operator=operator.ne)
    elif wt[0] == 'gt':
        return _field_value_predicate(wt[1], wt[2], _operator=operator.gt)
    elif wt[0] == 'gte':
        return _field_value_predicate(wt[1], wt[2], _operator=operator.ge)
    elif wt[0] == 'lt':
        return _field_value_predicate(wt[1], wt[2], _operator=operator.lt)
    elif wt[0] == 'lte':
        return _field_value_predicate(wt[1], wt[2], _operator=operator.le)
    elif wt[0] == 'contains':
        return _contains(wt[1], wt[2])
    elif wt[0] == 'ncontains':
        return _ncontains(wt[1], wt[2])
    elif wt[0] == 'in':
        return _in(wt[1], wt[2])
    elif wt[0] == 'nin':
        return _nin(wt[1], wt[2])
    elif wt[0] == 'and':
        return _and(wt[1:])
    elif wt[0] == 'or':
        return _or(wt[1:])
    elif wt[0] == 'startswith':
        return _startswith(wt[1], wt[2])
    elif wt[0] == 'missing':
        return _missing(wt[1], wt[2])
