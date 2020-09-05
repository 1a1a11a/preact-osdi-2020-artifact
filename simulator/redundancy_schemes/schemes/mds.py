#!/usr/local/bin/python3

from redundancy_schemes import FaultToleranceSchemes
import constants
import common
import math
import numpy as np
from rgroups.rgroup import RGroup
from scipy.special import comb


class MDS(FaultToleranceSchemes):
    def __init__(self):
        self._mttdl_target = self.calculate_mttdl(constants.DEFAULT_AFR,
                                                  common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)])
        FaultToleranceSchemes.__init__(self, self.__class__.__name__)

    def __del__(self):
        pass

    def calculate_mttdl(self, afr, rgroup):
        repair_time = constants.MAX_MTTR_ALLOWED
        mtbf = 8766 / (afr / 100)
        n_choose_k = comb(rgroup.data_chunks + rgroup.code_chunks, rgroup.data_chunks, exact=True)
        first_part = mtbf / (rgroup.data_chunks * n_choose_k)
        second_part = (mtbf / repair_time) ** rgroup.code_chunks
        return float(float(first_part) * float(second_part)) / (24 * 365)

    def get_best_scheme(self):
        r = RGroup(str((constants.MAX_STRIPE_DIMENSION +
                       constants.MIN_PARITIES_PER_STRIPE,
                       constants.MIN_PARITIES_PER_STRIPE)),
                   constants.MAX_STRIPE_DIMENSION,
                   constants.MIN_PARITIES_PER_STRIPE)
        r.tolerable_afr = 3.0

        for tolerable_afr in np.arange(0.1, constants.DEFAULT_AFR, 0.1):
            tolerable_mttdl = self.calculate_mttdl(tolerable_afr, r)
            if tolerable_mttdl < self._mttdl_target:
                r.tolerable_afr = tolerable_afr - 0.1
                while True:
                    s = self.get_stable_state_scheme(r.tolerable_afr, only_check=True)
                    if s.data_chunks != r.data_chunks or s.code_chunks != r.code_chunks:
                        r.tolerable_afr -= 0.1
                        continue
                    r.mttdl = self.calculate_mttdl(r.tolerable_afr, r)
                    assert(r.mttdl > self._mttdl_target)
                    break
                break
        return r

    def get_stable_state_scheme(self, afr, only_check=False, prev_rgroup=None):
        if afr < 0.1:
            max_stripe_dimension = constants.MAX_STRIPE_DIMENSION
        else:
            c2 = ((constants.DEFAULT_REDUNDANCY_SCHEME[0] - constants.DEFAULT_REDUNDANCY_SCHEME[1]) *
                  constants.DEFAULT_AFR) / afr
            max_stripe_dimension = min(math.floor(c2), constants.MAX_STRIPE_DIMENSION)
        storage_overhead_ratios = list()
        for k in range(constants.DEFAULT_REDUNDANCY_SCHEME[0] - constants.DEFAULT_REDUNDANCY_SCHEME[1],
                       max_stripe_dimension + 1):
            for p in range(constants.MIN_PARITIES_PER_STRIPE, math.floor(constants.MAX_STRIPE_DIMENSION * (
                    constants.DEFAULT_REDUNDANCY_SCHEME[0] / (
                    constants.DEFAULT_REDUNDANCY_SCHEME[0] - constants.DEFAULT_REDUNDANCY_SCHEME[1])) -
                                                                         constants.MAX_STRIPE_DIMENSION)):
                storage_overhead_ratios.append(((k, p), float(k + p) / k))

        storage_overhead_ratios = sorted(storage_overhead_ratios, key=lambda x: x[1])

        for scheme in storage_overhead_ratios:
            if float(scheme[0][0]) / (scheme[0][0] - scheme[0][1]) >= float(constants.DEFAULT_REDUNDANCY_SCHEME[0]) / (
                    constants.DEFAULT_REDUNDANCY_SCHEME[0] - constants.DEFAULT_REDUNDANCY_SCHEME[1]):
                return common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]
            r_tuple = scheme[0][0] + scheme[0][1], scheme[0][1]
            if str(r_tuple) in common.rgroups:
                r = common.rgroups[str(r_tuple)]
            else:
                r = RGroup(str(r_tuple), scheme[0][0], scheme[0][1])
                r.overhead = float(r.data_chunks + r.code_chunks) / r.data_chunks

            if prev_rgroup is not None and prev_rgroup.overhead > r.overhead and prev_rgroup.overhead / r.overhead < 1.02:
                return prev_rgroup

            rgroup_mttdl = self.calculate_mttdl(afr, r)
            if rgroup_mttdl >= self._mttdl_target:
                if r.name not in common.rgroups and only_check is False:
                    common.rgroups[r.name] = r
                    for tolerable_afr in np.arange(afr, constants.DEFAULT_AFR, 0.1):
                        tolerable_mttdl = self.calculate_mttdl(tolerable_afr, r)
                        if tolerable_mttdl < self._mttdl_target:
                            r.tolerable_afr = tolerable_afr - 0.1
                            r.mttdl = self.calculate_mttdl(r.tolerable_afr, r)
                            if only_check is False:
                                for rg_tup in common.rgroups_by_overhead:
                                    if rg_tup[0] < r.overhead:
                                        continue

                                    if rg_tup[0] / r.overhead <= 1.02:
                                        return rg_tup[1]

                                    # if r.overhead / rg_tup[0] >= 0.98:
                                    #     return r
                                common.rgroups_by_overhead.append((r.overhead, r))
                                common.rgroups_by_overhead.sort()
                            break
                return r

        return common.rgroups[str(constants.DEFAULT_REDUNDANCY_SCHEME)]
