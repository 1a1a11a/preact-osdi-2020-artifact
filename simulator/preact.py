#!/usr/local/bin/python3

import argparse

# age_based_monitoring is for calculating the AFR by looking back in time (snapshot) [HeART: FAST 2019].
import age_based_monitoring

# date_based_monitoring is for calculating the overheads by simulating each calendar date [PREACT: OSDI 2020].
import date_based_monitoring

# canary_monitoring is to generate the AFR curve for the batch of disks deployed within the first 7 days.
# Essentially the curve that helps us make the decisions.
import canary_monitoring

import constants
import common
import os
import sys
import logging
import matplotlib
sys.path.append("datasets")
sys.path.append("dgroups")
from dgroups import DGroup
from datasets import Backblaze
import datetime

matplotlib.rcParams.update({'font.size': 14})

parser = argparse.ArgumentParser()
parser.add_argument("--method", metavar='<METHOD>', required=True, choices=('age', 'date', 'canary'),
                    help="Choose method to process disk reliability data (choices = {age, date}).")
group = parser.add_mutually_exclusive_group()
group.add_argument("-m", "--model", help="Run PREACT on a particular make / model.", action='append')
group = parser.add_mutually_exclusive_group()
group.add_argument("-L", "--logging",
                   help="Specify logging level for PREACT (default = INFO). (choices = {INFO, DEBUG, ERROR})",
                   choices=('INFO', 'DEBUG', 'ERROR'))
group = parser.add_mutually_exclusive_group()
group.add_argument("-c", "--cluster", help="Name of the cluster.")
parser.add_argument('--canary', nargs='?', const=True, default=False, help="Enable the canary disk optimization.")
parser.add_argument('--iterative_cp', nargs='?', const=True, default=False,
                    help="Enable the iterative change point detection optimization.")
parser.add_argument('--multi_phase', nargs='?', const=True, default=False,
                    help="Enable having multiple phases of life.")
parser.add_argument('--naive', nargs='?', const=True, default=False,
                    help="Evaluate for naive transitioning.")
parser.add_argument('--front', nargs='?', const=True, default=False,
                    help="Plot only front page graph.")
parser.add_argument('--front_mono', nargs='?', const=True, default=False,
                    help="Plot only front page graph in mono.")
parser.add_argument('--only_plot', nargs='?', const=True, default=False,
                    help="Plot only front page graph.")
parser.add_argument('--step_wise_graphs', nargs='?', const=True, default=False,
                    help="Output each set of graphs for the IO over time. By default this option is "
                         "not set and only the combined graph is generated.")
args = parser.parse_args()

common.cluster = args.cluster

table_to_query = ""
if args.method == "age":
    table_to_query = "summary_drive_stats"
elif args.method == "date" or args.method == "canary":
    table_to_query = "monitored_disks"
else:
    print("Cannot initialize dataset because of wrong method.")
    exit(1)

# Next steps are to setup logging infrastructure.
logging_level = logging.INFO
if args.logging is not None:
    if args.logging == "INFO":
        logging_level = logging.INFO
    elif args.logging == "DEBUG":
        logging_level = logging.DEBUG
    elif args.logging == "ERROR":
        logging_level = logging.ERROR
    else:
        print("Wrong logging level specified. Check help for options.")

LOG_LEVEL_CONFIG = 60
logging.addLevelName(60, "CONFIG")

os.makedirs("logs/", exist_ok=True)
logging.basicConfig(filename='logs/preact_' + common.cluster + "_" +
                             str.join("-", tuple(args.model)).replace(" ", "_")
                             + '.log',
                    format='%(asctime)s [%(levelname)s]: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging_level, filemode='w')

logging.log(LOG_LEVEL_CONFIG, "Dataset %s selected.", constants.DATASET)

constants.ITERATIVE_CP = args.iterative_cp
constants.CANARY = args.canary
constants.MULTI_PHASE = args.multi_phase
constants.STEP_WISE_GRAPHS = args.step_wise_graphs

if args.naive:
    common.naive = "NAIVE"

if args.multi_phase:
    common.multi = "MULTI"

if args.front:
    constants.FRONT_GRAPH = True

if args.front_mono:
    constants.FRONT_GRAPH_MONO = True

today = datetime.datetime.today().strftime('%Y-%m-%d')
common.results_dir = str("results")

logging.info("Results dir = " + common.results_dir)
dataset = eval(constants.DATASET)(table_to_query)

for dg in args.model:
    if args.naive:
        deployment_type = constants.DeploymentType.NAIVE
    else:
        deployment_type = common.deployment_type[common.cluster][dg]
    common.dgroups[dg] = DGroup(dg, capacity=common.disk_capacity[dg],
                                dataset=dataset,
                                type=deployment_type)

if args.method == "age":
    age_based_monitoring.monitor_by_age(common.dgroups, dataset)
elif args.method == "date":
    if not args.only_plot:
        date_based_monitoring.monitor_by_date(common.dgroups, dataset)
    logging.info("Results dir = " + common.results_dir)
    date_based_monitoring.plot_date_wise_io(dataset)
    date_based_monitoring.plot_rgroup_distribution(dataset)
    print("plotting ended!")
    print("################################################")
    print("plots are in: " + common.results_dir + "/plots")
    print("################################################")
elif args.method == "canary":
    canary_monitoring.monitor_canaries(common.dgroups, dataset)
else:
    print("Wrong method chosen to process disk reliability data.")
    exit(1)

exit(0)
