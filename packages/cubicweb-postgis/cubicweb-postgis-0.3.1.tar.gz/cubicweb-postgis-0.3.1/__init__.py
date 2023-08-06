"""cubicweb-postgis application package

Test for postgis
"""

_GEOM_PARAMETERS = ('srid', 'geom_type','coord_dimension')
_GEOG_PARAMETERS = ('geom_type','coord_dimension')

def _update_postgis_metadata(session, rtype, subject, srid, geom_type, coord_dimension):
    """ This fonction update the postgis metadata columns
    """
    # this is specific to postgres
    try:
        dbdriver = session.vreg.config.system_source_config['db-driver']
    except AttributeError: # cw < 3.19.0
        dbdriver = session.vreg.config.sources()['system']['db-driver']
    if dbdriver != 'postgres':
        return # hack waiting for a better solution
    tn = 'cw_%s' % subject.lower()
    gc = 'cw_%s' % rtype.lower()
    params = {'tc': "", 'ts': 'public', 'tn': tn, 'gc': gc,
              'cd': coord_dimension, 's': srid, 't': geom_type}
    # Check if already registered metadata
    cursor = session.system_sql('SELECT * FROM geometry_columns '
                                'WHERE f_table_catalog=%(tc)s AND f_table_schema=%(ts)s '
                                'AND f_table_name=%(tn)s AND f_geometry_column=%(gc)s '
                                'AND coord_dimension=%(cd)s AND srid= %(s)s AND type=%(t)s', params)
    if cursor.fetchall():
        # Already existing meta data
        return
    # Create the entry in geometry_columns
    session.system_sql('INSERT INTO geometry_columns '
                       '(f_table_catalog, f_table_schema, f_table_name, f_geometry_column, '
                       'coord_dimension, srid, type) '
                       'VALUES (%(tc)s, %(ts)s, %(tn)s, %(gc)s, %(cd)s, %(s)s, %(t)s)', params)
    # Add postgis constraints
    session.system_sql("ALTER TABLE %(tn)s ADD CONSTRAINT enforce_dims_%(gc)s "
                       "CHECK (st_ndims(%(gc)s) = %(cd)s)" % params)
    session.system_sql("ALTER TABLE %(tn)s ADD CONSTRAINT enforce_geotype_%(gc)s "
                       "CHECK (geometrytype(%(gc)s) = '%(t)s'::text OR %(gc)s IS NULL)" % params)
    session.system_sql("ALTER TABLE %(tn)s ADD CONSTRAINT enforce_srid_%(gc)s "
                       "CHECK (st_srid(%(gc)s) = %(s)s)" % params)
