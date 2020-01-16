"""
This Python module is capable of driving 
screen of the MacSE CRT screen.

This module can generate verilog on its own,
but you must provide a clock of ~15.6672MHz
to the generated verilog.
>>> python3 crt.py generate
"""

from nmigen import *
from nmigen.cli import main
from nmigen.back.pysim import *
import numpy as np
import matplotlib.pyplot as plt
import sys

h_res = 704
v_res = 370

#portion of the video that gets displayed
active_video_h = 192
active_video_v = 28

#when is HSYNC low
HSYNC_low_begin = 15
HSYNC_low_end = 302

#when is VSYNC low
VSYNC_low_begin = 0
VSYNC_low_end = 4

total_pixels = h_res*v_res - 1

class CRT(Elaboratable):
    def __init__(self, sim=False, width=20):
        self.HSYNC = Signal()
        self.VIDEO = Signal()
        self.VSYNC = Signal()
        self.sim = sim
        self.width=20

        #expose internals for debugging
        if(self.sim):
            self.valid = Signal()
            self.pix_count = Signal(unsigned(self.width))
            self.h_count = Signal(unsigned(self.width))
            self.v_count = Signal(unsigned(self.width))

            self.active_row = Signal(unsigned(self.width))
            self.active_col = Signal(unsigned(self.width))

    def elaborate(self, platform):
        m = Module()

        #add unique clock domain
        m.domains.clk = ClockDomain("clk")

        pix_count = Signal(unsigned(self.width))

        valid = Signal()

        #pixels in one frame
        with m.If(pix_count < total_pixels):
            m.d.clk += pix_count.eq(pix_count + 1)
        with m.Else():
            m.d.clk += pix_count.eq(1)

        #horizontal index in current frame
        h_count = Signal(unsigned(self.width))
        with m.If(h_count < h_res - 1):
            m.d.clk += h_count.eq(h_count + 1)
        with m.Else():
            m.d.clk += h_count.eq(0)

        #vertical index in current frame
        v_count = Signal(unsigned(self.width))
        m.d.comb += v_count.eq(pix_count // h_res)

        #VSYNC
        with m.If((v_count >= VSYNC_low_begin) & (v_count <= VSYNC_low_end)):
            m.d.comb += self.VSYNC.eq(0)
        with m.Else():
            m.d.comb += self.VSYNC.eq(1)

        #HSYNC
        with m.If((h_count >= HSYNC_low_begin) & (h_count <= HSYNC_low_end)):
            m.d.comb += self.HSYNC.eq(0)
        with m.Else():
            m.d.comb += self.HSYNC.eq(1)

        
        #when is the video signal valid?
        valid = Signal()
        with m.If( (h_count >= active_video_h ) & (v_count >= active_video_v ) ):
            m.d.comb += valid.eq(1)
        with m.Else():
            m.d.comb += valid.eq(0)
        
        #what are the actual rows and columns on the screen
        active_col = Signal(unsigned(self.width))
        active_row = Signal(unsigned(self.width))
        m.d.comb += active_col.eq(h_count - 192)
        m.d.comb += active_row.eq(v_count - 28)
        
        #video signal
        m.d.comb += self.VIDEO.eq(valid & h_count[3] & v_count[3])

        #debugging
        if(self.sim):
            m.d.comb += self.valid.eq(valid)
            m.d.comb += self.pix_count.eq(pix_count)
            m.d.comb += self.h_count.eq(h_count)
            m.d.comb += self.v_count.eq(v_count)

            m.d.comb += self.active_row.eq(active_row)
            m.d.comb += self.active_col.eq(active_col)
        
        return m

def draw_single_frame():
    #how many rows in one frame to simulate?
    sim_rows = 342

    #populate array with image
    arr = np.zeros((342, 512))

    for count in range((sim_rows+28)*h_res):
        if((yield dut.valid)):
            arr[(yield dut.active_row),(yield dut.active_col)] = (yield dut.VIDEO)

        #advance clock
        yield

    #display image
    plt.imshow(arr, cmap='gray', vmin=0, vmax=1)
    plt.show()

VCD=False

import argparse
class HelpfulParser(argparse.ArgumentParser):
    def error(self, message):
        help = ''
        help += "\nExamples:\npython3 crt.py simulate --write_VCD=True"
        help += "\npython3 crt.py generate\n"
        sys.stderr.write(f'%s\n' % message)
        self.print_help()
        sys.stderr.write(help)
        sys.exit(2)

if __name__ == "__main__":

    #parse arguments
    parser = HelpfulParser()
    parser.add_argument("action", choices={'simulate','generate'})
    parser.add_argument('--write_VCD', help="whether to write VCD", default='True', type=str)
    args = parser.parse_args()

    #simulate
    if args.action == "simulate":
        print("SIMULATING...")
        dut = CRT(sim=True)
        sim = Simulator(dut)
        sim.add_clock(1/(15.6672e6), domain="clk")
        sim.add_sync_process(draw_single_frame)

        if(args.write_VCD == 'True'):
            with sim.write_vcd("test.vcd", "test.gtkw"):
                sim.run()
        else:
            sim.run()
    
    #generate verilog
    elif args.action == "generate":
        print("GENERATING...")
        from nmigen.back import verilog
        verilog_file = "CRT.v"
        f = open(verilog_file, "w")
        f.write(verilog.convert(CRT(), name='top',strip_internal_attrs=True))
        print(f"Verilog Written to: {verilog_file}")