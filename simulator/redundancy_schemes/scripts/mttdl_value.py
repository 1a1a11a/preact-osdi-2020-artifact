#!/usr/local/bin/python3

import matplotlib.pyplot as plt
from decimal import Decimal
from scipy.special import comb


def calculate_mttdl(afr, stripe_length, failures):
    mu = 0.25
    # mu = 0.5
    # mu = 0.1
    # mu = float(1/(3600/(16/250)))
    mtbf = 8766 / (afr / 100)
    denominator = 1
    for k in range(0, failures + 1):
        denominator *= (stripe_length - k)
    denominator *= (float(1.0 / mtbf) ** (failures + 1))
    numerator = (float(1.0 / mu) ** failures)
    return float(numerator / denominator) / (24 * 365)


def calculate_mttdl_cleversafe(afr, stripe_length, failures):
    # repair_time = 0.25
    # repair_time = 1.5
    repair_time = 1
    mtbf = 8766 / (afr / 100)
    data_chunks = int(stripe_length - failures)
    n_choose_k = comb(stripe_length, data_chunks, exact=True)
    first_part = mtbf / (data_chunks * n_choose_k)
    second_part = (mtbf / repair_time) ** (failures)
    return float(float(first_part) * float(second_part)) / (24 * 365)

# print('%.2E' % Decimal(calculate_mttdl(3.59, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.23, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.06, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.06, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.12, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.58, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(0.39, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.5, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.5, 14, 4)))

#### FOR 3-replication min afr
# print('%.2E' % Decimal(calculate_mttdl(3.82, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.77, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.34, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.8, 3, 2)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.82, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.77, 5, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.34, 4, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 7, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 6, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.8, 6, 2)))

#### FOR 3-replication in the graphs present in paper right now
# print('%.2E' % Decimal(calculate_mttdl(3.96, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.83, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.46, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.75, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.65, 3, 2)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.96, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.83, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.46, 5, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 5, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.75, 5, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.65, 5, 2)))

#### FOR 3-replication in the graphs present in paper right now
# print('%.2E' % Decimal(calculate_mttdl(3.1, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.61, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.37, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.88, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.08, 3, 2)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.1, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.61, 4, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.37, 5, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 4, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.88, 4, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.08, 3, 2)))

#### FOR 3-replication in the graphs present in paper right now
# print('%.2E' % Decimal(calculate_mttdl(3, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(0.94, 3, 2)))  # 2.47E+08
# print('%.2E' % Decimal(calculate_mttdl(2.18, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.17, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.38, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.74, 3, 2)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(0.94, 6, 2)))  # H-4A (best)
# print('%.2E' % Decimal(calculate_mttdl(2.18, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.17, 5, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.38, 5, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.74, 4, 2)))


#### FOR 9, 3 min afr
# print('%.2E' % Decimal(calculate_mttdl(3.82, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.77, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.34, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.8, 9, 3)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.82, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.77, 17, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.34, 13, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 26, 3)))  # S-8C
# print('%.2E' % Decimal(calculate_mttdl(1.32, 22, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.8, 17, 3)))

#### FOR 9, 3 in the graphs present in paper right now
# print('%.2E' % Decimal(calculate_mttdl(3.96, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.83, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.46, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.75, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.65, 9, 3)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.96, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.83, 11, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.46, 21, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 18, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.75, 18, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.65, 19, 3)))

#### FOR 9, 3 in the graphs present in paper right now
# print('%.2E' % Decimal(calculate_mttdl(3, 9, 3)))  # 1.76E+08
# print('%.2E' % Decimal(calculate_mttdl(0.94, 9, 3)))  # 1.83E+10
# print('%.2E' % Decimal(calculate_mttdl(2.18, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.17, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.38, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.74, 9, 3)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(0.94, 25, 3)))  # H-4A (best)
# print('%.2E' % Decimal(calculate_mttdl(2.18, 11, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.17, 20, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.38, 17, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.74, 14, 3)))

#### FOR 10, 4 min afr
# print('%.2E' % Decimal(calculate_mttdl(3.82, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.77, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.34, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.8, 14, 4)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.82, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.77, 27, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.34, 21, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 41, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 36, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.8, 27, 4)))

