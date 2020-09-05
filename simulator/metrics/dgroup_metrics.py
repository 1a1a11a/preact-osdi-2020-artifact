from dataclasses import dataclass
from metrics.disk_category_metrics import DiskCategoryMetrics


'''
This is the dataclass that maintains the Dgroup metrics.
'''
@dataclass
class DgroupMetrics:
    disk_metrics: DiskCategoryMetrics
    canary_disk_metrics: DiskCategoryMetrics
    step_metrics: dict  # date: DiskCategoryMetrics
    step_list: list  # list of steps (expect < 10)
    disk_step_mapping: dict  # serial_number: date_of_step
    disks_at_risk: dict
    canary_disks: dict
    capacity_moved_out_per_day: dict  # date: dict(rgroup: capacity moved)
    dates_of_work: dict  # serial_number: date_list_of_work
    last_canary_birthday: str
    io_bandwidth: float = 0
    background_io_bandwidth: float = 0
