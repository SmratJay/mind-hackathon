// Testbench for Registered ALU
// Tests synchronous behavior with asynchronous reset

`timescale 1ns/1ps

module alu_reg_4b_tb;

    reg clk, reset_n;
    reg [3:0] alu_f_in;
    reg alu_cout_in;
    wire [3:0] f;
    wire cout;
    integer errors;
    
    // Instantiate the registered ALU
    alu_reg_4b uut (
        .clk(clk),
        .reset_n(reset_n),
        .alu_f_in(alu_f_in),
        .alu_cout_in(alu_cout_in),
        .f(f),
        .cout(cout)
    );
    
    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;  // 10ns period
    end
    
    initial begin
        $display("===== Registered ALU Testbench =====");
        errors = 0;
        
        // Initialize inputs
        alu_f_in = 4'b0000;
        alu_cout_in = 1'b0;
        reset_n = 1;
        
        // Test 1: Asynchronous reset
        #2;
        reset_n = 0;  // Assert reset
        #15;
        if (f !== 4'b0000 || cout !== 1'b0) begin
            $display("ERROR: Reset failed - f:%b cout:%b", f, cout);
            errors = errors + 1;
        end else begin
            $display("PASS: Asynchronous reset working");
        end
        
        // Release reset
        reset_n = 1;
        #10;
        
        // Test 2: Register input on clock edge
        alu_f_in = 4'b1010;
        alu_cout_in = 1'b1;
        #10;  // Wait for clock edge
        if (f !== 4'b1010 || cout !== 1'b1) begin
            $display("ERROR: Register failed - f:%b cout:%b (expected 1010, 1)", f, cout);
            errors = errors + 1;
        end else begin
            $display("PASS: Registered 1010 correctly");
        end
        
        // Test 3: One-cycle latency
        alu_f_in = 4'b0101;
        alu_cout_in = 1'b0;
        #3;  // Before clock edge
        if (f !== 4'b1010) begin  // Should still hold old value
            $display("ERROR: Output changed before clock edge");
            errors = errors + 1;
        end
        #7;  // After clock edge
        if (f !== 4'b0101 || cout !== 1'b0) begin
            $display("ERROR: New value not latched - f:%b cout:%b", f, cout);
            errors = errors + 1;
        end else begin
            $display("PASS: One-cycle latency verified");
        end
        
        // Test 4: Reset overrides during clock
        alu_f_in = 4'b1111;
        alu_cout_in = 1'b1;
        #2;
        reset_n = 0;  // Assert reset asynchronously
        #3;
        if (f !== 4'b0000 || cout !== 1'b0) begin
            $display("ERROR: Async reset during operation failed");
            errors = errors + 1;
        end else begin
            $display("PASS: Async reset overrides clock");
        end
        
        reset_n = 1;
        #20;
        
        if (errors == 0) begin
            $display("PASS: All Registered ALU tests passed!");
        end else begin
            $display("FAIL: %0d errors found", errors);
        end
        
        $finish;
    end

endmodule
