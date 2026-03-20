from streamsim.src.core.simulator import StreamingSimulator
from streamsim.src.core.config import PlottingSetup
from streamsim.src.features.local_maxima import LocalMaximaDeriver
from streamsim.src.features.simple import SimpleFeature
from streamsim.src.detectors.simple import SimpleDetector
from streamsim.src.detectors.passthrough import PeakPassThrough
from streamsim.src.renderers.rpeak import RPeakRenderer
import numpy as np
import matplotlib.pyplot as plt

def run_sinus_example():
    """Demonstrates the LocalMaximaDeriver with a Sinus wave."""
    print("Running Sinus Wave Peak Detection...")
    fig, ax = plt.subplots(figsize=(12, 5))

    setup = PlottingSetup(
        fig=fig,
        ax=ax,
        title="Sinus Wave Peaks (General Detector)",
        ylim=(-2, 2)
    )

    # Generate Sinus Data Source
    def sinus_source():
        t = 0
        fs = 100.0
        while t < 20:
            sample = np.sin(2 * np.pi * 1.0 * t) # 1 Hz sine wave
            yield sample, t
            t += 1.0/fs

    # Use the GENERAL detector
    deriver = SimpleFeature()
    detector = SimpleDetector()
    
    # Reuse RPeakRenderer (it just looks for timestamps in features)
    renderer = RPeakRenderer(
        signal_color='blue',
        peak_color='orange', # Orange for sinus
        peak_size=8
    )

    sim = StreamingSimulator(
        plotting_setup=setup,
        feature_deriver=deriver,
        change_point_detector=detector,
        renderer=renderer,
        data_source=sinus_source,
        window_duration_sec=5.0,
        max_history=5000,
        interval_ms=30
    )
    
    sim.start()

if __name__ == "__main__":
    run_sinus_example()