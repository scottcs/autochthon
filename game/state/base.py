"""Game state."""
import collections
import typing


class BaseState:
    """Game state base class."""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        pass

    def on_enter(self) -> None:
        """Called when this state is entered."""
        pass

    def on_exit(self) -> None:
        """Called when this state is discarded or popped off the stack."""
        pass

    def on_pause(self) -> None:
        """Called when another state is pushed on top of this one."""
        pass

    def on_resume(self) -> None:
        """Called when this state becomes top-most on the stack after having been pushed down."""
        pass

    def handle_input(self) -> None:
        """Input handler."""
        pass

    def update(self) -> None:
        """Update iteration."""
        pass


class _Stack:
    """Game state stack."""

    def __init__(self) -> None:
        self._stack: collections.deque = collections.deque()

    @property
    def size(self) -> int:
        """Get the number of items on the stack."""
        return len(self._stack)

    @property
    def current(self) -> BaseState:
        """Get the current state."""
        return self._stack[-1]

    def push(self, state: BaseState) -> None:
        """Push a new state onto the stack."""
        if self.size > 0:
            self.current.on_pause()
        self._stack.append(state)
        self.current.on_enter()

    def pop(self) -> BaseState:
        """Remove and return the top-most state."""
        old_state = self._stack.pop()
        old_state.on_exit()
        if self.size > 0:
            self.current.on_resume()
        return old_state


Stack = _Stack()
