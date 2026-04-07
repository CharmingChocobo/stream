Getting Started
===============

Welcome to **StreamSim**, a flexible, multi-threaded framework for real-time time-series visualization. This guide will help you install the library, run the built-in demos, and understand the core architecture.

What is StreamSim?
------------------

StreamSim provides a **producer-consumer architecture** designed for processing streaming data with:

*   **Real-time visualization** using Matplotlib animations.
*   **Pluggable components** for feature derivation, anomaly detection, and rendering.
*   **Thread-safe data flow** ensuring smooth communication between processing and rendering threads.
*   **Support for multiple signal types**, including ECG, sinusoidal waves, and custom generators.

Installation
------------

Follow these steps to set up your environment.

1. **Clone the Repository**

   .. code-block:: bash

      git clone https://github.com/fenna/stream.git
      cd stream

2. **Install Dependencies**

   Install the required Python packages:

   .. code-block:: bash

      pip install -r requirements.txt

   **Required Dependencies:**
   *   `numpy`: For numerical computations.
   *   `matplotlib`: For visualization and animations.

   **Optional Dependencies:**
   *   `wfdb`: Required only if you plan to load real ECG data from the MIT-BIH database.

Quick Start: Running Demos
--------------------------

StreamSim includes two ready-to-run examples to demonstrate its capabilities.

**ECG R-Peak Detection Demo**

This demo processes real ECG signals to detect R-peaks, calculate heart rate, and flag anomalies.

.. code-block:: bash

   python3 -m streamsim.src.examples.ecg_demo

**What you will see:**
*   Real-time ECG signal processing.
*   Dynamic heart rate calculation.
*   Vertical line markers indicating detected anomalies.
*   A dynamic title displaying the current heart rate.

**Sinus Wave Peak Detection Demo**

This demo showcases general-purpose peak detection on synthetic sinusoidal signals.

.. code-block:: bash

   python3 -m streamsim.src.examples.sinus_demo

**What you will see:**
*   General-purpose peak detection on synthetic signals.
*   Red dot markers highlighting detected local maxima.
*   Configurable signal frequency and sampling rate.

Architecture Overview
---------------------

StreamSim operates on a linear pipeline where data flows from a source through processing stages to a renderer.

.. code-block:: text

   ┌──────────────┐     ┌────────────────────┐     ┌──────────────────┐
   │ Data Source  │────▶│ Feature Deriver    │────▶│ Detector         │
   │ (ECG/Sinus)  │     │ (extracts HR/peaks)│     │ (flags anomalies)│
   └──────────────┘     └────────────────────┘     └──────────────────┘
                                                        │
                                                        ▼
                                                    ┌──────────────────┐
                                                    │ Simulator Queue  │
                                                    │ (thread-safe)    │
                                                    └──────────────────┘
                                                        │
                                                        ▼
                                                    ┌──────────────────┐
                                                    │ Renderer         │
                                                    │ (visualizes)     │
                                                    └──────────────────┘

**Key Components:**

1.  **Data Source**: Generates or loads time-series data (e.g., `ECGDataSource`, `SinusDataSource`).
2.  **Feature Deriver**: Extracts specific metrics from the raw data (e.g., Heart Rate, Local Maxima).
3.  **Detector**: Monitors features to identify change points or anomalies (e.g., `HRAnomalyDetector`).
4.  **Renderer**: Visualizes the data stream, features, and detected events using Matplotlib.

Next Steps
----------

Now that you have the basics down, you can explore further:

*   **Usage**: Learn how to build your own custom pipelines with ``StreamingSimulator``.
*   **Modules**: Dive into the API reference to understand the interfaces for ``StreamingFeatureDeriver``, ``StreamingChangePointDetector``, and ``StreamingRenderer``.
*   **Development**: Read the guide on how to implement your own custom components.

Ready to build your own pipeline? Head over to the :doc:`usage` page.