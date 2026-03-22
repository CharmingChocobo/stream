### project structure

```
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── interfaces.py      # Abstract base classes
│   ├── simulator.py       # StreamingSimulator
│   └── config.py          # PlottingSetup, configuration dataclasses
├── features/
│   ├── __init__.py
│   ├── simple.py          # SimpleFeatureDeriver
│   ├── local_maxima.py    # LocalMaximaDeriver
│   └── rpeak.py           # RPeakFeatureDeriver
├── detectors/
│   ├── __init__.py
│   ├── simple.py          # SimpleDetector
│   └── passthrough.py     # PeakPassThrough
├── renderers/
│   ├── __init__.py
│   ├── matplotlib_line.py # MatplotlibLineRenderer
│   └── rpeak.py           # RPeakRenderer
├── sources/
│   ├── __init__.py
│   └── ecg.py             # ECG_DataSource
└── examples/
    ├── __init__.py
    ├── sinus_demo.py      # run_sinus_example
    └── ecg_demo.py        # run_rpeak_example
```