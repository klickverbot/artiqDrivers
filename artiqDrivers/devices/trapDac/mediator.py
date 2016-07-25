from artiq.language.core import *


class TrapDacWrapper:
    """
    Wraps basic trap DC & RF interface.
    Allows setting standard trapping parameters via 'named traps'

    device: key for trapDac_controller device
    traps: dict with 'trap names' as key, and 5-vector of [ecNear, ecFar, farComp, nearComp, bottomComp, rfLevel] as value
    """

    def __init__(self, dmgr, device, traps):
        self.device = dmgr.get(device)
        
        self.old_dc_vec = [0]*5
        self.old_rf = -15
        self.traps = traps

    def set_named_trap(self, trap_name):
        """Set the DC voltages and RF power to a named set of parameters"""
        if trap_name not in self.traps:
            raise ValueError("Trap name not in dict")

        self.set_trap(near_ec = self.traps[trap_name][0],
                    far_ec = self.traps[trap_name][1],
                    far_comp = self.traps[trap_name][2],
                    near_comp = self.traps[trap_name][3],
                    bottom_comp = self.traps[trap_name][4],
                    rf_level = self.traps[trap_name][5]])

    def set_trap(self, near_ec=None, far_ec=None, far_comp=None, near_comp=None, bottom_comp=None, rf_level=None):
        """Set the DC voltages and RF power to given values.
        Any unsupplied values are left unchanged."""

        dc_vec = [near_ec, far_ec, far_comp, bottom_comp, near_comp]

        # If any voltages need to be changed ...
        if not all(v is None for v in dc_vec ):
            for i, v in enumerate(dc_vec):
                if v is None:
                    dc_vec[i] = self.old_dc_vec[i]
            self.set_dc(dc_vec)
            self.old_dc_vec = dc_vec

        if rf_level is not None:
            self.set_rf_level(rf_level)
            self.old_rf = rf_level
