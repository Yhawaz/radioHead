module counter(     input wire clk_in,
                    input wire rst_in,
                    input wire [31:0] period_in,
                    output logic [31:0] count_out
              );
   logic [63:0] count;
   always_comb begin
      if((rst_in == 1) || (count_out == period_in -1)) begin
         count = 0;
      end
      else begin
         count = count_out + 1;
      end
   end

   always_ff @(posedge clk_in)begin
         count_out <= count;
   end
endmodule