import hyperspace
from rdflib import Graph
import collections
import requests


class FilterableList(list):
    def __getitem__(self, item_name):
        return [item for item in self if item.name == item_name]

    def keys(self):
        return set(sorted(item.name for item in self))


class Link(object):
    def __init__(self, name, href):
        self.name = name
        self.href = href

    def follow(self):
        return hyperspace.jump(self.href)

    def __str__(self):
        return '[{name}]({href})'.format(name=self.name, href=self.href)


class Query(object):
    def __init__(self, name, href, params):
        self.name = name
        self.href = href
        self.params = params

    def build(self, params):
        for key, value in params.items():
            if key in self.params:
                self.params[key] = value
            else:
                error_message = 'No query param {} exists in current ' \
                                'query template "{}"'.format(key, self.name)
                raise KeyError(error_message)
        return self

    def submit(self):
        """Very naive URL creation."""
        return hyperspace.jump(self.href + '?' + '&'.join(
            [key + '=' + value for key, value in self.params.items()]))

    def __str__(self):
        flat_params = ', '.join([u'{name}={value}'.format(name=name, value=value) for name, value in self.params.items()])

        return u'[{name}]({href}){{{params}}}'.format(
            name=self.name, href=self.href, params=flat_params)

class Template(object):
    def __init__(self, name, href, params, content_type):
        self.name = name
        self.href = href
        self.params = params
        self.content_type = content_type

    def build(self, newparams):
        for name, value in newparams.items():
            self.params[name] = value
        return self

    def submit(self):
        return hyperspace.send(self.href, self.params, self.content_type)

    def __str__(self):
        flat_params = u', '.join(
            [u'{name}={value}'.format(name=unicode(name), value=unicode(value))
             for name, value in self.params.items()]
        )

        return u'[{name}]({href}){{{params}}}'.format(
            name=self.name, href=self.href, params=flat_params)


class Page(object):
    def __init__(self, response):
        self.response = response
        self.url = response.url
        self.content_type = response.headers['Content-Type']
        self.extract_data()
        self.extract_links()
        self.extract_queries()
        self.extract_templates()

    def extract_data(self):
        self.data = Graph()
        self.data.parse(data=self.response.text)

    def extract_links(self):
        self.links = FilterableList()

    def extract_queries(self):
        self.queries = FilterableList()

    def extract_templates(self):
        self.templates = FilterableList()

    def __str__(self):
        return u'Page:\n\tData:\n{data}\n\tLinks:\n\t\t{links}\n\tQueries:\n\t\t{queries}\n\tTemplates:\n\t\t{templates}'.format(
            data=self.data.serialize(format='turtle').decode('utf-8'),
            links=u'\n\t\t'.join([unicode(l) for l in self.links]),
            queries=u'\n\t\t'.join([unicode(f) for f in self.queries]),
            templates=u'\n\t\t'.join([unicode(t) for t in self.templates])).encode('utf-8')
