// Module 2b: 4-bit Full Adder (Structural Implementation)
// Must instantiate four 1-bit full adders (fa_1b)
// Carries are chained: cout[i] feeds cin[i+1]
// Constraint: Must NOT use Verilog + operator for vector addition

module adder_4b(
    input wire [3:0] A,
    input wire [3:0] B,
    input wire Cin,
    output wire [3:0] S,
    output wire Cout
);

    // Internal carry chain
    wire c0, c1, c2, c3;
    
    // Structural instantiation of four 1-bit full adders
    // fa0 is the least significant bit (LSB)
    fa_1b fa0 (.A(A[0]), .B(B[0]), .Cin(Cin),  .S(S[0]), .Cout(c0));
    fa_1b fa1 (.A(A[1]), .B(B[1]), .Cin(c0),   .S(S[1]), .Cout(c1));
    fa_1b fa2 (.A(A[2]), .B(B[2]), .Cin(c1),   .S(S[2]), .Cout(c2));
    fa_1b fa3 (.A(A[3]), .B(B[3]), .Cin(c2),   .S(S[3]), .Cout(c3));
    
    // Final carry out
    assign Cout = c3;

endmodule
