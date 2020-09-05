#!/usr/local/bin/python3

from change_point_detectors import Detector
import constants
import numpy as np


class DeterministicSlidingWindow(Detector):
    def __init__(self):
        print("Initializing " + self.__class__.__name__ + " change point detector...")
        self._afr = np.array([])
        Detector.__init__(self, self.__class__.__name__)

    def detect_infant_mortality_end(self, data):
        self._afr = np.append(self._afr, data['cum_afr'].values)

        if len(self._afr) < constants.AGE_EXEMPT_FROM_STABLE_STATE:
            return -1

        if max(self._afr[(len(self._afr) - constants.MIN_SEGMENT_DAYS):(len(self._afr) - 1)]) - min(
                self._afr[(len(self._afr) - constants.MIN_SEGMENT_DAYS):(len(self._afr) - 1)]) <= \
                constants.AFR_DIFF_THRESHOLD:
            stable_state_start = len(self._afr)
            stable_state_afr = max(self._afr[(len(self._afr) - constants.MIN_SEGMENT_DAYS):(len(self._afr) - 1)])
            self._afr = np.array([])
            return (stable_state_start, stable_state_afr)
        return -1

    def detect_old_age_start(self, data, stable_state_start, stable_state_afr):
        self._afr = np.append(self._afr, data['cum_afr'].values)

        if len(self._afr) <= constants.MIN_SEGMENT_DAYS * 2:  # FIXME: this needs to be understood well
            return -1

        if max(data['cum_afr'].values) > stable_state_afr:
            return stable_state_start + len(self._afr)
        return -1
