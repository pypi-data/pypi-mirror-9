# Copyright (C) 2015 Haruhiko Matsuo <halm.matsuo@gmail.com>
#
#  Distributed under the MIT License.
#  See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT

from common import return_val_unit


class ElapsedTime(object):
    def __init__(self, profenv, rawdata):
        self.e = profenv
        self.d = rawdata

    @return_val_unit
    def int_memwait(self, *tag, **keyward):
        """ """
        return self.d.op_stv_wait_sxmiss_ex(*tag)

    @return_val_unit
    def float_memwait(self, *tag):
        """ """
        l2_wait = self.d.op_stv_wait_sxmiss(*tag)
        int_l2_wait = self.d.op_stv_wait_sxmiss_ex(*tag)
        return l2_wait - int_l2_wait

    @return_val_unit
    def store_wait(self, *tag):
        """ """
        return self.d.cse_window_empty_sp_full(*tag)

    @return_val_unit
    def int_cachewait(self, *tag):
        """ """
        wait = self.d.op_stv_wait_ex(*tag)
        l2_wait = self.d.op_stv_wait_sxmiss_ex(*tag)
        return wait - l2_wait

    @return_val_unit
    def float_cachewait(self, *tag):
        """ """
        wait = self.d.op_stv_wait(*tag)
        int_wait = self.d.op_stv_wait_ex(*tag)
        l2_wait = self.d.op_stv_wait_sxmiss(*tag)
        int_l2_wait = self.d.op_stv_wait_sxmiss_ex(*tag)
        return wait - l2_wait - int_wait + int_l2_wait

    @return_val_unit
    def int_opwait(self, *tag):
        """ """
        fl_comp_wait = self.d.fl_comp_wait(*tag)
        eu_comp_wait = self.d.eu_comp_wait(*tag)
        return eu_comp_wait - fl_comp_wait

    @return_val_unit
    def float_opwait(self, *tag):
        """ """
        return self.d.fl_comp_wait(*tag)

    @return_val_unit
    def branch_wait(self, *tag):
        """ """
        return self.d.branch_comp_wait(*tag)

    @return_val_unit
    def inst_fetch_wait(self, *tag):
        """ """
        cse = self.d.cse_window_empty(*tag)
        cse_sp = self.d.cse_window_empty_sp_full(*tag)
        sleep = self.d.sleep_cycle(*tag)
        return cse - cse_sp - sleep

    @return_val_unit
    def barrier(self, *tag):
        """ """
        return self.d.sleep_cycle(*tag)

    @return_val_unit
    def uOPcommit(self, *tag):
        """ """
        eff_inst = self.d.effective_instruction_counts(*tag)
        inst_flow = self.d.instruction_flow_counts(*tag)
        usxar1 = self.d.unpack_sxar1(*tag)
        usxar2 = self.d.unpack_sxar2(*tag)
        uOPs = inst_flow - (eff_inst + usxar1 + usxar2)
        return uOPs

    @return_val_unit
    def other_wait(self, *tag):
        """ """
        end0op = self.d.end0op(*tag)
        ostv_wait = self.d.op_stv_wait(*tag)
        cse = self.d.cse_window_empty(*tag)
        eu_comp_wait = self.d.eu_comp_wait(*tag)
        branch = self.d.branch_comp_wait(*tag)
        inst_flow = self.d.instruction_flow_counts(*tag)
        usxar1 = self.d.unpack_sxar1(*tag)
        usxar2 = self.d.unpack_sxar2(*tag)
        eff_inst = self.d.effective_instruction_counts(*tag)
        owait = end0op - ostv_wait - cse - eu_comp_wait - branch
        owait = owait - (inst_flow - (eff_inst + usxar1 + usxar2))
        return owait

    @return_val_unit
    def end1op(self, *tag):
        """ """
        return self.d.end1op(*tag)

    @return_val_unit
    def int_wr_wait(self, *tag):
        """ """
        return self.d.inh_cmit_gpr_2write(*tag)

    @return_val_unit
    def end2or3op(self, *tag):
        """ """
        end2op = self.d.end2op(*tag)
        end3op = self.d.end3op(*tag)
        inh = self.d.inh_cmit_gpr_2write(*tag)
        return end2op + end3op - inh

    @return_val_unit    
    def end4op(self, *tag):
        """ """
        cycle = self.d.cycle_counts1(*tag)
        end0op = self.d.end0op(*tag)
        end1op = self.d.end1op(*tag)
        end2op = self.d.end2op(*tag)
        end3op = self.d.end3op(*tag)
        return cycle - end0op - end1op - end2op - end3op
