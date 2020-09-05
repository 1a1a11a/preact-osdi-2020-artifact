#!/usr/local/bin/python3

from change_point_detectors import Detector
import constants
import matlab.engine


class Beatlex(Detector):
    def __init__(self):
        print("Initializing " + self.__class__.__name__ + " change point detector...")
        self.eng = matlab.engine.start_matlab()
        self._afr = []
        Detector.__init__(self, self.__class__.__name__)

    def detect_infant_mortality_end(self, data):
        self.eng.cd(r'/Users/saukad/devel/heart/change_points/implementations/beatlex', nargout=0)
        # afr = []
        for d in data['cum_afr']:
            # afr.append(float(d))
            self._afr.append(float(d))
        starts, ends, idx = self.eng.calculate_disk_change_point(matlab.double(self._afr), nargout=3)

        # Now we need to identify which among these actually classifies as a valid change point
        slice_start = 0
        for s in starts[0]:
            if (int(s) > 1) and ((data['cum_afr'][slice_start:int(s)].max() - data['cum_afr'][slice_start:int(s)].min())
                                     <= constants.AFR_DIFF_THRESHOLD) and \
                    (slice_start > constants.MIN_DAYS_BEFORE_STABLE_STATE) and \
                    (s - slice_start > constants.MIN_SEGMENT_DAYS):
                return s, data['cum_afr'][slice_start:int(s)].mean()
            slice_start = int(s)
        return -1

    def detect_old_age_start(self, data, stable_state_start, stable_state_afr):
        self.eng.cd(r'/Users/saukad/devel/heart/change_points/implementations/beatlex', nargout=0)
        # afr = []
        for d in data['cum_afr']:
            # afr.append(float(d))
            self._afr.append(float(d))
        starts, ends, idx = self.eng.calculate_disk_change_point(matlab.double(self._afr), nargout=3)

        # Now we need to identify which among these actually classifies as a valid change point
        slice_start = stable_state_start
        for s in starts[0]:
            if (int(s) > 1) and (data['cum_afr'][slice_start:int(s)].max() > stable_state_afr) and \
                    ((s - stable_state_start) > constants.MIN_DAYS_BEFORE_OLD_AGE):
                return s
            slice_start = int(s)
        return -1
