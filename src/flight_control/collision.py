from collections import deque

import numpy as np
from analysis import aggregate, detector

# AGG_NAMES = {
#     "basic": 'BaseAggregator',
#     "single diff": 'DiffAggregator',
#     "multi": 'MultiAggregator',
#     "multi diff": 'MultiDiffAggregator'
# }


class CollisionDetector:
    def __init__(self,
                 aggregator: aggregate.BaseAggregator,
                 detect: detector.BaseDetector):
        self.aggregator = aggregator
        self.detector = detect

    def __call__(self, new_value):
        agg_value = self.aggregator(new_value)
        has_collided = self.detector(agg_value)
        if has_collided:
            print(agg_value)
        return has_collided


class SingleMetricDiffDetector:
    def __init__(self, metric, threshold):
        self.threshold = threshold
        self.metric = metric
        self.records = deque([], maxlen=2)

    def add(self, row: dict):
        if self.metric not in row:
            raise Exception(f"Metric {self.metric} not in received state.")
        self.records.append(row[self.metric])

    def update(self, state: dict):
        self.add(state)
        if len(self.records) < 2:
            return False

        check = self.check_collision()

        return check

    def check_collision(self):
        dif = np.abs(np.diff(self.records)).item()
        check = dif > self.threshold
        return check
