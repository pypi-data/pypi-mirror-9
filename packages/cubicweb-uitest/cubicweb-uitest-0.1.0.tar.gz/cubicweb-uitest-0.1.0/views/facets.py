# -*- coding: utf-8 -*-
# copyright 2014 Logilab (Paris, FRANCE), all rights reserved.

"""cubicweb-uitest facets"""

from cubicweb.web.views import facets

from cubicweb.web import facet as facetbase
from cubicweb.predicates import is_instance, yes

_ = unicode

class EveryThingFacet(facetbase.AttributeFacet):
    """ EveryThing AttributeFacet on small_string"""
    __regid__ = 'uitest.attribute-facet'
    __select__ = facetbase.AttributeFacet.__select__ & is_instance('EveryThing')
    rtype = 'small_string'
    title = '1. facetbase.AttributeFacet on small_string attribute'
    order = 1

class  EveryThinDateRelatetionFacet(facetbase.RelationFacet):
    """RelationFacet for EveryThing RelationFacet on playes relation"""
    __regid__ = 'uitest.relation-facet'
    rtype = 'playes'
    target_attr = 'frequency'
    __select__ = facetbase.DateRangeFacet.__select__ & is_instance('EveryThing')
    title = '2. facetbase.RelationFacet on playes relation'
    order = 2

class RangeDateTimeEveryThingFacet(facetbase.DateRangeFacet):
    """DateRangeFacet for EveryThing on datetime attribute """
    __regid__ = 'uitest.data-range-facet'
    __select__ = facetbase.DateRangeFacet.__select__ & is_instance('EveryThing')
    rtype = 'datetime'
    title = '3. facetbase.DateRangeFacet on datetime attribute'
    order = 3

class CreationDateEveryThingFacet(facetbase.AttributeFacet):
    """AttributeFacet for EveryThing on datetime attribute """
    __regid__ = 'uitest.datatime-attribute-facet'
    __select__ = facetbase.DateRangeFacet.__select__ & is_instance('EveryThing')
    rtype = 'datetime'
    title = '4. facetbase.Attribute on datetime attribute'
    order = 4
