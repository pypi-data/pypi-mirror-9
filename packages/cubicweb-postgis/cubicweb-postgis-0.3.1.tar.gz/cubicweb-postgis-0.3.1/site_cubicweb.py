
# USE
# cubicweb-ctl db-create <instance>
# WARNING !!! DO NOT initialize the database
# Add postgis, e.g.:
# psql <database> -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
# psql <database> -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql
# cubicweb-ctl db-init <instance>

from logilab.database import FunctionDescr
from logilab.database import get_db_helper
from logilab.database.sqlgen import SQLExpression

from yams import register_base_type

from rql.utils import register_function

from cubes.postgis import _GEOM_PARAMETERS, _GEOG_PARAMETERS

# register new base type
register_base_type('Geometry', _GEOM_PARAMETERS)
register_base_type('Geography', _GEOG_PARAMETERS)

# Add the datatype to the helper mapping
pghelper = get_db_helper('postgres')
sqlitehelper = get_db_helper('sqlite')
pghelper.TYPE_MAPPING['Geometry'] = 'geometry'
sqlitehelper.TYPE_MAPPING['Geometry'] = 'text'

pghelper.TYPE_MAPPING['Geography'] = 'geography'
sqlitehelper.TYPE_MAPPING['Geography'] = 'text'

# Add a converter for Geometry
def convert_geom(x):
    if isinstance(x, (tuple, list)):
        # We give the (Geometry, SRID)
        return SQLExpression('ST_GeomFromText(%(geo)s, %(srid)s)', geo=x[0], srid=x[1])
    else:
        # We just give the Geometry
        return SQLExpression('ST_GeomFromText(%(geo)s, %(srid)s)', geo=x, srid=-1)

def convert_geog(x):
    # takes only a Geometry type, assumes GPS srid
    return SQLExpression('ST_GeogFromText(%(geo)s)', geo=x)

# Add the converter function to the known SQL_CONVERTERS
pghelper.TYPE_CONVERTERS['Geometry'] = convert_geom
pghelper.TYPE_CONVERTERS['Geography'] = convert_geog
# actually don't care of sqlite, it's just to make it possible to test
sqlitehelper.TYPE_CONVERTERS['Geometry'] = str
sqlitehelper.TYPE_CONVERTERS['Geography'] = str



class ST_EQUALS(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Bool'


class ST_INTERSECTS(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Bool'

class ST_INTERSECTION(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Geometry'


class ST_OVERLAPS(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Bool'

class ST_CROSSES(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Bool'

class ST_TOUCHES(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Bool'


class ST_GEOMETRYN(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Geometry'


class ST_WITHIN(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Bool'


class ST_CONTAINS(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Bool'


class ST_DWITHIN(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Float'


class ST_LENGTH(FunctionDescr):
    minargs = 1
    maxargs = 1
    supported_backends = ('postgres',)
    rtype = 'Float'


class ST_DISTANCE(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Float'


class ST_DISTANCE_SPHERE(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Float'


class ST_AREA(FunctionDescr):
    minargs = 1
    maxargs = 1
    supported_backends = ('postgres',)
    rtype = 'Float'


class ST_NUMINTERIORRINGS(FunctionDescr):
    minargs = 1
    maxargs = 1
    supported_backends = ('postgres',)
    rtype = 'Int'


class ST_SIMPLIFY(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Geometry'


class ST_TRANSFORM(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Geometry'


class ST_ASGEOJSON(FunctionDescr):
    minargs = 1
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'String'

class ST_GEOMFROMTEXT(FunctionDescr):
    minargs = 1
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Geometry'

class ST_GEOGFROMTEXT(FunctionDescr):
    minargs = 1
    maxargs = 1
    supported_backends = ('postgres',)
    rtype = 'Geography'

class ST_COVERS(FunctionDescr):
    minargs = 1
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Bool'

class GEOMETRY(FunctionDescr):
    minargs = 1
    maxargs = 1
    supported_backends = ('postgres',)
    rtype = 'Geometry'

class ST_UNION(FunctionDescr):
    aggregat = True
    minargs = 1
    supported_backends = ('postgres',)
    rtype = 'Geometry'


class DISPLAY(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'String'

    def as_sql_postgres(self, args):
        return 'ST_ASGeoJSON(ST_Transform(%s, %s))' % (args[0], args[1])


class ST_MAKEPOINT(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Geometry'


class ST_SETSRID(FunctionDescr):
    minargs = 2
    maxargs = 2
    supported_backends = ('postgres',)
    rtype = 'Geometry'


class ST_X(FunctionDescr):
    minargs = 1
    maxargs = 1
    supported_backends = ('postgres',)
    rtype = 'Float'


class ST_Y(FunctionDescr):
    minargs = 1
    maxargs = 1
    supported_backends = ('postgres',)
    rtype = 'Float'


class ST_Z(FunctionDescr):
    minargs = 1
    maxargs = 1
    supported_backends = ('postgres',)
    rtype = 'Float'


class ST_M(FunctionDescr):
    minargs = 1
    maxargs = 1
    supported_backends = ('postgres',)
    rtype = 'Float'


register_function(ST_EQUALS)
register_function(ST_INTERSECTS)
register_function(ST_INTERSECTION)
register_function(ST_OVERLAPS)
register_function(ST_CROSSES)
register_function(ST_TOUCHES)
register_function(ST_GEOMETRYN)
register_function(ST_WITHIN)
register_function(ST_CONTAINS)
register_function(ST_DWITHIN)
register_function(ST_LENGTH)
register_function(ST_DISTANCE)
register_function(ST_AREA)
register_function(ST_NUMINTERIORRINGS)
register_function(ST_SIMPLIFY)
register_function(ST_TRANSFORM)
register_function(DISPLAY)
register_function(ST_ASGEOJSON)
register_function(ST_GEOMFROMTEXT)
register_function(ST_GEOGFROMTEXT)
register_function(ST_COVERS)
register_function(GEOMETRY)
register_function(ST_UNION)
register_function(ST_MAKEPOINT)
register_function(ST_SETSRID)
register_function(ST_DISTANCE_SPHERE)
register_function(ST_X)
register_function(ST_Y)
register_function(ST_Z)
register_function(ST_M)
