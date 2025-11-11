// Testbench for 1-bit XOR gate
// Validates all 4 input combinations against truth table

`timescale 1ns/1ps

module xor_1b_tb;

    reg A, B;
    wire C;
    integer errors;
    
    // Instantiate the XOR gate
    xor_1b uut (
        .A(A),
        .B(B),
        .C(C)
    );
    
    initial begin
        $display("===== XOR 1-bit Testbench =====");
        $display("Testing truth table...");
        errors = 0;
        
        // Test case 1: 0 xor 0 = 0
        A = 0; B = 0; #10;
        if (C !== 1'b0) begin
            $display("ERROR: 0 xor 0 = %b (expected 0)", C);
            errors = errors + 1;
        end
        
        // Test case 2: 0 xor 1 = 1
        A = 0; B = 1; #10;
        if (C !== 1'b1) begin
            $display("ERROR: 0 xor 1 = %b (expected 1)", C);
            errors = errors + 1;
        end
        
        // Test case 3: 1 xor 0 = 1
        A = 1; B = 0; #10;
        if (C !== 1'b1) begin
            $display("ERROR: 1 xor 0 = %b (expected 1)", C);
            errors = errors + 1;
        end
        
        // Test case 4: 1 xor 1 = 0
        A = 1; B = 1; #10;
        if (C !== 1'b0) begin
            $display("ERROR: 1 xor 1 = %b (expected 0)", C);
            errors = errors + 1;
        end
        
        // Summary
        if (errors == 0) begin
            $display("PASS: All XOR tests passed!");
        end else begin
            $display("FAIL: %0d errors found", errors);
        end
        
        $finish;
    end

endmodule
