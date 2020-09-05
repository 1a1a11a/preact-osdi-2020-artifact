#!/usr/local/bin/python3

from abc import ABC, abstractmethod
import constants
import logging


class Dataset(ABC):
    """The dataset class that lets us fetch data for analysis."""

    def __init__(self, name):
        self.name = name
        self.min_sample_size = constants.MIN_SAMPLE_SIZE # change for step deployments
        logging.log(constants.LOG_LEVEL_CONFIG, name + " dataset initialized.")

    @abstractmethod
    def get_disks_in_memory(self):
        pass

    @abstractmethod
    def get_all_deployment_dates(self):
        pass

    @abstractmethod
    def get_disk_groups(self):
        pass
