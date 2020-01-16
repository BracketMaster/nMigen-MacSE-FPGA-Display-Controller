from nmigen import *
from nmigen.cli import main
import sys
from crt import CRT


class Top(Elaboratable):
    def __init__(self):
        self.CRT=CRT()
        self.HSYNC = Signal()
        self.VIDEO = Signal()
        self.VSYNC = Signal()

    def elaborate(self, platform):
        m = Module()

        #add top clock domain

        #add PLL
        m.submodules += Instance("pll",
            i_clock_in = ClockSignal(domain="sync"),
            o_clock_out = ClockSignal(domain="clk"),
        )

        #add CRT driver
        m.submodules.CRT = self.CRT
        #m.submodules += DomainRenamer({"clk": "input"})(self.CRT)
        m.d.sync += self.HSYNC.eq(self.CRT.HSYNC)
        m.d.sync += self.VIDEO.eq(self.CRT.VIDEO)
        m.d.sync += self.VSYNC.eq(self.CRT.VSYNC)
        return m

from nmigen.back import verilog
f = open("top.v", "w")
top = Top()
f.write(verilog.convert(top, name='top',strip_internal_attrs=True, ports=[top.HSYNC, top.VIDEO, top.VSYNC]))
