from cubicweb.web.views import uicfg
from cubicweb.web import uihelper, formfields as ff, formwidgets as fw

from cubes.relationwidget.views import RelationFacetWidget


_as = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs

def edit_as_attr(etype, relname, desttype='*', role='subject',
                 formtype=('main', 'muledit')):
    if role == 'subject':
        uicfg.autoform_section.tag_subject_of((etype, relname, desttype),
                                              formtype=formtype, section='attributes')
    else:
        uicfg.autoform_section.tag_object_of((desttype, relname, etype),
                                              formtype=formtype, section='attributes')

class EveryThingConfing(uihelper.FormConfig):
    etype = 'EveryThing'
    rels_as_attrs = ('playes', 'notes')
    widgets = dict(
        playes=fw.InOutWidget,
        boolean_checkbox=fw.CheckBox,
        date=fw.DateTimePicker,
        jqdate=fw.JQueryDatePicker,
        time=fw.JQueryTimePicker,
        datetime=fw.JQueryDateTimePicker,
        checkbox=fw.CheckBox,
        radio=fw.Radio,
        #interval=fw.IntervalWidget,
        #bit_integer=fw.BitSelect,
        )

def set_field_kwargs(etype, fieldname, **kwargs):
    uicfg.autoform_field_kwargs.tag_subject_of((etype, fieldname, '*'), kwargs)

for fst, attrs in (('Strings', ('title', 'small_string', 'medium_string',
                                'big_string', 'rich_string', 'password')),
                   ('Dates', ('date', 'jqdate', 'time', 'datetime')),
                   ('Integers', ('integer', 'big_integer', 'bit_integer',
                                 'decimal', 'float', 'interval')),
                   ('Boolean', ('boolean_radio', 'boolean_checkbox')),
                   ('Lists', ('notes_list', 'playes')),
                  ):
    for i, attr in enumerate(attrs):
        set_field_kwargs('EveryThing', attr, fieldset=_(fst), order=1)

edit_as_attr('EveryThing', 'playes', 'Note')

_affk.tag_subject_of(('EveryThing', 'notes', '*'),
                    {'widget': RelationFacetWidget})

_affk.tag_subject_of(('EveryThing', 'playes', 'Note'),
                    {'widget': RelationFacetWidget})

