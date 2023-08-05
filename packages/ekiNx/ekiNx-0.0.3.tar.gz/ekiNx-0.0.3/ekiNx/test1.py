# -*- coding: utf-8 -*-
"""
Created on Tue Jan  6 14:53:36 2015

1 - The preferred data format for input is a pandas dataframe with
specific columns name for nodes projected and nodes to project.
In these case you should use nodeSetsFromDataframe function 
to convert data and extract nodes
"""
import sys
import os
import pandas as pd
from ekiNx import core


def main():
    columns = ['customer' , 'products']
    content    = [['virginie','virginie','virginie','emilie','julie','patrick'],
               ['short','sweat','tablet','sweat','phone4','tablet']]
    data = pd.DataFrame(columns=columns)
    data['customer']   =   content[0]
    data['products']   =   content[1]
    
    
    """
    >>> OUT : 
           customer products
        0  virginie    short
        1  virginie    sweat
        2  virginie   tablet
        3    emilie    sweat
        4     julie   phone4
        5   patrick   tablet
    """
    
    
    name = "graphTest"
    u = 'customer'
    v='products'
    
    res = core.FromDataFrame(data, u, v )
    U = res[0]
    V = res[1]
    A = res[2]
    E = res[3]
    g = core.mapBipartite(U,V,E)
    g_projected = core.projectGraph(g, V, core.jaccard_distance, plot = 1)
    core.exportGEXF(g_projected, os.getcwd() + name )

if __name__ == '__main__':
    main()