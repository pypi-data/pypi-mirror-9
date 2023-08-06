# -*- coding: utf-8 -*-
# copyright 2014 Logilab (Paris, FRANCE), all rights reserved.

"""cubicweb-fevis views/utils for web ui"""

from cubicweb.web.component import Layout

LOREM = {'lat': u'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit ...',
                'de': u'Falsches Üben von Xylophonmusik quält jeden größeren Zwerg.',
                'ar': u'روباه قهوه‌ای‌رنگ چابک بر روی سگ تنبل پرید',
                'ja': u'かつてはテレタイプの試験にもしばしば用いられたほか、今日ではコンピュータで使用するフォントのサンプル文としても広く用いられている。数字を含めて試験する場合には',
                u'ru': u'Съешь ещё этих мягких французских булок, да выпей же чаю.',
                'fr': u'Le vif renard brun saute par-dessus le chien paresseux.',
                'en': u'The quick brown fox jumps over the lazy dog.',
                }

class BoxLayout(Layout):
    __regid__ = 'box_layout'

    def render(self, w):
        if self.init_rendering():
            view = self.cw_extra_kwargs['view']
            w(u'<div class="panel panel-default %s %s" id="%s">' % (self.cssclass, view.cssclass,
                                                                    view.domid))
            with wrap_on_write(w, u'<h5 class="panel-heading panel-title">',
                               u'</h5>') as wow:
                view.render_title(wow)
            w(u'<div class="panel-body">')
            view.render_body(w)
            # We dissapear the boxFooter CSS place holder, as shadows
            # or effect will be made with CSS
            w(u'</div></div>\n')

def simple_box(id, title, content, glyphicon_name=None, with_code=False):
    if glyphicon_name:
        title = '<i class="glyphicon glyphicon-%s"></i> %s' % (glyphicon_name, title)
    box = (u'''<div id="%(id)s" class="bsd-exemple panel panel-default">
    <h5 class="panel-heading panel-title">%(title)s</h5>
    <div class="panel-body">%(content)s</div>%(code)s
    </div>''')
    if False:
        code = '<div class="highlight"><pre><code class="html">%s</code></pre></div>' % content
    else:
        code = ''
    return box % {'id': id, 'title': title, 'content': content, 'code':code}

def blockquote(text, source=None):
    if source:
        source = u'<small class="pull-right"><cite title="Source">%s</cite></small>' % source
    return u'<blockquote><p>%(text)s</p>%(source)s</blockquote>' % {'source': source or u'',
                                                                   'text' : text}
