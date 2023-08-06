# -*- coding: utf-8 -*-
# copyright 2014 UNLISH (Montpellier, France), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@unlish.com
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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-mandrill schema"""


from yams.buildobjs import (
    EntityType, SubjectRelation,
    String, Int)


class Message(EntityType):
    __unique_together__ = (('_id',),)

    _id = String(required=True)

    state = String(
        vocabulary=(u"sent", u"queued", u"scheduled", u"rejected", u"invalid"))
    state_msg = String()

    template = String()

    ts = Int()

    from_email = String()
    from_name = String()
    subject = String()

    to_email = String()
    to_name = String()

    stags = String()

    headers = String()

    text = String()
    html = String()

    attachment = SubjectRelation(
        'File', cardinality='**', composite='subject')

    open = SubjectRelation(
        'MessageOpen', composite='subject', cardinality='**')
    clic = SubjectRelation(
        'MessageClick', composite='subject', cardinality='**')


class MessageOpen(EntityType):
    __unique_together__ = [('ts', 'ip', 'location', 'ua')]

    ts = Int()
    ip = String()
    location = String()
    ua = String()


class MessageClick(EntityType):
    __unique_together__ = [('ts', 'url', 'ip', 'location', 'ua')]

    ts = Int()
    url = String()
    ip = String()
    location = String()
    ua = String()
