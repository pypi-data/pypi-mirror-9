# encoding=utf-8

import utils


_CALLBACKS_REGISTRY = {}


def broadcast(cr, uid, sig, data=None):
    sigs_methods = _CALLBACKS_REGISTRY.setdefault(cr.dbname, find_all_callbacks(cr.dbname))

    methods = sigs_methods.get(sig, [])
    for method in methods:
        method(cr, uid, data)


def find_all_callbacks(dbname):
    reg = {}

    pool = utils.get_database_registry(dbname)
    models = (pool.get(m) for m in pool.models)
    for model in models:
        for base in model.__class__.__mro__:
            for cb in base.__dict__.get('_callbacks', []):
                sig, method = cb
                reg.setdefault(sig, []).append(getattr(model, method))
    return reg
