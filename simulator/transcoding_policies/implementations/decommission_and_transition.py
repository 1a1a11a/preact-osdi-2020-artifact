#!/usr/local/bin/python3

from transcoding_policies import TranscodingPolicy
import constants
import logging


class Decommission(TranscodingPolicy):
    def __init__(self, start_date, end_date):
        logging.log(constants.LOG_LEVEL_CONFIG, "Initializing " + self.__class__.__name__ + " transcoding policy...")
        TranscodingPolicy.__init__(self, self.__class__.__name__, start_date, end_date)

    def _calculate_transcoding_cost(self, capacity, from_rg, to_rg, avg_disks_transitioned=0, rgroup_num_disks=0):
        read_cost = capacity * constants.CLUSTER_FULLNESS_PERCENTAGE
        write_cost = read_cost
        return read_cost, write_cost
