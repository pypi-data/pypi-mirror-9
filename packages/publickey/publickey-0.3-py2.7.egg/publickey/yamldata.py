# -*- coding:utf-8 -*-
import yaml

empty = (None,)


def tags(entry):
    lst = entry.get('tags')
    if isinstance(lst, basestring):
        lst = [lst]
    return lst


def first_tag(entry):
    lst = tags(entry) or empty
    return lst[0]


def load(filepath):
    with open(filepath, 'r') as fp:
        return yaml.safe_load(fp.read())


def _all(doc):
    return ((name, x) for name, x in doc.items() if 'hostname' in x)


def filter_by_tags(doc, tags):
    items = _all(doc)
    if tags:
        criterion = set(tags)

        def filter_by_tags(iterable):
            for name, x in iterable:
                _tags = x.get('tags')
                if isinstance(_tags, basestring):
                    _tags = [_tags]
                if criterion <= set(_tags):
                    yield name, x
        items = list(filter_by_tags(items))
    return items
