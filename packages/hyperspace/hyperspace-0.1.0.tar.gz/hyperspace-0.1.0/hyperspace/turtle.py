from hyperspace.affordances import Page
from rdflib import Graph


class TurtlePage(Page):
    """
    Generic attempt to extract RDF data from anything supported by rdflib.
    No control affordances, so use this class only as a last resort unless
    a RESTful dead-end is acceptable.
    """

    def __init__(self, response):
        super(TurtlePage, self).__init__(response)

    def extract_data(self):
        self.data = Graph()
        self.data.parse(data=self.response.text, format='turtle')
