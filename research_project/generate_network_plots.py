import os


def subgraph_percentages_with_iterations_plot(placeid:str, pms:list, subgraphs_percentages:list, iterations:int):
    for prune_measure in pms:
        if prune_measure == "betweenness":
            weight_abstract = True
        else:
            weight_abstract = 6
        
        # EXISTING INFRASTRUCTURE
        # Load networks
        G_carall = csv_to_ig(PATH["data"] + placeid + "/", placeid, 'carall')
        map_center = nxdraw(G_carall, "carall")
        
        # Load POIs
        with open(PATH["data"] + placeid + "/" + placeid + '_poi_' + poi_source + '_nnidscarall.csv') as f:
            nnids = [int(line.rstrip()) for line in f]
        nodesize_poi = nodesize_from_pois(nnids)
        
        fig = initplot()
        nxdraw(G_carall, "carall", map_center)
        nxdraw(G_carall, "poi_unreached", map_center, nnids, "nx.draw_networkx_nodes", nodesize_poi)
        plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_carall_poi_' + poi_source + '.pdf', bbox_inches="tight")
        plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_carall_poi_' + poi_source + '.png', bbox_inches="tight", dpi=plotparam["dpi"])
        plt.close()
        
        
        # GENERATED, POI BASED
        # Load results
        for subgraph_percentage in tqdm(subgraphs_percentages, desc="Subgraphs percentages list", leave=False):
            for i in tqdm(range(iterations), desc="Iterations", leave=False):
                 
                filename = placeid + '_poi_' + poi_source + "_" + prune_measure + ".pickle"
                subgraph_iteration_dir = subgraph_percentage + "/" + str(i) + "/"

                with open(PATH["results"] + placeid + "/" + subgraph_iteration_dir + filename, 'rb') as f:
                    res = pickle.load(f)
                if debug: pp.pprint(res)
                    
                dir_path =  PATH["plots_networks"] + placeid + "/" + subgraph_iteration_dir

                # Ensure the directory exists before opening the file
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                # PLOT abstract MST
                fig = initplot()
                nxdraw(G_carall, "carall", map_center)
                nxdraw(res["MST_abstract"], "abstract", map_center, weighted = 6)
                nxdraw(G_carall, "poi_unreached", map_center, nnids, "nx.draw_networkx_nodes", nodesize_poi)
                nxdraw(G_carall, "poi_reached", map_center, list(set([v["id"] for v in res["MST"].vs]).intersection(set(nnids))), "nx.draw_networkx_nodes", nodesize_poi)
                plt.savefig(PATH["plots_networks"] + placeid + "/" + subgraph_iteration_dir  + placeid + '_MSTabstract_poi_' + poi_source + '.pdf', bbox_inches="tight")
                plt.savefig(PATH["plots_networks"] + placeid + "/" + subgraph_iteration_dir + placeid + '_MSTabstract_poi_' + poi_source + '.png', bbox_inches="tight", dpi=plotparam["dpi"])
                plt.close()
                
                # PLOT MST all together
                fig = initplot()
                nxdraw(G_carall, "carall")
                nxdraw(res["MST"], "bikegrown", map_center, nodesize = nodesize_grown)
                nxdraw(G_carall, "poi_unreached", map_center, nnids, "nx.draw_networkx_nodes", nodesize_poi)
                nxdraw(G_carall, "poi_reached", map_center, list(set([v["id"] for v in res["MST"].vs]).intersection(set(nnids))), "nx.draw_networkx_nodes", nodesize_poi)
                plt.savefig(PATH["plots_networks"] + placeid + "/" + subgraph_iteration_dir + placeid + '_MSTall_poi_' + poi_source + '.pdf', bbox_inches="tight")
                plt.savefig(PATH["plots_networks"] + placeid + "/" + subgraph_iteration_dir + placeid + '_MSTall_poi_' + poi_source + '.png', bbox_inches="tight", dpi=plotparam["dpi"])
                plt.close()
                
                # PLOT MST all together with abstract
                fig = initplot()
                nxdraw(G_carall, "carall", map_center)
                nxdraw(res["MST"], "bikegrown", map_center, nodesize = 0)
                nxdraw(res["MST_abstract"], "abstract", map_center, weighted = 6)
                nxdraw(G_carall, "poi_unreached", map_center, nnids, "nx.draw_networkx_nodes", nodesize_poi)
                nxdraw(G_carall, "poi_reached", map_center, list(set([v["id"] for v in res["MST"].vs]).intersection(set(nnids))), "nx.draw_networkx_nodes", nodesize_poi)
                plt.savefig(PATH["plots_networks"] + placeid + "/" + subgraph_iteration_dir + placeid + '_MSTabstractall_poi_' + poi_source + '.pdf', bbox_inches="tight")
                plt.savefig(PATH["plots_networks"] + placeid + "/" + subgraph_iteration_dir + placeid + '_MSTabstractall_poi_' + poi_source + '.png', bbox_inches="tight", dpi=plotparam["dpi"])
                plt.close()
                
                # PLOT abstract greedy triangulation (this can take some minutes)
                for GT_abstract, prune_quantile in zip(res["GT_abstracts"], res["prune_quantiles"]):
                    fig = initplot()
                    nxdraw(G_carall, "carall")
                    try:
                        GT_abstract.es["weight"] = GT_abstract.es["width"]
                    except:
                        pass
                    nxdraw(GT_abstract, "abstract", map_center, drawfunc = "nx.draw_networkx_edges", nodesize = 0, weighted = weight_abstract, maxwidthsquared = nodesize_poi)
                    nxdraw(G_carall, "poi_unreached", map_center, nnids, "nx.draw_networkx_nodes", nodesize_poi)
                    nxdraw(G_carall, "poi_reached", map_center, list(set([v["id"] for v in GT_abstract.vs]).intersection(set(nnids))), "nx.draw_networkx_nodes", nodesize_poi)
                    plt.savefig(PATH["plots_networks"] + placeid + "/" + subgraph_iteration_dir + placeid + '_GTabstract_poi_' + poi_source + "_" + prune_measure + "{:.3f}".format(prune_quantile) + '.png', bbox_inches="tight", dpi=plotparam["dpi"])
                    plt.close()
                
                # PLOT all together (this can take some minutes)
                for GT, prune_quantile in zip(res["GTs"], res["prune_quantiles"]):
                    fig = initplot()
                    nxdraw(G_carall, "carall")
                    nxdraw(GT, "bikegrown", map_center, nodesize = nodesize_grown)
                    nxdraw(G_carall, "poi_unreached", map_center, nnids, "nx.draw_networkx_nodes", nodesize_poi)
                    nxdraw(G_carall, "poi_reached", map_center, list(set([v["id"] for v in GT.vs]).intersection(set(nnids))), "nx.draw_networkx_nodes", nodesize_poi)
                    plt.savefig(PATH["plots_networks"] + placeid + "/" + subgraph_iteration_dir + placeid + '_GTall_poi_' + poi_source + "_" + prune_measure + "{:.3f}".format(prune_quantile) + '.png', bbox_inches="tight", dpi=plotparam["dpi"])
                    plt.close()
                


