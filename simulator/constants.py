#!/usr/local/bin/python3
import logging
import math
from enum import Enum

LOG_LEVEL_CONFIG = 60
logging.addLevelName(60, "CONFIG")

# To threshold the "flatness" beyond which useful life starts.
AFR_DIFF_THRESHOLD = 1

# Padding days trying to detect infant mortality.
AGE_EXEMPT_FROM_STABLE_STATE = 90

# Sensitivity for detecting what qualifies as an anomaly. [2, 3, 4] -- not so interesting, can be short
ANOMALY_SCORE_SENSITIVITY = 4.0

# Min num of days in a segment to know if infant mortality has ended.
MIN_SEGMENT_DAYS = 30

# Min days before we can declare infant mortality is over.
MIN_DAYS_BEFORE_STABLE_STATE = 30

# Min days after stable state start before we can declare old age has arrived.
MIN_DAYS_BEFORE_OLD_AGE = 30

# Data batch size, i.e. days of data collected at the same time for analysis
DATA_BATCH_SIZE = 1

# Sliding window for avoiding hysteresis
HYSTERESIS_SLIDING_WINDOW = 30

# Useful life AFR revision interval.
AFR_REVISION_INTERVAL = 30

# Cluster fullness percentage for evaluating how much data should move.
CLUSTER_FULLNESS_PERCENTAGE = 1.0

# Background I/O percentage of bandwidth
BACKGROUND_IO_BANDWIDTH_PERCENTAGE = 5.0

# HDD I/O bandwidth (in MB/sec)
HDD_IO_BANDWIDTH = 100

# AFR buffer above determined AFR.
AFR_BUFFER = 0.5

# Start and end date of analysis for simulator.
END_DATE = "2019-12-31"

# Min sample size for AFR estimation.
MIN_SAMPLE_SIZE = 3000 

# Min failures needed for correct AFR estimation.
MIN_FAILURES_NEEDED = 10

# Kinesis details
# Sleep time (secs.) between Kinesis anomaly detection phases.
SLEEP_TIME_BETWEEN_KINESIS_STAGES = 10
KINESIS_INPUT_STREAM = "HDD_AFR_INPUT_STREAM"
KINESIS_OUTPUT_STREAM = "HDD_AFR_ANOMALY_OUTPUT_STREAM"

# Default redundancy scheme [format is: (total stripe length, number of parities per stripe)]
DEFAULT_REDUNDANCY_SCHEME = (9, 3)
# DEFAULT_REDUNDANCY_SCHEME = (14, 4)

# Default AFR (in percentage)
DEFAULT_AFR = 16

# Anomaly detection
ANOMALY_DETECTOR = "RRCF"

# Change point detector
CHANGE_POINT_DETECTOR = "Ruptures"

# Redundancy schemes
REDUNDANCY_SCHEMES = "MDS"

# Transitioning types
class TransitionType(Enum):
    DECOMMISSIONING = 1
    BULK = 2

# Dataset
DATASET = "Backblaze"

# Deployment strategy
class DeploymentType(Enum):
    STEP = 1
    TRICKLE = 2
    NAIVE = 3

# Data redistribution strategy
REDISTRIBUTION_STRATEGY = "CheapDataRedistribution"

# Reduced useful life tuneable
REDUCED_USEFUL_LIFE_AGE = 30 

# Trigger wearout capacity needed (in days)
TRIGGER_TRANSITION_SPACE_WARNING = 80

# Maximum stripe width allowed
MAX_STRIPE_DIMENSION = 30

# Minimum parities per stripe
MIN_PARITIES_PER_STRIPE = 3

# Max MTTR in hours to repair a failed disk
MAX_MTTR_ALLOWED = 1.5

# Min MTTR it takes to repair a failed disk
MIN_MTTR_ACHIEVED = 0.5

# Transcoding policies
transcoding_policies = ["Decommission"]

# Scrubbing rate
SCRUBBING_RATE = float(1 / 14)

# Default cluster
DEFAULT_CLUSTER = "default"

# Min Rgroup size
MIN_RGROUP_SIZE = 1000

# Prefetch wearout by at most these many days.
WEAROUT_AGE_PADDING = 60

# Cap on future retirement work
FUTURE_RETIREMENT_WORK_CAP = BACKGROUND_IO_BANDWIDTH_PERCENTAGE

# Deviation from AFR to suggest wearout is far.
MIN_AFR_DEVIATION_NEEDED = 0.5

# Min age difference (in days) needed for adopting a new second level passing age
MIN_SECOND_LEVEL_AGE_DEVIATION_NEEDED = 30

# Y-axis limits for plotting
Y_AXIS_LIMITS = [20]

# Change point types
RUP_CHANGE = "RUp"
RDN_CHANGE = "RDn"

###### OPTIMIZATIONS ######
# Iterative CP
ITERATIVE_CP = False

# Mutiple phases in life
MULTI_PHASE = False

# Canary
CANARY = False

# Plot step-wise IO plots
STEP_WISE_GRAPHS = False

# Plot only first page IO plots.
FRONT_GRAPH = False

# Plot mono version of front graph.
FRONT_GRAPH_MONO = False

# Days to average the slope over, when we want to change phase of life
SLOPE_AVERAGING_WINDOW = 60

# Average lifetime IO bandwidth
AVG_LIFETIME_IO_BANDWIDTH_CAP = 0.01

# How many days in the future you want to project the AFR before choosing AFR
# for next phase of life
AFR_PROJECTION_WINDOW = 1.0 / AVG_LIFETIME_IO_BANDWIDTH_CAP

# What is the AFR threshold (fraction of tolerable AFR) for changing to a
# different phase of life
AFR_PHASE_TRANSITION_THRESHOLD = 0.75

# Work types
class WorkType(Enum):
    INFANCY = 1
    NON_URGENT_WEAROUT = 2
    WEAROUT = 3
