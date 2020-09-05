#!/usr/local/bin/python3

# This is the main driver file of the simulator. The simulator proceeds by date,
# and depending on the schedule of disk deployment and disk retirement,
# calculates the total data movement, additional I/O, etc. for
# implementing HeART.

import sys
from datasets import Backblaze
from datasets import Google
import constants
import datetime
from dgroups import DGroup
from dgroups import ChangePointDetails
from rgroups import RGroup
import common
import logging
from transcoding_policies.implementations.naive import Naive
from transcoding_policies.implementations.decommission_and_transition import Decommission
from transcoding_policies.implementations.naive_with_intra_batch_reads import NaiveWithIntraBatchReads

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
import os
import pandas as pd
import numpy as np
import properties
from ast import literal_eval as make_tuple
import matplotlib.patches as mpatches
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker
from tqdm import tqdm


def monitor_by_date(dgroups, dataset):
    all_dgroups = ', '.join("'{0}'".format(dg) for dg in list(dgroups.keys()))
    print("loading dataset...")
    all_disks_deployment_dates = dataset.get_all_deployment_dates(dgroups=all_dgroups)
    deployment_batches = {}
    disk_map = dataset.get_disks_in_memory(dgroups=all_dgroups)
    print("dataset loaded!")
    print("----------------------------------------")
    startdate = all_disks_deployment_dates[0]
    enddate = constants.END_DATE
    dt_range = common.daterange(datetime.datetime.strptime(startdate, "%Y-%m-%d"),
                                datetime.datetime.strptime(enddate, "%Y-%m-%d"))
    disk_deployment_order = {}
    disk_group_useful_life_afr = {}
    disk_group_wearout_date = {}
    last_disk_modified = {}
    disk_group_infancy_age = {}
    disk_chernoff_estimate = {}
    disk_group_next_checkup = {}
    disk_group_last_analysis = {}
    disk_batch_size = {}
    disk_group_step_details = {}
    useful_life_scheme_map = {}

    min_age_of_dead_disk = {}

    prev_rgroup = dict()
    prev_old_age_start_date = dict()

    for dg, dg_instance in dgroups.items():
        disk_deployment_order[dg] = []

        disk_chernoff_estimate[dg] = 0

        prev_rgroup[dg] = constants.DEFAULT_REDUNDANCY_SCHEME
        prev_old_age_start_date[dg] = -1

    for dt in all_disks_deployment_dates:
        # this loop populates the disk_map with the disks that are deployed with
        # the key being the date on which they were deployed.
        disk_batch = list()
        for disk, values in disk_map.items():
            if values[2] == dt:
                disk_batch.append(disk)
        deployment_batches[dt] = disk_batch

    transcoding_policies = dict()
    for p in constants.transcoding_policies:
        # initializing the transcoding policies
        # specified as an array in constants.py
        transcoding_policies[p] = eval(p)(startdate, enddate)

    decom_disk_details = dataset.get_all_decommissioned_disks(
        disk_groups=all_dgroups)
    expired_disk_details = dataset.get_all_expired_disks(disk_groups=all_dgroups)

    print("starting simulation...")
    with tqdm(total=int((datetime.datetime.strptime(enddate, "%Y-%m-%d") - datetime.datetime.strptime(startdate, "%Y-%m-%d")).days) + 1) as pbar:
        for dt in dt_range:
            # process changes in the cluster for each date
            cur_date_str = dt.strftime("%Y-%m-%d")
            logging.info("Processing date %s...", cur_date_str)

            for dg, dg_instance in dgroups.items():
                min_age_of_dead_disk[dg] = -1

            # check if there are any new disks being deployed on this day
            if cur_date_str in deployment_batches:
                for dg, dg_instance in dgroups.items():
                    disk_batch_size[dg] = 0

                for disk in deployment_batches[cur_date_str]:
                    dg = str(disk_map[disk][4])
                    step = int(disk_map[disk][5])
                    dg_instance = dgroups[dg]
                    if step != -1:
                        if dg not in disk_group_step_details:
                            disk_group_step_details[dg] = dict()
                        if step not in disk_group_step_details[dg]:
                            disk_group_step_details[dg][step] = (dg_instance,
                                                                cur_date_str)

                    if dg not in disk_group_next_checkup:
                        disk_group_last_analysis[dg] = dt
                        disk_group_next_checkup[dg] = dt + datetime.timedelta(
                            days=constants.AGE_EXEMPT_FROM_STABLE_STATE)
                        logging.info("Initial check-up on %s",
                                    disk_group_next_checkup[dg].strftime(
                                        "%Y-%m-%d"))

                    disk_deployment_order[dg].append(cur_date_str)

                    dataset.add_new_disk(disk, dg, cur_date_str,
                                        dg_instance.capacity, step)

                    # report each birth to the transcoding policy for bookkeeping.
                    for p, p_instance in transcoding_policies.items():
                        if step == -1:
                            step_key = None
                        else:
                            step_key = disk_group_step_details[dg][step]
                        p_instance.report_disk_birth(disk,
                                                    dg_instance, cur_date_str,
                                                    disk_step_key=step_key)

                    last_disk_modified[dg] = dt

                for dg, dg_instance in dgroups.items():
                    if dg in disk_group_useful_life_afr and disk_batch_size[dg] > 0:
                        logging.debug("Adding new disk batch of %s",
                                    disk_batch_size[dg])

            # this chunk of code evaluates one-day at a time, to see if old age has
            # been reached after detecting end of infancy, otherwise re-calculates
            # all of the disk stats from the beginning.
            for dg, dg_instance in dgroups.items():
                # this chunk of code handles the disk failures for a given day.

                if cur_date_str != constants.END_DATE and cur_date_str in expired_disk_details:
                    exp_disks = dict()
                    if dg in expired_disk_details[cur_date_str]:
                        exp_disks = expired_disk_details[cur_date_str][dg]

                    for exp_disk, exp_disk_details in exp_disks.items():
                        last_disk_modified[dg] = dt
                        age_of_dead_disk = (datetime.datetime.strptime(
                            cur_date_str, "%Y-%m-%d") - datetime.datetime.strptime(
                            exp_disk_details[1], "%Y-%m-%d")).days

                        # This is needed to see for which ages exactly do we have to
                        # recalculate the AFR to see if old age has reached.
                        if min_age_of_dead_disk[dg] == -1:
                            min_age_of_dead_disk[dg] = age_of_dead_disk
                        elif min_age_of_dead_disk[dg] > age_of_dead_disk:
                            min_age_of_dead_disk[dg] = age_of_dead_disk

                        # failures need to be reported to the database because
                        # disk-days are fetched from the DB.
                        r = dataset.report_expiry(exp_disk_details[0], cur_date_str)
                        if (r is None) or (len(r) == 0):
                            logging.error(
                                "Deleting disk (%s) that was never born of age %s.",
                                exp_disk_details[0], age_of_dead_disk)
                            exit(-1)

                        for p, p_instance in transcoding_policies.items():
                            p_instance.report_disk_failure(exp_disk_details[0],
                                                        cur_date_str)

                        logging.debug("Deleting disk (%s) of age %s",
                                    exp_disk_details[0], str(age_of_dead_disk))

                if cur_date_str != constants.END_DATE and cur_date_str in decom_disk_details:
                    decom_disks = dict()
                    if dg in decom_disk_details[cur_date_str]:
                        decom_disks = decom_disk_details[cur_date_str][dg]

                    for decom_disk in decom_disks.keys():
                        r = dataset.report_decommissioning(decom_disk, cur_date_str)
                        if (r is None) or (len(r) == 0):
                            logging.error("Decommissioning a disk (%s) that was "
                                        "never born of age %s.", decom_disk)
                            exit(1)
                        for p, p_instance in transcoding_policies.items():
                            p_instance.report_disk_decommissioning(decom_disk,
                                                                cur_date_str)

                if (dg in disk_group_useful_life_afr) and (
                    min_age_of_dead_disk[dg] != -1):
                    _ = dg_instance.revise_afr_curve(
                        today=cur_date_str, from_age=min_age_of_dead_disk[dg])
                    min_age_of_dead_disk[dg] = -1

            for dg, dg_instance in dgroups.items():
                # for the first 3 months, don't do anything, just let the disks
                # trickle in. At the end of the first 3 months, calculate if you
                # have the required number of disks, otherwise you wait one month
                # at a time until you do.

                if (dg in disk_group_next_checkup) and (
                    dt < disk_group_next_checkup[dg]):
                    continue

                if (len(disk_deployment_order[dg]) >=
                    constants.MIN_SAMPLE_SIZE) and (
                        transcoding_policies[
                            constants.transcoding_policies[0]].dgroup_wise_metrics[
                            dg_instance].disk_metrics.num_failed_disks >=
                        constants.MIN_FAILURES_NEEDED or
                        len(disk_deployment_order[dg]) >=
                        constants.MIN_SAMPLE_SIZE * 5) and (
                    (dg not in disk_group_useful_life_afr)):

                    rdn_performed, _ = dg_instance.revise_afr_curve(
                        today=cur_date_str, from_age=0)

                    if rdn_performed:
                        useful_life_scheme_map[dg] = dg_instance.latest_rdn_cp.rgroup
                        disk_group_useful_life_afr[dg] = dg_instance.latest_rdn_cp.tailoring_afr
                        disk_group_infancy_age[dg] = dg_instance.latest_rdn_cp.age_of_change

            # We revise the AFR curve if new disks are born or the AFR curve hasn't
            # been revised today because there were no disk failures. This makes
            # sure we understand the RUp transitions required ASAP.
            for dg, dg_instance in dgroups.items():
                if (dg in disk_group_useful_life_afr) and (
                    dg_instance.latest_afr_curve_revision != cur_date_str):
                    revise_from_age = dg_instance.latest_cp.age_of_change
                    if disk_batch_size[dg] > 0:
                        revise_from_age = 0
                        disk_batch_size[dg] = 0
                    elif dg_instance.latest_rup_cp is not None:
                        revise_from_age = dg_instance.latest_rup_cp.age_of_change
                    _ = dg_instance.revise_afr_curve(today=cur_date_str,
                                                    from_age=revise_from_age)

            for dg, dg_instance in dgroups.items():
                # We need to mark the transitions that need to be done today,
                # and their urgency based on whether they are RUp or RDn transitions.
                for p, p_instance in transcoding_policies.items():
                    phase_num = 1
                    for cp in dg_instance.rup_cp_list:
                        if cp.rgroup == common.rgroups[str(
                            constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]:
                            continue
                        disks_changing_phase_details = dataset.get_disks_changing_phase_of_life(
                        dg, cur_date_str, phase_num,
                            cp.age_of_change - constants.REDUCED_USEFUL_LIFE_AGE)

                        from_rgroup = dg_instance.latest_rdn_cp.rgroup
                        if phase_num > 1:
                            from_rgroup = dg_instance.rup_cp_list[
                                dg_instance.rup_cp_list.index(cp) - 1].rgroup

                        to_rgroup = cp.rgroup

                        step_or_trickle_key_dict = dict()

                        for d in disks_changing_phase_details:
                            step_key = p_instance.report_change_in_useful_life_rgroup(
                                dg_instance, from_rgroup, to_rgroup, cur_date_str,
                                from_age=cp.age_of_change -
                                        constants.REDUCED_USEFUL_LIFE_AGE,
                                disk=d[0])

                            if step_key not in step_or_trickle_key_dict:
                                step_or_trickle_key_dict[step_key] = True

                        for step_key in step_or_trickle_key_dict.keys():
                            p_instance.mark_rgroup_change_transition_for_date(
                                dg_instance, from_rgroup, to_rgroup,
                                step_key, cur_date_str,  urgent=True)
                            logging.info("%s disks changing phase of life today "
                                        "from %s to %s",
                                        str(len(disks_changing_phase_details)),
                                        from_rgroup.name, to_rgroup.name)
                        phase_num += 1

                if (dg_instance.latest_rup_cp is not None) and (
                    dg_instance.latest_rup_cp.rgroup == common.rgroups[str(
                    constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"]):
                    if dg not in disk_group_wearout_date:
                        disk_group_wearout_date[dg] = cur_date_str
                        _ = dataset.get_disks_entering_wearout(
                            dg, cur_date_str, dg_instance.latest_cp.age_of_change,
                            urgent=1)
                        disk_group_wearout_date[dg] = cur_date_str
                    else:
                        # These are the disks that are following the initial wave
                        # of disks that taught us where the RUp transition boundary
                        # is. So these RUp-s are performed in a non-urgent manner.
                        _ = dataset.get_disks_entering_wearout(
                            dg, cur_date_str, dg_instance.latest_cp.age_of_change -
                                            constants.REDUCED_USEFUL_LIFE_AGE,
                            urgent=0)

                if dg in disk_group_useful_life_afr:
                    disks_transitioning_to_useful_life_today = dataset.get_disks_entering_useful_life(
                    dg, cur_date_str, dg_instance.latest_rdn_cp.age_of_change)

                    logging.debug("Disks viable for transition today = " +
                                str(len(disks_transitioning_to_useful_life_today))
                                )

                    # It is important to report the optimized Rgroup that disks of a
                    # Dgroup are going to be transitioned to before we capture and
                    # report disks entering optimized Rgroup later on.
                    for d in disks_transitioning_to_useful_life_today:
                        for p, p_instance in transcoding_policies.items():
                            p_instance.report_disk_useful_life_rgroup(
                                d, dg_instance, cur_date_str)

            # The following section works on all disks from all makes/models from
            # the cluster being analyzed. The lists of disks transitioning from all
            # Dgroups are captured just before this.

            # These are all disks RUp-ing to the default redundancy scheme.
            all_disks_transitioning_to_wearout_today = dataset.get_all_disks_entering_wearout(cur_date_str)
            for d in all_disks_transitioning_to_wearout_today:
                for p, p_instance in transcoding_policies.items():
                    p_instance.report_disk_viable_for_wearout(
                        d, cur_date_str, total_disks_transitioning=len(
                        all_disks_transitioning_to_wearout_today))

            # These are all disks who know when the wearout is,
            # and so can RUp in a relaxed manner.
            all_disks_transitioning_to_non_urgent_wearout_today = dataset.get_all_disks_entering_non_urgent_wearout(
                cur_date_str)
            for d in all_disks_transitioning_to_non_urgent_wearout_today:
                for p, p_instance in transcoding_policies.items():
                    p_instance.report_disk_viable_for_non_urgent_wearout(
                        d, cur_date_str, total_disks_transitioning=len(
                        all_disks_transitioning_to_non_urgent_wearout_today))

            # These are all disks that are RDn-ing to a more
            # optimized redundancy scheme.
            all_disks_transitioning_to_useful_life_today = dataset.get_all_disks_entering_useful_life(cur_date_str)
            for d in all_disks_transitioning_to_useful_life_today:
                for p, p_instance in transcoding_policies.items():
                    p_instance.report_disk_viable_for_useful_life(
                        d, cur_date_str, total_disks_transitioning=len(
                        all_disks_transitioning_to_useful_life_today))

            # This call actually simulates all the transitions required and
            # manipulates all the necessary metrics.
            for p, p_instance in transcoding_policies.items():
                p_instance.process_daily_transitions(cur_date_str)
                p_instance.reset_daily_stats()

            common.day_wise_dt_range.append(dt)
            pbar.update(1)

    print("simulation ended!")
    print("----------------------------------------")
    print("plotting graphs...")
    for dg, dg_instance in dgroups.items():
        logging.info("Generating Dgroup graph for " + dg)
        dg_instance.plot_afr("date_wise_dgroup_afr")

def plot_date_wise_io(dataset):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    # os.makedirs("results/" + today + "/date_wise/" + common.cluster +
    #             "/plots/" + str(constants.REDUCED_USEFUL_LIFE_AGE), exist_ok=True)

    opts = []
    fname = ""

    if len(common.day_wise_dt_range) == 0:
        all_dgroups = ', '.join("'{0}'".format(dg) for dg in list(common.dgroups.keys()))
        all_disks_deployment_dates = dataset.get_all_deployment_dates(dgroups=all_dgroups)
        startdate = all_disks_deployment_dates[0]
        enddate = constants.END_DATE
        dt_range = common.daterange(datetime.datetime.strptime(startdate, "%Y-%m-%d"),
                                    datetime.datetime.strptime(enddate, "%Y-%m-%d"))
        for dt in dt_range:
            common.day_wise_dt_range.append(dt)

    for transcoding_policy in constants.transcoding_policies:
        if (constants.CANARY) and (constants.ITERATIVE_CP is False):
            fname = (common.results_dir + "/" + transcoding_policy +
                     "_total_cluster_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                     "%" + "_canary.csv")
            opts.append(properties.CANARY)
        elif (constants.CANARY is False) and (constants.ITERATIVE_CP):
            fname = (common.results_dir + "/" +
                     transcoding_policy + "_total_cluster_stats_performed_" +
                     str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_iterative_cp.csv")
            opts.append(properties.ITERATIVE_CP)
        elif (constants.CANARY is False) and (constants.ITERATIVE_CP is False):
            fname = (common.results_dir + "/" +
                     transcoding_policy + "_total_cluster_stats_performed_" +
                     str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_vanilla.csv")
            opts.append(properties.VANILLA)
        else:
            fname = (common.results_dir + "/" +
                     transcoding_policy + "_total_cluster_stats_performed_" +
                     str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%.csv")
            opts.append(properties.ITERATIVE_CP)
            opts.append(properties.CANARY)

    for optimizations in opts:
        for y_axis_lim in constants.Y_AXIS_LIMITS:
            for transcoding_policy in constants.transcoding_policies:
                df = pd.read_csv(fname)

                matplotlib.rcParams['figure.figsize'] = 12, 3
                _, ax1 = plt.subplots()
                ax2 = ax1.twinx()

                ax2.fill_between(common.day_wise_dt_range, np.asarray(
                    df[properties.INFANCY_NUM_DISKS].values),
                                    np.asarray(df[properties.INFANCY_NUM_DISKS].values +
                                            df[properties.USEFUL_LIFE_NUM_DISKS].values +
                                            df[properties.WEAROUT_NUM_DISKS].values), color='black',
                                    alpha=0.25, linewidth=0.5, edgecolor='black',
                                    zorder=10)

                ax2.fill_between(common.day_wise_dt_range, 0,
                                    np.asarray(df[properties.INFANCY_NUM_DISKS].values),
                                    color='black',
                                    alpha=0.45, linewidth=0.5, edgecolor='black',
                                    zorder=10)

                ax1.plot_date(common.day_wise_dt_range, np.asarray(
                    (df[properties.TOTAL_CLUSTER_DECOMMISSIONING_IO].values *
                        100) / df[properties.TOTAL_CLUSTER_IO_BANDWIDTH].values),
                                '-', color='green', linewidth=1, alpha=1)

                ax1.plot_date(common.day_wise_dt_range,
                                np.asarray(((df[properties.TOTAL_CLUSTER_SCHEDULABLE_IO].values + df[
                                    properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO].values) * 100) / df[
                                                properties.TOTAL_CLUSTER_IO_BANDWIDTH].values), '-',
                                color='blue', linewidth=1, alpha=1)

                ax1.plot_date(common.day_wise_dt_range, np.asarray(
                    (df[properties.TOTAL_CLUSTER_RECONSTRUCTION_IO].values * 100) / df[
                        properties.TOTAL_CLUSTER_IO_BANDWIDTH].values), '-',
                                color='red', linewidth=1, alpha=1)

                ax1.plot_date(common.day_wise_dt_range, np.asarray(
                    (df[properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO].values * 100) / df[
                        properties.TOTAL_CLUSTER_IO_BANDWIDTH].values), '-', color='blue', linewidth=1)

                ax1.fill_between(common.day_wise_dt_range, np.asarray(
                    ((df[properties.TOTAL_CLUSTER_SCHEDULABLE_IO].values +
                        df[properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO].values) * 100) /
                    df[properties.TOTAL_CLUSTER_IO_BANDWIDTH].values), 0, color='blue', alpha=0.3, linewidth=0)

                ax1.fill_between(common.day_wise_dt_range, np.asarray(
                    (df[properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO].values * 100) /
                    df[properties.TOTAL_CLUSTER_IO_BANDWIDTH].values), 0, color='blue', alpha=0.3, linewidth=0)

                ax1.fill_between(common.day_wise_dt_range, np.asarray(
                    (df[properties.TOTAL_CLUSTER_DECOMMISSIONING_IO].values * 100) /
                    df[properties.TOTAL_CLUSTER_IO_BANDWIDTH].values), 0, color='green', alpha=0.4, linewidth=0)

                ax1.fill_between(common.day_wise_dt_range, np.asarray(
                    (df[properties.TOTAL_CLUSTER_RECONSTRUCTION_IO].values * 100) /
                    df[properties.TOTAL_CLUSTER_IO_BANDWIDTH].values), 0, color='red', alpha=0.3, linewidth=0)

                plt.xlabel("Date")
                ax1.set_ylabel("Total IO per day (%)")
                ax2.set_ylabel("Num disks running")
                plt.xlim(common.day_wise_dt_range[0], common.day_wise_dt_range[len(common.day_wise_dt_range) - 1])
                ax1.set_ylim(0, y_axis_lim)
                ax2.set_ylim(0, common.cluster_num_disks[common.cluster])
                formatter = FuncFormatter(common.lakhs)
                ax2.yaxis.set_major_formatter(formatter)
                
                legend_elements = [
                                    Patch(facecolor='blue', edgecolor='blue', label='Transitioning (RDn or RUp) IO',
                                            alpha=0.6),
                                    Patch(facecolor='red', edgecolor='red', label='Reconstruction IO',
                                            alpha=0.7),
                                    Patch(facecolor='green', edgecolor='green', label='Decommissioning IO',
                                            alpha=0.6),
                                    Patch(facecolor='black', edgecolor='black', label='Unspecialized disks (right axis)',
                                            alpha=0.5),
                                    Patch(facecolor='black', edgecolor='black', label='Specialized disks (right axis)',
                                            alpha=0.25),
                ]

                ax1.legend(handles=legend_elements, loc="upper left", ncol=2, frameon=False)

                ax1.tick_params(axis='x')
                plt.savefig(common.results_dir + "/plots/transition_overload_with_reconstruction.pdf", bbox_inches='tight')

                plt.tight_layout()
                plt.gcf().clear()

    for y_axis_lim in constants.Y_AXIS_LIMITS:
        for transcoding_policy in constants.transcoding_policies:
            df = pd.read_csv(fname)

            matplotlib.rcParams['figure.figsize'] = 12, 3
            _, ax1 = plt.subplots()
            ax2 = ax1.twinx()

            ax2.fill_between(common.day_wise_dt_range, np.asarray(
                    df[properties.INFANCY_NUM_DISKS].values),
                                 np.asarray(df[properties.INFANCY_NUM_DISKS].values +
                                            df[properties.USEFUL_LIFE_NUM_DISKS].values +
                                            df[properties.WEAROUT_NUM_DISKS].values), color='black',
                                 alpha=0.25, linewidth=0.5, edgecolor='black',
                                 zorder=10)

            ax2.fill_between(common.day_wise_dt_range, 0,
                             np.asarray(df[properties.INFANCY_NUM_DISKS].values),
                             color='black',
                             alpha=0.45, linewidth=0.5, edgecolor='black',
                             zorder=10)

            ax1.plot_date(common.day_wise_dt_range,
                          np.asarray(
                              ((df[properties.TOTAL_CLUSTER_SCHEDULABLE_IO].values +
                                df[properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO].values +
                                df[properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO].values) * 100) / df[
                                         properties.TOTAL_CLUSTER_IO_BANDWIDTH].values), '-',
                          color='blue', linewidth=1, alpha=1)

            ax1.fill_between(common.day_wise_dt_range, np.asarray(
                ((df[properties.TOTAL_CLUSTER_SCHEDULABLE_IO].values +
                  df[properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO].values +
                  df[properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO].values) * 100) /
                df[properties.TOTAL_CLUSTER_IO_BANDWIDTH].values), 0, color='blue', alpha=0.3, linewidth=0)

            plt.xlabel("Date")
            ax1.set_ylabel("Total IO per day (%)", fontsize=18)
            ax2.set_ylabel("Num disks running", fontsize=18)
            plt.xlim(common.day_wise_dt_range[0], common.day_wise_dt_range[len(common.day_wise_dt_range) - 1])
            ax1.set_ylim(0, y_axis_lim)
            ax2.set_ylim(0, common.cluster_num_disks[common.cluster])
            formatter = FuncFormatter(common.lakhs)
            ax2.yaxis.set_major_formatter(formatter)
            
            legend_elements = [
                Patch(facecolor='blue', edgecolor='gray', label='Transitioning (RDn or RUp) IO', alpha=0.5),
                Patch(facecolor='black', edgecolor='gray', label='Unspecialized disks (right axis)', alpha=0.5),
                Patch(facecolor='black', edgecolor='gray', label='Specialized disks (right axis)', alpha=0.25)]

            ax1.legend(handles=legend_elements, loc="upper left", ncol=2, frameon=False)

            ax1.tick_params(axis='x')
            plt.savefig(common.results_dir + "/plots/only_transition_overload.pdf", bbox_inches='tight')

            plt.tight_layout()
            plt.gcf().clear()

def plot_rgroup_distribution(dataset):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    os.makedirs("results/" + today + "/date_wise/" + common.cluster +
                "/plots/" + str(constants.REDUCED_USEFUL_LIFE_AGE), exist_ok=True)

    opts = []
    fname = ""
    rgroup_fname = ""
    fname_append = ""

    for transcoding_policy in constants.transcoding_policies:
        if (constants.CANARY) and (constants.ITERATIVE_CP is False):
            fname = (common.results_dir + "/" + transcoding_policy +
                     "_total_cluster_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                     "%" + "_canary.csv")
            rgroup_fname = (common.results_dir + "/" + transcoding_policy +
                            "_rgroup_list_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_canary.txt")
            fname_append = "_canary"
            opts.append(properties.CANARY)
        elif (constants.CANARY is False) and (constants.ITERATIVE_CP):
            fname = (common.results_dir + "/" +
                     transcoding_policy + "_total_cluster_stats_performed_" +
                     str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_iterative_cp.csv")
            rgroup_fname = (common.results_dir + "/" + transcoding_policy + "_rgroup_list_" +
                     str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_iterative_cp.txt")
            fname_append = "_iterative_cp"
            opts.append(properties.ITERATIVE_CP)
        elif (constants.CANARY is False) and (constants.ITERATIVE_CP is False):
            fname = (common.results_dir + "/" +
                     transcoding_policy + "_total_cluster_stats_performed_" +
                     str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_vanilla.csv")
            rgroup_fname = (common.results_dir + "/" + transcoding_policy + "_rgroup_list_" +
                     str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_vanilla.txt")
            fname_append = "_vanilla"
            opts.append(properties.VANILLA)
        else:
            fname = (common.results_dir + "/" +
                     transcoding_policy + "_total_cluster_stats_performed_" +
                     str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%.csv")
            rgroup_fname = (common.results_dir + "/" + transcoding_policy + "_rgroup_list_" +
                     str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%.txt")
            opts.append(properties.ITERATIVE_CP)
            opts.append(properties.CANARY)

    i = 0
    for optimizations in opts:
        for transcoding_policy in constants.transcoding_policies:

            rg_list_file = rgroup_fname

            with open(rg_list_file) as f:
                rg_list = f.read().splitlines()

            matplotlib.rcParams['figure.figsize'] = 11, 2
            _, ax1 = plt.subplots()

            overall_df = pd.read_csv(fname)

            prev_val = 0

            default_overhead = 1.5

            default_capacity = overall_df[properties.TOTAL_CLUSTER_CAPACITY].to_numpy()

            for rg in rg_list:
                if rg == "(9, 3)" or rg == "(9, 3)_wearout":
                    continue

                df = pd.read_csv(common.results_dir + "/" + rg + "/" + transcoding_policy +
                                 "_rgroup_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                                 "%" + fname_append + ".csv")

                default_capacity = np.subtract(default_capacity, df[properties.RGROUP_CAPACITY].to_numpy())
                rg_tuple = make_tuple(rg)
                rg_overhead = float(rg_tuple[0]) / (rg_tuple[0] - rg_tuple[1])
                default_capacity += (df[properties.RGROUP_CAPACITY].to_numpy() / rg_overhead) * default_overhead

            for rg in rg_list:
                # rgroup distribution
                df = pd.read_csv(common.results_dir + "/" + rg + "/" + transcoding_policy +
                                 "_rgroup_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                                 "%" + fname_append + ".csv")

                if rg == "(9, 3)_wearout":
                    ax1.fill_between(common.day_wise_dt_range, np.asarray(
                        ((df[properties.RGROUP_CAPACITY].values + prev_val) * 100) /
                        default_capacity),
                                     (prev_val * 100) / default_capacity,
                                     color='maroon', alpha=0.5, edgecolor=None)
                elif rg == "(9, 3)":
                    ax1.fill_between(common.day_wise_dt_range, np.asarray(
                        ((df[properties.RGROUP_CAPACITY].values + prev_val) * 100) /
                        default_capacity),
                                     (prev_val * 100) / default_capacity,
                                     color='black', alpha=0.5, edgecolor=None)
                else:
                    ax1.fill_between(common.day_wise_dt_range, np.asarray(
                        ((df[properties.RGROUP_CAPACITY].values + prev_val) * 100) /
                        default_capacity),
                                     (prev_val * 100) / default_capacity, alpha=0.6, color=common.rg_color_dict[rg])
                i += 1

                prev_val += df[properties.RGROUP_CAPACITY].values

            logging.debug("avg space savings = " + str(1.0 - np.mean(np.asarray(prev_val / default_capacity))))
            logging.debug("max space savings = " + str(1.0 - np.min(np.asarray(prev_val / default_capacity))))
            ax1.set_ylabel("Capacity (%)", fontsize=11)
            ax1.tick_params(axis='x', labelsize=11)
            ax1.tick_params(axis='y', labelsize=11)
            ax1.set_ylim(0, 100)
            plt.xlim(common.day_wise_dt_range[0], common.day_wise_dt_range[len(common.day_wise_dt_range) - 1])

            plt.savefig(common.results_dir + "/plots/rgroups.pdf", bbox_inches='tight')

            plt.gcf().clear()
