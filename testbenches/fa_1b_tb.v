// Testbench for 1-bit Full Adder
// Tests all 8 combinations of A, B, Cin

`timescale 1ns/1ps

module fa_1b_tb;

    reg A, B, Cin;
    wire S, Cout;
    integer errors;
    
    // Instantiate the full adder
    fa_1b uut (
        .A(A),
        .B(B),
        .Cin(Cin),
        .S(S),
        .Cout(Cout)
    );
    
    initial begin
        $display("===== 1-bit Full Adder Testbench =====");
        errors = 0;
        
        // Test all 8 combinations
        A = 0; B = 0; Cin = 0; #10;
        if (S !== 1'b0 || Cout !== 1'b0) begin
            $display("ERROR: 0+0+0 = S:%b Cout:%b (expected S:0 Cout:0)", S, Cout);
            errors = errors + 1;
        end
        
        A = 0; B = 0; Cin = 1; #10;
        if (S !== 1'b1 || Cout !== 1'b0) begin
            $display("ERROR: 0+0+1 = S:%b Cout:%b (expected S:1 Cout:0)", S, Cout);
            errors = errors + 1;
        end
        
        A = 0; B = 1; Cin = 0; #10;
        if (S !== 1'b1 || Cout !== 1'b0) begin
            $display("ERROR: 0+1+0 = S:%b Cout:%b (expected S:1 Cout:0)", S, Cout);
            errors = errors + 1;
        end
        
        A = 0; B = 1; Cin = 1; #10;
        if (S !== 1'b0 || Cout !== 1'b1) begin
            $display("ERROR: 0+1+1 = S:%b Cout:%b (expected S:0 Cout:1)", S, Cout);
            errors = errors + 1;
        end
        
        A = 1; B = 0; Cin = 0; #10;
        if (S !== 1'b1 || Cout !== 1'b0) begin
            $display("ERROR: 1+0+0 = S:%b Cout:%b (expected S:1 Cout:0)", S, Cout);
            errors = errors + 1;
        end
        
        A = 1; B = 0; Cin = 1; #10;
        if (S !== 1'b0 || Cout !== 1'b1) begin
            $display("ERROR: 1+0+1 = S:%b Cout:%b (expected S:0 Cout:1)", S, Cout);
            errors = errors + 1;
        end
        
        A = 1; B = 1; Cin = 0; #10;
        if (S !== 1'b0 || Cout !== 1'b1) begin
            $display("ERROR: 1+1+0 = S:%b Cout:%b (expected S:0 Cout:1)", S, Cout);
            errors = errors + 1;
        end
        
        A = 1; B = 1; Cin = 1; #10;
        if (S !== 1'b1 || Cout !== 1'b1) begin
            $display("ERROR: 1+1+1 = S:%b Cout:%b (expected S:1 Cout:1)", S, Cout);
            errors = errors + 1;
        end
        
        if (errors == 0) begin
            $display("PASS: All 1-bit Full Adder tests passed!");
        end else begin
            $display("FAIL: %0d errors found", errors);
        end
        
        $finish;
    end

endmodule
