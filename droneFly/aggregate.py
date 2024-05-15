
import numpy as np
from collections import deque


class BaseAggregator:
    def __init__(self, window):
        self.window = window
        self.memory = deque(maxlen=window)

    def add(self, value):
        self.memory.append(value)

    def extract(self):
        output = self.aggregate()
        return output

    def aggregate(self):
        return self.memory[-1]

    def __call__(self, entry):
        self.add(entry)
        return self.extract()


class DiffAggregator(BaseAggregator):
    def __init__(self, window):
        super().__init__(window=window)

    def aggregate(self):
        diffs = np.diff(self.memory)
        abs_sum = np.sum(np.abs(diffs))
        return abs_sum


class MultiDiffAggregator(BaseAggregator):
    """
    Utilise the sum of absolute differences for one or more metrics.
    """
    def __init__(self, window, metrics, separate: bool = False):
        """

        :param window:
        :type window:
        :param metrics:
        :type metrics:
        :param separate: whether to sum across metrics when aggregating
            if False (default), return a single value, summed across metrics
            if True, returns a tuple
        :type separate: bool
        """
        super().__init__(window)
        self.metrics = metrics
        self.separate = separate

    def add(self, value):
        if isinstance(value, dict):
            # Dictionary input
            value = [*map(value.get, self.metrics)]
        elif isinstance(value, tuple) and hasattr(value, "_fields"):
            # Named tuple case
            value = [*map(lambda a: getattr(value, a), self.metrics)]

        assert len(value) == len(self.metrics)

        self.memory.append(value)

    def aggregate(self):
        arr = np.array(self.memory)  # -> 2D array
        darr = np.sum(np.abs(np.diff(arr, axis=0)), axis=0)  # sum of abs diff
        if not self.separate:
            return darr.sum()  # sum across metrics
        else:
            return darr


class MultiAggregator(BaseAggregator):

    def __init__(self, window, metrics):
        super().__init__(window=window)
        self.metrics = metrics

    def add(self, row):
        values = [*map(lambda a: getattr(row, a), self.metrics)]
        super().add(values)


if __name__ == "__main__":
    pass