def existing_network_plot(placeid:str, prune_measures:list):
    print(placeid + ": Plotting networks")
    for prune_measure in prune_measures:
        if prune_measure == "betweenness":
            weight_abstract = True
        else:
            weight_abstract = 6
        
        # EXISTING INFRASTRUCTURE
        # Load networks
        G_carall = csv_to_ig(PATH["data"] + placeid + "/", placeid, 'carall')
        G_biketrackcarall = csv_to_ig(PATH["data"] + placeid + "/", placeid, 'biketrackcarall')
        map_center = nxdraw(G_carall, "carall")
        
        # PLOT existing networks
        fig = initplot()
        nxdraw(G_carall, "carall", map_center)
        plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_carall.pdf', bbox_inches="tight")
        plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_carall.png', bbox_inches="tight", dpi=plotparam["dpi"])
        plt.close()
        
        try:
            G_biketrack = csv_to_ig(PATH["data"] + placeid + "/", placeid, 'biketrack')
            fig = initplot()
            nxdraw(G_biketrack, "biketrack", map_center)
            plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_biketrack.pdf', bbox_inches="tight")
            plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_biketrack.png', bbox_inches="tight", dpi=plotparam["dpi"])
            plt.close()
            
            fig = initplot()
            nxdraw(G_carall, "carall", map_center)
            nxdraw(G_biketrack, "biketrack", map_center, list(set([v["id"] for v in G_biketrack.vs]).intersection(set([v["id"] for v in G_carall.vs]))))
            nxdraw(G_biketrack, "biketrack_offstreet", map_center, list(set([v["id"] for v in G_biketrack.vs]).difference(set([v["id"] for v in G_carall.vs]))))
            plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_biketrackcarall.pdf', bbox_inches="tight")
            plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_biketrackcarall.png', bbox_inches="tight", dpi=plotparam["dpi"])
            plt.close()
        except:
            print(placeinfo["name"] + ": No bike tracks found")
        
        try:
            G_bikeable = csv_to_ig(PATH["data"] + placeid + "/", placeid, 'bikeable')
            fig = initplot()
            nxdraw(G_bikeable, "bikeable", map_center)
            plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_bikeable.pdf', bbox_inches="tight")
            plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_bikeable.png', bbox_inches="tight", dpi=plotparam["dpi"])
            plt.close()
        except:
            print(placeinfo["name"] + ": No bikeable infrastructure found")
        
        
        # Load POIs
        with open(PATH["data"] + placeid + "/" + placeid + '_poi_' + poi_source + '_nnidscarall.csv') as f:
            nnids = [int(line.rstrip()) for line in f]
        nodesize_poi = nodesize_from_pois(nnids)
        
        fig = initplot()
        nxdraw(G_carall, "carall", map_center)
        nxdraw(G_carall, "poi_unreached", map_center, nnids, "nx.draw_networkx_nodes", nodesize_poi)
        plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_carall_poi_' + poi_source + '.pdf', bbox_inches="tight")
        plt.savefig(PATH["plots_networks"] + placeid + "/" + placeid + '_carall_poi_' + poi_source + '.png', bbox_inches="tight", dpi=plotparam["dpi"])
        plt.close()