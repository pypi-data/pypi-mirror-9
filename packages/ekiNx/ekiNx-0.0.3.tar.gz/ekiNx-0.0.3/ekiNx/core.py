# -*- coding: utf-8 -*-
"""
1 - The preferred data format for input is a pandas dataframe with
specific columns name for nodes projected and nodes to project.
In these case you should use nodeSetsFromDataframe function 
to convert data and extract nodes

Examples
test1.py

2 - If input data is an pandas adjacency matrix you shoud use 
    graphFromPandasAdjancyMatrix
--------
@author: charles-abner DADI @EKIMETRICS
"""
import networkx as nx
from networkx.algorithms import bipartite
import numpy as np
import pandas as pd
import numpy as np

# Define some custom weight functions for projection
def jaccard_distance(G, u, v):
    unbrs = set(G[u])
    vnbrs = set(G[v])
    return float(len(unbrs & vnbrs)) / len(unbrs | vnbrs)

def inverse_norm1(G, u, v, weight='weight'):
    w = 0
    for nbr in set(G[u]) & set(G[v]):
        w += abs(G.edge[u][nbr].get(weight, 1) - G.edge[v][nbr].get(weight, 1))
    return 1/w


def FromDataFrame(data,u,v,w=None,alpha=None):
    
    """extract node sets from data frame:
    -------------------------------------------
    INPUT: 
    -------------------------------------------
    data is a pandas dataframe
    u is the name of column  for node 'projected'
    v is the name of column for node to project
    w is the name of column for weight
    alpha is a threshold to map or not a edge
    
    -------------------------------------------
    OUTPUT:
    -------------------------------------------
    U: are nodes projected
    V: are node to project
    E: edges with weight attributes if weight columns filled 
    A: numpy array of two columns
    """
    if(w==None):
        A = np.array([])
        A = np.array(data[[u,v]])
        U = list(set([e[0] for e in A]))
        V = list(set([e[1] for e in A]))
        E = [(e[0],e[1]) for e in A]
    else:
        if(alpha==None):
            alpha = 0
        A = np.array([])
        A = np.array(data[[u,v,w]])
        U = list(set([e[0] for e in A]))
        V = list(set([e[1] for e in A]))
        E = [(e[0],e[1],{'weight':int(e[2])}) for e in A if e[2] >= alpha]
    return (U,V,A,E)
    

    
def mapBipartite(U,V,E):
    """define bipartite graph, compute list 
    of egdes from nodes and add nodes|edges to graph"""
    """-------------------------------------------
    INPUT: 
    -------------------------------------------
    U nodes 'projected'
    V nodes to project
    E: edges with weight attributes if weight columns filled 
    
    -------------------------------------------
    OUTPUT:
    -------------------------------------------
    g: networkX biGraph 
    """    
    g = nx.Graph()
    g.add_nodes_from(V, bipartite=0)
    g.add_nodes_from(U, bipartite=1)
    g.add_edges_from(E)
    return g

def projectGraph(biGraph,V, weight_function, plot = 0):
    """projection of graph with a user defined weight function
    -------------------------------------------
    INPUT: 
    -------------------------------------------
    biGraph a bigraph networkX object 
    V is the set on 
    -------------------------------------------
    OUTPUT:
    -------------------------------------------
    g: a networkX object representing a undirected graph
        each node contain is label with column label
    """          
    projected_graph = bipartite.generic_weighted_projected_graph(biGraph, V, weight_function=weight_function)
    if(plot==1):
        nx.draw(projected_graph)
    return projected_graph


def graphFromPandasAdjancyMatrix(data ,plot=None):

    """map nodes and edges from adjancy matrix
    -------------------------------------------
    INPUT: 
    -------------------------------------------
    data is a pandas object representing an adjacency matrix
    -------------------------------------------
    OUTPUT:
    -------------------------------------------
    g: a networkX object representing a undirected graph
        each node contain is label with column label
    """    
    A = np.array(data)
    U = list(set(data.index))
    V = list(set(data.columns))
    g = nx.from_numpy_matrix(A)
    nodes_label = {key: value for (key, value) in enumerate(V)}
    g = nx.relabel_nodes(g,nodes_label)
    if(plot==1):
        nx.draw(g)
    return g

def exportGEXF(graph,path_out):
    """export graph in GEXF readable by gephi.."""    
    try:
        nx.write_gexf(graph, path_out + ".gexf")
        print " export to " + path_out + " is succeeded"
    except:
        print "Unexpected error:", sys.exc_info()[0]
#        
#def test():
#    u = 'index'
#    v=  'Chaine'
#    res = FromDataFrame(data, u, v )
#    U = res[0]
#    V = res[1]
#    A = res[2]
#    E = res[3]
#    g = mapBipartite(U,V,E)
#    g_projected = projectGraph(g, V, jaccard_distance, plot = 1)
#    exportGEXF(g_projected,path_out)
        
def proclamer():
    print " EkiNetworkX" 
    
if __name__ == '__main__':
    proclamer()