#### FOR 10, 4 for graphs present in paper right now
# print('%.2E' % Decimal(calculate_mttdl(3.96, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.83, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.46, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.75, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.65, 14, 4)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.96, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.83, 18, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.46, 34, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 28, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.75, 29, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.65, 30, 4)))

### FOR 10, 4 for graphs present in paper right now
# print('%.2E' % Decimal(calculate_mttdl(3.1, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.61, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.37, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.88, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.08, 14, 4)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.1, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.61, 24, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.37, 29, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 23, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.88, 21, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.08, 19, 4)))

## FOR 10, 4 for graphs present in paper right now
# print('%.2E' % Decimal(calculate_mttdl(3, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(0.94, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.18, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.17, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.38, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.74, 14, 4)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.1, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.61, 24, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.37, 29, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 23, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.88, 21, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.08, 19, 4)))

#######################################################
# print("front of graph")
# print('%.2E' % Decimal(calculate_mttdl(3.29, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(0.92, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.19, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.62, 3, 2)))
# print("default")
# print('%.2E' % Decimal(calculate_mttdl(3.29, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(0.92, 6, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.19, 6, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.62, 3, 2)))

# print("front of graph")
# print('%.2E' % Decimal(calculate_mttdl(3.29, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(0.92, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.19, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.62, 9, 3)))
# print("default")
# print('%.2E' % Decimal(calculate_mttdl(3.29, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(0.92, 18, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.19, 18, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.62, 9, 3)))

# print("front of graph")
# print('%.2E' % Decimal(calculate_mttdl(3.29, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(0.92, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.19, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.62, 14, 4)))
# print("default")
# print('%.2E' % Decimal(calculate_mttdl(3.29, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(0.92, 28, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.19, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.62, 14, 4)))

# print("front of graph")
# print('%.2E' % Decimal(calculate_mttdl(3.29, 20, 3)))
# print('%.2E' % Decimal(calculate_mttdl(0.92, 20, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.19, 20, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 20, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 20, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.62, 20, 3)))
# print("default")
# print('%.2E' % Decimal(calculate_mttdl(3.29, 20, 3)))
# print('%.2E' % Decimal(calculate_mttdl(0.92, 40, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.19, 40, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 40, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 40, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.62, 40, 3)))

## MONTHLY SLIDING WINDOW CODES (3, 1)
# print('%.2E' % Decimal(calculate_mttdl(4.01, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 3, 2)))
# print("alternates upto 2X")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 5, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 4, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 4, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 4, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 4, 2)))
# print("Doubling")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 6, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 6, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 6, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 6, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 6, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 6, 3)))
# print("alternates upto 4X")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 12, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 12, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 12, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 12, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 12, 3)))


## MONTHLY SLIDING WINDOW CODES (9, 6)
# print('%.2E' % Decimal(calculate_mttdl(4.01, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 9, 3)))
# print("alternates upto 2X")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 17, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 16, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 15, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 13, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 13, 3)))
# print("alternates upto 4X")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 36, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 36, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 36, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 36, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 36, 4)))
# print("Code thinning 26 nov default")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(4.01, 18, 4)))
# print('%.2E' % Decimal(calculate_mttdl(4.01, 17, 4)))
# print('%.2E' % Decimal(calculate_mttdl(4.01, 16, 4)))
# print('%.2E' % Decimal(calculate_mttdl(4.01, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(4.01, 14, 4)))
# print("just doubling the code")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 18, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 18, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 18, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 18, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 18, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 18, 4)))
# print("seeing what difference is needed")
# print('%.2E' % Decimal(calculate_mttdl(5, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 18, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 18, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 18, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 16, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 16, 3)))


