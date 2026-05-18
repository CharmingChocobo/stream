"""
Signal Data Processing Module

This module provides utilities for loading, modifying, and streaming
time-series data from CSV files.
The `SignalDataSource`, implements a callable interface that 
yields (sample, timestamp) pairs sequentially, allowing for  
streaming of signal data without loading the entire signalstream into memory at once.

Author: F.Feenstra & J. Beenen

Example:
    >>> data_source = create_data_source()

"""
import numpy as np
import pandas as pd
import yaml

# Load configuration from YAML file
with open("./config.yaml", "r", encoding="utf-8") as stream:
    config = yaml.safe_load(stream)


class SignalDataSource:
    """Generator-based wrapper for signal data."""
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


def csv_to_arrays(
        file_path: str,
        timestamp: str,
        category: str,
        value: str
    ) -> tuple[np.ndarray, list]:
    """
    Load time-series data from a CSV file (in long-format) and convert it to numpy arrays.
    
    The CSV file is expected to have the following three columns: 'timestamp', 'category', and 'value'.
    
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
        index= timestamp,
        columns= category,
        values= value
    )

    # Convert the DataFrame to a numpy array
    records = df.to_numpy().T
    category_names = df.columns.tolist()
    # print(f"Following categories found in the data: {category_names}")

    return records, category_names


def create_signal_data_source():
    """
    Create a signal data source with fallback to mock data.
    
    Attempts to load real signal data from a CSV file. If the file cannot be loaded,
    generates a synthetic signal for testing purposes.
    
    Returns:
        SignalDataSource: A data source containing either real or mock signal data.

    """
    try:
        records, category_names = csv_to_arrays(
            file_path= config["sensor_file"],
            timestamp= config["timestamp_column"],
            category= config["category_column"],
            value= config["value_column"],
        )
        # TODO: make this dynamic based on the data, for now we just take the first category and set fs to 1Hz for testing
        index = category_names.index(input(f"Enter the name of the parameter to use as signal {category_names}: ").lower())
        # index = 0
        print(f"Signal of parameter: {category_names[index]}")
        signal = records[index]
        # fs = 0.2
        # fs = 1 
        fs = 200 # This is 1000x faster than original
        # fs = 360
        # fs = 720
        # fs= 1280

        return SignalDataSource(signal, fs)
    except FileNotFoundError:
        print(f"CSV file not found: '{config['sensor_file']}'. Generating mock signal.")
        t = np.linspace(0, 10, 3600)
        # Simple mock ECG: sine + spikes
        signal = np.sin(2 * np.pi * 1.2 * t) 
        # Add some spikes
        for i in range(0, len(signal), 100):
            if i+10 < len(signal):
                signal[i:i+10] += 2.0
        return SignalDataSource(signal, 360.0)

if __name__ == "__main__":
    create_signal_data_source()
