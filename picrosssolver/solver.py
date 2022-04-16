from numpy import array_equal
import logging

from picrosssolver.objects.field_state import Field
from picrosssolver.exceptions.picross_exceptions import UnsolvableException
from picrosssolver.objects.state import State
import picrosssolver.solver_utils as SU



class Solver:
    """Base solver class
    """
    
    SPIN = 1
    SPINMEM = 2
    
    def __init__(self, field:Field):
        """Create Solver object from given Field.

        Args:
            field (Field): Field the solver will attempt to solve.
        """
        self.current_state = field
        self.solved = self.current_state.is_solved()
        self.cols, self.rows = self.current_state.field_arr.shape
        self.bar_memory = []
        self.stale_counter = 0
        self.stale_threshold = self.cols + self.rows + 1
         
    @classmethod
    def from_constraints(cls, column_constraints:list[int], row_constraints:list[int]) -> 'Solver':
        """Creates Solver object with given column and row constraints.

        Args:
            column_constraints (list[int]): List of constraints for the columns.
            row_constraints (list[int]): List of constraints for the rows.

        Returns:
            Solver: Solver initialized with the given constraints.
        """
        field = Field(column_values=column_constraints,
                      row_values=row_constraints)
        return cls(field)
    
    def stale_increase(self) -> None:
        """Increase stale counter by 1.
        """
        self.stale_counter += 1
        
    def stale_reset(self) -> None:
        """Reset stale counter to 0.
        """
        self.stale_counter = 0
        
    def is_stale(self) -> bool:
        """Whether the current solution is stale.
        """
        return self.stale_counter > self.stale_threshold
    
    def solve(self, algo=SPINMEM) -> int:
        """Attempts to solve current state

        Args:
            algo (optional): What algorithm to use. Options are SPIN or SPINMEM. SPINMEM is faster. Defaults to SPINMEM.

        Raises:
            UnsolvableException: Raises this if no solution can be found.

        Returns:
            int: Iterations taken to find a solution .
        """
        if(algo==Solver.SPIN):
            res = self._solve_spin()
        elif algo == Solver.SPINMEM:
            res = self._solve_spin_mem()
        return res
    
    def _solve_spin(self) -> int:
        """Solves current state with the spin algorithm.

        Raises:
            UnsolvableException: Raises this if no solution can be found.

        Returns:
            int: Iterations taken to find solution.
        """
        # Runs around calculatng all possibilities based on the current state on the board
        i = 0
        # If solved or stale, stop, else iterate with `i`.
        while not self.current_state.is_solved() and not self.is_stale():
            # Make sure i does not get out of bounds
            i_new = i%(self.cols+self.rows)
            row_val = None
            col_val = None
            # columns then rows
            if i_new // self.cols == 0:
                # Cols
                logging.info(f"CHECKING COLUMN {i_new} - Stale {self.stale_counter}/{self.stale_threshold}")
                col_val = i_new
            else:
                # Rows
                logging.info(f"CHECKING ROW {i_new%self.cols} - Stale {self.stale_counter}/{self.stale_threshold}")
                row_val = i_new%self.cols
            res = self.solve_step(column=col_val, row=row_val)

            # If bar was updated to something new, reset stale meter. Else increase by one.
            if res:
                logging.info(self.current_state)
                self.stale_reset()
            else:
                self.stale_increase()
            i += 1
        # If stale, exit
        if self.is_stale():
            logging.warning("UNSOLVABLE")
            logging.info(self.current_state)
            raise UnsolvableException("Solution became stale, cant solve.")
        return i
    
    def _solve_spin_mem(self) -> int:
        """Attempts to solve using spin algorithm with memory, instead of recalculating each iteration.

        Raises:
            UnsolvableException: Raises this if no solution can be found.

        Returns:
            int: number of iterations taken to find solution.
        """
        # Same as normal spin but stores the possibilities on each row/col so it doesnt have to recalculate them,
        # Simply re-filters them on each go
        i = 0
        # Store in self.bar_memory
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
            # Store on memory, will not recalculate these, simply filter them in the future until 1 is achieved.
            self.bar_memory.append(possibilities)

        # Now we iterate filtering on the possibility memory and filtering the possible bars from its current state
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
            # Get current state of bar
            current_bar, current_contraints = SU.get_bar_and_constraints(current_state=self.current_state,
                                                                         column=col_val, row=row_val)
            # Get possibilities from last iteration
            possibilities = self.bar_memory[i_new]
            new_possibilities = []
            # Update possibilities based on what we know on current_bar
            for possibility in possibilities:
                if SU.bar_compatible(current_bar, possibility):
                                     new_possibilities.append(possibility)
            # Update this bar's memory
            self.bar_memory[i_new] = new_possibilities
            # Update bar if its different to old one
            new_bar = SU.get_result_from_possibilities(new_possibilities)
            res = self.update_bar(current_bar, new_bar, col_val, row_val)
            
            # If bar was updated to something new, reset stale meter. Else increase by one.
            if res:
                logging.info(self.current_state)
                self.stale_reset()
            else:
                self.stale_increase()
        
            i += 1
        if self.is_stale():
            logging.warning("UNSOLVABLE")
            logging.info(self.current_state)
            raise UnsolvableException("Solution became stale, cant solve.")
        return i
        
        
    def solve_step(self, column:int=None, row:int=None) -> bool:
        """Solves the given column or row (only one).

        Args:
            column (int, optional): Column number. Must be None if row is given. Defaults to None.
            row (int, optional): Row number. Must be None if column is given. Defaults to None.

        Returns:
            bool: Whether the given row or column was updated with a different solution.
        """
        current_bar, current_contraints = SU.get_bar_and_constraints(self.current_state, column, row)
        
        logging.debug(f"{current_bar}")
        logging.debug(f"Constraints: {current_contraints}")
        
        new_bar = SU.solve_single_bar(current_bar, current_contraints, bar_length=len(current_bar))
        logging.debug(new_bar)

        return self.update_bar(current_bar=current_bar, new_bar=new_bar,
                               column=column, row=row)

    def update_bar(self, current_bar:list[State], new_bar:list[State], column:int=None, row:int=None) -> bool:
        """Updates given bar with the new bar given if different to current bar.

        Args:
            current_bar (list[State]): Current bar values.
            new_bar (list[State]): New bar values.
            column (int, optional): Column number. Exclusive with row. Defaults to None.
            row (int, optional): Row number. Exclusive with column. Defaults to None.

        Returns:
            bool: Whether the bar was updated or not.
        """
        # If nothing was deduced, return False, else update state and return True
        if array_equal(current_bar, new_bar):
            return False
        else:
            if column is not None:
                self.current_state.field_arr[column,:] = new_bar
            elif row is not None:
                self.current_state.field_arr[:,row] = new_bar
            return True
            
