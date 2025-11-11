// Module 1: 1-bit XOR Gate (Non-Primitive Implementation)
// Constraint: Must NOT use the Verilog xor operator (^) or xnor
// Implementation uses only primitive Boolean operators: ~, &, |
// Boolean Expression: C = (A & ~B) | (~A & B)

module xor_1b(
    input wire A,
    input wire B,
    output wire C
);

    // XOR function expanded into primitive gates
    // We intentionally expand XOR to ensure structural reuse hierarchy
    assign C = (A & ~B) | (~A & B);

endmodule
