# Picross/Nonogram Solver

Little for-fun project. Expect spaghetti code.

## Instructions:

* import `picrosssolver.objects.field_state.Field` and `picrossolver.solver.Solver`
* Create a `Field` object, passing it the column and row constraints from your puzzle.
* Create a `Solver` object, passing it the `Field` you just created.
* run the Solver instance's `solve` method.
* Print out the Solver instance's `current_state` attribute.

I could make it easier to use with a single command, but eh, this works.

If the nonogram is not solvable by looking at individual rows/columns,w it will not work.

## Examples

Both of the following examples are available in the `main.py` file.

An example for Pictopix's 1st level:

```python
from picrosssolver.solver import Solver
from picrosssolver.objects.field_state import Field

column_constraints = [[0], [1,1], [1,1], [5], [0]]
row_constraints = [[3], [1], [3], [1], [1]]

newState = Field(column_values=column_constraints,
                row_values=row_constraints)
mySolver = Solver(newState)

mySolver.solve()
print(solver.current_state)
```


And a bigger example, Pictopix's 83rd level (page 6, 8th, 15x15 "Flora" theme):

```python
from picrosssolver.solver import Solver
from picrosssolver.objects.field_state import Field

column_constraints = [[2], [2,3], [4,2], [7,2], [4,5], [4,4,2], [4,7], [2,6], [2,5], [4,2,2], [4,8], [4,2,4], [6,3], [4], [2]]
row_constraints = [[0],[2,2],[4,4],[4,4],[5,5],[2,4,3],[5,1,5],[6,5],[6,2],[5,2],[2,3,3],[2,4,3],[2,8],[2,5],[2]]

newState = Field(column_values=column_constraints,
                row_values=row_constraints)
mySolver = Solver(newState)

mySolver.solve()
print(solver.current_state)
```
