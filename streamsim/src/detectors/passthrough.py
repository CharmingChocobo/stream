"""Simple pass-through change point detector for peak features."""

__author__ = "F.Feenstra"

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
        self._drift_detected = is_peak  # <--- THIS IS THE KEY LINE
        return is_peak
    
    @property
    def drift_detected(self) -> bool:
        return self._drift_detected
    
    def reset(self) -> None:
        self._drift_detected = False