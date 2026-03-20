#matplotlibline.py
from streamsim.src.core.interfaces import StreamingRenderer
from typing import Any, List
import numpy as np

class MatplotlibLineRenderer(StreamingRenderer):
    """Default matplotlib line chart renderer."""
    
    def __init__(self, 
                 line_color: str = 'blue',
                 line_width: float = 2,
                 marker_style: str = 'ro',
                 marker_alpha: float = 0.7,
                 show_legend: bool = True,
                 title_template: str = "Streaming Data — Feature: {feature:.4f}"):
        self.line_color = line_color
        self.line_width = line_width
        self.marker_style = marker_style
        self.marker_alpha = marker_alpha
        self.show_legend = show_legend
        self.title_template = title_template
        
        self.line = None
        self.marker = None
        self.title_artist = None
        self.ax = None
        self.artists = []
    
    def initialize(self, ax: Any) -> List[Any]:
        self.ax = ax
        self.line, = ax.plot([], [], lw=self.line_width, 
                             color=self.line_color, label='Signal')
        self.marker, = ax.plot([], [], self.marker_style, 
                               alpha=self.marker_alpha, label='Change')
        self.title_artist = ax.set_title("")
        
        if self.show_legend:
            ax.legend()
        
        self.artists = [self.line, self.marker, self.title_artist]
        return self.artists
    
    def update(self, times: np.ndarray, samples: np.ndarray,
               features: np.ndarray, change_points: np.ndarray,
               window_duration_sec: float) -> List[Any]:
        
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
        self.line = None
        self.marker = None
        self.title_artist = None
        self.ax = None
