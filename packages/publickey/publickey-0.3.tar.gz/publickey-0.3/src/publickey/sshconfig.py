# -*- coding:utf-8 -*-
import sys
import codecs

import jinja2

import publickey.yamldata as yd


template = jinja2.Template(u'''\
{% for id, x in items %}
Host {{ id }}
  {% if x.title %}# {{ x.title }}{% endif %}
  HostName {{ x.hostname }}
  Port {{ x.port|default(22) }}
  User {{ x.user|default('ubuntu') }}
  IdentityFile {{ x.identityfile|default('~/.ssh/id_rsa') }}
{% endfor %}
ServerAliveInterval 120
''')


def generate(config):
    doc = yd.load(config.filepath)
    items = sorted(
        yd.filter_by_tags(doc, config.tags),
        # ((name, dct), ...)
        key=lambda x: (yd.first_tag(x[1]), x[0]),
    )
    text = template.render(items=items)
    codecs.getwriter('utf-8')(sys.stdout).write(text)
