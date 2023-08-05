# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy.ext.declarative import DeclarativeMeta
from watson.common import strings


NAME = 'sqlalchemy_declarative_base'


class _DeclarativeMeta(DeclarativeMeta):
    """Responsible for automatically assigning a tablename to a model.

    Tablenames will be pluralized.
    """
    @staticmethod
    def has_primary_key(dict_):
        for k, v in dict_.items():
            if isinstance(v, Column) and v.primary_key:
                return True
        return False

    def __new__(cls, classname, bases, dict_):
        tablename = dict_.get('__tablename__')
        if not tablename and not dict_.get('__table__') \
           and _DeclarativeMeta.has_primary_key(dict_):
            dict_['__tablename__'] = strings.pluralize(
                strings.snakecase(classname))
        return DeclarativeMeta.__new__(cls, classname, bases, dict_)
