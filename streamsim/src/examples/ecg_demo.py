""" ECG R-Peak Detection Demonstration Script."""

__author__ = "F.Feenstra"

from streamsim.src.core.simulator import StreamingSimulator
from streamsim.src.core.config import PlottingSetup
from streamsim.src.features.heart_rate import HRFeatureDeriver
from streamsim.src.detectors.hr_anomaly import HeartRateAnomalyDetector
from streamsim.src.renderers.vline import VerticalLineRenderer
from streamsim.src.sources.ecg import create_ecg_data_source, create_ecg_with_temporary_anomaly
from matplotlib import pyplot as plt


def run_rpeak_example():
    """
    Executes the R-Peak Detection demonstration pipeline.

    This function initializes all components required for the simulation,
    configures the visualization parameters, and starts the streaming loop.
    It blocks execution until the user closes the Matplotlib window.

    Components Initialized:
        - Data Source: Synthetic ECG signal generator.
        - Feature Deriver: RPeakFeatureDeriver for heartbeat detection.
        - Detector: PeakPassThrough (specialized logic).
        - Renderer: RPeakRenderer (blue signal, green peaks).

    Example:
        >>> run_rpeak_example()
        Running R-Peak Detection...
        # [Matplotlib window opens with live ECG data]
    """
    print("Running R-Peak Detection...")
    
    # 1. Setup Visualization
    fig, ax = plt.subplots(figsize=(12, 5))
    setup = PlottingSetup(
        fig=fig,
        ax=ax,
        title="ECG R-Peak Detection (Specialized Detector)",
        ylim=(-2, 2)
    )

    # 2. Initialize Data Source
    #data_source = create_ecg_data_source()
    data_source = create_ecg_with_temporary_anomaly(start=20.0, stop=25.0)
    
    # 3. Configure Feature Deriver (R-Peak Detection)
    # Sampling frequency set to 360Hz, typical for medical ECG devices.
    hr_deriver = HRFeatureDeriver(
        fs=360.0,
        min_rr_sec=0.2,      # Minimum RR interval (300 bpm limit)
        threshold_factor=0.7 # Sensitivity of the detection algorithm
    )
    # 4. configure detector  
    detector = HeartRateAnomalyDetector(
        threshold_std=3.0,       # Alert if HR deviates > 3 std devs from baseline
        warmup_beats=15,         # Learn baseline from first 15 beats
        confirmation_count=3,    # Require 3 consecutive outliers to alert
        recovery_count=5,        # Require 5 normal beats to clear alert
        baseline_adaptation=0.0  # Fixed baseline (no adaptation)
        )
    
    
    # 5. Configure Renderer
    renderer = VerticalLineRenderer(
        line_color='black',
        vline_color='red',
        vline_style='--',      # Dashed line
        vline_width=2.0,
        signal_label='ECG',
        vline_label='Anomaly',
        title_template='Heart Rate: {feature:.1f} bpm'
    )
    # 6. Initialize and Start Simulator
    sim = StreamingSimulator(
        plotting_setup=setup,
        feature_deriver=hr_deriver,
        change_point_detector=detector,
        renderer=renderer,
        data_source=data_source,
        window_duration_sec=5.0,  # Show last 5 seconds
        max_history=5000,         # Memory buffer limit
        interval_ms=30            # Update frequency (33Hz)
    )
    
    sim.start()

if __name__ == "__main__":
    run_rpeak_example()