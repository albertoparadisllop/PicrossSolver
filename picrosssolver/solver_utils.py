from numpy import array as np_array
from picrosssolver.objects.state import State
from picrosssolver.objects.field_state import Field
from picrosssolver.exceptions.picross_exceptions import SolverLogicException

from copy import deepcopy
import logging


def get_bar_and_constraints(current_state:Field, column:int=None, row:int=None) -> tuple[list[int], list[int]]:
    """Gets bar values and constraints from a given row/column.

    Args:
        current_state (Field): Field to get data from
        column (int, optional): Column number. Exclusive with row. Defaults to None.
        row (int, optional): Row number. Exclusive with column. Defaults to None.

    Returns:
        tuple[list[int], list[int]]: Tuple of bar values followed by constraints for that bar
    """
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

def solve_single_bar(bar:list[int], constraints:list[int], bar_length:int) -> list[int]:
    """Given a bar and its constraints, return deduction from both

    Args:
        bar (list[int]): Bar to be updated. Result will be a further solution from this state (or the same if no deductions can be made).
        constraints (list[int]): Bar constraints to be used.
        bar_length (int): length of bar.

    Returns:
        list[int]: List with new values for bar
    """
    # Get all possibilities for those constraints in the bar
    possibilities = get_possibilities_from_constraints(constraints, bar_length, current_bar_filter=bar)


    # Filter what positions can be solved (either empty on all possibilities, or filled in all possibilites)
    return get_result_from_possibilities(possibilities)


def get_possibilities_from_constraints(constraints:list[int], bar_length:int, current_bar_filter:list[State]=None) -> list[list[State]]:
    """Get all possibilities for a solution given a constraint, bar length and optionally, filter possible solutions by a given bar.

    Args:
        constraints (list[int]): bar constraints
        bar_length (int): Bar length to be used
        current_bar_filter (list[State], optional): Bar to filter possible solutions from. Defaults to None.

    Returns:
        list[list[State]]: List containing possible bars.
    """
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
    return _regenerate_from_space_data(possibilities, constraints, current_bar_filter=current_bar_filter)


def _regenerate_from_space_data(possibilities:list[list[State]], constraints:list[int], current_bar_filter:list[State]=None) -> list[list[State]]:
    """Regenerate bar values from the weird way they were generated in get_possibilities_from_constraints()

    Args:
        possibilities (list[list[State]]): Possibilities (each is a list of non-obligatory spaces in each position)
        constraints (list[int]): constraints to be used
        current_bar_filter (list[State], optional): Bar to filter results from. Defaults to None.

    Returns:
        list[list[State]]: _description_
    """
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


def bar_compatible(bar1:list[State], bar2:list[State]) -> bool:
    """Whether the two bars could be part of the solution for a single bar (no contradictions).

    Args:
        bar1 (list[State]): One bar to be compared.
        bar2 (list[State]): Second bar to be compared.

    Returns:
        bool: Whether bars are compatible.
    """
    res = []
    if len(bar1) != len(bar2):
        raise SolverLogicException("Bars of unequal length compared")
    for i in range(len(bar1)):
        if bar1[i] == State.INDET or bar2[i] == State.INDET:
            res.append(True)
        else:
            res.append(bar1[i] == bar2[i])
    return all(res)


def get_result_from_possibilities(bar_list:list[list[State]]) -> list[State]:
    """Given a set of possibilities, get a solution of common points of all possibilities.

    Args:
        bar_list (list[list[State]]): Possibility list

    Returns:
        list[State]: Bar aggregation of all possibilities
    """
    possibilities = np_array(bar_list)
    result = []
    for i in range(possibilities.shape[1]):
        res_state = get_conclusion_from_bar_position(possibilities[:,i])
        result.append(res_state)
    return result


def get_conclusion_from_bar_position(position_res_list:list[State]) -> State:
    """From a given set of States for a given position from multiple possibilities, what the conclusion is.

    Args:
        position_res_list (list[State]): States for the same bar-position in multiple possibilities.

    Returns:
        State: Logical conclusion from those possibilities.
    """
    first_res = position_res_list[0]
    all_equal = True
    
    for item in position_res_list[1:]:
        all_equal = all_equal and first_res == item
        
    if all_equal:
        return first_res
    else:
        return State.INDET
