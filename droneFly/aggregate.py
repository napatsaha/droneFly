from typing import NamedTuple, Dict, Union, List

import numpy as np
from collections import deque


class BaseAggregator:
    def __init__(self, window):
        self.window = window
        self.memory = deque(maxlen=window)

    def add(self, value):
        """
        Adds new value to memory
        """
        self.memory.append(value)

    def aggregate(self):
        """
        Extracts aggregated values from memory.
        (Expect to be overridden in child classes.)
        """
        return self.memory[-1]

    # def extract(self):
    #     output = self.aggregate()
    #     return output

    def __call__(self, entry):
        self.add(entry)
        return self.aggregate()


class DiffAggregator(BaseAggregator):
    def __init__(self, window):
        super().__init__(window=window)

    def aggregate(self):
        diffs = np.diff(self.memory)
        abs_sum = np.sum(np.abs(diffs))
        return abs_sum


def filter_state(value: Union[Dict, NamedTuple], metrics: List[str]):
    """
    Pull out selected keys from input state. Supports both dictionary and named tuples inputs.
    """
    if isinstance(value, dict):
        # Dictionary input
        value = [*map(value.get, metrics)]
    elif isinstance(value, tuple) and hasattr(value, "_fields"):
        # Named tuple case
        value = [*map(lambda a: getattr(value, a), metrics)]
    assert len(value) == len(metrics)
    return value


def diff_filter(arr: np.array):
    """
    Sum of absolute differences in an array, along the first axis, i.e. column-wise.
    Returns a scalar for 1D array, or an array (D-1) for >2D arrays
    """
    deltas = np.sum(np.abs(np.diff(arr, axis=0)), axis=0)
    return deltas


class MultiDiffAggregator(BaseAggregator):
    """
    Utilise the sum of absolute differences for one or more metrics.

    separate: whether to sum across metrics when aggregating
            if False (default), return a single value, summed across metrics
            if True, returns a tuple
    """
    def __init__(self, window, metrics, separate: bool = False):
        super().__init__(window)
        self.metrics = metrics
        self.separate = separate

    def add(self, value):
        value = filter_state(value, self.metrics)

        self.memory.append(value)

    def aggregate(self):
        """
        Calculates and returns sum of absolute derivatives from memory.
        (If separate=True, calculates for each metric independently.)
        """
        arr = np.array(self.memory)  # -> 2D array
        deltas = diff_filter(arr)  # sum of abs diff
        if not self.separate:
            return deltas.sum()  # sum across metrics
        else:
            return deltas


class NormAggregator(BaseAggregator):
    """
    Meant to represent composite magnitude of a particular measure (velocity, acceleration)
    across different axes (x, y, z), by using the L2 Norm.
    """
    def __init__(self, window, metrics):
        super().__init__(window)
        self.metrics = metrics

    def add(self, value):
        value = filter_state(value, self.metrics)
        self.memory.append(value)

    def aggregate(self):
        """
        Calculates the L2 Norm across metrics then returns the
        sum of absolute derivatives of those norms.
        """
        data = self.memory
        arr = np.array(data)
        norm = np.linalg.norm(arr, axis=1)
        if len(self.memory) > 1:
            return diff_filter(norm)
        else:
            return norm


class MultiAggregator(BaseAggregator):

    def __init__(self, window, metrics):
        super().__init__(window=window)
        self.metrics = metrics

    def add(self, row):
        values = [*map(lambda a: getattr(row, a), self.metrics)]
        super().add(values)


if __name__ == "__main__":
    pass
