# -*- coding: utf-8 -*-
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine
from watson.framework.debug import abc

TEMPLATE = """<style>
.watson-debug-toolbar__panel__debug {
    width: 100%;
}
.watson-debug-toolbar__panel__debug th:first-of-type {
    width: 80px;
}
</style>
<table class="watson-debug-toolbar__panel__debug">
    <thead>
        <tr>
            <th>Time</th><th>Query</th><th>Params</th>
        </tr>
    </thead>
    <tbody>
        {% for query in queries %}
        <tr>
            <td>{{ '{0:.2f}'.format(query['time']) }}ms</td>
            <td>{{ query['statement'] }}</td>
            <td>{{ query['parameters'] }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
"""
data = []


@event.listens_for(Engine, "before_cursor_execute")  # pragma: no cover
def before_cursor_execute(conn, cursor, statement, parameters,
                          context, executemany):
    context._query_start_time = time.time()  # pragma: no cover


@event.listens_for(Engine, "after_cursor_execute")  # pragma: no cover
def after_cursor_execute(conn, cursor, statement,
                         parameters, context, executemany):
    total = time.time() - context._query_start_time  # pragma: no cover
    data.append({
        'time': total*1000,
        'statement': statement,
        'parameters': parameters
    })  # pragma: no cover


class Query(abc.Panel):
    title = 'Database'

    def __init__(self, config, renderer, application):
        super(Query, self).__init__(config, renderer, application)
        self.application_run = application.run
        application.run = self.run

    def render(self):
        return self.renderer.env.from_string(TEMPLATE).render(
            queries=data)

    def render_key_stat(self):
        return '{0} queries ({1:.2f}ms)'.format(
            len(data),
            sum([query['time'] for query in data]))

    def run(self, environ, start_response):
        # Need to clear this on each run
        self.total = 0
        global data
        data = []
        return self.application_run(environ, start_response)
