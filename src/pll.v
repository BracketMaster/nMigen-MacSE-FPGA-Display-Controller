/**
 * PLL configuration
 *
 * This Verilog module was generated automatically
 * using the icepll tool from the IceStorm project.
 * Use at your own risk.
 *
 * Given input frequency:        12.000 MHz
 * Requested output frequency:  140.000 MHz
 * Achieved output frequency:   141.000 MHz
 */

module pll(
	input  clock_in,
	output clock_out,
	output locked
	);

wire clock_intermediate;

SB_PLL40_CORE #(
		.FEEDBACK_PATH("SIMPLE"),
		.DIVR(4'b0000),		// DIVR =  0
		.DIVF(7'b0101110),	// DIVF = 46
		.DIVQ(3'b010),		// DIVQ =  2
		.FILTER_RANGE(3'b001)	// FILTER_RANGE = 1
	) uut (
		.LOCK(locked),
		.RESETB(1'b1),
		.BYPASS(1'b0),
		.REFERENCECLK(clock_in),
		.PLLOUTCORE(clock_intermediate)
		);

reg [7:0]counter = 0;
assign clock_out = (counter > 4) ? 1 : 0;
always @(posedge clock_intermediate)
begin
if (counter < 8)
	counter <= counter + 1;
else
	counter <= 0;
end

endmodule
