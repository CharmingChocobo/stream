"""
Simple Feature Deriver for Streaming Data

This module provides a minimal feature derivation class that implements the
`StreamingFeatureDeriver` interface. It serves as a passthrough component,
treating raw samples directly as feature values without transformation.

This class is useful for:
    - Testing and debugging streaming pipelines
    - Scenarios where raw signal values are the desired features
    - As a template for implementing more complex feature derivers

Dependencies:
    - streamsim.src.core.interfaces.StreamingFeatureDeriver: Base interface

Author: F.Feenstra

"""
from streamsim.src.core.interfaces import StreamingFeatureDeriver
import numpy as np
from collections import deque
from typing import Optional, Any, Tuple, List


class SimpleFeature(StreamingFeatureDeriver):
    def __init__(self):
        self.value = None

    def add_sample(self, sample, timestamp=None):
        self.value = sample

    def get_feature(self):
        return self.value
    


class SmoothedSignalDeriver(StreamingFeatureDeriver):
    def __init__(self, window_size: int = 20):
        """
        Args:
            window_size: Number of samples to include in the moving average.
                         Higher values = smoother line but more lag.
        """
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)
        self._current_smoothed = None

    def add_sample(self, sample: float, timestamp: float = None) -> None:
        self.buffer.append(sample)
        
        # Calculate smoothed value if we have enough data
        if len(self.buffer) >= self.window_size:
            self._current_smoothed = np.mean(self.buffer)
        elif len(self.buffer) > 0:
            # Optional: Use partial average for initial samples
            self._current_smoothed = np.mean(self.buffer)
        else:
            self._current_smoothed = None

    def get_feature(self) -> Optional[float]:
        """Returns the smoothed value (the 'model')."""
        return self._current_smoothed

    def get_raw_sample(self) -> Optional[float]:
        """Helper to get the very last raw sample if needed elsewhere."""
        return self.buffer[-1] if self.buffer else None

    def reset(self) -> None:
        self.buffer.clear()
        self._current_smoothed = None