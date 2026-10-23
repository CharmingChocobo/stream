"""
Plateau Detector

Detects a plateau in the raw signal.

Detection Method:
    The detector maintains a rolling history of recent samples and computes the
    mean and standard deviation (SD). ~~A new sample is flagged as a change point if it
    deviates~~ from the recent SD by less than a configurable number of standard
    deviations (threshold).~~

Important Dependencies:
    - collections.deque: Efficient circular buffer
    - streamsim.src.core.interfaces.StreamingChangePointDetector: Base interface

Author: F. Feenstra & J. 
# TODO: It appears to function on the 'smooth model' data instead of the raw data. Ideally it should function on the raw signal.
"""

from collections import deque
import numpy as np
from streamsim.src.core.interfaces import StreamingChangePointDetector
from streamsim.src.core.logger import get_logger  # Import logger

# Get a logger specific to this module
logger = get_logger(__name__)


class PlateauDetector(StreamingChangePointDetector):
    """
    Flags a detection when (plateau = the moving variance < near_zero)

    Very simple change point detector that flags points deviating from recent mean
    by more than a specified number of standard deviations.
    """
    
    def __init__(
            self, 
            near_zero: float = 0.0001,
            history: int = 50
        ):
        """
        Initialize the PlateauDetector with a configurable sensitivity threshold (`near_zero`).
        
        Args:
            near_zero (float): Number of standard deviations for change point detection.
                               Default: 0.0001.
            history (int): 
                           Default: 50.
        """
        self.near_zero = near_zero
        self.history = deque(maxlen=history)


    def update(self, feature_value: float, raw_sample=None) -> bool:
        """
        Process a new sample and determine if it represents a change point.
        
        ~~Adds the sample to the rolling history, then checks if it deviates
        significantly from the recent mean using a z-score-based approach.~~

        Adds the sample to the rolling history, then checks if it deviates
        significantly from the recent SD using a z-score-based approach.
        
        Args:
            x (float): The new sample value to evaluate.
        
        Returns:
            bool: True if the sample is flagged as a change point, False otherwise.
        
        """
        self.history.append(feature_value)

        if len(self.history) > 20:
            arr = np.array(self.history)
            # Exclude current sample from statistics (use all but last)
            mean = arr[:-1].mean()
            std = arr[:-1].std()

            if (mean == feature_value) & (abs(std) <= self.near_zero * abs(std)):
            # if abs(std) <= self.near_zero * abs(std):
                return True
        return False
    