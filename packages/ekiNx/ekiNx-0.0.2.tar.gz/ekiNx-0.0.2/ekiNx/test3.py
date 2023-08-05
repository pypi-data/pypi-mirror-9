# -*- coding: utf-8 -*-
"""
Created on Tue Jan  6 14:53:36 2015
@author: charles-abner
"""
import sys
import os
import pandas as pd
from ekiNx import core

def main():
    columns = ['customer' , 'products']
    
    content    = [  ['virginie','virginie','virginie','emilie','julie','patrick'],
                    ['short','sweat','tablet','sweat','phone4','tablet'],
                    [3,2,1,5,6,3] ]
               
    data = pd.DataFrame(columns=columns)
    data['customer']   =   content[0]
    data['products']   =   content[1]
    data['weight']     =   content[2]
    
    
    """
    >>> OUT : 
           customer products  weight
        0  virginie    short       3
        1  virginie    sweat       2
        2  virginie   tablet       1
        3    emilie    sweat       5
        4     julie   phone4       6
        5   patrick   tablet       3
    """

    return data

if __name__ == '__main__':
    data = main()
    name = "graphTest"
    u = 'customer'
    v ='products'
    w = 'weight'
    alpha = 2

    res = core.FromDataFrame(data, u, v ,w, alpha)
    U = res[0]
    V = res[1]
    A = res[2]
    E = res[3]
    g = core.mapBipartite(U,V,E)
    g_projected = core.projectGraph(g, V, core.jaccard_distance, plot = 1)
    core.exportGEXF(g_projected, os.getcwd() + name )




