import copy
import math
import random
from typing import Optional

import igraph as ig
import numpy as np
from tqdm.notebook import tqdm

from src.functions import poipairs_by_distance, new_edge_intersects


def greedy_triangulation_in_steps(
    graph: ig.Graph,
    pois: list[int],
    numIterations: int,
    subgraph_percentages: list[float],
    prune_quantiles: Optional[list[float]] = None,
    prune_measure: str = "betweenness",
) -> tuple[list[ig.Graph], list[ig.Graph]]:
    for percentage in subgraph_percentages :
        if 1 < percentage < 0:
            raise ValueError("Subgraph percentage must be between 0 and 1")
    if (sum(subgraph_percentages)) != 1.0:
        raise ValueError("Subgraph percentages must sum to 1.0")
    if prune_quantiles is None:
        prune_quantiles = [1]
    if len(pois) < 2:
        return [], []
    poi_pairs = poipairs_by_distance(graph, pois, return_distances=True)
    poi_indices = {graph.vs.find(id=poi).index for poi in pois}
    if len(poi_pairs) == 0:
        return [], []

    subgraph_pois = random.sample(pois, int(len(pois) * subgraph_percentages))
    # subgraph_poi_indices = {graph.vs.find(id=poi).index for poi in subgraph_pois}
    subgraph_poi_pairs = poipairs_by_distance(graph, subgraph_pois, return_distances=True)

    edgeless_graph = copy.deepcopy(graph)
    for edge in edgeless_graph.es:
        edgeless_graph.es.delete(edge)

    gts, abstract_gts = [], []
    for prune_quantile in tqdm(
        prune_quantiles, desc=f"Greedy triangulation on {subgraph_percentage * 100}% subgraph", leave=False
    ):
        
        pois_continously = []
        abstract_gt = copy.deepcopy(edgeless_graph.subgraph(poi_indices))
        pruned_graph = abstract_gt
        gt_edges = None
        for iter in range(0, numIterations):

            subgraph_pois = random.sample(pois, int(len(pois) * subgraph_percentages[iter]))
            pois_continously = pois_continously.append(subgraph_pois)
            # subgraph_poi_indices = {graph.vs.find(id=poi).index for poi in subgraph_pois}
            subgraph_poi_pairs = poipairs_by_distance(graph, pois_continously, return_distances=True)

            gt_edges = gt_edges + _greedy_triangulation(pruned_graph, subgraph_poi_pairs, gt_edges)
            # TODO: We should only prune edges added in the last greedy triangulation
            pruned_graph = prune_graph(pruned_graph, prune_quantile, prune_measure)
  
            abstract_gts.append(pruned_graph)

        # Get node pairs we need to route, sorted by distance
        route_node_pairs = {}
        for edge in pruned_graph.es:
            route_node_pairs[(edge.source_vertex["id"], edge.target_vertex["id"])] = edge["weight"]
        route_node_pairs = sorted(route_node_pairs.items(), key=lambda x: x[1])

        # Do the routing
        gt_indices = set()
        for poi_pair, _ in route_node_pairs:
            v = graph.vs.find(id=poi_pair[0]).index
            w = graph.vs.find(id=poi_pair[1]).index
            sp = set(graph.get_shortest_path(v, w, weights="weight", output="vpath"))
            gt_indices = gt_indices.union(sp)

        abstract_gts.append(pruned_graph)
        gts.append(graph.induced_subgraph(gt_indices.union(poi_indices)))

    return gts, abstract_gts

def _greedy_triangulation_routing(
    graph: ig.Graph,
    pois: list[int],
    prune_quantiles: Optional[list[float]] = None,
    prune_measure: str = "betweenness"
) -> tuple[list[ig.Graph], list[ig.Graph]]:
    """
    Perform Greedy Triangulation (GT) on a subset of nodes (points of interest, POIs) in a graph,
    followed by routing to connect the GT graph up to a specified quantile of the chosen pruning measure.

    This method builds a maximal connected planar subgraph by connecting pairs of POI nodes in ascending
    order of their shortest path distances, ensuring that no edge crossings are introduced.
    The GT is then routed to create a connected graph within the specified pruning quantiles, resulting
    in a list of routed GTs and their abstract versions (Euclidean-based to track edge crossings).

    :param graph: The input graph to perform GT and routing on.
    :param pois: A list of node IDs in the graph representing the POIs to connect.
    :param prune_quantiles: Quantile values specifying the degree of pruning applied to the GT.
        Each quantile defines a pruned version of the GT graph based on the specified pruning measure.
        If None, no pruning is applied (default is [1], representing no pruning).
    :param prune_measure: The measure used for pruning edges in the GT.
        The options are 'betweenness', 'closeness', and 'random' (default is 'betweenness').
    :return: A tuple containing lists of the routed GTs and their abstract versions.

    Reference:
    Alessio Cardillo, Salvatore Scellato, Vito Latora, and Sergio Porta (2006).
    Structural properties of planar graphs of urban street patterns.
    Physical Review E, 73(6), 066107. https://doi.org/10.1103/PhysRevE.73.066107
    """
    if prune_quantiles is None:
        prune_quantiles = [1]
    if len(pois) < 2:
        return [], []  # We can't do anything with less than 2 POIs

    poi_indices = set()
    for poi in pois:
        poi_indices.add(graph.vs.find(id=poi).index)

    edgeless_graph = copy.deepcopy(graph)
    for edge in edgeless_graph.es:
        edgeless_graph.es.delete(edge)

    poi_pairs = poipairs_by_distance(graph, pois, return_distances=True)
    if len(poi_pairs) == 0:
        return [], []

    abstract_gts = []
    gts = []
    for prune_quantile in tqdm(prune_quantiles, desc="Greedy triangulation", leave=False):
        abstract_gt = copy.deepcopy(edgeless_graph.subgraph(poi_indices))

        _greedy_triangulation(abstract_gt, poi_pairs)
        pruned_graph = prune_graph(abstract_gt, prune_quantile, prune_measure)

        # Get node pairs we need to route, sorted by distance
        route_node_pairs = {}
        for edge in pruned_graph.es:
            route_node_pairs[(edge.source_vertex["id"], edge.target_vertex["id"])] = edge["weight"]
        route_node_pairs = sorted(route_node_pairs.items(), key=lambda x: x[1])

        # Do the routing
        gt_indices = set()
        for poi_pair, distance in route_node_pairs:
            v = graph.vs.find(id=poi_pair[0]).index
            w = graph.vs.find(id=poi_pair[1]).index
            sp = set(graph.get_shortest_paths(v, w, weights="weight", output="vpath")[0])
            gt_indices = gt_indices.union(sp)

        abstract_gts.append(pruned_graph)
        gts.append(graph.induced_subgraph(gt_indices.union(poi_indices)))

    return gts, abstract_gts


