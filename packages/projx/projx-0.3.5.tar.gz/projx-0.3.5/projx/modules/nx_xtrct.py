# -*- coding: utf-8 -*-
"""
Extractor and stream generator for the NetworkX data source.
"""
from projx import nxprojx


def nx_extractor(extractor_json, graph):
    """
    Parses etl extractor JSON and produces all of the data necessary for
    transformation.

    :param extractor: JSON.
    :param graph: networkx.Graph
    :returns: Dict.
    """
    proj_type = extractor_json.get("type", "subgraph")
    traversal = extractor_json.get("traversal", [])
    nodes = traversal[0::2]
    edges = traversal[1::2]
    node_type_attr = extractor_json.get("node_type_attr", "type")
    edge_type_attr = extractor_json.get("edge_type_attr", "type")
    try:
        node_type_seq = [node["node"].get(node_type_attr, "") for node in nodes]
        edge_type_seq = [edge["edge"].get(edge_type_attr, "") for edge in edges]
        node_alias = [node["node"]["alias"] for node in nodes]
    except KeyError:
        raise Exception("Please define valid traversal sequence")
    graph = nxprojx.reset_index(graph)
    paths = nxprojx.match(node_type_seq, edge_type_seq, graph, node_alias,
                          node_type_attr, edge_type_attr)
    if proj_type != "graph":
        paths = list(paths)
        graph = nxprojx.build_subgraph(paths, graph, records=True)
    extractor_json.update({"graph": graph, "paths": paths,
                           "node_type_attr": node_type_attr,
                           "edge_type_attr": edge_type_attr})
    return extractor_json


def nx_stream(transformers, extractor_json):
    """
    Pipeline transformer for NetworkX graph. Multiple transformations.

    :param transformers: List.
    :param projector: projx.NXprojector
    :param graph: networkx.Graph
    :param paths: List of lists.
    :returns: networkx.Graph
    """
    paths = extractor_json["paths"]
    for record in paths:
        for transformer in transformers:
            trans_kwrd = transformer.keys()[0]
            trans = transformer[trans_kwrd]
            yield record, trans_kwrd, trans