# ## MONTHLY SLIDING WINDOW CODES (14, 10)
# # print('%.2E' % Decimal(calculate_mttdl(10, 14, 4)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(4.01, 14, 4)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 14, 4)))  # print('%.2E' % Decimal(calculate_mttdl(1.99, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 14, 4)))  # print('%.2E' % Decimal(calculate_mttdl(2.38, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 14, 4)))  # print('%.2E' % Decimal(calculate_mttdl(2.35, 14, 4)))
# print("alternates upto 2X")
# print('%.2E' % Decimal(calculate_mttdl(10, 14, 4)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(4.01, 28, 4)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 28, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 25, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 25, 4)))  # print('%.2E' % Decimal(calculate_mttdl(1.99, 25, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 28, 5)))  # print('%.2E' % Decimal(calculate_mttdl(2.38, 30, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 28, 5)))
# print("Doubling benefits")
# # print('%.2E' % Decimal(calculate_mttdl(10, 28, 5)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(4.01, 28, 5)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 28, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 28, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 28, 5)))  # print('%.2E' % Decimal(calculate_mttdl(1.99, 25, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 28, 5)))  # print('%.2E' % Decimal(calculate_mttdl(2.38, 30, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 28, 5)))
# print("Doubling benefits MTTDL")
# # print('%.2E' % Decimal(calculate_mttdl(10, 28, 5)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(4.01, 28, 5)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 28, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 14, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 28, 5)))  # print('%.2E' % Decimal(calculate_mttdl(1.99, 25, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 28, 5)))  # print('%.2E' % Decimal(calculate_mttdl(2.38, 30, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 28, 5)))

# print('%.2E' % Decimal(calculate_mttdl(10, 9, 3)))


# print("alternates upto 4X")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 14, 4)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 56, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 56, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 56, 5)))  # print('%.2E' % Decimal(calculate_mttdl(1.99, 56, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 56, 5)))  # print('%.2E' % Decimal(calculate_mttdl(2.38, 56, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 56, 5)))  # print('%.2E' % Decimal(calculate_mttdl(2.35, 56, 5)))

# # ## MONTHLY SLIDING WINDOW CODES (20, 17)
# print('%.2E' % Decimal(calculate_mttdl(4.01, 20, 3)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 20, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 20, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 20, 3)))  # print('%.2E' % Decimal(calculate_mttdl(1.99, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 20, 3)))  # print('%.2E' % Decimal(calculate_mttdl(2.38, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 20, 3)))  # print('%.2E' % Decimal(calculate_mttdl(2.35, 14, 4)))
# print("alternates upto 2X")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 20, 3)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 40, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 37, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 37, 3)))  # print('%.2E' % Decimal(calculate_mttdl(1.99, 25, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 31, 3)))  # print('%.2E' % Decimal(calculate_mttdl(2.38, 30, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 31, 3)))
# print("alternates upto 4X")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 20, 3)))  # print('%.2E' % Decimal(calculate_mttdl(3.85, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 60, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 60, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 60, 4)))  # print('%.2E' % Decimal(calculate_mttdl(1.99, 56, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 60, 4)))  # print('%.2E' % Decimal(calculate_mttdl(2.38, 56, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 60, 4)))

#######################################################

# print("3-rep Jan 6, 2019")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 5, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 4, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 4, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 4, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 4, 2)))
#
# print("6-of-9 Jan 6, 2019")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 17, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 16, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 15, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 18, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 18, 4)))
#
# print("10-of-14 Jan 6, 2019")
# print('%.2E' % Decimal(calculate_mttdl(4.01, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.82, 28, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.04, 25, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.07, 25, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.48, 28, 5)))
# print('%.2E' % Decimal(calculate_mttdl(2.44, 28, 5)))

# ---------------------------------------------------------------------------
# print('\n1-of-3 optimization')
# up to 2X -- IBM
# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 3, 2)))
# print('AFR 4.01% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 6, 3)))
# print('AFR 1.82% 3-of-5 = ' + '%.2E' % Decimal(calculate_mttdl(1.82, 5, 2)))
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl(2.04, 4, 2)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl(2.07, 4, 2)))
# print('AFR 2.48% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl(2.48, 4, 2)))
# print('AFR 2.44% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl(2.44, 4, 2)))

# up to 2X -- CLEVERSAFE
# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 3, 2)))
# print('AFR 4.01% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 6, 3)))
# print('AFR 1.82% 3-of-5 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 5, 2)))
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 4, 2)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 4, 2)))
# print('AFR 2.48% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 4, 2)))
# print('AFR 2.44% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 4, 2)))

