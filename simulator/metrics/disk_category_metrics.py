from dataclasses import dataclass
from metrics.background_work import BackgroundWork
from metrics.work import Work
import numpy as np


'''
For each category of disks, these are the metrics that need to be monitored.
'''
@dataclass
class DiskCategoryMetrics:
    background_work: BackgroundWork
    last_month_transitioned_disks: np.array([])

    num_running_disks: int = 0
    num_failed_disks: int = 0
    num_decommissioned_disks: int = 0
    num_observed_disks: int = 0

    num_disks_skipped_useful_life: int = 0
    num_disks_transitioned_today: int = 0

    avg_disks_transitioned_per_day: int = 0

    capacity: int = 0

    num_infancy_disks: int = 0  # NA in Rgroup
    num_useful_life_disks: int = 0  # NA in Rgroup
    num_wearout_disks: int = 0  # NA in Rgroup
    num_at_risk_disks: int = 0  # NA in Rgroup

    total_background_io_bandwidth_allowed = 0.0
    total_background_io_bandwidth_needed = 0.0
    total_background_io_bandwidth_used = 0.0
