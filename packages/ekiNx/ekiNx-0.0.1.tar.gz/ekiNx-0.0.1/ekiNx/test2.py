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
    columns = ['short','sweat','tablet','phone4']
    index   = ['virginie','emilie','julie','patrick']
    M = [[0,0,0,1] , [1,0,0,1], [0,1,0,1],[0,1,1,0]]
    data = pd.DataFrame(data=M,index= index, columns=columns)
    
    """
    ---------------------------------------------------
    >>>OUT:           short  sweat  tablet  phone4
            virginie      0      0       0       1
            emilie        1      0       0       1
            julie         0      1       0       1
            patrick       0      1       1       0
    """
    return data
    
    
if __name__ == '__main__':
    data=main()
    res = core.graphFromPandasAdjancyMatrix(data, plot=1 )

