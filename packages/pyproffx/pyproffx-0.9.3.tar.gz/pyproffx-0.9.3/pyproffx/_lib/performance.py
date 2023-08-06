# Copyright (C) 2015 Haruhiko Matsuo <halm.matsuo@gmail.com>
#
#  Distributed under the MIT License.
#  See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT

"""Performance"""

from common import monitor_level_checker
import numpy as np


class Performance(object):
    def __init__(self, profenv, rawdata):
        self.e = profenv
        self.d = rawdata

    def max_cycle_counts(self, *tag):
        """ """
        label = tag[0][0]
        if tag[0] != 'A':
            id = tag[1]
            if hasattr(id, '__getitem__'):
                id_itr = (i for i in xrange(id[0], id[1]))
            else:
                id_itr = (id,)
        cpu_freq = self.e[0][2]

        if label == 'T':
            if self.d.is_hybrid:
                max_val = self.d.cycle_counts1(*tag)
            elif self.d.is_thread:
                max_val = self.d.cycle_counts1(*tag)
        elif label == 'P':
            if self.d.is_hybrid:
                max_val = self.d.max_cycle_counts1_per_process
                max_val = [max_val[id] for id in id_itr]
            elif self.d.is_flatmpi:
                max_val = self.d.cycle_counts1(*tag)
        elif tag[0][0] == 'A':
            max_val = self.d.max_cycle_counts1_per_application

        return np.array(max_val)

    def num_floating_ops(self, *tag):
        """Sum of the number of floating operations"""
        f = self.d.floating_instructions(*tag)
        fma = self.d.fma_instructions(*tag)
        simd_f = self.d.SIMD_floating_instructions(*tag)
        simd_fma = self.d.SIMD_fma_instructions(*tag)
        return f + fma*2 + simd_f*2 + simd_fma*4

    def mflops(self, *tag):
        """MFLOPS"""
        flop = self.num_floating_ops(*tag)
        cycle = self.max_cycle_counts(*tag)
        cpu_clock = self.e[0][2]
        return flop / cycle.astype(float) * cpu_clock

    def mips(self, *tag):
        """MIPS"""
        cycle = self.max_cycle_counts(*tag)
        ef_inst = self.d.effective_instruction_counts(*tag)
        cpu_clock = self.e[0][2]
        return ef_inst / cycle.astype(float) * cpu_clock

    def memory_throughput(self, *tag):
        """Memory throughput [GB/sec]"""
        L2_miss = self.d.L2_miss_dm(*tag) + self.d.L2_miss_pf(*tag)
        L2_wb = self.d.L2_wb_dm(*tag) + self.d.L2_wb_pf(*tag)
        cpu_clock = self.e[0][2]
        line_size = 128  # [Byte] L2 cache line
        trans_byte = (L2_miss + L2_wb) * line_size
        cycle = self.max_cycle_counts(*tag)
        return trans_byte / cycle.astype(float) * cpu_clock / 1.0e3

    def L2_throughput(self, *tag):
        """L2 throughput [GB/sec]"""
        L1D_miss = self.d.L1D_miss(*tag)
        cpu_clock = self.e[0][2]
        line_size = 128  # [Byte] L1 cache line
        trans_byte = L1D_miss * line_size
        cycle = self.max_cycle_counts(*tag)
        return trans_byte / cycle.astype(float) * cpu_clock / 1.0e3
