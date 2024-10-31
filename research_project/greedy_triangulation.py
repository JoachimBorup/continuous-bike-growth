from typing import Optional

import igraph as ig


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
    if len(pois) < 2: return ([], [])  # We can't do anything with less than 2 POIs

    # GT_abstract is the GT with same nodes but euclidian links to keep track of edge crossings
    pois_indices = set()
    for poi in pois:
        pois_indices.add(graph.vs.find(id=poi).index)
    G_temp = copy.deepcopy(graph)
    for e in G_temp.es:  # delete all edges
        G_temp.es.delete(e)

    poipairs = poipairs_by_distance(graph, pois, True)
    if len(poipairs) == 0: return ([], [])

    if prune_measure == "random":
        # run the whole GT first
        GT = copy.deepcopy(G_temp.subgraph(pois_indices))
        for poipair, poipair_distance in poipairs:
            poipair_ind = (GT.vs.find(id=poipair[0]).index, GT.vs.find(id=poipair[1]).index)
            if not new_edge_intersects(GT, (
            GT.vs[poipair_ind[0]]["x"], GT.vs[poipair_ind[0]]["y"], GT.vs[poipair_ind[1]]["x"],
            GT.vs[poipair_ind[1]]["y"])):
                GT.add_edge(poipair_ind[0], poipair_ind[1], weight=poipair_distance)
        # create a random order for the edges
        random.seed(0)  # const seed for reproducibility
        edgeorder = random.sample(range(GT.ecount()), k=GT.ecount())
    else:
        edgeorder = False

    GT_abstracts = []
    GTs = []
    for prune_quantile in tqdm(prune_quantiles, desc="Greedy triangulation", leave=False):
        GT_abstract = copy.deepcopy(G_temp.subgraph(pois_indices))
        GT_abstract = greedy_triangulation(GT_abstract, poipairs, prune_quantile, prune_measure, edgeorder)
        GT_abstracts.append(GT_abstract)

        # Get node pairs we need to route, sorted by distance
        routenodepairs = {}
        for e in GT_abstract.es:
            routenodepairs[(e.source_vertex["id"], e.target_vertex["id"])] = e["weight"]
        routenodepairs = sorted(routenodepairs.items(), key=lambda x: x[1])

        # Do the routing
        GT_indices = set()
        for poipair, poipair_distance in routenodepairs:
            poipair_ind = (graph.vs.find(id=poipair[0]).index, graph.vs.find(id=poipair[1]).index)
            sp = set(graph.get_shortest_paths(poipair_ind[0], poipair_ind[1], weights="weight", output="vpath")[0])
            GT_indices = GT_indices.union(sp)

        GT = graph.induced_subgraph(GT_indices)
        GTs.append(GT)

    return (GTs, GT_abstracts)
