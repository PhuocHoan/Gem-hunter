import sys
import copy
import time

count = 0

def parse_file(filepath):
    board = []
    with open(filepath, "r") as file:
        for line in file:
            # Split the line by commas and strip any leading/trailing whitespace
            elements = line.split(',')
            elements = [i.strip() for i in elements]
            # Replace '_' with '-1' and convert the elements to integers
            row = [int(element) if element != '_' else -1 for element in elements]
            board.append(row)
      
    return board, len(board), len(board[0])

def find_all_clauses(input_array, input_len, combi_len, indi_tup, ans_index, next_start, clause_tup):
    global count
    #----------------- Loop for List X
    for iter in range(next_start, input_len + 1):
        #------------------- Return if List X empty
        if combi_len <= 0:
            clause_tup.append(copy.copy(indi_tup))    
            count += 1
            return
        indi_tup[ans_index] = input_array[iter]
        find_all_clauses(input_array, input_len, combi_len - 1, indi_tup, ans_index + 1, iter + 1, clause_tup)

def find_cell_no(i, j, col):
    return i * col + j + 1

#find list X arround current square
def find_adjacent_cells(i, j, row, col):
    output = []    

    if i >= 1 and j >= 1:
        output.append(find_cell_no(i - 1, j - 1, col))
    if i >= 1:
        output.append(find_cell_no(i - 1, j, col))
    if i >= 1 and j < (col - 1):
        output.append(find_cell_no(i - 1, j + 1, col))
    if j < (col - 1):
        output.append(find_cell_no(i, j + 1, col))
    if i < (row - 1) and j < (col - 1):
        output.append(find_cell_no(i + 1, j + 1, col))
    if i < (row - 1):
        output.append(find_cell_no(i + 1, j, col))
    if i < (row - 1) and j >= 1:
        output.append(find_cell_no(i + 1, j - 1, col))
    if j >= 1:
        output.append(find_cell_no(i, j - 1, col))

    return output

def convert_to_CNF(board, row, col):
    # interpret the number constraints
    global count
    count_clause = 0
    result = []

    for i in range(row):
        for j in range(col):
            if board[i][j] == -1:
                continue
            elif board[i][j] != -1:
                result.append([-(i * col + j + 1)])
                first_adjacent_cells = find_adjacent_cells(i, j, row, col)
                count_adj = len(first_adjacent_cells)
                #--------------------------------------------------invalid board
                if ((board[i][j] > count_adj) or (board[i][j] < -1)):
                    print("Invalid board at postion Row: " + str(i) + " Col: " + str(j) + " !!!")
                    sys.exit(1)

                first_adjacent_cells.append(0)
                #------------------------------------------------List boom in current square
                indi_tup = []
                for k in range(board[i][j] + 1):
                    indi_tup.append(0)
                #print indi_tup
                first_tup = []
                count = 0
                #------------------------------------At least n boom 
                find_all_clauses(first_adjacent_cells, count_adj, board[i][j] + 1, indi_tup, 0, 0, first_tup)
                count_clause += count

                for k in range(len(first_tup)):
                    ls = []
                    for l in range(board[i][j] + 1):
                        ls.append(-1 * first_tup[k][l])
                    result.append(ls)

                #-----------------------------------At least n square not contain boom
                indi_tup = []
                for k in range(count_adj - board[i][j] + 1):
                        indi_tup.append(0)
                count = 0
                second_tup = []    
                find_all_clauses(first_adjacent_cells, count_adj, count_adj - board[i][j] + 1, indi_tup, 0, 0, second_tup)
                count_clause += count

                for k in range(len(second_tup)):
                        ls = []
                        for l in range(count_adj - board[i][j] + 1):
                            ls.append(second_tup[k][l])
                        result.append(ls)
            else:
                count_clause += 1
                result.append([find_cell_no(i, j, col)])
    return result

