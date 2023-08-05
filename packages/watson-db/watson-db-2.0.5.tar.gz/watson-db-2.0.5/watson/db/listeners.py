# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from watson.console.command import find_commands_in_module
from watson.framework import events
from watson.db import commands
from watson.db.meta import _DeclarativeMeta, NAME as DECLARATIVE_BASE_NAME
from watson.db.session import NAME as SESSION_NAME
from watson.db.engine import NAME as ENGINE_NAME


class Init(object):

    """Bootstraps watson.db into the event system of watson.

    Each session and engine can be retrieved from the container by using
    sqlalchemy_engine_[name of engine] and sqlalchemy_session_[name of session]
    respectively.
    """

    def _validate_config(self, config, container):
        """Validates the config and sets some standard defaults.
        """
        if 'db' not in config:
            raise ValueError(
                'No db has been configured in your application configuration.')
        default_fixtures = {
            'path': '../data/db/fixtures',
            'data': []
        }
        default_fixtures.update(config['db'].get('fixtures', {}))
        config['db']['fixtures'] = default_fixtures
        default_migrations = {
            'path': '../data/db/alembic',
            'use_twophase': False
        }
        default_migrations.update(config['db'].get('migrations', {}))
        config['db']['migrations'] = default_migrations
        for session, session_config in config['db']['connections'].items():
            if 'metadata' not in session_config:
                session_config['metadata'] = 'watson.db.models.Model'
        if DECLARATIVE_BASE_NAME not in config['dependencies']['definitions']:
            container.add(
                DECLARATIVE_BASE_NAME,
                declarative_base(name='Model', metaclass=_DeclarativeMeta))

    def _load_default_commands(self, config):
        """Load default database commands and append to application config.
        """
        existing_commands = config.get('commands', [])
        db_commands = find_commands_in_module(commands)
        db_commands.extend(existing_commands)
        config['commands'] = db_commands

    def _create_engines_and_sessions(self, config, container):
        for session, config in config['db']['connections'].items():
            # Configure the engine options and add it to the container
            engine = ENGINE_NAME.format(session)
            engine_init_args = config.get('engine_options', {})
            engine_init_args['name_or_url'] = config['connection_string']
            container.add_definition(
                engine,
                {
                    'item': 'watson.db.engine.make_engine',
                    'init': engine_init_args
                })
            # Configure the session options and add it to the container
            session_init_args = config.get('session_options', {})
            session_init_args['bind'] = engine
            container.add_definition(
                SESSION_NAME.format(session),
                {
                    'item': 'watson.db.session.Session',
                    'init': session_init_args
                })

    def __call__(self, event):
        app = event.target
        self._validate_config(app.config, app.container)
        self._load_default_commands(app.config)
        self._create_engines_and_sessions(app.config, app.container)
        if ('watson.db.listeners.Complete',) not in app.config['events'].get(
                events.COMPLETE, {}):
            app.dispatcher.add(
                events.COMPLETE,
                app.container.get('watson.db.listeners.Complete'),
                1,
                False)


class Complete(object):

    """Cleanups the db session at the end of each request.
    """

    def __call__(self, event):
        app = event.target
        if 'db' not in app.config:
            raise ValueError(
                'No db has been configured in your application configuration.')  # pragma: no cover
        for session, config in app.config['db']['connections'].items():
            session_name = SESSION_NAME.format(session)
            session = app.container.get(session_name)
            session.close()
