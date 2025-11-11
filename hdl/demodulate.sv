`timescale 1ns / 1ps
`default_nettype none
module demodulate #(
    parameter integer C_S00_AXIS_TDATA_WIDTH = 32,
    parameter integer C_M00_AXIS_TDATA_WIDTH = 32
)(
    // ports of axi slave bus interface s00_axis
    input wire s00_axis_aclk,
    input wire s00_axis_aresetn,
    input wire s00_axis_tlast,
    input wire s00_axis_tvalid,
    input wire [C_S00_AXIS_TDATA_WIDTH-1:0] s00_axis_tdata,
    input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1:0] s00_axis_tstrb,
    output logic s00_axis_tready,

    // ports of axi master bus interface m00_axis
    input wire m00_axis_tready,
    output logic m00_axis_tvalid,
    output logic m00_axis_tlast,
    output logic [C_M00_AXIS_TDATA_WIDTH-1:0] m00_axis_tdata, // [15:0] is magnitude (unsigned 16-bit integer). [31:16] is angle.
    output logic [(C_M00_AXIS_TDATA_WIDTH/8)-1:0] m00_axis_tstrb
);

logic [15:0] angle, angle_reg;
logic signed [31:0] angle_dif,res;

// todo: wire up oliver's cordic to the input
always_comb begin
    angle = m00_axis_tdata[31:16]; // grabbing upper 15 bits as the angle
    s00_axis_tready = m00_axis_tready || ~m00_axis_tvalid;
    angle_dif = $signed({1'b0,angle}) - $signed({1'b0,angle_reg}); // derivative issue
    res = angle_dif >>> 1;
end

always_ff @(posedge s00_axis_aclk)begin
    if(s00_axis_aresetn)begin
        // don't do anything
    end else begin
        if(s00_axis_tvalid && s00_axis_tready)begin
            // grab valid data and compute the difference
            angle_reg <= angle;
            m00_axis_tdata <= {16'b0,angle_dif[15:0]};// just grabbing the bottom 16 bits
            m00_axis_tvalid <= 1'b1;
	    m00_axis_tlast <= s00_axis_tlast;
	    m00_axis_tstrb <= s00_axis_tstrb;
        end else begin
            if(m00_axis_tvalid && m00_axis_tready)begin // check if data is grabbed
                m00_axis_tvalid <= 1'b0;
            end
        end
    end
end

endmodule


`default_nettype wire
