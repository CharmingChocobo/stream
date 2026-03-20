#ecg.py

import numpy as np  
import wfdb


class ECG_DataSource:
    """Generator-based."""
    def __init__(self, signal, fs):
        self.signal = signal
        self.fs = fs
        self._iterator = self._create_iterator()

    def _create_iterator(self):
        for i, sample in enumerate(self.signal):
            yield sample, i / self.fs

    def __call__(self):
        try:
            return next(self._iterator)
        except StopIteration:
            return None


def create_ecg_data_source():
    # Mock data if wfdb is not installed, otherwise load real data
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