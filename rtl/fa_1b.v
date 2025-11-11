// Module 2a: 1-bit Full Adder
// Must instantiate custom xor_1b for sum calculation
// Sum: S = A xor B xor Cin
// Carry: Cout = (A & B) | (Cin & (A xor B))

module fa_1b(
    input wire A,
    input wire B,
    input wire Cin,
    output wire S,
    output wire Cout
);

    // Internal wires
    wire xor_ab;      // A xor B
    wire xor_ab_cin;  // (A xor B) xor Cin = Sum
    
    // Instantiate custom XOR gates for sum calculation
    xor_1b xor0 (.A(A), .B(B), .C(xor_ab));
    xor_1b xor1 (.A(xor_ab), .B(Cin), .C(S));
    
    // Carry logic using primitive operators
    // Cout = (A & B) | (Cin & (A xor B))
    assign Cout = (A & B) | (Cin & xor_ab);

endmodule
