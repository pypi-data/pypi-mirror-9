# encoding=utf-8


import sys
sys.path.insert(0, '/home/odoo/odoo_gateway')
sys.path.insert(0, '/home/odoo/odoo-8.0-20150120')

from odoo_gateway import Session
s = Session(['-c', '/home/odoo/odoo-8.0-20150120/config-155.conf'])
