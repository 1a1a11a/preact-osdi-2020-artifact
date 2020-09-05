#!/usr/local/bin/python3

import constants
from datasets import Dataset
import sqlite3
import datetime
from datetime import timedelta, date
from collections import OrderedDict
import logging
import common


class Backblaze(Dataset):
    def __init__(self, table_to_query):
        if common.naive == "NAIVE":
            self.csv_path_prefix = "datasets/backblaze/data/simulated_date_data"
        else:
            # self.csv_path_prefix = "datasets/backblaze/data/simulated_date_data_canaries"
            self.csv_path_prefix = "datasets/backblaze/data/simulated_date_data"
        self.csv_cum_path_prefix = "datasets/backblaze/data/simulated_date_data"
        self.conn_static = sqlite3.connect("datasets/backblaze/data/backblaze_2013_Q2_to_2019_Q4.db")
        self.cursor_static = self.conn_static.cursor()
        self.conn = sqlite3.connect(":memory:")
        # self.conn = sqlite3.connect("/tmp/test_date_wise_deployments.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("DROP TABLE IF EXISTS monitored_disks")
        self.cursor.execute("CREATE TABLE monitored_disks(serial_number TEXT NOT NULL, model text not null, " +
                            "size integer, infancy_age integer, useful_life_age integer, is_dead integer default 0, " +
                            "birthday TEXT NOT NULL, expiry TEXT NOT NULL, age integer default 0, phase_of_life " +
                            "integer default 0, useful_life_date text, wearout_date, " +
                            "ft_infancy text, useful_life_scheme text, ft_wearout text, counted integer default 0, " +
                            "urgent default 0, failure integer default 0, censored integer default 0, step integer default -1);")
        self.cursor.execute("CREATE INDEX birthday_idx on monitored_disks(birthday)")
        self.cursor.execute("CREATE INDEX expiry_idx on monitored_disks(expiry)")
        self.cursor.execute("CREATE INDEX failure_idx on monitored_disks(failure)")
        self.cursor.execute("CREATE INDEX is_dead_idx on monitored_disks(is_dead)")
        self.cursor.execute("CREATE INDEX censored_idx on monitored_disks(censored)")
        self.cursor.execute("CREATE INDEX serial_number_idx on monitored_disks(serial_number)")
        self.cursor.execute("CREATE INDEX model_idx on monitored_disks(model)")
        self.cursor.execute("CREATE INDEX infancy_age_idx on monitored_disks(infancy_age)")
        self.cursor.execute("CREATE INDEX useful_life_idx on monitored_disks(useful_life_age)")
        self.cursor.execute("CREATE INDEX phase_of_life_idx on monitored_disks(phase_of_life)")
        self.anomalies = []
        self.anomaly_details = []
        self._disk_map = OrderedDict()
        self._table_to_query = table_to_query
        Dataset.__init__(self, self.__class__.__name__)

    def reset_counters(self):
        self.anomalies = []
        self.anomaly_details = []

    def get_disk_groups(self):
        self.cursor_static.execute("SELECT DISTINCT(model) FROM summary_drive_stats WHERE exclude = 0")
        disk_groups = []
        for d in self.cursor_static.fetchall():
            disk_groups.append(d[0])
        return disk_groups

    def get_all_deployment_dates(self, dgroups=None):
        deployment_dates = list()
        if dgroups is None:
            dgroups = "'HGST HMS5C4040ALE640', 'HGST HMS5C4040BLE640', 'ST4000DM000', 'ST8000DM002', " + \
                          "'ST8000NM0055', 'ST12000NM0007', 'HGST HUH721212ALN604'"
        self.cursor_static.execute("SELECT DISTINCT(birthday) FROM summary_drive_stats WHERE model in (" + dgroups +
                                   ") AND exclude = 0 ORDER BY JULIANDAY(birthday)")
        results = self.cursor_static.fetchall()
        for d in results:
            deployment_dates.append(d[0])
        return deployment_dates

    def get_disks_in_memory(self, dgroups=None):
        if dgroups is None:
            dgroups = "'HGST HMS5C4040ALE640', 'HGST HMS5C4040BLE640', 'ST4000DM000', 'ST8000DM002', " + \
                         "'ST8000NM0055', 'ST12000NM0007', 'HGST HUH721212ALN604'"

        # self.cursor_static.execute("SELECT serial_number, JULIANDAY(expiry) - JULIANDAY(birthday) AS age, birthday, " +
        #                            "expiry, size, ft_infancy, ft_useful_life, ft_wearout, model FROM " +
        #                            "summary_drive_stats WHERE model in (" + dgroups + ") AND JULIANDAY(expiry) >= " +
        #                            "JULIANDAY(birthday) AND exclude != 1 ORDER BY JULIANDAY(birthday) asc, " +
        #                            "serial_number ASC")
        self.cursor_static.execute("SELECT serial_number, JULIANDAY(expiry) - JULIANDAY(birthday) AS age, birthday, " +
                                   "expiry, model, -1 as step FROM " +
                                   "summary_drive_stats WHERE model in (" + dgroups + ") AND JULIANDAY(expiry) >= " +
                                   "JULIANDAY(birthday) AND exclude != 1 ORDER BY JULIANDAY(birthday) asc, " +
                                   "serial_number ASC")
        results = self.cursor_static.fetchall()
        for r in results:
            self._disk_map[r[0]] = r
        return self._disk_map

    def add_new_disk(self, serial_no, disk_group, birthday, size, step):
        self.cursor.execute("INSERT INTO monitored_disks (serial_number, birthday, expiry, model, phase_of_life, " +
                            "is_dead, size, useful_life_date, wearout_date, infancy_age, useful_life_age," +
                            " failure, censored, step) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            serial_no, birthday, constants.END_DATE, disk_group, 0, 0, size, "", "", 0, 0, 0, 0, step))
        self.conn.commit()
        return

    def report_expiry(self, serial_no, expiry):
        self.cursor.execute("UPDATE monitored_disks SET expiry = '" + expiry + "', is_dead = 1, failure = 1 WHERE " +
                            "serial_number = '" + serial_no + "'")
        self.conn.commit()
        self.cursor.execute("SELECT useful_life_scheme FROM " + self._table_to_query + " WHERE serial_number = '" +
                            serial_no + "'")
        return self.cursor.fetchall()

    def report_decommissioning(self, serial_no, expiry):
        self.cursor.execute("UPDATE monitored_disks SET expiry = '" + expiry + "', is_dead = 0, failure = 0, " +
                            "censored = 1 WHERE serial_number = '" + serial_no + "'")
        self.conn.commit()
        self.cursor.execute("SELECT serial_number FROM " + self._table_to_query + " WHERE serial_number = '" +
                            serial_no + "' and censored = 1")
        return self.cursor.fetchall()

    def get_all_expired_disks(self, disk_groups=None):
        if disk_groups is None:
            disk_groups = "'HGST HMS5C4040ALE640', 'HGST HMS5C4040BLE640', 'ST4000DM000', 'ST8000DM002', " + \
                          "'ST8000NM0055', 'ST12000NM0007', 'HGST HUH721212ALN604'"
        self.cursor_static.execute("SELECT serial_number, model, birthday, expiry FROM summary_drive_stats WHERE " +
                                   "JULIANDAY(expiry) >= JULIANDAY(birthday) AND failure = 1 AND model IN (" +
                                   disk_groups + ") and exclude = 0 ORDER BY JULIANDAY(expiry)")

        expired_disk_details = dict()
        for d in self.cursor_static.fetchall():
            if d[3] not in expired_disk_details:
                expired_disk_details[d[3]] = dict()
            if d[1] not in expired_disk_details[d[3]]:
                expired_disk_details[d[3]][d[1]] = dict()
            expired_disk_details[d[3]][d[1]][d[0]] = (d[0], d[2])

        return expired_disk_details

    def get_all_decommissioned_disks(self, disk_groups=None):
        if disk_groups is None:
            disk_groups = "'HGST HMS5C4040ALE640', 'HGST HMS5C4040BLE640', 'ST4000DM000', 'ST8000DM002', " + \
                          "'ST8000NM0055', 'ST12000NM0007', 'HGST HUH721212ALN604'"
        self.cursor_static.execute("SELECT serial_number, model, birthday, expiry FROM summary_drive_stats WHERE " +
                                   "JULIANDAY(expiry) >= JULIANDAY(birthday) AND failure = 0 AND censored = 1 AND " +
                                   "model IN (" + disk_groups + ") AND exclude = 0 ORDER BY JULIANDAY(expiry)")

        decom_disk_details = dict()
        for d in self.cursor_static.fetchall():
            if d[3] not in decom_disk_details:
                decom_disk_details[d[3]] = dict()
            if d[1] not in decom_disk_details[d[3]]:
                decom_disk_details[d[3]][d[1]] = dict()
            decom_disk_details[d[3]][d[1]][d[0]] = (d[0], d[2], d[3])

        return decom_disk_details

    def get_disks_entering_useful_life(self, disk_group, today, infancy_age, budget=-1, capacity=-1):
        self.cursor.execute("SELECT serial_number FROM monitored_disks WHERE model = '" + disk_group + "' AND " +
                            "phase_of_life = 0 AND counted = 0 AND JULIANDAY('" + today +
                            "') - JULIANDAY(birthday) >= " + str(infancy_age) + " AND JULIANDAY(expiry) = JULIANDAY('" +
                            constants.END_DATE + "') AND infancy_age = 0 AND failure = 0 AND censored = 0 ORDER BY " +
                            "JULIANDAY(birthday)")
        disks_transitioning_to_useful_life = list()
        results = self.cursor.fetchall()
        for d in results:
            disks_transitioning_to_useful_life.append(d[0])

        args = tuple(disks_transitioning_to_useful_life)
        self.cursor.execute("UPDATE monitored_disks SET infancy_age = " + str(infancy_age) + " WHERE model = '" +
                            str(disk_group) + "' AND serial_number IN ({seq})".format(
            seq=','.join(['?'] * len(disks_transitioning_to_useful_life))), args)
        self.conn.commit()
        return disks_transitioning_to_useful_life

    def get_all_disks_entering_useful_life(self, today, budget=-1, total_infancy_disks=-1):
        self.cursor.execute(
            "SELECT serial_number FROM monitored_disks WHERE phase_of_life = 0 AND counted = 0 AND JULIANDAY('" +
            today + "') - JULIANDAY(birthday) >= infancy_age AND infancy_age != 0 AND JULIANDAY(expiry) = JULIANDAY('" +
            constants.END_DATE + "') AND failure = 0 AND censored = 0 ORDER BY JULIANDAY(birthday)")
        disks_transitioning_to_useful_life = list()

        results = self.cursor.fetchall()

        for d in results:
            disks_transitioning_to_useful_life.append(d[0])

        args = tuple(disks_transitioning_to_useful_life)
        self.cursor.execute("UPDATE monitored_disks SET phase_of_life = 1, counted = 1 WHERE serial_number " +
                            "IN ({seq})".format(seq=','.join(['?'] * len(disks_transitioning_to_useful_life))), args)
        self.conn.commit()

        return disks_transitioning_to_useful_life

    def get_disks_changing_phase_of_life(self, disk_group, today, phase_of_life, phase_of_life_age):
        self.cursor.execute(
            "SELECT serial_number, step FROM monitored_disks WHERE model = ? and phase_of_life = ? AND " +
            "counted = 1 AND JULIANDAY(?) - JULIANDAY(birthday) >= ? AND JULIANDAY(expiry) = JULIANDAY(?) "
            "AND failure = 0 AND censored = 0 ORDER BY birthday", (disk_group, phase_of_life,
                                                                               today, phase_of_life_age,
                                                                               constants.END_DATE))
        disks_transitioning_to_another_phase = list()
        disk_details_of_transitioning_disks = list()

        results = self.cursor.fetchall()

        for d in results:
            disks_transitioning_to_another_phase.append(d[0])
            disk_details_of_transitioning_disks.append((d[0], d[1]))

        args = (disks_transitioning_to_another_phase)
        self.cursor.execute("UPDATE monitored_disks SET phase_of_life = phase_of_life + 1 " +
                            " WHERE serial_number " + "IN ({seq})".format(seq=','.join(['?'] * len(
                                disks_transitioning_to_another_phase))), args)
        self.conn.commit()
        return disk_details_of_transitioning_disks

    def get_disks_entering_wearout(self, disk_group, today, wearout_age,
                                   urgent=1, budget=-1, capacity=-1):
        self.cursor.execute("SELECT serial_number FROM monitored_disks WHERE model = ? AND " +
                            "((counted = 1) OR (counted = -1)) AND " +
                            "JULIANDAY(?) - JULIANDAY(birthday) >= ? AND JULIANDAY(expiry) = " +
                            "JULIANDAY(?) AND failure = 0 AND censored = 0 ORDER BY " +
                            "JULIANDAY(birthday)", (disk_group, today, wearout_age, constants.END_DATE))
        disks_transitioning_to_wearout = list()
        for d in self.cursor.fetchall():
            disks_transitioning_to_wearout.append(d[0])

        args = (wearout_age, urgent, disk_group)
        args += tuple(disks_transitioning_to_wearout)
        self.cursor.execute("UPDATE monitored_disks SET useful_life_age = ?, urgent = ? WHERE model = ? AND " +
                            "serial_number IN ({seq})".format(seq=','.join(['?'] * len(
                                disks_transitioning_to_wearout))), args)
        self.conn.commit()

        return disks_transitioning_to_wearout

    def get_all_disks_entering_wearout(self, today, budget=-1, total_useful_life_disks=-1):
        self.cursor.execute(
            "SELECT serial_number FROM monitored_disks WHERE counted = 1 AND " +
            "JULIANDAY(?) - JULIANDAY(birthday) >= useful_life_age AND useful_life_age > 0 AND " +
            "JULIANDAY(expiry) = JULIANDAY(?) AND urgent = 1 AND failure = 0 AND censored = 0 ORDER BY birthday", (
                today, constants.END_DATE))
        disks_transitioning_to_wearout = list()

        results = self.cursor.fetchall()

        for d in results:
            disks_transitioning_to_wearout.append(d[0])

        args = tuple(disks_transitioning_to_wearout)
        self.cursor.execute("UPDATE monitored_disks SET counted = 2 WHERE serial_number " +
                            "IN ({seq})".format(seq=','.join(['?'] * len(
                                disks_transitioning_to_wearout))), args)
        self.conn.commit()

        return disks_transitioning_to_wearout

    def get_all_disks_entering_non_urgent_wearout(self, today, budget=-1, total_useful_life_disks=-1):
        self.cursor.execute(
            "SELECT serial_number FROM monitored_disks WHERE " +
            "counted = 1 AND JULIANDAY(?) - JULIANDAY(birthday) >= useful_life_age AND " +
            "useful_life_age > 0 AND JULIANDAY(expiry) = JULIANDAY(?) AND urgent = 0 AND failure = 0 AND " +
            "censored = 0 ORDER BY birthday", (today, constants.END_DATE))
        disks_transitioning_to_wearout = list()

        results = self.cursor.fetchall()

        for d in results:
            disks_transitioning_to_wearout.append(d[0])

        args = tuple(disks_transitioning_to_wearout)
        self.cursor.execute("UPDATE monitored_disks SET counted = 2 WHERE serial_number " +
                            "IN ({seq})".format(seq=','.join(['?'] * len(
                                disks_transitioning_to_wearout))), args)
        self.conn.commit()

        return disks_transitioning_to_wearout
