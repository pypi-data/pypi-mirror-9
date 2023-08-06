Odoo Gateway
============

This package implements tools which help you to access database using
Odoo models' mechanizm. Use Odoo Gateway and you will be able to

-  Run models' methods in shell. Usefull when you need to fix some
   database data or test you code.
-  Create stand-alone scripts which can refer to Odoo models and call
   their methods.

Version
~~~~~~~

0.0.1

Tech
~~~~

To use Odoo Gateway properly you need only
`Odoo <https://www.odoo.com/documentation/8.0/index.html>`_ library of 7 or 8 versions.

Installation
~~~~~~~~~~~~

You can use pip: ::

  $ pip install odoo_gateway

Shell
~~~~~

Shell can be launched with::

  $ odoosh [params]


Parameters are the same as openerp server's ones. You can list then any time, just type::

  $ odoosh --help

Ok, lets do it right now!::

  $ odoosh -c config_file.conf -d database1

  In [1]:


Nice!
Odoo shell is launched now. Following objects are already in namespace:

-  **cr** - Odoo wrapper for psycopg's cursor::

    In [2]: cr
    <openerp.sql_db.Cursor at 0x3450d50>

    In [3]: cr.execute("select id, name from sale_order limit 1")
    In [4]: cr.fetchall()
    [(600094, u'SALE-123456')]``
-  **conn** - Psycopg's connection to database::

    In [5]: conn
    <connection object at 0x3485f60; dsn: 'host=localhost port=5432 user=odoo password=xxxx dbname=database1', closed: 0>
    In [6]: conn.rollback()

-  **rr** - Psycopg's cursor
-  **uid** - Id of Odoo superuser
-  **conf** - Instance of *openerp.tools.config.configmanager* that contains parsed Odoo parameters::

    In [7]: conf
    <openerp.tools.config.configmanager at 0x210bbd0>
    In [8]: conf['db_name']
    database1
    In [9]: conf['db_host']
    localhost
-  **models** - Adapter for Odoo models' list.::

    In [10]: models.sale_order  # get reference for model
    sale.order sale.order()
    In [11]: type(models.sale_order)
    openerp.api.sale.order
    In [12]: """Now we are free to apply API and user defined methods of model."""
    In [13]: sale1 = models.sale_order.search([('name','=', 'sale-111111')])
    In [14]: sale1.name sale-111111
    In [15]: sale2 = models['sale.order'].search([('name','=', 'sale-111112')])
    In [16]: sale2.name sale-111112

   There are two ways to refer to Odoo model.

  -  You can use model's name **name.of.model** and get reference with
     **models[name.of.model]**. See line *15* of example above.

  -  Or you can replace **'.'** with **'\_'** and type
     **models.name\_of\_model**. The result will be the same as in previous point. See lines 10-14.

-  **session** - Instance of odoo\_gateway.session.Session

Stand-alone scripts
~~~~~~~~~~~~~~~~~~~

There are problems which require using openerp API outside the openerp
server, in another independent process. For example imagine that you
have a Shop. *Done?* Ok. There is a python application APP. APP is a
messenger and uses the system of queues. Customers send messages in
which they describe what products they want to buy. APP gets messages
from queues, parses them and create sale orders in database.

I belive that APP does not need for openerp server to be launched. No, sir!

All you need is instance of *odoo\_gateway.session.Session*, which is
initiated with odoo server' command parameters.::

    from odoo_gateway import Session
    session = Session(['-c', 'config.conf', '-d', 'testdb'])

As you get session object you can get anything you may dream about.::

    models = session.models
    cr = session.cr
    conn = session.conn
    uid = session.uid
    rr = session.rr
    conf = session.conf

    # The power is yours now

    def create_sale(**params):
        models.sale_order.create(**params)
        cr.commit()


License
-------

BSD
