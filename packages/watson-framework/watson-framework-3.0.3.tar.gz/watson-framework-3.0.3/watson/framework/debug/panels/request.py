# -*- coding: utf-8 -*-
from watson.framework.debug import abc

TEMPLATE = """
<dt>Request:</dt>
<dd>{{ request.url }}</dd>
<dt>Method:</dt>
<dd>{{ request.method }}</dd>
<dt>Session Id:</dt>
<dd>{{ request.session.id }}</dd>
<dt>Headers:</dt>
<dd>
    <table>
    {% for key, value in request.headers|dictsort %}
        <tr><td>{{ key }}</td><td>{{ value }}</td></tr>
    {% endfor %}
    </table>
</dd>
<dt>Get Vars:</dt>
<dd>
    <table>
    {% for key, value in request.get|dictsort %}
        <tr><td>{{ key }}</td><td>{{ value }}</td></tr>
    {% else %}
        -
    {% endfor %}
    </table>
</dd>
<dt>Post Vars:</dt>
<dd>
    <table>
    {% for key, value in request.post|dictsort %}
        <tr><td>{{ key }}</td><td>{{ value }}</td></tr>
    {% else %}
        -
    {% endfor %}
    </table>
</dd>
<dt>Server:</dt>
<dd>
    <table>
    {% for key, value in request.server|dictsort %}
        <tr><td>{{ key }}</td><td>{{ value }}</td></tr>
    {% endfor %}
    </table>
</dd>
"""


class Panel(abc.Panel):
    title = 'Request'

    def render(self):
        return self.renderer.env.from_string(TEMPLATE).render(
            request=self.event.params['context']['request'])

    def render_key_stat(self):
        return self.event.params['context']['request'].method
