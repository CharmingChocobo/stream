""" Sinus Wave Peak Detection Demonstration Script."""

__author__ = "F.Feenstra"


#login set up
import logging
from streamsim.src.core.config import LoggingSetup
from streamsim.src.core.config import LOG_DIR
from datetime import datetime

# This MUST be the very first thing you do before importing other modules
logging_setup = LoggingSetup(
    level=logging.DEBUG,
    log_file=f"{LOG_DIR}/sinus_demo{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    timestamp_filename=True             # Set to True if you want unique filenames per run
)
logging_setup.setup_logging()
logger = logging.getLogger(__name__)


from streamsim.src.core.simulator import StreamingSimulator
from streamsim.src.core.config import PlottingSetup
from streamsim.src.features.local_maxima import LocalMaximaDeriver
from streamsim.src.sources.sinus import create_sinus_data_source
from streamsim.src.renderers.matplotlib_line import MatplotlibLineRenderer
from streamsim.src.detectors.passthrough import PeakPassThrough

import numpy as np
import matplotlib.pyplot as plt


def run_sinus_example():
    """
    Executes the Sinus Wave Peak Detection demonstration pipeline.

    This function sets up a synthetic 1 Hz sine wave source and processes it
    through a general-purpose feature derivation and detection chain. It
    visualizes the raw wave and marks the detected local maxima (peaks).

    Configuration Details:
        - Signal Frequency: 1.0 Hz (one cycle per second).
        - Sampling Rate: 100.0 Hz (10 ms intervals).
        - Duration: Generates data for 20 seconds.
        - Window Duration: 5.0 seconds of rolling data visible.
        - Simulation Interval: 30ms (approx. 33Hz update rate).
        - History Limit: Keeps up to 5000 samples in memory.

    Components Initialized:
        - Data Source: Custom generator yielding `sin(2πt)`.
        - Feature Deriver: `SimpleFeature` (passes data through).
        - Detector: `SimpleDetector` (identifies local maxima).
        - Renderer: `RPeakRenderer` (blue signal, orange peaks).

    Example:
        >>> run_sinus_example()
        Running Sinus Wave Peak Detection...
        # [Matplotlib window opens with live sine wave and orange peak markers]
    """
    logger.info("Running Sinus Wave Peak Detection...")
    
    # 1. Setup Visualization
    fig, ax = plt.subplots(figsize=(12, 5))
    setup = PlottingSetup(
        fig=fig,
        ax=ax,
        title="Sinus Wave Peaks (General Detector)",
        ylim=(-2, 2)
    )

    # 2. Define Data Source Generator
    # Generates a 1 Hz sine wave sampled at 100 Hz for 20 seconds.
    sinus_source = create_sinus_data_source(frequency=1.0, fs=100.0, duration=40.0)
    
    # 3. Configure Feature Deriver
    deriver = LocalMaximaDeriver()
    
    # 4. Configure Detector
    detector = PeakPassThrough()
    
    # 5. Configure Renderer
    renderer = MatplotlibLineRenderer(
        line_color='blue',
        marker_style='ro',
        marker_alpha=0.8,
        show_legend=True,
        marker_label='Peak',
        title_template="Sinus Wave Peaks — Latest Value: {feature:.1f}"
    )

    # 6. Initialize and Start Simulator
    sim = StreamingSimulator(
        plotting_setup=setup,
        feature_deriver=deriver,
        change_point_detector=detector,
        renderer=renderer,
        data_source=sinus_source,
        window_duration_sec=5.0,  # Show last 5 seconds
        max_history=5000,         # Memory buffer limit
        interval_ms=100           # Update frequency (10Hz)
    )
    
    sim.start()

if __name__ == "__main__":
    run_sinus_example()