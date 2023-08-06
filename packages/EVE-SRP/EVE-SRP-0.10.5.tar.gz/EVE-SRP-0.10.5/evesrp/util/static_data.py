from __future__ import unicode_literals
from tempfile import mkdtemp
from urllib.parse import urlparse
from os import path
import bz2
import requests
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.sql import select


meta = MetaData()


def download_to_temp(url, dest_path=None):
    if dest_path is None:
        dest_path = mkdtemp()
    parsed_url = urlparse(url)
    filename = path.basename(parsed_url.path)
    dest = path.join(dest_path, filename)
    ext = path.splitext(filename)[1]
    response = requests.get(url, stream=True)
    bunzip = False
    if ext in ('.bz2', '.bz'):
        decompressor = bz2.BZ2Decompressor()
        bunzip = True
    with open(dest, 'wb') as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:
                if bunzip:
                    inflated = decompressor.decompress(chunk)
                    if inflated:
                        f.write(inflated)
                else:
                    f.write(chunk)
    return dest


def bind_engine(sqlite_path):
    engine = create_engine('sqlite:///' + sqlite_path)
    meta.bind = engine
    meta.reflect()
    return engine


def get_systems(engine):
    systemNames = {}
    sel = select([meta.tables['mapSystems'].c.solarSystemID,
            meta.tables['mapSystems'].c.solarSystemName])
    result = engine.execute(sel)
    for row in result:
        systemNames[row[0]] = row[1]
    result.close()
    return systemNames


def get_constellations(engine):
    constellationNames = {}
    sel = select([meta.tables['mapConstellations'].c.constellationID,
            meta.tables['mapConstellations'].c.constellationName])
    result = engine.execute(sel)
    for row in result:
        constellationNames[row[0]] = row[1]
    result.close()
    return constellationNames


def get_regions(engine):
    regionNames = {}
    sel = select([meta.tables['mapRegions'].c.regionID,
            meta.tables['mapRegions'].c.regionName])
    result = engine.execute(sel)
    for row in result:
        regionNames[row[0]] = row[1]
    result.close()
    return regionNames


def get_system_constellations(engine, constellation_names):
    systemConstellations = {}
    sel = select([meta.tables['mapSystems'].c.solarSystemName,
            meta.tables['mapSystems'].c.constellationID])
    result = engine.execute(sel)
    for row in result:
        systemConstellations[row[0]] = constellation_names[row[1]]
    result.close()
    return systemConstellations


def get_constellation_regions(engine, region_names):
    constellationRegions = {}
    sel = select([meta.tables['mapConstellations'].c.constellationName,
            meta.tables['mapConstellations'].c.regionID])
    result = engine.execute(sel)
    for row in result:
        constellationRegions[row[0]] = region_names[row[1]]
    result.close()
    return constellationRegions


def get_ships(engine):
    # Get the Ship category ID
    cat_sel = select([meta.tables['invCategories'].c.categoryID]).\
            where(meta.tables['invCategories'].c.categoryName == 'Ship').limit(1)
    result = engine.execute(cat_sel)
    cat_id = result.fetchone()[0]
    result.close()

    # Get groups in this category
    group_sel = select([meta.tables['invGroups'].c.groupID]).where(
            meta.tables['invGroups'].c.categoryID == cat_id)
    group_result = engine.execute(group_sel)

    # get typeIDs and names
    names = {}
    for group_row in group_result:
        group_id = group_row[0]
        type_sel = select([meta.tables['invTypes'].c.typeID,
                meta.tables['invTypes'].c.typeName]).\
                where(meta.tables['invTypes'].c.groupID == group_id)
        type_result = engine.execute(type_sel)
        for row in type_result:
            names[row[0]] = row[1]
        type_result.close()
    group_result.close()

    return names


def update_static_data(data_dir=None):
    db_path = download_to_temp('https://www.fuzzwork.co.uk/dump/'
                               'sqlite-latest.sqlite.bz2')
    engine = bind_engine(db_path)
    # stuff...
