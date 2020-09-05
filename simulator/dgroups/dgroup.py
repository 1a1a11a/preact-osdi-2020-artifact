#!/usr/local/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import constants
import datetime
import os
import logging
import matplotlib
from shutil import copyfile

import sys
sys.path.append("datasets")
sys.path.append("anomalies")
sys.path.append("change_points")
sys.path.append("dgroups")
sys.path.append("redundancy_schemes")
sys.path.append("deployments")

from datasets import Backblaze
from anomaly_detectors.implementations.kinesis_rrcf import Kinesis_RRCF
from anomaly_detectors.implementations.rrcf import RRCF
# from change_points import Beatlex
from change_point_detectors import Ruptures
from change_point_detectors import Francisco
from change_point_detectors import ChangePy
from change_point_detectors import DeterministicSlidingWindow
from redundancy_schemes import MDS

import common
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker
import copy
import properties

# matplotlib.rcParams.update({'font.size': 18})
# matplotlib.rcParams.update({'font.size': 22})
matplotlib.rcParams['axes.xmargin'] = 0


class ChangePointDetails:
    def __init__(self, type, mean_afr, disk_days, failures,
        confident_afr, age_of_change, date_of_change, rgroup):
        '''Data class containing all the change points that were encountered
        for a given Dgroup. We want to maintain this list as a part of the
        Dgroup to see the different change points it went through in its life.

        :param type: RUp or RDn change point
        :param mean_afr: the mean AFR value
        :param confident_afr: the 99.9% confident AFR value
        :param age_of_change: the age at which the change point has occurred
        :param date_of_change:  date at which the change point has been detected
        :param rgroup: the rgroup suggested because of this change
        '''
        self.type = type
        self.mean_afr = mean_afr
        self.disk_days = disk_days
        self.failures = failures
        self.tailoring_afr = confident_afr
        self.age_of_change = age_of_change
        self.date_of_change = date_of_change
        self.rgroup = rgroup


