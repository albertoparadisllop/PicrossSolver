from picrosssolver.solver import Solver
from picrosssolver.objects.field_state import Field

import logging

def test_solver_small():
    column_constraints = [[0], [1,1], [1,1], [5], [0]]
    row_constraints = [[3], [1], [3], [1], [1]]
    
    newState = Field(column_values=column_constraints,
                     row_values=row_constraints)
    
    mySolver = Solver(newState)
    
    num = mySolver.solve()
    print(f"{num} iterations")
    print_solved(mySolver)
    
def test_solver_big():
    column_constraints = [[2], [2,3], [4,2], [7,2], [4,5], [4,4,2], [4,7], [2,6], [2,5], [4,2,2], [4,8], [4,2,4], [6,3], [4], [2]]
    row_constraints = [[0],[2,2],[4,4],[4,4],[5,5],[2,4,3],[5,1,5],[6,5],[6,2],[5,2],[2,3,3],[2,4,3],[2,8],[2,5],[2]]
    
    newState = Field(column_values=column_constraints,
                     row_values=row_constraints)
    
    mySolver = Solver(newState)
    
    num = mySolver.solve()
    print(f"{num} iterations")
    print_solved(mySolver)
    
    
 
def print_solved(solver:Solver):
    print()
    print("################################################")
    print("SOLVED")
    print("################################################")
    print(solver.current_state)
    print("################################################")

if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    test_solver_big()