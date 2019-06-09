"""A command line version of Minesweeper"""
import random
import re
import time
import copy
import itertools
from string import ascii_lowercase


def setupgrid(gridsize, start, numberofmines):
    emptygrid = [['0' for i in range(gridsize)] for i in range(gridsize)]

    mines = getmines(emptygrid, start, numberofmines)

    for i, j in mines:
        emptygrid[i][j] = 'X'

    grid = getnumbers(emptygrid)

    return (grid, mines)

def showgrid(grid):
    gridsize = len(grid)

    horizontal = '   ' + (4 * gridsize * '-') + '-'

    # Print top column letters
    toplabel = '     '

    for i in ascii_lowercase[:gridsize]:
        toplabel = toplabel + i + '   '

    print(toplabel + '\n' + horizontal)

    # Print left row numbers
    for idx, i in enumerate(grid):
        row = '{0:2} |'.format(idx + 1)

        for j in i:
            row = row + ' ' + j + ' |'

        print(row + '\n' + horizontal)

    print('')


def getrandomcell(grid):
    gridsize = len(grid)

    a = random.randint(0, gridsize - 1)
    b = random.randint(0, gridsize - 1)

    return (a, b)


def getneighbors(grid, rowno, colno):
    gridsize = len(grid)
    neighbors = []

    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            elif -1 < (rowno + i) < gridsize and -1 < (colno + j) < gridsize:
                neighbors.append((rowno + i, colno + j))

    return neighbors


def getmines(grid, start, numberofmines):
    mines = []
    neighbors = getneighbors(grid, *start)

    for i in range(numberofmines):
        cell = getrandomcell(grid)
        while cell == start or cell in mines or cell in neighbors:
            cell = getrandomcell(grid)
        mines.append(cell)

    return mines


def getnumbers(grid):
    for rowno, row in enumerate(grid):
        for colno, cell in enumerate(row):
            if cell != 'X':
                # Gets the values of the neighbors
                values = [grid[r][c] for r, c in getneighbors(grid,
                                                              rowno, colno)]

                # Counts how many are mines
                grid[rowno][colno] = str(values.count('X'))

    return grid


def showcells(grid, currgrid, rowno, colno):
    # Exit function if the cell was already shown
    if currgrid[rowno][colno] != ' ':
        return

    # Show current cell
    currgrid[rowno][colno] = grid[rowno][colno]

    # Get the neighbors if the cell is empty
    if grid[rowno][colno] == '0':
        for r, c in getneighbors(grid, rowno, colno):
            # Repeat function for each neighbor that doesn't have a flag
            if currgrid[r][c] != 'F':
                showcells(grid, currgrid, r, c)


def playagain():
    choice = input('Play again? (y/n): ')

    return choice.lower() == 'y'


def parseinput(inputstring, gridsize, helpmessage):
    cell = ()
    flag = False
    message = "Invalid cell. " + helpmessage

    pattern = r'([a-{}])([0-9]+)(f?)'.format(ascii_lowercase[gridsize - 1])
    validinput = re.match(pattern, inputstring)

    if inputstring == 'help':
        message = helpmessage

    elif validinput:
        rowno = int(validinput.group(2)) - 1
        colno = ascii_lowercase.index(validinput.group(1))
        flag = bool(validinput.group(3))

        if -1 < rowno < gridsize:
            cell = (rowno, colno)
            message = ''

    return {'cell': cell, 'flag': flag, 'message': message}


def playgame():
    gridsize = 9
    numberofmines = 10

    currgrid = [[' ' for i in range(gridsize)] for i in range(gridsize)]

    grid = []
    flags = []
    starttime = 0

    helpmessage = ("Type the column followed by the row (eg. a5). "
                   "To put or remove a flag, add 'f' to the cell (eg. a5f).")

    showgrid(currgrid)
    print(helpmessage + " Type 'help' to show this message again.\n")

    while True:
        minesleft = numberofmines - len(flags)
        prompt = input('Enter the cell ({} mines left): '.format(minesleft))
        result = parseinput(prompt, gridsize, helpmessage + '\n')

        message = result['message']
        cell = result['cell']
        
        print('AI chose: ' + str(cell))
        if cell:
            print('\n\n')
            rowno, colno = cell
            currcell = currgrid[rowno][colno]
            flag = result['flag']

            if not grid:
                grid, mines = setupgrid(gridsize, cell, numberofmines)
            if not starttime:
                starttime = time.time()

            if flag:
                # Add a flag if the cell is empty
                if currcell == ' ':
                    currgrid[rowno][colno] = 'F'
                    flags.append(cell)
                # Remove the flag if there is one
                elif currcell == 'F':
                    currgrid[rowno][colno] = ' '
                    flags.remove(cell)
                else:
                    message = 'Cannot put a flag there'

            # If there is a flag there, show a message
            elif cell in flags:
                message = 'There is a flag there'

            elif grid[rowno][colno] == 'X':
                print('Game Over\n')
                showgrid(grid)
                if playagain():
                    playgame()
                return

            elif currcell == ' ':
                showcells(grid, currgrid, rowno, colno)

            else:
                message = "That cell is already shown"

            if set(flags) == set(mines):
                minutes, seconds = divmod(int(time.time() - starttime), 60)
                print(
                    'You Win. '
                    'It took you {} minutes and {} seconds.\n'.format(minutes,
                                                                      seconds))
                showgrid(grid)
                if playagain():
                    playgame()
                return

        showgrid(currgrid)
        print(message)