class DGroup:
    def __init__(self, name, capacity=0, dataset=None, type=None):
        # Dataset handler
        self._d = dataset

        # Name of the Dgroup
        self.name = name

        # Capacity of the disk in TBs
        self.capacity = capacity

        # Deployment type of Dgroup (default = Trickle)
        self.deployment_type = type
        self.deployment_str = "trickle"
        if self.deployment_type == constants.DeploymentType.STEP:
            self.deployment_str = "step"

        # This df holds the instantenous AFRs
        # (sliding window over the past 30 days)
        self.afr_df = np.array([], dtype=[('days', 'int32'),
                                          ('afr', 'float64'),
                                          ('disk_days', 'int32'),
                                          ('num_failures', 'int32')])

        # Instantenous AFRs (sliding window over the past 30 days) as an array
        self.afr_array = np.zeros(1)

        # This df holds the cumulative AFRs of all disks
        self.cum_afr_df = np.array([], dtype=[('days', 'int32'),
                                              ('afr', 'float64'),
                                              ('disk_days', 'int32'),
                                              ('num_failures', 'int32')])

        # Cumulative AFRs of all disks
        self.cum_afr_array = np.zeros(1)

        # Rgroup being used for latest phase
        # of useful life (initialized to default)
        self.latest_rgroup = common.rgroups[str(
            constants.DEFAULT_REDUNDANCY_SCHEME)]

        # Max age of disk seen so far
        self.max_age = -1

        # Current age of disk
        self.current_age = -1

        # Current AFR of latest current age
        self.current_afr = -1.0

        # Dataframes that contain the data from
        # pre-processed CSV files for tracking daily AFRs
        self._df_map = dict()
        self._df = None

        # Dataframes that contain the data from
        # pre-processed CSV files for tracking daily AFRs for all disks
        self._cum_df_map = dict()
        self._cum_df = None

        # Change point detector that will help in detecting end of infancy.
        self._change_point_detector = eval(constants.CHANGE_POINT_DETECTOR)()

        # The encoding scheme to test with (MDS, etc.)
        self._fault_tolerance_scheme = eval(constants.REDUNDANCY_SCHEMES)()

        # The early warning system to use for
        # checking when to perform RUp transitions
        self._early_warning_system = eval(constants.REDUNDANCY_SCHEMES)()

        # Minimum sample size (different for
        # trickle deployments vs step deployments)
        self.min_sample_size = self._d.min_sample_size

        # List of change points the Dgroup has experienced
        self.cp_list = list()

        # Details of the latest change point
        self.latest_cp = None

        # Latest RDn change point
        self.latest_rdn_cp = None
        self.rdn_cp_list = list()

        # Latest RUp change point
        self.latest_rup_cp = None
        self.rup_cp_list = list()

        # Max afr observed and the age at which it was observed
        self.max_afr = -1.0
        self.max_afr_age = -1

        # Latest date when AFR curve was revised
        self.latest_afr_curve_revision = None

        # The age for which we had at least min_sample worth of disks.
        self.min_sample_age = -1
        self.latest_min_sample_age_revision = None

        # Legacy variables to be removed
        self.has_observed_mulligan = True

        # Latest step start date
        self.latest_step_start_date = None

        # transition tuples: (age_of_change, tolerated AFR)
        self.transition_tuples = list()

        self.transition_afr_array = np.zeros(1)

        self.transition_curves = dict()
        self.transition_num = 0

    def reset_counters(self, current_age=0):
        self.current_age = current_age
        self.afr_array = np.zeros(self.current_age + 1)
        self.cum_afr_array = np.zeros(self.current_age + 1)

    def _calculate_afr(self, disk_days, failures):
        return (float(failures) / disk_days) * 365 * 100

    def _calculate_slope(self, afr, window_size=15):
        """Calculates the slope of an afr curve."""
        # Define custom window function.
        def custom_window(arr):
            half_width = arr.shape[0] / 2
            weights = np.fromfunction(
                lambda i: 1 - (i - half_width)**2 / (half_width + 1)**2,
                arr.shape
            )
            return np.average(arr, weights=weights)

        slope = afr \
            .diff() \
            .fillna(0) \
            .rolling(window_size, min_periods=1, center=True) \
            .apply(custom_window, raw=True)
        return slope

    def _get_more_data(self, today=None, cumulative=False):
        logging.debug("Processing age %s", str(self.current_age))

        if today not in self._df_map:
            if os.path.exists(self._d.csv_path_prefix + "/" +
                              common.disk_shortname_map[self.name] + "/" +
                              today + ".parquet") is False:
                # Coming to this point means that all the canary / first step
                # drives are decommissioned. So now we now switch over to
                # the overall disk AFR curve to help us make decisions
                # (instead of just the canaries).
                self._df_map[today] = pd.read_parquet(
                    self._d.csv_cum_path_prefix + "/" +
                    common.disk_shortname_map[self.name] + "/" +
                    today + ".parquet")
            else:
                self._df_map[today] = pd.read_parquet(
                    self._d.csv_path_prefix + "/" +
                    common.disk_shortname_map[self.name] + "/" +
                    today + ".parquet")

        if today not in self._cum_df_map:
            self._cum_df_map[today] = pd.read_parquet(
                self._d.csv_cum_path_prefix + "/" +
                common.disk_shortname_map[self.name] + "/" + today + ".parquet")

        self._df = self._df_map[today]
        if cumulative:
            self._df = self._cum_df_map[today]

        self._cum_df = self._cum_df_map[today]

        # If you are trying to access age beyond today's max age, return False
        if self.current_age >= len(self._df):
            return False

        if self.current_age < constants.HYSTERESIS_SLIDING_WINDOW:
            self.current_afr = 0.0
        else:
            self.current_afr = self._calculate_afr(
                self._df["disk_days_window"][self.current_age],
                self._df["failures_window"][self.current_age])

        self.afr_array[self.current_age] = self.current_afr

        if self.max_afr < self.current_afr:
            self.max_afr = self.current_afr
            self.max_afr_age = self.current_age

        self.cum_afr_array[self.current_age] = self._calculate_afr(
            self._cum_df["disk_days_window"][self.current_age],
            self._cum_df["failures_window"][self.current_age])

        if self._df['disk_days'][self.current_age] >= constants.MIN_SAMPLE_SIZE:
            self.min_sample_age = self.current_age
        self.latest_min_sample_age_revision = today

        # Order of the following statements is important
        self.current_age += 1

        if len(self.afr_array) == self.current_age:
            self.afr_array = np.append(self.afr_array, [0.0])

        if len(self.cum_afr_array) == self.current_age:
            self.cum_afr_array = np.append(self.cum_afr_array, [0.0])

        return True

    def revise_afr_curve(self, today=None, from_age=-1, cumulative=False, hard_reset=False):
        '''Function to revise AFR curve.

        :param today: the date on which to revise AFR
        :param from_age: revise the AFR curve beyond a
        specific age (to expedite simulation)
        :return:
        '''
        rdn_performed = False
        rup_performed = False

        if hard_reset:
            self.latest_rup_cp = None
            self.latest_rdn_cp = None
            self.cp_list = list()

        if (self.latest_rup_cp is not None) and (
            self.latest_rup_cp.rgroup == common.rgroups[str(
            constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]):
            return rdn_performed, rup_performed

        if from_age >= 0:
            self.reset_counters(from_age)

        while self._has_more_data(today=today, cumulative=cumulative):
            if self.latest_rdn_cp is None:
                rdn_performed = self.can_perform_rdn_transition(today=today)
            elif (self.latest_rup_cp is None) or (
                self.latest_rup_cp.rgroup != common.rgroups[str(
                constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]):
                rup_performed = self.is_rup_transition_needed(today=today)

        self.latest_afr_curve_revision = today
        return rdn_performed, rup_performed

    def _has_more_data(self, today=None, cumulative=False):
        '''Helper function for getting more data from Dgroup.

        :param today: Date for which to enquire for more data
        :return: True if more data exists, False otherwise
        '''
        return self._get_more_data(today=today, cumulative=cumulative)

    def can_perform_rdn_transition(self, today=None):
        '''Detect the end of infant mortality using a change-point detector.

        :param today: The date on which you want to evaluate if infancy ended.
        :return: bool (True if infancy ended (by setting the Rgroup chosen),
        False if infancy didn't end)
        '''

        if (self.current_age < constants.HYSTERESIS_SLIDING_WINDOW) or (
            self._df_map[today]["disk_days"][
                constants.AGE_EXEMPT_FROM_STABLE_STATE] < self.min_sample_size):
            return False

        # Ask the change-point detector if infancy has ended
        res = self._change_point_detector.detect_infant_mortality_end(
            self.afr_array, today=today, raw_data_csv=self._df_map[today])

        if res == -1:
            # This means that the change-point detector hasn't detected end
            # of infancy. Return false.
            return False

        observed_mean_afr = float(res[1])

        # Check if end of infancy has already been detected. If it has, then
        # subsequent RDn checks should only check if the mean AFR has overshot
        # the tolerated AFR of the selected redundancy scheme. If not, then we
        # keep using the same scheme. If it has, then we need to re-encode all
        # disks that are beyond infancy to a more conservative redundancy
        # scheme. The reason we compare against observed AFR and not 99.9%
        # confident AFR of observed + buffer is because the initial scheme was
        # chosen on the basis of observed + buffer + 99.9% confidence precisely
        # to accommodate fluctuations.

        if (self.latest_rdn_cp is not None) and (
            observed_mean_afr < self.latest_rdn_cp.rgroup.tolerable_afr):
            return False

        # Reaching here means that the change-point detector has detected that
        # an RDn transition can be done.
        # Let's process the resultant AFR and Rgroup.
        last_rgroup_end_day = int(res[0])
        observed_confident_afr = common.get_confident_instantaneous_afr(
            observed_mean_afr, self._df_map[today]["disk_days_window"][
                last_rgroup_end_day],
            self._df_map[today]["failures_window"][last_rgroup_end_day])
        tailoring_afr = observed_confident_afr * (1 + constants.AFR_BUFFER)
        if self.latest_rdn_cp is None:
            prev_rdn_rgroup = self.latest_rgroup
        else:
            prev_rdn_rgroup = self.latest_rdn_cp.rgroup
        rg = self._fault_tolerance_scheme.get_stable_state_scheme(
            tailoring_afr, prev_rgroup=prev_rdn_rgroup)

        if rg == self.latest_rgroup:
            # If the detected Rgroup transition matches the Rgroup we are
            # currently in, return False since we don't need to transition to
            # anything.
            return False

        if (len(self.cp_list) > 0) and (
            self.cp_list[-1].date_of_change == today):
            logging.info("Dgroup " + self.name + " RDn'd from " +
                  self.cp_list[-1].rgroup.name + " to " + rg.name +
                  " on " + today + " for age = " + str(last_rgroup_end_day) +
                  " with tailoring AFR = " + str(tailoring_afr) +
                  ". Replacing " + self.cp_list[-1].rgroup.name +
                  " since it was transitioned to on the same day.")
            del self.cp_list[-1]
        else:
            logging.info("Dgroup " + self.name + " RDn'd from " +
                  self.latest_rgroup.name + " to " + rg.name + " on " +
                  today + " for age = " + str(last_rgroup_end_day) +
                  " with tailoring AFR = " + str(tailoring_afr)
                  + " and tolerated AFR = " + str(rg.tolerable_afr))

        self.latest_rgroup = rg

        # Create a change point details class and add it to the list
        # of observed change points..
        self.latest_cp = ChangePointDetails(
            constants.RDN_CHANGE, observed_mean_afr,
            self._df_map[today]["disk_days_window"][last_rgroup_end_day],
            self._df_map[today]["failures_window"][last_rgroup_end_day],
            tailoring_afr, self.current_age - 1, today, rg)

        self.transition_tuples.append((self.current_age,
                                       rg.tolerable_afr, today))

        self.latest_rdn_cp = self.latest_cp
        self.cp_list.append(self.latest_cp)
        self.rdn_cp_list.append(self.latest_cp)

        self.transition_curves[self.transition_num] = copy.deepcopy(
            self.afr_array)
        self.transition_num += 1

        return True

    def is_rup_transition_needed(self, today=None):
        '''This function detects if the observed AFR on a give date crosses
         some notion of AFR threshold causing us to perform an RUp transition.

        :param today: date on which we need to test if a phase of life is
         being crossed.
        :return:
        '''

        if (self.current_age < constants.HYSTERESIS_SLIDING_WINDOW) or (
            self._df_map[today]["disk_days"][self.current_age - 1] <
            self.min_sample_size) or (
            self.current_age <= self.latest_rdn_cp.age_of_change):
            return False

        # Reaching here means that the disks are at risk and we need to
        # start RUp-ing them in the background.
        last_rgroup_end_day = self.current_age - 1
        observed_mean_afr = self.current_afr
        future_tailoring_afr = -1.0

        res = False
        if (observed_mean_afr >= self.latest_rgroup.tolerable_afr *
            constants.AFR_PHASE_TRANSITION_THRESHOLD):
            # check the slope from the past few days and project in the future
            # to decide what AFR you should keep as the tolerating AFR.
            slope = self._calculate_slope(pd.DataFrame(self.afr_array[:-1]))
            future_tailoring_afr = self.latest_rgroup.tolerable_afr + (
                constants.AFR_PROJECTION_WINDOW * np.average(
                slope[-constants.SLOPE_AVERAGING_WINDOW:]))

            res = True

        if res is False:
            # This means disks aren't at risk, and therefore no
            # action needs to be taken.
            return False

        # Reaching here means that the change-point detector has detected
        # that an RUp transition is required.
        if constants.MULTI_PHASE is False:
            rg = common.rgroups[str(
                constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]
        else:
            if self.latest_rup_cp is None:
                prev_rup_rgroup = self.latest_rgroup
            else:
                prev_rup_rgroup = self.latest_rup_cp.rgroup
            rg = self._fault_tolerance_scheme.get_stable_state_scheme(
                common.get_confident_instantaneous_afr(
                future_tailoring_afr,
                self._df_map[today]["disk_days_window"][self.current_age - 1],
                self._df_map[today]["failures_window"][self.current_age - 1]),
                prev_rgroup=prev_rup_rgroup)
            if rg == common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]:
                rg = common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) +
                                    "_wearout"]

        if rg == self.latest_rgroup:
            # If the detected Rgroup transition matches the Rgroup we are
            # currently in, return False since we don't need to transition
            # to anything.
            return False

        # It may be possible that on the same day, the Rgroup was revised
        # multiple times. If that's the case, then only retain the last Rgroup.
        if (len(self.cp_list) > 0) and (
            self.cp_list[-1].date_of_change == today):
            logging.info("Dgroup " + self.name + " RUp'd from " +
                  self.cp_list[-1].rgroup.name + " to " + rg.name + " on " +
                  today + " for age = " + str(last_rgroup_end_day) +
                  ". Replacing " + self.cp_list[-1].rgroup.name +
                  " since it was transitioned to on the same day."  +
                  " Observed AFR = " + str(observed_mean_afr) +
                  ", future tailoring AFR = " + str(future_tailoring_afr) +
                  " and tolerated AFR = " + str(rg.tolerable_afr))
            del self.cp_list[-1]
        else:
            logging.info("Dgroup " + self.name + " RUp'd from " +
                  self.latest_rgroup.name + " to " +
                  rg.name + " on " + today + " for age = " +
                  str(last_rgroup_end_day) +
                  " Observed AFR = " + str(observed_mean_afr) +
                  ", future tailoring AFR = " + str(future_tailoring_afr) +
                  " and tolerated AFR = " + str(rg.tolerable_afr))

        self.latest_rgroup = rg

        # Create a change point details class and add it to the list
        # of observed change points.
        self.latest_cp = ChangePointDetails(
            constants.RUP_CHANGE, observed_mean_afr,
            self._df_map[today]["disk_days_window"][last_rgroup_end_day],
            self._df_map[today]["failures_window"][last_rgroup_end_day],
            self.latest_rgroup.tolerable_afr, self.current_age - 1, today, rg)
        self.transition_tuples.append((self.current_age, rg.tolerable_afr, today))
        self.latest_rup_cp = self.latest_cp
        self.cp_list.append(self.latest_cp)
        self.rup_cp_list.append(self.latest_cp)

        self.transition_curves[self.transition_num] = copy.deepcopy(
            self.afr_array)
        self.transition_num += 1

        return True

    def plot_afr(self, folder, revision_number=1, fig=None, axarr=None):
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        matplotlib.rcParams['figure.figsize'] = 3.5, 3
        matplotlib.rcParams.update({'font.size': 10})
        os.makedirs(common.results_dir + "/plots" + "/" + folder, exist_ok=True)
        copyfile("constants.py", common.results_dir + "/plots" + "/" +
                 folder + "/constants.py")

        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        all_dgroups = ', '.join("'{0}'".format(dg) for dg in list([self.name]))
        all_disks_deployment_dates = self._d.get_all_deployment_dates(
            dgroups=all_dgroups)
        startdate = all_disks_deployment_dates[0]
        enddate = constants.END_DATE
        dt_range = common.daterange(
            datetime.datetime.strptime(startdate, "%Y-%m-%d"),
            datetime.datetime.strptime(enddate, "%Y-%m-%d"))
        day_wise_dt_range = list()
        dates_analyzed = 0
        afr_array = list()
        days_to_subtract = common.subtract_days[common.cluster][self.name]

        for dt in dt_range:
            day_wise_dt_range.append(dt)
            if dates_analyzed < 1:
                afr_array.append(0.0)
                dates_analyzed += 1
                continue
            cur_date_str = dt.strftime("%Y-%m-%d")
            logging.info("Processing date %s...", cur_date_str)

            if cur_date_str not in self._df_map:
                if os.path.exists(self._d.csv_cum_path_prefix + "/" +
                                  common.disk_shortname_map[self.name] + "/" +
                                  cur_date_str + ".parquet") is False:
                    self._df_map[cur_date_str] = pd.read_parquet(
                        self._d.csv_cum_path_prefix + "/" +
                        common.disk_shortname_map[self.name] + "/" +
                        cur_date_str + ".parquet")
                else:
                    self._df_map[cur_date_str] = pd.read_parquet(
                        self._d.csv_cum_path_prefix + "/" +
                        common.disk_shortname_map[self.name] + "/" +
                        cur_date_str + ".parquet")

            afr_array.append(self._calculate_afr(
                self._df_map[cur_date_str]["disk_days_window"][len(
                    self._df_map[cur_date_str]["disk_days_window"]
                ) - min(dates_analyzed, days_to_subtract)],
                self._df_map[cur_date_str]["failures_window"][len(
                    self._df_map[cur_date_str]["failures_window"]
                ) - min(dates_analyzed, days_to_subtract)]))

            dates_analyzed += 1

        ax1.plot_date(day_wise_dt_range, afr_array, 'k', lw=1.5)
        ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(ticker.MultipleLocator(90))
        if len(day_wise_dt_range) > 90*4:
            ax1.xaxis.set_major_locator(ticker.MultipleLocator(365))
        ax1.tick_params(axis='x', labelsize=12, labelrotation=20)
        ax1.tick_params(axis='y', labelsize=12)
        ax1.set_ylim(0, constants.DEFAULT_AFR)

        i = 0
        for tup in self.transition_tuples:
            tolerable_afr = tup[1]
            age_of_change = tup[0]
            logging.info("Transition for age: " + str(age_of_change) +
                  " for tolerable_afr: " + str(tolerable_afr))
            if i == 0:
                x_idx_start = 0
                x_idx_end = day_wise_dt_range.index(
                    datetime.datetime.strptime(tup[2], "%Y-%m-%d"))
                y_arr = [float(constants.DEFAULT_AFR)] * (x_idx_end -
                                                          x_idx_start)
                x_arr = day_wise_dt_range[x_idx_start:x_idx_end]
                ax1.fill_between(y1=y_arr, x=x_arr,
                                 facecolor="gray", alpha=0.25)

            x_idx_start = day_wise_dt_range.index(
                datetime.datetime.strptime(tup[2], "%Y-%m-%d"))
            if i == len(self.transition_tuples) - 1:
                if self.deployment_type == constants.DeploymentType.TRICKLE:
                    x_idx_end = len(day_wise_dt_range) - 1
                else:
                    x_idx_end = len(day_wise_dt_range) - 1
            else:
                x_idx_end = day_wise_dt_range.index(datetime.datetime.strptime(
                    self.transition_tuples[i + 1][2], "%Y-%m-%d"))

            y_arr = [float(tolerable_afr)] * (x_idx_end - x_idx_start)
            x_arr = day_wise_dt_range[x_idx_start:x_idx_end]
            ax1.fill_between(y1=y_arr, x=x_arr,
                             facecolor="gray", alpha=0.25)

            y_arr = [float(tolerable_afr *
                           constants.AFR_PHASE_TRANSITION_THRESHOLD)] * (
                x_idx_end - x_idx_start)
            ax1.plot(x_arr, y_arr, ls="--", color="r", alpha=0.8)

            if (self.deployment_type == constants.DeploymentType.TRICKLE) and (
                i == len(self.transition_tuples) - 1):
                x_idx_start = self.min_sample_age
                x_idx_end = len(day_wise_dt_range) - 1
                y_arr = [float(constants.DEFAULT_AFR)] * (x_idx_end -
                                                          x_idx_start)
                x_arr = day_wise_dt_range[x_idx_start:x_idx_end]

            i += 1

        self.revise_afr_curve(today=constants.END_DATE, from_age=0,
                              cumulative=True, hard_reset=True)
        afr_array = common.subtract_days[common.cluster][self.name] * [0.0]
        for afr in self.afr_array:
            afr_array.append(afr)

        if self.deployment_type == constants.DeploymentType.TRICKLE:
            which_disks = 'canaries'
        else:
            which_disks = 'first step'
        legend_elements = [
            Line2D([0], [0], color='k', lw=1.5, ls='-',
                   label='AFR of ' + which_disks),
            Line2D([0], [0], color='r', lw=2, ls='--', label='Threshold-AFR'),
            Patch(facecolor='black', edgecolor='gray',
                  label='Tolerated-AFR region', alpha=0.25)]

        plt.legend(handles=legend_elements, frameon=False, fontsize=12,
                   loc='upper left')
        plt.ylabel("AFR (%)", fontsize=14)
        plt.tight_layout()
        fig.savefig(common.results_dir + "/" + self.name + ".pdf", pad_inches=0)
        return fig, axarr

    def plot_age_afr(self, folder, revision_number=1, fig=None, axarr=None):
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        matplotlib.rcParams['figure.figsize'] = 3.5, 3
        matplotlib.rcParams.update({'font.size': 10})
        os.makedirs("results/" + today, exist_ok=True)
        os.makedirs("results/" + today + "/" + common.cluster, exist_ok=True)
        os.makedirs("results/" + today + "/" + common.cluster + "/" + folder,
                    exist_ok=True)
        copyfile("constants.py", "results/" + today + "/" + common.cluster +
                 "/" + folder + "/constants.py")

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.plot(range(0, len(self.afr_array) - 1),
                 self.afr_array[0:len(self.afr_array) - 1],
                 'k', label='AFR', lw=1)
        plt.ylabel("AFR (%)")
        plt.tight_layout()
        fig.savefig("results/" + self.name + ".pdf", pad_inches=0)
        return fig, axarr
