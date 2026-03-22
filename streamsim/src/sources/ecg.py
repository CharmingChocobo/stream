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


def create_ecg_with_temporary_anomaly(start, stop):
    """Creates an ECG source with temporary heart rate increase from 10-20 seconds."""
    
    record = wfdb.rdrecord("100", pn_dir="mitdb")
    ecg_signal = record.p_signal[:, 0]
    fs = record.fs
    
    # Define phase boundaries
    phase1_end = int(start * fs)   # 0-start: Normal
    phase2_end = int(stop * fs)   # start-stop sec: Accelerated
    # stop++ sec: Normal again  
    
    # Acceleration factor (2x = double heart rate)
    acceleration_factor = 2
    
    # Phase 1: Normal (first 10 seconds)
    segment_normal_1 = ecg_signal[:phase1_end]
    
    # Phase 2: Accelerated (next 10 seconds worth of ORIGINAL signal, compressed)
    # Take samples from phase2_start to phase2_end, but downsample
    phase2_start = phase1_end
    phase2_end_original = phase2_end  # Original timeline
    segment_fast = ecg_signal[phase2_start:phase2_end_original:acceleration_factor]
    
    # Phase 3: Normal again (rest of signal)
    # Continue from where we left off in original signal
    segment_normal_2 = ecg_signal[phase2_end_original:]
    
    # Stitch together
    modified_signal = np.concatenate([segment_normal_1, segment_fast, segment_normal_2])
    
    return ECG_DataSource(modified_signal, fs)

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