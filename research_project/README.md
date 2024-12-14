# Continuous bike growth research project

by Amalie ([abso@itu.dk](mailto:abso@itu.dk)),
Joachim ([aljb@itu.dk](mailto:aljb@itu.dk)),
and Mai ([maod@itu.dk](mailto:maod@itu.dk))

This README assumes that you have followed the instructions in the README in the root of the repository,
and that you have activated the virtual environment.

## Copenhagen dataset

To download the Copenhagen dataset, run the following commands:

```
cd research_project
python shapefiles_for_cph/get_cph.py
```

## Iterative growth model

Run Jupyter Notebook with the OSMNX kernel. To run the iterative growth model, 
open the `iterative_growth_model.ipynb` notebook and run the cells in order.
You can choose to edit the parameters in the notebook (second code block) to experiment with different settings.

The notebook runs the algorithm by calling the `iterative_greedy_triangulation_routing` functon in
`greedy_triangulation.py`, which simulates the stepwise expansion of a bicycle network by incrementally
connecting points of interest (POIs) in a graph. This process mirrors real-world scenarios, where infrastructure
evolves over time rather than being built all at once.

## How it works

1. Input parameters:
   - `graph`: A representation of the city's street network.
   - `pois`: A list of points of interest (POIs) that should be connected.
   - `subgraph_percentages`: Defines how the POIs are split across iterations
     (e.g., 60% in the first iteration, 40% in the second).
   - `number_of_edges_to_add`: Specifies how many edges to add in each step. Replaces the `prune_quantiles` parameter
     in the original algorithm. Here, they should be equivalent to the number of edges the original algorithm would've
     added for those quantiles.
   - `prune_measure`: Determines how to prioritize edges for removal or retention based on metrics like:
     - `betweenness`: Focuses on high-traffic connections.
     - `closeness`: Prioritizes centrality.
     - `random`: Randomized pruning for experimentation.
2. Iterative process
   1. Divide POIs into subsets according to the specified percentages.
   2. Perform Greedy Triangulation (GT):
      - Iteratively add edges between POIs in ascending order of their shortest path distances, ensuring no edge
        crossings (maintaining planarity).
   3. Prune edges based on the chosen strategy (e.g., remove low-priority edges to meet constraints).
   4. Repeat the process for each POI subset and integrate results into the graph.
3. Routing
   - For each pair of connected POIs, route edges through the existing street network to ensure realistic connectivity.

## Outputs

The notebook generates two types of graphs:

- **Abstract Graphs**: High-level representations of the connected POIs.
- **Routed Graphs**: Detailed graphs showing connections mapped to the actual street network.
