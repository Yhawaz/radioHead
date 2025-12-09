//module fm_filter(     input wire clk,
//                    input wire rst,
//                    input wire validIn,
//                    input wire [31:0] dataIn,
//                    output logic validOut,
//                    output logic [31:0] dataOut
//              );
//
//    logic [31:0] sampled_data;
//
//    always_comb begin
//       dataOut = sampled_data; 
//    end
//    
//    always_ff@(posedge clk)begin
//        validOut<=validIn;
//        if(validIn)begin
//            sampled_data<=dataIn;
//        end
//    end
//
//endmodule
