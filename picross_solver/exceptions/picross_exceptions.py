
class UnsolvableException(Exception):
    """Indicates field is unsolvable.
+   """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        
class SolverLogicException(Exception):
    """Indicates there's been some error using the solver, or there's a bug somewhere (whoops).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)