module shifter(   input wire clk,
              input wire rst,
              input wire [31:0] data_in,
              input wire valid_data_in,
              input wire [3:0] sh_amt,
              output logic [7:0] sig_out);
 
    logic [31:0] cur_data;
    logic [7:0] shifted_data;

    
    assign shifted_data = cur_data >> 2*sh_amt;
    assign sig_out = shifted_data[7:0]; // just grabbing 8 bottom bits


    always_ff @(posedge clk)begin
        if(rst)begin
            sig_out <= 0;
        end else begin
            if(valid_data_in)begin
                cur_data <= data_in;
            end
        end
    end	    

endmodule
