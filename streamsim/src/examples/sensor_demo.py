"""Sensor Anomaly Detection Demonstration Script."""

__author__ = "F.Feenstra, J. Beenen"

#login set up
import logging
from streamsim.src.core.config import LoggingSetup
from streamsim.src.core.config import LOG_DIR
from datetime import datetime

# This MUST be the very first thing you do before importing other modules
logging_setup = LoggingSetup(
    level=logging.DEBUG,
    log_file=f"{LOG_DIR}/sensor_demo{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    timestamp_filename=True             # Set to True if you want unique filenames per run
)
logging_setup.setup_logging()
logger = logging.getLogger(__name__)


from streamsim.src.core.simulator import StreamingSimulator
from streamsim.src.core.config import PlottingSetup
# from streamsim.src.features.heart_rate import HRFeatureDeriver
from streamsim.src.features.simple import SimpleFeature
# from streamsim.src.detectors.hr_anomaly import HeartRateAnomalyDetector
from streamsim.src.detectors.simple import SimpleDetector
from streamsim.src.renderers.vline import VerticalLineRenderer

from streamsim.src.sources.sensor import create_signal_data_source #, create_ecg_with_temporary_anomaly
from matplotlib import pyplot as plt



def run_anomaly_detection_example():
    """
    Executes the Anomaly Detection demonstration pipeline.

    This function initializes all components required for the simulation,
    configures the visualization parameters, and starts the streaming loop.
    It blocks execution until the user closes the Matplotlib window.

    Components Initialized:
        - Data Source: Signal generator.
        - Feature Deriver: RPeakFeatureDeriver for heartbeat detection.
        - Detector: PeakPassThrough (specialized logic).
        - Renderer: RPeakRenderer (blue signal, green peaks).

    Example:
        >>> run_anomaly_detection_example()
        Running Anomaly Detection...
        # [Matplotlib window opens with live signal data]
    """
    logger.info("Starting Anomaly Detection demo")
    
    # 1. Setup Visualization
    fig, ax = plt.subplots(figsize=(12, 5))
    setup = PlottingSetup(
        fig=fig,
        ax=ax,
        title="Signal - Anomaly Detection (Z-Score Detector)",
        ylim= (-1, 15) #TODO: make this dynamic based on the data in window
    )

    # 2. Initialize Data Source
    data_source = create_signal_data_source()
    
    # 3. Configure Feature Deriver (R-Peak Detection)
    # # Sampling frequency set to 360Hz, typical for medical ECG devices.
    # deriver = HRFeatureDeriver(
    #     fs=360.0,
    #     min_rr_sec=0.2,      # Minimum RR interval (300 bpm limit)
    #     threshold_factor=0.7 # Sensitivity of the detection algorithm
    # )

    deriver = SimpleFeature()

    # 4. configure detector  
    # detector = HeartRateAnomalyDetector(
    #     threshold_std=3.0,       # Alert if HR deviates > 3 std devs from baseline
    #     warmup_beats=15,         # Learn baseline from first 15 beats
    #     confirmation_count=3,    # Require 3 consecutive outliers to alert
    #     recovery_count=5,        # Require 5 normal beats to clear alert
    #     baseline_adaptation=0.0  # Fixed baseline (no adaptation)
    #     )

    detector = SimpleDetector(threshold=10.0, history=1000)
    
    # 5. Configure Renderer
    renderer = VerticalLineRenderer(
        line_color='black',
        vline_color='red',
        vline_style='--',      # Dashed line
        vline_width=2.0,
        signal_label='Signal',
        vline_label='Anomaly',
        title_template='Real-time value: {feature:.2f}'
    )

    # 6. Initialize and Start Simulator
    sim = StreamingSimulator(
        plotting_setup=setup,
        feature_deriver=deriver,
        change_point_detector=detector,
        renderer=renderer,
        data_source=data_source,
        window_duration_sec=60.0,  # Show last 5 seconds
        max_history=5000,         # Memory buffer limit (TODO: in datapoints or in time?)
        interval_ms=1            # Update frequency (33Hz)
    )
    
    sim.start()

if __name__ == "__main__":
    run_anomaly_detection_example()