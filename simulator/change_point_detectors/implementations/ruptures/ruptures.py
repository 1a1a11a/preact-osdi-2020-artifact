#!/usr/local/bin/python3

from change_point_detectors import Detector
import constants
# import ruptures as rpt
import change_point_detectors.implementations.ruptures as rpt
import numpy as np
import logging
import math
import common


class Ruptures(Detector):
    def __init__(self):
        logging.log(constants.LOG_LEVEL_CONFIG, "Initializing " + self.__class__.__name__ + " change point detector...")
        self._afr = np.array([])
        self._pad = 0
        Detector.__init__(self, self.__class__.__name__)

    def __del__(self):
        del self._afr
        self._afr = np.array([])

    def detect_infant_mortality_end(self, data, today=None, raw_data_csv=None):
        self._afr = data
        if len(self._afr) < constants.AGE_EXEMPT_FROM_STABLE_STATE:
            return -1

        self._afr = data[constants.HYSTERESIS_SLIDING_WINDOW:]

        # note that the AFRs are actually fed into the change point detector in reverse order.
        algo = rpt.Window(width=constants.MIN_SEGMENT_DAYS, min_size=constants.MIN_SEGMENT_DAYS, model="normal").fit(
            self._afr[::-1])
        starts = algo.predict(pen=3)
        for s in starts:
            if raw_data_csv["disk_days"][len(self._afr) + constants.HYSTERESIS_SLIDING_WINDOW - s] >= \
                    constants.MIN_SAMPLE_SIZE and len(self._afr) + \
                    constants.HYSTERESIS_SLIDING_WINDOW - s >= constants.AGE_EXEMPT_FROM_STABLE_STATE - 1:
                stable_state_start = max((len(self._afr) + constants.HYSTERESIS_SLIDING_WINDOW) - s,
                                         constants.AGE_EXEMPT_FROM_STABLE_STATE) - 1
                stable_state_afr = self._afr[len(self._afr) - s - 1]
                return stable_state_start, stable_state_afr

        return -1

    def detect_old_age_start(self, data, stable_state_start, stable_state_afr, current_age, raw_data_csv=None, min_sample=constants.MIN_SAMPLE_SIZE):
        if data >= stable_state_afr and raw_data_csv["disk_days"][current_age] > (min_sample / 2):
            return current_age

        return -1
