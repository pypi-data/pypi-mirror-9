# Copyright (C) 2015 Haruhiko Matsuo <halm.matsuo@gmail.com>
#
#  Distributed under the MIT License.
#  See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT

import os
import csv
import parser
import raw


def load_pa(filedir, pa_label):
    """ Load data from PA csv files"""

    def make_data(fname, pa_label):
        with open(fname) as f:
            csvitr = csv.reader(f)
            p, d = parser.parser(csvitr, pa_label)
        return (p, d)

    prof_env = []
    prof_dat = []

    # read 7 files of PA profiler.
    for id in range(1, 8):
        # TODO use join?
        fname = os.path.join(filedir, 'output_prof_' + str(id) + '.csv')
        p, d = make_data(fname, pa_label)

        prof_env += [p]
        prof_dat += [d]

    return prof_env, raw.RawData(prof_dat)


def program_info(filedir, fname='output_prof_1.csv'):
    """Get measured labels"""

    full_path = filedir + fname

    labels = []
    MONITOR_LEVEL = ''
    with open(full_path) as f:
        while not (MONITOR_LEVEL == 'Application'):
            l = next(f)
            l = l.split()
            if l[0] == '"Performance' and l[6] == 'Application':
                MONITOR_LEVEL = 'Application'

        # skip the next 'Range'
        next(f)

        # remove double quotes and split lines by csv-delimeter
        fcsv = csv.reader(f)

        # Read until the next 'Range' found
        while True:
            l = next(fcsv)

            if l[0] != 'Range':
                labels.append(l[0])
            else:
                break

        # Get the largest process id (MPI rank) and thread id
        max_pid, max_tid = 0, 0
        for l in fcsv:
            if len(l) == 1:

                l = l[0].split()

                if l[-2] == 'Process' and int(l[-1]) > max_pid:
                    max_pid = int(l[7])

                if l[-2] == 'Thread' and int(l[-1]) > max_tid:
                    max_tid = int(l[7])

        ret = {'num_procs': max_pid + 1,
               'num_threads': max_tid + 1,
               'labels': labels}

    return ret


def get_range_labels(filedir, fname='output_prof_1.csv'):
    """Get measured labels"""

    full_path = filedir + fname

    labels = []
    MONITOR_LEVEL = ''
    with open(full_path) as f:
        while not (MONITOR_LEVEL == 'Application'):
            l = next(f)
            l = l.split()
            if l[0] == '"Performance' and l[6] == 'Application':
                MONITOR_LEVEL = 'Application'

        # skip the next 'Range'
        next(f)

        # remove double quotes and split lines by csv-delimeter
        fcsv = csv.reader(f)

        # Read until the next 'Range' found
        while True:
            l = next(fcsv)

            if l[0] != 'Range':
                labels.append(l[0])
            else:
                break

    return labels
