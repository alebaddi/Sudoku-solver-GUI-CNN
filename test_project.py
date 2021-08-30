import numpy as np
import random
from sudoku_solver import empty_position, check_sudoku, solve_sudoku
from sudoku_extrapolation import extrapolate_sudoku
import pytest
import hypothesis
from hypothesis import given
import hypothesis.strategies as st


######################################################################################################
## tests for sudoku_solver.py

# ====================================================================================================
# PROPERTY TESTING
# ====================================================================================================

@given(row=st.integers(min_value=0,max_value=8), col=st.integers(min_value=0,max_value=8))
def test_empty_position_all(row, col):
    '''Test if a all empty positions are found correctly'''
    sudoku = [
        [2, 4, 7, 1, 6, 5, 8, 3, 9],
        [6, 3, 9, 2, 7, 8, 1, 4, 5],
        [1, 8, 5, 4, 9, 3, 7, 6, 2],
        [5, 9, 2, 3, 1, 6, 4, 7, 8],
        [4, 6, 8, 5, 2, 7, 9, 1, 3],
        [7, 1, 3, 8, 4, 9, 2, 5, 6],
        [9, 2, 6, 7, 3, 1, 5, 8, 4],
        [8, 7, 4, 6, 5, 2, 3, 9, 1],
        [3, 5, 1, 9, 8, 4, 6, 2, 7]
    ]
    sudoku_with_zero = np.copy(sudoku)
    sudoku_with_zero[row][col] = 0
    assert empty_position(sudoku_with_zero) == (row, col), f"Should be ({row}, {col})"


@given(row=st.integers(min_value=0,max_value=8), col=st.integers(min_value=0,max_value=8))
def test_check_sudoku_all(row, col):
    '''Test if all the numbers of a completed sudoku are not repeated'''
    sudoku = [
        [2, 4, 7, 1, 6, 5, 8, 3, 9],
        [6, 3, 9, 2, 7, 8, 1, 4, 5],
        [1, 8, 5, 4, 9, 3, 7, 6, 2],
        [5, 9, 2, 3, 1, 6, 4, 7, 8],
        [4, 6, 8, 5, 2, 7, 9, 1, 3],
        [7, 1, 3, 8, 4, 9, 2, 5, 6],
        [9, 2, 6, 7, 3, 1, 5, 8, 4],
        [8, 7, 4, 6, 5, 2, 3, 9, 1],
        [3, 5, 1, 9, 8, 4, 6, 2, 7]
    ]
    assert check_sudoku(sudoku, sudoku[row][col], (row, col)) == True, "Should be True"


# ====================================================================================================
# UNIT TESTING
# ====================================================================================================

def test_empty_position_4_1():
    '''Test if the empty position (4, 1) is found correctly'''
    sudoku = [
        [2, 4, 7, 1, 6, 5, 8, 3, 9],
        [6, 3, 9, 2, 7, 8, 1, 4, 5],
        [1, 8, 5, 4, 9, 3, 7, 6, 2],
        [5, 9, 2, 3, 1, 6, 4, 7, 8],
        [4, 0, 8, 5, 2, 7, 9, 1, 3],
        [7, 1, 3, 8, 4, 9, 2, 5, 6],
        [9, 2, 6, 7, 3, 1, 5, 8, 4],
        [8, 7, 4, 6, 5, 2, 3, 9, 1],
        [3, 5, 1, 9, 8, 4, 6, 2, 7]
    ]
    assert empty_position(sudoku) == (4, 1), "Should be (4, 1)"


def test_empty_position_random():
    '''Test if a random empty position is found correctly'''
    sudoku = [
        [2, 4, 7, 1, 6, 5, 8, 3, 9],
        [6, 3, 9, 2, 7, 8, 1, 4, 5],
        [1, 8, 5, 4, 9, 3, 7, 6, 2],
        [5, 9, 2, 3, 1, 6, 4, 7, 8],
        [4, 6, 8, 5, 2, 7, 9, 1, 3],
        [7, 1, 3, 8, 4, 9, 2, 5, 6],
        [9, 2, 6, 7, 3, 1, 5, 8, 4],
        [8, 7, 4, 6, 5, 2, 3, 9, 1],
        [3, 5, 1, 9, 8, 4, 6, 2, 7]
    ]
    sudoku_with_zero = np.copy(sudoku)
    row = random.randint(0,8)
    col = random.randint(0,8)
    sudoku_with_zero[row][col] = 0
    assert empty_position(sudoku_with_zero) == (row, col), f"Should be ({row}, {col})"


def test_empty_postion_2x3():
    '''Test if the function works even with (2, 3) arrays'''
    my_array = [
        [1, 2, 3],
        [4, 0, 6]
    ]
    assert empty_position(my_array) == (1, 1), "Should be (1, 1)"


