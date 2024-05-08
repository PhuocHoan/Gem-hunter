from pysat.formula import CNF
from pysat.solvers import Glucose3, Solver
from itertools import combinations, groupby
from pprint import pprint 
import time

# Read the grid from a file
f = open("testcases/map6.txt")
row = col = 0
map = []
for l in f.readlines():
    line = l.strip().split(", ")
    map.append(line)
    col = len(line)
    row += 1
f.close()     

# Helper functions

# Generate the CNF for M(k, n)
def at_most_k(variables, k):
    return [[-x for x in comb] for comb in combinations(variables, k + 1)]

# Generate the CNF for L(k, n)
def at_least_k(variables, k):
    return [[x for x in comb] for comb in combinations(variables, len(variables) - k + 1)]

# Initialize the CNF formula
cnf = CNF()

# Map cells to variables
cell_vars = [[0] * col for _ in range(row)]
var_index = 1

for i in range(row):
    for j in range(col):
        if map[i][j] == '_':
            cell_vars[i][j] = var_index
            var_index += 1
            
for i in range(row):
    for j in range(col):
        if map[i][j] != '_':
            n, k = 0, int(map[i][j])
            adjacent_cells = []
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < row and 0 <= nj < col:
                        if map[ni][nj] == 'T' or map[ni][nj] == 'G':
                            k -= 1
                        elif map[ni][nj] == '_':
                            adjacent_cells.append(cell_vars[ni][nj])
            
            if (k == len(adjacent_cells)):
                for cell in adjacent_cells:
                    cnf.append([cell])
            else:
                U_k_n = at_most_k(adjacent_cells, k)
                L_k_n = at_least_k(adjacent_cells, k)
                # Making sure there are no duplicate clauses
                for clause in U_k_n:
                    if clause not in cnf:
                        cnf.append(clause)
                for clause in L_k_n:
                    if clause not in cnf:
                        cnf.append(clause)

clauses = cnf.clauses      
print(cnf.clauses)           
solver = Glucose3()
solver.append_formula(cnf)
solver.solve()
result = solver.get_model()
index = 0
for i in range(row):
    for j in range(col):
        if map[i][j] == '_':
            if result[index] > 0:
                map[i][j] = 'T'
            else:
                map[i][j] = 'G'
            index += 1

print('\n'.join([' '.join([str(cell) for cell in row]) for row in map]))