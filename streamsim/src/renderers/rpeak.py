#rpeak.py
"""Renderer for ECG signals with R-peak markers."""

from typing import Any, List
import numpy as np
from streamsim.src.core.interfaces import StreamingRenderer


class RPeakRenderer(StreamingRenderer):
    """
    Renderer for ECG signals with R-peak markers.
    
    Shows:
        - Signal line: Raw ECG signal
        - Peak markers: Detected R-peaks at peak timestamps
    """
    
    def __init__(
        self,
        signal_color: str = 'blue',
        signal_width: float = 1.5,
        peak_color: str = 'green',
        peak_size: float = 10,
        show_legend: bool = True
    ):
        self.signal_color = signal_color
        self.signal_width = signal_width
        self.peak_color = peak_color
        self.peak_size = peak_size
        self.show_legend = show_legend
        
        self.signal_line = None
        self.peak_marker = None
        self.ax = None
    
    def initialize(self, ax: Any) -> List[Any]:
        self.ax = ax
        
        self.signal_line, = ax.plot(
            [], [], lw=self.signal_width,
            color=self.signal_color, label='Signal'
        )
        
        self.peak_marker, = ax.plot(
            [], [], 'o',
            color=self.peak_color,
            markersize=self.peak_size,
            label='Peak',
            zorder=5
        )
        
        if self.show_legend:
            ax.legend(loc='upper right')
        
        return [self.signal_line, self.peak_marker]
    
    def update(
        self,
        times: np.ndarray,
        samples: np.ndarray,
        features: np.ndarray,
        change_points: np.ndarray,
        window_duration_sec: float
    ) -> List[Any]:
        
        if len(times) == 0:
            return [self.signal_line, self.peak_marker]
        
        mask = times >= times[-1] - window_duration_sec
        self.signal_line.set_data(times[mask], samples[mask])
        
        peak_timestamps = features[features != None] if len(features) > 0 else np.array([])
        
        if len(peak_timestamps) > 0:
            visible_peaks = peak_timestamps[peak_timestamps >= times[-1] - window_duration_sec]
            
            if len(visible_peaks) > 0:
                y_values = np.interp(visible_peaks, times, samples)
                self.peak_marker.set_data(visible_peaks, y_values)
                self.peak_marker.set_visible(True)
            else:
                self.peak_marker.set_visible(False)
        else:
            self.peak_marker.set_visible(False)
        
        return [self.signal_line, self.peak_marker]
    
    def cleanup(self) -> None:
        self.signal_line = None
        self.peak_marker = None
        self.ax = None