def test_check_sudoku_3_5():
    '''Test if a number of a completed sudoku is not repeated'''
    sudoku = [
        [2, 4, 7, 1, 6, 5, 8, 3, 9],
        [6, 3, 9, 2, 7, 8, 1, 4, 5],
        [1, 8, 5, 4, 9, 3, 7, 6, 2],
        [5, 9, 2, 3, 1, 6, 4, 7, 8],
        [4, 6, 8, 5, 2, 7, 9, 1, 3],
        [7, 1, 3, 8, 4, 9, 2, 5, 6],
        [9, 2, 6, 7, 3, 1, 5, 8, 4],
        [8, 7, 4, 6, 5, 2, 3, 9, 1],
        [3, 5, 1, 9, 8, 4, 6, 2, 7]
    ]
    assert check_sudoku(sudoku, sudoku[3][5], (3, 5)) == True, "Should be True"


def test_check_sudoku_8_1():
    '''Test if a number of a completed sudoku is repeated'''
    sudoku = [
        [2, 4, 7, 1, 6, 5, 8, 3, 9],
        [6, 3, 9, 2, 7, 8, 1, 4, 5],
        [1, 8, 5, 4, 9, 3, 7, 6, 2],
        [5, 9, 2, 3, 1, 6, 4, 7, 8],
        [4, 6, 8, 5, 2, 7, 9, 1, 3],
        [7, 1, 3, 8, 4, 9, 2, 5, 6],
        [9, 2, 6, 7, 3, 1, 5, 8, 4],
        [8, 7, 4, 6, 5, 2, 3, 9, 1],
        [3, 5, 1, 9, 8, 4, 6, 2, 7]
    ]
    assert check_sudoku(sudoku, 1, (8, 1)) == False, "Should be False"


def test_check_sudoku_row():
    '''Test if it is correctly recongnized that there are no repetition of a number in a row'''
    sudoku = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [7, 0, 3, 8, 4, 9, 2, 5, 6],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]
    assert check_sudoku(sudoku, 1, (2, 1)) == True, "Should be True"


def test_check_sudoku_column():
    '''Test if it is correctly recongnized that there is a repetition of a number in a column'''
    sudoku = [
        [0, 0, 0, 0, 0, 0, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 5, 0, 0],
        [0, 0, 0, 0, 0, 0, 4, 0, 0],
        [0, 0, 0, 0, 0, 0, 3, 0, 0],
        [0, 0, 0, 0, 0, 0, 7, 0, 0],
        [0, 0, 0, 0, 0, 0, 9, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 6, 0, 0]
    ]
    assert check_sudoku(sudoku, 7, (1, 6)) == False, "Should be False"


def test_check_sudoku_block():
    '''Test if it is correctly recongnized that there is a repetition of a number in a block'''
    sudoku = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 3, 1, 8, 0, 0, 0],
        [0, 0, 0, 5, 9, 0, 0, 0, 0],
        [0, 0, 0, 6, 7, 4, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]
    assert check_sudoku(sudoku, 3, (4, 5)) == False, "Should be False"


def test_check_2x3():
    '''Test if the function does not work with (2, 3) arrays'''
    my_array = [
        [1, 2, 3],
        [4, 0, 6]
    ]
    with pytest.raises(IndexError):
        check_sudoku(my_array, 5, (1, 1))


def test_solve_sudoku_1():
    '''Test if a valid sudoku puzzle is solved'''
    sudoku = [
        [7, 5, 0, 0, 0, 0, 2, 0, 0],
        [2, 6, 9, 0, 0, 7, 0, 0, 0],
        [0, 3, 0, 0, 8, 9, 0, 0, 7],
        [0, 0, 0, 6, 0, 2, 3, 8, 0],
        [0, 0, 6, 0, 3, 0, 4, 0, 0],
        [0, 9, 2, 8, 0, 4, 0, 0, 0],
        [5, 0, 0, 9, 2, 0, 0, 6, 0],
        [0, 0, 0, 3, 0, 0, 9, 2, 5],
        [0, 0, 3, 0, 0, 0, 0, 1, 4]
    ]
    assert solve_sudoku(sudoku) == True, "Should be True"
    solve_sudoku(sudoku)
    for i in range(len(sudoku)):
        for j in range(len(sudoku)):
            assert check_sudoku(sudoku, sudoku[i][j], (i, j)) == True, "Should be True"


def test_solve_sudoku_2():
    '''Test if a sudoku puzzle with a repetition is not solved'''
    sudoku = [
        [4, 0, 0, 6, 7, 0, 0, 8, 0],
        [0, 1, 0, 3, 0, 0, 0, 2, 4],
        [0, 0, 9, 0, 0, 1, 6, 0, 0],
        [7, 9, 4, 5, 0, 0, 4, 0, 0],
        [5, 0, 0, 0, 3, 0, 0, 0, 8],
        [0, 0, 8, 0, 0, 2, 0, 7, 9],
        [0, 0, 6, 7, 0, 0, 8, 0, 0],
        [2, 7, 0, 0, 0, 4, 0, 9, 0],
        [0, 8, 0, 0, 2, 3, 0, 0, 6]
    ]
    assert solve_sudoku(sudoku) == False, "Should be False"


