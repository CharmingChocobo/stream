"""Matplotlib renderer with vertical line change point visualization."""

from typing import List, Any
import numpy as np
from streamsim.src.core.interfaces import StreamingRenderer


class VerticalLineRenderer(StreamingRenderer):
    """
    Streaming renderer that displays vertical lines at detected change points.
     
    Args:
        line_color (str): Color of the signal line (default: 'blue').
        line_width (float): Stroke width of the signal line (default: 2.0).
        vline_color (str): Color of the vertical change lines (default: 'red').
        vline_style (str): Line style for vertical lines (default: '--' dashed).
        vline_width (float): Width of vertical lines (default: 1.5).
        vline_alpha (float): Transparency of vertical lines (default: 0.7).
        signal_label (str): Legend label for the signal line (default: 'Signal').
        vline_label (str): Legend label for change lines (default: 'Anomaly').
        show_legend (bool): Whether to display the plot legend (default: True).
        title_template (str): Format string for dynamic title with {feature} placeholder.
    
    Example:
        >>> renderer = VerticalLineRenderer(
        ...     line_color='black',
        ...     vline_color='red',
        ...     vline_style='--',
        ...     title_template='Heart Rate: {feature:.1f} bpm'
        ... )
        >>> fig, ax = plt.subplots()
        >>> artists = renderer.initialize(ax)
    """
    
    def __init__(
        self,
        line_color: str = 'blue',
        line_width: float = 2,
        vline_color: str = 'red',
        vline_style: str = '--',
        vline_width: float = 1.5,
        vline_alpha: float = 0.7,
        signal_label: str = 'Signal',
        vline_label: str = 'Anomaly',
        show_legend: bool = True,
        title_template: str = "Streaming Data — Feature: {feature:.4f}"
    ):
        self.line_color = line_color
        self.line_width = line_width
        self.vline_color = vline_color
        self.vline_style = vline_style
        self.vline_width = vline_width
        self.vline_alpha = vline_alpha
        self.signal_label = signal_label
        self.vline_label = vline_label
        self.show_legend = show_legend
        self.title_template = title_template
        
        self.line = None
        self.vlines = []  # List of vertical line artists
        self.title_artist = None
        self.ax = None
        self.artists = []
        
        # Track displayed change points to avoid duplicates
        self._displayed_changes = set()
    
    def initialize(self, ax: Any) -> List[Any]:
        """
        Create initial plot elements on the provided axes.
        
        Args:
            ax (Any): The matplotlib Axes instance to draw on.
        
        Returns:
            List[Any]: List of artist objects for animation tracking.
        """
        self.ax = ax
        self.line, = ax.plot([], [], lw=self.line_width, 
                             color=self.line_color, label=self.signal_label)
        
        # Create a proxy artist for legend (actual vlines created dynamically)
        self._legend_proxy, = ax.plot([], [], 
                                       color=self.vline_color,
                                       linestyle=self.vline_style,
                                       lw=self.vline_width,
                                       label=self.vline_label)
        
        self.title_artist = ax.set_title("")
        
        if self.show_legend:
            ax.legend()
        
        self.artists = [self.line, self.title_artist]
        return self.artists
    
    def update(
        self,
        times: np.ndarray,
        samples: np.ndarray,
        features: np.ndarray,
        change_points: np.ndarray,
        window_duration_sec: float
    ) -> List[Any]:
        """
        Update plot elements with new streaming data.
        
        Args:
            times (np.ndarray): Array of timestamps.
            samples (np.ndarray): Array of signal values.
            features (np.ndarray): Array of feature values.
            change_points (np.ndarray): Array of change point timestamps.
            window_duration_sec (float): Visible time window duration.
        
        Returns:
            List[Any]: Updated artist objects.
        """
        # print(f"[Renderer] Received change_points: {change_points}, len={len(change_points)}")

        if len(times) == 0:
            return self.artists
        
        # Update signal line
        mask = times >= times[-1] - window_duration_sec
        self.line.set_data(times[mask], samples[mask])
        
        # Get current y-limits for vertical lines
        y_min, y_max = self.ax.get_ylim()
        
        # Determine visible window
        window_start = times[-1] - window_duration_sec
        window_end = times[-1]
        
        # Remove old vertical lines outside the window
        for vline in self.vlines[:]:
            x_pos = vline.get_xdata()[0]
            if x_pos < window_start:
                vline.remove()
                self.vlines.remove(vline)
                self._displayed_changes.discard(x_pos)
        
        # Add new vertical lines for change points in window
        if len(change_points) > 0:
            visible_cps = change_points[change_points >= window_start]
            
            for cp in visible_cps:
                # Round to avoid floating point duplicate issues
                cp_key = round(cp, 4)
                
                if cp_key not in self._displayed_changes:
                    # Create vertical line spanning full y-range
                    vline = self.ax.axvline(
                        x=cp,
                        color=self.vline_color,
                        linestyle=self.vline_style,
                        linewidth=self.vline_width,
                        alpha=self.vline_alpha
                    )
                    self.vlines.append(vline)
                    self._displayed_changes.add(cp_key)
        
        # Update title with latest feature value
        if len(features) > 0 and self.title_artist is not None:
            latest_feature = features[-1]
            if latest_feature is not None:
                self.title_artist.set_text(
                    self.title_template.format(feature=latest_feature)
                )
        
        return self.artists + self.vlines
    
    def cleanup(self) -> None:
        """Release resources and clear references."""
        for vline in self.vlines:
            vline.remove()
        self.vlines.clear()
        self._displayed_changes.clear()
        
        self.line = None
        self.title_artist = None
        self.ax = None
        self.artists = []