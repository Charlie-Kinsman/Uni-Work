//Fourth draft of Verilog code. A lot of the dummy variables have been changed for real ones. The conversion from voltage to temperature and voltage to temperature is for the lab thermistor (PT100) and the lab TEC (2MC10-081-20).
//The temperature to voltage conversion is now using lines of best fit rather than a square root.
//The algorithm takes in the 8-bit data from the ADC, converts it to a temperature to make sure the input of the PID algorith has the same response as the output, the output is then converted to a voltage for the TEC. This was then converted to a PWM signal which is then sent to the DAC.
//This is pieces of code I either found and edited or some original stuff.


//Read ADC
module uart_rx 
  #(parameter CLKS_PER_BIT)
  (
   input        i_Clock,
   input        i_Rx_Serial,
   output       o_Rx_DV,
   output [7:0] o_Rx_Byte
   );
    
  parameter s_IDLE         = 3'b000;
  parameter s_RX_START_BIT = 3'b001;
  parameter s_RX_DATA_BITS = 3'b010;
  parameter s_RX_STOP_BIT  = 3'b011;
  parameter s_CLEANUP      = 3'b100;
   
  reg           r_Rx_Data_R = 1'b1;
  reg           r_Rx_Data   = 1'b1;
   
  reg [7:0]     r_Clock_Count = 0;
  reg [2:0]     r_Bit_Index   = 0; //8 bits total
  reg [7:0]     r_Rx_Byte     = 0;
  reg           r_Rx_DV       = 0;
  reg [2:0]     r_SM_Main     = 0;
   
  // Purpose: Double-register the incoming data.
  // This allows it to be used in the UART RX Clock Domain.
  // (It removes problems caused by metastability)
  always @(posedge i_Clock)
    begin
      r_Rx_Data_R <= i_Rx_Serial;
      r_Rx_Data   <= r_Rx_Data_R;
    end
   
   
  // Purpose: Control RX state machine
  always @(posedge i_Clock)
    begin
       
      case (r_SM_Main)
        s_IDLE :
          begin
            r_Rx_DV       <= 1'b0;
            r_Clock_Count <= 0;
            r_Bit_Index   <= 0;
             
            if (r_Rx_Data == 1'b0)          // Start bit detected
              r_SM_Main <= s_RX_START_BIT;
            else
              r_SM_Main <= s_IDLE;
          end
         
        // Check middle of start bit to make sure it's still low
        s_RX_START_BIT :
          begin
            if (r_Clock_Count == (CLKS_PER_BIT-1)/2)
              begin
                if (r_Rx_Data == 1'b0)
                  begin
                    r_Clock_Count <= 0;  // reset counter, found the middle
                    r_SM_Main     <= s_RX_DATA_BITS;
                  end
                else
                  r_SM_Main <= s_IDLE;
              end
            else
              begin
                r_Clock_Count <= r_Clock_Count + 1;
                r_SM_Main     <= s_RX_START_BIT;
              end
          end // case: s_RX_START_BIT
         
         
        // Wait CLKS_PER_BIT-1 clock cycles to sample serial data
        s_RX_DATA_BITS :
          begin
            if (r_Clock_Count < CLKS_PER_BIT-1)
              begin
                r_Clock_Count <= r_Clock_Count + 1;
                r_SM_Main     <= s_RX_DATA_BITS;
              end
            else
              begin
                r_Clock_Count          <= 0;
                r_Rx_Byte[r_Bit_Index] <= r_Rx_Data;
                 
                // Check if we have received all bits
                if (r_Bit_Index < 7)
                  begin
                    r_Bit_Index <= r_Bit_Index + 1;
                    r_SM_Main   <= s_RX_DATA_BITS;
                  end
                else
                  begin
                    r_Bit_Index <= 0;
                    r_SM_Main   <= s_RX_STOP_BIT;
                  end
              end
          end // case: s_RX_DATA_BITS
     
     
        // Receive Stop bit.  Stop bit = 1
        s_RX_STOP_BIT :
          begin
            // Wait CLKS_PER_BIT-1 clock cycles for Stop bit to finish
            if (r_Clock_Count < CLKS_PER_BIT-1)
              begin
                r_Clock_Count <= r_Clock_Count + 1;
                r_SM_Main     <= s_RX_STOP_BIT;
              end
            else
              begin
                r_Rx_DV       <= 1'b1;
                r_Clock_Count <= 0;
                r_SM_Main     <= s_CLEANUP;
              end
          end // case: s_RX_STOP_BIT
     
         
        // Stay here 1 clock
        s_CLEANUP :
          begin
            r_SM_Main <= s_IDLE;
            r_Rx_DV   <= 1'b0;
          end
         
         
        default :
          r_SM_Main <= s_IDLE;
         
      endcase
    end   
   
  assign o_Rx_DV   = r_Rx_DV;
  assign o_Rx_Byte = r_Rx_Byte;
   
endmodule // uart_rx


//Take digital voltage input and convert to numerical temperature
module V_T #(B=7)
(output signed [B:0] temp_in,
input signed [B:0] o_Rx_Byte);
parameter grad = -218;
parameter intercept = 318.6757;
assign temp_in <= (grad * o_Rx_Byte) + intercept;
endmodule


//Calculate the error
module error #(B=7)
(output signed [B:0] error,
input signed [B:0] temp_in);
parameter sp = 253;
assign error <= temp_in - sp;
endmodule

//PID algorithm with dummy variables
module PID #(B=7)(
    output signed [B:0] temp_out,
input signed [B:0] temp_in,
input signed [B:0] error,
input clk,
input reset);
parameter k_p=1;
parameter k_i=2;
parameter k_d=3;
reg signed [B:0] temp_prev;
reg signed [B:0] error_sum;
reg signed [B:0] error_prev;
assign temp_out = temp_prev - (k_p * error) - (k_i * error_sum) - ((k_d * (error_prev - error_T))
always @ (posedge clk)
       if (reset == 1) begin
           temp_prev<=temp_in;
           error_prev<=0;
           error_sum<=0
       end
       else begin
           temp_prev<=temp_out;
           error_prev<=error;
           error_sum<=error_sum + error
        end   
endmodule

//Take temperature output and convert to del_T

module T_dT #(B=7)
(output signed [B:0] del_T,
input signed [B:0] temp_out);
assign del_t <= 295 - temp_out;
endmodule

//Take change in temperature and convert to voltage
module T_V #(B=7)
(output signed [B:0] del_V,
input signed [B:0] del_T);
if (del_T<0) begin
    del_T <= -del_T
end
if ((del_T>=0) && (del_T<21)) begin
    assign del_V <= (0.066 * del_T) + 2.12
end
else if ((del_T>=21) && (del_T<35)) begin
    assign del_V <= (0.108 * del_T) + 1.236
end
else if ((del_T>=35) && (del_T<40.5)) begin
    assign del_V <= (0.209 * del_T) - 2.31
end
else if ((del_T>=40.5) && (del_T<41.8)) begin
    assign del_V <= (0.467 * del_T) - 12.745
end
else if ((del_T>=41.8) && (del_T<=42)) begin
    assign del_V <= (1.9 * del_T) - 72.65
end
if (del_T>42) begin
    assign del_V <= 7.187
end
endmodule

//Digital Voltage to PWM data
module PWM #(B=7)
(input clk,
input [B:0] del_V,
input load,
output data_ana);
reg [B:0] d;
reg [B:0] count;
reg data_ana;
always @ (posedge clk)
   if (load == 1'b1) d <= del_V;
initial count = 8'b0;
always @ (posedge clk) begin
    count <= count + 1'b1;
    if (count > d)
    data_ana <= 1'b0;
    else
    data_ana <= 1'b1; 
end
endmodule

//H-Bridge direction flow
module Hot_Cold #(B=7)
    (input [B:0] del_T,
    input clk,
    output h_pos,
    output h_neg);
    always @ (posedge clk) begin
       if (del_T >= 1'b0)
       h_pos <= 1'b1;
       h_neg <= 1'b0
       else
       h_neg <= 1'b1
       h_pos <= 1'b0
    end
endmodule

//Send to DAC
module uart_tx 
  #(parameter CLKS_PER_BIT)
  (
   input       i_Clock,
   input       i_Tx_DV,
   input [7:0] data_ana, 
   output      o_Tx_Active,
   output reg  o_Tx_Serial,
   output      o_Tx_Done);
  
  parameter s_IDLE         = 3'b000;
  parameter s_TX_START_BIT = 3'b001;
  parameter s_TX_DATA_BITS = 3'b010;
  parameter s_TX_STOP_BIT  = 3'b011;
  parameter s_CLEANUP      = 3'b100;
   
  reg [2:0]    r_SM_Main     = 0;
  reg [7:0]    r_Clock_Count = 0;
  reg [2:0]    r_Bit_Index   = 0;
  reg [7:0]    r_Tx_Data     = 0;
  reg          r_Tx_Done     = 0;
  reg          r_Tx_Active   = 0;
     
  always @(posedge i_Clock)
    begin
       
      case (r_SM_Main)
        s_IDLE :
          begin
            o_Tx_Serial   <= 1'b1;         // Drive Line High for Idle
            r_Tx_Done     <= 1'b0;
            r_Clock_Count <= 0;
            r_Bit_Index   <= 0;
             
            if (i_Tx_DV == 1'b1)
              begin
                r_Tx_Active <= 1'b1;
                r_Tx_Data   <= data_ana;
                r_SM_Main   <= s_TX_START_BIT;
              end
            else
              r_SM_Main <= s_IDLE;
          end // case: s_IDLE
         
         
        // Send out Start Bit. Start bit = 0
        s_TX_START_BIT :
          begin
            o_Tx_Serial <= 1'b0;
             
            // Wait CLKS_PER_BIT-1 clock cycles for start bit to finish
            if (r_Clock_Count < CLKS_PER_BIT-1)
              begin
                r_Clock_Count <= r_Clock_Count + 1;
                r_SM_Main     <= s_TX_START_BIT;
              end
            else
              begin
                r_Clock_Count <= 0;
                r_SM_Main     <= s_TX_DATA_BITS;
              end
          end // case: s_TX_START_BIT
         
         
        // Wait CLKS_PER_BIT-1 clock cycles for data bits to finish         
        s_TX_DATA_BITS :
          begin
            o_Tx_Serial <= r_Tx_Data[r_Bit_Index];
             
            if (r_Clock_Count < CLKS_PER_BIT-1)
              begin
                r_Clock_Count <= r_Clock_Count + 1;
                r_SM_Main     <= s_TX_DATA_BITS;
              end
            else
              begin
                r_Clock_Count <= 0;
                 
                // Check if we have sent out all bits
                if (r_Bit_Index < 7)
                  begin
                    r_Bit_Index <= r_Bit_Index + 1;
                    r_SM_Main   <= s_TX_DATA_BITS;
                  end
                else
                  begin
                    r_Bit_Index <= 0;
                    r_SM_Main   <= s_TX_STOP_BIT;
                  end
              end
          end // case: s_TX_DATA_BITS
         
         
        // Send out Stop bit.  Stop bit = 1
        s_TX_STOP_BIT :
          begin
            o_Tx_Serial <= 1'b1;
             
            // Wait CLKS_PER_BIT-1 clock cycles for Stop bit to finish
            if (r_Clock_Count < CLKS_PER_BIT-1)
              begin
                r_Clock_Count <= r_Clock_Count + 1;
                r_SM_Main     <= s_TX_STOP_BIT;
              end
            else
              begin
                r_Tx_Done     <= 1'b1;
                r_Clock_Count <= 0;
                r_SM_Main     <= s_CLEANUP;
                r_Tx_Active   <= 1'b0;
              end
          end // case: s_Tx_STOP_BIT
         
         
        // Stay here 1 clock
        s_CLEANUP :
          begin
            r_Tx_Done <= 1'b1;
            r_SM_Main <= s_IDLE;
          end
         
         
        default :
          r_SM_Main <= s_IDLE;
         
      endcase
    end
 
  assign o_Tx_Active = r_Tx_Active;
  assign o_Tx_Done   = r_Tx_Done;
   
endmodule
