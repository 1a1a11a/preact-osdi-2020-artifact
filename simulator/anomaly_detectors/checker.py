#!/usr/local/bin/python3

from abc import ABC, abstractmethod
import constants
import logging


class Checker(ABC):
    def __init__(self, concrete_class_name):
        logging.log(constants.LOG_LEVEL_CONFIG, concrete_class_name + " anomaly checker initialized.")

    @abstractmethod
    def get_anomaly_score(self, days, data, key):
        pass
