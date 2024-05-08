import itertools
import pprint
import time

# Read the grid from a file
def read_grid(filename):
    try:
        with open(filename, 'r') as file:
            # Read and split each line by ', ', converting the text file into a list of lists
            grid = [line.strip().split(', ') for line in file]
        return grid
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None

# Write the solved grid to a file
def write_grid(grid, filename):
    try:
        with open(filename, 'w') as file:
            # Write each row of the grid to the file, joined by ', '
            for row in grid:
                file.write(', '.join(row) + '\n')
    except IOError:
        print(f"Error writing to file {filename}.")

# Validate whether a configuration of traps and gems is correct
def validate_configuration(grid, config):
    rows, cols = len(grid), len(grid[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Ensure the numbers on the grid match the number of adjacent traps
    for i in range(rows):
        for j in range(cols):
            if grid[i][j].isdigit():
                count = sum((0 <= i + di < rows and 0 <= j + dj < cols and config[i + di][j + dj] == 'T')
                            for di, dj in directions)
                if count != int(grid[i][j]):
                    return False

    # Ensure every 'T' is adjacent to at least one numeric tile
    for i in range(rows):
        for j in range(cols):
            if config[i][j] == 'T':
                if not any((0 <= i + di < rows and 0 <= j + dj < cols and grid[i + di][j + dj].isdigit())
                           for di, dj in directions):
                    return False

    return True

# Solve the puzzle using a brute force approach
def solve_gem_hunter(grid):
    rows, cols = len(grid), len(grid[0])
    indices = [(i, j) for i in range(rows) for j in range(cols) if grid[i][j] == '_']
    all_possibilities = itertools.product(['T', 'G'], repeat=len(indices))

    # Generate all possible configurations of 'T' and 'G' for the empty cells
    for possibility in all_possibilities:
        config = [row[:] for row in grid]  # Make a copy of the grid
        for (i, j), value in zip(indices, possibility):
            config[i][j] = value
        if validate_configuration(grid, config):
            return config  # Return the first valid configuration found

    return 'No valid configurations'


def main():
    input_filename = 'testcases/' + input('Enter the filename of the input file: ')
    output_filename = 'testcases/' + input('Enter the filename of the output file: ')

    start_time = time.time()
    grid = read_grid(input_filename)
    if grid:
        solution = solve_gem_hunter(grid)
        print("--- %s seconds ---" % (time.time() - start_time))
        write_grid(solution, output_filename)

if __name__ == "__main__":
    main()

# It took too much time to solve. The last time it took 10,1 mins