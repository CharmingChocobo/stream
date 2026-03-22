"""Main streaming simulator with multi-threaded architecture."""

__author__ = "F.Feenstra"

import numpy as np
import threading
from typing import Optional, Any, List
import time
from queue import Queue, Empty
from typing import Callable, Optional, Tuple, List
from collections import deque
from streamsim.src.core.interfaces import StreamingFeatureDeriver, StreamingChangePointDetector, StreamingRenderer
from streamsim.src.core.config import PlottingSetup


class StreamingSimulator:
    """
    General framework for streaming time-series visualization.
    
    Provides multi-threaded architecture with pluggable components for
    feature extraction and change point detection.
    """
    
    def __init__(
        self,
        plotting_setup: PlottingSetup,
        feature_deriver: StreamingFeatureDeriver,
        change_point_detector: StreamingChangePointDetector,
        renderer: StreamingRenderer = None,
        data_source: Callable[[], Optional[Tuple[float, float]]] = None,
        window_duration_sec: float = 30.0,
        interval_ms: int = 50,
        max_history: int = 2000,
    ):
        self.plotting_setup = plotting_setup
        self.feature_deriver = feature_deriver
        self.change_point_detector = change_point_detector
        self.data_source = data_source
        self.window_duration_sec = window_duration_sec
        self.interval_ms = interval_ms
        self.max_history = max_history
        
        # Import here to avoid circular dependency
        from streamsim.src.renderers.matplotlib_line import MatplotlibLineRenderer
        self.renderer = renderer or MatplotlibLineRenderer()

        # Buffers (MAIN THREAD ONLY)
        self.sample_buffer = deque(maxlen=max_history)
        self.time_buffer = deque(maxlen=max_history)
        self.feature_buffer = deque(maxlen=max_history)
        self.change_point_times = deque(maxlen=max_history)

        # Queue (thread communication)
        self.queue = Queue(maxsize=10000)

        # State
        self.is_running = False
        self.animation = None
        self.processing_thread = None

    def _processing_loop(self) -> None:
        """Worker thread: processes data and feeds queues."""
    
        self.change_timestamps = []
        
        while self.is_running:
            sample_data = self.data_source()
            if sample_data is None:
                break

            timestamp = None
            try:
                sample, timestamp = sample_data
                self.feature_deriver.add_sample(sample, timestamp)
            except (ValueError, TypeError):
                sample = sample_data
                self.feature_deriver.add_sample(sample)

            feature = self.feature_deriver.get_feature()
            
            is_change = self.change_point_detector.update(feature)
            
            print(f"[Simulator] Feature={feature}, is_change={is_change}")
            
            if is_change:
                if not hasattr(self, '_anomaly_line_added') or not self._anomaly_line_added:
                    self.change_timestamps.append(timestamp)
                    self._anomaly_line_added = True
                    print(f"[Simulator] ADDED change point: t={timestamp:.2f}s")
            else:
                self._anomaly_line_added = False

            if not self.queue.full():
                self.queue.put({
                    "sample": sample,
                    "timestamp": timestamp,
                    "feature": feature,
                    "is_change": is_change,
                    "change_points": np.array(self.change_timestamps)
                })

            time.sleep(0.001)


    def _init_plot(self) -> List[Any]:
        """Initialize plot elements for animation."""
        artists = self.renderer.initialize(self.plotting_setup.ax)
        self.plotting_setup.configure()
        return artists
    

    def _update_plot(self, frame: int) -> List[Any]:
        """Main thread: Queue -> Buffer -> Render."""
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        
        # Track change points from queue
        change_points_list = []
        
        count = 0
        while count < 200:
            try:
                msg = self.queue.get_nowait()
            except Empty:
                break
            
            if msg.get("end"):
                self.is_running = False
                break

            self.sample_buffer.append(msg["sample"])
            self.time_buffer.append(msg["timestamp"])
            
            if msg["feature"] is not None:
                self.feature_buffer.append(msg["feature"])
            
            # Collect change points from queue message
            if "change_points" in msg and len(msg["change_points"]) > 0:
                change_points_list = list(msg["change_points"])
            
            count += 1

        if not self.time_buffer:
            return []

        times = np.fromiter(self.time_buffer, float)
        samples = np.fromiter(self.sample_buffer, float)
        features = np.fromiter(self.feature_buffer, float) if self.feature_buffer else np.array([])
        
        # FIX: Use actual change point timestamps, not features!
        cps = np.array(change_points_list) if change_points_list else np.array([])

        artists = self.renderer.update(times, samples, features, cps, self.window_duration_sec)
        
        latest = times[-1]
        if latest <= self.window_duration_sec:
            self.plotting_setup.ax.set_xlim(0, self.window_duration_sec)
        else:
            self.plotting_setup.ax.set_xlim(latest - self.window_duration_sec, latest)
        
        return artists


    def start(self) -> None:
        """Start the streaming simulation."""
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        
        self.is_running = True

        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self.processing_thread.start()

        self.animation = FuncAnimation(
            self.plotting_setup.fig,
            self._update_plot,
            init_func=self._init_plot,
            interval=self.interval_ms,
            blit=False,
            cache_frame_data=False
        )

        plt.show()


    def stop(self) -> None:
        """Stop the streaming simulation."""
        self.is_running = False

        if self.processing_thread:
            self.processing_thread.join(timeout=1)

        if self.animation:
            self.animation.event_source.stop()

        self.renderer.cleanup()