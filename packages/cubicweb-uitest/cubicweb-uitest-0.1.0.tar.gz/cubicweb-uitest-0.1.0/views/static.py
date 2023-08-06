# -*- coding: utf-8 -*-
# copyright 2014 Logilab (Paris, FRANCE), all rights reserved.

"""cubicweb-fevis views/startup for web ui"""

from cubicweb.web.views.startup import IndexView

from cubes.uitest.views import utils

class DemoStartupView(IndexView):
    """demo Home Page view"""
    __regid__ = 'uitest.typography'
    title = _('Typography')

    def call(self, **kwargs):
        """ add an editable card and a demo video"""
        # editable card
        _ = self._cw._
        self.w(u'<h1>%s</h1>' % _('Typography'))
        self.w(u'<p>%s</p>' % _(u"This view provides a collection of typography samples such as headings, paragraphs, lists.."))
        self.nav_menu()
        self.w(u'<div class="row">')
        self.w(u'<div class="col-sm-6">')
        self.titles()
        self.w(u'</div>')
        self.w(u'<div class="col-sm-6">')
        self.definition_lists()
        self.blockquote()
        self.address()
        self.w(u'</div>')
        self.w(u'</div>')
        self.menus()
        self.lists()
        self.code()

    def nav_menu(self):
        html = u'''<p>No margin must be found here</p> <div class="bts-red-borders">
<ul class="nav nav-tabs">
  <li class="active"><a href="#titles">Titles</a></li>
  <li><a href="#dl">Definition Lists</a></li>
  <li><a href="#lists">Lists</a></li>
</ul></div>'''
        self.w(utils.simple_box('nav', 'NavMenu', html))

    @property
    def lorem(self):
        return {'lat': u'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit ...',
                'de': u'Falsches Üben von Xylophonmusik quält jeden größeren Zwerg.',
                'ar': u'روباه قهوه‌ای‌رنگ چابک بر روی سگ تنبل پرید',
                'ja': u'かつてはテレタイプの試験にもしばしば用いられたほか、今日ではコンピュータで使用するフォントのサンプル文としても広く用いられている。数字を含めて試験する場合には',
                u'ru': u'Съешь ещё этих мягких французских булок, да выпей же чаю.',
                'fr': u'Le vif renard brun saute par-dessus le chien paresseux.',
                'en': u'The quick brown fox jumps over the lazy dog.',
                }

    def get_paragraph(self, text, klass=''):
        return u'<p class="%s">%s</p>' % (klass, text)

    def get_title(self, i):
        tag = 'h%s'% i
        title = '%s. Heading %s' % (tag, i)
        return ['<%s>' % tag, title, '</%s>' % tag]

    def titles(self):
        html = []
        for i in range(1,7):
            html.extend(self.get_title(i))
        langs = utils.LOREM.keys()
        for i in range(1,7):
            html.extend(self.get_title(i))
            html.append(self.get_paragraph(utils.LOREM[langs[i]]))
        self.w(utils.simple_box('headings', 'Headings', u'\n'.join(html)))

    def get_lists(self, tag='ul'):
        html = []
        w = html.append
        w(u'<%s>' % tag)
        w(u'<li><a href="http://cubicweb.org">Link List Item</a></li>')
        w(u'<li><a href="http://cubicweb.org" rel="tooltip" title=" tooltip for Link List Item">'
          u'Link List Item with tooltip</a></li>')
        w(u'<%s>' % tag)
        w(u'<li><i>Nested List Item in italic</i></li>')
        w(u'<li><b>Nested List Item in bold</b></li>')
        w(u'<%s>'% tag)
        for i in range(2):
            w(u'<li> Double Nested List Item</li>')
        w(u'</%s>' % tag)
        w(u'<%s class="list-unstyled">' % tag)
        w(u'<li><i>Nested Unstyled List Item in italic</i></li>')
        w(u'<li><b>Nested Unstyled List Item in bold</b></li>')
        w(u'</%s>'% tag)
        w(u'<li><strong>Nested List Item in strong</strong></li>')
        w(u'<li><em>Nested List Item in emphasis</em></li>')
        w(u'</%s>' % tag)
        w(u'''<li><i class="fa fa-warning text-warning"></i>
        <i>List Item with custom icon</i>''')
        w(u'<li><span class="label label-danger">I am a label</span></li>')
        w(u'</%s>' % tag)
        return html

    def get_classed_lists(self, tag='ul', klass='list-striped list-unstyled'):
        html = []
        w = html.append
        w(u'<%s class="%s">' % (tag, klass))
        w(u'<li class="odd"><a href="http://cubicweb.org">Link List Item</a></li>')
        w(u'<li class="even" ><a href="http://cubicweb.org" rel="tooltip" title=" tooltip for Link List Item">'
          u'Link List Item with tooltip</a></li>')
        w(u'<%s class="%s">' % (tag, klass))
        w(u'<li class="odd"><i>Nested List Item in italic</i></li>')
        w(u'<li class="even"><b>Nested List Item in bold</b></li>')
        w(u'<%s class="%s">' % (tag, klass))
        for i in range(2):
            w(u'<li class="%s"> Double Nested List Item</li>' % (u'odd' if i%2 else u'even'))
        w(u'</%s>' % tag)
        w(u'<%s class="list-unstyled %s">' % (tag, klass))
        w(u'<li class="odd"><i>Nested Unstyled List Item in italic</i></li>')
        w(u'<li class="even"><b>Nested Unstyled List Item in bold</b></li>')
        w(u'</%s>'% tag)
        w(u'<li class="odd"><strong>Nested List Item in strong</strong></li>')
        w(u'<li class="even"><em>Nested List Item in emphasis</em></li>')
        w(u'</%s>' % tag)
        w(u'''<li  class="odd"><i class="fa fa-warning text-warning"></i>
        <i>List Item with custom icon</i>''')
        w(u'<li class="even"><span class="label label-danger">I am a label</span></li>')
        w(u'</%s>' % tag)
        return html

    def lists(self):
        html = ['<div class="row">']
        html.extend(['<div class="col-sm-2">'])
        html.extend(['<h3>Unordered Lists whithout class</h3>'])
        html.extend(self.get_lists())
        html.extend(['</div>', '<div class="col-sm-2">'])
        html.extend(['<h3>Ordered lists whithout class</h3>'])
        html.extend(self.get_lists(tag='ol'))
        html.extend(['</div>'])
        html.extend(['<div class="col-sm-2">'])
        html.extend(['<h3>Unordered lists with "list-striped" class</h3>'])
        html.extend(self.get_classed_lists())
        html.extend(['</div>', '<div class="col-sm-2">'])
        html.extend(['<h3>Ordered lists with "list-striped" class</h3>'])
        html.extend(self.get_classed_lists(tag='ol'))
        html.extend(['</div>'])
        html.extend(['<div class="col-sm-2">'])
        html.extend(['<h3>Unordered lists with "list-unstyled" class</h3>'])
        html.extend(self.get_classed_lists(klass="list-unstyled"))
        html.extend(['</div>'])
        html.extend(['<div class="col-sm-2">'])
        html.extend(['<h3>Ordered lists with "list-unstyled" class</h3>'])
        html.extend(self.get_classed_lists(tag='ol', klass="list-unstyled"))
        html.extend(['</div>'])
        html.extend(['</div>'])
        self.w(utils.simple_box('lists', 'Lists', u'\n'.join(html)))

    def get_def_lists(self, klass=""):
        return u"""<dl class="%s">
        <dt>Lorem ipsum</dt>
        <dd>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</dd>
        <dt>Ut enim ad minim veniam</dt>
        <dd>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</dd>
        <dd>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</dd>
        <dt>Excepteur sint</dt>
        <dt>ccaecat cupidatat</dt>
        <dd>At vero eos et accusamus et iusto odio dignissimos ducimus, qui blanditiis praesentium voluptatum deleniti atque corrupti, quos dolores et quas molestias excepturi sint, obcaecati cupiditate non provident, similique sunt in culpa, qui officia deserunt mollitia animi, id est laborum et dolorum fuga.</dd>
        </dl>""" % klass

    def definition_lists(self):
        self.w(utils.simple_box('deflists', 'Definition lists', self.get_def_lists()))

    def get_blockquote(self, text):
        return u'<blockquote>%s</blockquote>' % text

    def blockquote(self):
        html = [utils.blockquote(utils.LOREM['ja'], source=u'まる')]
        self.w(utils.simple_box('blockquote', 'Blockquote', u'\n'.join(html)))

    def address(self):
        address = u'''<address>
        <strong>Logilab, Inc.</strong>
        <br>
        104 boulevard Auguste Blanqui
        <br>
        75013 Paris
        <br>
        <abbr title="Phone">P:</abbr>
        01 23 34 45 56
        </address>'''
        self.w(utils.simple_box('address', 'Address', address))



    def code(self):
        code = u'''<pre>
input, select, textarea {
  height: 34px;
  padding: 6px 6px;
  font-size: 14px;
  line-height: 1.428571429;
  color: #555555;
  vertical-align: middle;
  background-color: #ffffff;
  border: 1px solid #cccccc;
  border-radius: 4px;
}</pre>'''
        self.w(utils.simple_box('code', 'pre', code, glyphicon_name='edit'))

    @property
    def get_drop_down_menu_1(self):
        return u'''<div class="dropdown clearfix">
      <button data-toggle="dropdown" id="dropdownMenu1" type="button" class="btn dropdown-toggle sr-only">
        Dropdown
        <span class="caret"></span>
      </button>
      <ul aria-labelledby="dropdownMenu1" role="menu" class="dropdown-menu">
        <li role="presentation"><a href="#" tabindex="-1" role="menuitem">Action</a></li>
        <li role="presentation"><a href="#" tabindex="-1" role="menuitem">Another action</a></li>
        <li role="presentation"><a href="#" tabindex="-1" role="menuitem">Something else here</a></li>
        <li class="divider" role="presentation"></li>
        <li role="presentation"><a href="#" tabindex="-1" role="menuitem">Separated link</a></li>
      </ul>
    </div>'''

    @property
    def get_drop_down_menu_2(self):
        return u'''<div class="dropdown clearfix">
      <button data-toggle="dropdown" id="dropdownMenu2" type="button" class="btn dropdown-toggle sr-only">
        Dropdown
        <span class="caret"></span>
      </button>
      <ul aria-labelledby="dropdownMenu2" role="menu" class="dropdown-menu">
        <li class="dropdown-header" role="presentation">Dropdown header</li>
        <li role="presentation"><a href="#" tabindex="-1" role="menuitem">Action</a></li>
        <li role="presentation"><a href="#" tabindex="-1" role="menuitem">Another action</a></li>
        <li role="presentation"><a href="#" tabindex="-1" role="menuitem">Something else here</a></li>
        <li class="divider" role="presentation"></li>
        <li class="dropdown-header" role="presentation">Dropdown header</li>
        <li role="presentation"><a href="#" tabindex="-1" role="menuitem">Separated link</a></li>
      </ul>
    </div>'''

    def menus(self):
        self.w(u'<div class="row">')
        self.w(u'<div class="col-sm-3">')
        html = [self.get_drop_down_menu_1]
        self.w(utils.simple_box('ddm1', 'DropDownMenu', '\n'.join(html), with_code=True))
        self.w(u'</div>')
        self.w(u'<div class="col-sm-3">')
        html = [self.get_drop_down_menu_2]
        self.w(utils.simple_box('ddm2', 'DropDownMenu', '\n'.join(html), with_code=True))
        self.w(u'</div>')
        self.w(u'</div>')
