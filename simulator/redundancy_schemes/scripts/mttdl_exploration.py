#!/usr/local/bin/python3

import matplotlib.pyplot as plt
from decimal import Decimal


def calculate_mttdl(afr, stripe_length, failures):
    mu = 0.25
    # mu = 0.1
    mtbf = float(8766 / afr)
    denominator = 1
    for k in range(0, failures + 1):
        denominator *= (stripe_length - k)
    denominator *= (float(1 / mtbf) ** (failures + 1))
    numerator = (float(1 / mu) ** failures)
    return float(numerator / denominator) / (24 * 365)

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
# print('%.2E' % Decimal(calculate_mttdl(1.15, 30, 3)))  # S-8C
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
# print('%.2E' % Decimal(calculate_mttdl(4.15, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.93, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.48, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.79, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.93, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.12, 3, 2)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(4.15, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.93, 30, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.48, 30, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.79, 30, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.93, 30, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.12, 30, 3)))

# print('%.2E' % Decimal(calculate_mttdl(3.1, 3, 2))) #########################
# print('%.2E' % Decimal(calculate_mttdl(1.61, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.37, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.88, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(2.08, 3, 2)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.1, 3, 2)))
# print('%.2E' % Decimal(calculate_mttdl(1.61, 30, 3)))  # 62%
# print('%.2E' % Decimal(calculate_mttdl(1.37, 30, 3)))  # 62%
# print('%.2E' % Decimal(calculate_mttdl(1.76, 29, 3)))  # 62%
# print('%.2E' % Decimal(calculate_mttdl(1.88, 28, 3)))  # 62%
# print('%.2E' % Decimal(calculate_mttdl(2.08, 25, 3)))  # 62%


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
# print('%.2E' % Decimal(calculate_mttdl(1.15, 26, 3)))
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

# ## FOR 9, 3 in the graphs present in paper right now ###########
# print('%.2E' % Decimal(calculate_mttdl(3.1, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.61, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.37, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.88, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(2.08, 9, 3)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.1, 9, 3)))
# print('%.2E' % Decimal(calculate_mttdl(1.61, 30, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.37, 30, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 30, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.88, 30, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.08, 30, 4)))

#### FOR 10, 4 min afr
# print('%.2E' % Decimal(calculate_mttdl(3.82, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.77, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(3.82, 27, 6)))
# print('%.2E' % Decimal(calculate_mttdl(2.34, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.15, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.32, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.8, 14, 4)))
print('%.2E' % Decimal(calculate_mttdl(3.82, 14, 4)))
print('%.2E' % Decimal(calculate_mttdl(3.82, 27, 6)))
print('%.2E' % Decimal(calculate_mttdl(2.34, 14, 4)))
print('%.2E' % Decimal(calculate_mttdl(1.15, 14, 4)))
print('%.2E' % Decimal(calculate_mttdl(1.32, 14, 4)))
print('%.2E' % Decimal(calculate_mttdl(1.8, 14, 4)))
print("alternates")
print('%.2E' % Decimal(calculate_mttdl(3.82, 14, 4)))
print('%.2E' % Decimal(calculate_mttdl(1.77, 27, 4)))
print('%.2E' % Decimal(calculate_mttdl(2.34, 21, 4)))
print('%.2E' % Decimal(calculate_mttdl(1.15, 30, 4)))
print('%.2E' % Decimal(calculate_mttdl(1.32, 36, 4)))
print('%.2E' % Decimal(calculate_mttdl(1.8, 27, 4)))

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

### FOR 10, 4 for graphs present in paper right now ############
# print('%.2E' % Decimal(calculate_mttdl(3.1, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.61, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.37, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.76, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.88, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(2.08, 14, 4)))
# print("alternates")
# print('%.2E' % Decimal(calculate_mttdl(3.1, 14, 4)))
# print('%.2E' % Decimal(calculate_mttdl(1.61, 24, 4)))  # 14%
# print('%.2E' % Decimal(calculate_mttdl(1.37, 29, 4)))  # 17%
# print('%.2E' % Decimal(calculate_mttdl(1.76, 30, 5)))  # 14%
# print('%.2E' % Decimal(calculate_mttdl(1.88, 30, 5)))  # 14%
# print('%.2E' % Decimal(calculate_mttdl(2.08, 30, 5)))  # 14%


# Seagate 4TB B --- 3.96
# HGST 4TB A --- 2.83
# HGST 4TB B --- 1.46
# Seagate 8TB Com --- 1.76
# Seagate 8TB Ent --- 1.75
# Seagate 12TB Ent --- 1.65

# ----------------------------------------------------------------------------------
# DG    |  3-rep                  |  (9, 6)                 |  (10, 4)
# S-4   |  0%           2.87E+06  |  0%           4.81E+07  |  0%           5.12E+09
# H-4A  |  61% (30, 26) 4.10E+08  |  23% (30, 26) 4.10E+08  |  14% (30, 25) 1.96E+11
# H-4B  |  62% (30, 27) 1.37E+07  |  23% (30, 26) 1.25E+10  |  17% (30, 26) 1.25E+10
# S-8C  |  62% (30, 27) 6.39E+06  |  23% (30, 26) 4.81E+09  |  17% (29, 25) 5.78E+09
# S-8E  |  62% (30, 27) 4.73E+06  |  23% (30, 26) 3.30E+09  |  16% (27, 23) 5.83E+09
# S-12E |  62% (30, 27) 3.25E+06  |  23% (30, 26) 2.07E+09  |  14% (25, 21) 5.54E+09
# ----------------------------------------------------------------------------------