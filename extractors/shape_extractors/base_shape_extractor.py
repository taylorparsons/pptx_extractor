from abc import ABC, abstractmethod

class BaseShapeExtractor(ABC):
    @abstractmethod
    def can_extract(self, shape):
        pass

    @abstractmethod
    def extract(self, shape):
        pass