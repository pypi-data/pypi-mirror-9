import sys
from imposm.geom import load_geom
from shapely import geometry, wkt
import json

def dump_featurecollection(geoms, out):
    result = {'type': 'FeatureCollection', 'features': []}
    for geom in geoms:
        result['features'].append({
            'type': 'Feature',
            'geometry': geometry.mapping(geom),
            'properties': {},
        })

    json.dump(result, out)

def test_limit():
    rtree_limit = load_geom(sys.argv[1])

    result = {'type': 'FeatureCollection', 'features': []}
    for geom in rtree_limit.polygons:
        result['features'].append({
            'type': 'Feature',
            'geometry': geometry.mapping(geom),
            'properties': {},
        })

    json.dump(result, open('/tmp/1-test-10.geojson', 'w'))

def test_clip():
    poly = geometry.asShape(json.load(open('/tmp/complete.geojson')))
    bbox = geometry.Polygon([(7.7, 49.1), (7.8, 49.1), (7.8, 49.2), (7.7, 49.2), (7.7, 49.1)])
    bbox = geometry.Polygon([(7.8, 49.1), (7.7, 49.1), (7.7, 49.2), (7.8, 49.2), (7.8, 49.1)])

    bbox = wkt.loads('POLYGON ((7.7999999999999998 49.1000000000000014, 7.7000000000000002 49.1000000000000014, 7.7000000000000002 49.2000000000000028, 7.7999999999999998 49.2000000000000028, 7.7999999999999998 49.1000000000000014))')

    intersect = bbox.intersection(poly)
    dump_featurecollection([intersect], open('/tmp/part-intersect.geojson', 'w'))


if __name__ == '__main__':
    test_clip()
