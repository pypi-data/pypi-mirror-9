# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-uitest schema"""

from datetime import date

from yams.buildobjs import EntityType, \
     String, Date, Datetime, Time, Bytes, BigInt, Int, RichString, Boolean, \
     Float, Decimal, Interval, Password, TZTime, TZDatetime, Bytes, \
     SubjectRelation, RelationType, RelationDefinition

PERSMISSIONS_ANON = {
    'read':   ('managers', 'users', 'guests'),
    'add':    ('managers', 'users', 'guests'),
    'update': ('managers', 'users', 'guests'),
    'delete': ('managers', 'users', 'guests' ),
    }

REL_PERMISSIONS_ANON = {
    'read':   ('managers', 'users', 'guests'),
    'add':    ('managers', 'users', 'guests'),
    'delete': ('managers', 'users', 'guests'),
    }

NOTES = (
    _(u'ut'), _(u'ut majeur'), _(u'ut mineur'),
    _(u'do'), _(u'do majeur'), _(u'do mineur'),
    _(u'sol'), _(u'ré'), _(u'la'), _(u'mi'), _(u'si'), _(u'fa dièse'), _(u'do dièse'),
    _(u'sol majeur'), _(u'ré majeur'), _(u'la majeur'), _(u'mi majeur'), _(u'si majeur'), _(u'fa dièse majeur'), _(u'do dièse majeur'),
    _(u'fa'), _(u'si bémol'), _(u'mi bémol'), _(u'la bémol'), _(u'ré bémol'), _(u'sol bémol'), _(u'do bémol'),
    _(u'fa majeur'), _(u'si bémol majeur'), _(u'mi bémol majeur'), _(u'la bémol majeur'), _(u'ré bémol majeur'), _(u'sol bémol majeur'), _(u'do bémol majeur'),
    _(u'la mineur'), _(u'mi mineur'), _(u'si mineur'), _(u'fa dièse mineur'), _(u'do dièse mineur'), _(u'sol dièse mineur'), _(u'ré dièse mineur'), _(u'la dièse mschineur'),
    _(u'ré mineur'), _(u'sol mineur'), _(u'do mineur'), _(u'fa mineur'), _(u'si bémol mineur'), _(u'mi bémol mineur'), _(u'la bémol mineur')
    )
BIT = ()

class EveryThing(EntityType):
    __permissions__ = PERSMISSIONS_ANON
    title = String(required=True)
    small_string = String(maxsize=12, description='This is a small string (maxize=12)')
    medium_string = String(maxsize=256, description='This is a meduim string (maxsize=256)')
    big_string = String(description='This is a big string, no maxsize')
    rich_string = RichString(default_format='text/html', description='This is a rich string')
    password = Password(description='This is a passeword')
    date = Date(default='TODAY', description='This is a datew with DateTimePicker widget') # date naissance
    jqdate = Date(default='TODAY', description='This is a date with JQueryDatePicker widget') # date naissance
    time = Time(description='This is a date with JQueryTimePicker widget') # date naissance
    datetime = Datetime(default='TODAY', description='This is a date with JQueryDateTimePicker widget') # date naissance
    integer = Int(description='This is an integer')
    big_integer = Int(description='This is an a big integer')
    bit_integer = Int(description='This is a bit integer with BitSelect widget')
    decimal = Decimal(description='This is an decimal')
    float = Float(description='This is a float')
    interval = Interval(description='This is an interval')
    boolean_radio = Boolean(required=True, default=False, description='This is a boolean radio')
    boolean_checkbox = Boolean(required=True, default=False, description='This is a boolean checkbox with CheckBox widget')
    notes_list = String(vocabulary=NOTES,  description='This is a note list with default Select widget')
    byte = Bytes(description='This are bytes')


NOTES_VOCABULARY = [_('Do'), _('Do#'), _('Re'), _('Re#'), _('Mi'), _('Fa'),
                    _('Fa#'), _('Sol'), _('Sol#'),_('La'), _('Sib'), _('Si')]

class Note(EntityType):
    __permissions__ = PERSMISSIONS_ANON
    name = String(vocabulary=NOTES_VOCABULARY,
                  required=True, internationalizable=True)
    frequency = Float(description=_('Hz'), default=440, required=True)
    octave = Int(required=True,
                 constraints=[IntervalBoundConstraint(0, 7)]) # XXX more ?

class playes(RelationType):
    __permissions__ = REL_PERMISSIONS_ANON
    subject = 'EveryThing'
    object = 'Note'
    cardinality = '**'
    description = u'This is a note list with InOutWidget'

class notes(RelationType):
    __permissions__ = REL_PERMISSIONS_ANON
    subject = 'EveryThing'
    object = ('Note', 'EveryThing')
    cardinality = '**'
    description = u'This is a note list with RelationWidget'
