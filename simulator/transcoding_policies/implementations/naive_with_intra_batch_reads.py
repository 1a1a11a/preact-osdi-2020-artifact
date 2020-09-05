#!/usr/local/bin/python3

from transcoding_policies import TranscodingPolicy
import constants
import logging


class NaiveWithIntraBatchReads(TranscodingPolicy):
    def __init__(self, start_date, end_date, canary, iterative_cp):
        logging.log(constants.LOG_LEVEL_CONFIG, "Initializing " + self.__class__.__name__ + " transcoding policy...")
        TranscodingPolicy.__init__(self, self.__class__.__name__, start_date, end_date)

    def _calculate_transcoding_cost(self, capacity, from_rg, to_rg, avg_disks_transitioned=0, rgroup_num_disks=0):
        if avg_disks_transitioned == 0 or rgroup_num_disks == 0:
            print(avg_disks_transitioned, rgroup_num_disks)
            print(from_rg.name)
            print(to_rg.name)
            exit(0)
        data_from_transitioning_disks = capacity * (1.0 / from_rg.overhead) * (
                (float(avg_disks_transitioned) / rgroup_num_disks) * from_rg.data_chunks) / avg_disks_transitioned
        data_from_outside_disks = capacity * (1.0 / from_rg.overhead) * (
                1 - (float(avg_disks_transitioned) / rgroup_num_disks)) * from_rg.data_chunks
        read_cost = data_from_transitioning_disks + data_from_outside_disks
        write_cost = (data_from_outside_disks * to_rg.overhead) + data_from_transitioning_disks * (1.0 / to_rg.overhead)
        return read_cost, write_cost
