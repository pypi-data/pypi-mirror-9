from functools import wraps


def construct_hexconnector_port(st):
    def init_adapter(cn):
        app_config = cn.g_('app_config')
        backend_name = app_config.get('nimoy', {}).get('backend_name', 'in_memory')
        connection_str = app_config.get('nimoy', {}).get('connection_str', None)
        st.init_backend(backend_name, connection_str)

    def close_adapter(cn):
        st.close()

    ret = {
        'init_adapter': init_adapter,
        'close_adapter': close_adapter
    }
    for list_name in st._lists:
        _create, _update_one, _update_many, _get_one, _get_many = st.construct_functions(list_name)
        ret['create_{}'.format(list_name)] = add_cn_param(_create)
        ret['update_{}'.format(list_name)] = add_cn_param(_update_one)
        ret['update_{}s'.format(list_name)] = add_cn_param(_update_many)
        ret['get_{}'.format(list_name)] = add_cn_param(_get_one)
        ret['get_{}s'.format(list_name)] = add_cn_param(_get_many)
    return ret


def add_cn_param(fn):
    @wraps(fn)
    def _new_fn(cn, *args, **kwargs):
        return fn(*args, **kwargs)
    return _new_fn
