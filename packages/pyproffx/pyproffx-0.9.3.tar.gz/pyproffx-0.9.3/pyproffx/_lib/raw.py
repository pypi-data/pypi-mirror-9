# Copyright (C) 2015 Haruhiko Matsuo <halm.matsuo@gmail.com>
#
#  Distributed under the MIT License.
#  See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT

from common import tag_maker, element_wise


class RawData(object):
    def __init__(self, parsed_input):
        (self._PA1, self._PA2, self._PA3, self._PA4,
         self._PA5, self._PA6, self._PA7) = (0, 1, 2, 3, 4, 5, 6)

        self.PA = parsed_input

        self.has_thread = ('Thread', 0, 0) in self.PA[self._PA1]
        self.has_process = ('Process', 0) in self.PA[self._PA1]
        self.num_processes, self.num_threads = self._num_procs_and_threads()

        self.is_hybrid = self.has_thread and self.has_process
        self.is_thread = self.has_thread and (not self.has_process)
        self.is_flatmpi = (not self.has_thread) and self.has_process
        self.is_single = (not self.has_thread) and (not self.has_process)

        self.max_cycle_counts1_per_process = []
        if self.is_hybrid or self.is_thread:
            for i in range(self.num_processes):
                tag = 'Thread', i, (0, self.num_threads)
                counts = self.cycle_counts1(*tag)
                self.max_cycle_counts1_per_process.append(counts.max())

        self.max_cycle_counts1_per_application = []
        if self.is_hybrid:
            _tmp = self.max_cycle_counts1_per_process
            self.max_cycle_counts1_per_application = max(_tmp)
        elif self.is_thread:
            _tmp = self.cycle_counts1('Thread', 0, (0, self.num_threads))
            self.max_cycle_counts1_per_application = max(_tmp)
        elif self.is_flatmpi:
            counts = self.cycle_counts1('Process', (0, self.num_processes))
            self.max_cycle_counts1_per_application.append(counts.max())
        elif self.is_single:
            counts = self.cycle_counts1('A')
            self.max_cycle_counts1_per_application.append(counts)

    def _num_procs_and_threads(self):
        # Even a sireal program has 1 process at leaset.
        _num_processes = 1
        _num_threads = 0

        if self.has_process:
            _max_process_id = 0
            for k in self.PA[self._PA1].keys():
                if k[0] == 'Process':
                    if k[1] > _max_process_id:
                        _max_process_id = k[1]
            _num_processes += _max_process_id

        if self.has_thread:
            _max_thread_id = 0
            for k in self.PA[self._PA1].keys():
                if k[0] == 'Thread':
                    if k[2] > _max_thread_id:
                        _max_thread_id = k[2]
            _num_threads = _max_thread_id + 1

        return _num_processes, _num_threads

    def _cycle_counts(self, *tag):
        """ """
        return self.PA[self._PA1][tag]['cycle_counts']

    @tag_maker
    @element_wise
    def cycle_counts1(self, *tag):
        """ """
        return self.PA[self._PA1][tag]['cycle_counts']

    @tag_maker
    @element_wise
    def op_stv_wait_sxmiss(self, *tag):
        """ """
        return self.PA[self._PA1][tag]['op_stv_wait_sxmiss']

    @tag_maker
    @element_wise
    def op_stv_wait_sxmiss_ex(self, *tag):
        """ """
        return self.PA[self._PA1][tag]['op_stv_wait_sxmiss_ex']

    @tag_maker
    @element_wise
    def op_stv_wait_nc_pend(self, *tag):
        """ """
        return self.PA[self._PA1][tag]['op_stv_wait_nc_pend']

    @tag_maker
    @element_wise
    def op_stv_wait_ex(self, *tag):
        """ """
        return self.PA[self._PA1][tag]['op_stv_wait_ex']

    @tag_maker
    @element_wise
    def op_stv_wait(self, *tag):
        """ """
        return self.PA[self._PA1][tag]['op_stv_wait']

    @tag_maker
    @element_wise
    def branch_instructions(self, *tag):
        """ """
        return self.PA[self._PA1][tag]['branch_instructions']

    @tag_maker
    @element_wise
    def effective_instruction_counts(self, *tag):
        """ """
        return self.PA[self._PA1][tag]['effective_instruction_counts']

    @tag_maker
    @element_wise
    def eu_comp_wait(self, *tag):
        """ """
        return self.PA[self._PA2][tag]['eu_comp_wait']

    @tag_maker
    @element_wise
    def sleep_cycle(self, *tag):
        """ """
        return self.PA[self._PA2][tag]['sleep_cycle']

    @tag_maker
    @element_wise
    def cse_window_empty(self, *tag):
        """ """
        return self.PA[self._PA2][tag]['cse_window_empty']

    @tag_maker
    @element_wise
    def cse_window_empty_sp_full(self, *tag):
        """ """
        return self.PA[self._PA2][tag]['cse_window_empty_sp_full']

    @tag_maker
    @element_wise
    def fl_comp_wait(self, *tag):
        """ """
        return self.PA[self._PA2][tag]['fl_comp_wait']

    @tag_maker
    @element_wise
    def load_store_instructions(self, *tag):
        """ """
        return self.PA[self._PA2][tag]['load_store_instructions']

    @tag_maker
    @element_wise
    def branch_comp_wait(self, *tag):
        """ """
        return self.PA[self._PA2][tag]['branch_comp_wait']

    @tag_maker
    @element_wise
    def cycle_counts2(self, *tag):
        """ """
        return self.PA[self._PA2][tag]['cycle_counts']

    @tag_maker
    @element_wise
    def inh_cmit_gpr_2write(self, *tag):
        """ """
        return self.PA[self._PA3][tag]['inh_cmit_gpr_2write']

    @tag_maker
    @element_wise
    def end3op(self, *tag):
        """ """
        return self.PA[self._PA3][tag]['3endop']

    @tag_maker
    @element_wise
    def end0op(self, *tag):
        """ """
        return self.PA[self._PA3][tag]['0endop']

    @tag_maker
    @element_wise
    def fma_instructions(self, *tag):
        """ """
        return self.PA[self._PA3][tag]['fma_instructions']

    @tag_maker
    @element_wise
    def end2op(self, *tag):
        """ """
        return self.PA[self._PA3][tag]['2endop']

    @tag_maker
    @element_wise
    def floating_instructions(self, *tag):
        """ """
        return self.PA[self._PA3][tag]['floating_instructions']

    @tag_maker
    @element_wise
    def end1op(self, *tag):
        """ """
        return self.PA[self._PA3][tag]['1endop']

    @tag_maker
    @element_wise
    def cycle_counts3(self, *tag):
        """ """
        return self.PA[self._PA3][tag]['cycle_counts']

    @tag_maker
    @element_wise
    def L2_miss_pf(self, *tag):
        """ """
        return self.PA[self._PA4][tag]['L2_miss_pf']

    @tag_maker
    @element_wise
    def L2_wb_dm(self, *tag):
        """ """
        return self.PA[self._PA4][tag]['L2_wb_dm']

    @tag_maker
    @element_wise
    def L1D_miss(self, *tag):
        """L1D miss"""
        return self.PA[self._PA4][tag]['L1D_miss']

    @tag_maker
    @element_wise
    def instruction_flow_counts(self, *tag):
        """ """
        return self.PA[self._PA4][tag]['instruction_flow_counts']

    @tag_maker
    @element_wise
    def L2_miss_dm(self, *tag):
        """ """
        return self.PA[self._PA4][tag]['L2_miss_dm']

    @tag_maker
    @element_wise
    def cycle_counts4(self, *tag):
        """ """
        return self.PA[self._PA4][tag]['cycle_counts']

    @tag_maker
    @element_wise
    def prefetch_instructions(self, *tag):
        """ """
        return self.PA[self._PA4][tag]['prefetch_instructions']

    @tag_maker
    @element_wise
    def L2_wb_pf(self, *tag):
        """ """
        return self.PA[self._PA4][tag]['L2_wb_pf']

    @tag_maker
    @element_wise
    def SIMD_load_store_instructions(self, *tag):
        """ """
        return self.PA[self._PA5][tag]['SIMD_load_store_instructions']

    @tag_maker
    @element_wise
    def SIMD_floating_instructions(self, *tag):
        """ """
        return self.PA[self._PA5][tag]['SIMD_floating_instructions']

    @tag_maker
    @element_wise
    def SIMD_fl_load_instructions(self, *tag):
        """ """
        return self.PA[self._PA5][tag]['SIMD_fl_load_instructions']

    @tag_maker
    @element_wise
    def trap_DMMU_miss(self, *tag):
        """ """
        return self.PA[self._PA5][tag]['trap_DMMU_miss']

    @tag_maker
    @element_wise
    def SIMD_fma_instructions(self, *tag):
        """ """
        return self.PA[self._PA5][tag]['SIMD_fma_instructions']

    @tag_maker
    @element_wise
    def SIMD_fl_store_instructions(self, *tag):
        """ """
        return self.PA[self._PA5][tag]['SIMD_fl_store_instructions']

    @tag_maker
    @element_wise
    def uDTLB_miss(self, *tag):
        """ """
        return self.PA[self._PA5][tag]['uDTLB_miss']

    @tag_maker
    @element_wise
    def cycle_counts5(self, *tag):
        """ """
        return self.PA[self._PA5][tag]['cycle_counts']

    @tag_maker
    @element_wise
    def fl_store_instructions(self, *tag):
        """ """
        return self.PA[self._PA6][tag]['fl_store_instructions']

    @tag_maker
    @element_wise
    def Reserved32(self, *tag):
        """ """
        return self.PA[self._PA6][tag]['Reserved32']

    @tag_maker
    @element_wise
    def Reserved31(self, *tag):
        """ """
        return self.PA[self._PA6][tag]['Reserved31']

    @tag_maker
    @element_wise
    def ex_store_instructions(self, *tag):
        """ """
        return self.PA[self._PA6][tag]['ex_store_instructions']

    @tag_maker
    @element_wise
    def Reserved27(self, *tag):
        """ """
        return self.PA[self._PA6][tag]['Reserved27']

    @tag_maker
    @element_wise
    def cycle_counts6(self, *tag):
        """ """
        return self.PA[self._PA6][tag]['cycle_counts']

    @tag_maker
    @element_wise
    def ex_load_instructions(self, *tag):
        """ """
        return self.PA[self._PA6][tag]['ex_load_instructions']

    @tag_maker
    @element_wise
    def fl_load_instructions(self, *tag):
        """ """
        return self.PA[self._PA6][tag]['fl_load_instructions']

    @tag_maker
    @element_wise
    def L1I_thrashing(self, *tag):
        """ """
        return self.PA[self._PA7][tag]['L1I_thrashing']

    @tag_maker
    @element_wise
    def unpack_sxar2(self, *tag):
        """ """
        return self.PA[self._PA7][tag]['unpack_sxar2']

    @tag_maker
    @element_wise
    def unpack_sxar1(self, *tag):
        """ """
        return self.PA[self._PA7][tag]['unpack_sxar1']

    @tag_maker
    @element_wise
    def L1I_miss(self, *tag):
        """ """
        return self.PA[self._PA7][tag]['L1I_miss']

    @tag_maker
    @element_wise
    def op_stv_wait_swpf(self, *tag):
        """ """
        return self.PA[self._PA7][tag]['op_stv_wait_swpf']

    @tag_maker
    @element_wise
    def L1D_thrashing(self, *tag):
        """ """
        return self.PA[self._PA7][tag]['L1D_thrashing']

    @tag_maker
    @element_wise
    def cycle_counts7(self, *tag):
        """ """
        return self.PA[self._PA7][tag]['cycle_counts']

    @tag_maker
    @element_wise
    def single_sxar_commit(self, *tag):
        """ """
        return self.PA[self._PA7][tag]['single_sxar_commit']