# up to 4X
# print('AFR 4.01% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 12, 3)))
# print('AFR 1.82% 3-of-5 = ' + '%.2E' % Decimal(calculate_mttdl(1.82, 12, 3)))
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl(2.04, 12, 3)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl(2.07, 12, 3)))
# print('AFR 2.48% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl(2.48, 12, 3)))
# print('AFR 2.44% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl(2.44, 12, 3)))

# print('\n6-of-9 optimization')
# up to 2X -- IBM
# print('AFR 4.01% 6-of-9 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 9, 3)))
# print('AFR 4.01% 14-of-18 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 18, 4))) # 20, 3
# print('AFR 1.82% 14-of-17 = ' + '%.2E' % Decimal(calculate_mttdl(1.82, 17, 3))) # 42, 3
# print('AFR 2.04% 13-of-16 = ' + '%.2E' % Decimal(calculate_mttdl(2.04, 16, 3))) # 37, 3
# print('AFR 2.07% 12-of-15 = ' + '%.2E' % Decimal(calculate_mttdl(2.07, 15, 3))) # 37, 3
# print('AFR 2.48% 14-of-18 = ' + '%.2E' % Decimal(calculate_mttdl(2.48, 18, 4))) # 31, 3
# print('AFR 2.44% 14-of-18 = ' + '%.2E' % Decimal(calculate_mttdl(2.44, 18, 4))) # 31, 3

# up to 2X -- CLEVERSAFE
# print('AFR 4.01% 6-of-9 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 9, 3)))
# print('AFR 4.01% 14-of-18 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 18, 4)))
# print('AFR 1.82% 14-of-17 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 17, 3)))
# print('AFR 2.04% 13-of-16 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 16, 3)))
# print('AFR 2.07% 12-of-15 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 15, 3)))
# print('AFR 2.48% 14-of-18 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 18, 4)))
# print('AFR 2.44% 14-of-18 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 18, 4)))

# up to 4X
# print('AFR 4.01% 6-of-9 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 9, 3)))
# print('AFR 4.01% 14-of-18 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 36, 4))) # 20, 3
# print('AFR 1.82% 14-of-17 = ' + '%.2E' % Decimal(calculate_mttdl(1.82, 36, 4))) # 42, 3
# print('AFR 2.04% 13-of-16 = ' + '%.2E' % Decimal(calculate_mttdl(2.04, 36, 4))) # 37, 3
# print('AFR 2.07% 12-of-15 = ' + '%.2E' % Decimal(calculate_mttdl(2.07, 36, 4))) # 37, 3
# print('AFR 2.48% 14-of-18 = ' + '%.2E' % Decimal(calculate_mttdl(2.48, 36, 4))) # 31, 3
# print('AFR 2.44% 14-of-18 = ' + '%.2E' % Decimal(calculate_mttdl(2.44, 36, 4))) # 31, 3
#
# print('\n10-of-14 optimization')
# up to 2X -- IBM
# print('AFR 4.01% 10-of-14 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 14, 4)))
# print('AFR 4.01% 23-of-25 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 28, 5))) # 31, 4
# print('AFR 1.82% 24-of-28 = ' + '%.2E' % Decimal(calculate_mttdl(1.82, 28, 4))) # 67, 4
# print('AFR 2.04% 21-of-25 = ' + '%.2E' % Decimal(calculate_mttdl(2.04, 25, 4))) # 60, 4
# print('AFR 2.07% 21-of-25 = ' + '%.2E' % Decimal(calculate_mttdl(2.07, 25, 4))) # 59, 4
# print('AFR 2.48% 23-of-28 = ' + '%.2E' % Decimal(calculate_mttdl(2.48, 28, 5))) # 50, 4
# print('AFR 2.44% 23-of-28 = ' + '%.2E' % Decimal(calculate_mttdl(2.44, 28, 5))) # 50, 4

