from copy import deepcopy

from numpy import full as np_full, transpose

from picrosssolver.objects.state import State

class Field:
    
    def __init__(self, column_values, row_values):
        self.x = len(column_values)
        self.y = len(row_values)
        self.column_values = column_values
        self.row_values = row_values
        self.field_arr = np_full(shape=(self.x,self.y), 
                                 fill_value=State.INDET)
    
    @classmethod
    def copy_field(cls, copy_from):
        new_field = Field(copy_from.column_values,
                          row_values=copy_from.row_values)
        new_field.field_arr = deepcopy(copy_from.field_arr)
        
    def is_solved(self):
        return State.INDET not in self.field_arr
    
    def __repr__(self) -> str:
        str_res = f"Columns: {self.column_values}"
        str_res += f"\nRows:    {self.row_values}"
        str_res += "\n"
        str_res += str(transpose(deepcopy(self.field_arr)))
        
        return str_res