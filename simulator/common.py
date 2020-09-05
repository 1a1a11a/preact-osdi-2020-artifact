#!/usr/local/bin/python3

# This is the file containing common functions useful across different modules.

import numpy as np
from datetime import timedelta, date
import datetime
import calendar
from scipy.special import comb
import math
import scipy.stats
from rgroups.rgroup import RGroup
import constants

disk_shortname_map = dict()
disk_shortname_map["HGST HMS5C4040ALE640"] = 'H4A'
disk_shortname_map["HGST HMS5C4040BLE640"] = 'H4B'
disk_shortname_map["ST4000DM000"] = 'S4'
disk_shortname_map["ST8000DM002"] = 'S8C'
disk_shortname_map["ST8000NM0055"] = 'S8E'
disk_shortname_map["ST12000NM0007"] = 'S12E'
disk_shortname_map["HGST HUH721212ALN604"] = 'H12E'

# disk capacity map
disk_capacity = dict()
disk_capacity["ST4000DM000"] = 4
disk_capacity["HGST HMS5C4040ALE640"] = 4
disk_capacity["HGST HMS5C4040BLE640"] = 4
disk_capacity["ST8000DM002"] = 8
disk_capacity["ST8000NM0055"] = 8
disk_capacity["ST12000NM0007"] = 12
disk_capacity["HGST HUH721212ALN604"] = 12

deployment_type = dict()
deployment_type['bb'] = dict()
deployment_type['bb']["ST4000DM000"] = constants.DeploymentType.TRICKLE
deployment_type['bb']["HGST HMS5C4040ALE640"] = constants.DeploymentType.TRICKLE
deployment_type['bb']["HGST HMS5C4040BLE640"] = constants.DeploymentType.TRICKLE
deployment_type['bb']["ST8000DM002"] = constants.DeploymentType.TRICKLE
deployment_type['bb']["ST8000NM0055"] = constants.DeploymentType.TRICKLE
deployment_type['bb']["ST12000NM0007"] = constants.DeploymentType.TRICKLE
deployment_type['bb']["HGST HUH721212ALN604"] = constants.DeploymentType.TRICKLE

# cluster obfuscation map
cluster_obfuscation_map = dict()
cluster_obfuscation_map["bb"] = "backblaze"

# cluster size map
cluster_num_disks = dict()
cluster_num_disks['bb'] = 130000

# subtract days map
subtract_days = dict()

subtract_days['bb'] = dict()
subtract_days['bb']["HGST HMS5C4040ALE640"] = 447
subtract_days['bb']["HGST HMS5C4040BLE640"] = 233
subtract_days['bb']["ST4000DM000"] = 166
subtract_days['bb']["ST8000DM002"] = 89
subtract_days['bb']["ST8000NM0055"] = 151
subtract_days['bb']["ST12000NM0007"] = 65
subtract_days['bb']["HGST HUH721212ALN604"] = 233

# color dict
rg_color_dict = dict()
rg_color_dict["(9, 3)"] = "blue"
rg_color_dict["(13, 3)"] = "purple"
rg_color_dict["(14, 3)"] = "blue"
rg_color_dict["(15, 3)"] = "brown"
rg_color_dict["(16, 3)"] = "teal"
rg_color_dict["(17, 3)"] = "indigo"
rg_color_dict["(18, 3)"] = "midnightblue"
rg_color_dict["(19, 3)"] = "saddlebrown"
rg_color_dict["(20, 3)"] = "blue"
rg_color_dict["(21, 3)"] = "olive"
rg_color_dict["(22, 3)"] = "olive"
rg_color_dict["(23, 3)"] = "violet"
rg_color_dict["(24, 3)"] = "darkviolet"
rg_color_dict["(25, 3)"] = "teal"
rg_color_dict["(26, 3)"] = "pink"
rg_color_dict["(27, 3)"] = "blue"
rg_color_dict["(28, 3)"] = "darkblue"
rg_color_dict["(29, 3)"] = "black"
rg_color_dict["(30, 3)"] = "olive"
rg_color_dict["(31, 3)"] = "blue"
rg_color_dict["(33, 3)"] = "darkgreen"
rg_color_dict["(9, 3)_wearout"] = "maroon"

# cluster
cluster = constants.DEFAULT_CLUSTER

# min useful life AFR in cluster
min_useful_life_afr = constants.DEFAULT_AFR

naive = "Pacemaker"

multi = "SINGLE"

results_dir = ""

# Master Dgroup map
dgroups = dict()

# Master Rgroup map
rgroups = dict()
rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)] = RGroup(
    str(constants.DEFAULT_REDUNDANCY_SCHEME),
    constants.DEFAULT_REDUNDANCY_SCHEME[0] -
    constants.DEFAULT_REDUNDANCY_SCHEME[1],
    constants.DEFAULT_REDUNDANCY_SCHEME[1])
rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].tolerable_afr = constants.DEFAULT_AFR
rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].overhead = float(constants.DEFAULT_REDUNDANCY_SCHEME[0]) / (
        constants.DEFAULT_REDUNDANCY_SCHEME[0] - constants.DEFAULT_REDUNDANCY_SCHEME[1])

rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"] = RGroup(
    str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout", constants.DEFAULT_REDUNDANCY_SCHEME[0] -
                                         constants.DEFAULT_REDUNDANCY_SCHEME[1], constants.DEFAULT_REDUNDANCY_SCHEME[1])
rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"].overhead = float(constants.DEFAULT_REDUNDANCY_SCHEME[0]) / (
        constants.DEFAULT_REDUNDANCY_SCHEME[0] - constants.DEFAULT_REDUNDANCY_SCHEME[1])
rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME) + "_wearout"].tolerable_afr = constants.DEFAULT_AFR

rgroups_by_overhead = list([(float(rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].data_chunks +
                                   rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].code_chunks) /
                             rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)].data_chunks,
                             rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)])])

day_wise_dt_range = list()

def chernoff_hoeffding_bound(p):
    delta = 0.2
    confidence = 0.01
    return -np.log(confidence) / (p * delta + p * (1 - delta) * np.log(1 - delta))

def daterange(date1, date2):
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + timedelta(n)

def get_confident_instantaneous_afr(afr_mean, disk_days, failures):
    std_dev = float(math.sqrt(failures)) / disk_days
    std_dev *= (365 * 100)
    annualized_error = scipy.stats.norm.ppf(0.999) * std_dev
    confident_afr = afr_mean + annualized_error
    return confident_afr

def days_between(d1, d2):
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def lakhs(x, pos):
    'The two args are the value and tick position'
    if x == 0:
        return 0
    return '%1dK' % (x * 1e-3)
