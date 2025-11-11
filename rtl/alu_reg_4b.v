// Module 4: Registered ALU Output Stage
// Synchronizes ALU outputs to clock with active-low asynchronous reset
// Critical: Uses blocking assignments (=) in reset branch
//          Uses non-blocking assignments (<=) in clocked branch

module alu_reg_4b(
    input wire clk,
    input wire reset_n,           // Active-low asynchronous reset
    input wire [3:0] alu_f_in,    // Combinational ALU result input
    input wire alu_cout_in,        // Combinational ALU carry input
    output reg [3:0] f,            // Registered result output
    output reg cout                // Registered carry output
);

    // Sequential logic with asynchronous reset
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            // Asynchronous reset: use blocking assignments for immediate effect
            f = 4'b0000;
            cout = 1'b0;
        end else begin
            // Normal operation: use non-blocking assignments for proper register behavior
            f <= alu_f_in;
            cout <= alu_cout_in;
        end
    end

endmodule
