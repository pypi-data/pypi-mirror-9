# encoding=utf-8

from broadcast import broadcast
from session import Session

def shell():
    import IPython
    import sys

    session = Session(sys.argv[1:])
    models = session.models
    cr = session.cr
    conn = session.conn
    uid = session.uid
    rr = session.rr
    conf = session.conf

    from openerp import netsvc
    wf = netsvc.LocalService("workflow")

    IPython.embed()
