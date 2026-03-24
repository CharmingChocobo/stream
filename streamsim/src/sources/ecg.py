"""
ECG Data Processing Module

This module provides utilities for loading, modifying, and streaming
electrocardiogram (ECG) signals from the MIT-BIH Arrhythmia Database.
It includes functionality for creating synthetic anomalies (e.g., 
temporary heart rate acceleration). 
The `ECG_DataSource`, implements a callable interface that 
yields (sample, timestamp) pairs sequentially, allowing for  
streaming of signal data without loading the entire signalstream into memory at once.

Dependencies:
    - wfdb: Waveform database access for MIT-BIH records

Author: F.Feenstra

Example:
    >>> data_source = create_ecg_data_source()
    >>> modified_source = create_ecg_with_temporary_anomaly(start=5, stop=10)

"""

import numpy as np  
import wfdb


class ECG_DataSource:
    """Generator-based wrapper for ECG data."""
    def __init__(self, signal, fs):
        """
        Initialize the ECG data source.
        
        Args:
            signal (np.ndarray): Array of ECG signal amplitude values.
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




def create_ecg_data_source():
    """
    Create an ECG data source with fallback to mock data.
    
    Attempts to load real ECG data from the MIT-BIH Arrhythmia Database
    (record '100'). If the wfdb library is unavailable or the record cannot
    be loaded, generates a synthetic ECG-like signal for testing purposes.
    
    Returns:
        ECG_DataSource: A data source containing either real or mock ECG data.

    """
    try:
        record = wfdb.rdrecord("100", pn_dir="mitdb")
        ecg_signal = record.p_signal[:, 0]
        fs = record.fs

        return ECG_DataSource(ecg_signal, fs)
    except ImportError:
        print("wfdb not found. Generating mock ECG-like signal.")
        t = np.linspace(0, 10, 3600)
        # Simple mock ECG: sine + spikes
        signal = np.sin(2 * np.pi * 1.2 * t) 
        # Add some spikes
        for i in range(0, len(signal), 100):
            if i+10 < len(signal):
                signal[i:i+10] += 2.0
        return ECG_DataSource(signal, 360.0)
    


def create_ecg_with_temporary_anomaly(start, stop):
    """
    Create an ECG data source with a temporary heart rate acceleration.
    
    Generates a modified ECG signal where the segment between 'start' and 
    'stop' seconds is accelerated (compressed in time) to simulate increased
    heart rate. The rest of the signal remains unchanged.
    
    Args:
        start (float): Start time in seconds where acceleration begins.
        stop (float): End time in seconds where acceleration ends.
    
    Returns:
        ECG_DataSource: A data source containing the modified ECG signal.
    
    """
    try: 
        record = wfdb.rdrecord("100", pn_dir="mitdb")
        ecg_signal = record.p_signal[:, 0]
        fs = record.fs
    except ImportError:
        print("wfdb not found. Generating mock ECG-like signal.")
        t = np.linspace(0, 10, 3600)
        # Simple mock ECG: sine + spikes
        signal = np.sin(2 * np.pi * 1.2 * t) 
        # Add some spikes
        for i in range(0, len(signal), 100):
            if i+10 < len(signal):
                signal[i:i+10] += 2.0  
        ecg_signal = signal
        fs = 360.0
    

    # Define phase boundaries
    phase1_end = int(start * fs)  # 0-start: Normal
    phase2_end = int(stop * fs)   # start-stop sec: Accelerated
                                  # stop++ sec: Normal again  
    
    acceleration_factor = 2 # Acceleration factor (2x = double heart rate)
    segment_normal_1 = ecg_signal[:phase1_end]
    phase2_start = phase1_end
    phase2_end_original = phase2_end  
    segment_fast = ecg_signal[phase2_start:phase2_end_original:acceleration_factor]
    segment_normal_2 = ecg_signal[phase2_end_original:]
    
    modified_signal = np.concatenate([segment_normal_1, segment_fast, segment_normal_2])
    
    return ECG_DataSource(modified_signal, fs)
