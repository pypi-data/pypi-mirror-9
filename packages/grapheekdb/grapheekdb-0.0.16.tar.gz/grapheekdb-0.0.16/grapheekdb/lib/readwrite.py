# -*- coding:utf-8 -*-

import json


class GraphReadWrite(object):

    def write(self, path):
        # Open file soon to avoid building a big structure
        # if file cannot be written
        fp = open(path, 'w')
        # ---
        nodes = []
        edges = []
        node_indexes = []
        edge_indexes = []
        for node in self.V():
            data = node.data().copy()
            data['_id'] = node.get_id()
            nodes.append(data)
        for edge in self.E():
            data = edge.data().copy()
            data['_src'] = edge.inV().next().get_id()  # could be optimized
            data['_tgt'] = edge.outV().next().get_id()  # ditto
            edges.append(data)
        node_indexes = self.get_node_indexes()
        edge_indexes = self.get_edge_indexes()
        dic = {
            'nodes': nodes,
            'edges': edges,
            'node_indexes': node_indexes,
            'edge_indexes': edge_indexes
        }
        json.dump(dic, fp)
        # finished, close file
        fp.close()

    def read(self, path):
        # Open file soon to avoid building a big structure
        # if file cannot be written
        fp = open(path, 'r')
        dic = json.load(fp)
        # reloading nodes :
        node_dump_id_to_node = {}
        for node_data in dic['nodes']:
            data = node_data.copy()
            node_id = data.pop('_id')
            node_dump_id_to_node[node_id] = self.add_node(**data)
        # reloading edges :
        for edge_data in dic['edges']:
            data = edge_data.copy()
            src_id = data.pop('_src')
            tgt_id = data.pop('_tgt')
            src = node_dump_id_to_node[src_id]
            tgt = node_dump_id_to_node[tgt_id]
            self.add_edge(src, tgt, **data)
        # Rebuilding node indexes :
        for fields, filters in dic['node_indexes']:
            self.add_node_index(*fields)
        # Rebuilding edge indexes :
        for fields, filters in dic['edge_indexes']:
            self.add_edge_index(*fields, **filters)
        # finished, close file
        fp.close()
