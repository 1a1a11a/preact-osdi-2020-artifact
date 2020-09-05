#!/usr/local/bin/python3


# This is the file that contains all the string constants, similar to a JAVA properties file.

# Dgroup
DGROUP_CAPACITY = "dgroup_capacity"
DGROUP_RUNNING_NUM_DISKS = "dgroup_num_running_disks"
DGROUP_INFANCY_NUM_DISKS = "dgroup_infancy_num_disks"
DGROUP_USEFUL_LIFE_NUM_DISKS = "dgroup_useful_life_num_disks"
DGROUP_WEAROUT_NUM_DISKS = "dgroup_wearout_num_disks"
DGROUP_FAILED_NUM_DISKS = "dgroup_failed_num_disks"
DGROUP_DECOMMISSIONED_NUM_DISKS = "dgroup_decommissioned_num_disks"

DGROUP_CANARY_RUNNING_NUM_DISKS = "dgroup_canary_num_disks"
DGROUP_CANARY_INFANCY_NUM_DISKS = "dgroup_canary_infancy_num_disks"
DGROUP_CANARY_USEFUL_LIFE_NUM_DISKS = "dgroup_canary_useful_life_num_disks"
DGROUP_CANARY_WEAROUT_NUM_DISKS = "dgroup_canary_wearout_num_disks"
DGROUP_CANARY_FAILED_NUM_DISKS = "dgroup_canary_failed_num_disks"
DGROUP_CANARY_DECOMMISSIONED_NUM_DISKS = "dgroup_canary_decommissioned_num_disks"

DGROUP_RECONSTRUCTION_IO = "dgroup_reconstruction_io"
DGROUP_RECONSTRUCTION_READS = "dgroup_reconstruction_reads"
DGROUP_RECONSTRUCTION_WRITES = "dgroup_reconstruction_writes"

DGROUP_SCHEDULABLE_IO = "dgroup_schedulable_io"
DGROUP_SCHEDULABLE_READS = "dgroup_schedulable_reads"
DGROUP_SCHEDULABLE_WRITES = "dgroup_schedulable_writes"

DGROUP_DECOMMISSIONING_IO = "dgroup_decommissioning_io"
DGROUP_DECOMMISSIONING_READS = "dgroup_decommissioning_reads"
DGROUP_DECOMMISSIONING_WRITES = "dgroup_decommissioning_writes"

DGROUP_URGENT_REDISTRIBUTION_IO = "dgroup_urgent_redistribution_io"
DGROUP_URGENT_REDISTRIBUTION_READS = "dgroup_urgent_redistribution_reads"
DGROUP_URGENT_REDISTRIBUTION_WRITES = "dgroup_urgent_redistribution_writes"

DGROUP_NON_URGENT_REDISTRIBUTION_IO = "dgroup_non_urgent_redistribution_io"
DGROUP_NON_URGENT_REDISTRIBUTION_READS = "dgroup_non_urgent_redistribution_reads"
DGROUP_NON_URGENT_REDISTRIBUTION_WRITES = "dgroup_non_urgent_redistribution_writes"

# Rgroup
RGROUP_CAPACITY = "rgroup_capacity"
RGROUP_RUNNING_NUM_DISKS = "rgroup_num_running_disks"
RGROUP_FAILED_NUM_DISKS = "rgroup_failed_num_disks"
RGROUP_DECOMMISSIONED_NUM_DISKS = "rgroup_decommissioned_num_disks"

RGROUP_RECONSTRUCTION_IO = "rgroup_reconstruction_io"
RGROUP_RECONSTRUCTION_READS = "rgroup_reconstruction_reads"
RGROUP_RECONSTRUCTION_WRITES = "rgroup_reconstruction_writes"

RGROUP_SCHEDULABLE_IO = "rgroup_schedulable_io"
RGROUP_SCHEDULABLE_READS = "rgroup_schedulable_reads"
RGROUP_SCHEDULABLE_WRITES = "rgroup_schedulable_writes"

RGROUP_DECOMMISSIONING_IO = "rgroup_decommissioning_io"
RGROUP_DECOMMISSIONING_READS = "rgroup_decommissioning_reads"
RGROUP_DECOMMISSIONING_WRITES = "rgroup_decommissioning_writes"

