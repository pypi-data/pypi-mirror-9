# encoding=utf-8

from odoo_gateway import Session

import sys
sys.path.insert(0, '/home/odoo/odoo_gateway')
s = Session(['-c', '/home/panaetov/Work/lib/openerp-7.0-20131031-002505/openerp-server-155.conf'])
