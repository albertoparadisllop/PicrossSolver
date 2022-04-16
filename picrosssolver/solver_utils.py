from numpy import array as np_array
from picrosssolver.objects.state import State
from picrosssolver.exceptions.picross_exceptions import SolverLogicException

from copy import deepcopy
import logging


def get_bar_and_constraints(current_state, column=None, row=None):
    if column is not None and row is not None:
            raise SolverLogicException("Only a row or a column can be specified, not both")
    if column is not None:
        current_bar = current_state.field_arr[column,:]
        current_contraints = current_state.column_values[column]
        logging.debug(f"COLUMN")
    elif row is not None:
        current_bar = current_state.field_arr[:,row]
        current_contraints = current_state.row_values[row]
        logging.debug(f"ROW")
    else:
        raise SolverLogicException("No row or column to solve specified in Solve Step")
    return current_bar, current_contraints

def solve_single_bar(bar, constraints, bar_length):
    # Get all possibilities for those constraints in the bar
    possibilities = get_possibilities_from_constraints(constraints, bar_length, current_bar_filter=bar)


    # Filter what positions can be solved (either empty on all possibilities, or filled in all possibilites)
    return get_result_from_possibilities(possibilities)


def get_possibilities_from_constraints(constraints, bar_length, current_bar_filter=None):
    spaces = bar_length-sum(constraints)
    intermediate_spaces = (len(constraints)-1)
    leeway = spaces-intermediate_spaces
    
    max_space = intermediate_spaces+1
    # Possibilities here refers to how many non-obligatory spaces between each obligatory item
    # This means add one extra space between each constraint
    # [0,2,0] for constraints [1,1] on bar length 5 mean [#,X,X,X,#] 
    #               ->  0 on the left, 2 (+ 1 obligatory) in the middle, 0 on right
    # [1,1,2,0] for constraints [2,4,3] on bar length mean [X,#,#,X,X,#,#,#,#,X,X,X,#,#,#]
    #               ->  1 on left, 1 (+ 1 ob) on next, 2 (+ 1 ob) on next, 0 on right
    possibilities = [[]]
    # End when all possibilities have a length of the required number of spaces
    for i in range(max_space+1):
        new_possibilities = []
        for possibility in possibilities:
            remaining_spaces = leeway-sum(possibility)
            start_index = remaining_spaces if i==max_space else 0
            for j in range(start_index, remaining_spaces+1):
                new_possibility = deepcopy(possibility)
                new_possibility.append(j)
                new_possibilities.append(new_possibility)
        possibilities = new_possibilities
        logging.debug(possibilities)
    return regenerate_from_space_data(possibilities, constraints, current_bar_filter=current_bar_filter)


def regenerate_from_space_data(possibilities, constraints, current_bar_filter=None):
    bar_possibility_list = []
    for possibility in possibilities:
        new_bar = []
        for i in range(len(possibility)):
            new_bar = new_bar + [State.EMPTY]*(possibility[i]+(1 if i > 0 and i < len(possibility)-1 else 0))
            if i < len(possibility)-1:
                new_bar = new_bar + [State.FILL]*constraints[i]
        if(current_bar_filter is None or bar_compatible(new_bar, current_bar_filter)):
            bar_possibility_list.append(new_bar)
    return bar_possibility_list


def bar_compatible(bar1, bar2):
    res = []
    if len(bar1) != len(bar2):
        raise SolverLogicException("Bars of unequal length compared")
    for i in range(len(bar1)):
        if bar1[i] == State.INDET or bar2[i] == State.INDET:
            res.append(True)
        else:
            res.append(bar1[i] == bar2[i])
    return all(res)


def get_result_from_possibilities(bar_list):
    possibilities = np_array(bar_list)
    result = []
    for i in range(possibilities.shape[1]):
        res_state = get_conclusion_from_bar_position(possibilities[:,i])
        result.append(res_state)
    return result


def get_conclusion_from_bar_position(position_res_list):
    first_res = position_res_list[0]
    all_equal = True
    
    for item in position_res_list[1:]:
        all_equal = all_equal and first_res == item
        
    if all_equal:
        return first_res
    else:
        return State.INDET
