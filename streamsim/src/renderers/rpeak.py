#rpeak.py
"""Renderer for ECG signals with R-peak markers."""

from typing import Any, List
import numpy as np
from streamsim.src.core.interfaces import StreamingRenderer


class RPeakRenderer(StreamingRenderer):
    """
    Renderer for ECG signals with R-peak markers.
    
    This class provides real-time visualization of electrocardiogram (ECG) signals
    with automatic marking of detected R-peaks (QRS complexes). It extends the
    StreamingRenderer base class to support dynamic updates of signal traces
    and peak annotations within a configurable time window.
    
    Attributes:
        signal_color (str): Color of the ECG signal line (default: 'blue').
        signal_width (float): Line width of the signal trace (default: 1.5).
        peak_color (str): Color of the R-peak markers (default: 'green').
        peak_size (float): Size of the peak marker points (default: 10).
        show_legend (bool): Whether to display the plot legend (default: True).
        
    Visual Elements:
        - Signal line: Displays the raw ECG signal within the active time window
        - Peak markers: Shows detected R-peaks as circular markers at their
          corresponding signal amplitude positions
        
    Methods:
        initialize(ax): Sets up the matplotlib axes with empty signal and peak
                       line objects, and optionally adds a legend.
        update(): Refreshes the visualization with new signal data and peak
                 timestamps, filtering to the specified window duration.
        cleanup(): Releases references to plot elements for memory management.
        
    Parameters:
        signal_color (str): Color specification for the ECG signal line.
        signal_width (float): Stroke width for the signal line.
        peak_color (str): Color specification for R-peak markers.
        peak_size (float): Marker size in points for R-peaks.
        show_legend (bool): Toggle legend visibility in the upper right corner.
        
    Returns:
        List[Any]: In update(), returns list of updated matplotlib artists
                   [signal_line, peak_marker] for animation frameworks.
                   
    Example:
        >>> #Creates a new renderer instance with customized colors
        >>> renderer = RPeakRenderer(signal_color='red', peak_color='yellow') 
        >>> #Prepare the matplotlib axes (ax) for rendering
        >>> artists = renderer.initialize(ax)
        >>> #In the animation loop, update the plot with new data
        >>> renderer.update(times, samples, features, change_points, 10.0)
        
    Note:
        Peak timestamps in the features array should be in the same time units
        as the times array. Peaks outside the visible window are automatically
        filtered out. The peak y-values are interpolated from the signal data.
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