# up to 2X -- CLEVERSAFE
# print('AFR 4.01% 10-of-14 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 14, 4)))
# print('AFR 4.01% 23-of-25 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 28, 5)))
# print('AFR 1.82% 24-of-28 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 28, 4)))
# print('AFR 2.04% 21-of-25 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 25, 4)))
# print('AFR 2.07% 21-of-25 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 25, 4)))
# print('AFR 2.48% 23-of-28 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 28, 5)))
# print('AFR 2.44% 23-of-28 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 28, 5)))

# up to 4X
# print('AFR 4.01% 10-of-14 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 14, 4)))
# print('AFR 4.01% 23-of-25 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 56, 5))) # 31, 4
# print('AFR 1.82% 24-of-28 = ' + '%.2E' % Decimal(calculate_mttdl(1.82, 56, 5))) # 67, 4
# print('AFR 2.04% 21-of-25 = ' + '%.2E' % Decimal(calculate_mttdl(2.04, 56, 5))) # 60, 4
# print('AFR 2.07% 21-of-25 = ' + '%.2E' % Decimal(calculate_mttdl(2.07, 56, 5))) # 59, 4
# print('AFR 2.48% 23-of-28 = ' + '%.2E' % Decimal(calculate_mttdl(2.48, 56, 5))) # 50, 4
# print('AFR 2.44% 23-of-28 = ' + '%.2E' % Decimal(calculate_mttdl(2.44, 56, 5))) # 50, 4
# ---------------------------------------------------------------------------


# --------------------- 2 times K, not N -------------------------------
# up to 2X -- CLEVERSAFE
# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 3, 2)))
# # print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 5, 3)))
# print('AFR 1.82% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 3, 2)))
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 3, 2)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 3, 2)))
# print('AFR 2.48% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 3, 2)))
# print('AFR 2.44% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 3, 2)))

# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 9, 3)))
# # print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 16, 4)))
# print('AFR 1.82% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 9, 3)))
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 9, 3)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 9, 3)))
# print('AFR 2.48% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 9, 3)))
# print('AFR 2.44% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 9, 3)))

# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01`44, 14, 4)))

# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 30, 5)))
# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 25, 5)))
# print('AFR 1.82% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 55, 5)))
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 55, 5)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 55, 5)))
# print('AFR 2.48% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 21, 4)))
# print('AFR 2.44% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 21, 4)))

# ----------------------------------------------------------------------


# up to 4X -- CLEVERSAFE
# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 3, 2)))
# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 3, 2)))
# print('AFR 1.82% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 5, 2)))
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 4, 2)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 4, 2)))
# print('AFR 2.48% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 4, 2)))
# print('AFR 2.44% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 4, 2)))

# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 9, 3)))
# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 28, 4)))
# print('AFR 1.82% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 28, 4)))
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 28, 4)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 28, 4)))
# print('AFR 2.48% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 28, 4)))
# print('AFR 2.44% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 28, 4)))
#
# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 14, 4)))
# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 45, 5)))
# print('AFR 1.82% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 45, 5)))
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 45, 5)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 45, 5)))
# print('AFR 2.48% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 45, 5)))
# print('AFR 2.44% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 45, 5)))

# ----------------------------------------------------------------------


# up to 2X -- CLEVERSAFE
# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 24, 3)))
# # print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 3, 2)))
# print('AFR 1.82% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 45, 3))) # 6.25%
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 45, 3)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 45, 3)))
# print('AFR 2.48% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 37, 3))) # >4%
# print('AFR 2.44% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 37, 3)))

# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 14, 2)))
# # print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 3, 2)))
# print('AFR 1.82% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 26, 2))) # 7.14%
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 26, 2)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 26, 2)))
# print('AFR 2.48% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 22, 2))) # 6.5%
# print('AFR 2.44% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 22, 2)))

# print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 8, 1)))
# # print('AFR 4.01% 1-of-3 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 3, 2)))
# print('AFR 1.82% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 15, 1))) # 6.25%
# print('AFR 2.04% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.04, 15, 1)))
# print('AFR 2.07% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.07, 15, 1)))
# print('AFR 2.48% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.48, 12, 1))) # 4.5%
# print('AFR 2.44% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(2.44, 12, 1)))

# ----------------------------------------------------------------------

