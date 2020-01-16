prog: top.bin
	iceprog -S top.bin

top.bin: top.asc
	icepack top.asc top.bin

top.asc: top.pcf top.blif
	arachne-pnr -d 8k -p top.pcf top.blif -o top.asc

top.blif: top.v pll.v
	yosys -p "synth_ice40 -blif top.blif" top.v pll.v

pll.v:
	icepll -m -f pll.v -o 140

top.v:
	python3 generate_top_ice40HX8K.py

clean:
	rm -rf pll.v test.gtkw test.vcd CRT.v top.v top.bin top.blif top.asc

sim:
	python3 crt.py simulate --write_VCD=False

.PHONY: prog clean sim