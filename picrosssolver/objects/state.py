from enum import Enum, auto

class State(Enum):
    # We know it must be empty
    EMPTY = auto()    
    # We dont know what it will be
    INDET = auto()
    # We know it must be filled in
    FILL = auto()
    
    def __repr__(self) -> str:
        if self == State.EMPTY:
            return "x"
        elif self == State.INDET:
            return "□"
        elif self == State.FILL:
            return "■"
        else:
            raise Exception("Undefined State")