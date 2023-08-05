# Copyright 2011, 2012 Omniscale (http://omniscale.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import defaultdict
from multiprocessing import Process

import threading
from Queue import Queue

from imposm.base import OSMElem
from imposm.geom import IncompletePolygonError
from imposm.mapping import DropElem, PolygonTable
from imposm.multipolygon import RelationBuilder
from imposm.util import setproctitle


import logging
log = logging.getLogger(__name__)

class ImporterProcess(Process):
    name = 'importer'

    def __init__(self, in_queue, db, mapper, osm_cache, dry_run):
        Process.__init__(self)
        self.daemon = True
        setproctitle('imposm %s process' % self.name)

        self.in_queue = in_queue
        self.mapper = mapper
        self.osm_cache = osm_cache
        self.db = db
        self.dry_run = dry_run
        self.db_queue = Queue(256)

    def run(self):
        self.setup()
        # cProfile.runctx('self.doit()', globals(), locals(), 'profile%s.dat' % (self.name,))
        self.doit()
        self.teardown()

    def setup(self):
        self.db_importer = threading.Thread(target=self.db_importer,
            args=(self.db_queue, self.db),
            kwargs=dict(dry_run=self.dry_run))
        self.db_importer.start()

    def doit(self):
        pass

    def teardown(self):
        self.osm_cache.close_all()
        self.db_queue.put(None)
        self.db_importer.join()

class TupleBasedImporter(ImporterProcess):
    def db_importer(self, queue, db, dry_run=False):
        db.reconnect()
        mappings = defaultdict(list)

        while True:
            data = queue.get()
            if data is None:
                break

            mapping, osm_id, osm_elem, extra_args = data
            insert_data = mappings[mapping]

            if isinstance(osm_elem.geom, (list)):
                for geom in osm_elem.geom:
                    insert_data.append((osm_id, db.geom_wrapper(geom)) + tuple(extra_args))
            else:
                insert_data.append((osm_id, db.geom_wrapper(osm_elem.geom)) + tuple(extra_args))

            if len(insert_data) >= 128:
                if not dry_run:
                    db.insert(mapping, insert_data)
                del mappings[mapping]

        # flush
        for mapping, insert_data in mappings.iteritems():
            if not dry_run:
                db.insert(mapping, insert_data)

    def insert(self, mappings, osm_id, geom, tags):
        inserted = False
        for type, ms in mappings:
            for m in ms:
                osm_elem = OSMElem(osm_id, geom, type, tags)
                try:
                    m.filter(osm_elem)
                    m.build_geom(osm_elem)
                    extra_args = m.field_values(osm_elem)
                    self.db_queue.put((m, osm_id, osm_elem, extra_args))
                    inserted = True
                except DropElem:
                    pass
        return inserted

class DictBasedImporter(ImporterProcess):
    def db_importer(self, queue, db, dry_run=False):
        db.reconnect()
        insert_data = []

        while True:
            data = queue.get()
            if data is None:
                break

            data['geometry'] = db.geom_wrapper(data['geometry'])
            insert_data.append(data)

            if len(insert_data) >= 128:
                if not dry_run:
                    db.insert(insert_data)
                insert_data = []
        # flush
        if not dry_run:
            db.insert(insert_data)


    def insert(self, mappings, osm_id, geom, tags):
        inserted = False
        osm_objects = {}

        for type, ms in mappings:
            for m in ms:
                osm_elem = OSMElem(osm_id, geom, type, tags)
                try:
                    m.filter(osm_elem)
                except DropElem:
                    continue

                if m.geom_type in osm_objects:
                    obj = osm_objects[m.geom_type]
                    obj['fields'].update(m.field_dict(osm_elem))
                    obj['fields'][type[0]] = type[1]
                    obj['mapping_names'].append(m.name)
                else:
                    try:
                        m.build_geom(osm_elem)
                    except DropElem:
                        continue
                    obj = {}
                    obj['fields'] = m.field_dict(osm_elem)
                    obj['fields'][type[0]] = type[1]
                    obj['osm_id'] = osm_id
                    obj['geometry'] = osm_elem.geom
                    obj['mapping_names'] = [m.name]
                    osm_objects[m.geom_type] = obj

                inserted = True

        for obj in osm_objects.itervalues():
            if isinstance(obj['geometry'], (list, )):
                for geom in obj['geometry']:
                    obj_part = obj.copy()
                    obj_part['geometry'] = geom
                    self.db_queue.put(obj_part)
            else:
                self.db_queue.put(obj)

        return inserted


