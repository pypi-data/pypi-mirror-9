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

"""cubicweb-postgis postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""
from cubes.postgis import _update_postgis_metadata

# Get the entity schema for our type 'Geometry'
eschema = fsschema.eschema('Geometry')
# Get all the objects (as a list)
orelations = eschema.object_relations()

pushed_relations = set()
for rtype in orelations:
    for d in rtype.rdefs.values():
        _update_postgis_metadata(session, rtype.type, d.subject.type,
                                 d.srid, d.geom_type, d.coord_dimension)

session.commit()
