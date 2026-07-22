# Core Module Interface definition
from abc import ABC, abstractmethod
from fastapi import APIRouter

class BaseModule(ABC):
    """
    Abstract Base Class for all OpenTerminal plugin modules.
    Any new feature (e.g. News, Forecast, Portfolio) must inherit from this class
    and register itself dynamically to the application during boot-up.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Lifecycle hook to initialize the module.
        Used to setup module resources, connect to databases, pre-seed tables,
        or register background event subscribers to the event bus.
        """
        pass
        
    @abstractmethod
    def register_routes(self) -> APIRouter:
        """
        Lifecycle hook to define and return the router structure for this module.
        The dynamic framework loader mounts these routes onto the main API gateway.
        """
        pass
