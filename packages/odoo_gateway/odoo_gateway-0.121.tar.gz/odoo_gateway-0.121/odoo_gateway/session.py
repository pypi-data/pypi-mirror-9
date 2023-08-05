# encoding=utf-8

import faults
import logging
import openerp
from openerp.cli import server as startup
from openerp import SUPERUSER_ID

logger = logging.getLogger('odoo_gateway')


api_version = openerp.release.version


def _get_cursor(registry):
    if api_version < '8':
        return registry.db.cursor()
    return registry._db.cursor()


def _initialize_config(openerp_options):
    openerp.tools.config.parse_config(list(openerp_options))
    return openerp.tools.config


def _get_database_registry(db_name):
    return openerp.modules.registry.RegistryManager.get(
        db_name,
        update_module=False,
    )


def _simplify_model_name(model_name):
    return model_name.replace(".", "_")


class Session(object):

    def __init__(self, openerp_options, db_name=None, uid=SUPERUSER_ID):

        self.conf = _initialize_config(openerp_options)

        openerp.netsvc.init_logger()

        # check that OS user is not superuser
        startup.check_root_user()

        # check that DBMS user is not postgres
        startup.check_postgres_user()

        # log main config parameters
        startup.report_configuration()

        self.registry = _get_database_registry(
            db_name or self.conf['db_name']
        )

        self.cr = _get_cursor(self.registry)  # odoo wrapper for cursor
        self.rr = self.cr._obj  # psycopg2 cursor
        self.conn = self.cr.connection
        self.uid = uid
        self.initiate_models()

    def initiate_models(self):
        if api_version < '8':
            self.models = Models_old(self)
        else:
            self.models = Models(self)
            self.models_old = Models_old(self)

    def rollback(self):
        self.cr.rollback()
        logger.info('Rollback')

    def commit(self):
        self.cr.commit()
        logger.info('Commit')

    def create_savepoint(self, name):
        self.cr.execute("SAVEPOINT {}".format(name))

    def rollback_to_savepoint(self, name):
        self.cr.execute("ROLLBACK TO SAVEPOINT {}".format(name))

    def release_savepoint(self, name):
        self.cr.execute('RELEASE SAVEPOINT {}'.format(name))

    def xid(self):
        self.cr.execute("select txid_current()")
        return self.cr.fetchone()[0]


class Models(object):

    def __init__(self, session):
        self.session = session
        self.registry = session.registry
        openerp.api.Environment._local.environments = \
            openerp.api.Environments()

        env = self.env
        for model_name in self.registry.models:
            setattr(
                self, _simplify_model_name(model_name),
                env[model_name]
            )

    @property
    def env(self):
        if not getattr(self, '_env', None):
            self._env = openerp.api.Environment(self.session.cr, self.session.uid, {})
        return self._env

    def __getitem__(self, model_name):
        return self.env[model_name]


class Models_old(object):

    def __init__(self, session):
        self.session = session
        self.registry = session.registry

        for model_name, model in self.registry.models.items():
            setattr(
                self, _simplify_model_name(model_name),
                model
            )

    def __getitem__(self, model_name):
        try:
            return getattr(self, _simplify_model_name(model_name))
        except AttributeError:
            raise faults.RootException(u"Cannot find model {}".format(
                model_name,
            ))
