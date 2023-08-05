# -*- coding: utf-8 -*-
"""
Created on Sun Feb 15 00:08:18 2015

@author: José Jiménez

Sparse Matrix Multiplication tools
"""


"""
SparseMatrixMult(A,B,sizeA,sizeB)

A: dict in the form (key="(i,j)",value)
B: same

returns: C dict in the form (key="(i,j)",value)

Caution: Function does not check matrix dimensions.
"""

def SparseMatrixMult(A,B):
        
    s = len(A.keys())
    r = len(B.keys())
    
    inter = {}
    C = {}
    
    for i in range(s):
        fila = eval(A.keys()[i])[0]
        columna = eval(A.keys()[i])[1]
        
        val1 = A.values()[i]
        
        # Look for every register in B with same column
        
        for j in range(r):
            row = eval(B.keys()[j])[0]
            column = eval(B.keys()[j])[1]
            
            val2 = B.values()[j]
            if columna == row:
                tupla = str((fila,columna,row,column))
                inter[tupla] = val1*val2
    
    # Group by fila,column (i,k) using addition
    
    if inter == {}:
        string = "All products are 0"
        return string
        
    
    u = len(inter.keys())
    
    for y in range(u):
        key = eval(inter.keys()[y])
        val = inter.values()[y]
        i, k = key[0], key[3]
        
        tupla = str((i,k))
        
        try:
            C[tupla] = C[tupla] + val
        except:
            C[tupla] = val
    
    return C
        
 

"""
GenSparseMatrix(size,p)

Generates a sparse matrix using a dict in the form (key="(i,j)",value).

size: tuple of size 2 giving (nrow,ncol)
p: probability of non-zero value por each position, e.g: given a n*m matrix
the expected number of non-zero elements is n*m*p.

Requires numpy to work.
"""       
        

def GenSparseMatrix(size,p):
    import numpy as num
    n = size[0]
    m = size[1]
    
    C = {}
    
    for i in range(n):
        for j in range(m):
            al = num.random.random()
            if al < p:
                tup = str((i,j))
                C[tup] = num.random.randint(low=100)
    
    return C
                
"""
SparseMatElementWise(A,B,operation)

Performs element-wise operations given matrixes A and B.

A: dict in the form (key='(i,j)',value)
B: dict in the form (key='(i,j)',value)
operation: one of the following: 'plus','minus','times'

Caution: function does not check matrix sizes.
"""        
        
def SparseMatElementWise(A,B,operation):
    
    s = len(A.keys())
    r = len(B.keys())
    
    C = {}
    
    ## Using sets
    
    intersection = set(A.keys()) & set(B.keys())
    onlyA = set(A.keys()) - intersection
    onlyB = set(B.keys()) - intersection
    
    if operation == 'plus':    
        
        for key in intersection:
            C[key]=A[key]+B[key]
        for key in onlyA:
            C[key]=A[key]
        for key in onlyB:
            C[key]=B[key]
    
    if operation == 'minus':
        
        for key in intersection:
            C[key]=A[key]-B[key]
        for key in onlyA:
            C[key]=A[key]
        for key in onlyB:
            C[key]= -B[key]
            
    else:
        for key in intersection:
            C[key] = A[key] * B[key]
    
    return C
            
    
    
                    
                


        
    