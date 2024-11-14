#First attempt at graph similarity
import igraph as ig
import math
import random

#we calculate the shortest path between all vertices in g1 and g2. The error is the sum of errors for g2 compared to g1. 
def sum_of_errors(graph1, graph2) -> tuple[int, int, int]:
    error = 0
    g1_disconnected_points = 0
    g2_disconnected_points = 0

    num_vertices = graph1.vcount()
    if num_vertices != graph2.vcount() :
        raise Exception("The two graphs do not have the same number of vertices")
    for i in range (0, num_vertices):
        for j in range (0, num_vertices):
            if (i==j or i>j) :
                continue
            else :
                shortest_path_g1_length = graph1.distances(i, j, weights='weight')
                shortest_path_g2_length = graph2.distances(i, j, weights='weight')

                if(math.isinf(shortest_path_g1_length[0][0]) and math.isinf(shortest_path_g2_length[0][0])) :
                    g1_disconnected_points = g1_disconnected_points + 1
                    g2_disconnected_points = g2_disconnected_points + 1
                elif(math.isinf(shortest_path_g1_length[0][0])) :
                    g1_disconnected_points = g1_disconnected_points + 1
                elif(math.isinf(shortest_path_g2_length[0][0])) :
                    g2_disconnected_points = g2_disconnected_points + 1
                else :    
                    diff = shortest_path_g2_length[0][0]-shortest_path_g1_length[0][0]
                    error = error+diff
    return error, g1_disconnected_points, g2_disconnected_points

def generate_unique_vertex_pairs(number_of_pairs) -> list:
    unique_tuples = set()
    while len(unique_tuples) < number_of_pairs:
        unique_tuples.add((random.randint(0, number_of_pairs-1), random.randint(0, number_of_pairs-1)))
    return list(unique_tuples)


#Calculate the shortest path from a certain percent of the vertices to another vertex. The pairs are randomly generated. The error returned is the sum of errors for g2 compared to g1. 
def sum_of_errors_part_of_graph(graph1, graph2, percent) -> tuple[int, int, int]:
    error = 0
    g1_disconnected_points = 0
    g2_disconnected_points = 0

    num_vertices = graph1.vcount()
    if num_vertices != graph2.vcount() :
        raise Exception("The two graphs do not have the same number of vertices")
    
    number_of_pairs = int(num_vertices * percent)
    random_vertices_from_to = generate_unique_vertex_pairs(number_of_pairs)

    for i,j in random_vertices_from_to:
        if i==j :
            continue
        else :
            shortest_path_g1_length = graph1.distances(i, j, weights='weight')
            shortest_path_g2_length = graph2.distances(i, j, weights='weight')

            if(math.isinf(shortest_path_g1_length[0][0]) and math.isinf(shortest_path_g2_length[0][0])) :
                g1_disconnected_points = g1_disconnected_points + 1
                g2_disconnected_points = g2_disconnected_points + 1
            elif(math.isinf(shortest_path_g1_length[0][0])) :
                g1_disconnected_points = g1_disconnected_points + 1
            elif(math.isinf(shortest_path_g2_length[0][0])) :
                g2_disconnected_points = g2_disconnected_points + 1
            else :    
                diff = shortest_path_g2_length[0][0]-shortest_path_g1_length[0][0]
                error = error+diff
    return error, g1_disconnected_points, g2_disconnected_points

