// Testbench for 4-bit ALU
// Tests all operations: transfer, add, subtract, AND, OR, XOR, NOT

`timescale 1ns/1ps

module alu_4b_tb;

    reg [3:0] A, B;
    reg [2:0] S;
    reg Cin;
    wire [3:0] F;
    wire Cout;
    integer errors;
    
    // Instantiate the ALU
    alu_4b uut (
        .A(A),
        .B(B),
        .S(S),
        .Cin(Cin),
        .F(F),
        .Cout(Cout)
    );
    
    initial begin
        $display("===== 4-bit ALU Testbench =====");
        errors = 0;
        
        A = 4'b1010;  // A = 10
        B = 4'b0110;  // B = 6
        
        // Test 1: Transfer A (S=000)
        S = 3'b000; Cin = 0; #10;
        if (F !== 4'b1010) begin
            $display("ERROR: Transfer A = %b, expected 1010", F);
            errors = errors + 1;
        end else begin
            $display("PASS: Transfer A = %b", F);
        end
        
        // Test 2: A + B (S=001)
        S = 3'b001; Cin = 0; #10;
        if (F !== 4'b0000 || Cout !== 1'b1) begin  // 10+6=16, overflow
            $display("ERROR: A+B = %b (Cout:%b), expected 0000 (Cout:1)", F, Cout);
            errors = errors + 1;
        end else begin
            $display("PASS: A+B = %b (Cout:%b) [10+6=16, overflow]", F, Cout);
        end
        
        // Test 3: A - B (S=010)
        S = 3'b010; Cin = 1; #10;
        if (F !== 4'b0100) begin  // 10-6=4
            $display("ERROR: A-B = %b, expected 0100", F);
            errors = errors + 1;
        end else begin
            $display("PASS: A-B = %b [10-6=4]", F);
        end
        
        // Test 4: A AND B (S=011)
        S = 3'b011; Cin = 0; #10;
        if (F !== 4'b0010) begin  // 1010 & 0110 = 0010
            $display("ERROR: A AND B = %b, expected 0010", F);
            errors = errors + 1;
        end else begin
            $display("PASS: A AND B = %b", F);
        end
        
        // Test 5: A OR B (S=100)
        S = 3'b100; Cin = 0; #10;
        if (F !== 4'b1110) begin  // 1010 | 0110 = 1110
            $display("ERROR: A OR B = %b, expected 1110", F);
            errors = errors + 1;
        end else begin
            $display("PASS: A OR B = %b", F);
        end
        
        // Test 6: A XOR B (S=101)
        S = 3'b101; Cin = 0; #10;
        if (F !== 4'b1100) begin  // 1010 ^ 0110 = 1100
            $display("ERROR: A XOR B = %b, expected 1100", F);
            errors = errors + 1;
        end else begin
            $display("PASS: A XOR B = %b", F);
        end
        
        // Test 7: NOT A (S=110)
        S = 3'b110; Cin = 0; #10;
        if (F !== 4'b0101) begin  // ~1010 = 0101
            $display("ERROR: NOT A = %b, expected 0101", F);
            errors = errors + 1;
        end else begin
            $display("PASS: NOT A = %b", F);
        end
        
        // Additional subtraction test: B - A (should borrow)
        A = 4'b0011; B = 4'b0111;  // 3 and 7
        S = 3'b010; Cin = 1; #10;  // 7 - 3 = 4
        if (F !== 4'b0100) begin
            $display("ERROR: 7-3 = %b, expected 0100", F);
            errors = errors + 1;
        end else begin
            $display("PASS: 7-3 = %b", F);
        end
        
        if (errors == 0) begin
            $display("PASS: All ALU tests passed!");
        end else begin
            $display("FAIL: %0d errors found", errors);
        end
        
        $finish;
    end

endmodule
