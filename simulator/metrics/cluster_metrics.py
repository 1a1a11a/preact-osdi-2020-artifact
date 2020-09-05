from dataclasses import dataclass
from metrics.disk_category_metrics import DiskCategoryMetrics
from metrics.background_work import BackgroundWork
from metrics.work import Work


'''
These are cluster metrics that are used to understand state of cluster each day.
'''
@dataclass
class ClusterMetrics:
    total_disk_metrics: DiskCategoryMetrics
    trickle_pool: DiskCategoryMetrics
    retiring_work_by_date: dict  # date: (read, write))
    total_cluster_io_bandwidth: float = 0.0
    total_background_io_bandwidth_allowed: float = 0.0
    total_background_io_bandwidth_needed: float = 0.0
    total_background_io_bandwidth_used: float = 0.0
