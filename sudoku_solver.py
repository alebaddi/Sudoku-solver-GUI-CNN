import numpy as np


def empty_position(sudoku):
    '''Find the row and column indices of the empty positions of a sudoku'''
    for i in range(len(sudoku)):
        for j in range(len(sudoku[0])):
            if sudoku[i][j] == 0:
                return i, j

    return None


def check_sudoku(sudoku, number, position):
    '''Check if rows, columns and blocks of a sudoku have all the numbers from 1 to 9'''
    for j in range(len(sudoku[0])):
        if sudoku[position[0]][j] == number and position[1] != j:
            return False

    for i in range(len(sudoku)):
        if sudoku[i][position[1]] == number and position[0] != i:
            return False

    n = 3
    a = position[0] // n
    b = position[1] // n

    for i in range(a*n, a*n + n):
        for j in range(b*n, b*n + n):
            if sudoku[i][j] == number and (i, j) != position:
                return False

    return True


def solve_sudoku(sudoku):
    '''Solve a sudoku that must be a 9x9 array'''
    # check the puzzle validity
    for i in range(len(sudoku[0])):
        for j in range(len(sudoku[0])):
            if sudoku[i][j] != 0:
                if check_sudoku(sudoku, sudoku[i][j], (i, j)) == False:
                    return False

    # find empty positions
    if not empty_position(sudoku):
        return True
    else:
        row, col = empty_position(sudoku)

    # check if the conditions are satisfied for each digit entered
    for n in range(1, len(sudoku[0])+1):
        if check_sudoku(sudoku, n, (row, col)):
            sudoku[row][col] = n

            if solve_sudoku(sudoku):
                return True

            sudoku[row][col] = 0

    return False
