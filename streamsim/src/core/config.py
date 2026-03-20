"""Configuration dataclasses for the streaming framework."""

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple


@dataclass
class PlottingSetup:
    """Encapsulates matplotlib figure and axes configuration."""
    fig: Any
    ax: Any
    artists: Dict[str, Any] = field(default_factory=dict)
    xlim: Tuple[float, float] = None
    ylim: Tuple[float, float] = None
    title: str = "Streaming Data Visualization"
    
    def configure(self) -> None:
        """Apply initial configuration to axes."""
        self.ax.set_title(self.title)
        if self.xlim:
            self.ax.set_xlim(self.xlim)
        if self.ylim:
            self.ax.set_ylim(self.ylim)