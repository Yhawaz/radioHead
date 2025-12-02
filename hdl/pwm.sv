module pwm(   input wire clk,
              input wire rst,
              input wire [31:0] data_in,
              input wire valid_data_in,
              input wire [3:0] sh_amt,
              output logic sig_out);
 
    logic [31:0] count;
    logic [7:0] cur_dc;
    logic [7:0] shifted_dc;
    counter mc (.clk(clk),
                .rst(rst),
                .period(255),
                .count(count));

    assign shifted_dc = cur_dc >> 2*sh_amt;


    always_ff @(posedge clk)begin
	if(rst)begin
	   cur_dc <= 0;
	end else begin
	   if(count == 254)begin
		cur_dc <= shifted_dc;
	   end
	end

    end	    
    assign sig_out = count<cur_dc; //very simple threshold check
endmodule
