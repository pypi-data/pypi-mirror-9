from .functor import Functor
from .monad import Monad
from .monoid import Monoid


class State(Monad, Functor):

    """The state monad."""

    def __init__(self, value: "Any", log: Monoid):
        """Initialize a new state.
		pass
