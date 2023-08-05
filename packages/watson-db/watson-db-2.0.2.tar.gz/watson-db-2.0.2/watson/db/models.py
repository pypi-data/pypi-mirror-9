# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from watson.framework.applications import Base
from watson.db.meta import _DeclarativeMeta, NAME as DECLARATIVE_BASE_NAME


def modelmaker(name='Model', **kwargs):
    return declarative_base(name=name, metaclass=_DeclarativeMeta, **kwargs)


# Some standard defaults
try:
    Model = Base.global_app.container.get(DECLARATIVE_BASE_NAME)
except:
    # Application is not instantiated
    Model = modelmaker()
