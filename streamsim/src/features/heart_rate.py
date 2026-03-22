"""R-Peak detection for ECG signals with heart rate calculation."""

import numpy as np
from collections import deque
from typing import Optional, Tuple

from streamsim.src.core.interfaces import StreamingFeatureDeriver


class HRFeatureDeriver(StreamingFeatureDeriver):
    """
    Feature deriver that detects R-peaks in ECG signals and calculates heart rate.
    
    Signal Processing Pipeline:
        Raw ECG → Bandpass → Derivative → Square → Moving Average → Threshold
    
    Heart Rate Calculation:
        - Measures RR intervals between consecutive R-peaks
        - Computes instantaneous heart rate: HR = 60 / RR_interval (BPM)
        - Optionally smooths using a moving average of recent intervals
    """
    
    def __init__(
        self,
        fs: float = 360.0,
        min_rr_sec: float = 0.2,
        threshold_factor: float = 0.7,
        rr_window_size: int = 5,
        min_hr: float = 30.0,
        max_hr: float = 220.0
    ):
        """
        Initialize the R-Peak feature deriver.
        
        Args:
            fs (float): Sampling frequency in Hz (default: 360.0).
            min_rr_sec (float): Minimum RR interval in seconds (refractory period).
            threshold_factor (float): Adaptive threshold sensitivity (0.0-1.0).
            rr_window_size (int): Number of RR intervals to average for heart rate.
            min_hr (float): Minimum valid heart rate in BPM.
            max_hr (float): Maximum valid heart rate in BPM.
        """
        self.fs = fs
        self.min_rr_sec = min_rr_sec
        self.threshold_factor = threshold_factor
        self.rr_window_size = rr_window_size
        self.min_hr = min_hr
        self.max_hr = max_hr
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
        
        # Heart rate calculation state
        self._last_peak_timestamp: Optional[float] = None
        self._rr_intervals: deque = deque(maxlen=rr_window_size)
        self._heart_rate: Optional[float] = None
        
        # Output
        self._peak_timestamp: Optional[float] = None
        self._current_timestamp = 0.0
    
    def add_sample(self, sample: float, timestamp: float = None) -> None:
        """
        Process a new ECG sample and detect R-peaks.
        
        Args:
            sample (float): The ECG signal sample value.
            timestamp (float, optional): Timestamp of the sample in seconds.
        """
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
            self._update_heart_rate()
    
    def get_feature(self) -> Optional[float]:
        """ Get the latest heart rate """
        return self.get_heart_rate()
    
    def get_heart_rate(self) -> Optional[float]:
        """
        Get the current heart rate in beats per minute (BPM).
        
        The heart rate is calculated as a moving average of the last N RR intervals,
        where N is determined by rr_window_size.
        
        Returns:
            Optional[float]: Heart rate in BPM, or None if insufficient data.
        """
        return self._heart_rate
    
    def get_rr_interval(self) -> Optional[float]:
        """
        Get the most recent RR interval in seconds.
        
        Returns:
            Optional[float]: Last RR interval in seconds, or None if no interval recorded.
        """
        if len(self._rr_intervals) > 0:
            return self._rr_intervals[-1]
        return None
    
    def get_features(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get both the peak timestamp and heart rate.
        
        Convenience method for retrieving all derived features at once.
        
        Returns:
            Tuple[Optional[float], Optional[float]]: (peak_timestamp, heart_rate)
        """
        return self._peak_timestamp, self._heart_rate
    
    def reset(self) -> None:
        """Reset all internal state and buffers."""
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
        self._last_peak_timestamp = None
        self._rr_intervals.clear()
        self._heart_rate = None
        self._peak_timestamp = None
    
    def _update_heart_rate(self) -> None:
        """Calculate heart rate from the current RR interval."""
        if self._last_peak_timestamp is not None:
            rr_interval = self._current_timestamp - self._last_peak_timestamp
            
            # Validate RR interval (physiological bounds)
            min_rr = 60.0 / self.max_hr  # e.g., 0.27s for max 220 BPM
            max_rr = 60.0 / self.min_hr  # e.g., 2.0s for min 30 BPM
            
            if min_rr <= rr_interval <= max_rr:
                self._rr_intervals.append(rr_interval)
                
                # Calculate smoothed heart rate
                if len(self._rr_intervals) > 0:
                    avg_rr = sum(self._rr_intervals) / len(self._rr_intervals)
                    self._heart_rate = 60.0 / avg_rr
        
        self._last_peak_timestamp = self._current_timestamp
    
    def _bandpass_filter(self, sample: float) -> float:
        """Apply bandpass filtering to the signal."""
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
        """Compute the derivative of the filtered signal."""
        if len(self._buffer_filtered) < 5:
            return 0.0
        
        buf = list(self._buffer_filtered)[-5:]
        return (-buf[0] - 2*buf[1] + 2*buf[3] + buf[4]) / 8.0
    
    def _moving_average(self, sample: float) -> float:
        """Apply moving average to the squared signal."""
        if len(self._buffer_squared) < self.window_samples:
            return sample
        return sum(list(self._buffer_squared)[-self.window_samples:]) / self.window_samples
    
    def _update_threshold(self, integrated: float) -> None:
        """Update the adaptive detection threshold."""
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
        """Detect if the current sample is an R-peak."""
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