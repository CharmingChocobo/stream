"""
Robust change point detector for identifying persistent heart rate anomalies.

This module implements a `StreamingChangePointDetector` that establishes a fixed
baseline during an initial warmup period and compares subsequent heart rate values
against it. Unlike rolling-window approaches, it maintains a stable reference to
detect sustained deviations (anomalies) rather than transient noise.

Key behaviors:
- **Warmup Phase**: Collects a specified number of beats to calculate mean and
  standard deviation.
- **Anomaly Detection**: Flags a change point only after a configurable streak of
  consecutive outliers (values exceeding a Z-score threshold).
- **Recovery**: Clears the alert state after a sustained return to normal values.
- **Optional Baseline Adaptation**: Can slowly adjust the baseline mean over time
  to accommodate long-term trends while still detecting sudden shifts.

Author: F.Feenstra
"""

from collections import deque
import numpy as np
from streamsim.src.core.interfaces import StreamingChangePointDetector


class HeartRateAnomalyDetector(StreamingChangePointDetector):
    """
    Detects heart rate deviations against a FIXED baseline established during warmup.
    
    Unlike rolling window detectors, this maintains the original baseline and only
    updates it slowly (or not at all), making it sensitive to sudden changes that
    persist over time.
    """
    
    def __init__(
        self, 
        threshold_std: float = 3.0,      # How many std devs from baseline
        warmup_beats: int = 15,          # Beats to establish baseline
        confirmation_count: int = 3,     # Consecutive outliers to confirm
        recovery_count: int = 5,         # Consecutive normal values to clear alert
        baseline_adaptation: float = 0.0 # How fast baseline adapts (0 = fixed, 0.1 = slow)
    ):
        self.threshold_std = threshold_std
        self.warmup_beats = warmup_beats
        self.confirmation_count = confirmation_count
        self.recovery_count = recovery_count
        self.baseline_adaptation = baseline_adaptation
        
        # Warmup buffer
        self._warmup_buffer = deque(maxlen=warmup_beats)
        
        # Fixed baseline (established after warmup)
        self._baseline_mean = None
        self._baseline_std = None
        
        # State tracking
        self._beat_count = 0
        self._outlier_streak = 0
        self._normal_streak = 0
        self._drift_detected = False

    def update(self, feature_value: float) -> bool:
        """
        Update detector with new heart rate value.
        
        Args:
            feature_value (float): Current heart rate in BPM.
        
        Returns:
            bool: True if a significant deviation is confirmed.
        """
        if feature_value is None:
            return False

        self._beat_count += 1
        
        # Phase 1: Warmup - collect baseline data
        if self._beat_count <= self.warmup_beats:
            self._warmup_buffer.append(feature_value)
            return False
        
        # Phase 2: Establish baseline after warmup completes
        if self._baseline_mean is None:
            arr = np.array(self._warmup_buffer)
            self._baseline_mean = arr.mean()
            self._baseline_std = max(arr.std(), 5.0)  # Floor at 5 BPM std
            print(f"[Detector] Baseline established: {self._baseline_mean:.1f} ± {self._baseline_std:.1f} BPM")
            return False
        
        # Phase 3: Compare against fixed baseline
        deviation = abs(feature_value - self._baseline_mean)
        z_score = deviation / self._baseline_std
        
        is_outlier = z_score > self.threshold_std
        
        if is_outlier:
            self._outlier_streak += 1
            self._normal_streak = 0
            
            # Confirm anomaly after consecutive outliers
            if self._outlier_streak >= self.confirmation_count:
                if not self._drift_detected:
                    print(f"[Detector] ANOMALY DETECTED at beat {self._beat_count}: HR={feature_value:.1f}, baseline={self._baseline_mean:.1f}")
                self._drift_detected = True
                return True
        else:
            self._normal_streak += 1
            
            # Clear alert after sustained return to normal
            if self._normal_streak >= self.recovery_count:
                if self._drift_detected:
                    print(f"[Detector] Anomaly CLEARED at beat {self._beat_count}")
                self._drift_detected = False
                self._outlier_streak = 0
        
        # Optional: Slowly adapt baseline (for long-term drift accommodation)
        if self.baseline_adaptation > 0 and not self._drift_detected:
            self._baseline_mean = (
                (1 - self.baseline_adaptation) * self._baseline_mean +
                self.baseline_adaptation * feature_value
            )
        
        return self._drift_detected

    @property
    def drift_detected(self) -> bool:
        """Check if a change point was recently detected."""
        return self._drift_detected

    def reset(self) -> None:
        """Reset internal state."""
        self._warmup_buffer.clear()
        self._baseline_mean = None
        self._baseline_std = None
        self._beat_count = 0
        self._outlier_streak = 0
        self._normal_streak = 0
        self._drift_detected = False