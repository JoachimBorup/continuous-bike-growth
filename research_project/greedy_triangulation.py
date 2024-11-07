import copy
import math
import random
from typing import Optional

import igraph as ig
import numpy as np
from tqdm.notebook import tqdm

from src.functions import poipairs_by_distance, new_edge_intersects


def greedy_triangulation_routing(
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
    for e in edgeless_graph.es:
        edgeless_graph.es.delete(e)

    poi_pairs = poipairs_by_distance(graph, pois, return_distances=True)
    if len(poi_pairs) == 0:
        return [], []

    # GT_abstract is the GT with same nodes but euclidian links to keep track of edge crossings
    GT_abstracts = []
    GTs = []
    for prune_quantile in tqdm(prune_quantiles, desc="Greedy triangulation", leave=False):
        GT_abstract = copy.deepcopy(edgeless_graph.subgraph(poi_indices))  # TODO: Pass non-empty graph to GT
        GT_abstract = greedy_triangulation(GT_abstract, poi_pairs, prune_quantile, prune_measure)
        GT_abstracts.append(GT_abstract)

        # Get node pairs we need to route, sorted by distance
        route_node_pairs = {}
        for e in GT_abstract.es:
            route_node_pairs[(e.source_vertex["id"], e.target_vertex["id"])] = e["weight"]
        route_node_pairs = sorted(route_node_pairs.items(), key=lambda x: x[1])

        # Do the routing
        GT_indices = set()
        for poi_pair, distance in route_node_pairs:
            v = graph.vs.find(id=poi_pair[0]).index
            w = graph.vs.find(id=poi_pair[1]).index
            sp = set(graph.get_shortest_paths(v, w, weights="weight", output="vpath")[0])
            GT_indices = GT_indices.union(sp)

        GT = graph.induced_subgraph(GT_indices)
        GTs.append(GT)

    return GTs, GT_abstracts


def greedy_triangulation(
    GT: ig.Graph,
    poi_pairs: list[tuple[tuple[int, int], float]],
    prune_quantile: float = 1,
    prune_measure="betweenness",
) -> ig.Graph:
    """Greedy Triangulation (GT) of a graph GT with an empty edge set.
    Distances between pairs of nodes are given by poi_pairs.

    The GT connects pairs of nodes in ascending order of their distance provided
    that no edge crossing is introduced. It leads to a maximal connected planar
    graph, while minimizing the total length of edges considered.
    See: cardillo2006spp
    """

    # Add edges between POIs in ascending order of distance
    for poi_pair, distance in poi_pairs:
        v = GT.vs.find(id=poi_pair[0]).index
        w = GT.vs.find(id=poi_pair[1]).index
        if not new_edge_intersects(GT, (
            GT.vs[v]["x"], GT.vs[v]["y"],
            GT.vs[w]["x"], GT.vs[w]["y"]
        )):
            GT.add_edge(v, w, weight=distance)

    # Get the measure for pruning
    if prune_measure == "betweenness":
        BW = GT.edge_betweenness(directed=False, weights="weight")
        qt = np.quantile(BW, 1 - prune_quantile)
        sub_edges = []
        for c, e in enumerate(GT.es):
            if BW[c] >= qt:
                sub_edges.append(c)
            GT.es[c]["bw"] = BW[c]
            GT.es[c]["width"] = math.sqrt(BW[c] + 1) * 0.5
        # Prune
        return GT.subgraph_edges(sub_edges)

    if prune_measure == "closeness":
        CC = GT.closeness(vertices=None, weights="weight")
        qt = np.quantile(CC, 1 - prune_quantile)
        sub_nodes = []
        for c, v in enumerate(GT.vs):
            if CC[c] >= qt:
                sub_nodes.append(c)
            GT.vs[c]["cc"] = CC[c]
        return GT.induced_subgraph(sub_nodes)

    if prune_measure == "random":
        # For reproducibility
        random.seed(0)
        # Create a random order for the edges
        edge_order = random.sample(range(GT.ecount()), k=GT.ecount())
        # "lower" and + 1 so smallest quantile has at least one edge
        index = np.quantile(np.arange(len(edge_order)), prune_quantile, interpolation="lower") + 1
        return GT.subgraph_edges(edge_order[:index])

    raise ValueError(f"Unknown pruning measure: {prune_measure}")
