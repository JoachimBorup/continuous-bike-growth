def greedy_triangulation_routing(G, pois, prune_quantiles=[1], prune_measure="betweenness"):
    """Greedy Triangulation (GT) of a graph G's node subset pois,
    then routing to connect the GT (up to a quantile of betweenness
    betweenness_quantile).
    G is an ipgraph graph, pois is a list of node ids.

    The GT connects pairs of nodes in ascending order of their distance provided
    that no edge crossing is introduced. It leads to a maximal connected planar
    graph, while minimizing the total length of edges considered. 
    See: cardillo2006spp

    Distance here is routing distance, while edge crossing is checked on an abstract 
    level.
    """

    if len(pois) < 2: return ([], [])  # We can't do anything with less than 2 POIs

    # GT_abstract is the GT with same nodes but euclidian links to keep track of edge crossings
    pois_indices = set()
    for poi in pois:
        pois_indices.add(G.vs.find(id=poi).index)
    G_temp = copy.deepcopy(G)
    for e in G_temp.es:  # delete all edges
        G_temp.es.delete(e)

    poipairs = poipairs_by_distance(G, pois, True)
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
            poipair_ind = (G.vs.find(id=poipair[0]).index, G.vs.find(id=poipair[1]).index)
            sp = set(G.get_shortest_paths(poipair_ind[0], poipair_ind[1], weights="weight", output="vpath")[0])
            GT_indices = GT_indices.union(sp)

        GT = G.induced_subgraph(GT_indices)
        GTs.append(GT)

    return (GTs, GT_abstracts)
