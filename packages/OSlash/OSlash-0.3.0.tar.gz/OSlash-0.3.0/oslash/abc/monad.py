r"""The Monad abstract base class.

All instances of the Monad typeclass should obey the three monad laws:

    1) Left identity: return a >>= f = f a
    2) Right identity: m >>= return = m
    3) Associativity: (m >>= f) >>= g = m >>= (\x -> f x >>= g)
"""

from abc import ABCMeta, abstractmethod

from typing import Callable, Any


class Monad(metaclass=ABCMeta):

    """Monad abstract base class."""

    @abstractmethod
    def bind(self, func: Callable[[Any], 'Monad']) -> 'Monad':
        """Monad bind method.

        Haskell: (>>=) :: m a -> (a -> m b) -> m b

        This is the mother of all methods. It's hard to describe what it
        does, because it can be used for anything:

        * Transformation, for projecting Monadic values and functions.
        * Composition, for composing and combining monadic values and
          functions.
        * Sequencing, of Monadic functions.
        * Flattening, of nested Monadic values.

        Returns a new Monad.
        """
        return NotImplemented

    @classmethod
    def unit(cls, *args) -> 'Monad':
        """return :: a -> m a .

        Inject a value into the monadic type. Since return is a reserved
        word in Python, we align with Scala and use the name unit
        instead.
        """
        return cls(*args)

    def __or__(self, func: Callable[[Any], 'Monad']) -> 'Monad':
        """Use >> as operator for bind.

        Provide the | operator instead of the Haskell >>= operator
        """
        return self.bind(func)