def SolverCNF(cnf):
    def unit_propagation(assignments, clauses):
        unit_clauses = [c for c in clauses if len(c) == 1]
        while unit_clauses:
            #unit is single clause
            unit = unit_clauses[0][0]
            if [-unit] in unit_clauses:
               return None, None
            assignments[abs(unit)] = (unit > 0)
            ls = []
            # check unit in any clause or not, unit always true
            for c in clauses: 
                if unit not in c:
                    if -unit in c:
                        c.remove(-unit)
                        ls.append(c)
                    else:
                        ls.append(c)
            clauses = ls    
            unit_clauses = [c for c in clauses if len(c) == 1]
        return assignments, clauses

    def dpll(assignments, clauses):
        # Tackle single clause
        assignments, clauses = unit_propagation(assignments, clauses)
        if clauses == None:
            return None
        if all(len(c) == 0 for c in clauses):
            return assignments
        if any(len(c) == 0 for c in clauses):
            return None

        literal = abs(clauses[0][0])
        new_clauses = copy.deepcopy(clauses)
        new_clauses.append([literal])
        result = dpll({}, new_clauses)
        if result is None:
            assignments[literal] = False
            
            new_clauses = copy.deepcopy(clauses)
            new_clauses.append([-literal])
            assignments.update(dpll({}, new_clauses))
        
        new_clauses = copy.deepcopy(clauses)
        new_clauses.append([-literal])
        result = dpll({}, new_clauses)
        if result is None:
            assignments[literal] = True
            new_clauses = copy.deepcopy(clauses)
            new_clauses.append([literal])
            assignments.update(dpll({}, new_clauses))

        return assignments
   
    assignments = {}
    result = dpll(assignments, cnf)
    if result == None:
        return {}
    return result

def apply_resolution(cnf_clauses):
    #add 1 clause to the clauses
    def unit_propagation(assignments, clauses):
        unit_clauses = [c for c in clauses if len(c) == 1]
        while unit_clauses:
            #unit is single clause
            unit = unit_clauses[0][0]
            if [-unit] in unit_clauses:
               return None, None
            assignments[abs(unit)] = (unit > 0)
            ls = []
            #check unit in any clause or not, unit always true
            for c in clauses: 
                if unit not in c:
                    if -unit in c:
                        c.remove(-unit)
                        ls.append(c)
                    else:
                        ls.append(c)
            clauses = ls    
            unit_clauses = [c for c in clauses if len(c) == 1]
        return assignments, clauses    

    #combine 2 clause
    def resolve(clause1, clause2):
        resolved_clause = []
        for literal in clause1:
            if literal not in clause2:
                resolved_clause.append(literal)  
        for literal in clause2:
            if literal not in clause1:
                resolved_clause.append(literal)  
        return resolved_clause 
    
    assignment,cnf_clauses = unit_propagation({}, cnf_clauses)
    if cnf_clauses == None:
        return {}
    
    n = 1

    #sord by array len in array
    cnf_clauses = sorted(cnf_clauses, key=len)
    while len(cnf_clauses) > 1 and n != len(cnf_clauses):
        n = len(cnf_clauses)

        #resolution 3 combine to 2 
        for i in range(n - 1, 1, -1):
            found = False
            if len(cnf_clauses[i]) == 3:
                for j in range(0, i - 1):
                    if len(cnf_clauses[j]) == 2 and cnf_clauses.count(cnf_clauses[j]) == 2:
                        resolved_clause = resolve(cnf_clauses[j], cnf_clauses[i])
                        if len(resolved_clause) == 1:
                            if resolved_clause[0] > 0:
                               assignment[resolved_clause[0]] = False
                               cnf_clauses.append([resolved_clause[0]])
                            else:
                               assignment[abs(resolved_clause[0])] = True
                               cnf_clauses.append([resolved_clause[0]])
                            
                            found = True
                            break
            if found:
                break
        
        new_assignment,cnf_clauses = unit_propagation({}, cnf_clauses)
        if cnf_clauses == None:
            return assignment
        assignment.update(new_assignment)

    return assignment

def output(board, solution, row, col,name):
    arr = []
    for i in range(row):
        r = []
        for j in range(col):
            if board[i][j] != -1:
                r.append(str(board[i][j]))
            else:
                if (i * col + j + 1) in solution:
                    if solution[i * col + j + 1] == True:
                        r.append('T') 
                    else:
                        r.append('G')
                else:
                    r.append('G')
        arr.append(r)
        
    with open(f'output{name}.txt', 'w') as output_file:
        for i in arr:
            output_file.write(', '.join(i) + '\n')

if __name__ == '__main__':

    start_time = time.time()  # Record the start time

    filename = "testcases/map5.txt"
    board, row, col = parse_file(filename)
    cnf_clauses = convert_to_CNF(board, row, col)
    solution = apply_resolution(cnf_clauses)
    # sort key of solution
    solution = dict(sorted(solution.items(), key=lambda item: item[0]))
    output(board, solution, row, col, '_' + str(row))

    end_time = time.time()  # Record the end time
    execution_time = end_time - start_time  # Calculate the execution time
    print("Execution time:", execution_time, "seconds")