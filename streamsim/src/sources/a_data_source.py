"""
AData Signal Generation Module

This module provides a data source for loading and streaming signal data 
from the 'a_data.csv' file. It mimics the interface of the SinusDataSource 
to allow seamless replacement in existing pipelines.

The `ADataDataSource` implements a callable interface that yields 
(sample, timestamp) pairs sequentially.

"""

from pathlib import Path
import pandas as pd

class SensorDataSource:
    """Generator-based wrapper for Sensor data."""
    def __init__(self, signal, fs):
        """
        Initialize the data source.
        
        Args:
            signal (np.ndarray): Array of signal values.
            fs (float): Sampling frequency in Hz.
        """
        self.signal = signal
        self.fs = fs
        self._iterator = self._create_iterator()

    def _create_iterator(self):
        """
        Create a generator that yields (sample, timestamp) pairs.
        
        Iterates through the signal array, computing the timestamp for each
        sample based on its index and the sampling frequency.
        
        Yields:
            tuple: A pair containing (sample_value, timestamp_in_seconds).
        """
        for i, sample in enumerate(self.signal):
            yield sample, i / self.fs

    def __call__(self):
        """
        Retrieve the next sample from the iterator.
        
        Returns:
            tuple|None: (sample, timestamp) if available, None if exhausted.
        """
        try:
            return next(self._iterator)
        except StopIteration:
            return None



def create_a_data_source(file_path: str = None, fs: float = 200.0) -> SensorDataSource:
    """
    Create data source.

    Returns:
        ADataDataSource: A data source containing sensor data.

    """
    try:
        data_dir = Path.home() / ".streamsim" / "data"
        df = pd.read_csv(f"{data_dir}/{file_path}")
        signal = df['value'].values
        return SensorDataSource(signal, fs)
    except ImportError:
        print("data not found, generate mock data instead")
        t = np.linspace(0, 10, 3600)
        # Simple mock ECG: sine + spikes
        signal = np.sin(2 * np.pi * 1.2 * t) 
        # Add some spikes
        for i in range(0, len(signal), 100):
            if i+10 < len(signal):
                signal[i:i+10] += 2.0
        return SensorDataSource(signal, 360.0)
    

