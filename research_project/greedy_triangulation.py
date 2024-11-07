import copy
import random
from typing import Optional

import igraph as ig
from tqdm.notebook import tqdm

from src.functions import poipairs_by_distance, new_edge_intersects, greedy_triangulation


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

    if prune_measure == "random":
        # Run the whole GT first
        GT: ig.Graph = copy.deepcopy(edgeless_graph.subgraph(poi_indices))
        # Add edges between POIs in ascending order of distance
        for poi_pair, distance in poi_pairs:
            v = GT.vs.find(id=poi_pair[0]).index
            w = GT.vs.find(id=poi_pair[1]).index
            if not new_edge_intersects(GT, (
                GT.vs[v]["x"], GT.vs[w]["y"],
                GT.vs[v]["x"], GT.vs[w]["y"],
            )):
                GT.add_edge(v, w, weight=distance)
        # Create a random order for the edges
        random.seed(0)  # const seed for reproducibility
        edge_order = random.sample(range(GT.ecount()), k=GT.ecount())
    else:
        edge_order = False

    # GT_abstract is the GT with same nodes but euclidian links to keep track of edge crossings
    GT_abstracts = []
    GTs = []
    for prune_quantile in tqdm(prune_quantiles, desc="Greedy triangulation", leave=False):
        GT_abstract = copy.deepcopy(edgeless_graph.subgraph(poi_indices))
        GT_abstract = greedy_triangulation(GT_abstract, poi_pairs, prune_quantile, prune_measure, edge_order)
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
