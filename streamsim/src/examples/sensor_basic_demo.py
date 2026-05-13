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