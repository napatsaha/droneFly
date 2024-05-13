"""
Based on a standard deviation identification of a bump or anomaly in running data.

If new datum is above certain threshold of STD, then signal is considered a bump.

New positive signal can be included in calculation of running sample via:
- Influence weight
- Baseline percentile

See:
https://stackoverflow.com/questions/22583391/peak-signal-detection-in-realtime-timeseries-data/22640362#22640362
"""
import logging
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from collections import deque


class BaseDetector(ABC):
    def add(self, value) -> bool:
        pass

    @abstractmethod
    def __call__(self, value) -> bool:
        pass


class ZScorePeakDetection(BaseDetector):
    """
    Class docstring
    """
    def __init__(self, window: int = 5, threshold: float = 3, influence: float = 1.0):
        """
        Real time signal anomaly detector based on Z-score and standard deviation.

        A new value entry is compared to the current running sample; if is *threshold* unit of
        standard deviation away, then it is considered an anomaly.

        Running sample is calculated based on the previous *window* entries observed.

        New value which is considered an anomaly can be included in the sample based on the
        *influence* factor, weighted against the last recent entry in the sample. An influence
        of 1.0 adds the new value unchanged, while an influence of 0.0 uses the previous value
        instead.

        """
        self.window = window
        self.threshold = threshold
        self.influence = influence
        self.sample = deque(maxlen=self.window)
        self.std = None
        self.mean = None

        self.logger = logging.getLogger("ZScorer")
        
    def add(self, new_value) -> bool:
        """
        Add new value to filter, and return whether the value is an anomaly
        """
        if len(self.sample) >= self.window:
            z = np.abs((new_value - self.mean) / self.std)
            is_signal = z >= self.threshold
            if is_signal:
                self.logger.debug("Current Mean: %f -- Std: %f" % (self.mean, self.std))
                self.logger.debug("New Value: {} -- Z Score {}".format(new_value, z))
        else:
            is_signal = False

        self._append(new_value, is_signal)
        self._recalculate()

        return is_signal

    def __call__(self, new_value):
        return self.add(new_value)

    def _append(self, new_value, signal: bool):
        """
        Decide how to append new value if it is a signal
        """
        if signal:
            # old_value = new_value
            new_value = self.influence * new_value + \
                        (1 - self.influence) * self.sample[-1]
            self.logger.debug("Adjusted value %f" % new_value)
        self.sample.append(new_value)

    def _recalculate(self):
        """
        Recalculate mean and standard deviation
        """
        self.mean = np.mean(self.sample)
        self.std = np.std(self.sample)
        

if __name__ == "__main__":

    filename = "../data/Curved_24-04-22_14-47-46.csv"
    data = pd.read_csv(filename)
    metric = "agz"

    detector = ZScorePeakDetection(window=10, threshold=3, influence=0)

    for row in data.itertuples():
        newvalue = getattr(row, metric)

        bump = detector.add(newvalue)

        if bump:
            print(getattr(row, "Index"), getattr(row, "time_elapsed"), newvalue, sep="\t")

