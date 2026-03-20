#passthrough.py
from typing import Optional
from streamsim.src.core.interfaces import StreamingChangePointDetector

class PeakPassThrough(StreamingChangePointDetector):
    """
    Simple pass-through that signals when a peak is detected.
    Used when the feature deriver already does the detection logic.
    """
    
    def update(self, feature_value: Optional[float]) -> bool:
        """Returns True if feature_value is not None (indicating a peak timestamp)."""
        return feature_value is not None
    
    @property
    def drift_detected(self) -> bool:
        return False


