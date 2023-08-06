# encoding=utf-8

import openerp


api_version = openerp.release.version


def get_cursor(registry):
    if api_version < '8':
        return registry.db.cursor()
    return registry._db.cursor()


def initialize_config(openerp_options):
    openerp.tools.config.parse_config(list(openerp_options))
    return openerp.tools.config


def get_database_registry(db_name):
    return openerp.modules.registry.RegistryManager.get(
        db_name,
        update_module=False,
    )
