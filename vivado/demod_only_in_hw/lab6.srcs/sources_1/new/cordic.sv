`timescale 1ns/1ps
module cordic #
(
        parameter integer C_S00_AXIS_TDATA_WIDTH    = 32,
        parameter integer C_M00_AXIS_TDATA_WIDTH    = 32
    )
    (
 
        // Ports of Axi Slave Bus Interface S00_AXIS
        input wire  s00_axis_aclk, s00_axis_aresetn,
        input wire  s00_axis_tlast, s00_axis_tvalid,
        input wire [C_S00_AXIS_TDATA_WIDTH-1 : 0] s00_axis_tdata,
        input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1: 0] s00_axis_tstrb,
        output logic  s00_axis_tready,
 
        // Ports of Axi Master Bus Interface M00_AXIS
        input wire  m00_axis_aclk, m00_axis_aresetn,
        input wire  m00_axis_tready,
        output logic  m00_axis_tvalid, m00_axis_tlast,
        output logic [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata,
        output logic [(C_M00_AXIS_TDATA_WIDTH/8)-1: 0] m00_axis_tstrb
    );

    // data coming in is x, y
    assign s00_axis_tready = m00_axis_tready || ~m00_axis_tvalid;

    logic signed [32:0]  x_arr [15:0];
    logic signed [32:0]  y_arr [15:0];
    logic [15:0] z_arr [15:0];

    logic [15:0] t_last_pipe,t_valid_pipe,t_strb_pipe,rotate_pipe;
    logic signed [32:0] x,real_x;
    logic signed [32:0] y,real_y;
    logic signed [15:0] z;

    logic signed [15:0] x15,y15;

    assign x15 = x[15:0];
    assign y15 = y[15:0];

    logic [15:0] cordic_angles [0:15];

    initial begin
        cordic_angles[0]  = 16'h2000;
        cordic_angles[1]  = 16'h12e4;
        cordic_angles[2]  = 16'h09fb;
        cordic_angles[3]  = 16'h0511;
        cordic_angles[4]  = 16'h028b;
        cordic_angles[5]  = 16'h0146;
        cordic_angles[6]  = 16'h00a3;
        cordic_angles[7]  = 16'h0051;
        cordic_angles[8]  = 16'h0029;
        cordic_angles[9]  = 16'h0014;
        cordic_angles[10] = 16'h000a;
        cordic_angles[11] = 16'h0005;
        cordic_angles[12] = 16'h0003;
        cordic_angles[13] = 16'h0001;
        cordic_angles[14] = 16'h0001;
        cordic_angles[15] = 16'h0000;
    end

    
    logic [63:0] magnitude;
    logic [15:0] angle;
    // 2pi = 16'b1111_1111_1111_1111
    // implict angle range must be 0, 2pi since angle is positive

    // // test bench debug
    logic [31:0] z0,z1,z2,z3,z4,z5,z6,z7,z8,z9,z10,z11,z12,z13,z14,z15;
    always_comb begin
        z0 = z_arr[0];
        z1 = z_arr[1];
        z2 = z_arr[2];
        z3 = z_arr[3];
        z4 = z_arr[4];
        z5 = z_arr[5];
        z6 = z_arr[6];
        z7 = z_arr[7];
        z8 = z_arr[8];
        z9 = z_arr[9];
        z10 = z_arr[10];
        z11 = z_arr[11];
        z12 = z_arr[12];
        z13 = z_arr[13];
        z14 = z_arr[14];
        z15 = z_arr[15];
    end

    logic rotated;
    
    logic [15:0] deg_int;

    real test;



    always_comb begin
        x = $signed(s00_axis_tdata[15:0]);
        y = $signed(s00_axis_tdata[31:16]);
        z = 0;

        // moving to Quadrant I and IV
        if( $signed(x) < 0 )begin
            // If you're in qudrants II or III, then the point must be rotated for
            // x to be greater than 0

            // rotation by 180 degrees entails flipping sign of both numbers
            // two's complement
            rotated = 1;
            real_x = -$signed(x)*32'sd39796;
            real_y = -$signed(y)*32'sd39796;
        end else begin
            rotated = 0;
            real_x = x*32'sd39796;
            real_y = y*32'sd39796;
        end

        // if(t_valid_pipe[15])begin
        //     foreach (z_arr[i]) begin
        //         deg_int = (z_arr[i] * 360) >> 16; // truncated integer degrees
        //         $write("ang[%0d]=%0d°%s", i, deg_int, (i==15) ? "\n" : ", ");
        //     end
        //     foreach (z_arr[i]) begin
        //         deg_int = (z_arr[i] * 360); // truncated integer degrees
        //         $write("z_arr[%0d]=%0d%s", i, z_arr[i], (i==15) ? "\n" : ", ");
        //     end


        // end


        // final result
        if(rotate_pipe[15] == 1'b1)begin
            // rotate by pi by adding pi to the angle
            // determine what that value is
            // angle = angle + pi
             //angle = z_arr[15] + 16'b0111_1111_1111_1111; // 15 ones
            angle = z_arr[15] - 16'h8000; // 15 ones
        end else begin
            angle = z_arr[15];
        end
        
        // pre multiply then divide????
        magnitude = (x_arr[15]) >> 16;
         // final result
        m00_axis_tdata = {angle,magnitude[15:0]};
        m00_axis_tvalid = t_valid_pipe[15];
        m00_axis_tlast = t_last_pipe[15];
        m00_axis_tstrb = t_strb_pipe[15];
    end
  
    logic last_valid;

    always_ff @(posedge s00_axis_aclk)begin
        if (s00_axis_aresetn==0)begin
            t_last_pipe <= 0;
            t_valid_pipe <= 0;
            t_strb_pipe <= 0;
            for(int i = 0; i<16; i++)begin
                rotate_pipe[i] <= 0;
                x_arr[i] <= 0;
                y_arr[i] <= 0;
                z_arr[i] <= 0;
            end
        end else begin
            if (m00_axis_tready)begin
                // base case and data intake
                if(s00_axis_tvalid && s00_axis_tready)begin
                    x_arr[0] <= real_x;
                    y_arr[0] <= real_y;
                    z_arr[0] <= 0;
                    rotate_pipe[0] <= rotated; 
                end


                t_last_pipe[0] <= s00_axis_tlast;
                t_valid_pipe[0] <= s00_axis_tvalid;
                t_strb_pipe[0] <= s00_axis_tstrb;
                
                // you must do this for each value in the pipeline
                for(int i = 0; i<15; i++)begin
                    if( $signed(y_arr[i]) > 33'sd0)begin
                        x_arr[i+1] <= $signed(x_arr[i]) + ($signed(y_arr[i]) >>> i);
                        y_arr[i+1] <= $signed(y_arr[i]) - ($signed(x_arr[i]) >>> i);
                        z_arr[i+1] <= z_arr[i] + $signed(cordic_angles[i]);
                    end else begin
                        x_arr[i+1] <= $signed(x_arr[i]) - ($signed(y_arr[i]) >>> i);
                        y_arr[i+1] <= $signed(y_arr[i]) + ($signed(x_arr[i]) >>> i);
                        z_arr[i+1] <= z_arr[i] - $signed(cordic_angles[i]);
                    end
                     // rotated logic
                    rotate_pipe[i+1] <= rotate_pipe[i];

                    // AXIS pipeline
                    t_last_pipe[i+1] <= t_last_pipe[i];
                    t_valid_pipe[i+1] <= t_valid_pipe[i];
                    t_strb_pipe[i+1] <= t_strb_pipe[i];
                end

                // $write("x - Array contents: ");
                // foreach (x_arr[i]) $write("arr[%0d]=%0d%s", i, x_arr[i], (i==15) ? "\n" : ", ");


                // $write("y - Array contents: ");
                // foreach (y_arr[i]) $write("arr[%0d]=%0d%s", i, y_arr[i], (i==15) ? "\n" : ", ");


                // imediately upstream propagate ready and then downstream valid
                // only update when down stream is ready and there is valid input data
            end


        end
    end


endmodule
