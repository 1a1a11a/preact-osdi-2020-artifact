#!/usr/local/bin/python3

from anomaly_detectors import Checker
import constants
import rrcf
import pandas as pd


class RRCF(Checker):
    def __init__(self, disk_group):
        self._disk_group = disk_group
        self._rrcf_properties = dict()
        self._num_trees = 256
        self._tree_size = 29  # also known as subSampleSize on the Amazon Kinesis RRCF documentation page.
        self._time_decay = 30
        self._shingle_size = 1
        self._forest = []
        for _ in range(0, self._num_trees):
            tree = rrcf.RCTree()
            self._forest.append(tree)
        self._index = 0
        self._avg_codisp = {}
        self.data_vs_anomalies = []

        self._iloc_num = 0
        self._anomaly_df = pd.DataFrame(columns=['days', 'cum_afr', 'anomaly'])
        Checker.__init__(self, "Local robust random cut forest")

    def __del__(self):
        self._anomaly_df.to_csv("results/2020-01-06/data/anomaly_scores.csv")

    def get_anomaly_score(self, days, data, key):
        print("Processing day " + str(days))
        self._index = days
        for tree in self._forest:
            # If tree is above permitted size, drop the oldest point (FIFO)
            if len(tree.leaves) > self._tree_size:
                tree.forget_point(self._index - self._tree_size)

            # Insert the new point into the tree
            tree.insert_point(float(data), index=self._index)

            # Compute codisp on the new point and take the average among all trees
            if not self._index in self._avg_codisp:
                self._avg_codisp[self._index] = 0
            self._avg_codisp[self._index] += tree.codisp(self._index) / self._num_trees

        self._anomaly_df.loc[self._iloc_num] = [days, data, float(self._avg_codisp[self._index])]
        self._iloc_num += 1
        if self._avg_codisp[self._index] > constants.ANOMALY_SCORE_SENSITIVITY:
            self.data_vs_anomalies.append((int(self._index), float(self._avg_codisp[self._index])))

        return self.data_vs_anomalies
