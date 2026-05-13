"""
Sensor Data Processing Module

This module provides utilities for loading, modifying, and streaming
time-series data from CSV files.
The `ECG_DataSource`, implements a callable interface that 
yields (sample, timestamp) pairs sequentially, allowing for  
streaming of signal data without loading the entire signalstream into memory at once.

Dependencies:
    - wfdb: Waveform database access for MIT-BIH records

Author: F.Feenstra & J. Beenen

Example:
    >>> data_source = create_ecg_data_source()
    >>> modified_source = create_ecg_with_temporary_anomaly(start=5, stop=10)

"""
import numpy as np  
# import wfdb
import pandas as pd


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


def csv_to_arrays(
        file_path: str,
        timestamp: str = 'timestamp',
        category: str = 'category',
        value: str = 'value'
    ) -> tuple[np.ndarray, list]:
    """
    Load time-series data from a CSV file (in long-format) and convert it to numpy arrays.
    
    The CSV file is expected to have three columns: 'timestamp', 'category', and 'value'.
    
    Args:
        file_path (str): Path to the CSV file containing the data.
        timestamp (str): Name of the column representing timestamps.
        category (str): Name of the column representing categories or parameters.
        value (str): Name of the column representing the values.

    Returns:
        tuple: A tuple containing:
            - records (np.ndarray): 2D array of shape (num_timestamps, num_categories) with the values.
            - category_names (list): List of category names corresponding to the columns in 'records'.

    """
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Create wide-format DataFrame with timestamps as index and categories as columns
    df = df.pivot(
        index= 'parameter_sequence',
        columns= 'parameter',
        values= 'value'
    )

    # Convert the DataFrame to a numpy array
    records = df.to_numpy().T
    category_names = df.columns.tolist()

    return records, category_names


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
        # record = wfdb.rdrecord("100", pn_dir="mitdb")
        # ecg_signal = record.p_signal[:, 0]
        # fs = record.fs

        records, category_names = csv_to_arrays(
            file_path="./data/case1_frame1.csv",
            timestamp='parameter_sequence',
            category='parameter',
            value='value'
        )
        # TODO: make this dynamic based on the data, for now we just take the first category and set fs to 1Hz for testing
        index = 0
        signal = records[index]
        fs = 1 
        # fs = 0.2
        # fs= 360
        print(f"Signal of parameter: {category_names[index]}")

        return ECG_DataSource(signal, fs)
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
    
# create_ecg_data_source()