#Calculate the shortest path from all points of interest to all points of interest 
def sum_of_errors_pois(graph1, graph2, pois) -> tuple[int, int, int]:
    error = 0
    g1_disconnected_points = 0
    g2_disconnected_points = 0

    print(f'Graph 1 contains 4483790348: {4483790348 in graph1.vs["id"]}')
    print(f'Graph 2 contains 4483790348: {4483790348 in graph2.vs["id"]}')

    iterations = 0
    print(f'Expecting {len(pois)*(len(pois)-1)/2} iterations')

    for v in pois:  # IDs, not indices
        for w in pois:
            if (v==w or v>w):
                continue

            if iterations % 100 == 0:
                print(f'Iteration {iterations}')
            iterations += 1

            print(f'v: {v}, w: {w}')
            shortest_path_g1_length = graph1.distances(graph1.vs.find(id=v).index, graph1.vs.find(id=w).index, weights='weight')
            #print(f"Shortest path length in g1 (total Euclidean distance): {shortest_path_g1_length[0]}")
            shortest_path_g2_length = graph2.distances(graph2.vs.find(id=v).index, graph2.vs.find(id=w).index, weights='weight')
            #print(f"Shortest path length in g2 (total Euclidean distance): {shortest_path_g2_length[0]}")
            if(math.isinf(shortest_path_g1_length[0][0]) and math.isinf(shortest_path_g2_length[0][0])) :
                g1_disconnected_points = g1_disconnected_points + 1
                g2_disconnected_points = g2_disconnected_points + 1
            elif(math.isinf(shortest_path_g1_length[0][0])) :
                g1_disconnected_points = g1_disconnected_points + 1
            elif(math.isinf(shortest_path_g2_length[0][0])) :
                g2_disconnected_points = g2_disconnected_points + 1
            else :
                diff = shortest_path_g2_length[0][0]-shortest_path_g1_length[0][0]
                error = error+diff
    return error, g1_disconnected_points, g2_disconnected_points

#Compute Euclidean distance between two vertices
def euclidean_distance(v1, v2, graph):
    x1, y1 = graph.vs[v1]['coord']
    x2, y2 = graph.vs[v2]['coord']
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def example() :
    #10 random coordinates in the range 0-9
    coordinates = [(0,1),(0,0),(4,9),(3,6),(9,9),(4,4),(5,3),(8,2),(2,7),(0,6),(0,7)]

    #A graph g1 with 10 vertices and 28 edges
    g1 = ig.Graph()
    g1.add_vertices(11)
    g1.add_edges([(1, 4), (5, 7), (4, 8), (1, 2), (2, 3), (5, 0), (2, 4), (8, 9), (9, 0), (1, 5), (6, 8), (3, 6), (2, 0), (1, 0), (3, 7), (1, 3), (6, 7), (6, 0), (1, 8), (3, 4), (2, 8), (6, 9), (2, 5), (2, 7), (7, 8), (4, 9), (5, 8), (7, 9)
    ])
    g1.vs['coord'] = coordinates
    # Compute the weights (Euclidean distances) for all edges in g1
    weights = [euclidean_distance(edge.source, edge.target, g1) for edge in g1.es]
    g1.es['weight'] = weights

    #A graph g2 with 10 vertices and 28 edges. It has the same vertices and coordinates as g1. It has 60% of the same edges and 40% new randomly generated edges
    g2 = ig.Graph()
    g2.add_vertices(11)
    g2.add_edges([(1, 9), (7, 8), (3, 4), (6, 9), (7, 9), (1, 8), (3, 6), (2, 6), (3, 7), (8, 0), (4, 0), (1, 3), (5, 8), (3, 9), (4, 5), (2, 7), (7, 0), (1, 0), (5, 6), (6, 7), (3, 5), (6, 0), (3, 0), (2, 5), (3, 8), (4, 9), (2, 8), (2, 0)
    ])
    g2.vs['coord'] = coordinates
    # Compute the weights (Euclidean distances) for all edges in g2
    weights = [euclidean_distance(edge.source, edge.target, g2) for edge in g2.es]
    g2.es['weight'] = weights

    #Run examples
    error = sum_of_errors(g1, g2)
    print(f"The error is: {error} when graph2 is compared to graph1 for all vertices to all vertices, O(N^2*x) where x is the runtime of the distances method") 

    percent = 1.0
    error_for_part_of_graph = sum_of_errors_part_of_graph(g1, g2, percent) 
    print(f"The error is: {error_for_part_of_graph} when graph2 is compared to graph1 for {percent*100}% of the starting points, O({percent}N*x) where x is the runtime of the distances method")

    error_for_pois, g1_disconnected_pois, g2_disconnected_pois = sum_of_errors_pois(g1, g2, [1,2,7,8,9,10])
    print(f"The error is: {error_for_pois} and there are {g1_disconnected_pois} pairs of points in g1 and {g2_disconnected_pois} pairs of points in g2 that can't reach each other when graph2 is compared to graph1 for the points of interest, O(pois^2)")

#
# if __name__ == "__main__":
#     #Run the example to check if the methods work
#     example()
