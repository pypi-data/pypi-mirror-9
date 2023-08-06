# -*- coding: utf-8 -*-
# copyright 2014 Logilab (Paris, FRANCE), all rights reserved.

"""cubicweb-fevis views/forms for web ui"""

from cubicweb.web.views.startup import IndexView
from cubes.uitest.views import utils

class FormsStartupView(IndexView):
    """demo Forms view"""
    __regid__ = 'uitest.static_forms'
    title = _('Static forms')

    def call(self, **kwargs):
        self.w(u'<h1>%s</h1>' % _('Static forms'))
        self.forms()

    def forms(self):
        self.form_basic()
        self.forms_horizontal()
        self.forms_inline()

    def form_basic(self):
        form = u'''
 <div class="formTitle"><h1>Email (création)</h1></div>
 <legend>Informations générales</legend>
  <form role="form entityForm" id="entityForm">
  <fieldset><legend>Email</legend>
  <div class="form-group">
    <label class="required" for="exampleInputEmail1">Email address</label>
    <input type="email" class="form-control" id="exampleInputEmail1" placeholder="Enter email">
  </div>
  <div class="form-group">
    <label for="exampleInputPassword1">Password</label>
    <input type="password" class="form-control" id="exampleInputPassword1" placeholder="Password">
  </div>
  <div class="form-group">
    <label for="exampleInputFile">File input</label>
    <input type="file" id="exampleInputFile">
    <p class="help-block">Example block-level help text here.</p>
  </div>
  <div class="checkbox">
    <label>
      <input type="checkbox"> Check me out
    </label>
  </div>
  <button type="submit" class="btn btn-default">Submit</button>
  </fieldset>
</form>'''
        self.w(utils.simple_box('form_b', 'Basic form', form))

    def forms_horizontal(self):
        form = u'''
 <div class="formTitle"><h1>Email (création)</h1></div>
 <legend>Informations générales</legend>
 <form class="form-horizontal entityForm" id="entityForm" role="form">
  <fieldset><legend>Email</legend>
  <div class="form-group">
    <label for="inputEmail3" class="col-md-3 control-label required">Email</label>
    <div class="col-md-9">
      <input type="email" class="form-control" id="inputEmail3" placeholder="Email">
    </div>
  </div>
  <div class="form-group">
    <label for="inputPassword3" class="col-md-3 control-label">Password</label>
    <div class="col-md-9">
      <input type="password" class="form-control" id="inputPassword3" placeholder="Password">
    </div>
  </div>
 <div class="form-group">
    <label for="comment4" class="col-md-3 control-label required">Comment 1</label>
    <div class="col-md-9">
      <textarea class="form-control" id="comment4" ></textarea>
    </div>
  </div>
  <div class="form-group">
    <label for="comment5" class="col-md-3 control-label required">Comment 2</label>
    <div class="col-md-9">
      <input type="email" class="form-control" id="comment5" placeholder="Comment" />
      <p class="help-block">This is a small string</p>
    </div>
  </div>

  <div class="form-group">
    <div class="col-sm-offset-3 col-md-9">
      <div class="checkbox">
        <label>
          <input type="checkbox"> Remember me
        </label>
      </div>
    </div>
  </div>
  <div class="form-group">
    <div class="col-sm-offset-3 col-md-9">
      <button type="submit" class="btn btn-default">Sign in</button>
    </div>
  </div>
 </fieldset>
</form>'''
        self.w(utils.simple_box('form_h', 'Horizontal form', form))


    def forms_inline(self):
        form = u'''
 <div class="formTitle"><h1>Email (création)</h1></div>
 <legend>Informations générales</legend>
 <form class="form-inline entityForm" id="entityForm role="form">
 <fieldset><legend>Email</legend>
  <div class="form-group">
    <label  class="sr-only" for="exampleInputEmail2">Email address</label>
    <input type="email" class="form-control" id="exampleInputEmail2" placeholder="Enter email">
  </div>
  <div class="form-group">
    <label class="sr-only" for="exampleInputPassword2">Password</label>
    <input type="password" class="form-control" id="exampleInputPassword2" placeholder="Password">
  </div>
  <div class="checkbox">
    <label>
      <input type="checkbox"> Remember me
    </label>
  </div>
  <button type="submit" class="btn btn-primary">Sign in</button>
 </fieldset>
</form>'''
        self.w(utils.simple_box('form_h', 'Inline form', form))
