from numpy import array_equal
import logging

from picrosssolver.objects.field_state import Field
from picrosssolver.exceptions.picross_exceptions import UnsolvableException
import picrosssolver.solver_utils as SU



class Solver:
    
    SPIN = 1
    SPINMEM = 2
    
    def __init__(self, field:Field):
        self.current_state = field
        self.solved = self.current_state.is_solved()
        self.cols, self.rows = self.current_state.field_arr.shape
        self.bar_memory = []
        self.stale_counter = 0
        self.stale_threshold = self.cols + self.rows + 1
        
    def stale_increase(self):
        self.stale_counter += 1
        
    def stale_reset(self):
        self.stale_counter = 0
        
    def is_stale(self):
        return self.stale_counter > self.stale_threshold
    
    def solve(self, algo=SPINMEM):
        if(algo==Solver.SPIN):
            res = self.solve_spin()
        elif algo == Solver.SPINMEM:
            res = self.solve_spin_mem()
        return res
    
    def solve_spin(self):
        # Runs around calculatng all possibilities based on the current state on the board
        i = 0
        while not self.current_state.is_solved() and not self.is_stale():
            i_new = i%(self.cols+self.rows)
            if i_new // self.cols == 0:
                # Cols
                logging.info(f"CHECKING COLUMN {i_new} - Stale {self.stale_counter}/{self.stale_threshold}")
                res = self.solve_step(column=i_new, row=None)
            else:
                # Rows
                logging.info(f"CHECKING ROW {i_new%self.cols} - Stale {self.stale_counter}/{self.stale_threshold}")
                res = self.solve_step(column = None, row=i_new%self.cols)
            if res:
                logging.info(self.current_state)
            self.stale_reset() if res else self.stale_increase()
            i += 1
        if self.is_stale():
            logging.warning("UNSOLVABLE")
            logging.info(self.current_state)
            raise UnsolvableException("Solution became stale, cant solve.")
        return i
    
    def solve_spin_mem(self):
        # Same as normal spin but stores the possibilities on each row/col so it doesnt have to recalculate them,
        # Simply re-filters them on each go
        i = 0
        # Store in mem
        for i in range(self.rows+self.cols):
            row_val = None
            col_val = None
            if i // self.cols == 0:
                # Cols
                col_val = i
            else:
                # Rows
                row_val = i%self.cols
            current_bar, current_contraints = SU.get_bar_and_constraints(current_state=self.current_state,
                                                                         column=col_val, row=row_val)
            possibilities = SU.get_possibilities_from_constraints(constraints=current_contraints,
                                                                  bar_length=len(current_bar),
                                                                  current_bar_filter=current_bar)
            self.bar_memory.append(possibilities)
            self.update_bar(current_bar, SU.get_result_from_possibilities(possibilities), column = col_val, row = row_val)
        # Now we iterate filtering on the possibility memory and recalculating the result
        while not self.current_state.is_solved() and not self.is_stale():
            i_new = i%(self.cols+self.rows)
            col_val = None
            row_val = None
            if i_new // self.cols == 0:
                # Cols
                logging.info(f"CHECKING COLUMN {i_new} - Stale {self.stale_counter}/{self.stale_threshold}")
                col_val = i_new
            else:
                # Rows
                logging.info(f"CHECKING ROW {i_new%self.cols} - Stale {self.stale_counter}/{self.stale_threshold}")
                row_val = i_new%self.cols
            current_bar, current_contraints = SU.get_bar_and_constraints(current_state=self.current_state,
                                                                         column=col_val, row=row_val)
            possibilities = self.bar_memory[i_new]
            new_possibilities = []
            for possibility in possibilities:
                if SU.bar_compatible(current_bar, possibility):
                                     new_possibilities.append(possibility)
            self.bar_memory[i_new] = new_possibilities
            new_bar = SU.get_result_from_possibilities(new_possibilities)
            res = self.update_bar(current_bar, new_bar, col_val, row_val)
            if res:
                logging.info(self.current_state)
            self.stale_reset() if res else self.stale_increase()
            i += 1
        if self.is_stale():
            logging.warning("UNSOLVABLE")
            logging.info(self.current_state)
            raise UnsolvableException("Solution became stale, cant solve.")
        return i
        
        
    def solve_step(self, column:int=None, row:int=None) -> bool:
        
        current_bar, current_contraints = SU.get_bar_and_constraints(self.current_state, column, row)
        
        logging.debug(f"{current_bar}")
        logging.debug(f"Constraints: {current_contraints}")
        
        new_bar = SU.solve_single_bar(current_bar, current_contraints, bar_length=len(current_bar))
        logging.debug(new_bar)

        return self.update_bar(current_bar=current_bar, new_bar=new_bar,
                               column=column, row=row)

    def update_bar(self, current_bar, new_bar, column=None, row=None):
        # If nothing was deduced, return False, else update state and return True
        if array_equal(current_bar, new_bar):
            return False
        else:
            if column is not None:
                self.current_state.field_arr[column,:] = new_bar
            elif row is not None:
                self.current_state.field_arr[:,row] = new_bar
            return True
            
