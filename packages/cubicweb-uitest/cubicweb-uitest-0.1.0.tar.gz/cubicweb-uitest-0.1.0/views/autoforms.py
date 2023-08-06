"""uitest implementation of autoforms

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"
from cubicweb.predicates import is_instance

from cubicweb.web.views import forms, autoform, editforms

class EveryThingEntityForm(autoform.AutomaticEntityForm):
    __select__ = (autoform.AutomaticEntityForm.__select__ &
                  is_instance('EveryThing'))

    fieldsets_in_order = (_('Strings'), _('Dates'), _('Integers'),
                          _('Boolean'), _('Lists'), None)
