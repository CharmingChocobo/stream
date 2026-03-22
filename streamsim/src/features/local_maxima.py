__author__ = "F.Feenstra"

from collections import deque
from typing import Optional
import time
from streamsim.src.core.interfaces import StreamingFeatureDeriver
import numpy as np  

class LocalMaximaDeriver(StreamingFeatureDeriver):
    """
    General-purpose peak detector for any signal (Sinus, Sine, Triangle, etc.).
    
    Detects a peak when the current sample is strictly greater than its 
    immediate neighbors (left and right).
    
    Returns:
        - get_feature(): Returns peak timestamp when a peak is detected, None otherwise.
    """
    
    def __init__(self, window_size: int = 3, threshold: float = 0.0):
        """
        Args:
            window_size: Number of samples to look back/forward. 
                         Minimum 3 (left, center, right).
            threshold: Minimum height relative to local mean to be considered a peak.
        """
        if window_size < 3:
            raise ValueError("Window size must be at least 3 to compare neighbors.")
            
        self.window_size = window_size
        self.threshold = threshold
        
        # Buffer to hold recent (value, timestamp) tuples
        self._buffer = deque(maxlen=window_size + 1)
        
        # Output state
        self._peak_timestamp: Optional[float] = None
    
    def add_sample(self, sample: float, timestamp: float = None) -> None:
        ts = timestamp if timestamp is not None else time.time()
        self._buffer.append((sample, ts))
        
        # Reset output for this cycle
        self._peak_timestamp = None
        
        # Need enough data to check neighbors
        if len(self._buffer) < self.window_size + 1:
            return

        buf_list = list(self._buffer)
        
        # We check the sample at index -2 (the one before current) as a potential peak
        # because we need to see the drop-off on the right side (current sample).
        # Indices: -3 (left), -2 (center), -1 (right/current)
        if len(buf_list) >= 3:
            center_idx = -2
            left_idx = -3
            right_idx = -1
            
            center_val, center_ts = buf_list[center_idx]
            left_val, _ = buf_list[left_idx]
            right_val, _ = buf_list[right_idx]
            
            # Check if center is strictly greater than neighbors
            if center_val > left_val and center_val > right_val:
                # Optional: Threshold check (relative to recent mean)
                recent_vals = [v for v, _ in buf_list[-self.window_size:]]
                recent_mean = np.mean(recent_vals)
                
                if center_val - recent_mean > self.threshold:
                    self._peak_timestamp = center_ts

    def get_feature(self) -> Optional[float]:
        """Returns the peak timestamp if a peak was detected, None otherwise."""
        return self._peak_timestamp

    def reset(self) -> None:
        self._buffer.clear()
        self._peak_timestamp = None
