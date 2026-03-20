from streamsim.src.core.interfaces import StreamingFeatureDeriver


class SimpleFeature(StreamingFeatureDeriver):
    def __init__(self):
        self.value = None

    def add_sample(self, sample, timestamp=None):
        self.value = sample

    def get_feature(self):
        return self.value