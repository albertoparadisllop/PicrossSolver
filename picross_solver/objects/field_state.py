from copy import deepcopy

from numpy import full as np_full
from numpy import transpose

from picross_solver.objects.state import State


class Field:
    """Represents a picross field with its constraints and grid.
    """
    def __init__(self, column_values:list, row_values:list):
        """Create Picross Field from given column and row constraints

        Args:
            column_values (list): Column constraints
            row_values (list): Row constraints
        """
        self.x = len(column_values)
        self.y = len(row_values)
        self.column_values = column_values
        self.row_values = row_values
        self.field_arr = np_full(shape=(self.x,self.y), 
                                 fill_value=State.INDET)
    
    @classmethod
    def copy_field(cls, copy_from:'Field') -> 'Field':
        """Performs a deepcopy on the given field.

        Args:
            copy_from (Field): Field to copy data from.

        Returns:
            Field: Copied field.
        """
        new_field = cls(copy_from.column_values,
                        row_values=copy_from.row_values)
        new_field.field_arr = deepcopy(copy_from.field_arr)
        return new_field
        
    def is_solved(self) -> bool:
        """Whether the field is "solved" or not. A field is solved when all cells are either FILL or EMPTY.

        Returns:
            bool: True if the field is solved, false if not.
        """
        return State.INDET not in self.field_arr
    
    def __repr__(self) -> str:
        str_res = f"Columns: {self.column_values}"
        str_res += f"\nRows:    {self.row_values}"
        str_res += "\n"
        str_res += str(transpose(deepcopy(self.field_arr)))
        
        return str_res