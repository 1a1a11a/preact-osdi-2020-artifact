#!/usr/local/bin/python3

import sys
import constants
import common
import datetime
from datetime import timedelta, date
import os.path
import pandas as pd
import matplotlib.pyplot as plt
import json
from ast import literal_eval
import matplotlib
sys.path.append("dgroups")
import logging
from dgroups import DGroup
import numpy as np
from numpy import genfromtxt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
sys.path.append("datasets")
sys.path.append("dgroups")
from dgroups import DGroup
from datasets import Backblaze


# S-12E 46days
# G-1 (nj) 15 days
# G-3 (nj) 8 days

def monitor_canaries(dgroups, dataset):
    for dg_name in dgroups.keys():
        dg_name_str = ', '.join("'{0}'".format(dg) for dg in list([dg_name]))
        all_disks_deployment_dates = dataset.get_all_deployment_dates(dgroups=dg_name_str)
        startdate = all_disks_deployment_dates[0]
        enddate = constants.END_DATE
        age_array = np.zeros(common.days_between(startdate, enddate) + 1)
        dt_range = common.daterange(datetime.datetime.strptime(startdate, "%Y-%m-%d"),
                                    datetime.datetime.strptime(enddate, "%Y-%m-%d"))
        afr_array = np.zeros(common.days_between(startdate, enddate) + 1)
        disk_days_array = np.zeros(common.days_between(startdate, enddate) + 1)

        confident_afr_array = np.zeros(common.days_between(startdate, enddate) + 1)

        df_map = dict()
        current_date = 0
        day_wise_dt_range = list()

        result_date = datetime.datetime.today().strftime('%Y-%m-%d')
        os.makedirs("results/" + result_date, exist_ok=True)
        os.makedirs("results/" + result_date + "/canary/" + common.cluster, exist_ok=True)

        days_to_subtract = 46

        for dt in dt_range:
            today = dt.strftime("%Y-%m-%d")
            logging.info("Processing date %s...", today)
            # df_map[today] = np.genfromtxt("datasets/google/data/sep_3/" + common.cluster + "/simulated_date_data/" +
            #                               common.disk_shortname_map[dg_name] + "/" +
            #                               today + ".csv", delimiter=',', skip_header=1, usecols=(0, 4, 5, 6, 7),
            #                               names=["age", "disk_days", "failures", "disk_days_window", "failures_window"])

            df_map[today] = np.genfromtxt("datasets/backblaze/data/simulated_date_data/" +
                                          common.disk_shortname_map[dg_name] + "/" +
                                          today + ".csv", delimiter=',', skip_header=1, usecols=(0, 4, 5, 6, 7),
                                          names=["age", "disk_days", "failures", "disk_days_window", "failures_window"])

            age_array[current_date] = current_date
            if len(df_map[today]["disk_days_window"]) < days_to_subtract or df_map[today]["disk_days_window"][len(df_map[today]["disk_days_window"]) - days_to_subtract] <= 0:
                afr_array[current_date] = 0.0
                confident_afr_array[current_date] = 0.0
            else:
                disk_days_window = df_map[today]["disk_days_window"][len(df_map[today]["disk_days_window"]) - days_to_subtract]
                failures_window = df_map[today]["failures_window"][len(df_map[today]["failures_window"]) - days_to_subtract]
                sliding_window_afr = (float(failures_window) / disk_days_window) * 365 * 100
                # if current_date == 31:
                # print(today, disk_days_window, failures_window, sliding_window_afr, len(df_map[today]["disk_days_window"]))
                # exit(0)
                afr_array[current_date] = sliding_window_afr
                disk_days_array[current_date] = df_map[today]["disk_days"][len(df_map[today]["disk_days"]) - days_to_subtract]

                # window_upper_bound = int(sliding_window_afr) + constants.HYSTERESIS_SLIDING_WINDOW
                # num_failures_in_useful_life_window = df_map[today]["failures_window"][int(sliding_window_afr):window_upper_bound]
                # num_disk_days_in_useful_life_window = df_map[today]["disk_days_window"][int(sliding_window_afr):window_upper_bound]
                # if num_disk_days_in_useful_life_window == 0:
                #     print(current_date)
                #     exit(0)
                # confident_afr_array[current_date] = common.get_confident_instantaneous_afr(
                #     sliding_window_afr, num_failures_in_useful_life_window, num_disk_days_in_useful_life_window)
            current_date += 1
            day_wise_dt_range.append(dt)

        fig = plt.figure()
        axarr = fig.add_subplot(111)

        day_wise_dt_range_left = day_wise_dt_range

        common.cluster = "nj"
        dataset = eval("Google")("summary_drive_stats")
        # dg_name_str = ', '.join("'{0}'".format(dg) for dg in list([dg_name]))
        # all_disks_deployment_dates = dataset.get_all_deployment_dates()
        startdate = "2018-08-03"  # all_disks_deployment_dates[0]
        enddate = "2019-09-01"
        age_array = np.zeros(common.days_between(startdate, enddate) + 1)
        dt_range = common.daterange(datetime.datetime.strptime(startdate, "%Y-%m-%d"),
                                    datetime.datetime.strptime(enddate, "%Y-%m-%d"))
        afr_array = np.zeros(common.days_between(startdate, enddate) + 1)
        disk_days_array = np.zeros(common.days_between(startdate, enddate) + 1)

        confident_afr_array = np.zeros(common.days_between(startdate, enddate) + 1)

        df_map = dict()
        current_date = 0
        day_wise_dt_range = list()

        result_date = datetime.datetime.today().strftime('%Y-%m-%d')
        os.makedirs("results/" + result_date, exist_ok=True)
        os.makedirs("results/" + result_date + "/canary/" + common.cluster, exist_ok=True)


        days_to_subtract = 8

        for dt in dt_range:
            today = dt.strftime("%Y-%m-%d")
            logging.info("Processing date %s...", today)
            df_map[today] = np.genfromtxt("datasets/google/data/sep_3/" + common.cluster + "/simulated_date_data/" +
                                          common.disk_shortname_map["M3_m1_s5"] + "/" +
                                          today + ".csv", delimiter=',', skip_header=1, usecols=(0, 4, 5, 6, 7),
                                          names=["age", "disk_days", "failures", "disk_days_window", "failures_window"])

            # df_map[today] = np.genfromtxt("datasets/backblaze/data/simulated_date_data/" +
            #                               common.disk_shortname_map[dg_name] + "/" +
            #                               today + ".csv", delimiter=',', skip_header=1, usecols=(0, 4, 5, 6, 7),
            #                               names=["age", "disk_days", "failures", "disk_days_window", "failures_window"])

            age_array[current_date] = current_date
            if len(df_map[today]["disk_days_window"]) < days_to_subtract or df_map[today]["disk_days_window"][len(df_map[today]["disk_days_window"]) - days_to_subtract] <= 0:
                afr_array[current_date] = 0.0
                confident_afr_array[current_date] = 0.0
            else:
                disk_days_window = df_map[today]["disk_days_window"][len(df_map[today]["disk_days_window"]) - days_to_subtract]
                failures_window = df_map[today]["failures_window"][len(df_map[today]["failures_window"]) - days_to_subtract]
                sliding_window_afr = (float(failures_window) / disk_days_window) * 365 * 100
                # if current_date == 31:
                # print(today, disk_days_window, failures_window, sliding_window_afr, len(df_map[today]["disk_days_window"]))
                # exit(0)
                afr_array[current_date] = sliding_window_afr
                disk_days_array[current_date] = df_map[today]["disk_days"][len(df_map[today]["disk_days"]) - days_to_subtract]

                # window_upper_bound = int(sliding_window_afr) + constants.HYSTERESIS_SLIDING_WINDOW
                # num_failures_in_useful_life_window = df_map[today]["failures_window"][int(sliding_window_afr):window_upper_bound]
                # num_disk_days_in_useful_life_window = df_map[today]["disk_days_window"][int(sliding_window_afr):window_upper_bound]
                # if num_disk_days_in_useful_life_window == 0:
                #     print(current_date)
                #     exit(0)
                # confident_afr_array[current_date] = common.get_confident_instantaneous_afr(
                #     sliding_window_afr, num_failures_in_useful_life_window, num_disk_days_in_useful_life_window)
            current_date += 1
            day_wise_dt_range.append(dt)

        fig = plt.figure()
        axarr = fig.add_subplot(111)

        day_wise_dt_range_right = day_wise_dt_range

        matplotlib.rcParams.update({'font.size': 20})
        # matplotlib.rc('xtick', labelsize=50)
        # matplotlib.rc('ytick', labelsize=50)

        # G-3 (cluster 1)
        # matplotlib.rcParams.update({'font.size': 18})
        # full_disk_afr_array = genfromtxt("results/" + result_date + "/canary/" + common.cluster + "/M3_m1_s5.csv", delimiter=',')
        # full_disk_afr_array = np.pad(full_disk_afr_array, (7, 0), 'constant', constant_values=(0.0, 0.0))
        # axarr.plot_date(day_wise_dt_range, afr_array, 'k', label='AFR')
        # axarr.set_ylim(0, constants.DEFAULT_AFR)
        # axarr.set_xlim([datetime.date(2018, 8, 3), datetime.date(2019, 9, 1)])
        # axarr.set_ylabel("AFR (%)")
        #
        # plt.xticks(rotation=15, fontsize=18)
        # plt.yticks(fontsize=18)
        # ax2 = axarr.twiny()
        # ax2.set_xlim(0, len(afr_array) - 1)
        #
        # y_arr = [float(3.74)] * (common.days_between('2018-11-25', '2019-03-05'))
        # x_arr = list(range(common.days_between('2018-08-03', '2018-11-26'),
        #                    common.days_between('2018-08-03', '2019-03-06')))
        # ax2.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)
        #
        # y_arr = [float(0.94)] * (common.days_between('2018-11-25', '2019-03-05'))
        # ax2.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)
        #
        # y_arr = [float(6.41)] * (common.days_between('2019-03-04', '2019-05-16'))
        # x_arr = list(range(common.days_between('2018-08-03', '2019-03-04'),
        #                    common.days_between('2018-08-03', '2019-05-16')))
        # ax2.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)
        #
        # y_arr = [float(5.61)] * (common.days_between('2019-03-04', '2019-05-16'))
        # ax2.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)
        #
        # ax2.plot(age_array, afr_array, 'k', label='AFR', alpha=0.6)
        # ax2.plot(age_array, full_disk_afr_array[0:len(full_disk_afr_array) - 7 - 1], 'red', label='allDiskAFR', lw=2)
        # ax2.tick_params(top=True, direction="in")
        # ax2.set_xticklabels([])
        # ax2.set_xticks([])
        # # axarr.set_xlabel("Date")
        #
        # legend_elements = [Line2D([0], [0], color='red', lw=2, ls='-', label='AFR of all disks in Dgroup'),
        #                    Line2D([0], [0], color='black', lw=2, ls='-', label='AFR of first step'),
        #                    Line2D([0], [0], color='green', lw=2.5, ls='--', label='Tailoring AFRs (Orig & 2ndLife)'),
        #                    Patch(facecolor='black', edgecolor='gray', label='Tolerated AFR protection', alpha=0.3)]
        #
        # axarr.legend(handles=legend_elements, loc="upper left", ncol=1, frameon=False)  # bbox_to_anchor=(1, 1.04),
        # axarr.xaxis.set_major_locator(MaxNLocator(6))
        # axarr.yaxis.set_visible(False)
        #
        # fig.tight_layout()
        # fig.savefig("results/" + result_date + "/canary/" + common.cluster +
        #             "/G-3_cluster_1.pdf", pad_inches=0, bbox_inches='tight')

        # G-3 (cluster 1) in eval
        # matplotlib.rcParams.update({'font.size': 16})
        # full_disk_afr_array = genfromtxt("results/" + result_date + "/canary/" + common.cluster + "/M3_m1_s5.csv", delimiter=',')
        # full_disk_afr_array = np.pad(full_disk_afr_array, (7, 0), 'constant', constant_values=(0.0, 0.0))
        # axarr.plot_date(day_wise_dt_range, afr_array, 'k', label='AFR')
        # axarr.set_ylim(0, constants.DEFAULT_AFR)
        # axarr.set_xlim([datetime.date(2018, 8, 3), datetime.date(2019, 9, 1)])
        # axarr.set_ylabel("AFR (%)")
        #
        # plt.xticks(rotation=15, fontsize=18)
        # ax2 = axarr.twiny()
        # ax2.set_xlim(0, len(afr_array) - 1)
        #
        # y_arr = [float(3.74)] * (common.days_between('2018-11-25', '2019-03-05'))
        # x_arr = list(range(common.days_between('2018-08-03', '2018-11-26'),
        #                    common.days_between('2018-08-03', '2019-03-06')))
        # ax2.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)
        #
        # y_arr = [float(0.94)] * (common.days_between('2018-11-25', '2019-03-05'))
        # ax2.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)
        #
        # y_arr = [float(6.41)] * (common.days_between('2019-03-04', '2019-05-16'))
        # x_arr = list(range(common.days_between('2018-08-03', '2019-03-04'),
        #                    common.days_between('2018-08-03', '2019-05-16')))
        # ax2.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)
        #
        # y_arr = [float(5.61)] * (common.days_between('2019-03-04', '2019-05-16'))
        # ax2.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)
        #
        # ax2.plot(age_array, afr_array, 'k', label='AFR', alpha=0.6)
        # # ax2.plot(age_array, full_disk_afr_array[0:len(full_disk_afr_array) - 7 - 1], 'red', label='allDiskAFR', lw=2)
        # ax2.tick_params(top=True, direction="in")
        # ax2.set_xticklabels([])
        # ax2.set_xticks([])
        # # axarr.set_xlabel("Date")
        #
        # legend_elements = [Line2D([0], [0], color='black', lw=2, ls='-', label='AFR of first step'),
        #                    Line2D([0], [0], color='green', lw=2.5, ls='--', label='Tailoring AFRs (Orig & 2ndLife)'),
        #                    Patch(facecolor='black', edgecolor='gray', label='Tolerated AFR protection', alpha=0.3),
        #                    Patch(facecolor='maroon', edgecolor='gray', label='Wearout protection', alpha=0.5)]
        #
        # axarr.legend(handles=legend_elements, loc="upper left", ncol=1, frameon=False)  # bbox_to_anchor=(1, 1.04),
        # axarr.xaxis.set_major_locator(MaxNLocator(6))
        # axarr.yaxis.set_visible(False)
        #
        # fig.tight_layout()
        # fig.savefig("results/" + result_date + "/canary/" + common.cluster +
        #             "/G-3_cluster_1_eval.pdf", pad_inches=0,
        #             bbox_inches='tight')

        # G-1 (cluster 1)
        # # matplotlib.rcParams.update({'font.size': 16})
        # axarr.plot_date(day_wise_dt_range, afr_array, 'k', label='AFR')
        # axarr.set_ylim(0, constants.DEFAULT_AFR)
        # axarr.set_xlim([datetime.date(2017, 7, 10), datetime.date(2019, 9, 1)])
        # axarr.set_ylabel("AFR (%)")
        #
        # plt.xticks(rotation=15, fontsize=18)
        # plt.yticks(np.arange(0, 16, 3.0), fontsize=18)
        # ax2 = axarr.twiny()
        # ax2.set_xlim(0, len(afr_array) - 1)
        #
        # y_arr = [float(3.69)] * (common.days_between('2017-12-03', '2018-05-29'))
        # x_arr = list(range(common.days_between('2017-07-10', '2017-12-04'),
        #                    common.days_between('2017-07-10', '2018-05-30')))
        # ax2.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)
        #
        # y_arr = [float(0.398)] * (common.days_between('2017-12-03', '2018-05-29'))
        # ax2.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)
        #
        # y_arr = [float(6.41)] * (common.days_between('2018-05-28', '2019-09-02'))
        # x_arr = list(range(common.days_between('2017-07-10', '2018-05-28'),
        #                    common.days_between('2017-07-10', '2019-09-02')))
        # ax2.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)
        #
        # y_arr = [float(5.61)] * (common.days_between('2018-05-28', '2019-09-02'))
        # ax2.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)
        #
        # ax2.plot(age_array, afr_array, 'k')
        # ax2.tick_params(top=True, direction="in")
        # ax2.set_xticklabels([])
        # ax2.set_xticks([])
        #
        # axarr.xaxis.set_major_locator(MaxNLocator(6))
        #
        # legend_elements = [Line2D([0], [0], color='black', lw=2, ls='-', label='AFR of first step'),
        #                    Line2D([0], [0], color='green', lw=2, ls='--', label='Tailoring AFRs (Orig & 2ndLife)'),
        #                    Patch(facecolor='black', edgecolor='gray', label='Tolerated AFR protection', alpha=0.3),
        #                    Patch(facecolor='maroon', edgecolor='gray', label='Wearout protection', alpha=0.5)]
        #
        # # axarr.legend(handles=legend_elements, ncol=1, bbox_to_anchor=(1.7, 1.05))
        #
        # # axarr.set_xlabel("Date")
        # axarr.set_ylabel("AFR (%)", fontsize=20)
        # fig.tight_layout()
        # fig.savefig("results/" + result_date + "/canary/" + common.cluster + "/G-1_cluster_1_eval.pdf", pad_inches=0, bbox_inches='tight')

        # S-12E (backblaze)
        # full_disk_afr_array = genfromtxt("results/" + result_date + "/canary/" + common.cluster + "/s12e.csv", delimiter=',')
        # full_disk_afr_array = np.pad(full_disk_afr_array, (days_to_subtract - 1, 0), 'constant', constant_values=(0.0, 0.0))
        # afr_array = genfromtxt("results/" + result_date + "/canary/" + common.cluster + "/s12e_raw_afr.csv", delimiter=",")
        # axarr.plot_date(day_wise_dt_range, afr_array, 'k', label='AFR', alpha=0.5)
        # axarr.set_ylim(0, constants.DEFAULT_AFR)
        # axarr.set_xlim([datetime.date(2017, 9, 6), datetime.date(2019, 6, 30)])
        # axarr.set_ylabel("AFR (%)", fontsize=20)
        #
        # plt.xticks(rotation=15, fontsize=18)
        # plt.yticks(fontsize=18)
        # ax2 = axarr.twiny()
        # ax2.set_xlim(0, len(afr_array) - 1)
        #
        # y_arr = [float(3.93)] * (509 - 92)
        # x_arr = list(range(common.days_between('2018-02-02', '2017-09-07'),
        #                    common.days_between('2017-09-07', '2019-03-26')))
        # ax2.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)
        #
        # y_arr = [float(3.33)] * (509 - 92)
        #
        # ax2.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)
        # #
        # # y_arr = [float(6.41)] * (common.days_between('2018-05-28', '2019-09-02'))
        # # x_arr = list(range(common.days_between('2017-07-10', '2018-05-28'),
        # #                    common.days_between('2017-07-10', '2019-09-02')))
        # # ax2.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)
        # #
        # # y_arr = [float(5.61)] * (common.days_between('2018-05-28', '2019-09-02'))
        # # ax2.plot(x_arr, y_arr, ls="--", color="red")
        #
        # ax2.plot(age_array, afr_array, 'k', label='AFR', alpha=0.6)
        # ax2.plot(age_array, full_disk_afr_array[0:len(full_disk_afr_array) - days_to_subtract], 'red', label='allDiskAFR', linewidth=2)
        # ax2.tick_params(top=True, direction="in")
        # ax2.set_xticklabels([])
        # ax2.set_xticks([])
        # np.savetxt("results/" + result_date + "/canary/" + common.cluster + "/s12e_raw_afr.csv", afr_array, delimiter=',')
        # # axarr.set_xlabel("Date")
        #
        # legend_elements = [Line2D([0], [0], color='red', lw=2, ls='-', label='AFR of all disks in Dgroup'),
        #                    Line2D([0], [0], color='black', lw=2, ls='-', label='AFR of canary disks'),
        #                    Line2D([0], [0], color='green', lw=2.5, ls='--', label='Tailoring AFR'),
        #                    Patch(facecolor='black', edgecolor='gray', label='Tolerated AFR protection', alpha=0.3)]
        #
        # axarr.legend(handles=legend_elements, loc="upper left", ncol=1, frameon=False)  # bbox_to_anchor=(1, 1.04),
        # axarr.xaxis.set_major_locator(MaxNLocator(6))
        # # axarr.yaxis.set_visible(False)
        # fig.tight_layout()
        # fig.savefig("results/" + result_date + "/canary/" + common.cluster + "/S-12E_backblaze.pdf", pad_inches=0, bbox_inches='tight')
        #
        #
        # fig, axarr = plt.subplots(2, sharex=True)
        # axarr[0].plot_date(day_wise_dt_range, afr_array, 'r', label='AFR')
        # axarr[0].plot_date(day_wise_dt_range, confident_afr_array, 'k', label='AFR')
        # axarr[0].set_ylim(0, constants.DEFAULT_AFR)
        # axarr[1].plot_date(day_wise_dt_range, disk_days_array, linestyle='-', label='Disks')
        # axarr[0].set_ylabel("AFR (%)")
        # axarr[1].set_ylabel("Disks")
        # for line in axarr[1].lines:
        #     line.set_marker(None)
        # plt.xticks(rotation=20)
        # axarr[0].set_title(common.disk_obfuscation_map[dg_name] + "(" +
        #                 common.cluster_obfuscation_map[common.cluster] +
        #                 ") initial disk AFR by date")
        # fig.savefig("results/" + result_date + "/canary/" + common.cluster + "/" +
        #             common.disk_obfuscation_map[dg_name] + "_" +
        #             common.cluster_obfuscation_map[common.cluster] +
        #             "_initial_week_disks.pdf", pad_inches=0)


        days_to_subtract_left = 46
        full_disk_afr_array = genfromtxt("results/" + result_date + "/canary/bb/s12e.csv", delimiter=',')
        full_disk_afr_array = np.pad(full_disk_afr_array, (days_to_subtract_left - 1, 0), 'constant', constant_values=(0.0, 0.0))
        afr_array_left = genfromtxt("results/" + result_date + "/canary/bb/s12e_raw_afr.csv", delimiter=',')
        age_array = np.arange(0, len(afr_array))

        # set plot style
        plt.style.use(["plotStyle", ])
        # matplotlib.rcParams.update({'font.size': 20})

        # create plot
        fig, axes = plt.subplots(1, 2, figsize=(10,4),
                                 gridspec_kw={"wspace":0.05, "hspace":0},
                                 subplot_kw={"sharey":True, "frame_on":True}
                                 )

        # left subplot
        axes[0].plot_date(day_wise_dt_range_left, afr_array_left, 'k', label='AFR', alpha=0.5)
        axes[0].plot_date(day_wise_dt_range_left, afr_array_left, 'k', label='AFR', alpha=0.6)
        axes[0].plot_date(day_wise_dt_range_left, full_disk_afr_array[0:len(full_disk_afr_array) - days_to_subtract_left], 'red', label='allDiskAFR', linewidth=2)
        axes[0].xaxis.set_tick_params(rotation=20)

        ax2_left = axes[0].twiny()
        ax2_left.set_xlim(0, len(afr_array_left) - 1)
        ax2_left.set_xticks([])

        y_arr = [float(3.93)] * (509 - 92)
        # x_arr = list(range(len(y_arr)))
        x_arr = list(range(common.days_between('2018-02-02', '2017-09-07'),
                           common.days_between('2017-09-07', '2019-03-26')))

        ax2_left.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)

        y_arr = [float(3.33)] * (509 - 92)
        ax2_left.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)


        print(axes[0].get_xticks())
        axes[0].set_xticks([736634. , 736754. , 736876. ,736999. ,737119.])

        # axes[0].tick_params(top=True, direction="in")
        # axes[0].xaxis.set_major_locator(MaxNLocator(8))
        axes[0].yaxis.set_major_locator(MaxNLocator(4))
        # axes[0].set_xticklabels([])
        # axes[0].set_xticks([])
        axes[0].set_ylim(0, constants.DEFAULT_AFR)
        # axes[0].set_xlim([datetime.date(2017, 9, 6), datetime.date(2019, 6, 30)])
        axes[0].set_ylabel("AFR (%)")


        days_to_subtract_right = 8
        full_disk_afr_array = genfromtxt("results/" + result_date + "/canary/" + common.cluster + "/M3_m1_s5.csv", delimiter=',')
        full_disk_afr_array = np.pad(full_disk_afr_array, (days_to_subtract_right - 1, 0), 'constant', constant_values=(0.0, 0.0))
        # afr_array = genfromtxt("results/" + result_date + "/canary/" + common.cluster + "/s12e_raw_afr.csv", delimiter=',')
        age_array = np.arange(0, len(afr_array_left))

        y_arr = [float(3.74)] * (common.days_between('2018-11-25', '2019-03-05'))
        x_arr = list(range(common.days_between('2018-08-03', '2018-11-26'),
                           common.days_between('2018-08-03', '2019-03-06')))

        # right subplot
        print(len(afr_array))
        print(len(day_wise_dt_range_right))
        axes[1].plot_date(day_wise_dt_range_right, afr_array, 'k', label='AFR', alpha=0.5)
        axes[1].plot_date(day_wise_dt_range_right, afr_array, 'k', label='AFR', alpha=0.6)
        axes[1].plot_date(day_wise_dt_range_right, full_disk_afr_array[0:len(full_disk_afr_array) - days_to_subtract_right], 'red', label='allDiskAFR', linewidth=2)

        ax2_right = axes[1].twiny()
        ax2_right.set_xlim(0, len(afr_array) - 1)
        ax2_right.set_xticks([])
        # ax2_right.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)
        # ax2_right.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)

        # y_arr = [float(6.41)] * (common.days_between('2019-03-04', '2019-05-16'))
        # x_arr = list(range(common.days_between('2018-08-03', '2019-03-04'),
        #                    common.days_between('2018-08-03', '2019-05-16')))
        #
        # ax2_right.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)
        # ax2_right.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)
        #
        # y_arr = [float(5.61)] * (common.days_between('2019-03-04', '2019-05-16'))
        # x_arr = list(range(common.days_between('2018-08-03', '2019-03-04'),
        #                                       common.days_between('2018-08-03', '2019-05-16')))
        #
        # ax2_right.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)
        # ax2_right.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)


        # first life
        y_arr = [float(3.74)] * (common.days_between('2018-11-25', '2019-03-05'))
        x_arr = list(range(common.days_between('2018-08-03', '2018-11-26'),
                           common.days_between('2018-08-03', '2019-03-06')))
        ax2_right.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)

        y_arr = [float(0.94)] * (common.days_between('2018-11-25', '2019-03-05'))
        ax2_right.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)

        #second life
        y_arr = [float(6.41)] * (common.days_between('2019-03-04', '2019-05-16'))
        x_arr = list(range(common.days_between('2018-08-03', '2019-03-04'),
                           common.days_between('2018-08-03', '2019-05-16')))
        ax2_right.fill_between(y1=y_arr, x=x_arr, facecolor="black", alpha=0.2)

        y_arr = [float(5.61)] * (common.days_between('2019-03-04', '2019-05-16'))
        ax2_right.plot(x_arr, y_arr, ls="--", color="green", lw=2.5)

        axes[1].xaxis.set_tick_params(rotation=20)

        print(axes[1].get_xticks())
        # axes[1].set_xticks([736938., 737060. , 737180. , 737303.])
        axes[1].set_xticks([736938., 736999., 737060., 737119., 737180., 737241.])

        axes[1].yaxis.set_ticks([])
        # axes[1].xaxis.set_major_locator(MaxNLocator(6))
        axes[1].set_ylim(0, constants.DEFAULT_AFR)
        # axes[1].set_xlim([datetime.date(2017, 9, 6), datetime.date(2019, 6, 30)])

        legend_elements = [Line2D([0], [0], color='red', lw=2, ls='-', label='AFR of all disks in Dgroup'),
                           Line2D([0], [0], color='black', lw=2, ls='-', label='AFR of canary disks'),
                           Line2D([0], [0], color='green', lw=2.5, ls='--', label='Tailoring AFR'),
                           Patch(facecolor='black', edgecolor='gray', label='Tolerated AFR protection', alpha=0.3)]




        axes[1].text(737090., 6.7, "2ndLife")


        plt.legend(handles=legend_elements, frameon=True, facecolor="white", edgecolor="black", framealpha=1,
                   labelspacing=0.2, columnspacing=0.6, bbox_to_anchor=(1.055, 1.042), ncol=2)
        fig.tight_layout()
        fig.savefig("S-12E_backblaze_new.pdf", pad_inches=0, bbox_inches='tight')



        plt.gcf().clear()
