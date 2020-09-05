from dataclasses import dataclass


'''
This is the dataclass (struct) for holding all kinds of work: 
Reconstruction, Scrubbing, Urgent Reencoding, Schedulable Reencoding, Decommissioning
'''
@dataclass
class Work:
    reads: int = 0
    writes: int = 0
    io: int = 0

