#!/usr/local/bin/python3

from transcoding_policies import TranscodingPolicy
import constants
import logging


class Naive(TranscodingPolicy):
    def __init__(self, start_date, end_date):
        logging.log(constants.LOG_LEVEL_CONFIG, "Initializing " + self.__class__.__name__ + " transcoding policy...")
        TranscodingPolicy.__init__(self, self.__class__.__name__, start_date, end_date)

    def _calculate_transcoding_cost(self, capacity, from_rg, to_rg, avg_disks_transitioned=0, rgroup_num_disks=0):
        read_cost = capacity * (1.0 / from_rg.overhead) * from_rg.data_chunks
        write_cost = read_cost * to_rg.overhead
        return read_cost, write_cost
