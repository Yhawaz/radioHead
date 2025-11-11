`timescale 1ns / 1ps
`default_nettype none
module diff_manchester#(
    parameter integer C_S00_AXIS_TDATA_WIDTH = 32,
    parameter integer C_M00_AXIS_TDATA_WIDTH = 32

)(
    // Ports of Axi Slave Bus Interface S00_AXIS
    input wire s00_axis_aclk,
    input wire s00_axis_aresetn,
    input wire s00_axis_tlast,
    input wire s00_axis_tvalid,
    input wire [C_S00_AXIS_TDATA_WIDTH-1:0] s00_axis_tdata,
    input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1:0] s00_axis_tstrb,
    output logic s00_axis_tready,

    // Ports of Axi Master Bus Interface M00_AXIS
    input wire m00_axis_tready,
    output logic m00_axis_tvalid,
    output logic m00_axis_tlast,
    output logic [C_M00_AXIS_TDATA_WIDTH-1:0] m00_axis_tdata, // [15:0] is magnitude (unsigned 16-bit integer). [31:16] is angle.
    output logic [(C_M00_AXIS_TDATA_WIDTH/8)-1:0] m00_axis_tstrb
);




//inputs:
//a 1 or a 0, im gonna assume its the least significant bit 
//
//reasoning behind this, bpsk will produce one value for each iq signal, since we're streaming it theres no point in buffering or batching so we're getting and producing 1 bit every cycle(or every iq value)

//outputs
//a 1 or a 0

//stateful
logic prev_bit;

//comb
logic out_bit;
logic in_handshake;
logic out_handshake;

always_comb begin
   	s00_axis_tready = m00_axis_tready || ~m00_axis_tvalid;
	in_handshake = s00_axis_tready && s00_axis_tvalid;
	out_handshake = m00_axis_tready && m00_axis_tvalid;
	out_bit = prev_bit != s00_axis_tdata[0];
	m00_axis_tstrb = 4'b1111;
	
end

always_ff@(posedge s00_axis_aclk)begin
	if(s00_axis_aresetn == 1'b0)begin
		prev_bit<=1;
		m00_axis_tvalid<=0;
		m00_axis_tlast<=0;
		m00_axis_tdata<=0;
	end else begin
		if(in_handshake)begin
			prev_bit<=s00_axis_tdata[0];
			m00_axis_tdata<={31'b0,out_bit};
			m00_axis_tvalid<=1;
			m00_axis_tlast<=s00_axis_tlast;
		end else if (out_handshake)begin
			m00_axis_tvalid<=0;
			m00_axis_tlast<=0;
		end

	end
end


endmodule
