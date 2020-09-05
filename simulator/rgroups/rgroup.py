#!/usr/local/bin/python3


class RGroup:
    def __init__(self, name, data_chunks, code_chunks):
        self.name = name
        self.data_chunks = data_chunks
        self.code_chunks = code_chunks
        self.mttdl = 0
        self.tolerable_afr = 0.0
        self.overhead = 0.0
        self.disks = dict()
        self.disks_crossing_second_level_afr = dict()

    def __lt__(self, other):
        return self.code_chunks < other.code_chunks
