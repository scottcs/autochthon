"""Game state."""
import collections

import game.events
import game.types
import game.world


class EmptyStateQueueException(Exception):
    """There is no current state but state was accessed."""


class BaseState:
    """Game state base class."""

    def on_enter(self) -> None:
        """Called when this state is entered."""
        game.events.Input.handle(self._on_input)
        self._on_enter()

    def _on_enter(self) -> None:
        """Overwrite in child class."""
        pass

    def on_exit(self) -> None:
        """Called when this state is discarded or popped off the stack."""
        game.events.Input.unhandle(self._on_input)
        self._on_exit()

    def _on_exit(self) -> None:
        """Overwrite in child class."""
        pass

    def on_pause(self) -> None:
        """Called when another state is pushed on top of this one."""
        game.events.Input.unhandle(self._on_input)
        self._on_pause()

    def _on_pause(self) -> None:
        """Overwrite in child class."""
        pass

    def on_resume(self) -> None:
        """Called when this state becomes top-most on the stack after having been pushed down."""
        game.events.Input.handle(self._on_input)
        self._on_resume()

    def _on_resume(self) -> None:
        """Overwrite in child class."""
        pass

    def _on_input(self, event: game.types.Event):
        """Handle input; overwrite in child class."""
        pass

    def update(self) -> None:
        """Update iteration."""
        self._update()

    def _update(self) -> None:
        """Overwrite in child class."""
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
        try:
            return self._stack[-1]
        except IndexError:
            raise EmptyStateQueueException("Attempt to access top of empty queue.")

    def push(self, state: BaseState) -> None:
        """Push a new state onto the stack."""
        if self.size > 0:
            self.current.on_pause()
        self._stack.append(state)
        self.current.on_enter()

    def pop(self) -> BaseState:
        """Remove and return the top-most state."""
        try:
            old_state = self._stack.pop()
        except IndexError:
            raise EmptyStateQueueException("Attempt to pop from empty queue.")
        old_state.on_exit()
        if self.size > 0:
            self.current.on_resume()
        return old_state

    def pop_to(self, state: BaseState) -> BaseState:
        """Pop all states up to and including the given state."""
        while self.current != state:
            self.pop()
        return self.pop()


Stack = _Stack()
