import time
from contextlib import ContextDecorator
from typing import Optional


class time_it(ContextDecorator):
    """
    Context manager that can be used to time the containing code block.

    :param label: Some text label.
    :param silent: If False, print the time needed.
    """

    def __init__(self, label=None, silent=False):
        self._label = label
        self._t0 = None
        self._delta = -1.
        self._silent = silent

    @property
    def label(self) -> Optional[str]:
        """The label."""
        return self._label

    @property
    def delta(self) -> float:
        return self._delta

    def __enter__(self):
        self._t0 = time.clock()
        return self

    def __exit__(self, *exc):
        self._delta = time.clock() - self._t0
        if not self._silent:
            if self._label:
                print(f'{self._label}: took {self._delta} seconds')
            else:
                print(f'took {self._delta} seconds')
        return False
