`timescale 1ns / 1ps
`default_nettype none
module triple(      input  wire [31:0] data_in,
                    output logic signed [31:0] data_out
              );

    //hot take nothing Im about to write is gonna be AXI Compliant I'm just gonna shove them all in one runner
   logic [31:0] count;
    
   always_comb begin
        if($signed(data_in)>7000000000)begin
            data_out = 7000000000;
        end else if($signed(data_in)<-7000000000) begin
            data_out = -7000000000;
        end else begin
            data_out = data_in;
        end
   end

endmodule
`default_nettype wire
