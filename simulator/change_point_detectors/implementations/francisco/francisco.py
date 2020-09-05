#!/usr/local/bin/python3

from change_point_detectors import Detector
import sys, os
import numpy as np
import scipy as sp
import pandas as pd
# import lifelines as ll
import logging
import constants

from scipy.stats import norm


class Francisco(Detector):
    def __init__(self):
        logging.log(constants.LOG_LEVEL_CONFIG, "Initializing " + self.__class__.__name__ + " change point detector...")
        self._afr = np.array([])
        # self._last_appended = 0
        self._pad = 0
        Detector.__init__(self, self.__class__.__name__)

    def __del__(self):
        del self._afr
        self._afr = np.array([])

    def detect_infant_mortality_end(self, data, today=None, raw_data_csv=None):
        total_disks = len(data)
        # print(data[data.censored == 0])
        # exit(0)
        failures = raw_data_csv[data.censored == 0]
        failure_times = np.sort(failures.age.values + 1)
        total_failures = len(failures)
        # print(str(total_failures))
        # print("in francisco = " + str(failures) + " " + str(failure_times) + " " + str(total_failures))

        likelihoods = np.zeros(total_failures)
        lams1 = np.zeros(total_failures)
        lams2 = np.zeros(total_failures)

        # Try every possible changepoint index.
        for changepoint_idx in range(total_failures):
            changepoint = changepoint_idx + 1

            # Calculate exposure time (disk days) before changepoint.
            failed_exposure_before = np.sum(failure_times[:changepoint])
            censored_exposure_before = (total_disks - changepoint) * failure_times[changepoint_idx]
            exposure_before = failed_exposure_before + censored_exposure_before

            # Calculate exposure time (disk days) after changepoint.
            failed_exposure_before = np.sum(failure_times[:changepoint])
            failed_exposure_after = np.sum(failure_times[changepoint:] - failure_times[changepoint_idx])
            censored_exposure_after = (total_disks - total_failures) * (failure_times[-1] - failure_times[changepoint_idx])
            exposure_after = failed_exposure_after + censored_exposure_after

            # Calculate lambdas.
            lam1 = changepoint / exposure_before
            lam2 = (total_failures - changepoint) / exposure_after

            # Calculate likelihood
            likelihoods[changepoint_idx] = \
                changepoint * np.log(lam1) \
                + (total_failures - changepoint) * np.log(lam2)

            lams1[changepoint_idx] = lam1
            lams2[changepoint_idx] = lam2

        # Choose the most likely changepoint.
        likely_changepoint = np.nanargmax(likelihoods)
        lam1 = lams1[likely_changepoint]
        lam2 = lams2[likely_changepoint]
        changepoint_age = failure_times[likely_changepoint]

        if changepoint_age > 0:
            return max(changepoint_age, constants.AGE_EXEMPT_FROM_STABLE_STATE), lam2, changepoint_age

        return -1

    def detect_old_age_start(self, data, stable_state_start, stable_state_afr, current_age, raw_data_csv=None):
        if data >= stable_state_afr and raw_data_csv.loc[current_age].disk_days > (constants.MIN_SAMPLE_SIZE / 2) and \
                current_age > stable_state_start:
            return current_age

        return -1
