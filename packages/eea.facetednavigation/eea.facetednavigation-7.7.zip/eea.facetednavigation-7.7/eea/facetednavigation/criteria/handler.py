""" Low level faceted criteria API
"""
from persistent.list import PersistentList
from zope.component import getUtility
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from zope.schema.interfaces import IVocabularyFactory
from eea.facetednavigation.config import ANNO_CRITERIA
from eea.facetednavigation.widgets.storage import Criterion
from eea.facetednavigation.interfaces import IWidgetsInfo
from eea.facetednavigation.settings.interfaces import IDontInheritConfiguration

from eea.facetednavigation.criteria.interfaces import ICriteria

class Criteria(object):
    """ Handle criteria
    """
    implements(ICriteria)

    def __init__(self, context):
        """ Handle criteria
        """
        # LinguaPlone support
        if IDontInheritConfiguration.providedBy(context):
            self.context = context
        else:
            canonical = getattr(context, 'getCanonical', None)
            if canonical:
                self.context = canonical()
            else:
                self.context = context
        self.criteria = self._criteria()

    def _criteria(self):
        """ Get criteria from annotations
        """
        anno = IAnnotations(self.context)
        criteria = anno.get(ANNO_CRITERIA, None)
        if criteria is None:
            anno[ANNO_CRITERIA] = PersistentList()
        return anno[ANNO_CRITERIA]

    def _update(self, values):
        """ Update criteria
        """
        anno = IAnnotations(self.context)
        anno[ANNO_CRITERIA] = PersistentList(values)
        self.criteria = anno[ANNO_CRITERIA]
    #
    # Getters
    #
    def newid(self):
        """ Get new id
        """
        return Criterion().getId()

    def get(self, key, default=None):
        """ Get criterion
        """
        for cid, cvalue in self.items():
            if key == cid:
                return cvalue
        return default

    def keys(self):
        """ Criteria keys
        """
        return [criterion.getId() for criterion in self.criteria]

    def values(self):
        """ Criteria values
        """
        return [criterion for criterion in self.criteria]

    def items(self):
        """ Criteria items
        """
        return [(criterion.getId(), criterion) for criterion in self.criteria]
    #
    # Setters
    #
    def add(self, wid, position, section='default', **kwargs):
        """ Add criterion
        """
        widget = self.widget(wid)
        if not widget:
            raise NameError("Widget type '%s' is undefined" % wid)

        properties = {}
        criteria = self.criteria
        taken_ids = [criterion.getId() for criterion in criteria]
        properties['_taken_ids_'] = taken_ids
        properties.update(kwargs)

        criterion = Criterion(widget=wid, position=position,
                              section=section, **properties)
        criteria.append(criterion)
        return criterion.getId()

    def delete(self, cid):
        """ Delete criteria by given ids
        """
        if not cid:
            raise TypeError('delete takes exactly one argument (0 given)')

        for index, criterion in enumerate(self.criteria):
            criterion_id = criterion.getId()
            if criterion_id == cid:
                self.criteria.pop(index)
                return
        raise KeyError(cid)

    def edit(self, cid, **properties):
        """ Update criterion properties
        """
        criterion = self.get(cid)
        if not criterion:
            raise KeyError(cid)

        criterion.update(**properties)
        self.criteria._p_changed = 1
    #
    # Position
    #
    def up(self, cid):
        """ Move criterion up
        """
        insert = None
        index = 0
        for index, criterion in enumerate(self.criteria):
            if criterion.getId() == cid:
                insert = self.criteria.pop(index)
                break
        if not insert:
            raise KeyError(cid)

        if index > 0:
            index -= 1
        self.criteria.insert(index, insert)

    def down(self, cid):
        """ Move criterion down
        """
        insert = None
        index = 0
        for index, criterion in enumerate(self.criteria):
            if criterion.getId() == cid:
                insert = self.criteria.pop(index)
                break
        if not insert:
            raise KeyError(cid)

        index += 1
        self.criteria.insert(index, insert)

    def position(self, **kwargs):
        """ Update criteria position from given lists
        """
        voc = getUtility(IVocabularyFactory,
                         'eea.faceted.vocabularies.WidgetPositions')
        positions = ((term.value, kwargs.get(term.value, []))
                     for term in voc(self.context))

        res = []
        for position, cids in positions:
            for cid in cids:
                criterion = self.get(cid)
                criterion.update(position=position)
                res.append(criterion)
        self._update(res)
    #
    # Utils
    #
    def widget(self, wid=None, cid=None):
        """ Return widget by given wid or from criterion by given cid
        """
        if not wid:
            criterion = self.get(cid)
            if not criterion:
                raise KeyError(cid)
            wid = criterion.get('widget')
        info = getUtility(IWidgetsInfo)
        return info.widgets.get(wid, None)
