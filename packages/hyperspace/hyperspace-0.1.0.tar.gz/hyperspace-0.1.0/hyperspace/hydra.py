from hyperspace.affordances import FilterableList, Link, Page
from rdflib import Namespace, Graph, URIRef


HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')


class HydraPage(Page):
    def __init__(self, response):
        self.data = Graph()
        self.links = FilterableList()
        super(HydraPage, self).__init__(response)

    def extract_data(self):
        self.data.parse(data=self.response.text, format='json-ld', identifier=self.url)

    def extract_links(self):
        for p, o in self.data.predicate_objects(URIRef(self.url)):
            if isinstance(o, URIRef):
                link = Link(p.toPython(), o.toPython())
                self.links.append(link)
