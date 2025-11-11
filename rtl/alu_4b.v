// Module 3: 4-bit Arithmetic Logic Unit (ALU)
// Supports 8 operations controlled by S[2:0] and Cin
// Must instantiate adder_4b for arithmetic operations
// Must instantiate xor_1b for XOR logic operation
//
// Control Signal Mapping:
// S[2:0] | Cin | Function    | Implementation
// -------|-----|-------------|---------------
// 000    | 0   | F = A       | Adder with B=0000
// 001    | 0   | F = A + B   | Adder with B
// 010    | 1   | F = A - B   | Adder with ~B, Cin=1 (2's complement)
// 011    | X   | F = A & B   | Logic AND
// 100    | X   | F = A | B   | Logic OR
// 101    | X   | F = A xor B | Custom XOR instances
// 110    | X   | F = ~A      | Logic NOT

module alu_4b(
    input wire [3:0] A,
    input wire [3:0] B,
    input wire [2:0] S,
    input wire Cin,
    output reg [3:0] F,
    output reg Cout
);

    // Internal signals for adder
    wire [3:0] B_mux;        // Preprocessed B input (direct or inverted)
    wire cin_internal;        // Cin for adder
    wire [3:0] adder_result;
    wire adder_cout;
    
    // Internal signals for XOR operation
    wire xor_bit0, xor_bit1, xor_bit2, xor_bit3;
    
    // B input multiplexer: controlled by S[1] for arithmetic operations
    // S[1]=0 → B direct; S[1]=1 → B inverted (for subtraction)
    assign B_mux = (S[2:0] == 3'b010) ? ~B : B;
    
    // Cin routing: set to 1 for subtraction to complete 2's complement
    assign cin_internal = (S[2:0] == 3'b010) ? 1'b1 : Cin;
    
    // Instantiate 4-bit adder for arithmetic operations
    adder_4b adder_inst (
        .A(A),
        .B(B_mux),
        .Cin(cin_internal),
        .S(adder_result),
        .Cout(adder_cout)
    );
    
    // Instantiate four 1-bit XOR gates for XOR operation
    xor_1b xor_inst0 (.A(A[0]), .B(B[0]), .C(xor_bit0));
    xor_1b xor_inst1 (.A(A[1]), .B(B[1]), .C(xor_bit1));
    xor_1b xor_inst2 (.A(A[2]), .B(B[2]), .C(xor_bit2));
    xor_1b xor_inst3 (.A(A[3]), .B(B[3]), .C(xor_bit3));
    
    // ALU operation selector
    always @(*) begin
        case (S)
            3'b000: begin  // F = A (transfer A)
                F = A;
                Cout = 1'b0;
            end
            3'b001: begin  // F = A + B
                F = adder_result;
                Cout = adder_cout;
            end
            3'b010: begin  // F = A - B (2's complement subtraction)
                F = adder_result;
                Cout = adder_cout;
            end
            3'b011: begin  // F = A & B
                F = A & B;
                Cout = 1'b0;
            end
            3'b100: begin  // F = A | B
                F = A | B;
                Cout = 1'b0;
            end
            3'b101: begin  // F = A xor B (using custom XOR instances)
                F = {xor_bit3, xor_bit2, xor_bit1, xor_bit0};
                Cout = 1'b0;
            end
            3'b110: begin  // F = ~A (NOT A)
                F = ~A;
                Cout = 1'b0;
            end
            default: begin
                F = 4'b0000;
                Cout = 1'b0;
            end
        endcase
    end

endmodule