# print('AFR 2.48% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(3.29, 3, 2)))
# print('AFR 2.44% 2-of-4 = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(0.92, 4, 2)))

# print('AFR 4.01% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 4, 2)))
# print('AFR 4.01% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 5, 2)))
# print('AFR 4.01% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 6, 2)))
# print('AFR 4.01% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl(10, 9, 3)))
# print('AFR 4.01% 3-of-6 = ' + '%.2E' % Decimal(calculate_mttdl(4.01, 7, 1)))

# -------------------- AFTER FINDING THE SLIDING WINDOW BUG -----------------------
# print("------------------------------- 1 of 3 ---------------------------------")
# print('AFR S-4 4.02% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.02, 3, 2)))
# print('AFR H-4A 0.61% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 4, 2)))
# print('AFR H-4B 1.3% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.3, 4, 2)))
# print('AFR S-8C 1.93% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.93, 4, 2)))
# print('AFR S-8E 1.82% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 4, 2)))
# print('AFR S-12E 1.89% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.89, 4, 2)))
# print("------------------------------- 6 of 9 ---------------------------------")
# print('AFR S-4 4.02% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.02, 9, 3)))
# print('AFR H-4A 0.61% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 15, 3)))
# print('AFR H-4B 1.3% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.3, 15, 3)))
# print('AFR S-8C 1.93% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.93, 15, 3)))
# print('AFR S-8E 1.82% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 15, 3)))
# print('AFR S-12E 1.89% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.89, 15, 3)))
# print("------------------------------- 10 of 14 ---------------------------------")
# print('AFR S-4 4.02% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.02, 14, 4)))
# print('AFR H-4A 0.61% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 24, 4)))
# print('AFR H-4B 1.3% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.3, 24, 4)))
# print('AFR S-8C 1.93% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.93, 24, 4)))
# print('AFR S-8E 1.82% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 24, 4)))
# print('AFR S-12E 1.89% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.89, 24, 4)))
# print("-------------------")
# print('AFR S-4 4.02% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.02, 9, 3)))
# print('AFR S-4 4.02% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.02, 14, 3)))
# print("============================================================================")
# print('AFR DG1 5% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(7.1, 9, 3)))
# print('AFR DG2 3% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(5, 12, 3)))
# print('AFR DG3 1% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(3, 15, 3)))

# ---------------------- AFTER realizing default AFR = 16% ---------------------------
print("------------------------------- 6 of 9 ---------------------------------")
print('DEFAULT REDUNDANCY MTTDL (16% AFR) = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.01, 9, 3)))
# print('AFR S-4 4% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4, 33, 3)))
# print('AFR H-4A 0.61% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 15, 3)))
# print('AFR H-4B 1.3% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.3, 15, 3)))
# print('AFR S-8C 1.93% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.93, 15, 3)))
# print('AFR S-8E 1.82% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 15, 3)))
# print('AFR S-12E 1.89% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.89, 15, 3)))
# print("------------------------------- 10 of 14 ---------------------------------")
# print('AFR S-4 4.02% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.02, 14, 4)))
# print('AFR H-4A 0.61% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 24, 4)))
# print('AFR H-4B 1.3% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.3, 24, 4)))
# print('AFR S-8C 1.93% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.93, 24, 4)))
# print('AFR S-8E 1.82% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.82, 24, 4)))
# print('AFR S-12E 1.89% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(1.89, 24, 4)))
# print("-------------------")
# print('AFR S-4 4.02% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.02, 9, 3)))
# print('AFR S-4 4.02% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(4.02, 14, 3)))
# print("============================================================================")
# print('AFR DG1 5% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(7.1, 9, 3)))
# print('AFR DG2 3% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(5, 12, 3)))
# print('AFR DG3 1% = ' + '%.2E' % Decimal(calculate_mttdl_cleversafe(3, 15, 3)))
# Seagate 4TB B --- 3.96
# HGST 4TB A --- 2.83
# HGST 4TB B --- 1.46
# Seagate 8TB Com --- 1.76
# Seagate 8TB Ent --- 1.75
# Seagate 12TB Ent --- 1.65
