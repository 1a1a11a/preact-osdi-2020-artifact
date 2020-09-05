#!/usr/local/bin/python3

from abc import ABC, abstractmethod
import constants
import logging


class FaultToleranceSchemes(ABC):
    def __init__(self, concrete_class_name):
        logging.log(constants.LOG_LEVEL_CONFIG, concrete_class_name + " fault tolerance initialized.")

    @abstractmethod
    def calculate_mttdl(self, afr, rgroup):
        pass

    @abstractmethod
    def get_stable_state_scheme(self, afr):
        pass
