"""
Local Maxima Peak Detector for Streaming Signals

This module provides a streaming feature deriver that detects local maxima
(peaks) in time-series signals. It implements the `StreamingFeatureDeriver`
interface to identify peaks where the current sample is strictly greater than
its neighboring samples.

It uses a configurable sliding window to compare each sample against
its left and right neighbors, with an optional threshold to filter out minor
fluctuations. This makes it suitable for detecting significant peaks in various
signal types (sinusoidal, triangular, ECG, etc.).

Features:
    - Configurable window size for neighbor comparison
    - Optional threshold filtering relative to local mean
    - Returns peak timestamps for downstream processing
    - Memory-efficient buffer using deque
    - Explicit reset capability for state management

Important Dependencies:
    - streamsim.src.core.interfaces.StreamingFeatureDeriver: Base interface
    - collections.deque: Efficient circular buffer

Author: F.Feenstra

"""

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
        self._buffer = deque(maxlen=window_size + 1) # Buffer to hold recent (value, timestamp) tuples
        self._peak_timestamp: Optional[float] = None

    
    def add_sample(self, sample: float, timestamp: float = None) -> None:
        """
        Add a new sample and evaluate for peak detection.
        
        Stores the sample with its timestamp in the internal buffer, then
        checks if the previous sample (now at center position) qualifies as
        a local maximum based on neighbor comparison and threshold criteria.
        
        Args:
            sample (float): The raw signal sample value.
            timestamp (float, optional): Timestamp of the sample in seconds.
                                         If None, uses current system time.
                                         Default: None.
        
        Note:
            Minimum Requirement: You need at least window_size + 1 
            samples before any peak can be detected. Early samples are skipped.
            To confirm a peak, you need to see both sides of it:
            - Ascending slope: The sample before must be lower
            - Descending slope: The sample after must be lower
            The Catch: When a new sample arrives, you can't tell if it's a peak 
            yet—you need the next sample to confirm the signal drops. 
            So the code checks the previous sample (index -2) once 
            the current sample (index -1) arrives.

        """
 
        ts = timestamp if timestamp is not None else time.time()
        self._buffer.append((sample, ts))
        
        self._peak_timestamp = None
        
        if len(self._buffer) < self.window_size + 1:
            return

        right_val, _ = self._buffer[-1]
        center_val, center_ts = self._buffer[-2]
        left_val, _ = self._buffer[-3]
        
        if center_val > left_val and center_val > right_val:
            recent_vals = [v for v, _ in list(self._buffer)[-self.window_size:]]
            recent_mean = np.mean(recent_vals)
            
            if center_val - recent_mean > self.threshold:
                self._peak_timestamp = center_ts

    
    def get_feature(self) -> Optional[float]:
        """Returns the peak timestamp if a peak was detected, None otherwise."""
        return self._peak_timestamp

    def reset(self) -> None:
        self._buffer.clear()
        self._peak_timestamp = None
