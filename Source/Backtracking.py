import copy
import time
import pprint

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


# Backtracking algorithm to solve the gem hunter puzzle
def backtrack(map, i, j):
    if j == col:
        if i == row - 1:
            print('\n'.join([' '.join([str(cell) for cell in row]) for row in map]))
            raise(Exception("Found solution"))
        else:
            backtrack(map, i + 1, 0)   
    elif map[i][j] == '_':
        for c in ['T', 'G']:
            if is_valid((i, j), map, c):
                map[i][j] = c
                backtrack(map, i, j + 1)
                map[i][j] = '_'
    else:
        backtrack(map, i, j + 1)


# Get the adjacent cells (i, j)
def get_adjacent_cells(cell):
    adjacent_cells = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni, nj = cell[0] + di, cell[1] + dj
            if 0 <= ni < row and 0 <= nj < col:
                adjacent_cells.append((ni, nj))
    return adjacent_cells


# Get the values of the adjacent cells
def get_adjacent_cell_values(cell, map):
    values = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni, nj = cell[0] + di, cell[1] + dj
            if 0 <= ni < row and 0 <= nj < col:
                values.append(map[ni][nj])
    return values


# Check if the configuration with the assignment is valid
def is_valid(cell, map, value):
    map_temp = copy.deepcopy(map)
    map_temp[cell[0]][cell[1]] = value
    adjacent_cells = get_adjacent_cells(cell)
    for neighbor in adjacent_cells:
        if map_temp[neighbor[0]][neighbor[1]] != '_' and map_temp[neighbor[0]][neighbor[1]] != 'T' and map_temp[neighbor[0]][neighbor[1]] != 'G':
            new_adj_cell_values = get_adjacent_cell_values(neighbor, map_temp)
            if new_adj_cell_values.count('T') > int(map_temp[neighbor[0]][neighbor[1]]):
                return False
            if new_adj_cell_values.count('T') < int(map_temp[neighbor[0]][neighbor[1]]) and new_adj_cell_values.count('_') < int(map_temp[neighbor[0]][neighbor[1]]) - new_adj_cell_values.count('T'):
                return False
    return True

    
try:
    start_time = time.time()
    backtrack(map, 0, 0)
except Exception as e:
    print(e)
    print("--- %s seconds ---" % (time.time() - start_time))