def test_solve_sudoku_3():
    '''Test if an impossible sudoku puzzle is not solved'''
    sudoku = [
        [4, 0, 0, 6, 7, 0, 0, 8, 0],
        [8, 1, 0, 3, 0, 0, 0, 2, 4],
        [0, 0, 9, 0, 0, 1, 6, 0, 0],
        [7, 9, 0, 5, 0, 0, 4, 0, 0],
        [5, 0, 0, 0, 3, 0, 0, 0, 8],
        [0, 0, 8, 0, 0, 2, 0, 7, 9],
        [0, 0, 6, 7, 0, 0, 8, 0, 0],
        [2, 7, 0, 0, 0, 4, 0, 9, 0],
        [0, 8, 0, 0, 2, 3, 0, 0, 6]
    ]
    assert solve_sudoku(sudoku) == False, "Should be False"

def test_solve_sudoku_empty():
    '''Test how an empty sudoku is filled'''
    empty_sudoku= np.zeros((9, 9), dtype=np.int8)
    sudoku = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 1, 4, 3, 6, 5, 8, 9, 7],
        [3, 6, 5, 8, 9, 7, 2, 1, 4],
        [8, 9, 7, 2, 1, 4, 3, 6, 5],
        [5, 3, 1, 6, 4, 2, 9, 7, 8],
        [6, 4, 2, 9, 7, 8, 5, 3, 1],
        [9, 7, 8, 5, 3, 1, 6, 4, 2]
    ]
    assert solve_sudoku(empty_sudoku) == True, "Should be True"
    solve_sudoku(empty_sudoku)
    assert (empty_sudoku == sudoku).all() == True, "Should be filled in a different way"


######################################################################################################
## tests for sudoku_extrapolation.py

# ====================================================================================================
# UNIT TESTING
# ====================================================================================================

def test_extrapolation_sudoku():
    '''Test if a sudoku puzzle is extracted correctly from an image'''
    sudoku = [
        [6, 0, 0, 7, 0, 0, 0, 2, 1],
        [0, 2, 0, 3, 0, 0, 7, 0, 4],
        [0, 0, 3, 1, 0, 0, 0, 5, 0],
        [8, 4, 7, 0, 3, 0, 0, 0, 0],
        [0, 0, 0, 6, 1, 8, 0, 0, 0],
        [0, 0, 0, 0, 4, 0, 9, 3, 8],
        [0, 7, 0, 0, 0, 2, 1, 0, 0],
        [3, 0, 9, 0, 0, 1, 0, 7, 0],
        [2, 6, 0, 0, 0, 3, 0, 0, 9]
    ]
    sudoku_image = "icon_and_demo_images/images_for_testing/sudoku_16.jpg"
    model_name = "sudoku_model/model_sudoku.hdf5"
    assert (extrapolate_sudoku(sudoku_image, model_name) == sudoku).all(), "Should be a different puzzle"


def test_extrapolation_handwritten_sudoku():
    '''Test if a sudoku puzzle with handwritten digits is extracted correctly from an image'''
    sudoku = [
        [0, 4, 0, 1, 0, 5, 0, 3, 9],
        [6, 3, 0, 0, 7, 8, 1, 4, 5],
        [1, 0, 5, 4, 0, 3, 7, 6, 0],
        [5, 0, 0, 3, 1, 6, 4, 7, 0],
        [4, 6, 0, 5, 2, 0, 0, 1, 3],
        [0, 1, 3, 8, 4, 0, 0, 5, 6],
        [0, 0, 6, 7, 3, 1, 5, 8, 4],
        [8, 7, 4, 6, 5, 2, 3, 9, 1],
        [3, 5, 1, 9, 8, 4, 6, 2, 7]
    ]
    sudoku_image = "icon_and_demo_images/images_for_testing/sudoku_hand_15.JPG"
    model_name = "sudoku_model/model_sudoku_mnist.hdf5"
    assert (extrapolate_sudoku(sudoku_image, model_name) == sudoku).all(), "Should be a different puzzle"


def test_extrapolate_empty_image():
    '''Test if nothing is detected'''
    sudoku = np.zeros((9, 9), dtype=np.int8)
    sudoku_image = "icon_and_demo_images/images_for_testing/not_sudoku.PNG"
    model_name = "sudoku_model/model_sudoku.hdf5"
    assert (extrapolate_sudoku(sudoku_image, model_name) == sudoku).all(), "Should be an empty array"


def test_extrapolate_no_model():
    '''Test error if is given an empty model path'''
    sudoku_image = "icon_and_demo_images/images_for_testing/sudoku_hand_15.JPG"
    model_name = ''
    with pytest.raises(IOError):
        extrapolate_sudoku(sudoku_image, model_name)


def test_extrapolate_no_image():
    '''Test error if is given an empty image path'''
    sudoku_image = ''
    model_name = "sudoku_model/model_sudoku.hdf5"
    with pytest.raises(AttributeError):
        extrapolate_sudoku(sudoku_image, model_name)
