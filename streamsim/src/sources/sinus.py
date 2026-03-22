__author__ = "F.Feenstra"

import numpy as np

class SinusDataSource:
    """Callable data source for sinus wave signals."""
    
    def __init__(self, frequency: float = 1.0, fs: float = 100.0, duration: float = 20.0):
        """
        Initialize the sinus wave data source.
        
        Args:
            frequency: Frequency of the sinus wave in Hz (default: 1.0 Hz).
            fs: Sampling frequency in Hz (default: 100.0 Hz).
            duration: Total duration of the signal in seconds (default: 20.0 sec).
        """
        self.frequency = frequency
        self.fs = fs
        self.duration = duration
        self._iterator = self._create_iterator()

    def _create_iterator(self):
        """Create the internal iterator that yields (sample, timestamp) pairs."""
        n_samples = int(self.duration * self.fs)
        for i in range(n_samples):
            t = i / self.fs
            sample = np.sin(2 * np.pi * self.frequency * t)
            yield sample, t

    def __call__(self):
        """
        Return the next (sample, timestamp) pair.
        
        Returns:
            tuple: (sample, timestamp) or None if data exhausted.
        """
        try:
            return next(self._iterator)
        except StopIteration:
            return None


def create_sinus_data_source(frequency: float = 1.0, fs: float = 100.0, duration: float = 20.0):
    """
    Factory function to create a SinusDataSource.
    
    Args:
        frequency: Frequency of the sinus wave in Hz.
        fs: Sampling frequency in Hz.
        duration: Total duration in seconds.
    
    Returns:
        SinusDataSource: An initialized callable data source.
    """
    return SinusDataSource(frequency=frequency, fs=fs, duration=duration)