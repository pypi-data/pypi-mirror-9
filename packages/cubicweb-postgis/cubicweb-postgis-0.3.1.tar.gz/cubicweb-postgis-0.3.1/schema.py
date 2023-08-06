# -*- coding: utf-8 -*-
# copyright 2012-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-postgis schema"""
from yams.buildobjs import make_type
Geometry = make_type('Geometry')
# Example of use:
#     Geometry(geom_type='POINT', srid=-1, coord_dimension=2)

Geography = make_type('Geography')
# Example of use:
#     Geography(geom_type='POINT', coord_dimension=2)

