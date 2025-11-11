// Testbench for 4-bit Adder
// Tests key addition cases including overflow

`timescale 1ns/1ps

module adder_4b_tb;

    reg [3:0] A, B;
    reg Cin;
    wire [3:0] S;
    wire Cout;
    integer errors;
    
    // Instantiate the 4-bit adder
    adder_4b uut (
        .A(A),
        .B(B),
        .Cin(Cin),
        .S(S),
        .Cout(Cout)
    );
    
    initial begin
        $display("===== 4-bit Adder Testbench =====");
        errors = 0;
        
        // Test 1: 0 + 0 + 0 = 0
        A = 4'b0000; B = 4'b0000; Cin = 0; #10;
        if (S !== 4'b0000 || Cout !== 1'b0) begin
            $display("ERROR: 0+0+0 = %b (Cout:%b), expected 0000 (Cout:0)", S, Cout);
            errors = errors + 1;
        end
        
        // Test 2: 5 + 3 = 8
        A = 4'b0101; B = 4'b0011; Cin = 0; #10;
        if (S !== 4'b1000 || Cout !== 1'b0) begin
            $display("ERROR: 5+3 = %b (Cout:%b), expected 1000 (Cout:0)", S, Cout);
            errors = errors + 1;
        end
        
        // Test 3: 7 + 8 = 15
        A = 4'b0111; B = 4'b1000; Cin = 0; #10;
        if (S !== 4'b1111 || Cout !== 1'b0) begin
            $display("ERROR: 7+8 = %b (Cout:%b), expected 1111 (Cout:0)", S, Cout);
            errors = errors + 1;
        end
        
        // Test 4: 15 + 1 = 16 (overflow, Cout should be 1)
        A = 4'b1111; B = 4'b0001; Cin = 0; #10;
        if (S !== 4'b0000 || Cout !== 1'b1) begin
            $display("ERROR: 15+1 = %b (Cout:%b), expected 0000 (Cout:1)", S, Cout);
            errors = errors + 1;
        end
        
        // Test 5: 15 + 15 = 30 (overflow)
        A = 4'b1111; B = 4'b1111; Cin = 0; #10;
        if (S !== 4'b1110 || Cout !== 1'b1) begin
            $display("ERROR: 15+15 = %b (Cout:%b), expected 1110 (Cout:1)", S, Cout);
            errors = errors + 1;
        end
        
        // Test 6: 9 + 6 + 1 (Cin) = 16
        A = 4'b1001; B = 4'b0110; Cin = 1; #10;
        if (S !== 4'b0000 || Cout !== 1'b1) begin
            $display("ERROR: 9+6+1 = %b (Cout:%b), expected 0000 (Cout:1)", S, Cout);
            errors = errors + 1;
        end
        
        if (errors == 0) begin
            $display("PASS: All 4-bit Adder tests passed!");
        end else begin
            $display("FAIL: %0d errors found", errors);
        end
        
        $finish;
    end

endmodule
