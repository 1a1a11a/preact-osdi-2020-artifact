#!/usr/local/bin/python3

from abc import ABC, abstractmethod, abstractproperty
import constants
import logging
import datetime
import common
import properties
import numpy as np
import math
import copy
from all_metrics import Metrics
from metrics.cluster_metrics import ClusterMetrics
from metrics.dgroup_metrics import DgroupMetrics
from metrics.rgroup_metrics import RgroupMetrics
from metrics.work import Work
from metrics.disk_category_metrics import DiskCategoryMetrics
from metrics.background_work import BackgroundWork


class TranscodingPolicy(ABC):
    def __init__(self, concrete_class_name, start_date, end_date):
        self.name = concrete_class_name
        self.num_running_disks = 0
        self.num_total_disks = 0
        self.num_failed_disks = 0
        self.num_decommissioned_disks = 0

        self.metrics = Metrics(self.name, (datetime.datetime.strptime(end_date, "%Y-%m-%d") -
                                           datetime.datetime.strptime(start_date, "%Y-%m-%d")).days + 1,
                               constants.CANARY, constants.ITERATIVE_CP)

        self.running_disks = dict()  # serial_number: (date, dgroup, rgroup, phase_of_life)
        self.failed_disks = dict()  # serial_number: (date, dgroup, rgroup, phase_of_life)
        self.decommissioned_disks = dict()  # serial_number: (date, dgroup, rgroup, phase_of_life)

        self.disks_viable_for_wearout = dict()  # serial_number: (date, reads, writes)
        self.disks_viable_for_useful_life = dict()  # serial_number: (date, rgroup, reads, writes)
        self.disks_viable_for_non_urgent_wearout = dict()  # serial_number: (date, reads, writes, convert_to_urgent_date)
        self.disks_viable_for_decommissioning = dict()  # serial_number: date

        self.disks_viable_for_useful_life_order = list()  # serial_number
        self.disks_viable_for_wearout_order = list()  # serial_number
        self.disks_viable_for_non_urgent_wearout_order = list()  # serial_number
        self.disks_viable_for_decommissioning_order = list()  # serial_number

        self.convert_to_urgent = dict()  # date: dict(serial_number: non_urgent_date)

        self.failed_disks_order = list()  # serial_number: date
        self.useful_life_disks_order = dict()  # serial_number: date
        self.wearout_disks_order = dict()  # serial_number: date
        self.non_urgent_wearout_disks_order = dict()  # serial_number: date
        self.decommissioned_disks_order = dict()  # serial_number: date

        self.rgroup_start_dates = dict()  # rgroup: date
        self.dgroup_start_dates = dict()  # dgroup: date

        self.longitudinal_cluster_metrics = list()  # cluster_wise_metrics object for each day
        self.dgroup_wise_metrics = dict()  # dgroup: metrics
        self.rgroup_wise_metrics = dict()  # rgroup: metrics

        self.disks_that_skipped_transitioning = dict()  # serial_number: (date, dgroup)

        self.day = 0

        self.rgroup_start_dates[str(constants.DEFAULT_REDUNDANCY_SCHEME)] = start_date

        self.daily_cluster_metrics = ClusterMetrics(DiskCategoryMetrics(
            BackgroundWork(Work(), Work(), Work(), Work(), Work(), Work(),
                           Work(), Work(), Work(), Work(), Work(), Work()),
            np.array([])), DiskCategoryMetrics(
            BackgroundWork(Work(), Work(), Work(), Work(), Work(), Work(),
                           Work(), Work(), Work(), Work(), Work(), Work()),
            np.array([])), dict())

        self.rgroup_wise_metrics[common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]] = \
            RgroupMetrics(DiskCategoryMetrics(BackgroundWork(Work(), Work(), Work(), Work(), Work(), Work(),
                                                             Work(), Work(), Work(), Work(), Work(), Work()),
                                              np.array([])), False, dict(), dict())

        self.rgroup_wise_metrics[common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]] = \
            RgroupMetrics(DiskCategoryMetrics(BackgroundWork(Work(), Work(), Work(), Work(), Work(), Work(),
                                                             Work(), Work(), Work(), Work(), Work(), Work()),
                                              np.array([])), False, dict(), dict())

        # self.pending_aggressive_reencoding = dict()  # serial_number: date
        # self.performed_aggressive_reencoding = dict()  # dest_rg: dict(serial_number, date)

        self.pending_aggressive_reencoding_optimized = dict()  # serial_number: date
        self.pending_aggressive_reencoding_optimized_order = dict()  # list of pending optimized re-encodings to be done per step
        self.performed_aggressive_reencoding_optimized = dict()  # dest_rg: dict(serial_number, date)

        self.future_work_map = dict()  # date_at_which_to_add_capacity: (serial_number, rgroup_during_conversion)
        self.disk_future_work_dates = dict()  # serial_number: list(date, read, write)

        self.latest_useful_life_rg = dict()  # serial_number: rgroup
        self.total_num_disks_retired = 0
        self.disk_retired = dict()
        self.transition_rg = dict()  # date: (dg, old_rg, new_rg)

        self.optimized_disk_days = dict()  # serial_number: (enter_date, exit_date)
        self.optimal_optimized_disk_days = dict()  # serial_number: (enter_date, exit_date)

        self.urgent_transition_rg = dict()  # date: (dg, old_rg, new_rg, step_or_trickle)
        self.date_to_start_background_retirement = dict()  # date: (date_at_which_issued, serial_number, num_days_to_spread_it_out, from_rg)
        self.disk_batch_retirement_end_date = dict()  # date_of_batch_reencoding_over: list(date_of_issue, dgroup)
        self.disk_batch_retirement_length = dict()

        self.step_wise_metrics = dict()  # dgroup: dict(date: (step_details, rgroup_wise_metrics_for_step))
        self.daily_step_wise_io_metrics = dict()  # step_or_trickle_metrics: dict('total', 'allowed', 'used', 'needed')
        self.disk_date_to_step_date = dict()  # date_of_disk_deployment: date_of_step_it_belongs_to

        self.steps_requiring_aggressive_reencoding_to_wearout = dict()
        self.steps_requiring_aggressive_reencoding_to_non_urgent_wearout = dict()
        self.steps_requiring_aggressive_reencoding_from_infancy = dict()

        self.pending_work = dict()
        self.pending_work[constants.WorkType.INFANCY] = dict()
        self.pending_work[constants.WorkType.NON_URGENT_WEAROUT] = dict()
        self.pending_work[constants.WorkType.WEAROUT] = dict()

        self.performed_work = dict()
        self.performed_work[constants.WorkType.INFANCY] = dict()
        self.performed_work[constants.WorkType.NON_URGENT_WEAROUT] = dict()
        self.performed_work[constants.WorkType.WEAROUT] = dict()

        self.optimal_disk_days = dict() # serial_number: overhead: (start-optimized, stop-optimized)
        self.actual_disk_days = dict() # serial_number: overhead: (start-optimized, stop_optimized)
        self.latest_optimal_rgroup = dict() # serial_number: rgroup
        self.latest_actual_rgroup = dict()  # serial_number: rgroup

        self.transition_stats = dict()  # type: number
        self.transition_stats[constants.TransitionType.DECOMMISSIONING] = 0
        self.transition_stats[constants.TransitionType.BULK] = 0

    def __del__(self):
        self.metrics.save_metrics_to_file()

        # FIXME: revisit counting of optimal and actual disk-days
        total_optimized_disk_days = 0
        for disk, dates in self.optimized_disk_days.items():
            entry = dates[0]
            exit = dates[1]
            if exit is None:
                exit = constants.END_DATE
            total_optimized_disk_days += common.days_between(entry, exit)

        total_optimal_optimized_disk_days = 0
        for disk, dates in self.optimal_optimized_disk_days.items():
            entry = dates[0]
            exit = dates[1]
            if exit is None:
                exit = constants.END_DATE
            total_optimal_optimized_disk_days += common.days_between(entry, exit)

        optimal_disk_day_overhead = 0.0
        actual_disk_day_overhead = 0.0
        optimal_space_savings_per_disk = dict()
        optimal_disk_day_overhead_per_disk = dict()
        actual_disk_day_overhead_per_disk = dict()
        optimal_total_optimized_disk_days = 0
        optimal_space_savings_list = list()
        for disk, overhead_dict in self.optimal_disk_days.items():
            optimal_space_savings_per_disk[disk] = 0.0
            total_disk_days = 0
            for overhead, tup in overhead_dict.items():
                start_date = tup[0]
                end_date = tup[1]
                if end_date is None:
                    end_date = constants.END_DATE
                total_disk_days += common.days_between(start_date, end_date) + 1
                optimal_space_savings_per_disk[disk] += (overhead * (common.days_between(start_date, end_date) + 1))
                if overhead == common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].overhead:
                    continue
                else:
                    optimal_total_optimized_disk_days += common.days_between(start_date, end_date) + 1
                optimal_disk_day_overhead_per_disk[disk] = (float(tup[2]) / overhead) * common.days_between(start_date, end_date)
            if total_disk_days == 0:
                print("Disk is " + disk)
                print(overhead_dict)
            optimal_space_savings_per_disk[disk] = float(optimal_space_savings_per_disk[disk] / (common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].overhead * total_disk_days))
            optimal_space_savings_list.append(optimal_space_savings_per_disk[disk])

        actual_space_savings_per_disk = dict()
        actual_space_savings_list = list()
        actual_total_optimized_disk_days = 0
        for disk, overhead_dict in self.actual_disk_days.items():
            actual_space_savings_per_disk[disk] = 0.0
            total_disk_days = 0
            for overhead, tup in overhead_dict.items():
                start_date = tup[0]
                end_date = tup[1]
                if end_date is None:
                    end_date = constants.END_DATE
                total_disk_days += common.days_between(start_date, end_date) + 1
                actual_space_savings_per_disk[disk] += (overhead * (common.days_between(start_date, end_date) + 1))
                if overhead == common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].overhead:
                    continue
                else:
                    actual_total_optimized_disk_days += common.days_between(start_date, end_date) + 1
                actual_disk_day_overhead_per_disk[disk] = (float(tup[2]) / overhead) * common.days_between(start_date, end_date)
            actual_space_savings_per_disk[disk] = float(actual_space_savings_per_disk[disk] / (common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].overhead * total_disk_days))
            actual_space_savings_list.append(actual_space_savings_per_disk[disk])

        total_optimal_disk_days = 0
        for disk, val in optimal_disk_day_overhead_per_disk.items():
            total_optimal_disk_days += val

        total_actual_disk_days = 0
        for disk, val in actual_disk_day_overhead_per_disk.items():
            total_actual_disk_days += val

        total_transitions = self.transition_stats[constants.TransitionType.DECOMMISSIONING] + self.transition_stats[constants.TransitionType.BULK]
        logging.info("transitioning by decommissioning = " + str(float(self.transition_stats[constants.TransitionType.DECOMMISSIONING]) / total_transitions))
        logging.info("transitioning by bulk parity recalculation = " + str(float(self.transition_stats[constants.TransitionType.BULK]) / total_transitions))

        logging.info("optimal optimized disk days = " + str(optimal_total_optimized_disk_days))
        logging.info("actual optimized disk days = " + str(actual_total_optimized_disk_days))

        logging.info("avg. optimal space savings = " + str(np.mean(optimal_space_savings_list)))
        logging.info("avg. actual space savings = " + str(np.mean(actual_space_savings_list)))

        logging.info("optimized disk days = " + str(total_optimized_disk_days))
        logging.info("optimal optimized disk days = " + str(total_optimal_optimized_disk_days))
        logging.info("disk-days lost percentage = " + str(100.0 - ((float(total_optimized_disk_days) / total_optimal_optimized_disk_days) * 100.0)))

    @abstractmethod
    def _calculate_transcoding_cost(self, capacity, from_rg, to_rg,
        avg_disks_transitioned=0, rgroup_num_disks=0):
        pass

    def _record_optimal_disk_days(self, serial_number, date, to_rg, dead=0):
        self.optimal_disk_days[serial_number][self.latest_optimal_rgroup[serial_number].overhead] = (self.optimal_disk_days[serial_number][self.latest_optimal_rgroup[serial_number].overhead][0], date, self.running_disks[serial_number][1].capacity)
        if not dead:
            self.optimal_disk_days[serial_number][to_rg.overhead] = (date, None, self.running_disks[serial_number][1].capacity)
        self.latest_optimal_rgroup[serial_number] = to_rg

    def _record_actual_disk_days(self, serial_number, date, to_rg, dead=0):
        self.actual_disk_days[serial_number][self.latest_actual_rgroup[serial_number].overhead] = (self.actual_disk_days[serial_number][self.latest_actual_rgroup[serial_number].overhead][0], date, self.running_disks[serial_number][1].capacity)
        if not dead:
            self.actual_disk_days[serial_number][to_rg.overhead] = (date, None, self.running_disks[serial_number][1].capacity)
        self.latest_actual_rgroup[serial_number] = to_rg

    def _get_deployment_and_rgroup_metrics(self, serial_number, failed=False):
        if failed:
            dgroup = self.failed_disks[serial_number][1]
        else:
            dgroup = self.running_disks[serial_number][1]
        dgroup_metrics = self.dgroup_wise_metrics[dgroup]
        if dgroup.deployment_type == constants.DeploymentType.STEP:
            if serial_number in dgroup_metrics.disk_step_mapping:
                step_date = dgroup_metrics.disk_step_mapping[serial_number]
                return self.step_wise_metrics[dgroup][step_date][0], self.step_wise_metrics[dgroup][step_date][1], (dgroup, step_date)
        return self.daily_cluster_metrics.trickle_pool, self.rgroup_wise_metrics, 'trickle_pool'

    def report_disk_useful_life_rgroup(self, serial_number, dgroup, date):
        if serial_number in self.dgroup_wise_metrics[dgroup].canary_disks:
            self.disks_that_skipped_transitioning[serial_number] = (date, dgroup)
            return
        else:
            self.disks_viable_for_useful_life[serial_number] = (date, dgroup.latest_rdn_cp.rgroup)
        self.disks_viable_for_useful_life_order.append(serial_number)

    def reset_daily_stats(self):
        del self.daily_cluster_metrics.total_disk_metrics.background_work
        self.daily_cluster_metrics.total_disk_metrics.background_work = BackgroundWork(Work(), Work(), Work(), Work(),
                                                                                       Work(), Work(), Work(), Work(),
                                                                                       Work(), Work(), Work(), Work())

        for dg, dg_mertics in self.dgroup_wise_metrics.items():
            del dg_mertics.disk_metrics.background_work
            del dg_mertics.canary_disk_metrics.background_work
            dg_mertics.disk_metrics.background_work = BackgroundWork(Work(), Work(), Work(), Work(),
                                                                     Work(), Work(), Work(), Work(),
                                                                     Work(), Work(), Work(), Work())
            dg_mertics.canary_disk_metrics.background_work = BackgroundWork(Work(), Work(), Work(), Work(),
                                                                            Work(), Work(), Work(), Work(),
                                                                            Work(), Work(), Work(), Work())

        del self.daily_cluster_metrics.trickle_pool.background_work
        self.daily_cluster_metrics.trickle_pool.background_work = BackgroundWork(Work(), Work(), Work(), Work(),
                                                                                 Work(), Work(), Work(), Work(),
                                                                                 Work(), Work(), Work(), Work())

        del self.daily_step_wise_io_metrics
        self.daily_step_wise_io_metrics = dict()
        for dg, date_dict in self.step_wise_metrics.items():
            for dt, tup in date_dict.items():
                step_or_trickle_metrics = tup[0]
                del step_or_trickle_metrics.background_work
                step_or_trickle_metrics.background_work = BackgroundWork(Work(), Work(), Work(), Work(),
                                                                         Work(), Work(), Work(), Work(),
                                                                         Work(), Work(), Work(), Work())

                rgroup_wise_metrics = tup[1]
                for rg, rg_mertics in rgroup_wise_metrics.items():
                    del rg_mertics.disk_metrics.background_work
                    rg_mertics.disk_metrics.background_work = BackgroundWork(Work(), Work(), Work(), Work(),
                                                                             Work(), Work(), Work(), Work(),
                                                                             Work(), Work(), Work(), Work())

        for rg, rg_mertics in self.rgroup_wise_metrics.items():
            del rg_mertics.disk_metrics.background_work
            rg_mertics.disk_metrics.background_work = BackgroundWork(Work(), Work(), Work(), Work(),
                                                                     Work(), Work(), Work(), Work(),
                                                                     Work(), Work(), Work(), Work())

    def report_disk_decommissioning(self, serial_number, date):
        self.disks_viable_for_decommissioning_order.append(serial_number)
        self.disks_viable_for_decommissioning[serial_number] = date
        step_or_trickle_metrics, rgroup_wise_metrics, _ = self._get_deployment_and_rgroup_metrics(serial_number)
        rgroup_wise_metrics[self.running_disks[serial_number][2]].potential_capacity_after_redundancy_management -= self.running_disks[serial_number][1].capacity
        self._record_optimal_disk_days(serial_number, date, common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"], dead=1)

    def report_disk_failure(self, serial_number, date):
        self.num_failed_disks += 1
        dgroup = self.running_disks[serial_number][1]
        rgroup = self.running_disks[serial_number][2]
        phase_of_life = self.running_disks[serial_number][3]

        self._record_optimal_disk_days(serial_number, date, common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"], dead=1)
        self._record_actual_disk_days(serial_number, date, common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"], dead=1)

        step_or_trickle_details, rgroup_wise_metrics, step_key = self._get_deployment_and_rgroup_metrics(serial_number)

        if serial_number in self.disks_viable_for_useful_life:
            rgroup_wise_metrics[rgroup].potential_capacity_after_redundancy_management -= dgroup.capacity

            if step_key != 'trickle_pool' and self.disks_viable_for_useful_life[serial_number][1] in self.pending_work[constants.WorkType.INFANCY][step_key]:
                if serial_number in self.performed_work[constants.WorkType.INFANCY][step_key][self.disks_viable_for_useful_life[serial_number][1]]:
                    del self.performed_work[constants.WorkType.INFANCY][step_key][self.disks_viable_for_useful_life[serial_number][1]][serial_number]
            elif serial_number in self.disks_viable_for_useful_life_order:
                self.disks_viable_for_useful_life_order.remove(serial_number)
            elif dgroup.deployment_type == constants.DeploymentType.STEP:
                for dest_rg, dest_rg_list in self.pending_work[constants.WorkType.INFANCY][step_key].items():
                    if serial_number in dest_rg_list:
                        dest_rg_list.remove(serial_number)
            del self.disks_viable_for_useful_life[serial_number]
        elif serial_number in self.disks_viable_for_wearout:
            rgroup_wise_metrics[common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]].potential_capacity_after_redundancy_management -= dgroup.capacity

            if step_key != 'trickle_pool' and self.disks_viable_for_wearout[serial_number][1] in self.pending_work[constants.WorkType.WEAROUT][step_key]:
                if serial_number in self.performed_work[constants.WorkType.WEAROUT][step_key][self.disks_viable_for_wearout[serial_number][1]]:
                    del self.performed_work[constants.WorkType.WEAROUT][step_key][self.disks_viable_for_wearout[serial_number][1]][serial_number]
            elif serial_number in self.disks_viable_for_wearout_order:
                self.disks_viable_for_wearout_order.remove(serial_number)
            elif dgroup.deployment_type == constants.DeploymentType.STEP:
                for dest_rg, dest_rg_list in self.pending_work[constants.WorkType.WEAROUT][step_key].items():
                    if serial_number in dest_rg_list:
                        dest_rg_list.remove(serial_number)
            del self.disks_viable_for_wearout[serial_number]
        elif serial_number in self.disks_viable_for_non_urgent_wearout:
            rgroup_wise_metrics[common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]].potential_capacity_after_redundancy_management -= dgroup.capacity
            if step_key != 'trickle_pool' and self.disks_viable_for_non_urgent_wearout[serial_number][1] in self.pending_work[constants.WorkType.NON_URGENT_WEAROUT][step_key]:
                if serial_number in self.performed_work[constants.WorkType.NON_URGENT_WEAROUT][step_key][self.disks_viable_for_non_urgent_wearout[serial_number][1]]:
                    del self.performed_work[constants.WorkType.NON_URGENT_WEAROUT][step_key][self.disks_viable_for_non_urgent_wearout[serial_number][1]][serial_number]
            elif serial_number in self.disks_viable_for_non_urgent_wearout_order:
                self.disks_viable_for_non_urgent_wearout_order.remove(serial_number)
            elif dgroup.deployment_type == constants.DeploymentType.STEP:
                for dest_rg, dest_rg_list in self.pending_work[constants.WorkType.NON_URGENT_WEAROUT][step_key].items():
                    if serial_number in dest_rg_list:
                        dest_rg_list.remove(serial_number)
            if self.disks_viable_for_non_urgent_wearout[serial_number][3] in self.convert_to_urgent and serial_number in self.convert_to_urgent[self.disks_viable_for_non_urgent_wearout[serial_number][3]]:
                del self.convert_to_urgent[self.disks_viable_for_non_urgent_wearout[serial_number][3]][serial_number]
            del self.disks_viable_for_non_urgent_wearout[serial_number]

        if serial_number in self.disks_viable_for_decommissioning:
            rgroup_wise_metrics[rgroup].potential_capacity_after_redundancy_management += self.running_disks[serial_number][1].capacity
            del self.disks_viable_for_decommissioning[serial_number]
            self.disks_viable_for_decommissioning_order.remove(serial_number)

        # order of adding to failed and then removing from running is important
        self.failed_disks[serial_number] = (date, dgroup, rgroup, phase_of_life)

        del rgroup.disks[serial_number]
        del self.running_disks[serial_number]

        self.failed_disks_order.append(serial_number)
        self.daily_cluster_metrics.total_disk_metrics.num_running_disks -= 1
        self.daily_cluster_metrics.total_disk_metrics.num_failed_disks += 1

        reconstruction_reads = dgroup.capacity * rgroup.data_chunks
        reconstruction_writes = dgroup.capacity

        dgroup_metrics = self.dgroup_wise_metrics[dgroup]
        dgroup_metrics.disk_metrics.num_running_disks -= 1
        dgroup_metrics.disk_metrics.num_failed_disks += 1

        if serial_number in dgroup_metrics.canary_disks:
            dgroup_metrics.canary_disk_metrics.num_running_disks -= 1
            dgroup_metrics.canary_disk_metrics.num_failed_disks += 1

        step_or_trickle_details.num_running_disks -= 1
        step_or_trickle_details.num_failed_disks += 1
        step_or_trickle_details.background_work.reconstruction_needed.reads += reconstruction_reads
        step_or_trickle_details.background_work.reconstruction_needed.reads += reconstruction_writes
        step_or_trickle_details.background_work.reconstruction_needed.io += reconstruction_reads + reconstruction_writes
        step_or_trickle_details.capacity -= dgroup.capacity

        dgroup_metrics.disk_metrics.background_work.reconstruction_needed.reads += reconstruction_reads
        dgroup_metrics.disk_metrics.background_work.reconstruction_needed.reads += reconstruction_writes
        dgroup_metrics.disk_metrics.background_work.reconstruction_needed.io += reconstruction_reads + reconstruction_writes

        if phase_of_life == properties.PHASE_OF_LIFE_INFANCY:
            step_or_trickle_details.num_infancy_disks -= 1
            dgroup_metrics.disk_metrics.num_infancy_disks -= 1
            if serial_number in dgroup_metrics.canary_disks:
                dgroup_metrics.canary_disk_metrics.num_infancy_disks -= 1
        elif phase_of_life == properties.PHASE_OF_LIFE_USEFUL_LIFE:
            step_or_trickle_details.num_useful_life_disks -= 1
            dgroup_metrics.disk_metrics.num_useful_life_disks -= 1
            if serial_number in dgroup_metrics.canary_disks:
                dgroup_metrics.canary_disk_metrics.num_useful_life_disks -= 1
        elif phase_of_life == properties.PHASE_OF_LIFE_WEAROUT:
            step_or_trickle_details.num_wearout_disks -= 1
            dgroup_metrics.disk_metrics.num_wearout_disks -= 1
            if serial_number in dgroup_metrics.canary_disks:
                dgroup_metrics.canary_disk_metrics.num_wearout_disks -= 1

        if serial_number in dgroup_metrics.canary_disks:
            del dgroup_metrics.canary_disks[serial_number]

        rgroup_wise_metrics[rgroup].disk_metrics.num_running_disks -= 1
        rgroup_wise_metrics[rgroup].disk_metrics.num_failed_disks += 1
        if rgroup_wise_metrics[rgroup].disk_metrics.num_running_disks < 0:
            assert 1 == 0

        dgroup_metrics.disk_metrics.capacity = dgroup_metrics.disk_metrics.num_running_disks * dgroup.capacity
        rgroup_wise_metrics[rgroup].disk_metrics.capacity -= dgroup.capacity
        self.daily_cluster_metrics.total_disk_metrics.capacity -= dgroup.capacity

        if serial_number in self.optimized_disk_days:
            self.optimized_disk_days[serial_number] = (self.optimized_disk_days[serial_number][0], date)
            self.optimal_optimized_disk_days[serial_number] = (self.optimal_optimized_disk_days[serial_number][0], date)

    def report_disk_birth(self, serial_number, dgroup, date, disk_step_key=None):
        self.running_disks[serial_number] = (date, dgroup, common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)],
                                             properties.PHASE_OF_LIFE_INFANCY)
        self.daily_cluster_metrics.total_disk_metrics.num_running_disks += 1
        self.daily_cluster_metrics.total_disk_metrics.num_infancy_disks += 1
        self.daily_cluster_metrics.total_disk_metrics.num_observed_disks += 1
        if dgroup not in self.dgroup_start_dates:
            self.dgroup_start_dates[dgroup] = date
            self.dgroup_wise_metrics[dgroup] = DgroupMetrics(
                DiskCategoryMetrics(
                    BackgroundWork(Work(), Work(), Work(), Work(), Work(),
                                   Work(), Work(), Work(), Work(), Work(),
                                   Work(), Work()), np.array([])),
                DiskCategoryMetrics(
                    BackgroundWork(Work(), Work(), Work(), Work(), Work(),
                                   Work(), Work(), Work(), Work(), Work(),
                                   Work(), Work()), np.array([])),
                dict(), list(), dict(), dict(), dict(), dict(), dict(), date)

            self.step_wise_metrics[dgroup] = dict()

        dgroup_metrics = self.dgroup_wise_metrics[dgroup]
        dgroup_metrics.disk_metrics.num_running_disks += 1
        dgroup_metrics.disk_metrics.num_infancy_disks += 1
        dgroup_metrics.disk_metrics.num_observed_disks += 1

        if disk_step_key is not None:
            disk_step_date = disk_step_key[1]
            current_step_metrics = None
            if disk_step_date not in self.step_wise_metrics[dgroup]:
                self.dgroup_wise_metrics[dgroup].step_list.append(disk_step_date)
                current_step_metrics = DiskCategoryMetrics(
                    BackgroundWork(Work(), Work(), Work(), Work(), Work(),
                                   Work(), Work(), Work(), Work(), Work(),
                                   Work(), Work()), np.array([]))
                self.step_wise_metrics[dgroup][disk_step_date] = (current_step_metrics, dict())
                self.step_wise_metrics[dgroup][disk_step_date][1][common.rgroups[str(
                    constants.DEFAULT_REDUNDANCY_SCHEME)]] = RgroupMetrics(
                    DiskCategoryMetrics(BackgroundWork(Work(), Work(), Work(),
                                                       Work(), Work(), Work(),
                                                       Work(), Work(), Work(),
                                                       Work(), Work(), Work()),
                                        np.array([])), False, dict(), dict())
                self.step_wise_metrics[dgroup][disk_step_date][1][common.rgroups[str(
                    constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]
                ] = RgroupMetrics(
                    DiskCategoryMetrics(BackgroundWork(Work(), Work(), Work(),
                                                       Work(), Work(), Work(),
                                                       Work(), Work(), Work(),
                                                       Work(), Work(), Work()),
                                        np.array([])), False, dict(), dict())
                self.dgroup_wise_metrics[dgroup].step_metrics[disk_step_date] = current_step_metrics
            else:
                current_step_metrics = self.dgroup_wise_metrics[dgroup].step_metrics[disk_step_date]

            dgroup_metrics.disk_step_mapping[serial_number] = disk_step_date
            current_step_metrics.num_running_disks += 1
            current_step_metrics.num_infancy_disks += 1
            current_step_metrics.num_observed_disks += 1
        elif (dgroup.deployment_type == constants.DeploymentType.TRICKLE) and (
            (len(dgroup_metrics.canary_disks) <= constants.MIN_SAMPLE_SIZE) or (
                dgroup_metrics.last_canary_birthday == date)):
            if dgroup_metrics.last_canary_birthday != date:
                dgroup_metrics.last_canary_birthday = date
            dgroup_metrics.canary_disks[serial_number] = date
            dgroup_metrics.canary_disk_metrics.num_running_disks += 1
            dgroup_metrics.canary_disk_metrics.num_infancy_disks += 1
            self.daily_cluster_metrics.trickle_pool.num_running_disks += 1
            self.daily_cluster_metrics.trickle_pool.num_infancy_disks += 1
            self.daily_cluster_metrics.trickle_pool.num_observed_disks += 1
        else:
            self.daily_cluster_metrics.trickle_pool.num_running_disks += 1
            self.daily_cluster_metrics.trickle_pool.num_infancy_disks += 1
            self.daily_cluster_metrics.trickle_pool.num_observed_disks += 1

        dgroup_metrics.disk_metrics.capacity = dgroup_metrics.disk_metrics.num_running_disks * dgroup.capacity

        _, rgroup_metrics, _ = self._get_deployment_and_rgroup_metrics(serial_number)
        rgroup_metrics = rgroup_metrics[common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]]
        rgroup_metrics.disk_metrics.num_running_disks += 1
        rgroup_metrics.disk_metrics.capacity += dgroup.capacity

        self.optimal_disk_days[serial_number] = dict()
        self.optimal_disk_days[serial_number][common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].overhead] = (date, None)
        self.latest_optimal_rgroup[serial_number] = common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]
        self.actual_disk_days[serial_number] = dict()
        self.actual_disk_days[serial_number][common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].overhead] = (date, None)
        self.latest_actual_rgroup[serial_number] = common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]

        self.daily_cluster_metrics.total_disk_metrics.capacity += dgroup.capacity

        common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].disks[serial_number] = (date, dgroup.capacity * constants.CLUSTER_FULLNESS_PERCENTAGE)

        if dgroup.deployment_type == constants.DeploymentType.TRICKLE and dgroup_metrics.last_canary_birthday == date:
            return False
        return True

    def report_disk_viable_for_useful_life(self, serial_number, date, total_disks_transitioning=0):
        if serial_number in self.disks_that_skipped_transitioning:
            return

        rgroup = self.disks_viable_for_useful_life[serial_number][1]

        step_or_trickle_metrics, rgroup_wise_metrics, _ = self._get_deployment_and_rgroup_metrics(serial_number)

        if rgroup not in rgroup_wise_metrics:
            rgroup_wise_metrics[rgroup] = RgroupMetrics(DiskCategoryMetrics(
                BackgroundWork(Work(), Work(), Work(), Work(), Work(), Work(),
                               Work(), Work(), Work(), Work(), Work(), Work()),
                np.array([])), False, dict(), dict())
        if rgroup not in self.rgroup_wise_metrics:
            self.rgroup_wise_metrics[rgroup] = RgroupMetrics(DiskCategoryMetrics(
                BackgroundWork(Work(), Work(), Work(), Work(), Work(), Work(),
                               Work(), Work(), Work(), Work(), Work(), Work()),
                np.array([])), False, dict(), dict())

        from_rgroup = common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]
        if rgroup_wise_metrics[from_rgroup].disk_metrics.avg_disks_transitioned_per_day == 0:
            rgroup_wise_metrics[from_rgroup].disk_metrics.avg_disks_transitioned_per_day = int(math.ceil(
                (float(rgroup_wise_metrics[from_rgroup].disk_metrics.num_running_disks) /
                 step_or_trickle_metrics.num_running_disks) * total_disks_transitioning))

        schedulable_reencoding_needed_reads, schedulable_reencoding_needed_writes = self._calculate_transcoding_cost(
            (self.running_disks[serial_number][1]).capacity, common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)],
            rgroup, avg_disks_transitioned=rgroup_wise_metrics[from_rgroup].disk_metrics.avg_disks_transitioned_per_day,
            rgroup_num_disks=rgroup_wise_metrics[from_rgroup].disk_metrics.num_running_disks)

        transitioning_date = self.disks_viable_for_useful_life[serial_number][0]
        self.disks_viable_for_useful_life[serial_number] = (transitioning_date, rgroup,
                                                            schedulable_reencoding_needed_reads,
                                                            schedulable_reencoding_needed_writes)

        step_or_trickle_metrics.background_work.schedulable_reencoding_needed.reads += schedulable_reencoding_needed_reads
        step_or_trickle_metrics.background_work.schedulable_reencoding_needed.writes += schedulable_reencoding_needed_writes
        step_or_trickle_metrics.background_work.schedulable_reencoding_needed.io += (
            schedulable_reencoding_needed_reads + schedulable_reencoding_needed_writes)

        rgroup_wise_metrics[from_rgroup].potential_capacity_after_redundancy_management -= (
            self.running_disks[serial_number][1]).capacity
        rgroup_wise_metrics[from_rgroup].potential_transcoding_capacity_needed += (
            self.running_disks[serial_number][1]).capacity
        rgroup_wise_metrics[rgroup].potential_capacity_after_redundancy_management += (
            self.running_disks[serial_number][1]).capacity

        self.optimal_optimized_disk_days[serial_number] = (date, None)
        self._record_optimal_disk_days(serial_number, date, self.disks_viable_for_useful_life[serial_number][1])

    def report_disk_viable_for_wearout(self, serial_number, date, non_urgent_to_urgent=False, total_disks_transitioning=0):
        if not non_urgent_to_urgent:
            self._record_optimal_disk_days(serial_number, date, common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"])
        if (serial_number in self.disks_that_skipped_transitioning) or (
                serial_number in common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"].disks):
            return

        if non_urgent_to_urgent is True and serial_number not in self.running_disks:
            return

        step_or_trickle_metrics, rgroup_wise_metrics, step_key = self._get_deployment_and_rgroup_metrics(serial_number)

        if self.running_disks[serial_number][3] == properties.PHASE_OF_LIFE_INFANCY:
            if serial_number in self.disks_viable_for_useful_life:
                reencoding_needed_reads = self.disks_viable_for_useful_life[serial_number][2]
                reencoding_needed_writes = self.disks_viable_for_useful_life[serial_number][3]

                step_or_trickle_metrics.background_work.schedulable_reencoding_needed.reads -= reencoding_needed_reads
                step_or_trickle_metrics.background_work.schedulable_reencoding_needed.writes -= reencoding_needed_writes
                step_or_trickle_metrics.background_work.schedulable_reencoding_needed.io -= (
                        reencoding_needed_reads + reencoding_needed_writes)

                dgroup = self.running_disks[serial_number][1]
                if step_key != 'trickle_pool' and serial_number in self.performed_work[constants.WorkType.INFANCY][step_key][self.disks_viable_for_useful_life[serial_number][1]]:
                    del self.performed_work[constants.WorkType.INFANCY][step_key][self.disks_viable_for_useful_life[serial_number][1]][serial_number]
                elif serial_number in self.disks_viable_for_useful_life_order:
                    self.disks_viable_for_useful_life_order.remove(serial_number)
                elif dgroup.deployment_type == constants.DeploymentType.STEP:
                    for dest_rg, dest_rg_list in self.pending_work[constants.WorkType.INFANCY][step_key].items():
                        if serial_number in dest_rg_list:
                            dest_rg_list.remove(serial_number)
                rgroup_wise_metrics[self.disks_viable_for_useful_life[serial_number][1]].potential_capacity_after_redundancy_management -= self.running_disks[serial_number][1].capacity
                del self.disks_viable_for_useful_life[serial_number]

            current_running_disk_tuple = self.running_disks[serial_number]
            dgroup = current_running_disk_tuple[1]
            rgroup = common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]
            to_rgroup = common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]
            self.running_disks[serial_number] = (self.running_disks[serial_number][0], dgroup,
                                                 to_rgroup, properties.PHASE_OF_LIFE_WEAROUT)
            dgroup_metrics = self.dgroup_wise_metrics[dgroup]
            dgroup_metrics.disk_metrics.num_infancy_disks -= 1
            dgroup_metrics.disk_metrics.num_wearout_disks += 1

            if serial_number in dgroup_metrics.canary_disks:
                dgroup_metrics.canary_disk_metrics.num_infancy_disks -= 1
                dgroup_metrics.canary_disk_metrics.num_wearout_disks += 1

            self.daily_cluster_metrics.total_disk_metrics.num_disks_skipped_useful_life += 1
            dgroup_metrics.disk_metrics.num_disks_skipped_useful_life += 1
            step_or_trickle_metrics.num_disks_skipped_useful_life += 1

            from_rgroup_metrics = rgroup_wise_metrics[rgroup]
            from_rgroup_metrics.disk_metrics.num_running_disks -= 1
            if from_rgroup_metrics.disk_metrics.num_running_disks < 0:
                # print(date, from_rgroup_metrics)
                raise ValueError
            to_rgroup_metrics = rgroup_wise_metrics[to_rgroup]
            to_rgroup_metrics.disk_metrics.num_running_disks += 1

            from_rgroup_metrics.disk_metrics.capacity -= dgroup.capacity
            to_rgroup_metrics.disk_metrics.capacity += dgroup.capacity

            self.daily_cluster_metrics.total_disk_metrics.num_infancy_disks -= 1
            self.daily_cluster_metrics.total_disk_metrics.num_wearout_disks += 1
            step_or_trickle_metrics.num_infancy_disks -= 1
            step_or_trickle_metrics.num_wearout_disks += 1

            rgroup_wise_metrics[rgroup].disk_metrics.capacity -= (
                self.running_disks[serial_number][1]).capacity
            rgroup_wise_metrics[to_rgroup].disk_metrics.capacity += (
                self.running_disks[serial_number][1]).capacity

            to_rgroup.disks[serial_number] = (date, rgroup.disks[serial_number][1])
            del rgroup.disks[serial_number]

            if serial_number in self.optimized_disk_days:
                self.optimized_disk_days[serial_number] = (self.optimized_disk_days[serial_number][0], date)
                self.optimal_optimized_disk_days[serial_number] = (self.optimal_optimized_disk_days[serial_number][0], date)
            return

        dgroup = self.running_disks[serial_number][1]
        if dgroup.deployment_type == constants.DeploymentType.TRICKLE and (serial_number in self.dgroup_wise_metrics[dgroup].canary_disks):
            return
        else:
            from_rgroup = self.running_disks[serial_number][2]

            if serial_number in from_rgroup.disks_crossing_second_level_afr:
                self.disks_viable_for_wearout[serial_number] = (date, 0, 0)
            else:
                cannot_delay_reencoding = False
                days_till_urgency = -1
                if dgroup.deployment_type == constants.DeploymentType.TRICKLE:
                    canary_start_age = common.days_between(date, self.dgroup_wise_metrics[dgroup].last_canary_birthday)
                    if (len(dgroup.cum_afr_array[dgroup.cp_list[-2].age_of_change:canary_start_age]) > 0) and (
                        np.max(dgroup.cum_afr_array[dgroup.cp_list[-2].age_of_change:canary_start_age]
                               ) >= from_rgroup.tolerable_afr):
                        days_till_urgency = canary_start_age - dgroup.cp_list[-2].age_of_change
                        cannot_delay_reencoding = True
                    else:
                        days_till_urgency = constants.REDUCED_USEFUL_LIFE_AGE
                else:
                    last_age_to_check = dgroup.min_sample_age + common.days_between(
                        date, dgroup.latest_min_sample_age_revision)
                    if (len(dgroup.afr_array[dgroup.cp_list[-2].age_of_change:last_age_to_check]) > 0) and (
                        np.max(dgroup.afr_array[dgroup.cp_list[-2].age_of_change:last_age_to_check]
                               ) >= from_rgroup.tolerable_afr):
                        days_till_urgency = last_age_to_check - dgroup.cp_list[-2].age_of_change
                        cannot_delay_reencoding = True
                    else:
                        days_till_urgency = constants.REDUCED_USEFUL_LIFE_AGE

                if (not cannot_delay_reencoding) and (not non_urgent_to_urgent):
                    self.report_disk_viable_for_non_urgent_wearout(
                        serial_number, date,
                        total_disks_transitioning=total_disks_transitioning,
                        days_till_urgency=days_till_urgency)
                    return

                if rgroup_wise_metrics[from_rgroup].disk_metrics.avg_disks_transitioned_per_day == 0:
                    rgroup_wise_metrics[from_rgroup].disk_metrics.avg_disks_transitioned_per_day = int(math.ceil(
                        (float(rgroup_wise_metrics[from_rgroup].disk_metrics.num_running_disks) /
                         self.daily_cluster_metrics.total_disk_metrics.num_running_disks) * total_disks_transitioning))

                urgent_reencoding_needed_reads, urgent_reencoding_needed_writes = self._calculate_transcoding_cost(
                    dgroup.capacity, from_rgroup,
                    common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"], avg_disks_transitioned=rgroup_wise_metrics[
                        from_rgroup].disk_metrics.avg_disks_transitioned_per_day, rgroup_num_disks=rgroup_wise_metrics[
                        from_rgroup].disk_metrics.num_running_disks)

                self.disks_viable_for_wearout[serial_number] = (date, urgent_reencoding_needed_reads, urgent_reencoding_needed_writes)

                step_or_trickle_metrics.background_work.urgent_reencoding_needed.reads += urgent_reencoding_needed_reads
                step_or_trickle_metrics.background_work.urgent_reencoding_needed.writes += urgent_reencoding_needed_writes
                step_or_trickle_metrics.background_work.urgent_reencoding_needed.io += (urgent_reencoding_needed_reads + urgent_reencoding_needed_writes)

                if non_urgent_to_urgent is True:
                    reencoding_needed_reads = self.disks_viable_for_non_urgent_wearout[serial_number][1]
                    reencoding_needed_writes = self.disks_viable_for_non_urgent_wearout[serial_number][2]
                    step_or_trickle_metrics.background_work.non_urgent_reencoding_needed.reads -= reencoding_needed_reads
                    step_or_trickle_metrics.background_work.non_urgent_reencoding_needed.writes -= reencoding_needed_writes
                    step_or_trickle_metrics.background_work.non_urgent_reencoding_needed.io -= (
                        reencoding_needed_reads + reencoding_needed_writes)

                    if (step_key != 'trickle_pool') and (
                        step_key in self.pending_work[constants.WorkType.NON_URGENT_WEAROUT]) and (
                        self.disks_viable_for_non_urgent_wearout[serial_number][1] in
                        self.pending_work[constants.WorkType.NON_URGENT_WEAROUT][step_key]):
                        if serial_number in self.performed_work[constants.WorkType.NON_URGENT_WEAROUT][step_key][self.disks_viable_for_non_urgent_wearout[serial_number][1]]:
                            del self.performed_work[constants.WorkType.NON_URGENT_WEAROUT][step_key][self.disks_viable_for_non_urgent_wearout[serial_number][1]][serial_number]
                    elif serial_number in self.disks_viable_for_non_urgent_wearout_order:
                        self.disks_viable_for_non_urgent_wearout_order.remove(serial_number)
                    elif dgroup.deployment_type == constants.DeploymentType.STEP:
                        for dest_rg, dest_rg_list in self.pending_work[constants.WorkType.NON_URGENT_WEAROUT][step_key].items():
                            if serial_number in dest_rg_list:
                                dest_rg_list.remove(serial_number)
                    del self.disks_viable_for_non_urgent_wearout[serial_number]

                if serial_number not in self.disk_retired:
                    rgroup_wise_metrics[from_rgroup].potential_transcoding_capacity_needed += (
                        self.running_disks[serial_number][1]).capacity
            self.disks_viable_for_wearout_order.append(serial_number)
            rgroup_wise_metrics[common.rgroups[str(
                constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]].potential_capacity_after_redundancy_management += (
                self.running_disks[serial_number][1]).capacity

    def report_disk_viable_for_non_urgent_wearout(self, serial_number, date,
        total_disks_transitioning=0, days_till_urgency=-1):

        actual_wearout = datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=constants.REDUCED_USEFUL_LIFE_AGE)
        self._record_optimal_disk_days(serial_number, actual_wearout.strftime("%Y-%m-%d"), common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"])
        if (serial_number in self.disks_that_skipped_transitioning) or (
                serial_number in common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"].disks):
          return

        from_rgroup = self.running_disks[serial_number][2]

        step_or_trickle_metrics, rgroup_wise_metrics, step_key = self._get_deployment_and_rgroup_metrics(serial_number)

        if (self.running_disks[serial_number][3] == properties.PHASE_OF_LIFE_INFANCY) or (from_rgroup == common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]):
            if serial_number in self.disks_viable_for_useful_life:
                reencoding_needed_reads = self.disks_viable_for_useful_life[serial_number][2]
                reencoding_needed_writes = self.disks_viable_for_useful_life[serial_number][3]

                step_or_trickle_metrics.background_work.schedulable_reencoding_needed.reads -= reencoding_needed_reads
                step_or_trickle_metrics.background_work.schedulable_reencoding_needed.writes -= reencoding_needed_writes
                step_or_trickle_metrics.background_work.schedulable_reencoding_needed.io -= (
                        reencoding_needed_reads + reencoding_needed_writes)

                dgroup = self.running_disks[serial_number][1]
                if step_key != 'trickle_pool' and serial_number in self.performed_work[constants.WorkType.INFANCY][step_key][self.disks_viable_for_useful_life[serial_number][1]]:
                    del self.performed_work[constants.WorkType.INFANCY][step_key][self.disks_viable_for_useful_life[serial_number][1]][serial_number]
                elif serial_number in self.disks_viable_for_useful_life_order:
                    self.disks_viable_for_useful_life_order.remove(serial_number)
                elif dgroup.deployment_type == constants.DeploymentType.STEP:
                    for dest_rg, dest_rg_list in self.pending_work[constants.WorkType.INFANCY][step_key].items():
                        if serial_number in dest_rg_list:
                            dest_rg_list.remove(serial_number)
                rgroup_wise_metrics[
                    self.disks_viable_for_useful_life[serial_number][1]].potential_capacity_after_redundancy_management -= self.running_disks[serial_number][1].capacity
                del self.disks_viable_for_useful_life[serial_number]

            current_running_disk_tuple = self.running_disks[serial_number]
            dgroup = current_running_disk_tuple[1]
            rgroup = common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]
            to_rgroup = common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]
            self.running_disks[serial_number] = (self.running_disks[serial_number][0], dgroup,
                                                 to_rgroup, properties.PHASE_OF_LIFE_WEAROUT)
            dgroup_metrics = self.dgroup_wise_metrics[dgroup]
            dgroup_metrics.disk_metrics.num_infancy_disks -= 1
            dgroup_metrics.disk_metrics.num_wearout_disks += 1

            if serial_number in dgroup_metrics.canary_disks:
                dgroup_metrics.canary_disk_metrics.num_infancy_disks -= 1
                dgroup_metrics.canary_disk_metrics.num_wearout_disks += 1

            self.daily_cluster_metrics.total_disk_metrics.num_disks_skipped_useful_life += 1
            dgroup_metrics.disk_metrics.num_disks_skipped_useful_life += 1

            from_rgroup_metrics = rgroup_wise_metrics[rgroup]
            from_rgroup_metrics.disk_metrics.num_running_disks -= 1
            if from_rgroup_metrics.disk_metrics.num_running_disks < 0:
                # print(date, from_rgroup_metrics)
                raise ValueError
            to_rgroup_metrics = rgroup_wise_metrics[to_rgroup]
            to_rgroup_metrics.disk_metrics.num_running_disks += 1

            from_rgroup_metrics.disk_metrics.capacity -= dgroup.capacity
            to_rgroup_metrics.disk_metrics.capacity += dgroup.capacity

            step_or_trickle_metrics.num_infancy_disks -= 1
            step_or_trickle_metrics.num_wearout_disks += 1

            rgroup_wise_metrics[rgroup].disk_metrics.capacity -= (
                self.running_disks[serial_number][1]).capacity
            rgroup_wise_metrics[to_rgroup].disk_metrics.capacity += (
                self.running_disks[serial_number][1]).capacity

            to_rgroup.disks[serial_number] = (date, rgroup.disks[serial_number][1])
            del rgroup.disks[serial_number]

            if serial_number in self.optimized_disk_days:
                self.optimized_disk_days[serial_number] = (self.optimized_disk_days[serial_number][0], date)
                self.optimal_optimized_disk_days[serial_number] = (self.optimal_optimized_disk_days[serial_number][0], date)
            return

        if serial_number in from_rgroup.disks_crossing_second_level_afr:
            self.disks_viable_for_non_urgent_wearout[serial_number] = (date, 0, 0)
        else:
            if rgroup_wise_metrics[from_rgroup].disk_metrics.avg_disks_transitioned_per_day == 0:
                rgroup_wise_metrics[from_rgroup].disk_metrics.avg_disks_transitioned_per_day = int(math.ceil(
                    (float(rgroup_wise_metrics[from_rgroup].disk_metrics.num_running_disks) /
                     self.daily_cluster_metrics.total_disk_metrics.num_running_disks) * total_disks_transitioning))

            non_urgent_reencoding_needed_reads, non_urgent_reencoding_needed_writes = self._calculate_transcoding_cost(
                (self.running_disks[serial_number][1]).capacity, from_rgroup,
                common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"],
                avg_disks_transitioned=rgroup_wise_metrics[from_rgroup].disk_metrics.avg_disks_transitioned_per_day,
                rgroup_num_disks=rgroup_wise_metrics[from_rgroup].disk_metrics.num_running_disks)

            step_or_trickle_metrics.background_work.non_urgent_reencoding_needed.reads += non_urgent_reencoding_needed_reads
            step_or_trickle_metrics.background_work.non_urgent_reencoding_needed.writes += non_urgent_reencoding_needed_writes
            step_or_trickle_metrics.background_work.non_urgent_reencoding_needed.io += (
                        non_urgent_reencoding_needed_reads + non_urgent_reencoding_needed_writes)

            dgroup = self.running_disks[serial_number][1]

            age_today = (datetime.datetime.strptime(
                date, "%Y-%m-%d") -
                         datetime.datetime.strptime(
                             self.running_disks[serial_number][0],
                             "%Y-%m-%d")).days
            # TODO: have to check if AFR projection is being done correctly.
            if days_till_urgency >= 0:
                convert_to_urgent_on_date = (
                    datetime.datetime.strptime(date, "%Y-%m-%d") +
                    datetime.timedelta(days=min(
                        1.0 / constants.AVG_LIFETIME_IO_BANDWIDTH_CAP,
                        days_till_urgency))).strftime("%Y-%m-%d")
            else:
                convert_to_urgent_on_date = (
                    datetime.datetime.strptime(date, "%Y-%m-%d") +
                    datetime.timedelta(days=min(
                        1.0 / constants.AVG_LIFETIME_IO_BANDWIDTH_CAP,
                        dgroup.latest_rup_cp.age_of_change - age_today))
                ).strftime("%Y-%m-%d")

            if convert_to_urgent_on_date not in self.convert_to_urgent:
                self.convert_to_urgent[convert_to_urgent_on_date] = dict()
            self.convert_to_urgent[convert_to_urgent_on_date][serial_number] = date

            self.disks_viable_for_non_urgent_wearout[serial_number] = (
                date, non_urgent_reencoding_needed_reads,
                non_urgent_reencoding_needed_writes, convert_to_urgent_on_date)

            if serial_number not in self.disk_retired:
                rgroup_wise_metrics[from_rgroup].potential_transcoding_capacity_needed += (
                    self.running_disks[serial_number][1]).capacity
        self.disks_viable_for_non_urgent_wearout_order.append(serial_number)
        rgroup_wise_metrics[common.rgroups[str(
            constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]].potential_capacity_after_redundancy_management += (
            self.running_disks[serial_number][1]).capacity

    def mark_rgroup_change_transition_for_date(self, dg, old_rg, new_rg, step_key, date, urgent=False):
        if urgent is False:
            if date not in self.transition_rg:
                self.transition_rg[date] = list()
            self.transition_rg[date].append((dg, old_rg, new_rg, step_key))
        else:
            if date not in self.urgent_transition_rg:
                self.urgent_transition_rg[date] = list()

            if (dg, old_rg, new_rg) not in self.urgent_transition_rg[date]:
                # insert the tuple in the right place,
                # i.e. we should always have increasing overhead order.
                trans_tup = None
                for trans_tup in self.urgent_transition_rg[date]:
                    if trans_tup[2].overhead > new_rg.overhead:
                        # insert tuple before trans_tup current position
                        break
                if (trans_tup is not None) and (self.urgent_transition_rg[date].index(trans_tup) <
                                                len(self.urgent_transition_rg[date]) - 1):
                    self.urgent_transition_rg[date].insert(self.urgent_transition_rg[date].index(trans_tup),
                                                           (dg, old_rg, new_rg, step_key))
                else:
                    self.urgent_transition_rg[date].append((dg, old_rg, new_rg, step_key))
                logging.debug(str((dg.name, old_rg.name, new_rg.name)) + " added on date = " + date + " urgently")

    def report_change_in_useful_life_rgroup(self, dg, old_rg, new_rg, date, from_age=0, disk=None):
        step_key = None
        if disk is None:
            for disk in old_rg.disks:
                if self.running_disks[disk][1] != dg:
                    continue

                if (from_age > 0) and common.days_between(date, self.running_disks[disk][0]) < from_age:
                    continue

                step_or_trickle_metrics, rgroup_wise_metrics, step_key = self._get_deployment_and_rgroup_metrics(disk)

                if new_rg not in rgroup_wise_metrics:
                    rgroup_wise_metrics[new_rg] = RgroupMetrics(DiskCategoryMetrics(
                        BackgroundWork(Work(), Work(), Work(), Work(), Work(), Work(),
                                       Work(), Work(), Work(), Work(), Work(), Work()),
                        np.array([])), False, dict(), dict())

                if step_key not in self.pending_aggressive_reencoding_optimized:
                    self.pending_aggressive_reencoding_optimized[step_key] = dict()

                if new_rg not in self.pending_aggressive_reencoding_optimized[step_key]:
                    self.pending_aggressive_reencoding_optimized[step_key][new_rg] = list()

                if step_key not in self.performed_aggressive_reencoding_optimized:
                    self.performed_aggressive_reencoding_optimized[step_key] = dict()

                if new_rg not in self.performed_aggressive_reencoding_optimized[step_key]:
                    self.performed_aggressive_reencoding_optimized[step_key][new_rg] = dict()

                if step_key not in self.pending_aggressive_reencoding_optimized_order:
                    self.pending_aggressive_reencoding_optimized_order[step_key] = list()

                if new_rg not in self.pending_aggressive_reencoding_optimized_order[step_key]:
                    self.pending_aggressive_reencoding_optimized_order[step_key].append(new_rg)

                self.pending_aggressive_reencoding_optimized[step_key][new_rg].append(disk)
        else:
            step_or_trickle_metrics, rgroup_wise_metrics, step_key = self._get_deployment_and_rgroup_metrics(disk)
            if self.running_disks[disk][1] != dg:
                return

            actual_change_date = datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=constants.REDUCED_USEFUL_LIFE_AGE)
            self._record_optimal_disk_days(disk, actual_change_date.strftime("%Y-%m-%d"), new_rg)

            if new_rg not in rgroup_wise_metrics:
                rgroup_wise_metrics[new_rg] = RgroupMetrics(DiskCategoryMetrics(
                    BackgroundWork(Work(), Work(), Work(), Work(), Work(), Work(),
                                   Work(), Work(), Work(), Work(), Work(), Work()),
                    np.array([])), False, dict(), dict())

            if step_key not in self.pending_aggressive_reencoding_optimized:
                self.pending_aggressive_reencoding_optimized[step_key] = dict()

            if new_rg not in self.pending_aggressive_reencoding_optimized[step_key]:
                self.pending_aggressive_reencoding_optimized[step_key][new_rg] = list()

            if step_key not in self.performed_aggressive_reencoding_optimized:
                self.performed_aggressive_reencoding_optimized[step_key] = dict()

            if new_rg not in self.performed_aggressive_reencoding_optimized[step_key]:
                self.performed_aggressive_reencoding_optimized[step_key][new_rg] = dict()

            if step_key not in self.pending_aggressive_reencoding_optimized_order:
                self.pending_aggressive_reencoding_optimized_order[step_key] = list()

            if new_rg not in self.pending_aggressive_reencoding_optimized_order[step_key]:
                self.pending_aggressive_reencoding_optimized_order[step_key].append(new_rg)

            self.pending_aggressive_reencoding_optimized[step_key][new_rg].append(disk)
        return step_key

    def reencode_aggressively_from_optimized_rgroup(self, dgroup, from_rgroup, to_rgroup,
                                                    background_io_allowed, date, step_key, urgent=False):
        cannot_delay_reencoding = False
        violation_age = -1

        if dgroup.deployment_type == constants.DeploymentType.TRICKLE:
            last_age_to_check = common.days_between(date, self.dgroup_wise_metrics[dgroup].last_canary_birthday)
        else:
            last_age_to_check = dgroup.min_sample_age + common.days_between(
                date, dgroup.latest_min_sample_age_revision)
        if (len(dgroup.cum_afr_array[dgroup.cp_list[-2].age_of_change:last_age_to_check]) > 0) and (
            np.max(dgroup.cum_afr_array[dgroup.cp_list[-2].age_of_change:last_age_to_check]
                   ) >= from_rgroup.tolerable_afr):
            cannot_delay_reencoding = True
            violation_age = dgroup.cp_list[-2].age_of_change + np.argmax(
                dgroup.cum_afr_array[dgroup.cp_list[-2].age_of_change:last_age_to_check])

        num_disks_reencoded = 0
        all_disks_reencoded = False

        dest_rg_list = self.pending_aggressive_reencoding_optimized[step_key][to_rgroup]

        total_reads_performed = 0
        total_writes_performed = 0

        while len(dest_rg_list) > 0 and ((background_io_allowed > 0) or (cannot_delay_reencoding is True)):
            disk = dest_rg_list[0]

            if disk not in self.running_disks:
                dest_rg_list.pop(0)
                continue
            if self.running_disks[disk][2] != from_rgroup:
                if dgroup.deployment_type == constants.DeploymentType.TRICKLE and (disk not in self.dgroup_wise_metrics[self.running_disks[disk][1]].canary_disks):
                    logging.info("Wrong Rgroup is being associated with disk. Serial number: %s, Rgroup expected:"
                                 " %s, Rgroup actual: %s", disk, from_rgroup.name, self.running_disks[disk][2].name)
                    raise LookupError
                dest_rg_list.pop(0)
                continue

            if step_key == 'trickle_pool' and dgroup.deployment_type == constants.DeploymentType.NAIVE:
                useful_life_reencoding_reads, useful_life_reencoding_writes = self._calculate_transcoding_cost(
                    (self.running_disks[disk][1]).capacity, from_rgroup, to_rgroup)
            elif step_key == 'trickle_pool':
                useful_life_reencoding_reads = from_rgroup.disks[disk][1]
                useful_life_reencoding_writes = useful_life_reencoding_reads
            else:
                useful_life_reencoding_reads = (from_rgroup.disks[disk][1] * (1.0 / from_rgroup.overhead))
                useful_life_reencoding_writes = useful_life_reencoding_reads * (float(to_rgroup.code_chunks) / (to_rgroup.data_chunks + to_rgroup.code_chunks))

            step_or_trickle_metrics, rgroup_wise_metrics, _ = self._get_deployment_and_rgroup_metrics(disk)
            self._init_daily_io_metrics_if_needed(step_key, step_or_trickle_metrics)

            # Check if the current AFR is >= tolerated AFR of the Rgroup
            # we are transitioning from. That would mean
            # we need to urgently re-encode all disks today.
            if urgent and cannot_delay_reencoding and violation_age > 0 and (common.days_between(date, self.running_disks[disk][0]) >= violation_age):
                step_or_trickle_metrics.background_work.urgent_reencoding_performed.reads += useful_life_reencoding_reads
                step_or_trickle_metrics.background_work.urgent_reencoding_performed.writes += \
                    useful_life_reencoding_writes
                step_or_trickle_metrics.background_work.urgent_reencoding_performed.io += (
                    useful_life_reencoding_reads + useful_life_reencoding_writes)

                background_io_allowed -= (useful_life_reencoding_reads + useful_life_reencoding_writes)
                dest_rg_list.pop(0)
                #### ACTUAL
                self._record_actual_disk_days(disk, date, to_rgroup)
                self.transition_stats[constants.TransitionType.BULK] += 1

                self.performed_aggressive_reencoding_optimized[step_key][to_rgroup][disk] = date
                num_disks_reencoded += 1
            elif background_io_allowed > (useful_life_reencoding_reads + useful_life_reencoding_writes):
                step_or_trickle_metrics.background_work.schedulable_reencoding_performed.reads += \
                    useful_life_reencoding_reads
                step_or_trickle_metrics.background_work.schedulable_reencoding_performed.writes += \
                    useful_life_reencoding_writes
                step_or_trickle_metrics.background_work.schedulable_reencoding_performed.io += (
                    useful_life_reencoding_reads + useful_life_reencoding_writes)

                self.transition_stats[constants.TransitionType.BULK] += 1

                total_reads_performed += useful_life_reencoding_reads
                total_writes_performed += useful_life_reencoding_writes

                background_io_allowed -= (useful_life_reencoding_reads + useful_life_reencoding_writes)
                dest_rg_list.pop(0)

                self._record_actual_disk_days(disk, date, to_rgroup)

                self.performed_aggressive_reencoding_optimized[step_key][to_rgroup][disk] = date
                num_disks_reencoded += 1
            else:
                background_io_allowed = 0
                if len(dest_rg_list) > 0:
                    break

        if len(dest_rg_list) == 0 and to_rgroup in self.performed_aggressive_reencoding_optimized[step_key]:
            # every intended disk has been aggressively reencoded
            # now we can reflect the useful life details in the metrics
            all_disks_reencoded = True
            for disk, dates in self.performed_aggressive_reencoding_optimized[step_key][to_rgroup].items():
                if disk not in self.running_disks or disk not in from_rgroup.disks:
                    continue

                step_or_trickle_metrics, rgroup_wise_metrics, _ = self._get_deployment_and_rgroup_metrics(disk)
                self._init_daily_io_metrics_if_needed(step_key, step_or_trickle_metrics)

                if urgent is False:
                    rgroup_wise_metrics[from_rgroup].potential_transcoding_capacity_needed -= self.running_disks[disk][1].capacity
                self.running_disks[disk] = (self.running_disks[disk][0], self.running_disks[disk][1], to_rgroup, properties.PHASE_OF_LIFE_USEFUL_LIFE)
                rgroup_wise_metrics[to_rgroup].disk_metrics.capacity += self.running_disks[disk][1].capacity
                rgroup_wise_metrics[from_rgroup].disk_metrics.capacity -= self.running_disks[disk][1].capacity
                rgroup_wise_metrics[from_rgroup].disk_metrics.num_running_disks -= 1
                rgroup_wise_metrics[to_rgroup].disk_metrics.num_running_disks += 1

                if urgent is False:
                    to_rgroup.disks[disk] = (date, from_rgroup.disks[disk][1])
                else:
                    to_rgroup.disks[disk] = (date, dgroup.capacity * constants.CLUSTER_FULLNESS_PERCENTAGE)
                del from_rgroup.disks[disk]
                self.latest_useful_life_rg[disk] = to_rgroup

            self.pending_aggressive_reencoding_optimized_order[step_key].remove(to_rgroup)
            del self.performed_aggressive_reencoding_optimized[step_key][to_rgroup]

        return background_io_allowed, all_disks_reencoded, num_disks_reencoded

    def type_2_reencoding(self, from_rgroup, step_key, type, date):
        num_disks_reencoded = 0

        all_disks_reencoded = False
        for dest_rg, dest_rg_list in self.pending_work[type][step_key].items():
            if len(dest_rg_list) < (dest_rg.data_chunks + dest_rg.code_chunks):
                continue

            while len(dest_rg_list) > 0:
                disk = dest_rg_list[0]
                if disk not in self.running_disks:
                    dest_rg_list.pop(0)
                    continue

                cannot_delay_reencoding = False
                violation_age = -1

                if type == constants.WorkType.NON_URGENT_WEAROUT or type == constants.WorkType.WEAROUT:
                    dgroup = self.running_disks[disk][1]
                    last_age_to_check = dgroup.min_sample_age + common.days_between(date, dgroup.latest_min_sample_age_revision)
                    if (len(dgroup.cum_afr_array[dgroup.cp_list[-2].age_of_change:last_age_to_check]) > 0) and (
                        np.max(dgroup.cum_afr_array[dgroup.cp_list[-2].age_of_change:last_age_to_check]
                               ) >= from_rgroup.tolerable_afr):
                        cannot_delay_reencoding = True
                        violation_age = dgroup.cp_list[-2].age_of_change + np.argmax(
                            dgroup.cum_afr_array[dgroup.cp_list[-2].age_of_change:last_age_to_check])

                useful_life_reencoding_reads = (from_rgroup.disks[disk][1] * (1.0 / from_rgroup.overhead))
                useful_life_reencoding_writes = useful_life_reencoding_reads * (float(dest_rg.code_chunks) / (dest_rg.data_chunks))
                
                step_or_trickle_metrics, rgroup_wise_metrics, _ = self._get_deployment_and_rgroup_metrics(disk)
                self._init_daily_io_metrics_if_needed(step_key, step_or_trickle_metrics)

                if (cannot_delay_reencoding and (common.days_between(date, self.running_disks[disk][0]) >= violation_age)) or (self.daily_step_wise_io_metrics[step_key]['allowed'] > (useful_life_reencoding_reads + useful_life_reencoding_writes)):
                    step_or_trickle_metrics.background_work.schedulable_reencoding_performed.reads += \
                        useful_life_reencoding_reads
                    step_or_trickle_metrics.background_work.schedulable_reencoding_performed.writes += \
                        useful_life_reencoding_writes
                    step_or_trickle_metrics.background_work.schedulable_reencoding_performed.io += (
                        useful_life_reencoding_reads + useful_life_reencoding_writes)

                    self.daily_step_wise_io_metrics[step_key]['allowed'] -= (useful_life_reencoding_reads + useful_life_reencoding_writes)
                    dest_rg_list.pop(0)

                    self._record_actual_disk_days(disk, date, dest_rg)
                    self.performed_work[type][step_key][dest_rg][disk] = date

                    if type == constants.WorkType.NON_URGENT_WEAROUT:
                        del self.convert_to_urgent[self.disks_viable_for_non_urgent_wearout[disk][3]][disk]

                    self.transition_stats[constants.TransitionType.BULK] += 1
                    num_disks_reencoded += 1
                else:
                    break

            if len(dest_rg_list) == 0:
                # every intended disk has been aggressively reencoded
                # now we can reflect the useful life details in the metrics
                for disk, dates in self.performed_work[type][step_key][dest_rg].items():
                    if disk not in self.running_disks:
                        continue
                    step_or_trickle_metrics, rgroup_wise_metrics, _ = self._get_deployment_and_rgroup_metrics(disk)
                    rgroup_wise_metrics[from_rgroup].potential_transcoding_capacity_needed -= self.running_disks[disk][1].capacity
                    rgroup_wise_metrics[dest_rg].potential_capacity_after_redundancy_management -= (self.running_disks[disk][1].capacity)
                    rgroup_wise_metrics[dest_rg].disk_metrics.capacity += self.running_disks[disk][1].capacity
                    rgroup_wise_metrics[from_rgroup].disk_metrics.capacity -= self.running_disks[disk][1].capacity
                    rgroup_wise_metrics[from_rgroup].disk_metrics.num_running_disks -= 1
                    rgroup_wise_metrics[dest_rg].disk_metrics.num_running_disks += 1
                    if type == constants.WorkType.INFANCY:
                        self.running_disks[disk] = (self.running_disks[disk][0], self.running_disks[disk][1], dest_rg, properties.PHASE_OF_LIFE_USEFUL_LIFE)
                        self.daily_cluster_metrics.total_disk_metrics.num_infancy_disks -= 1
                        self.daily_cluster_metrics.total_disk_metrics.num_useful_life_disks += 1
                        step_or_trickle_metrics.num_infancy_disks -= 1
                        step_or_trickle_metrics.num_useful_life_disks += 1
                        del self.disks_viable_for_useful_life[disk]
                    elif type == constants.WorkType.NON_URGENT_WEAROUT:
                        self.running_disks[disk] = (self.running_disks[disk][0], self.running_disks[disk][1], dest_rg, properties.PHASE_OF_LIFE_WEAROUT)
                        self.daily_cluster_metrics.total_disk_metrics.num_useful_life_disks -= 1
                        self.daily_cluster_metrics.total_disk_metrics.num_wearout_disks += 1
                        step_or_trickle_metrics.num_useful_life_disks -= 1
                        step_or_trickle_metrics.num_wearout_disks += 1
                        if disk in self.disks_viable_for_non_urgent_wearout:
                            del self.disks_viable_for_non_urgent_wearout[disk]
                    elif type == constants.WorkType.WEAROUT:
                        self.running_disks[disk] = (self.running_disks[disk][0], self.running_disks[disk][1], dest_rg, properties.PHASE_OF_LIFE_WEAROUT)
                        self.daily_cluster_metrics.total_disk_metrics.num_useful_life_disks -= 1
                        self.daily_cluster_metrics.total_disk_metrics.num_wearout_disks += 1
                        step_or_trickle_metrics.num_useful_life_disks -= 1
                        step_or_trickle_metrics.num_wearout_disks += 1
                        del self.disks_viable_for_wearout[disk]
                    if disk not in from_rgroup.disks:
                        logging.error("From rgroup = " + from_rgroup.name + ". The Rgroup the disk is in: " + self.running_disks[disk][2].name)
                    else:
                        dest_rg.disks[disk] = (date, from_rgroup.disks[disk][1])
                    del from_rgroup.disks[disk]

                    self.optimized_disk_days[disk] = (date, None)
                    self.latest_useful_life_rg[disk] = dest_rg

                del self.performed_work[type][step_key][dest_rg]
                all_disks_reencoded = True

        return all_disks_reencoded

    def _init_daily_io_metrics_if_needed(self, step_key, step_or_trickle_metrics):
        if step_key not in self.daily_step_wise_io_metrics:
            self.daily_step_wise_io_metrics[step_key] = dict()
            self.daily_step_wise_io_metrics[step_key]['total'] = float(constants.HDD_IO_BANDWIDTH * step_or_trickle_metrics.num_running_disks * 24 * 3600) / 1048576
            self.daily_step_wise_io_metrics[step_key]['allowed'] = self.daily_step_wise_io_metrics[step_key]['total'] * (constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE / 100.0)
            self.daily_step_wise_io_metrics[step_key]['used'] = 0.0
            self.daily_step_wise_io_metrics[step_key]['needed'] = 0.0
            logging.info("Num disks = " + str(step_or_trickle_metrics.num_running_disks) +
                         ", key = " + str(step_key) + " Total = " +
                         str(self.daily_step_wise_io_metrics[step_key]['total']) +
                         ", allowed = " + str(self.daily_step_wise_io_metrics[step_key]['allowed']))

    '''
    This function deals with all the performed encodings based on background io capacity available.
    '''
    def process_daily_transitions(self, date):
        self.daily_cluster_metrics.total_cluster_io_bandwidth = float(
            constants.HDD_IO_BANDWIDTH *
            self.daily_cluster_metrics.total_disk_metrics.num_running_disks * 24 * 3600) / 1048576
        self.daily_cluster_metrics.total_background_io_bandwidth_allowed = self.daily_cluster_metrics.total_cluster_io_bandwidth * (constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE / 100.0)
        self.daily_cluster_metrics.total_background_io_bandwidth_needed = 0.0
        self.daily_cluster_metrics.total_background_io_bandwidth_used = 0.0

        disks_transitioning_to_useful_life_today = list()
        disks_transitioning_to_wearout_today = list()
        disks_reconstructed_today = list()
        disks_decommissioned_today = list()

        # background_io_bandwidth_allowed = self.daily_cluster_metrics.total_background_io_bandwidth_allowed
        # total_io_bandwidth = self.daily_cluster_metrics.total_cluster_io_bandwidth

        # first check if its better to retire the whole Rgroup instead of transcoding.
        # first sort the rgroups by amount of work to be done.
        rgroups_by_capacity = {}
        for dg, date_dict in self.step_wise_metrics.items():
            for dt, tup in date_dict.items():
                rgroup_wise_metrics = tup[1]
                rgroups_by_capacity[(dg, dt)] = (list([]), rgroup_wise_metrics)
                for rg, rg_metric in rgroup_wise_metrics.items():
                    rgroups_by_capacity[(dg, dt)][0].append((rg_metric.disk_metrics.capacity, rg))
                rgroups_by_capacity[(dg, dt)][0].sort()
        rgroups_by_capacity['trickle_pool'] = (list([]), self.rgroup_wise_metrics)
        for rg, rg_metric in self.rgroup_wise_metrics.items():
            rgroups_by_capacity['trickle_pool'][0].append((rg_metric.disk_metrics.capacity, rg))
        rgroups_by_capacity['trickle_pool'][0].sort()

        # second, add non-urgent disks convertible to urgent to the urgent list, then start processing everything.
        if date in self.convert_to_urgent:
            logging.debug("Transferring %s disks to urgent on %s.", str(len(self.convert_to_urgent[date])), date)
            total_transitioning_disks = len(self.convert_to_urgent[date])
            for disk in self.convert_to_urgent[date]:
                self.report_disk_viable_for_wearout(disk, date, non_urgent_to_urgent=True,
                                                    total_disks_transitioning=total_transitioning_disks)
            del self.convert_to_urgent[date]

        # order of background operations is:
        # 1. reconstructions
        # 2. urgent transitions to wearout
        # 3. scrubbing
        # 4. non-urgent transitions to wearout
        # 5. decommissioning
        # 6. transitions to useful life
        # 7. aggressive reencoding of Dgroup disks from one optimized Rgroup to another

        # 1. reconstructions
        num_failed_disks_order = len(self.failed_disks_order)
        for i in range(0, num_failed_disks_order):
        # while len(self.failed_disks_order) > 0:
            disk = self.failed_disks_order[i]

            dg = self.failed_disks[disk][1]
            rg = self.failed_disks[disk][2]
            reconstruction_reads = dg.capacity * rg.data_chunks
            reconstruction_writes = dg.capacity

            step_or_trickle_metrics, rgroup_wise_metrics, step_key = self._get_deployment_and_rgroup_metrics(disk, failed=True)
            self._init_daily_io_metrics_if_needed(step_key, step_or_trickle_metrics)

            if self.daily_step_wise_io_metrics[step_key]['total'] >= (reconstruction_reads + reconstruction_writes):
                step_or_trickle_metrics.background_work.reconstruction_performed.reads += reconstruction_reads
                step_or_trickle_metrics.background_work.reconstruction_performed.writes += reconstruction_writes
                step_or_trickle_metrics.background_work.reconstruction_performed.io += reconstruction_reads + reconstruction_writes

                self.dgroup_wise_metrics[dg].disk_metrics.background_work.reconstruction_performed.reads += reconstruction_reads
                self.dgroup_wise_metrics[dg].disk_metrics.background_work.reconstruction_performed.writes += reconstruction_writes
                self.dgroup_wise_metrics[dg].disk_metrics.background_work.reconstruction_performed.io += reconstruction_reads + reconstruction_writes

                rgroup_wise_metrics[rg].disk_metrics.background_work.reconstruction_performed.reads += reconstruction_reads
                rgroup_wise_metrics[rg].disk_metrics.background_work.reconstruction_performed.writes += reconstruction_writes
                rgroup_wise_metrics[rg].disk_metrics.background_work.reconstruction_performed.io += reconstruction_reads + reconstruction_writes

                self.daily_step_wise_io_metrics[step_key]['allowed'] -= (reconstruction_reads + reconstruction_writes)
                self.daily_step_wise_io_metrics[step_key]['total'] -= (reconstruction_reads + reconstruction_writes)
                disks_reconstructed_today.append(disk)
                del self.failed_disks[disk]
            else:
                print(step_or_trickle_metrics)
                raise OverflowError
        del self.failed_disks_order
        self.failed_disks_order = list()

        # 2. urgent transitions to wearout
        to_rg = common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]
        num_disks_viable_for_wearout_order = len(self.disks_viable_for_wearout_order)
        disks_viable_for_wearout_order_incomplete = list()
        for i in range(0, num_disks_viable_for_wearout_order):
            disk = self.disks_viable_for_wearout_order[i]
            dg = self.running_disks[disk][1]
            rg = self.running_disks[disk][2]

            step_or_trickle_metrics, rgroup_wise_metrics, step_key = self._get_deployment_and_rgroup_metrics(disk)
            self._init_daily_io_metrics_if_needed(step_key, step_or_trickle_metrics)

            if step_key != 'trickle_pool':
                if step_key not in self.pending_work[constants.WorkType.WEAROUT]:
                    self.pending_work[constants.WorkType.WEAROUT][step_key] = dict()

                if to_rg not in self.pending_work[constants.WorkType.WEAROUT][step_key]:
                    self.pending_work[constants.WorkType.WEAROUT][step_key][to_rg] = list()

                if step_key not in self.performed_work[constants.WorkType.WEAROUT]:
                    self.performed_work[constants.WorkType.WEAROUT][step_key] = dict()

                if to_rg not in self.performed_work[constants.WorkType.WEAROUT][step_key]:
                    self.performed_work[constants.WorkType.WEAROUT][step_key][to_rg] = dict()

                self.pending_work[constants.WorkType.WEAROUT][step_key][to_rg].append(disk)
                self.steps_requiring_aggressive_reencoding_to_wearout[step_key] = rg
            else:

                wearout_reencoding_reads = self.disks_viable_for_wearout[disk][1]
                wearout_reencoding_writes = self.disks_viable_for_wearout[disk][2]

                if disk in self.disk_retired:
                    wearout_reencoding_reads = 0
                    wearout_reencoding_writes = 0

                if self.daily_step_wise_io_metrics[step_key]['total'] >= (
                    wearout_reencoding_reads + wearout_reencoding_writes):
                    age_today = (datetime.datetime.strptime(date, "%Y-%m-%d") -
                                 datetime.datetime.strptime(self.running_disks[disk][0], "%Y-%m-%d")).days
                    if (dg.latest_rup_cp == common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]) and (
                        age_today > dg.latest_rup_cp.age_of_change) and (
                        disk not in self.dgroup_wise_metrics[dg].disks_at_risk) and (
                        disk not in rg.disks_crossing_second_level_afr):
                        if dg.afr_array[age_today] > rg.tolerable_afr:
                            if disk in self.dgroup_wise_metrics[dg].canary_disks:
                                logging.info("canary, %s, %s, %s, %s, %s", disk, str(age_today),
                                             str(dg.afr_array[age_today]), str(rg.tolerable_afr), str(rg.name))
                            else:
                                logging.info("%s, %s, %s, %s, %s", disk, str(age_today),
                                             str(dg.afr_array[age_today]), str(rg.tolerable_afr), str(rg.name))
                                self.dgroup_wise_metrics[dg].disks_at_risk[disk] = date

                    step_or_trickle_metrics.background_work.urgent_reencoding_performed.reads += \
                        wearout_reencoding_reads
                    step_or_trickle_metrics.background_work.urgent_reencoding_performed.writes += \
                        wearout_reencoding_writes
                    step_or_trickle_metrics.background_work.urgent_reencoding_performed.io += (
                            wearout_reencoding_reads + wearout_reencoding_writes)

                    self.dgroup_wise_metrics[
                        dg].disk_metrics.background_work.urgent_reencoding_performed.reads += wearout_reencoding_reads
                    self.dgroup_wise_metrics[
                        dg].disk_metrics.background_work.urgent_reencoding_performed.writes += wearout_reencoding_writes
                    self.dgroup_wise_metrics[
                        dg].disk_metrics.background_work.urgent_reencoding_performed.io += (
                        wearout_reencoding_reads + wearout_reencoding_writes)

                    rgroup_wise_metrics[rg].disk_metrics.num_running_disks -= 1
                    rgroup_wise_metrics[to_rg].disk_metrics.num_running_disks += 1

                    rgroup_wise_metrics[to_rg].io_bandwidth = float(
                        constants.HDD_IO_BANDWIDTH * rgroup_wise_metrics[to_rg].disk_metrics.num_running_disks
                        * 24 * 3600) / 1048576
                    rgroup_wise_metrics[rg].io_bandwidth = float(
                        constants.HDD_IO_BANDWIDTH * rgroup_wise_metrics[rg].disk_metrics.num_running_disks
                        * 24 * 3600) / 1048576

                    self.dgroup_wise_metrics[dg].disk_metrics.num_useful_life_disks -= 1
                    self.dgroup_wise_metrics[dg].disk_metrics.num_wearout_disks += 1

                    if disk in self.dgroup_wise_metrics[dg].canary_disks:
                        self.dgroup_wise_metrics[dg].canary_disk_metrics.num_useful_life_disks -= 1
                        self.dgroup_wise_metrics[dg].canary_disk_metrics.num_wearout_disks += 1

                    rgroup_wise_metrics[to_rg].disk_metrics.capacity += dg.capacity
                    rgroup_wise_metrics[rg].disk_metrics.capacity -= dg.capacity

                    self.daily_cluster_metrics.total_disk_metrics.num_useful_life_disks -= 1
                    self.daily_cluster_metrics.total_disk_metrics.num_wearout_disks += 1

                    step_or_trickle_metrics.num_useful_life_disks -= 1
                    step_or_trickle_metrics.num_wearout_disks += 1

                    self.daily_step_wise_io_metrics[step_key]['allowed'] -= (wearout_reencoding_reads + wearout_reencoding_writes)
                    self.daily_step_wise_io_metrics[step_key]['total'] -= (wearout_reencoding_reads + wearout_reencoding_writes)

                    rgroup_wise_metrics[rg].disk_metrics.num_disks_transitioned_today += 1

                    rgroup_wise_metrics[rg].potential_transcoding_capacity_needed -= dg.capacity
                    rgroup_wise_metrics[to_rg].potential_capacity_after_redundancy_management -= dg.capacity

                    self.wearout_disks_order[disk] = date
                    disks_transitioning_to_wearout_today.append(disk)
                    del self.disks_viable_for_wearout[disk]

                    to_rg.disks[disk] = (date, rg.disks[disk][1])
                    del rg.disks[disk]

                    self.running_disks[disk] = (self.running_disks[disk][0], dg, to_rg, properties.PHASE_OF_LIFE_WEAROUT)

                    if disk in self.optimized_disk_days:
                        self.optimized_disk_days[disk] = (self.optimized_disk_days[disk][0], date)
                        self.optimal_optimized_disk_days[disk] = (self.optimal_optimized_disk_days[disk][0], date)
                    self._record_actual_disk_days(disk, date, common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"])

                    self.transition_stats[constants.TransitionType.DECOMMISSIONING] += 1
                else:
                    disks_viable_for_wearout_order_incomplete.append(disk)
                    continue
        self.disks_viable_for_wearout_order = disks_viable_for_wearout_order_incomplete
        for step_key, from_rg in self.steps_requiring_aggressive_reencoding_to_wearout.items():
            _ = self.type_2_reencoding(from_rg, step_key, constants.WorkType.WEAROUT, date)

        for s, v in self.daily_step_wise_io_metrics.items():
            if v['allowed'] < 0:
                v['allowed'] = 0

        # first try and see if any urgent Rgroup transitions are possible
        if date in self.urgent_transition_rg:
            for trans_tup in self.urgent_transition_rg[date]:
                if trans_tup[3] == 'trickle_pool':
                    self._init_daily_io_metrics_if_needed(trans_tup[3], self.daily_cluster_metrics.trickle_pool)
                else:
                    self._init_daily_io_metrics_if_needed(trans_tup[3], self.step_wise_metrics[trans_tup[3][0]][trans_tup[3][1]][0])
                self.daily_step_wise_io_metrics[trans_tup[3]]['allowed'], all_disks_reencoded, num_disks_reencoded = self.reencode_aggressively_from_optimized_rgroup(
                    trans_tup[0], trans_tup[1], trans_tup[2], self.daily_step_wise_io_metrics[trans_tup[3]]['allowed'], date, trans_tup[3], urgent=True)
                logging.debug("%s disks reencoded from %s to %s", str(num_disks_reencoded), trans_tup[1].name,
                             trans_tup[2].name)
                if not all_disks_reencoded:
                    tomorrow = (datetime.datetime.strptime(date, "%Y-%m-%d") +
                                datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                    self.mark_rgroup_change_transition_for_date(trans_tup[0], trans_tup[1],
                                                                trans_tup[2], trans_tup[3], tomorrow, urgent=True)

        for s, v in self.daily_step_wise_io_metrics.items():
            if v['allowed'] < 0:
                v['allowed'] = 0

        # 3. scrubbing
        self.daily_cluster_metrics.total_disk_metrics.background_work.scrubbing_needed.io += (
                self.daily_cluster_metrics.total_cluster_io_bandwidth * constants.SCRUBBING_RATE)

        self.daily_cluster_metrics.total_disk_metrics.background_work.scrubbing_performed.io += (
                self.daily_cluster_metrics.total_cluster_io_bandwidth * constants.SCRUBBING_RATE)

        # 4. non-urgent wearout
        to_rg = common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]
        num_disks_viable_for_non_urgent_wearout_order = len(self.disks_viable_for_non_urgent_wearout_order)
        disks_viable_for_non_urgent_wearout_order_incomplete = list()
        for i in range(0, num_disks_viable_for_non_urgent_wearout_order):
            disk = self.disks_viable_for_non_urgent_wearout_order[i]
            dg = self.running_disks[disk][1]
            rg = self.running_disks[disk][2]

            step_or_trickle_metrics, rgroup_wise_metrics, step_key = self._get_deployment_and_rgroup_metrics(disk)
            self._init_daily_io_metrics_if_needed(step_key, step_or_trickle_metrics)

            if step_key != 'trickle_pool':
                if step_key not in self.pending_work[constants.WorkType.NON_URGENT_WEAROUT]:
                    self.pending_work[constants.WorkType.NON_URGENT_WEAROUT][step_key] = dict()

                if to_rg not in self.pending_work[constants.WorkType.NON_URGENT_WEAROUT][step_key]:
                    self.pending_work[constants.WorkType.NON_URGENT_WEAROUT][step_key][to_rg] = list()

                if step_key not in self.performed_work[constants.WorkType.NON_URGENT_WEAROUT]:
                    self.performed_work[constants.WorkType.NON_URGENT_WEAROUT][step_key] = dict()

                if to_rg not in self.performed_work[constants.WorkType.NON_URGENT_WEAROUT][step_key]:
                    self.performed_work[constants.WorkType.NON_URGENT_WEAROUT][step_key][to_rg] = dict()

                self.pending_work[constants.WorkType.NON_URGENT_WEAROUT][step_key][to_rg].append(disk)
                self.steps_requiring_aggressive_reencoding_to_non_urgent_wearout[step_key] = rg
            else:
                non_urgent_wearout_reencoding_reads = self.disks_viable_for_non_urgent_wearout[disk][1]
                non_urgent_wearout_reencoding_writes = self.disks_viable_for_non_urgent_wearout[disk][2]

                if disk in self.disk_retired:
                    non_urgent_wearout_reencoding_reads = 0
                    non_urgent_wearout_reencoding_writes = 0

                if self.daily_step_wise_io_metrics[step_key]['allowed'] >= (non_urgent_wearout_reencoding_reads + non_urgent_wearout_reencoding_writes):
                    step_or_trickle_metrics.background_work.non_urgent_reencoding_performed.reads += \
                        non_urgent_wearout_reencoding_reads
                    step_or_trickle_metrics.background_work.non_urgent_reencoding_performed.writes += \
                        non_urgent_wearout_reencoding_writes
                    step_or_trickle_metrics.background_work.non_urgent_reencoding_performed.io += (
                            non_urgent_wearout_reencoding_reads + non_urgent_wearout_reencoding_writes)
                else:
                    disks_viable_for_non_urgent_wearout_order_incomplete.append(disk)
                    continue

                self.dgroup_wise_metrics[dg].disk_metrics.num_useful_life_disks -= 1
                self.dgroup_wise_metrics[dg].disk_metrics.num_wearout_disks += 1

                if disk in self.dgroup_wise_metrics[dg].canary_disks:
                    self.dgroup_wise_metrics[dg].canary_disk_metrics.num_useful_life_disks -= 1
                    self.dgroup_wise_metrics[dg].canary_disk_metrics.num_wearout_disks += 1

                rgroup_wise_metrics[rg].disk_metrics.num_running_disks -= 1
                rgroup_wise_metrics[to_rg].disk_metrics.num_running_disks += 1

                rgroup_wise_metrics[to_rg].io_bandwidth = float(
                    constants.HDD_IO_BANDWIDTH * rgroup_wise_metrics[to_rg].disk_metrics.num_running_disks
                    * 24 * 3600) / 1048576
                rgroup_wise_metrics[rg].io_bandwidth = float(
                    constants.HDD_IO_BANDWIDTH * rgroup_wise_metrics[rg].disk_metrics.num_running_disks
                    * 24 * 3600) / 1048576

                rgroup_wise_metrics[to_rg].disk_metrics.capacity += dg.capacity
                rgroup_wise_metrics[rg].disk_metrics.capacity -= dg.capacity

                rgroup_wise_metrics[rg].disk_metrics.num_disks_transitioned_today += 1

                rgroup_wise_metrics[rg].potential_transcoding_capacity_needed -= dg.capacity
                rgroup_wise_metrics[to_rg].potential_capacity_after_redundancy_management -= dg.capacity

                self.daily_cluster_metrics.total_disk_metrics.num_useful_life_disks -= 1
                self.daily_cluster_metrics.total_disk_metrics.num_wearout_disks += 1

                step_or_trickle_metrics.num_useful_life_disks -= 1
                step_or_trickle_metrics.num_wearout_disks += 1

                self.daily_step_wise_io_metrics[step_key]['allowed'] -= (
                    non_urgent_wearout_reencoding_reads + non_urgent_wearout_reencoding_writes)

                self.non_urgent_wearout_disks_order[disk] = date

                if disk not in rg.disks_crossing_second_level_afr:
                    del self.convert_to_urgent[self.disks_viable_for_non_urgent_wearout[disk][3]][disk]

                del self.disks_viable_for_non_urgent_wearout[disk]
                disks_transitioning_to_wearout_today.append(disk)

                to_rg.disks[disk] = (date, rg.disks[disk][1])
                del rg.disks[disk]

                self.running_disks[disk] = (self.running_disks[disk][0], dg, to_rg, properties.PHASE_OF_LIFE_WEAROUT)

                if disk in self.optimized_disk_days:
                    self.optimized_disk_days[disk] = (self.optimized_disk_days[disk][0], date)
                    self.optimal_optimized_disk_days[disk] = (self.optimal_optimized_disk_days[disk][0], date)

                self._record_actual_disk_days(disk, date, common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"])
                self.transition_stats[constants.TransitionType.DECOMMISSIONING] += 1

        self.disks_viable_for_non_urgent_wearout_order = disks_viable_for_non_urgent_wearout_order_incomplete
        for step_key, from_rg in self.steps_requiring_aggressive_reencoding_to_non_urgent_wearout.items():
            _ = self.type_2_reencoding(from_rg, step_key, constants.WorkType.NON_URGENT_WEAROUT, date)

        # 5. decommissioning
        num_disks_viable_for_decommissioning_order = len(self.disks_viable_for_decommissioning_order)
        disks_viable_for_decommissioning_order_incomplete = list()
        for i in range(0, num_disks_viable_for_decommissioning_order):
            disk = self.disks_viable_for_decommissioning_order[i]
            dg = self.running_disks[disk][1]
            rg = self.running_disks[disk][2]

            decommissioning_reads = dg.capacity
            decommissioning_writes = dg.capacity

            step_or_trickle_metrics, rgroup_wise_metrics, step_key = self._get_deployment_and_rgroup_metrics(disk)
            self._init_daily_io_metrics_if_needed(step_key, step_or_trickle_metrics)

            if self.daily_step_wise_io_metrics[step_key]['allowed'] >= (decommissioning_reads + decommissioning_writes):
                step_or_trickle_metrics.background_work.decommissioning_performed.reads += decommissioning_reads
                step_or_trickle_metrics.background_work.decommissioning_performed.writes += decommissioning_writes
                step_or_trickle_metrics.background_work.decommissioning_performed.io += (decommissioning_reads + decommissioning_writes)

                self.dgroup_wise_metrics[dg].disk_metrics.background_work.decommissioning_performed.reads += decommissioning_reads
                self.dgroup_wise_metrics[
                    dg].disk_metrics.background_work.decommissioning_performed.writes += decommissioning_writes
                self.dgroup_wise_metrics[
                    dg].disk_metrics.background_work.decommissioning_performed.io += (decommissioning_reads + decommissioning_writes)

                rgroup_wise_metrics[rg].disk_metrics.background_work.decommissioning_performed.reads += decommissioning_reads
                rgroup_wise_metrics[
                    rg].disk_metrics.background_work.decommissioning_performed.writes += decommissioning_writes
                rgroup_wise_metrics[
                    rg].disk_metrics.background_work.decommissioning_performed.io += (decommissioning_reads + decommissioning_writes)

                self.dgroup_wise_metrics[dg].disk_metrics.num_running_disks -= 1
                rgroup_wise_metrics[rg].disk_metrics.num_running_disks -= 1
                self.daily_cluster_metrics.total_disk_metrics.num_running_disks -= 1
                step_or_trickle_metrics.num_running_disks -= 1

                self.dgroup_wise_metrics[dg].disk_metrics.num_decommissioned_disks += 1
                rgroup_wise_metrics[rg].disk_metrics.num_decommissioned_disks += 1
                self.daily_cluster_metrics.total_disk_metrics.num_decommissioned_disks += 1
                step_or_trickle_metrics.num_decommissioned_disks += 1

                if disk in self.dgroup_wise_metrics[dg].canary_disks:
                    self.dgroup_wise_metrics[dg].canary_disk_metrics.num_running_disks -= 1
                    self.dgroup_wise_metrics[dg].canary_disk_metrics.num_decommissioned_disks += 1

                self.dgroup_wise_metrics[dg].disk_metrics.capacity -= dg.capacity
                rgroup_wise_metrics[rg].disk_metrics.capacity -= dg.capacity
                self.daily_cluster_metrics.total_disk_metrics.capacity -= dg.capacity
                step_or_trickle_metrics.capacity -= dg.capacity

                self._record_actual_disk_days(disk, date, common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"], dead=1)

                self.dgroup_wise_metrics[dg].io_bandwidth = float(
                    constants.HDD_IO_BANDWIDTH * self.dgroup_wise_metrics[dg].disk_metrics.num_running_disks
                    * 24 * 3600) / 1048576
                rgroup_wise_metrics[rg].io_bandwidth = float(
                    constants.HDD_IO_BANDWIDTH * rgroup_wise_metrics[rg].disk_metrics.num_running_disks
                    * 24 * 3600) / 1048576
                self.daily_cluster_metrics.io_bandwidth = float(
                    constants.HDD_IO_BANDWIDTH * self.daily_cluster_metrics.total_disk_metrics.num_running_disks
                    * 24 * 3600) / 1048576
                self.daily_step_wise_io_metrics[step_key]['total'] = float(
                    constants.HDD_IO_BANDWIDTH * step_or_trickle_metrics.num_running_disks
                    * 24 * 3600) / 1048576

                self.daily_step_wise_io_metrics[step_key]['allowed'] -= decommissioning_reads + decommissioning_writes
                disks_decommissioned_today.append(disk)
                self.decommissioned_disks_order[disk] = date
                del self.disks_viable_for_decommissioning[disk]

                phase_of_life = self.running_disks[disk][3]
                if disk in self.disks_viable_for_useful_life:
                    rgroup_wise_metrics[
                        self.disks_viable_for_useful_life[disk][1]].potential_capacity_after_redundancy_management -= dg.capacity
                    if step_key != 'trickle_pool' and self.disks_viable_for_useful_life[disk][1] in self.performed_work[constants.WorkType.INFANCY][step_key] and disk in self.performed_work[constants.WorkType.INFANCY][step_key][self.disks_viable_for_useful_life[disk][1]]:
                        del self.performed_work[constants.WorkType.INFANCY][step_key][self.disks_viable_for_useful_life[disk][1]][disk]
                    elif disk in self.disks_viable_for_useful_life_order:
                        self.disks_viable_for_useful_life_order.remove(disk)
                    elif dg.deployment_type == constants.DeploymentType.STEP:
                        for dest_rg, dest_rg_list in self.pending_work[constants.WorkType.INFANCY][step_key].items():
                            if disk in dest_rg_list:
                                dest_rg_list.remove(disk)
                    del self.disks_viable_for_useful_life[disk]
                elif disk in self.disks_viable_for_wearout:
                    rgroup_wise_metrics[common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]].potential_capacity_after_redundancy_management -= dg.capacity
                    if step_key != 'trickle_pool' and self.disks_viable_for_wearout[disk][1] in self.performed_work[constants.WorkType.WEAROUT][step_key] and disk in self.performed_work[constants.WorkType.WEAROUT][step_key][self.disks_viable_for_wearout[disk][1]]:
                        del self.performed_work[constants.WorkType.WEAROUT][step_key][self.disks_viable_for_wearout[disk][1]][disk]
                    elif disk in self.disks_viable_for_wearout_order:
                        self.disks_viable_for_wearout_order.remove(disk)
                    elif dg.deployment_type == constants.DeploymentType.STEP:
                        for dest_rg, dest_rg_list in self.pending_work[constants.WorkType.WEAROUT][step_key].items():
                            if disk in dest_rg_list:
                                dest_rg_list.remove(disk)
                    del self.disks_viable_for_wearout[disk]
                elif disk in self.disks_viable_for_non_urgent_wearout:
                    rgroup_wise_metrics[common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]].potential_capacity_after_redundancy_management -= dg.capacity
                    non_urgent_wearout_date = self.disks_viable_for_non_urgent_wearout[disk][0]
                    convert_to_urgent_date = (datetime.datetime.strptime(non_urgent_wearout_date, "%Y-%m-%d") +
                                              datetime.timedelta(days=constants.REDUCED_USEFUL_LIFE_AGE)).strftime(
                        "%Y-%m-%d")
                    if convert_to_urgent_date in self.convert_to_urgent and disk in self.convert_to_urgent[convert_to_urgent_date]:
                        del self.convert_to_urgent[convert_to_urgent_date][disk]
                    if step_key != 'trickle_pool' and self.disks_viable_for_non_urgent_wearout[disk][1] in self.performed_work[constants.WorkType.NON_URGENT_WEAROUT][step_key] and disk in self.performed_work[constants.WorkType.NON_URGENT_WEAROUT][step_key][self.disks_viable_for_wearout[disk][1]]:
                        del self.performed_work[constants.WorkType.NON_URGENT_WEAROUT][step_key][self.disks_viable_for_non_urgent_wearout[disk][1]][disk]
                    elif disk in self.disks_viable_for_non_urgent_wearout_order:
                        self.disks_viable_for_non_urgent_wearout_order.remove(disk)
                    elif dg.deployment_type == constants.DeploymentType.STEP:
                        for dest_rg, dest_rg_list in self.pending_work[constants.WorkType.NON_URGENT_WEAROUT][step_key].items():
                            if disk in dest_rg_list:
                                dest_rg_list.remove(disk)
                    del self.disks_viable_for_non_urgent_wearout[disk]

                if phase_of_life == properties.PHASE_OF_LIFE_INFANCY:
                    self.daily_cluster_metrics.total_disk_metrics.num_infancy_disks -= 1
                    step_or_trickle_metrics.num_infancy_disks -= 1
                    self.dgroup_wise_metrics[dg].disk_metrics.num_infancy_disks -= 1
                    if disk in self.dgroup_wise_metrics[dg].canary_disks:
                        self.dgroup_wise_metrics[dg].canary_disk_metrics.num_infancy_disks -= 1
                elif phase_of_life == properties.PHASE_OF_LIFE_USEFUL_LIFE:
                    self.daily_cluster_metrics.total_disk_metrics.num_useful_life_disks -= 1
                    step_or_trickle_metrics.num_useful_life_disks -= 1
                    self.dgroup_wise_metrics[dg].disk_metrics.num_useful_life_disks -= 1
                    if disk in self.dgroup_wise_metrics[dg].canary_disks:
                        self.dgroup_wise_metrics[dg].canary_disk_metrics.num_useful_life_disks -= 1
                elif phase_of_life == properties.PHASE_OF_LIFE_WEAROUT:
                    self.daily_cluster_metrics.total_disk_metrics.num_wearout_disks -= 1
                    step_or_trickle_metrics.num_wearout_disks -= 1
                    self.dgroup_wise_metrics[dg].disk_metrics.num_wearout_disks -= 1
                    if disk in self.dgroup_wise_metrics[dg].canary_disks:
                        self.dgroup_wise_metrics[dg].canary_disk_metrics.num_wearout_disks -= 1

                if disk in self.dgroup_wise_metrics[dg].canary_disks:
                    del self.dgroup_wise_metrics[dg].canary_disks[disk]
                del self.running_disks[disk]

                del rg.disks[disk]

                if disk in self.optimized_disk_days:
                    self.optimized_disk_days[disk] = (self.optimized_disk_days[disk][0], date)
                    self.optimal_optimized_disk_days[disk] = (self.optimal_optimized_disk_days[disk][0], date)
            else:
                disks_viable_for_decommissioning_order_incomplete.append(disk)
                continue
        self.disks_viable_for_decommissioning_order = disks_viable_for_decommissioning_order_incomplete

        # 6. transitions to useful life
        from_rg = common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]
        num_disks_viable_for_useful_life_order = len(self.disks_viable_for_useful_life_order)
        disks_viable_for_useful_life_order_incomplete = list()
        for i in range(0, num_disks_viable_for_useful_life_order):
            disk = self.disks_viable_for_useful_life_order[i]
            dg = self.running_disks[disk][1]
            rg = self.disks_viable_for_useful_life[disk][1]

            useful_life_reencoding_reads = self.disks_viable_for_useful_life[disk][2]
            useful_life_reencoding_writes = self.disks_viable_for_useful_life[disk][3]

            step_or_trickle_metrics, rgroup_wise_metrics, step_key = self._get_deployment_and_rgroup_metrics(disk)
            self._init_daily_io_metrics_if_needed(step_key, step_or_trickle_metrics)

            if step_key != 'trickle_pool':
                if step_key not in self.pending_work[constants.WorkType.INFANCY]:
                    self.pending_work[constants.WorkType.INFANCY][step_key] = dict()

                if rg not in self.pending_work[constants.WorkType.INFANCY][step_key]:
                    self.pending_work[constants.WorkType.INFANCY][step_key][rg] = list()

                if step_key not in self.performed_work[constants.WorkType.INFANCY]:
                    self.performed_work[constants.WorkType.INFANCY][step_key] = dict()

                if rg not in self.performed_work[constants.WorkType.INFANCY][step_key]:
                    self.performed_work[constants.WorkType.INFANCY][step_key][rg] = dict()

                self.pending_work[constants.WorkType.INFANCY][step_key][rg].append(disk)
                self.steps_requiring_aggressive_reencoding_from_infancy[step_key] = from_rg
            else:
                if self.daily_step_wise_io_metrics[step_key]['allowed'] >= (useful_life_reencoding_reads + useful_life_reencoding_writes):
                    age_today = (datetime.datetime.strptime(date, "%Y-%m-%d") -
                                 datetime.datetime.strptime(self.running_disks[disk][0], "%Y-%m-%d")).days
                    if (dg.latest_rup_cp == common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]) and (
                        age_today > dg.latest_rup_cp.age_of_change) and (
                        disk not in self.dgroup_wise_metrics[dg].disks_at_risk):
                        raise ValueError

                    step_or_trickle_metrics.background_work.schedulable_reencoding_performed.reads += useful_life_reencoding_reads
                    step_or_trickle_metrics.background_work.schedulable_reencoding_performed.writes += useful_life_reencoding_writes
                    step_or_trickle_metrics.background_work.schedulable_reencoding_performed.io += (
                            useful_life_reencoding_reads + useful_life_reencoding_writes)

                    self.dgroup_wise_metrics[
                        dg].disk_metrics.background_work.schedulable_reencoding_performed.reads += useful_life_reencoding_reads
                    self.dgroup_wise_metrics[
                        dg].disk_metrics.background_work.schedulable_reencoding_performed.writes += useful_life_reencoding_writes
                    self.dgroup_wise_metrics[
                        dg].disk_metrics.background_work.schedulable_reencoding_performed.io += (
                            useful_life_reencoding_reads + useful_life_reencoding_writes)

                    self.dgroup_wise_metrics[dg].disk_metrics.num_infancy_disks -= 1
                    self.dgroup_wise_metrics[dg].disk_metrics.num_useful_life_disks += 1

                    rgroup_wise_metrics[from_rg].disk_metrics.num_running_disks -= 1
                    rgroup_wise_metrics[rg].disk_metrics.num_running_disks += 1

                    rgroup_wise_metrics[from_rg].disk_metrics.num_disks_transitioned_today += 1

                    rgroup_wise_metrics[from_rg].potential_transcoding_capacity_needed -= dg.capacity
                    rgroup_wise_metrics[rg].potential_capacity_after_redundancy_management -= dg.capacity

                    if disk in self.dgroup_wise_metrics[dg].canary_disks:
                        self.dgroup_wise_metrics[dg].canary_disk_metrics.num_infancy_disks -= 1
                        self.dgroup_wise_metrics[dg].canary_disk_metrics.num_useful_life_disks += 1

                    rgroup_wise_metrics[from_rg].io_bandwidth = float(
                        constants.HDD_IO_BANDWIDTH * rgroup_wise_metrics[
                            from_rg].disk_metrics.num_running_disks * 24 * 3600) / 1048576
                    rgroup_wise_metrics[rg].io_bandwidth = float(
                        constants.HDD_IO_BANDWIDTH * rgroup_wise_metrics[rg].disk_metrics.num_running_disks
                        * 24 * 3600) / 1048576

                    rgroup_wise_metrics[rg].disk_metrics.capacity += dg.capacity
                    rgroup_wise_metrics[from_rg].disk_metrics.capacity -= dg.capacity

                    self.daily_cluster_metrics.total_disk_metrics.num_infancy_disks -= 1
                    self.daily_cluster_metrics.total_disk_metrics.num_useful_life_disks += 1

                    step_or_trickle_metrics.num_infancy_disks -= 1
                    step_or_trickle_metrics.num_useful_life_disks += 1

                    self.daily_step_wise_io_metrics[step_key]['allowed'] -= (useful_life_reencoding_reads + useful_life_reencoding_writes)
                    self.useful_life_disks_order[disk] = date
                    disks_transitioning_to_useful_life_today.append(disk)
                    del self.disks_viable_for_useful_life[disk]

                    self.running_disks[disk] = (self.running_disks[disk][0], self.running_disks[disk][1], rg,
                                                properties.PHASE_OF_LIFE_USEFUL_LIFE)

                    self.latest_useful_life_rg[disk] = rg

                    rg.disks[disk] = (date, from_rg.disks[disk][1])
                    del from_rg.disks[disk]

                    self.optimized_disk_days[disk] = (date, None)
                    self._record_actual_disk_days(disk, date, rg)
                    self.transition_stats[constants.TransitionType.DECOMMISSIONING] += 1
                else:
                    disks_viable_for_useful_life_order_incomplete.append(disk)
                    continue
        self.disks_viable_for_useful_life_order = disks_viable_for_useful_life_order_incomplete

        for step_key, from_rg in self.steps_requiring_aggressive_reencoding_from_infancy.items():
            _ = self.type_2_reencoding(from_rg, step_key, constants.WorkType.INFANCY, date)

        for dg, date_dict in self.step_wise_metrics.items():
            for dt, tup in date_dict.items():
                rgroup_wise_metrics = tup[1]

                # Add the cluster metrics object to the the longitudinal cluster metrics.
                for rg, rg_metric in rgroup_wise_metrics.items():
                    if rg_metric.disk_metrics.num_disks_transitioned_today > 0:
                        rg_metric.disk_metrics.last_month_transitioned_disks = np.append(
                            rg_metric.disk_metrics.last_month_transitioned_disks,
                            [rg_metric.disk_metrics.num_disks_transitioned_today])
                    if rg_metric.disk_metrics.num_running_disks < 0:
                        print(date, rg.name, rg_metric)
                        raise ValueError

                for rg, rg_metric in rgroup_wise_metrics.items():
                    if rg_metric.disk_metrics.last_month_transitioned_disks.shape[0] > 0:
                        rows_to_average_over = max(rg_metric.disk_metrics.last_month_transitioned_disks.shape[0], 30)
                        rg_metric.disk_metrics.avg_disks_transitioned_per_day = int(np.average(
                            rg_metric.disk_metrics.last_month_transitioned_disks[int(rows_to_average_over * -1):]))
                        rg_metric.disk_metrics.num_disks_transitioned_today = 0

        # the following snippet is for handling the trickle pool disks
        for rg, rg_metric in self.rgroup_wise_metrics.items():
            if rg_metric.disk_metrics.num_disks_transitioned_today > 0:
                rg_metric.disk_metrics.last_month_transitioned_disks = np.append(
                    rg_metric.disk_metrics.last_month_transitioned_disks,
                    [rg_metric.disk_metrics.num_disks_transitioned_today])
            if rg_metric.disk_metrics.num_running_disks < 0:
                print(date, rg.name, rg_metric)
                raise ValueError

        for rg, rg_metric in self.rgroup_wise_metrics.items():
            if rg_metric.disk_metrics.last_month_transitioned_disks.shape[0] > 0:
                rows_to_average_over = max(rg_metric.disk_metrics.last_month_transitioned_disks.shape[0], 30)
                rg_metric.disk_metrics.avg_disks_transitioned_per_day = int(np.average(
                    rg_metric.disk_metrics.last_month_transitioned_disks[int(rows_to_average_over * -1):]))
                rg_metric.disk_metrics.num_disks_transitioned_today = 0

        for dg, date_dict in self.step_wise_metrics.items():
            for dt, tup in date_dict.items():
                v = tup[0]
                self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_needed.reads += v.background_work.reconstruction_needed.reads
                self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_needed.writes += v.background_work.reconstruction_needed.writes
                self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_needed.io += v.background_work.reconstruction_needed.io
                self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_performed.reads += v.background_work.reconstruction_performed.reads
                self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_performed.writes += v.background_work.reconstruction_performed.writes
                self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_performed.io += v.background_work.reconstruction_performed.io
                self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_needed.reads += v.background_work.urgent_reencoding_needed.reads
                self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_needed.writes += v.background_work.urgent_reencoding_needed.writes
                self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_needed.io += v.background_work.urgent_reencoding_needed.io
                self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_performed.reads += v.background_work.urgent_reencoding_performed.reads
                self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_performed.writes += v.background_work.urgent_reencoding_performed.writes
                self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_performed.io += v.background_work.urgent_reencoding_performed.io
                self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_needed.reads += v.background_work.non_urgent_reencoding_needed.reads
                self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_needed.writes += v.background_work.non_urgent_reencoding_needed.writes
                self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_needed.io += v.background_work.non_urgent_reencoding_needed.io
                self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_performed.reads += v.background_work.non_urgent_reencoding_performed.reads
                self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_performed.writes += v.background_work.non_urgent_reencoding_performed.writes
                self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_performed.io += v.background_work.non_urgent_reencoding_performed.io
                self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_needed.reads += v.background_work.schedulable_reencoding_needed.reads
                self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_needed.writes += v.background_work.schedulable_reencoding_needed.writes
                self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_needed.io += v.background_work.schedulable_reencoding_needed.io
                self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_performed.reads += v.background_work.schedulable_reencoding_performed.reads
                self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_performed.writes += v.background_work.schedulable_reencoding_performed.writes
                self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_performed.io += v.background_work.schedulable_reencoding_performed.io
                self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_needed.reads += v.background_work.decommissioning_needed.reads
                self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_needed.writes += v.background_work.decommissioning_needed.writes
                self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_needed.io += v.background_work.decommissioning_needed.io
                self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_performed.reads += v.background_work.decommissioning_performed.reads
                self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_performed.writes += v.background_work.decommissioning_performed.writes
                self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_performed.io += v.background_work.decommissioning_performed.io

        self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_needed.reads += self.daily_cluster_metrics.trickle_pool.background_work.reconstruction_needed.reads
        self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_needed.writes += self.daily_cluster_metrics.trickle_pool.background_work.reconstruction_needed.writes
        self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_needed.io += self.daily_cluster_metrics.trickle_pool.background_work.reconstruction_needed.io
        self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_performed.reads += self.daily_cluster_metrics.trickle_pool.background_work.reconstruction_performed.reads
        self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_performed.writes += self.daily_cluster_metrics.trickle_pool.background_work.reconstruction_performed.writes
        self.daily_cluster_metrics.total_disk_metrics.background_work.reconstruction_performed.io += self.daily_cluster_metrics.trickle_pool.background_work.reconstruction_performed.io
        self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_needed.reads += self.daily_cluster_metrics.trickle_pool.background_work.urgent_reencoding_needed.reads
        self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_needed.writes += self.daily_cluster_metrics.trickle_pool.background_work.urgent_reencoding_needed.writes
        self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_needed.io += self.daily_cluster_metrics.trickle_pool.background_work.urgent_reencoding_needed.io
        self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_performed.reads += self.daily_cluster_metrics.trickle_pool.background_work.urgent_reencoding_performed.reads
        self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_performed.writes += self.daily_cluster_metrics.trickle_pool.background_work.urgent_reencoding_performed.writes
        self.daily_cluster_metrics.total_disk_metrics.background_work.urgent_reencoding_performed.io += self.daily_cluster_metrics.trickle_pool.background_work.urgent_reencoding_performed.io
        self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_needed.reads += self.daily_cluster_metrics.trickle_pool.background_work.non_urgent_reencoding_needed.reads
        self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_needed.writes += self.daily_cluster_metrics.trickle_pool.background_work.non_urgent_reencoding_needed.writes
        self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_needed.io += self.daily_cluster_metrics.trickle_pool.background_work.non_urgent_reencoding_needed.io
        self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_performed.reads += self.daily_cluster_metrics.trickle_pool.background_work.non_urgent_reencoding_performed.reads
        self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_performed.writes += self.daily_cluster_metrics.trickle_pool.background_work.non_urgent_reencoding_performed.writes
        self.daily_cluster_metrics.total_disk_metrics.background_work.non_urgent_reencoding_performed.io += self.daily_cluster_metrics.trickle_pool.background_work.non_urgent_reencoding_performed.io
        self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_needed.reads += self.daily_cluster_metrics.trickle_pool.background_work.schedulable_reencoding_needed.reads
        self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_needed.writes += self.daily_cluster_metrics.trickle_pool.background_work.schedulable_reencoding_needed.writes
        self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_needed.io += self.daily_cluster_metrics.trickle_pool.background_work.schedulable_reencoding_needed.io
        self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_performed.reads += self.daily_cluster_metrics.trickle_pool.background_work.schedulable_reencoding_performed.reads
        self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_performed.writes += self.daily_cluster_metrics.trickle_pool.background_work.schedulable_reencoding_performed.writes
        self.daily_cluster_metrics.total_disk_metrics.background_work.schedulable_reencoding_performed.io += self.daily_cluster_metrics.trickle_pool.background_work.schedulable_reencoding_performed.io
        self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_needed.reads += self.daily_cluster_metrics.trickle_pool.background_work.decommissioning_needed.reads
        self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_needed.writes += self.daily_cluster_metrics.trickle_pool.background_work.decommissioning_needed.writes
        self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_needed.io += self.daily_cluster_metrics.trickle_pool.background_work.decommissioning_needed.io
        self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_performed.reads += self.daily_cluster_metrics.trickle_pool.background_work.decommissioning_performed.reads
        self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_performed.writes += self.daily_cluster_metrics.trickle_pool.background_work.decommissioning_performed.writes
        self.daily_cluster_metrics.total_disk_metrics.background_work.decommissioning_performed.io += self.daily_cluster_metrics.trickle_pool.background_work.decommissioning_performed.io

        self.metrics.save_daily_stats(self.day, self.daily_cluster_metrics,
                                      self.dgroup_wise_metrics, self.rgroup_wise_metrics, self.step_wise_metrics)

        self.day += 1
