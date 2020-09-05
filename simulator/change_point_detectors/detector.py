#!/usr/local/bin/python3

from abc import ABC, abstractmethod
import constants
import logging


class Detector(ABC):
    def __init__(self, concrete_class_name):
        logging.log(constants.LOG_LEVEL_CONFIG, concrete_class_name + " change point detector initialized.")

    @abstractmethod
    def detect_infant_mortality_end(self, data):
        pass

    @abstractmethod
    def detect_old_age_start(self, data, stable_state_start, stable_state_afr, current_age):
        pass
