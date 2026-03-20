"""ECG R-Peak detection demonstration."""

import matplotlib.pyplot as plt

from streamsim.src.core.simulator import StreamingSimulator
from streamsim.src.core.config import PlottingSetup
from streamsim.src.features.rpeak import RPeakFeatureDeriver
from streamsim.src.detectors.passthrough import PeakPassThrough
from streamsim.src.renderers.rpeak import RPeakRenderer
from streamsim.src.sources.ecg import create_ecg_data_source

def run_rpeak_example():
    """Demonstrates the RPeakFeatureDeriver with ECG data."""
    print("Running R-Peak Detection...")
    fig, ax = plt.subplots(figsize=(12, 5))

    setup = PlottingSetup(
        fig=fig,
        ax=ax,
        title="ECG R-Peak Detection (Specialized Detector)",
        ylim=(-2, 2)
    )

    data_source = create_ecg_data_source()
    
    # Use the SPECIALIZED detector
    peak_deriver = RPeakFeatureDeriver(
        fs=360.0,
        min_rr_sec=0.2,
        threshold_factor=0.7, 
    )
    
    detector = PeakPassThrough()
    
    renderer = RPeakRenderer(
        signal_color='blue',
        peak_color='green',
        peak_size=8
    )

    sim = StreamingSimulator(
        plotting_setup=setup,
        feature_deriver=peak_deriver,
        change_point_detector=detector,
        renderer=renderer,
        data_source=data_source,
        window_duration_sec=5.0,
        max_history=5000,
        interval_ms=30
    )
    
    sim.start()

if __name__ == "__main__":
    run_rpeak_example()