class NodeProcess(ImporterProcess):
    name = 'node'

    def doit(self):
        while True:
            nodes = self.in_queue.get()
            if nodes is None:
                break

            for node in nodes:
                mappings = self.mapper.for_nodes(node.tags)
                if not mappings:
                    continue

                self.insert(mappings, node.osm_id, node.coord, node.tags)

class NodeProcessDict(NodeProcess, DictBasedImporter):
    pass

class NodeProcessTuple(NodeProcess, TupleBasedImporter):
    pass


def filter_out_polygon_mappings(mappings):
    result = []
    for tag, ms in mappings:
        ms = [m for m in ms if m.table != PolygonTable]
        if ms:
            result.append((tag, ms))
    return result

class WayProcess(ImporterProcess):
    name = 'way'

    def doit(self):
        coords_cache = self.osm_cache.coords_cache(mode='r')
        inserted_ways_cache = self.osm_cache.inserted_ways_cache(mode='r')
        inserted_ways = iter(inserted_ways_cache)

        try:
            skip_id = inserted_ways.next()
        except StopIteration:
            skip_id = 2**64

        while True:
            ways = self.in_queue.get()
            if ways is None:
                break

            for way in ways:
                # forward to the next skip id that is not smaller
                # than our current id
                while skip_id < way.osm_id:
                    try:
                        skip_id = inserted_ways.next()
                    except StopIteration:
                        skip_id = 2**64

                mappings = self.mapper.for_ways(way.tags)
                if not mappings:
                    continue

                if skip_id == way.osm_id:
                    # skip polygon mappings, way was already inserted as MultiPolygon
                    mappings = filter_out_polygon_mappings(mappings)
                    if not mappings:
                        continue

                coords = coords_cache.get_coords(way.refs)

                if not coords:
                    log.debug('missing coords for way %s', way.osm_id)
                    continue

                self.insert(mappings, way.osm_id, coords, way.tags)

class WayProcessDict(WayProcess, DictBasedImporter):
    pass

class WayProcessTuple(WayProcess, TupleBasedImporter):
    pass

class RelationProcess(ImporterProcess):
    name = 'relation'

    def __init__(self, in_queue, db, mapper, osm_cache, dry_run, inserted_way_queue):
        super(RelationProcess, self).__init__(in_queue, db, mapper, osm_cache, dry_run)
        self.inserted_way_queue = inserted_way_queue

    def doit(self):
        coords_cache = self.osm_cache.coords_cache(mode='r')
        ways_cache = self.osm_cache.ways_cache(mode='r')

        while True:
            relations = self.in_queue.get()
            if relations is None:
                break

            for relation in relations:
                builder = RelationBuilder(relation, ways_cache, coords_cache)
                try:
                    builder.build()
                except IncompletePolygonError, ex:
                    if str(ex):
                        log.debug(ex)
                    continue
                mappings = self.mapper.for_relations(relation.tags)

                inserted = False
                if mappings:
                    inserted = self.insert(mappings, relation.osm_id, relation.geom, relation.tags)
                if inserted and any(m.skip_inserted_ways for _, ms in mappings for m in ms):
                    for w in relation.ways:
                        if mappings_intersect(mappings, self.mapper.for_relations(w.tags)):
                            self.inserted_way_queue.put(w.osm_id)


def mappings_intersect(a, b):
    """
    True if `a` and `b` share a mapping.
    Mapping is a list of ((key, value), (mapping1, mapping2,...)).

    >>> mappings_intersect([(('waterway', 'riverbank'), ('mapping_waterareas',))],
    ... [(('waterway', 'riverbank'), ('mapping_waterareas',))])
    True
    >>> mappings_intersect([(('waterway', 'riverbank'), ('mapping_waterareas',))],
    ... [(('place', 'island'), ('mapping_landusage',))])
    False
    >>> mappings_intersect([(('waterway', 'riverbank'), ('mapping_waterareas',))],
    ... [(('place', 'island'), ('mapping_landusage',)),
    ...  (('waterway', 'riverbank'), ('mapping_waterareas',))])
    True
    """

    for a_key_val, a_mappings in a:
        for a_map in a_mappings:
            for b_key_val, b_mappings in b:
                for b_map in b_mappings:
                    if a_key_val == b_key_val and a_map == b_map:
                        return True

    return False

class RelationProcessDict(RelationProcess, DictBasedImporter):
    pass

class RelationProcessTuple(RelationProcess, TupleBasedImporter):
    pass
