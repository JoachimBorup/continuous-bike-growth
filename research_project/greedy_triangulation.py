# import copy
# import math
# import random
# from typing import Optional
#
# import igraph as ig
# import numpy as np
# from tqdm.notebook import tqdm
#
# from src.functions import poipairs_by_distance, new_edge_intersects


def greedy_triangulation_in_steps(
    graph: ig.Graph,
    pois: list[int],
    subgraph_percentage: float,
    prune_quantiles: Optional[list[float]] = None,
    prune_measure: str = "betweenness",
) -> tuple[list[ig.Graph], list[ig.Graph]]:
    if 1 < subgraph_percentage < 0:
        raise ValueError("Subgraph percentage must be between 0 and 1")
    if prune_quantiles is None:
        prune_quantiles = [1]
    if len(pois) < 2:
        return [], []
    poi_pairs = poipairs_by_distance(graph, pois, return_distances=True)
    poi_indices = {graph.vs.find(id=poi).index for poi in pois}
    if len(poi_pairs) == 0:
        return [], []

    random.seed(0)
    subgraph_pois = random.sample(pois, int(len(pois) * subgraph_percentage))
    # subgraph_poi_indices = {graph.vs.find(id=poi).index for poi in subgraph_pois}
    subgraph_poi_pairs = poipairs_by_distance(graph, subgraph_pois, return_distances=True)

    edgeless_graph = copy.deepcopy(graph)
    for edge in edgeless_graph.es:
        edgeless_graph.es.delete(edge)

    GTs, GT_abstracts = [], []
    for prune_quantile in tqdm(prune_quantiles, desc=f"Greedy triangulation on {subgraph_percentage * 100}% subgraph", leave=False):
        # GT_abstract is the GT with same nodes but euclidian links to keep track of edge crossings
        GT_abstract = copy.deepcopy(edgeless_graph.subgraph(poi_indices))

        _greedy_triangulation(GT_abstract, subgraph_poi_pairs)
        pruned_graph = prune_graph(GT_abstract, prune_quantile, prune_measure)

        # Add the rest of the vertices to the GT graph and run greedy triangulation again
        _greedy_triangulation(pruned_graph, poi_pairs)
        pruned_graph = prune_graph(GT_abstract, prune_quantile, prune_measure)

        # Get node pairs we need to route, sorted by distance
        route_node_pairs = {}
        for edge in pruned_graph.es:
            route_node_pairs[(edge.source_vertex["id"], edge.target_vertex["id"])] = edge["weight"]
        route_node_pairs = sorted(route_node_pairs.items(), key=lambda x: x[1])

        # Do the routing
        GT_indices = set()
        for poi_pair, _ in route_node_pairs:
            v = graph.vs.find(id=poi_pair[0]).index
            w = graph.vs.find(id=poi_pair[1]).index
            sp = set(graph.get_shortest_path(v, w, weights="weight", output="vpath"))
            GT_indices = GT_indices.union(sp)

        GT = graph.induced_subgraph(GT_indices.union(poi_indices))
        GTs.append(GT)

    return GTs, GT_abstracts


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

    GT_abstracts = []
    GTs = []
    for prune_quantile in tqdm(prune_quantiles, desc="Greedy triangulation", leave=False):
        # GT_abstract is the GT with same nodes but euclidian links to keep track of edge crossings
        GT_abstract = copy.deepcopy(edgeless_graph.subgraph(poi_indices))
        _greedy_triangulation(GT_abstract, poi_pairs)
        pruned_graph = prune_graph(GT_abstract, prune_quantile, prune_measure)
        GT_abstracts.append(GT_abstract)

        # Get node pairs we need to route, sorted by distance
        route_node_pairs = {}
        for edge in pruned_graph.es:
            route_node_pairs[(edge.source_vertex["id"], edge.target_vertex["id"])] = edge["weight"]
        route_node_pairs = sorted(route_node_pairs.items(), key=lambda x: x[1])

        # Do the routing
        GT_indices = set()
        for poi_pair, distance in route_node_pairs:
            v = graph.vs.find(id=poi_pair[0]).index
            w = graph.vs.find(id=poi_pair[1]).index
            sp = set(graph.get_shortest_paths(v, w, weights="weight", output="vpath")[0])
            GT_indices = GT_indices.union(sp)

        GT = graph.induced_subgraph(GT_indices.union(poi_indices))
        GTs.append(GT)

    return GTs, GT_abstracts


def _greedy_triangulation(
    graph: ig.Graph,
    poi_pairs: list[tuple[tuple[int, int], float]],
) -> None:
    """Greedy Triangulation (GT) of a graph GT with an empty edge set.
    Distances between pairs of nodes are given by poi_pairs.

    The GT connects pairs of nodes in ascending order of their distance provided
    that no edge crossing is introduced. It leads to a maximal connected planar
    graph, while minimizing the total length of edges considered.
    See: cardillo2006spp
    """

    # Add edges between POIs in ascending order of distance
    for poi_pair, distance in poi_pairs:
        v = graph.vs.find(id=poi_pair[0]).index
        w = graph.vs.find(id=poi_pair[1]).index
        if not new_edge_intersects(graph, (
            graph.vs[v]["x"], graph.vs[v]["y"],
            graph.vs[w]["x"], graph.vs[w]["y"]
        )):
            graph.add_edge(v, w, weight=distance)


def prune_graph(graph: ig.Graph, prune_quantile: float, prune_measure: str) -> ig.Graph:
    """
    Prune a graph based on the given measure and quantile.
    The pruning measure can be one of:

    - 'betweenness': Edge betweenness.
    - 'closeness': Vertex closeness centrality.
    - 'random': Random edge pruning.

    :param graph: The input graph to prune.
    :param prune_quantile: The quantile value specifying the degree of pruning.
    :param prune_measure: The measure used for pruning edges in the graph.
    :return: The pruned graph - a subgraph of the input graph.
    """
    prune_measures = {
        "betweenness": _prune_betweenness,
        "closeness": _prune_closeness,
        "random": _prune_random,
    }

    if prune_measure in prune_measures:
        return prune_measures[prune_measure](graph, prune_quantile)

    raise ValueError(f"Unknown pruning measure: {prune_measure}")


def _prune_betweenness(graph: ig.Graph, prune_quantile: float) -> ig.Graph:
    """
    Prune a graph based on edge betweenness, keeping only the edges with betweenness above the given quantile.
    The betweenness of an edge is the number of shortest paths that pass through it.
    """
    edge_betweenness = graph.edge_betweenness(directed=False, weights="weight")
    quantile = np.quantile(edge_betweenness, 1 - prune_quantile)
    subgraph_edges = []

    for i in range(graph.ecount()):
        if edge_betweenness[i] >= quantile:
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
    # For reproducibility
    random.seed(0)
    # Create a random order for the edges
    edge_order = random.sample(range(graph.ecount()), k=graph.ecount())
    # "lower" and + 1 so smallest quantile has at least one edge
    index = np.quantile(np.arange(len(edge_order)), prune_quantile, method="lower") + 1
    return graph.subgraph_edges(edge_order[:index], delete_vertices=False)
