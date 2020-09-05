from metrics.work import Work
from dataclasses import dataclass

'''
This is the dataclass that holds all types of background work performed.
'''
@dataclass
class BackgroundWork:
    scrubbing_needed: Work
    scrubbing_performed: Work
    reconstruction_needed: Work
    reconstruction_performed: Work
    urgent_reencoding_needed: Work
    urgent_reencoding_performed: Work
    non_urgent_reencoding_needed: Work
    non_urgent_reencoding_performed: Work
    schedulable_reencoding_needed: Work
    schedulable_reencoding_performed: Work
    decommissioning_needed: Work
    decommissioning_performed: Work
