# -*- coding: utf-8 -*-
# copyright 2014 Logilab (Paris, FRANCE), all rights reserved.

"""cubicweb-fevis views/secondary for web ui"""
from cubicweb.web.views.startup import IndexView

class ResultStartupView(IndexView):
    """secondary views"""
    __regid__ = 'uitest.secondary'
    title = _('EveryThing secondary views')

    def call(self, **kwargs):
        self.w('<h1%s</h1>' % _('EveryThing secondary views'))
        rset = self._cw.execute('Any X WHERE X is EveryThing')
        if rset:
            entity = rset.get_entity(0,0)
            views = [v for v in self._cw.vreg['views'].possible_views(self._cw,
                                                                      rset=entity.as_rset())
                     if v.category != 'startupview']
            self.w(u'<ol>')
            for view in views:
                self.w(u'<li>')
                self.display_view(view, entity)
                self.w(u'</li>')
            self.w(u'</ol>')

    def display_view(self, view, entity):
        _ = self._cw._
        vid = view.__regid__
        self.w(u'<h2>%s</h2>' % _('"%s" view' % vid))
        self.w(u'<p>%s</p>' % _('Python code'))
        self.w(u'''<code>
                   <ol class="codeline">
                     <li>rset = self._cw.execute('Any X is EveryThin ').get_entity(0, 0)</li>
                     <li>entity.wview('%(vid)s', w=self.w)</li>
                    </ol>
                 </code>''' % {'vid':vid})
        self.w('<p>%s</p>' % _('Resulting HTML'))
        self.w(u'<div class="code-result">')
        try:
            # self.w(view.render()) XXX this is a problem with "list" view which
            # only generate <li></li> markup
            entity.view(vid, w=self.w)
        except Exception, err:
            self.w(u'<div class="danger error">%s</div>' % repr(err))
        self.w(u'</div>')