RGROUP_URGENT_REDISTRIBUTION_IO = "rgroup_urgent_redistribution_io"
RGROUP_URGENT_REDISTRIBUTION_READS = "rgroup_urgent_redistribution_reads"
RGROUP_URGENT_REDISTRIBUTION_WRITES = "rgroup_urgent_redistribution_writes"

RGROUP_NON_URGENT_REDISTRIBUTION_IO = "rgroup_non_urgent_redistribution_io"
RGROUP_NON_URGENT_REDISTRIBUTION_READS = "rgroup_non_urgent_redistribution_reads"
RGROUP_NON_URGENT_REDISTRIBUTION_WRITES = "rgroup_non_urgent_redistribution_writes"

# Total
NUM_FAILED_DISKS = "num_failed_disks"
NUM_DECOMMISSIONED_DISKS = "num_decommissioned_disks"
NUM_RUNNING_DISKS = "num_running_disks"

INFANCY_NUM_DISKS = "infancy_num_disks"
USEFUL_LIFE_NUM_DISKS = "useful_life_num_disks"
WEAROUT_NUM_DISKS = "wearout_num_disks"

CANARY_NUM_DISKS = "canary_num_disks"
CANARY_INFANCY_NUM_DISKS = "canary_infancy_num_disks"
CANARY_USEFUL_LIFE_NUM_DISKS = "canary_useful_life_num_disks"
CANARY_WEAROUT_NUM_DISKS = "canary_wearout_num_disks"

TOTAL_CLUSTER_CAPACITY = "total_cluster_capacity"

TOTAL_CLUSTER_RECONSTRUCTION_IO = "total_cluster_reconstruction_io"
TOTAL_CLUSTER_RECONSTRUCTION_READS = "total_cluster_reconstruction_reads"
TOTAL_CLUSTER_RECONSTRUCTION_WRITES = "total_cluster_reconstruction_writes"

TOTAL_CLUSTER_SCRUBBING_IO = "total_cluster_scrubbing_io"
TOTAL_CLUSTER_SCRUBBING_READS = "total_cluster_scrubbing_reads"
TOTAL_CLUSTER_SCRUBBING_WRITES = "total_cluster_scrubbing_writes"

TOTAL_CLUSTER_URGENT_REDISTRIBUTION_IO = "total_cluster_urgent_redistribution_io"
TOTAL_CLUSTER_URGENT_REDISTRIBUTION_READS = "total_cluster_urgent_redistribution_reads"
TOTAL_CLUSTER_URGENT_REDISTRIBUTION_WRITES = "total_cluster_urgent_redistribution_writes"

TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_IO = "total_cluster_non_urgent_redistribution_io"
TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_READS = "total_cluster_non_urgent_redistribution_reads"
TOTAL_CLUSTER_NON_URGENT_REDISTRIBUTION_WRITES = "total_cluster_non_urgent_redistribution_writes"

TOTAL_CLUSTER_DECOMMISSIONING_IO = "total_cluster_decommissioning_io"
TOTAL_CLUSTER_DECOMMISSIONING_READS = "total_cluster_decommissioning_reads"
TOTAL_CLUSTER_DECOMMISSIONING_WRITES = "total_cluster_decommissioning_writes"

TOTAL_CLUSTER_SCHEDULABLE_IO = "total_cluster_schedulable_io"
TOTAL_CLUSTER_SCHEDULABLE_READS = "total_cluster_schedulable_reads"
TOTAL_CLUSTER_SCHEDULABLE_WRITES = "total_cluster_schedulable_writes"

TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH = "total_cluster_background_io_bandwidth"
TOTAL_CLUSTER_BACKGROUND_IO_BANDWIDTH_ALLOWED = "total_cluster_background_io_allowed"
TOTAL_CLUSTER_IO_BANDWIDTH = "total_cluster_io_bandwidth"

# General strings required
DGROUP = "dgroup"
RGROUP = "rgroup"
TOTAL = "total"
NEEDED = "needed"
PERFORMED = "performed"

# Phase of life constants
PHASE_OF_LIFE_INFANCY = 1
PHASE_OF_LIFE_USEFUL_LIFE = 2
PHASE_OF_LIFE_WEAROUT = 3
PHASE_OF_LIFE_CANARY = 4

# Optimizations
ITERATIVE_CP = "_iterative_cp"
CANARY = "_canary"
VANILLA = "_vanilla"
