# -*- coding: utf-8 -*-
import json
import os
from watson.common import imports
from watson.db.contextmanagers import transaction_scope


__all__ = ('populate', 'populate_all')


def populate_all(sessions, fixtures, callback=None):
    data_dir = fixtures['path']
    total = 0
    for file_name, session_name in fixtures['data']:
        if not session_name:
            session_name = 'default'
        file_path = os.path.abspath(os.path.join(data_dir, file_name))
        file_name_ext = '{}.json'.format(file_path)
        total += populate(sessions[session_name], file_name_ext)
    return total


def populate(session, file_name):
    total = 0
    with open(file_name) as file:
        json_data = json.loads(file.read())
        with transaction_scope(session) as session:
            for item in json_data:
                class_ = imports.load_definition_from_string(item['class'])
                basic_fields = {k: v for k, v in item['fields'].items() if not isinstance(v, (list, tuple))}
                obj = class_(**basic_fields)
                total += 1
                session.add(obj)
    return total
