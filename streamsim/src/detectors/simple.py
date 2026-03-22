"""Very simple change point detector that flags points that deviate significantly from the recent mean."""

__author__ = "F.Feenstra"

from collections import deque
import numpy as np
from streamsim.src.core.interfaces import StreamingChangePointDetector


class SimpleDetector(StreamingChangePointDetector):
    def __init__(self, threshold=2.0):
        self.threshold = threshold
        self.history = deque(maxlen=50)

    def update(self, x):
        self.history.append(x)

        if len(self.history) > 20:
            arr = np.array(self.history)
            mean = arr[:-1].mean()
            std = arr[:-1].std()

            if std > 0 and abs(x - mean) > self.threshold * std:
                return True
        return False

