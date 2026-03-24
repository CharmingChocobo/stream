"""
Simple Pass-Through Change Point Detector for Peak Features

This module provides a minimalistic change point detector designed specifically
for scenarios where the presence of a valid feature value (such as a detected peak)
directly indicates a change point or event of interest. It implements the
`StreamingChangePointDetector` interface to integrate with the streaming simulator. 
If a valid feature value is provided (i.e., not None), it flags this as a 
change point by returning True and setting the `drift_detected` property to True. 
This allows downstream components to react to detected peaks without additional 
logic for interpreting feature values.  

Important Dependencies:
    - streamsim.src.core.interfaces.StreamingChangePointDetector: Base interface

Author: F.Feenstra
"""

from typing import Optional
from streamsim.src.core.interfaces import StreamingChangePointDetector

class PeakPassThrough(StreamingChangePointDetector):
    """ 
    Simple pass-through detector for peak detection.
    Returns True (and sets drift_detected=True) whenever a valid feature (peak) is provided.
    """
    
    def __init__(self):
        self._drift_detected = False

    def update(self, feature_value: Optional[float]) -> bool:
        """
        Returns True if feature_value is not None (indicating a peak).
        Crucially, this also updates the drift_detected property.
        """
        is_peak = feature_value is not None
        self._drift_detected = is_peak  
        return is_peak
    
    @property
    def drift_detected(self) -> bool:
        return self._drift_detected
    
    def reset(self) -> None:
        self._drift_detected = False