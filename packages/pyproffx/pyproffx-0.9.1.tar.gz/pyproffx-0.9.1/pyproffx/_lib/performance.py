# Copyright (C) 2015 Haruhiko Matsuo <halm.matsuo@gmail.com>
#
#  Distributed under the MIT License.
#  See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT

"""Performance"""

from common import monitor_level_checker


class Performance(object):
    def __init__(self, profenv, rawdata):
        self.e = profenv
        self.d = rawdata

    @monitor_level_checker
    def elapsed_time(self, *tag):
        """Elapsed time [sec]"""
        cycle = self.d.cycle_counts1(*tag)
        cpu_clock = self.e[0][2] * 1.0e6
        return cycle.astype(float) / cpu_clock

    def num_floating_ops(self, *tag):
        """Sum of the number of floating operations"""
        f = self.d.floating_instructions(*tag)
        fma = self.d.fma_instructions(*tag)
        simd_f = self.d.SIMD_floating_instructions(*tag)
        simd_fma = self.d.SIMD_fma_instructions(*tag)
        return f + fma*2 + simd_f*2 + simd_fma*4

    @monitor_level_checker
    def mflops(self, *tag):
        """MFLOPS"""
        flop = self.num_floating_ops(*tag)
        cycle = self.d.cycle_counts1(*tag)
        cpu_clock = self.e[0][2]
        return flop / cycle.astype(float) * cpu_clock

    @monitor_level_checker
    def mips(self, *tag):
        """MIPS"""
        cycle = self.d.cycle_counts1(*tag)
        ef_inst = self.d.effective_instruction_counts(*tag)
        cpu_clock = self.e[0][2]
        return ef_inst / cycle.astype(float) * cpu_clock

    @monitor_level_checker
    def memory_throughput(self, *tag):
        """Memory throughput [GB/sec]"""
        L2_miss = self.d.L2_miss_dm(*tag) + self.d.L2_miss_pf(*tag)
        L2_wb = self.d.L2_wb_dm(*tag) + self.d.L2_wb_pf(*tag)
        cycle = self.d.cycle_counts1(*tag)
        cpu_clock = self.e[0][2]
        line_size = 128  # [Byte] L2 cache line
        trans_byte = L2_miss + L2_wb * line_size
        return trans_byte / cycle.astype(float) * cpu_clock / 1.0e3

    @monitor_level_checker
    def L2_throughput(self, *tag):
        """L2 throughput [GB/sec]"""
        L1D_miss = self.d.L1D_miss(*tag)
        cycle = self.d.cycle_counts1(*tag)
        cpu_clock = self.e[0][2]
        line_size = 128  # [Byte] L1 cache line
        trans_byte = L1D_miss * line_size
        return trans_byte / cycle.astype(float) * cpu_clock / 1.0e3
