
class UnsolvableException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        
class SolverLogicException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)