def _greedy_triangulation(graph: ig.Graph, poi_pairs: list[tuple[tuple[int, int], float]]) -> set[int]:
    """Greedy Triangulation (GT) of a graph GT with an empty edge set.
    Distances between pairs of nodes are given by poi_pairs.

    The GT connects pairs of nodes in ascending order of their distance provided
    that no edge crossing is introduced. It leads to a maximal connected planar
    graph, while minimizing the total length of edges considered.
    See: cardillo2006spp
    """
    edges_added = set()

    # Add edges between POIs in ascending order of distance
    for poi_pair, distance in poi_pairs:
        v = graph.vs.find(id=poi_pair[0]).index
        w = graph.vs.find(id=poi_pair[1]).index
        if not new_edge_intersects(graph, (
            graph.vs[v]["x"], graph.vs[v]["y"],
            graph.vs[w]["x"], graph.vs[w]["y"]
        )):
            edges_added.add(graph.add_edge(v, w, weight=distance).index)

    return edges_added


def prune_graph(
    graph: ig.Graph,
    prune_quantile: float,
    prune_measure: str,
    gt_edges: Optional[set[int]] = None,
) -> ig.Graph:
    """
    Prune a graph based on the given measure and quantile.
    The pruning measure can be one of:

    - 'betweenness': Edge betweenness.
    - 'closeness': Vertex closeness centrality.
    - 'random': Random edge pruning.

    :param graph: The input graph to prune.
    :param prune_quantile: The quantile value specifying the degree of pruning.
    :param prune_measure: The measure used for pruning edges in the graph.
    :param gt_edges: The indices of the edges added during the last greedy triangulation. Defaults to all edges.
    :return: The pruned graph - a subgraph of the input graph.
    """
    prune_measures = {
        "betweenness": _prune_betweenness,
        "closeness": _prune_closeness,
        "random": _prune_random,
    }

    if not gt_edges:
        gt_edges = set(range(graph.ecount()))

    if prune_measure in prune_measures:
        return prune_measures[prune_measure](graph, prune_quantile, gt_edges)

    raise ValueError(f"Unknown pruning measure: {prune_measure}")


def _prune_betweenness(graph: ig.Graph, prune_quantile: float, gt_edges: set[int]) -> ig.Graph:
    """
    Prune a graph based on edge betweenness, keeping only the edges with betweenness above the given quantile.
    The betweenness of an edge is the number of shortest paths that pass through it.
    """
    edge_betweenness = graph.edge_betweenness(directed=False, weights="weight")
    # Consider only the edges added during the last greedy triangulation
    quantile = np.quantile([edge_betweenness[i] for i in gt_edges], 1 - prune_quantile)
    subgraph_edges = []

    for i in range(graph.ecount()):
        if i in gt_edges and edge_betweenness[i] >= quantile:
            subgraph_edges.append(i)
        graph.es[i]["bw"] = edge_betweenness[i]
        # For visualization, scale the width of the edge based on its betweenness
        graph.es[i]["width"] = math.sqrt(edge_betweenness[i] + 1) * 0.5

    return graph.subgraph_edges(subgraph_edges, delete_vertices=False)


def _prune_closeness(graph: ig.Graph, prune_quantile: float) -> ig.Graph:
    """
    Prune a graph based on closeness centrality, keeping only the vertices with closeness above the given quantile.
    The closeness of a vertex measures how close it is to all other vertices in the graph.
    """
    closeness = graph.closeness(vertices=None, weights="weight")
    quantile = np.quantile(closeness, 1 - prune_quantile)
    subgraph_vertices = []

    for i in range(graph.vcount()):
        if closeness[i] >= quantile:
            subgraph_vertices.append(i)
        graph.vs[i]["cc"] = closeness[i]

    # TODO: Check whether vertices are deleted
    return graph.induced_subgraph(subgraph_vertices)


def _prune_random(graph: ig.Graph, prune_quantile: float) -> ig.Graph:
    """Prune a graph randomly, keeping only the edges up to the given quantile."""
    # Create a random order for the edges
    edge_order = random.sample(range(graph.ecount()), k=graph.ecount())
    # "lower" and + 1 so smallest quantile has at least one edge
    index = np.quantile(np.arange(len(edge_order)), prune_quantile, method="lower") + 1
    return graph.subgraph_edges(edge_order[:index], delete_vertices=False)