class AI:
    def __init__(self, grid_size, grid):
        self.grid = grid
        self.grid_size = grid_size
        self.directions = [(-1,-1), (-1,0), (0,-1), (1,1), (1,0), (0,1), (-1,1), (1,-1)]
        self.bomb_marker = 'x'
        self.no_bomb_marker = 'o'

    def get_new_blank_grid(self):
        return copy.deepcopy(self.grid)

    def parse_input(self, cellchoice, helpmessage):
        return {'cell': cellchoice, 'flag': False, 'message': helpmessage}

    def is_valid_cell(self, cell):
        return cell[0] >= 0 and cell[1] >= 0 and cell[0] < self.grid_size and cell[1] < self.grid_size

    def add_offset(self, cell, offset):
        return (cell[0] + offset[0], cell[1] + offset[1])

    def get_grid_value(self, cell, grid=None):
        if grid == None:
            grid = self.grid
        return grid[cell[0]][cell[1]]

    def set_grid_value(self, cell, grid, value):
        grid[cell[0]][cell[1]] = value

    def get_valid_adjacencies(self, cell):
        for direction in self.directions:
            new_cell = self.add_offset(cell, direction)
            if self.is_valid_cell(new_cell):
                yield new_cell

    def get_uncovered_adjacencies(self, cell):
        return [new_cell for new_cell in self.get_valid_adjacencies(cell) if self.get_grid_value(new_cell) == ' ']
    
    def mark_possible_mines(self, mine_cells, all_cells):
        if len(all_cells) == 0:
            return None
        new_grid = self.get_new_blank_grid()
        for cell in all_cells:
            self.set_grid_value(cell, new_grid, self.no_bomb_marker)
        for cell in mine_cells:
            self.set_grid_value(cell, new_grid, self.bomb_marker)
        
        return new_grid

    def get_mine_combinations(self, cell):
        uncovered_cells = self.get_uncovered_adjacencies(cell)
        try:
            num_mines = int(self.get_grid_value(cell))
            possible_combinations = list(itertools.combinations(uncovered_cells, num_mines))
            if len(possible_combinations[0]) == 0:
                return None
            return [self.mark_possible_mines(combination, uncovered_cells) for combination in possible_combinations]
            
        except ValueError:
            return None
    
    def get_grid_iter(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                yield (i, j)

    def get_cell_options(self, cell=(0,0)):
        grids = []
        
        for cell in self.get_grid_iter():
            combinations = self.get_mine_combinations(cell)
            if combinations != None:
                grids.append(combinations)
    
        return grids

    def cells_match(self, val1, val2):
        return not ((val1 == self.bomb_marker and val2 == self.no_bomb_marker) or (val1 == self.no_bomb_marker and val2 == self.bomb_marker))

    def get_important_value(self, val1, val2):
        if val1 == self.bomb_marker or val1 == self.no_bomb_marker:
            return val1
        else:
            return val2
    
    def merge_grids(self, grid1, grid2):
        merged_grid = self.get_new_blank_grid()
        for cell in self.get_grid_iter():
            grid1_val = self.get_grid_value(cell, grid1)
            grid2_val = self.get_grid_value(cell, grid2)
            if not self.cells_match(grid1_val, grid2_val):
                return None
            self.set_grid_value(cell, merged_grid, self.get_important_value(grid1_val, grid2_val))
        return merged_grid

    def get_possible_solutions(self):
        groups = self.get_cell_options()
        
        merged_grids = groups[0]
        for group in groups[1:]:
            matches = []
            for grid1 in merged_grids:
                for grid2 in group:
                    merged_grid = self.merge_grids(grid1, grid2)
                    if merged_grid != None:
                        matches.append(merged_grid)
            merged_grids = matches
        return merged_grids

    def merge_solutions(self, solutions):
        new_grid = self.get_new_blank_grid()
        for cell in self.get_grid_iter():
            vals = [self.get_grid_value(cell, grid) for grid in solutions]
            if vals.count(vals[0]) == len(vals):
                self.set_grid_value(cell, new_grid, vals[0])
            else:
                self.set_grid_value(cell, new_grid, ' ')
        return new_grid
    
    def get_confident_choice(self, cell, grid):
        try:
            num_bombs = int(self.get_grid_value(cell, grid))
            bombs_found = 0
            non_bomb_cell = None
            for adj_cell in self.get_valid_adjacencies(cell):
                val = self.get_grid_value(adj_cell, grid)
                if val == self.bomb_marker:
                    bombs_found += 1
                elif val == self.no_bomb_marker:
                    return adj_cell
            if bombs_found == num_bombs:
                return non_bomb_cell
            return None
        except ValueError:
            return None

    def get_probable_choice(self, solutions):
        probabilities = {}
        for cell in self.get_grid_iter():
            probabilities[cell] = 0
            for solution in solutions:
                grid_value = self.get_grid_value(cell, solution)
                if grid_value not in (self.no_bomb_marker, ' '):
                    probabilities[cell] = -1
                elif self.get_grid_value(cell, solution) == self.no_bomb_marker:
                    probabilities[cell] += 1
        max_cell = max(probabilities.keys(), key=(lambda key: probabilities[key]))
        print(f'Max probability: {probabilities[max_cell]} / {len(solutions)}')
        return max_cell

    def choose_next_move(self, grid):
        self.grid = grid
        solutions = self.get_possible_solutions()

        solution = self.merge_solutions(solutions)
        
        for cell in self.get_grid_iter():
            choice = self.get_confident_choice(cell, solution)
            if choice != None:
                print('Definitive choice')
                return choice
        
        print('Probable choice')
        return self.get_probable_choice(solutions)
        

def checkforwin(grid, displaygrid, gridsize):
    for i in range(gridsize):
        for j in range(gridsize):
            if displaygrid[i][j] == ' ' and grid[i][j] != 'X':
                return False
    return True
    
def playai():
    gridsize = 10
    numberofmines = 20
    
    currgrid = [[' ' for i in range(gridsize)] for i in range(gridsize)]
    ai = AI(gridsize, currgrid)
    grid = []
    flags = []
    starttime = 0

    helpmessage = ("Type the column followed by the row (eg. a5). "
                   "To put or remove a flag, add 'f' to the cell (eg. a5f).")

    showgrid(currgrid)
    aichoice = (0,0)
    print(helpmessage + " Type 'help' to show this message again.\n")

    while True:
        minesleft = numberofmines - len(flags)
        prompt = input('Press enter to let the AI make a move ({} mines left): '.format(minesleft))
        result = ai.parse_input(aichoice, helpmessage + '\n')

        message = result['message']
        cell = result['cell']
        print('AI chose: ' + str(cell))
        if cell:
            print('\n\n')
            rowno, colno = cell
            currcell = currgrid[rowno][colno]
            flag = result['flag']

            if not grid:
                grid, mines = setupgrid(gridsize, cell, numberofmines)
            if not starttime:
                starttime = time.time()

            if flag:
                # Add a flag if the cell is empty
                if currcell == ' ':
                    currgrid[rowno][colno] = 'F'
                    flags.append(cell)
                # Remove the flag if there is one
                elif currcell == 'F':
                    currgrid[rowno][colno] = ' '
                    flags.remove(cell)
                else:
                    message = 'Cannot put a flag there'

            # If there is a flag there, show a message
            elif cell in flags:
                message = 'There is a flag there'

            elif grid[rowno][colno] == 'X':
                print('Game Over\n')
                showgrid(grid)
                if playagain():
                    playai()
                return

            elif currcell == ' ':
                showcells(grid, currgrid, rowno, colno)
                if checkforwin(grid, currgrid, gridsize):
                    minutes, seconds = divmod(int(time.time() - starttime), 60)
                    print(
                        'You Win. '
                        'It took you {} minutes and {} seconds.\n'.format(minutes,
                                                                        seconds))
                    showgrid(grid)
                    if playagain():
                        playai()
                    return


            else:
                message = "That cell is already shown"


        showgrid(currgrid)
        aichoice = ai.choose_next_move(currgrid)
        if grid[aichoice[0]][aichoice[1]] == 'X':
            aichoice = ai.choose_next_move(currgrid)

        print(message)

playai()
