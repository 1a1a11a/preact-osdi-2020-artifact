from dataclasses import dataclass
from metrics.disk_category_metrics import DiskCategoryMetrics


'''
This is the dataclass that maintains the Rgroup metrics.
'''
@dataclass
class RgroupMetrics:
    disk_metrics: DiskCategoryMetrics
    emptying_in_progress: False
    capacity_moved_out_per_day: dict  # date: capacity_removed
    disk_batch_transitioning_slowly: dict
    io_bandwidth: float = 0
    background_io_bandwidth: float = 0
    potential_capacity_after_redundancy_management: int = 0
    potential_transcoding_capacity_needed: int = 0
