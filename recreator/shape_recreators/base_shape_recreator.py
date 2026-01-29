from abc import ABC, abstractmethod

class BaseShapeRecreator(ABC):
    @abstractmethod
    def can_recreate(self, shape_data):
        pass

    @abstractmethod
    def recreate(self, slide, shape_data):
        pass