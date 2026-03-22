from typing import List, Any
import numpy as np
from streamsim.src.core.interfaces import StreamingRenderer 

class MatplotlibLineRenderer(StreamingRenderer):
    """
    Default matplotlib line chart renderer for streaming data visualization.
    
    This class implements the StreamingRenderer interface to provide real-time
    visualization of streaming signals with configurable styling and change point
    annotation. It supports dynamic title updates based on feature values and
    flexible legend configuration for both signal and marker elements.
    
    Designed for use with the streaming framework's data pipeline, this renderer
    efficiently updates plot elements without redrawing the entire figure,
    making it suitable for high-frequency data streams.
    
    Args:
        line_color (str): Color of the signal line (default: 'blue').
        line_width (float): Stroke width of the signal line (default: 2.0).
        marker_style (str): Matplotlib marker style string (default: 'ro' = red circles).
        marker_alpha (float): Transparency of change point markers (default: 0.7).
        signal_label (str): Legend label for the signal line (default: 'Signal').
        marker_label (str): Legend label for change point markers (default: 'Change').
        show_legend (bool): Whether to display the plot legend (default: True).
        title_template (str): Format string for dynamic title with {feature} placeholder.
        

    Returns:
        List[Any]: In initialize() and update(), returns list of artist objects
                   [line, marker, title_artist] for animation framework tracking.
    
    Example:
        >>> from streamsim.src.renderers.matplotlibline import MatplotlibLineRenderer
        >>> import matplotlib.pyplot as plt
        >>>
        >>> # Basic usage with defaults
        >>> renderer = MatplotlibLineRenderer()
        >>> fig, ax = plt.subplots()
        >>> artists = renderer.initialize(ax)
        >>>
        >>> # Customized for ECG visualization
        >>> renderer = MatplotlibLineRenderer(
        ...     line_color='black',
        ...     marker_style='go',
        ...     signal_label='ECG Lead II',
        ...     marker_label='R-Peak',
        ...     title_template='Heart Rate: {feature:.1f} bpm'
        ... )
        >>> artists = renderer.initialize(ax)
        >>> # Later in the loop:
        >>> renderer.update(times, samples, features, change_points, 5.0)
        >>>
        >>> # Hide markers from legend
        >>> renderer = MatplotlibLineRenderer(marker_label='_nolegend_')
    
    """
    
    def __init__(
        self,
        line_color: str = 'blue',
        line_width: float = 2,
        marker_style: str = 'ro',
        marker_alpha: float = 0.7,
        signal_label: str = 'Signal',
        marker_label: str = 'Change',
        show_legend: bool = True,
        title_template: str = "Streaming Data — Feature: {feature:.4f}"
    ):
        self.line_color = line_color
        self.line_width = line_width
        self.marker_style = marker_style
        self.marker_alpha = marker_alpha
        self.signal_label = signal_label
        self.marker_label = marker_label
        self.show_legend = show_legend
        self.title_template = title_template
        
        self.line = None
        self.marker = None
        self.title_artist = None
        self.ax = None
        self.artists = []
    
    def initialize(self, ax: Any) -> List[Any]:
        """
        Create initial plot elements on the provided axes.
        
        Sets up the signal line, change point markers, and dynamic title on the
        given matplotlib axes. This method should be called once before the
        streaming loop begins.
        
        Args:
            ax (Any): The matplotlib Axes instance to draw on. Typically obtained
                      from plt.subplots() or fig.add_subplot().
        
        Returns:
            List[Any]: List of artist objects [line, marker, title_artist] that
                       should be tracked for efficient updates (e.g., blitting).
        
        Example:
            >>> fig, ax = plt.subplots()
            >>> renderer = MatplotlibLineRenderer()
            >>> artists = renderer.initialize(ax)
            >>> assert len(artists) == 3  # line, marker, title
        """
        self.ax = ax
        self.line, = ax.plot([], [], lw=self.line_width, 
                             color=self.line_color, label=self.signal_label)
        
        self.marker, = ax.plot([], [], self.marker_style, 
                               alpha=self.marker_alpha, label=self.marker_label)
        
        self.title_artist = ax.set_title("")
        
        if self.show_legend:
            ax.legend()
        
        self.artists = [self.line, self.marker, self.title_artist]
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
        
        Refreshes the signal line, change point markers, and dynamic title based
        on the latest data within the specified time window. This method is called
        repeatedly during the streaming loop.
        
        Args:
            times (np.ndarray): Array of timestamps corresponding to each sample.
            samples (np.ndarray): Array of raw signal values.
            features (np.ndarray): Array of derived feature values (may contain None).
            change_points (np.ndarray): Array of timestamps where change points
                                        were detected.
            window_duration_sec (float): Duration of the visible time window in
                                         seconds. Only data within this window
                                         will be displayed.
        
        Returns:
            List[Any]: Updated list of artist objects that have been modified.
                       Used by animation frameworks to determine what to redraw.
        
        Example:
            >>> times = np.array([0, 1, 2, 3, 4, 5])
            >>> samples = np.array([0, 1, 0, -1, 0, 1])
            >>> features = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
            >>> change_points = np.array([2.5, 4.5])
            >>> artists = renderer.update(times, samples, features, change_points, 3.0)
        """
        if len(times) == 0:
            return self.artists
        
        # Update signal line
        mask = times >= times[-1] - window_duration_sec
        self.line.set_data(times[mask], samples[mask])
        
        # Update change point markers
        if len(change_points) > 0:
            visible_mask = change_points >= times[-1] - window_duration_sec
            visible_cps = change_points[visible_mask]
            
            if len(visible_cps) > 0:
                y_values = np.interp(visible_cps, times, samples)
                self.marker.set_xdata(visible_cps)
                self.marker.set_ydata(y_values)
                self.marker.set_visible(True)
            else:
                self.marker.set_visible(False)
        else:
            self.marker.set_visible(False)
        
        # Update title with latest feature value
        if len(features) > 0 and self.title_artist is not None:
            latest_feature = features[-1]
            self.title_artist.set_text(self.title_template.format(feature=latest_feature))
        
        return self.artists
    
    def cleanup(self) -> None:
        """
        Release resources and clear references.
        This method can be called when the simulation is stopped to clean up any resources and prevent memory leaks.
        """
        self.line = None
        self.marker = None
        self.title_artist = None
        self.ax = None
        self.artists = []