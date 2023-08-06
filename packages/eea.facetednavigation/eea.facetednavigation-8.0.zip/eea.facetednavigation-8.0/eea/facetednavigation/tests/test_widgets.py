""" Solr tests
"""
from eea.facetednavigation.tests.base import FacetedTestCase
from eea.facetednavigation.widgets.widget import CountableWidget


class DummySolrResponse(dict):
    """ Solr
    """
    @property
    def facet_counts(self):
        """ Count
        """
        return {'facet_fields': self}


class CountableWidgetTestCase(FacetedTestCase):
    """ Test
    """
    def afterSetUp(self):
        """ Setup
        """
        self.request = self.app.REQUEST

    def test_widget_empty_count(self):
        """ Empty count
        """
        data = {}
        widget = CountableWidget(self.portal, self.request, data=data)
        self.assertEqual(widget.count([]), {})

    def test_widget_solr_count(self):
        """ Test facet extraction from solr response
        """
        data = {'index': 'tags'}
        widget = CountableWidget(self.portal, self.request, data=data)
        dummyresponse = DummySolrResponse({'tags': {'foo': 10, 'bar': 7}})
        self.assertEqual(widget.count(dummyresponse),
                         {'': 1, 'all': 1, u'bar': 7, u'foo': 10})
