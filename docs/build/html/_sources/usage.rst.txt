Usage
=====

This guide explains how to build custom streaming pipelines with StreamSim. You'll learn how to create your own data sources, feature derivers, detectors, and renderers.

Building a Custom Pipeline
--------------------------

StreamSim uses a **producer-consumer architecture** where you connect pluggable components together. The main entry point is the ``StreamingSimulator`` class.

Basic Pipeline Setup
~~~~~~~~~~~~~~~~~~~~

Here's a minimal example of creating a custom pipeline:

.. code-block:: python

   from streamsim.src.core.simulator import StreamingSimulator
   from streamsim.src.core.config import PlottingSetup
   import matplotlib.pyplot as plt

   # 1. Setup visualization
   fig, ax = plt.subplots(figsize=(12, 5))
   setup = PlottingSetup(
       fig=fig,
       ax=ax,
       title="My Custom Signal",
       ylim=(-2, 2)
   )

   # 2. Create your components (see below for implementation details)
   deriver = MyFeatureDeriver()
   detector = MyDetector()
   renderer = MyRenderer(
       line_color='blue',
       marker_style='ro',
       title_template="Latest Value: {feature:.4f}"
   )

   # 3. Create a custom data source
   def my_data_source():
       """Generator that yields (sample, timestamp) tuples."""
       import time
       import numpy as np
       
       t = 0
       while True:
           sample = np.sin(t)
           yield sample, t
           t += 0.01
           time.sleep(0.01)

   # 4. Initialize and start the simulator
   sim = StreamingSimulator(
       plotting_setup=setup,
       feature_deriver=deriver,
       change_point_detector=detector,
       renderer=renderer,
       data_source=my_data_source,
       window_duration_sec=5.0,
       interval_ms=50
   )
   sim.start()

   # Keep the plot window open
   plt.show()

Understanding the Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``StreamingSimulator`` accepts the following key parameters:

*   **plotting_setup**: A ``PlottingSetup`` object containing the Matplotlib figure and axis.
*   **feature_deriver**: An instance of ``StreamingFeatureDeriver`` to extract features from raw data.
*   **change_point_detector**: An instance of ``StreamingChangePointDetector`` to identify anomalies.
*   **renderer**: An instance of ``StreamingRenderer`` to visualize the data stream.
*   **data_source**: A generator function yielding ``(sample, timestamp)`` tuples.
*   **window_duration_sec**: How many seconds of data to display at once.
*   **interval_ms**: Refresh interval for the animation in milliseconds.

Implementing Custom Components
------------------------------

To extend StreamSim, you need to implement the three core interfaces. Each component processes data in a streaming fashion.

Custom Feature Deriver
~~~~~~~~~~~~~~~~~~~~~~

A feature deriver extracts meaningful metrics from raw data samples.

.. code-block:: python

   from streamsim.src.core.interfaces import StreamingFeatureDeriver

   class MyFeatureDeriver(StreamingFeatureDeriver):
       """Extracts a custom feature from incoming samples."""

       def __init__(self):
           self._buffer = []
           self._feature_value = 0.0

       def add_sample(self, sample, timestamp):
           """
           Process a new sample.

           Args:
               sample: The raw data value.
               timestamp: The timestamp of the sample.
           """
           self._buffer.append(sample)
           # Keep buffer size manageable
           if len(self._buffer) > 100:
               self._buffer.pop(0)
           
           # Compute feature (e.g., moving average)
           self._feature_value = sum(self._buffer) / len(self._buffer)

       def get_feature(self):
           """Return the current feature value."""
           return self._feature_value

       def reset(self):
           """Clear internal state."""
           self._buffer.clear()
           self._feature_value = 0.0

**Key Methods:**

*   ``add_sample(sample, timestamp)``: Called for each incoming data point.
*   ``get_feature()``: Returns the computed feature value.
*   ``reset()``: Clears state when the simulation restarts.

Custom Detector
~~~~~~~~~~~~~~~

A detector monitors feature values and flags change points or anomalies.

.. code-block:: python

   from streamsim.src.core.interfaces import StreamingChangePointDetector

   class MyDetector(StreamingChangePointDetector):
       """Detects when feature values exceed a threshold."""

       def __init__(self, threshold=0.5):
           self._threshold = threshold
           self._drift_detected = False

       def update(self, feature_value):
           """
           Analyze the feature and determine if a change occurred.

           Args:
               feature_value: The current feature value from the deriver.

           Returns:
               bool: True if a change/anomaly is detected.
           """
           is_change = abs(feature_value) > self._threshold
           self._drift_detected = is_change
           return is_change

       @property
       def drift_detected(self):
           """Property to check if drift was detected."""
           return self._drift_detected

**Key Methods:**

*   ``update(feature_value)``: Called with each new feature value. Returns ``True`` if a change is detected.
*   ``drift_detected``: Property that exposes the current detection state.

Custom Renderer
~~~~~~~~~~~~~~~

A renderer visualizes the data stream, features, and detected events.

.. code-block:: python

   from streamsim.src.core.interfaces import StreamingRenderer
   import matplotlib.pyplot as plt

   class MyRenderer(StreamingRenderer):
       """Custom renderer with colored markers for anomalies."""

       def __init__(self, line_color='blue', marker_color='red'):
           self.line_color = line_color
           self.marker_color = marker_color
           self.line = None
           self.marker = None

       def initialize(self, ax):
           """
           Create plot elements.

           Args:
               ax: Matplotlib axis object.

           Returns:
               list: List of artist objects to track.
           """
           self.line, = ax.plot([], [], color=self.line_color, label='Signal')
           self.marker = ax.scatter([], [], color=self.marker_color, label='Anomaly')
           ax.legend()
           return [self.line, self.marker]

       def update(self, times, samples, features, change_points, window_duration_sec):
           """
           Update plot elements with new data.

           Args:
               times: Array of timestamps.
               samples: Array of raw sample values.
               features: Array of feature values.
               change_points: Boolean array indicating change points.
               window_duration_sec: Duration of the current window.

           Returns:
               list: Updated artist objects.
           """
           self.line.set_data(times, samples)
           
           # Mark change points
           if len(change_points) > 0:
               anomaly_times = times[change_points]
               anomaly_samples = samples[change_points]
               self.marker.set_offsets(list(zip(anomaly_times, anomaly_samples)))
           
           return [self.line, self.marker]

       def cleanup(self):
           """Release resources when the simulation ends."""
           pass

**Key Methods:**

*   ``initialize(ax)``: Creates initial plot elements. Must return a list of artists.
*   ``update(times, samples, features, change_points, window_duration_sec)``: Updates the plot with new data. Must return updated artists.
*   ``cleanup()``: Cleans up resources when the simulation stops.



Next Steps
----------

Now that you understand how to build custom pipelines, you can:

*   Explore the :doc:`modules` API reference for detailed interface specifications.
*   Study the built-in examples in ``streamsim/src/examples/`` for more patterns.
*   Contribute your own components back to the project!

