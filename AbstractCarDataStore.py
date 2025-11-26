__package__ = "AbstractCarDataStore"

from abc import ABC, abstractmethod

class AbstractCarDataStore(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def insertIntoRegionCodeTable(self, data: str) -> bool:
        pass

    @abstractmethod
    def insertOrUpdateVisitorsTable(self, data: str) -> bool:
        pass
