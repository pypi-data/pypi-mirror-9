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

"""cubicweb-uitest postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

# Example of site property change
set_property('ui.site-title', "CW tests")

# create notes
import numpy as np
from datetime import timedelta, datetime

from cubes.uitest.schema import NOTES_VOCABULARY

def generate_tempered_scale(lowest_note=-45 ,highest_note=43):
    keyboard = np.arange(lowest_note, highest_note)
    frequencies = 440 * 2. ** ((keyboard) / 12.)
    return frequencies

notes = []

frequencies = generate_tempered_scale()
for i, frequency in enumerate(frequencies):
    name = NOTES_VOCABULARY[i%len(NOTES_VOCABULARY)]
    notes.append(session.create_entity('Note',
                                       frequency=frequency,
                                       name=name,
                                       octave=i/12))


# create an excemple of EveryThing
session.create_entity('EveryThing',
                      title=u'Every thing you can have',
                      small_string=u'Lorem Ipsum',
                      medium_string =u'Lorem Ipsum is simply dummy text of the printing and typesetting industry.',
                      big_string = u'''Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.''',
                      rich_string = u'''<h1>Lorem Ipsum<h1> <p>is simply dummy text of the printing and typesetting industry.</p> <h2>Lorem Ipsum<h2> <p>has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. </p><p>It was popularised in the 1960s with the release of Letraset sheets containing <strong>Lorem Ipsum</strong> passages, and more recently with desktop publishing software like <strong>Aldus PageMaker</strong> including versions of <strong>Lorem Ipsum</strong>.</p>''',
                      integer = 314,
                      big_integer = 31415926,
                      decimal = 3.141592653793,
                      float = 3.141592653589793,
                      time = u'15:15',
                      playes = notes[:3],
                      notes = notes[:3],
                      )

# create a batch of EveryThing:

for i in range(24):
    session.create_entity('EveryThing',
                          title=u'%s every things' % i,
                          small_string=u'Lorem %s' % i,
                          medium_string =u'Lorem Ipsum is simply dummy text of the printing and typesetting industry. %s' % 1,
                          big_string = u'''Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.''',
                          rich_string = u'''<h1>Lorem Ipsum<h1> <p>is simply dummy text of the printing and typesetting industry.</p> <h2>Lorem Ipsum<h2> <p>has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. </p><p>It was popularised in the 1960s with the release of Letraset sheets containing <strong>Lorem Ipsum</strong> passages, and more recently with desktop publishing software like <strong>Aldus PageMaker</strong> including versions of <strong>Lorem Ipsum</strong>.</p>''',
                          integer = 314+i,
                          big_integer = 31415926+i,
                          decimal = 3.141592653793+i,
                          float = 3.141592653589793+i,
                          time = u'%s:15' % i,
                          datetime=datetime.now() + timedelta(i),
                          playes = notes[:i],
                          notes = notes[:i]
                      )
