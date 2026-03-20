"""Abstract base classes for the streaming framework."""

from abc import ABC, abstractmethod
from typing import Optional, Any, List
import numpy as np


class StreamingFeatureDeriver(ABC):
    """Abstract base class for feature extraction from streaming data."""
    
    @abstractmethod
    def add_sample(self, sample: float, timestamp: float = None) -> None:
        """Add a new sample to the processor."""
        pass
    
    @abstractmethod
    def get_feature(self) -> Optional[float]:
        """Get the latest derived feature value."""
        pass
    
    def reset(self) -> None:
        """Reset internal state."""
        pass


class StreamingChangePointDetector(ABC):
    """Abstract base class for change point detection."""
    
    @abstractmethod
    def update(self, feature_value: Optional[float]) -> bool:
        """Update detector with new feature value. Returns True if change detected."""
        pass
    
    @property
    def drift_detected(self) -> bool:
        """Check if drift/change was detected."""
        return False


class StreamingRenderer(ABC):
    """Abstract base class for streaming visualizations."""
    
    @abstractmethod
    def initialize(self, ax: Any) -> List[Any]:
        """Create initial plot elements. Returns list of artists for blitting."""
        pass
    
    @abstractmethod
    def update(self, times: np.ndarray, samples: np.ndarray, 
               features: np.ndarray, change_points: np.ndarray,
               window_duration_sec: float) -> List[Any]:
        """Update plot elements with new data. Returns updated artists."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Release resources if needed."""
        pass

