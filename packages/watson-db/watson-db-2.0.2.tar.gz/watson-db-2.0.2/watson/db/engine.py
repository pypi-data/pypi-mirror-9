# -*- coding: utf-8 -*-
from sqlalchemy import create_engine

NAME = 'sqlalchemy_engine_{}'


def make_engine(**kwargs):
    """Create a new engine for SqlAlchemy.

    Remove the container argument that is sent through from the DI container.
    """
    del kwargs['container']
    return create_engine(**kwargs)


def create_db(engine, model, drop=False):
    """Creates a new database on the given engine based on the models metadata.

    Args:
        engine (Engine): A SQLAlchemy engine object
        model (object): The model base containing the associated metadata.
    """
    if drop:
        model.metadata.drop_all(engine)
    model.metadata.create_all(engine, checkfirst=True)
