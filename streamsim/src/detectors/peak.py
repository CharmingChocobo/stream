from streamsim.src.core.interfaces import StreamingChangePointDetector

class PeakDetector(StreamingChangePointDetector):
    """Flags local maxima as change points."""
    
    def __init__(self):
        self._last_value = None
        self._last_timestamp = None
        self._was_increasing = False  # Track direction
        self._drift_detected = False
    
    def update(self, feature_value: float, timestamp: float = None) -> bool:
        if feature_value is None:
            return False
        
        if self._last_value is None:
            self._last_value = feature_value
            self._last_timestamp = timestamp
            return False
        
        # Track direction (increasing or decreasing)
        is_increasing = feature_value > self._last_value
        
        # Peak detected when going from increasing to decreasing
        is_peak = self._was_increasing and not is_increasing
        
        if is_peak:
            self._drift_detected = True
            self._was_increasing = False
            self._last_value = feature_value
            self._last_timestamp = timestamp
            return True
        else:
            self._drift_detected = False
            self._was_increasing = is_increasing
            self._last_value = feature_value
            return False
    
    @property
    def drift_detected(self) -> bool:
        return self._drift_detected
    
    def reset(self) -> None:
        self._last_value = None
        self._last_timestamp = None
        self._was_increasing = False
        self._drift_detected = False