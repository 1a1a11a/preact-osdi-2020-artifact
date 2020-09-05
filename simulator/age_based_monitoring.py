#!/usr/local/bin/python3

import sys
import constants
import common
import datetime
from datetime import timedelta, date
import os.path
import pandas as pd
import matplotlib.pyplot as plt
import json
from ast import literal_eval
import matplotlib
sys.path.append("dgroups")
import logging
from dgroups import DGroup


# matplotlib.rcParams.update({'font.size': 14})

def monitor_by_age(disk_groups, dataset):
    # the flow is as follows:
    # get dataset -> get disk groups -> initialize dg with its anomaly checker and change point detector ->
    # perform infant mortality detection -> perform old age detection -> plot -> cleanup
    #
    # "HGST HMS5C4040ALE640", "HGST HMS5C4040BLE640", "ST4000DM000", "ST8000DM002",
    # "ST8000NM0055", "ST12000NM0007", "HGST HUH721212ALN604"

    for dg, dg_instance in disk_groups.items():
        # dg_instance = DGroup(dg, dataset=dataset)
        dg_instance.revise_afr_curve(today="2019-12-31", from_age=0, cumulative=True)
        fig = None
        axarr = None
        # if dg_instance.deployment_type == constants.DeploymentType.TRICKLE:
        #     fig, axarr = dg_instance.plot_afr("cum_afr")
        # dg_instance.revise_afr_curve(today="2019-12-31", from_age=0, cumulative=True)
        fig, axarr = dg_instance.plot_age_afr("cum_afr", fig=fig, axarr=axarr)
        plt.gcf().clear()
