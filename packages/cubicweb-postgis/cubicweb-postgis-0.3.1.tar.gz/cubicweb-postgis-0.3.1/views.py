# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-postgis views/forms/actions/components for web ui"""
from cwtags.tag import div, label, input

from cubicweb import uilib
from cubicweb.utils import UStringIO
from cubicweb.web import formfields
from cubicweb.web import formwidgets
from cubicweb.view import EntityView
from cubicweb.predicates import match_kwargs

try:
    from shapely import wkb
except ImportError:
    wkb = None


# StringField is probably not the worst default choice
formfields.FIELDS['Geometry'] = formfields.StringField
uilib.PRINTERS['Geometry'] = uilib.print_string
formfields.FIELDS['Geography'] = formfields.StringField
uilib.PRINTERS['Geography'] = uilib.print_string


class RefpointAttributeView(EntityView):
    __regid__ = 'refpointattr'
    __select__ = EntityView.__select__ & match_kwargs('rtype')

    def entity_call(self, entity, rtype, **kwargs):
        value = getattr(entity, rtype)
        if value:
            value = wkb.loads(value.decode('hex'))
            self.w(u'lat: %s, long: %s' % (value.x, value.y))


class RefpointWidget(formwidgets.TextInput):

    def _render(self, form, field, renderer):
        ustring = UStringIO()
        w = ustring.write
        value = self.values(form, field)[0]
        longitude = 0
        latitude = 0
        if value:
            value = wkb.loads(value.decode('hex'))
            longitude = value.x
            latitude = value.y
        with div(w, class_='form-group'):
            w(label(u'longitude'))
            w(input(type='text', value=longitude,
                    name=field.input_name(form, 'longitude')))
        with div(w, class_='form-group'):
            w(label(u'latitude'))
            w(input(type='text', value=latitude,
                    name=field.input_name(form, 'latitude')))
        return ustring.getvalue()

    def process_field_data(self, form, field):
        """Return process posted value(s) for widget and return something
        understandable by the associated `field`. That value may be correctly
        typed or a string that the field may parse.
        """
        posted = form._cw.form
        longitude = posted.get(field.input_name(form, 'longitude')).strip() or None
        latitude =  posted.get(field.input_name(form, 'latitude')).strip() or None
        return u'POINT(%s %s)' % (longitude, latitude)
