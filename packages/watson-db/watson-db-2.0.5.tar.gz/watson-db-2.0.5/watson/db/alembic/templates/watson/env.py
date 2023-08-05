# -*- coding: utf-8 -*-
from logging.config import fileConfig
import logging
from alembic import context
from watson.common.imports import load_definition_from_string

config = context.config

fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

watson = config.watson

USE_TWOPHASE = watson['config']['migrations']['use_twophase']

target_metadata = {}
engines = {}
for name, options in watson['config']['connections'].items():
    metadata = options['metadata']
    if isinstance(metadata, str):
        metadata = load_definition_from_string(metadata).metadata
    target_metadata[name] = metadata
    engines[name] = {
        'url': options['connection_string'],
        'instance': watson['container'].get(
            'sqlalchemy_engine_{0}'.format(name))
    }


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    for name, details in engines.items():
        logger.info('Migrating database {}'.format(name))
        file_ = '{}.sql'.format(name)
        with open(file_, 'w') as buffer:
            context.configure(
                url=details['url'],
                output_buffer=buffer,
                target_metadata=target_metadata.get(name))
        with context.begin_transaction():
            context.run_migrations(engine_name=name)


def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    for name, details in engines.items():
        engine = details['instance']
        details['connection'] = conn = engine.connect()

        if USE_TWOPHASE:
            details['transaction'] = conn.begin_twophase()
        else:
            details['transaction'] = conn.begin()

    try:
        for name, details in engines.items():
            logger.info('Migrating database {}'.format(name))
            context.configure(
                connection=details['connection'],
                upgrade_token='{}_upgrades'.format(name),
                downgrade_token='{}_downgrades'.format(name),
                target_metadata=target_metadata.get(name)
            )
            context.run_migrations(engine_name=name)
        if USE_TWOPHASE:
            for rec in engines.values():
                rec['transaction'].prepare()

        for rec in engines.values():
            rec['transaction'].commit()
    except:
        for rec in engines.values():
            rec['transaction'].rollback()
        raise
    finally:
        for rec in engines.values():
            rec['connection'].close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
