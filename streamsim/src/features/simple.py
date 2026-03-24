"""
Simple Feature Deriver for Streaming Data

This module provides a minimal feature derivation class that implements the
`StreamingFeatureDeriver` interface. It serves as a passthrough component,
treating raw samples directly as feature values without transformation.

This class is useful for:
    - Testing and debugging streaming pipelines
    - Scenarios where raw signal values are the desired features
    - As a template for implementing more complex feature derivers

Dependencies:
    - streamsim.src.core.interfaces.StreamingFeatureDeriver: Base interface

Author: F.Feenstra

"""
from streamsim.src.core.interfaces import StreamingFeatureDeriver


class SimpleFeature(StreamingFeatureDeriver):
    def __init__(self):
        self.value = None

    def add_sample(self, sample, timestamp=None):
        self.value = sample

    def get_feature(self):
        return self.value