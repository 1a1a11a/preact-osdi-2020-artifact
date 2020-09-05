#!/usr/local/bin/python3

import matplotlib.pyplot as plt
import os
import sys
import datetime
import numpy as np
from shutil import copyfile
from datetime import timedelta, date
import properties
import constants
import common
import copy
import pandas as pd
import logging
from dgroups.dgroup import DGroup
from rgroups.rgroup import RGroup

from metrics.cluster_metrics import ClusterMetrics
from metrics.dgroup_metrics import DgroupMetrics
from metrics.rgroup_metrics import RgroupMetrics


class Metrics:
    def __init__(self, transcoding_policy, num_days, canary, iterative_cp):
        self.transcoding_policy = transcoding_policy

        self.running_disk_stats = dict()

        self.running_disk_stats[properties.INFANCY_NUM_DISKS] = np.zeros(num_days)
        self.running_disk_stats[properties.USEFUL_LIFE_NUM_DISKS] = np.zeros(num_days)
        self.running_disk_stats[properties.WEAROUT_NUM_DISKS] = np.zeros(num_days)

        self.running_disk_stats[properties.NUM_FAILED_DISKS] = np.zeros(num_days)
        self.running_disk_stats[properties.NUM_DECOMMISSIONED_DISKS] = np.zeros(num_days)
        self.running_disk_stats[properties.NUM_RUNNING_DISKS] = np.zeros(num_days)

        self.running_disk_stats[properties.TOTAL_CLUSTER_CAPACITY] = np.zeros(num_days)

        self.running_disk_stats[properties.CANARY_NUM_DISKS] = np.zeros(num_days)
        self.running_disk_stats[properties.CANARY_INFANCY_NUM_DISKS] = np.zeros(num_days)
        self.running_disk_stats[properties.CANARY_USEFUL_LIFE_NUM_DISKS] = np.zeros(num_days)
        self.running_disk_stats[properties.CANARY_WEAROUT_NUM_DISKS] = np.zeros(num_days)

        # total cluster needed
        self.running_disk_stats[properties.NEEDED] = dict()
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_RECONSTRUCTION_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_RECONSTRUCTION_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_RECONSTRUCTION_WRITES] = np.zeros(num_days)

        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCHEDULABLE_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCHEDULABLE_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCHEDULABLE_WRITES] = np.zeros(num_days)

        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_DECOMMISSIONING_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_DECOMMISSIONING_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_DECOMMISSIONING_WRITES] = np.zeros(num_days)

        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCRUBBING_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCRUBBING_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCRUBBING_WRITES] = np.zeros(num_days)

        # total cluster performed
        self.running_disk_stats[properties.PERFORMED] = dict()
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_RECONSTRUCTION_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_RECONSTRUCTION_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_RECONSTRUCTION_WRITES] = np.zeros(num_days)

        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCHEDULABLE_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCHEDULABLE_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCHEDULABLE_WRITES] = np.zeros(num_days)

        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_DECOMMISSIONING_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_DECOMMISSIONING_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_DECOMMISSIONING_WRITES] = np.zeros(num_days)

        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCRUBBING_IO] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCRUBBING_READS] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCRUBBING_WRITES] = np.zeros(num_days)

        self.running_disk_stats[properties.TOTAL_CLUSTER_IO_BANDWIDTH] = np.zeros(num_days)
        self.running_disk_stats[properties.TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH_ALLOWED] = np.zeros(num_days)
        self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH] = np.zeros(num_days)
        self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH] = np.zeros(num_days)

        self.dgroup_stats = dict()
        self.dgroup_stats_needed = dict()
        self.dgroup_stats_performed = dict()

        self.num_days = num_days
        for d in common.dgroups:
            self._setup_dgroup_stats(d)

        self.rgroup_stats = dict()
        self.rgroup_stats_needed = dict()
        self.rgroup_stats_performed = dict()

        for r in common.rgroups:
            self._setup_rgroup_stats(r)

        self.canary = canary
        self.iterative_cp = iterative_cp

    def _setup_dgroup_stats(self, d):
        num_days = self.num_days
        self.dgroup_stats[d] = dict()
        self.dgroup_stats[d][properties.DGROUP_INFANCY_NUM_DISKS] = np.zeros(num_days)
        self.dgroup_stats[d][properties.DGROUP_USEFUL_LIFE_NUM_DISKS] = np.zeros(num_days)
        self.dgroup_stats[d][properties.DGROUP_WEAROUT_NUM_DISKS] = np.zeros(num_days)
        self.dgroup_stats[d][properties.DGROUP_CAPACITY] = np.zeros(num_days)

        self.dgroup_stats[d][properties.DGROUP_RUNNING_NUM_DISKS] = np.zeros(num_days)
        self.dgroup_stats[d][properties.DGROUP_FAILED_NUM_DISKS] = np.zeros(num_days)
        self.dgroup_stats[d][properties.DGROUP_DECOMMISSIONED_NUM_DISKS] = np.zeros(num_days)

        self.dgroup_stats[d][properties.DGROUP_CANARY_RUNNING_NUM_DISKS] = np.zeros(num_days)
        self.dgroup_stats[d][properties.DGROUP_CANARY_INFANCY_NUM_DISKS] = np.zeros(num_days)
        self.dgroup_stats[d][properties.DGROUP_CANARY_USEFUL_LIFE_NUM_DISKS] = np.zeros(num_days)
        self.dgroup_stats[d][properties.DGROUP_CANARY_WEAROUT_NUM_DISKS] = np.zeros(num_days)
        self.dgroup_stats[d][properties.DGROUP_CANARY_FAILED_NUM_DISKS] = np.zeros(num_days)
        self.dgroup_stats[d][properties.DGROUP_CANARY_DECOMMISSIONED_NUM_DISKS] = np.zeros(num_days)

        # needed
        self.dgroup_stats_needed[d] = dict()
        self.dgroup_stats_needed[d][properties.DGROUP_RECONSTRUCTION_IO] = np.zeros(num_days)
        self.dgroup_stats_needed[d][properties.DGROUP_RECONSTRUCTION_READS] = np.zeros(num_days)
        self.dgroup_stats_needed[d][properties.DGROUP_RECONSTRUCTION_WRITES] = np.zeros(num_days)

        self.dgroup_stats_needed[d][properties.DGROUP_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.dgroup_stats_needed[d][properties.DGROUP_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.dgroup_stats_needed[d][properties.DGROUP_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.dgroup_stats_needed[d][properties.DGROUP_SCHEDULABLE_IO] = np.zeros(num_days)
        self.dgroup_stats_needed[d][properties.DGROUP_SCHEDULABLE_READS] = np.zeros(num_days)
        self.dgroup_stats_needed[d][properties.DGROUP_SCHEDULABLE_WRITES] = np.zeros(num_days)

        self.dgroup_stats_needed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.dgroup_stats_needed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.dgroup_stats_needed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.dgroup_stats_needed[d][properties.DGROUP_DECOMMISSIONING_IO] = np.zeros(num_days)
        self.dgroup_stats_needed[d][properties.DGROUP_DECOMMISSIONING_READS] = np.zeros(num_days)
        self.dgroup_stats_needed[d][properties.DGROUP_DECOMMISSIONING_WRITES] = np.zeros(num_days)

        # performed
        self.dgroup_stats_performed[d] = dict()
        self.dgroup_stats_performed[d][properties.DGROUP_RECONSTRUCTION_IO] = np.zeros(num_days)
        self.dgroup_stats_performed[d][properties.DGROUP_RECONSTRUCTION_READS] = np.zeros(num_days)
        self.dgroup_stats_performed[d][properties.DGROUP_RECONSTRUCTION_WRITES] = np.zeros(num_days)

        self.dgroup_stats_performed[d][properties.DGROUP_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.dgroup_stats_performed[d][properties.DGROUP_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.dgroup_stats_performed[d][properties.DGROUP_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.dgroup_stats_performed[d][properties.DGROUP_SCHEDULABLE_IO] = np.zeros(num_days)
        self.dgroup_stats_performed[d][properties.DGROUP_SCHEDULABLE_READS] = np.zeros(num_days)
        self.dgroup_stats_performed[d][properties.DGROUP_SCHEDULABLE_WRITES] = np.zeros(num_days)

        self.dgroup_stats_performed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.dgroup_stats_performed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.dgroup_stats_performed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.dgroup_stats_performed[d][properties.DGROUP_DECOMMISSIONING_IO] = np.zeros(num_days)
        self.dgroup_stats_performed[d][properties.DGROUP_DECOMMISSIONING_READS] = np.zeros(num_days)
        self.dgroup_stats_performed[d][properties.DGROUP_DECOMMISSIONING_WRITES] = np.zeros(num_days)

    def _setup_rgroup_stats(self, r):
        num_days = self.num_days
        self.rgroup_stats[r] = dict()
        self.rgroup_stats[r][properties.RGROUP_RUNNING_NUM_DISKS] = np.zeros(num_days)
        self.rgroup_stats[r][properties.RGROUP_FAILED_NUM_DISKS] = np.zeros(num_days)
        self.rgroup_stats[r][properties.RGROUP_DECOMMISSIONED_NUM_DISKS] = np.zeros(num_days)
        self.rgroup_stats[r][properties.RGROUP_CAPACITY] = np.zeros(num_days)

        # needed
        self.rgroup_stats_needed[r] = dict()
        self.rgroup_stats_needed[r][properties.RGROUP_RECONSTRUCTION_IO] = np.zeros(num_days)
        self.rgroup_stats_needed[r][properties.RGROUP_RECONSTRUCTION_READS] = np.zeros(num_days)
        self.rgroup_stats_needed[r][properties.RGROUP_RECONSTRUCTION_WRITES] = np.zeros(num_days)

        self.rgroup_stats_needed[r][properties.RGROUP_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.rgroup_stats_needed[r][properties.RGROUP_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.rgroup_stats_needed[r][properties.RGROUP_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.rgroup_stats_needed[r][properties.RGROUP_SCHEDULABLE_IO] = np.zeros(num_days)
        self.rgroup_stats_needed[r][properties.RGROUP_SCHEDULABLE_READS] = np.zeros(num_days)
        self.rgroup_stats_needed[r][properties.RGROUP_SCHEDULABLE_WRITES] = np.zeros(num_days)

        self.rgroup_stats_needed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.rgroup_stats_needed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.rgroup_stats_needed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.rgroup_stats_needed[r][properties.RGROUP_DECOMMISSIONING_IO] = np.zeros(num_days)
        self.rgroup_stats_needed[r][properties.RGROUP_DECOMMISSIONING_READS] = np.zeros(num_days)
        self.rgroup_stats_needed[r][properties.RGROUP_DECOMMISSIONING_WRITES] = np.zeros(num_days)

        # performed
        self.rgroup_stats_performed[r] = dict()
        self.rgroup_stats_performed[r][properties.RGROUP_RECONSTRUCTION_IO] = np.zeros(num_days)
        self.rgroup_stats_performed[r][properties.RGROUP_RECONSTRUCTION_READS] = np.zeros(num_days)
        self.rgroup_stats_performed[r][properties.RGROUP_RECONSTRUCTION_WRITES] = np.zeros(num_days)

        self.rgroup_stats_performed[r][properties.RGROUP_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.rgroup_stats_performed[r][properties.RGROUP_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.rgroup_stats_performed[r][properties.RGROUP_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.rgroup_stats_performed[r][properties.RGROUP_SCHEDULABLE_IO] = np.zeros(num_days)
        self.rgroup_stats_performed[r][properties.RGROUP_SCHEDULABLE_READS] = np.zeros(num_days)
        self.rgroup_stats_performed[r][properties.RGROUP_SCHEDULABLE_WRITES] = np.zeros(num_days)

        self.rgroup_stats_performed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_IO] = np.zeros(num_days)
        self.rgroup_stats_performed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_READS] = np.zeros(num_days)
        self.rgroup_stats_performed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_WRITES] = np.zeros(num_days)

        self.rgroup_stats_performed[r][properties.RGROUP_DECOMMISSIONING_IO] = np.zeros(num_days)
        self.rgroup_stats_performed[r][properties.RGROUP_DECOMMISSIONING_READS] = np.zeros(num_days)
        self.rgroup_stats_performed[r][properties.RGROUP_DECOMMISSIONING_WRITES] = np.zeros(num_days)

    def save_daily_stats(self, i, daily_stats, dgroup_metrics, rgroup_metrics, step_wise_metrics):
        # total cluster disk metrics
        np.put(self.running_disk_stats[properties.INFANCY_NUM_DISKS], i,
               daily_stats.total_disk_metrics.num_infancy_disks)
        np.put(self.running_disk_stats[properties.USEFUL_LIFE_NUM_DISKS], i,
               daily_stats.total_disk_metrics.num_useful_life_disks)
        np.put(self.running_disk_stats[properties.WEAROUT_NUM_DISKS], i,
               daily_stats.total_disk_metrics.num_wearout_disks)

        np.put(self.running_disk_stats[properties.NUM_FAILED_DISKS], i,
               daily_stats.total_disk_metrics.num_failed_disks)
        np.put(self.running_disk_stats[properties.NUM_DECOMMISSIONED_DISKS], i,
               daily_stats.total_disk_metrics.num_decommissioned_disks)
        np.put(self.running_disk_stats[properties.NUM_RUNNING_DISKS], i,
               daily_stats.total_disk_metrics.num_running_disks)

        np.put(self.running_disk_stats[properties.TOTAL_CLUSTER_CAPACITY], i,
               daily_stats.total_disk_metrics.capacity)

        # np.put(self.running_disk_stats[properties.CANARY_NUM_DISKS], i,
        #        daily_stats.total_disk_metrics.num_canary_disks)
        # np.put(self.running_disk_stats[properties.CANARY_INFANCY_NUM_DISKS], i,
        #        daily_stats.total_disk_metrics.num_canary_failed_disks)
        # np.put(self.running_disk_stats[properties.CANARY_USEFUL_LIFE_NUM_DISKS], i,
        #        daily_stats.total_disk_metrics.num_canary_useful_life_disks)
        # np.put(self.running_disk_stats[properties.CANARY_WEAROUT_NUM_DISKS], i,
        #        daily_stats.total_disk_metrics.num_canary_wearout_disks)

        # total cluster io metrics
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_RECONSTRUCTION_IO], i,
               daily_stats.total_disk_metrics.background_work.reconstruction_needed.io)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_RECONSTRUCTION_READS], i,
               daily_stats.total_disk_metrics.background_work.reconstruction_needed.reads)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_RECONSTRUCTION_WRITES], i,
               daily_stats.total_disk_metrics.background_work.reconstruction_needed.writes)

        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO], i,
               daily_stats.total_disk_metrics.background_work.urgent_reencoding_needed.io)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_READS], i,
               daily_stats.total_disk_metrics.background_work.urgent_reencoding_needed.reads)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_WRITES], i,
               daily_stats.total_disk_metrics.background_work.urgent_reencoding_needed.writes)

        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCHEDULABLE_IO], i,
               daily_stats.total_disk_metrics.background_work.schedulable_reencoding_needed.io)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCHEDULABLE_READS], i,
               daily_stats.total_disk_metrics.background_work.schedulable_reencoding_needed.reads)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCHEDULABLE_WRITES], i,
               daily_stats.total_disk_metrics.background_work.schedulable_reencoding_needed.writes)

        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO], i,
               daily_stats.total_disk_metrics.background_work.non_urgent_reencoding_needed.io)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_READS], i,
               daily_stats.total_disk_metrics.background_work.non_urgent_reencoding_needed.reads)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_WRITES], i,
               daily_stats.total_disk_metrics.background_work.non_urgent_reencoding_needed.writes)

        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_DECOMMISSIONING_IO], i,
               daily_stats.total_disk_metrics.background_work.decommissioning_needed.io)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_DECOMMISSIONING_READS], i,
               daily_stats.total_disk_metrics.background_work.decommissioning_needed.reads)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_DECOMMISSIONING_WRITES], i,
               daily_stats.total_disk_metrics.background_work.decommissioning_needed.writes)

        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCRUBBING_IO], i,
               daily_stats.total_disk_metrics.background_work.scrubbing_needed.io)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCRUBBING_READS], i,
               daily_stats.total_disk_metrics.background_work.scrubbing_needed.reads)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCRUBBING_WRITES], i,
               daily_stats.total_disk_metrics.background_work.scrubbing_needed.writes)

        # total cluster performed
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_RECONSTRUCTION_IO], i,
               daily_stats.total_disk_metrics.background_work.reconstruction_performed.io)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_RECONSTRUCTION_READS], i,
               daily_stats.total_disk_metrics.background_work.reconstruction_performed.reads)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_RECONSTRUCTION_WRITES], i,
               daily_stats.total_disk_metrics.background_work.reconstruction_performed.writes)

        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO], i,
               daily_stats.total_disk_metrics.background_work.urgent_reencoding_performed.io)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_READS], i,
               daily_stats.total_disk_metrics.background_work.urgent_reencoding_performed.reads)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_WRITES], i,
               daily_stats.total_disk_metrics.background_work.urgent_reencoding_performed.writes)

        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCHEDULABLE_IO], i,
               daily_stats.total_disk_metrics.background_work.schedulable_reencoding_performed.io)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCHEDULABLE_READS], i,
               daily_stats.total_disk_metrics.background_work.schedulable_reencoding_performed.reads)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCHEDULABLE_WRITES], i,
               daily_stats.total_disk_metrics.background_work.schedulable_reencoding_performed.writes)

        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO], i,
               daily_stats.total_disk_metrics.background_work.non_urgent_reencoding_performed.io)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_READS], i,
               daily_stats.total_disk_metrics.background_work.non_urgent_reencoding_performed.reads)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_WRITES], i,
               daily_stats.total_disk_metrics.background_work.non_urgent_reencoding_performed.writes)

        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_DECOMMISSIONING_IO], i,
               daily_stats.total_disk_metrics.background_work.decommissioning_performed.io)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_DECOMMISSIONING_READS], i,
               daily_stats.total_disk_metrics.background_work.decommissioning_performed.reads)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_DECOMMISSIONING_WRITES], i,
               daily_stats.total_disk_metrics.background_work.decommissioning_performed.writes)

        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCRUBBING_IO], i,
               daily_stats.total_disk_metrics.background_work.scrubbing_performed.io)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCRUBBING_READS], i,
               daily_stats.total_disk_metrics.background_work.scrubbing_performed.reads)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCRUBBING_WRITES], i,
               daily_stats.total_disk_metrics.background_work.scrubbing_performed.writes)

        np.put(self.running_disk_stats[properties.TOTAL_CLUSTER_IO_BANDWIDTH], i,
               daily_stats.total_cluster_io_bandwidth)
        np.put(self.running_disk_stats[properties.TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH_ALLOWED], i,
               daily_stats.total_background_io_bandwidth_allowed)
        np.put(self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH], i,
               daily_stats.total_background_io_bandwidth_needed)
        np.put(self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH], i,
               daily_stats.total_background_io_bandwidth_used)

        for dg, dg_metrics in dgroup_metrics.items():
            d = dg.name

            if dg.name not in self.dgroup_stats:
                self._setup_dgroup_stats(dg.name)

            np.put(self.dgroup_stats[d][properties.DGROUP_INFANCY_NUM_DISKS], i, dg_metrics.disk_metrics.num_infancy_disks)
            np.put(self.dgroup_stats[d][properties.DGROUP_USEFUL_LIFE_NUM_DISKS], i, dg_metrics.disk_metrics.num_useful_life_disks)
            np.put(self.dgroup_stats[d][properties.DGROUP_WEAROUT_NUM_DISKS], i, dg_metrics.disk_metrics.num_wearout_disks)
            np.put(self.dgroup_stats[d][properties.DGROUP_CAPACITY], i, dg_metrics.disk_metrics.capacity)

            np.put(self.dgroup_stats[d][properties.DGROUP_RUNNING_NUM_DISKS], i, dg_metrics.disk_metrics.num_running_disks)
            np.put(self.dgroup_stats[d][properties.DGROUP_FAILED_NUM_DISKS], i,
                   dg_metrics.disk_metrics.num_failed_disks)
            np.put(self.dgroup_stats[d][properties.DGROUP_DECOMMISSIONED_NUM_DISKS], i,
                   dg_metrics.disk_metrics.num_decommissioned_disks)

            np.put(self.dgroup_stats[d][properties.DGROUP_CANARY_INFANCY_NUM_DISKS], i,
                   dg_metrics.canary_disk_metrics.num_infancy_disks)
            np.put(self.dgroup_stats[d][properties.DGROUP_CANARY_USEFUL_LIFE_NUM_DISKS], i,
                   dg_metrics.canary_disk_metrics.num_useful_life_disks)
            np.put(self.dgroup_stats[d][properties.DGROUP_CANARY_WEAROUT_NUM_DISKS], i,
                   dg_metrics.canary_disk_metrics.num_wearout_disks)

            np.put(self.dgroup_stats[d][properties.DGROUP_CANARY_RUNNING_NUM_DISKS], i,
                   dg_metrics.canary_disk_metrics.num_running_disks)
            np.put(self.dgroup_stats[d][properties.DGROUP_CANARY_FAILED_NUM_DISKS], i,
                   dg_metrics.canary_disk_metrics.num_failed_disks)
            np.put(self.dgroup_stats[d][properties.DGROUP_CANARY_DECOMMISSIONED_NUM_DISKS], i,
                   dg_metrics.canary_disk_metrics.num_decommissioned_disks)

            # np.put(self.dgroup_stats[d][properties.DGROUP_CANARY_NUM_DISKS], i,
            #        dg_metrics.disk_metrics.num_canary_disks)
            # np.put(self.dgroup_stats[d][properties.DGROUP_CANARY_INFANCY_NUM_DISKS], i,
            #        dg_metrics.disk_metrics.num_infancy_canary_disks)
            # np.put(self.dgroup_stats[d][properties.DGROUP_CANARY_USEFUL_LIFE_NUM_DISKS], i,
            #        dg_metrics.disk_metrics.num_useful_life_canary_disks)
            # np.put(self.dgroup_stats[d][properties.DGROUP_CANARY_WEAROUT_NUM_DISKS], i,
            #        dg_metrics.disk_metrics.num_wearout_canary_disks)

            # needed
            np.put(self.dgroup_stats_needed[d][properties.DGROUP_RECONSTRUCTION_IO], i,
                   dg_metrics.disk_metrics.background_work.reconstruction_needed.io)
            np.put(self.dgroup_stats_needed[d][properties.DGROUP_RECONSTRUCTION_READS], i,
                   dg_metrics.disk_metrics.background_work.reconstruction_needed.reads)
            np.put(self.dgroup_stats_needed[d][properties.DGROUP_RECONSTRUCTION_WRITES], i,
                   dg_metrics.disk_metrics.background_work.reconstruction_needed.writes)

            np.put(self.dgroup_stats_needed[d][properties.DGROUP_URGENT_REDISTRIBUTION_IO], i,
                   dg_metrics.disk_metrics.background_work.urgent_reencoding_needed.io)
            np.put(self.dgroup_stats_needed[d][properties.DGROUP_URGENT_REDISTRIBUTION_READS], i,
                   dg_metrics.disk_metrics.background_work.urgent_reencoding_needed.reads)
            np.put(self.dgroup_stats_needed[d][properties.DGROUP_URGENT_REDISTRIBUTION_WRITES], i,
                   dg_metrics.disk_metrics.background_work.urgent_reencoding_needed.writes)

            np.put(self.dgroup_stats_needed[d][properties.DGROUP_SCHEDULABLE_IO], i,
                   dg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.io)
            np.put(self.dgroup_stats_needed[d][properties.DGROUP_SCHEDULABLE_READS], i,
                   dg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.reads)
            np.put(self.dgroup_stats_needed[d][properties.DGROUP_SCHEDULABLE_WRITES], i,
                   dg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.writes)

            np.put(self.dgroup_stats_needed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_IO], i,
                   dg_metrics.disk_metrics.background_work.non_urgent_reencoding_needed.io)
            np.put(self.dgroup_stats_needed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_READS], i,
                   dg_metrics.disk_metrics.background_work.non_urgent_reencoding_needed.reads)
            np.put(self.dgroup_stats_needed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_WRITES], i,
                   dg_metrics.disk_metrics.background_work.non_urgent_reencoding_needed.writes)

            np.put(self.dgroup_stats_needed[d][properties.DGROUP_DECOMMISSIONING_IO], i,
                   dg_metrics.disk_metrics.background_work.decommissioning_needed.io)
            np.put(self.dgroup_stats_needed[d][properties.DGROUP_DECOMMISSIONING_READS], i,
                   dg_metrics.disk_metrics.background_work.decommissioning_needed.reads)
            np.put(self.dgroup_stats_needed[d][properties.DGROUP_DECOMMISSIONING_WRITES], i,
                   dg_metrics.disk_metrics.background_work.decommissioning_needed.writes)

            # performed
            np.put(self.dgroup_stats_performed[d][properties.DGROUP_RECONSTRUCTION_IO], i,
                   dg_metrics.disk_metrics.background_work.reconstruction_performed.io)
            np.put(self.dgroup_stats_performed[d][properties.DGROUP_RECONSTRUCTION_READS], i,
                   dg_metrics.disk_metrics.background_work.reconstruction_performed.reads)
            np.put(self.dgroup_stats_performed[d][properties.DGROUP_RECONSTRUCTION_WRITES], i,
                   dg_metrics.disk_metrics.background_work.reconstruction_performed.writes)

            np.put(self.dgroup_stats_performed[d][properties.DGROUP_URGENT_REDISTRIBUTION_IO], i,
                   dg_metrics.disk_metrics.background_work.urgent_reencoding_performed.io)
            np.put(self.dgroup_stats_performed[d][properties.DGROUP_URGENT_REDISTRIBUTION_READS], i,
                   dg_metrics.disk_metrics.background_work.urgent_reencoding_performed.reads)
            np.put(self.dgroup_stats_performed[d][properties.DGROUP_URGENT_REDISTRIBUTION_WRITES], i,
                   dg_metrics.disk_metrics.background_work.urgent_reencoding_performed.writes)

            np.put(self.dgroup_stats_performed[d][properties.DGROUP_SCHEDULABLE_IO], i,
                   dg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.io)
            np.put(self.dgroup_stats_performed[d][properties.DGROUP_SCHEDULABLE_READS], i,
                   dg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.reads)
            np.put(self.dgroup_stats_performed[d][properties.DGROUP_SCHEDULABLE_WRITES], i,
                   dg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.writes)

            np.put(self.dgroup_stats_performed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_IO], i,
                   dg_metrics.disk_metrics.background_work.non_urgent_reencoding_performed.io)
            np.put(self.dgroup_stats_performed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_READS], i,
                   dg_metrics.disk_metrics.background_work.non_urgent_reencoding_performed.reads)
            np.put(self.dgroup_stats_performed[d][properties.DGROUP_NON_URGENT_REDISTRIBUTION_WRITES], i,
                   dg_metrics.disk_metrics.background_work.non_urgent_reencoding_performed.writes)

            np.put(self.dgroup_stats_performed[d][properties.DGROUP_DECOMMISSIONING_IO], i,
                   dg_metrics.disk_metrics.background_work.decommissioning_performed.io)
            np.put(self.dgroup_stats_performed[d][properties.DGROUP_DECOMMISSIONING_READS], i,
                   dg_metrics.disk_metrics.background_work.decommissioning_performed.reads)
            np.put(self.dgroup_stats_performed[d][properties.DGROUP_DECOMMISSIONING_WRITES], i,
                   dg_metrics.disk_metrics.background_work.decommissioning_performed.writes)

        total_rgroup_capacity = dict()
        for dg, date_dict in step_wise_metrics.items():
            for dt, tup in date_dict.items():
                step_rgroup_metrics = tup[1]
                for rg, rg_metrics in step_rgroup_metrics.items():
                    if rg not in total_rgroup_capacity:
                        total_rgroup_capacity[rg] = 0
                    total_rgroup_capacity[rg] += rg_metrics.disk_metrics.capacity

        for rg, rg_metrics in rgroup_metrics.items():
            if rg not in total_rgroup_capacity:
                total_rgroup_capacity[rg] = 0
            total_rgroup_capacity[rg] += rg_metrics.disk_metrics.capacity

        for rg, rg_metrics in rgroup_metrics.items():
            r = rg.name

            if r not in self.rgroup_stats:
                self._setup_rgroup_stats(r)

            np.put(self.rgroup_stats[r][properties.RGROUP_RUNNING_NUM_DISKS], i,
                   rg_metrics.disk_metrics.num_running_disks)
            np.put(self.rgroup_stats[r][properties.RGROUP_FAILED_NUM_DISKS], i,
                   rg_metrics.disk_metrics.num_failed_disks)
            np.put(self.rgroup_stats[r][properties.RGROUP_DECOMMISSIONED_NUM_DISKS], i,
                   rg_metrics.disk_metrics.num_decommissioned_disks)
            # np.put(self.rgroup_stats[r][properties.RGROUP_CAPACITY], i,
            #        rg_metrics.disk_metrics.capacity)
            np.put(self.rgroup_stats[r][properties.RGROUP_CAPACITY], i, total_rgroup_capacity[rg])

            # needed
            np.put(self.rgroup_stats_needed[r][properties.RGROUP_RECONSTRUCTION_IO], i,
                   rg_metrics.disk_metrics.background_work.reconstruction_needed.io)
            np.put(self.rgroup_stats_needed[r][properties.RGROUP_RECONSTRUCTION_READS], i,
                   rg_metrics.disk_metrics.background_work.reconstruction_needed.reads)
            np.put(self.rgroup_stats_needed[r][properties.RGROUP_RECONSTRUCTION_WRITES], i,
                   rg_metrics.disk_metrics.background_work.reconstruction_needed.writes)

            np.put(self.rgroup_stats_needed[r][properties.RGROUP_URGENT_REDISTRIBUTION_IO], i,
                   rg_metrics.disk_metrics.background_work.urgent_reencoding_needed.io)
            np.put(self.rgroup_stats_needed[r][properties.RGROUP_URGENT_REDISTRIBUTION_READS], i,
                   rg_metrics.disk_metrics.background_work.urgent_reencoding_needed.reads)
            np.put(self.rgroup_stats_needed[r][properties.RGROUP_URGENT_REDISTRIBUTION_WRITES], i,
                   rg_metrics.disk_metrics.background_work.urgent_reencoding_needed.writes)

            np.put(self.rgroup_stats_needed[r][properties.RGROUP_SCHEDULABLE_IO], i,
                   rg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.io)
            np.put(self.rgroup_stats_needed[r][properties.RGROUP_SCHEDULABLE_READS], i,
                   rg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.reads)
            np.put(self.rgroup_stats_needed[r][properties.RGROUP_SCHEDULABLE_WRITES], i,
                   rg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.writes)

            np.put(self.rgroup_stats_needed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_IO], i,
                   rg_metrics.disk_metrics.background_work.non_urgent_reencoding_needed.io)
            np.put(self.rgroup_stats_needed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_READS], i,
                   rg_metrics.disk_metrics.background_work.non_urgent_reencoding_needed.reads)
            np.put(self.rgroup_stats_needed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_WRITES], i,
                   rg_metrics.disk_metrics.background_work.non_urgent_reencoding_needed.writes)

            np.put(self.rgroup_stats_needed[r][properties.RGROUP_DECOMMISSIONING_IO], i,
                   rg_metrics.disk_metrics.background_work.decommissioning_needed.io)
            np.put(self.rgroup_stats_needed[r][properties.RGROUP_DECOMMISSIONING_READS], i,
                   rg_metrics.disk_metrics.background_work.decommissioning_needed.reads)
            np.put(self.rgroup_stats_needed[r][properties.RGROUP_DECOMMISSIONING_WRITES], i,
                   rg_metrics.disk_metrics.background_work.decommissioning_needed.writes)

            # performed
            np.put(self.rgroup_stats_performed[r][properties.RGROUP_RECONSTRUCTION_IO], i,
                   rg_metrics.disk_metrics.background_work.reconstruction_performed.io)
            np.put(self.rgroup_stats_performed[r][properties.RGROUP_RECONSTRUCTION_READS], i,
                   rg_metrics.disk_metrics.background_work.reconstruction_performed.reads)
            np.put(self.rgroup_stats_performed[r][properties.RGROUP_RECONSTRUCTION_WRITES], i,
                   rg_metrics.disk_metrics.background_work.reconstruction_performed.writes)

            np.put(self.rgroup_stats_performed[r][properties.RGROUP_URGENT_REDISTRIBUTION_IO], i,
                   rg_metrics.disk_metrics.background_work.urgent_reencoding_performed.io)
            np.put(self.rgroup_stats_performed[r][properties.RGROUP_URGENT_REDISTRIBUTION_READS], i,
                   rg_metrics.disk_metrics.background_work.urgent_reencoding_performed.reads)
            np.put(self.rgroup_stats_performed[r][properties.RGROUP_URGENT_REDISTRIBUTION_WRITES], i,
                   rg_metrics.disk_metrics.background_work.urgent_reencoding_performed.writes)

            np.put(self.rgroup_stats_performed[r][properties.RGROUP_SCHEDULABLE_IO], i,
                   rg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.io)
            np.put(self.rgroup_stats_performed[r][properties.RGROUP_SCHEDULABLE_READS], i,
                   rg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.reads)
            np.put(self.rgroup_stats_performed[r][properties.RGROUP_SCHEDULABLE_WRITES], i,
                   rg_metrics.disk_metrics.background_work.schedulable_reencoding_needed.writes)

            np.put(self.rgroup_stats_performed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_IO], i,
                   rg_metrics.disk_metrics.background_work.non_urgent_reencoding_performed.io)
            np.put(self.rgroup_stats_performed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_READS], i,
                   rg_metrics.disk_metrics.background_work.non_urgent_reencoding_performed.reads)
            np.put(self.rgroup_stats_performed[r][properties.RGROUP_NON_URGENT_REDISTRIBUTION_WRITES], i,
                   rg_metrics.disk_metrics.background_work.non_urgent_reencoding_performed.writes)

            np.put(self.rgroup_stats_performed[r][properties.RGROUP_DECOMMISSIONING_IO], i,
                   rg_metrics.disk_metrics.background_work.decommissioning_performed.io)
            np.put(self.rgroup_stats_performed[r][properties.RGROUP_DECOMMISSIONING_READS], i,
                   rg_metrics.disk_metrics.background_work.decommissioning_performed.reads)
            np.put(self.rgroup_stats_performed[r][properties.RGROUP_DECOMMISSIONING_WRITES], i,
                   rg_metrics.disk_metrics.background_work.decommissioning_performed.writes)

    def save_metrics_to_file(self):
        # today = datetime.datetime.today().strftime('%Y-%m-%d')
        os.makedirs(common.results_dir, exist_ok=True)
        os.makedirs(common.results_dir + "/plots", exist_ok=True)

        df = pd.DataFrame(self.running_disk_stats[properties.TOTAL_CLUSTER_IO_BANDWIDTH],
                          columns=[properties.TOTAL_CLUSTER_IO_BANDWIDTH])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH_ALLOWED,
                  self.running_disk_stats[properties.TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH_ALLOWED])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_RECONSTRUCTION_IO,
                  self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_RECONSTRUCTION_IO])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO,
                  self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO,
                  self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_SCRUBBING_IO,
                  self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCRUBBING_IO])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_DECOMMISSIONING_IO,
                  self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_DECOMMISSIONING_IO])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_SCHEDULABLE_IO,
                  self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCHEDULABLE_IO])
        if (self.canary is True) and (self.iterative_cp is False):
            df.to_csv(common.results_dir + "/" +
                      self.transcoding_policy + "_total_cluster_stats_needed_" +
                      str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_canary.csv")
        elif (self.canary is False) and (self.iterative_cp is True):
            df.to_csv(common.results_dir + "/" +
                      self.transcoding_policy + "_total_cluster_stats_needed_" +
                      str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_iterative_cp.csv")
        elif (self.canary is False) and (self.iterative_cp is False):
            df.to_csv(common.results_dir + "/" +
                      self.transcoding_policy + "_total_cluster_stats_needed_" +
                      str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_vanilla.csv")
        else:
            df.to_csv(common.results_dir + "/" +
                  self.transcoding_policy + "_total_cluster_stats_needed_" +
                  str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%.csv")

        df = pd.DataFrame(self.running_disk_stats[properties.TOTAL_CLUSTER_IO_BANDWIDTH],
                          columns=[properties.TOTAL_CLUSTER_IO_BANDWIDTH])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH_ALLOWED,
                  self.running_disk_stats[properties.TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH_ALLOWED])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_RECONSTRUCTION_IO,
                  self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_RECONSTRUCTION_IO])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO,
                  self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO,
                  self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_SCRUBBING_IO,
                  self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCRUBBING_IO])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_DECOMMISSIONING_IO,
                  self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_DECOMMISSIONING_IO])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_SCHEDULABLE_IO,
                  self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCHEDULABLE_IO])
        df.insert(df.shape[1], properties.NUM_RUNNING_DISKS, self.running_disk_stats[properties.NUM_RUNNING_DISKS])
        df.insert(df.shape[1], properties.NUM_FAILED_DISKS, self.running_disk_stats[properties.NUM_FAILED_DISKS])
        df.insert(df.shape[1], properties.INFANCY_NUM_DISKS, self.running_disk_stats[properties.INFANCY_NUM_DISKS])
        df.insert(df.shape[1], properties.WEAROUT_NUM_DISKS, self.running_disk_stats[properties.WEAROUT_NUM_DISKS])
        df.insert(df.shape[1], properties.USEFUL_LIFE_NUM_DISKS, self.running_disk_stats[properties.USEFUL_LIFE_NUM_DISKS])
        df.insert(df.shape[1], properties.NUM_DECOMMISSIONED_DISKS, self.running_disk_stats[properties.NUM_DECOMMISSIONED_DISKS])
        df.insert(df.shape[1], properties.TOTAL_CLUSTER_CAPACITY,
                  self.running_disk_stats[properties.TOTAL_CLUSTER_CAPACITY])
        if (self.canary is True) and (self.iterative_cp is False):
            df.to_csv(common.results_dir + "/" +
                      self.transcoding_policy + "_total_cluster_stats_performed_" +
                      str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_canary.csv")
        elif (self.canary is False) and (self.iterative_cp is True):
            df.to_csv(common.results_dir + "/" +
                      self.transcoding_policy + "_total_cluster_stats_performed_" +
                      str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_iterative_cp.csv")
        elif (self.canary is False) and (self.iterative_cp is False):
            df.to_csv(common.results_dir + "/" +
                      self.transcoding_policy + "_total_cluster_stats_performed_" +
                      str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%" + "_vanilla.csv")
        else:
            df.to_csv(common.results_dir + "/" +
                      self.transcoding_policy + "_total_cluster_stats_performed_" +
                      str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%.csv")

        if (self.canary is True) and (self.iterative_cp is False):
            f = open(common.results_dir + "/" +
                     self.transcoding_policy + "_dgroup_list_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                     "%_canary.txt", "w")
        elif (self.canary is False) and (self.iterative_cp is True):
            f = open(common.results_dir + "/" +
                     self.transcoding_policy + "_dgroup_list_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                     "%_iterative_cp.txt", "w")
        elif (self.canary is False) and (self.iterative_cp is False):
            f = open(common.results_dir + "/" +
                     self.transcoding_policy + "_dgroup_list_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                     "%_vanilla.txt", "w")
        else:
            f = open(common.results_dir + "/" +
                     self.transcoding_policy + "_dgroup_list_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                     "%.txt", "w")

        for d in common.dgroups:
            f.write(d + "\n")
            df = pd.DataFrame(self.dgroup_stats[d][properties.DGROUP_RUNNING_NUM_DISKS],
                              columns=[properties.DGROUP_RUNNING_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_INFANCY_NUM_DISKS,
                      self.dgroup_stats[d][properties.DGROUP_INFANCY_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_USEFUL_LIFE_NUM_DISKS,
                      self.dgroup_stats[d][properties.DGROUP_USEFUL_LIFE_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_WEAROUT_NUM_DISKS,
                      self.dgroup_stats[d][properties.DGROUP_WEAROUT_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_FAILED_NUM_DISKS,
                      self.dgroup_stats[d][properties.DGROUP_FAILED_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_DECOMMISSIONED_NUM_DISKS,
                      self.dgroup_stats[d][properties.DGROUP_DECOMMISSIONED_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_CANARY_RUNNING_NUM_DISKS,
                      self.dgroup_stats[d][properties.DGROUP_CANARY_RUNNING_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_CANARY_INFANCY_NUM_DISKS,
                      self.dgroup_stats[d][properties.DGROUP_CANARY_INFANCY_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_CANARY_USEFUL_LIFE_NUM_DISKS,
                      self.dgroup_stats[d][properties.DGROUP_CANARY_USEFUL_LIFE_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_CANARY_WEAROUT_NUM_DISKS,
                      self.dgroup_stats[d][properties.DGROUP_CANARY_WEAROUT_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_CANARY_FAILED_NUM_DISKS,
                      self.dgroup_stats[d][properties.DGROUP_CANARY_FAILED_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_CANARY_DECOMMISSIONED_NUM_DISKS,
                      self.dgroup_stats[d][properties.DGROUP_CANARY_DECOMMISSIONED_NUM_DISKS])
            df.insert(df.shape[1], properties.DGROUP_CAPACITY,
                      self.dgroup_stats[d][properties.DGROUP_CAPACITY])
            os.makedirs(common.results_dir + "/" + d, exist_ok=True)
            if (self.canary is True) and (self.iterative_cp is False):
                df.to_csv(common.results_dir + "/" + d + "/" + self.transcoding_policy +
                          "_dgroup_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                          "%_canary.csv")
            elif (self.canary is False) and (self.iterative_cp is True):
                df.to_csv(common.results_dir + "/" + d + "/" + self.transcoding_policy +
                          "_dgroup_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                          "%_iterative_cp.csv")
            elif (self.canary is False) and (self.iterative_cp is False):
                df.to_csv(common.results_dir + "/" + d + "/" + self.transcoding_policy +
                          "_dgroup_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                          "%_vanilla.csv")
            else:
                df.to_csv(common.results_dir + "/" + d + "/" + self.transcoding_policy +
                          "_dgroup_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%.csv")

        f.close()

        disk_days_map = dict()
        disk_days_map[str(constants.DEFAULT_REDUNDANCY_SCHEME)] = 0
        if (self.canary is True) and (self.iterative_cp is False):
            f = open(common.results_dir + "/" +
                     self.transcoding_policy + "_rgroup_list_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                     "%_canary.txt", "w")
        elif (self.canary is False) and (self.iterative_cp is True):
            f = open(common.results_dir + "/" +
                     self.transcoding_policy + "_rgroup_list_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                     "%_iterative_cp.txt", "w")
        elif (self.canary is False) and (self.iterative_cp is False):
            f = open(common.results_dir + "/" +
                     self.transcoding_policy + "_rgroup_list_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                     "%_vanilla.txt", "w")
        else:
            f = open(common.results_dir + "/" +
                     self.transcoding_policy + "_rgroup_list_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                     "%.txt", "w")

        for r in common.rgroups:
            if r not in self.rgroup_stats:
                logging.info("Rgroup " + r + " not in rgroup_stats.")
                continue

            f.write(r + "\n")

            df = pd.DataFrame(self.rgroup_stats[r][properties.RGROUP_RUNNING_NUM_DISKS],
                              columns=[properties.RGROUP_RUNNING_NUM_DISKS])
            df.insert(df.shape[1], properties.RGROUP_DECOMMISSIONED_NUM_DISKS,
                      self.rgroup_stats[r][properties.RGROUP_DECOMMISSIONED_NUM_DISKS])
            df.insert(df.shape[1], properties.RGROUP_CAPACITY,
                      self.rgroup_stats[r][properties.RGROUP_CAPACITY])
            df.insert(df.shape[1], properties.RGROUP_FAILED_NUM_DISKS,
                      self.rgroup_stats[r][properties.RGROUP_FAILED_NUM_DISKS])
            os.makedirs(common.results_dir + "/" + r, exist_ok=True)
            if (self.canary is True) and (self.iterative_cp is False):
                df.to_csv(common.results_dir + "/" + r + "/" + self.transcoding_policy +
                          "_rgroup_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                          "%_canary.csv")
            elif (self.canary is False) and (self.iterative_cp is True):
                df.to_csv(common.results_dir + "/" + r + "/" + self.transcoding_policy +
                          "_rgroup_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                          "%_iterative_cp.csv")
            elif (self.canary is False) and (self.iterative_cp is False):
                df.to_csv(common.results_dir + "/" + r + "/" + self.transcoding_policy +
                          "_rgroup_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) +
                          "%_vanilla.csv")
            else:
                df.to_csv(common.results_dir+ "/" + r + "/" + self.transcoding_policy +
                          "_rgroup_stats_performed_" + str(constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%.csv")

            disk_days_map[r] = sum(self.rgroup_stats[r][properties.RGROUP_RUNNING_NUM_DISKS])
            disk_days_map[str(constants.DEFAULT_REDUNDANCY_SCHEME)] += sum(self.rgroup_stats[r][properties.RGROUP_RUNNING_NUM_DISKS])
        f.close()



        # df.insert(df.shape[1], "total_cluster_reencoding_io_performed",
        #           self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCHEDULABLE_IO])
        # df.insert(df.shape[1], "total_cluster_reencoding_io_remaining",
        #           self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCHEDULABLE_IO] -
        #           self.running_disk_stats[properties.PERFORMED][properties.TOTAL_CLUSTER_SCHEDULABLE_IO])
        # df.insert(df.shape[1], "total_cluster_scrubbing",
        #           self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCRUBBING_IO])
        # df.insert(df.shape[1], "total_transcoding_disks_read",
        #           self.running_disk_stats[properties.NEEDED][properties.TOTAL_CLUSTER_SCHEDULABLE_IO])
        # df.insert(df.shape[1], "total_transcoding_disks_written",
        #           metrics.io_overhead['total_transcoding_disks_written']['io'])
        # df.insert(df.shape[1], "total_transcoding_read_ios_performed",
        #           metrics.io_overhead['total_transcoding_read_ios_performed']['io'])
        # df.insert(df.shape[1], "total_transcoding_write_ios_performed",
        #           metrics.io_overhead['total_transcoding_write_ios_performed']['io'])

        # for scheme, values in metrics.io_overhead['total_rgroup_capacity'].items():
        #     df.insert(df.shape[1], "redundancy_scheme_" + str(scheme),
        #               metrics.io_overhead['total_rgroup_capacity'][scheme])
        # df.to_csv("results/" + today + "/date_wise/data/" + self.transcoding_policy + "_total_cluster_stats_" + str(
        #     constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%.csv")
        #
        # for dg in disk_groups:
        #     os.makedirs("results/" + today + "/date_wise/" + dg + "/data", exist_ok=True)
        #     df = pd.DataFrame(metrics.io_overhead['total_cluster_io_capacity']['io'],
        #                       columns=["total_cluster_io_capacity"])
        #     df.insert(df.shape[1], "reconstruction", metrics.io_overhead[dg]['reconstruction']['io'])
        #     df.insert(df.shape[1], "schedulable_reencoding_required",
        #               metrics.io_overhead[dg]['schedulable_reencoding_required']['io'])
        #     df.insert(df.shape[1], "urgent_reencoding_required",
        #               metrics.io_overhead[dg]['urgent_reencoding_required']['io'])
        #     df.insert(df.shape[1], "reencoding_performed", metrics.io_overhead[dg]['reencoding_performed']['io'])
        #     df.insert(df.shape[1], "reencoding_required", metrics.io_overhead[dg]['reencoding_required']['io'])
        #     df.insert(df.shape[1], "total_cluster_background_io_allowed",
        #               metrics.io_overhead['total_cluster_background_io_allowed']['io'])
        #     df.insert(df.shape[1], "total_cluster_scrubbing", metrics.io_overhead['total_cluster_scrubbing']['io'])
        #     df.insert(df.shape[1], "infancy", metrics.phase_of_life[dg]['infancy'])
        #     df.insert(df.shape[1], "useful_life", metrics.phase_of_life[dg]['useful_life'])
        #     df.insert(df.shape[1], "wearout", metrics.phase_of_life[dg]['wearout'])
        #     df.to_csv("results/" + today + "/date_wise/" + dg + "/data/disk_group_stats_" + str(
        #         constants.BACKGROUND_IO_BANDWIDTH_PERCENTAGE) + "%.csv")
