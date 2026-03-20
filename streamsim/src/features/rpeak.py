"""R-Peak detection for ECG signals."""

import numpy as np
from collections import deque
from typing import Optional

from streamsim.src.core.interfaces import StreamingFeatureDeriver

class RPeakFeatureDeriver(StreamingFeatureDeriver):
    """
    Feature deriver that detects R-peaks in ECG signals.
    
    Signal Processing Pipeline:
        Raw ECG → Bandpass → Derivative → Square → Moving Average → Threshold
    """
    
    def __init__(
        self,
        fs: float = 360.0,
        min_rr_sec: float = 0.2,
        threshold_factor: float = 0.7
    ):
        self.fs = fs
        self.min_rr_sec = min_rr_sec
        self.threshold_factor = threshold_factor
        self.window_samples = int(0.08 * fs)
        
        # Signal processing buffers
        self._buffer_raw = deque(maxlen=self.window_samples * 3)
        self._buffer_filtered = deque(maxlen=self.window_samples * 3)
        self._buffer_derivative = deque(maxlen=self.window_samples * 3)
        self._buffer_squared = deque(maxlen=self.window_samples * 3)
        self._buffer_integrated = deque(maxlen=self.window_samples * 3)
        
        # Adaptive threshold state
        self._signal_level = 0.0
        self._noise_level = 0.0
        self._threshold = 0.0
        
        # Peak detection state
        self._sample_count = 0
        self._last_peak_sample = -int(fs * min_rr_sec)
        
        # Output
        self._peak_timestamp: Optional[float] = None
        self._current_timestamp = 0.0
    
    def add_sample(self, sample: float, timestamp: float = None) -> None:
        self._sample_count += 1
        self._current_timestamp = timestamp if timestamp is not None else self._sample_count / self.fs
        self._peak_timestamp = None
        
        # Pipeline
        self._buffer_raw.append(sample)
        
        filtered = self._bandpass_filter(sample)
        self._buffer_filtered.append(filtered)
        
        derivative = self._compute_derivative(filtered)
        self._buffer_derivative.append(derivative)
        
        squared = derivative ** 2
        self._buffer_squared.append(squared)
        
        integrated = self._moving_average(squared)
        self._buffer_integrated.append(integrated)
        
        self._update_threshold(integrated)
        
        if self._detect_peak(integrated):
            self._peak_timestamp = self._current_timestamp
    
    def get_feature(self) -> Optional[float]:
        return self._peak_timestamp
    
    def reset(self) -> None:
        self._buffer_raw.clear()
        self._buffer_filtered.clear()
        self._buffer_derivative.clear()
        self._buffer_squared.clear()
        self._buffer_integrated.clear()
        
        self._signal_level = 0.0
        self._noise_level = 0.0
        self._threshold = 0.0
        self._sample_count = 0
        self._last_peak_sample = -int(self.fs * self.min_rr_sec)
        self._peak_timestamp = None
    
    def _bandpass_filter(self, sample: float) -> float:
        if len(self._buffer_raw) < self.window_samples:
            return sample
        
        window = list(self._buffer_raw)[-self.window_samples:]
        baseline = sum(window) / len(window)
        high_passed = sample - baseline
        
        if len(self._buffer_filtered) >= 3:
            smoothed = 0.6 * high_passed + 0.3 * self._buffer_filtered[-1] + 0.1 * self._buffer_filtered[-2]
        else:
            smoothed = high_passed
        
        return smoothed
    
    def _compute_derivative(self, sample: float) -> float:
        if len(self._buffer_filtered) < 5:
            return 0.0
        
        buf = list(self._buffer_filtered)[-5:]
        return (-buf[0] - 2*buf[1] + 2*buf[3] + buf[4]) / 8.0
    
    def _moving_average(self, sample: float) -> float:
        if len(self._buffer_squared) < self.window_samples:
            return sample
        return sum(list(self._buffer_squared)[-self.window_samples:]) / self.window_samples
    
    def _update_threshold(self, integrated: float) -> None:
        if self._sample_count < self.window_samples * 2:
            self._signal_level = max(self._signal_level, integrated * 0.5)
            self._noise_level = integrated * 0.1
            self._threshold = self._signal_level * self.threshold_factor
            return
        
        if integrated > self._threshold:
            self._signal_level = 0.875 * self._signal_level + 0.125 * integrated
        else:
            self._noise_level = 0.875 * self._noise_level + 0.125 * integrated
        
        self._threshold = self._noise_level + self.threshold_factor * (self._signal_level - self._noise_level)
        self._threshold = max(self._threshold, self._signal_level * 0.1)
    
    def _detect_peak(self, integrated: float) -> bool:
        samples_since_last = self._sample_count - self._last_peak_sample
        refractory_samples = int(self.fs * self.min_rr_sec)
        
        if integrated <= self._threshold:
            return False
        if samples_since_last < refractory_samples:
            return False
        if len(self._buffer_integrated) < 3:
            return False
        
        recent = list(self._buffer_integrated)[-3:]
        if integrated >= recent[-2] and (len(recent) < 3 or integrated >= recent[-3]):
            self._last_peak_sample = self._sample_count
            return True
        
        return False