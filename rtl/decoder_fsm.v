// Module 5: Instruction Decoder FSM (Control Unit)
// Five-state machine: INIT → FETCH → LOAD → EXECUTE → STORE → (loop to FETCH)
// Decodes 11-bit instructions and generates control signals for RAM and ALU
//
// Instruction Format: [10:8] opcode, [7:4] op1 (address), [3:0] op2 (data/address)
//
// Opcode Encoding:
// 000 - STO: Store constant
// 001 - ADD: Add constant
// 010 - SUB: Subtract constant
// 011 - AND: Logical AND
// 100 - OR:  Logical OR
// 101 - XOR: Logical XOR
// 110 - NOT: Logical NOT

module decoder_fsm(
    input wire clk,
    input wire reset_n,              // Active-low asynchronous reset
    input wire [10:0] instruction,   // 11-bit instruction from RAM
    
    // RAM control signals
    output reg ram_csn,              // Chip select (active low)
    output reg ram_rwn,              // Read/Write (1=read, 0=write)
    output reg ram_addr_sel,         // Address mux select (0=PC, 1=op1)
    output reg ram_data_sel,         // Data input mux select (0=op2, 1=ALU_out)
    
    // ALU control signals
    output reg [2:0] alu_s,          // ALU operation select
    output reg alu_cin,              // ALU carry in
    
    // Program counter control
    output reg pc_inc,               // Increment PC
    output reg pc_reset              // Reset PC (not used, kept for future)
);

    // State encoding
    localparam [2:0] INIT    = 3'b000,
                     FETCH   = 3'b001,
                     LOAD    = 3'b010,
                     EXECUTE = 3'b011,
                     STORE   = 3'b100;
    
    // State registers
    reg [2:0] current_state, next_state;
    
    // Instruction decode
    wire [2:0] opcode;
    wire [3:0] op1, op2;
    
    assign opcode = instruction[10:8];
    assign op1 = instruction[7:4];
    assign op2 = instruction[3:0];
    
    // State register with asynchronous reset
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n)
            current_state <= INIT;
        else
            current_state <= next_state;
    end
    
    // Next state combinational logic
    always @(*) begin
        case (current_state)
            INIT:    next_state = FETCH;
            FETCH:   next_state = LOAD;
            LOAD:    next_state = EXECUTE;
            EXECUTE: next_state = STORE;
            STORE:   next_state = FETCH;
            default: next_state = INIT;
        endcase
    end
    
    // Output logic (combinational)
    always @(*) begin
        // Default values
        ram_csn = 1'b1;       // Chip not selected
        ram_rwn = 1'b1;       // Read mode
        ram_addr_sel = 1'b0;  // PC as address
        ram_data_sel = 1'b0;  // op2 as data
        alu_s = 3'b000;       // ALU transfer A
        alu_cin = 1'b0;
        pc_inc = 1'b0;
        pc_reset = 1'b0;
        
        case (current_state)
            INIT: begin
                // Reset/idle state
                ram_csn = 1'b1;
                ram_rwn = 1'b1;
                pc_reset = 1'b1;
            end
            
            FETCH: begin
                // Fetch instruction from RAM at address PC
                ram_csn = 1'b0;       // Enable RAM
                ram_rwn = 1'b1;       // Read mode
                ram_addr_sel = 1'b0;  // Use PC as address
                pc_inc = 1'b1;        // Increment PC for next instruction
            end
            
            LOAD: begin
                // Read operand from RAM at address op1
                ram_csn = 1'b0;       // Enable RAM
                ram_rwn = 1'b1;       // Read mode
                ram_addr_sel = 1'b1;  // Use op1 as address
            end
            
            EXECUTE: begin
                // ALU performs operation based on opcode
                ram_csn = 1'b1;       // RAM idle
                ram_rwn = 1'b1;       // Read mode (idle)
                
                // Decode opcode to ALU control signals
                case (opcode)
                    3'b000: begin  // STO: Transfer op2 (constant)
                        alu_s = 3'b000;   // F = A (but A will be op2)
                        alu_cin = 1'b0;
                    end
                    3'b001: begin  // ADD: A + op2
                        alu_s = 3'b001;   // F = A + B
                        alu_cin = 1'b0;
                    end
                    3'b010: begin  // SUB: A - op2
                        alu_s = 3'b010;   // F = A - B
                        alu_cin = 1'b1;   // 2's complement
                    end
                    3'b011: begin  // AND: A & op2
                        alu_s = 3'b011;   // F = A & B
                        alu_cin = 1'b0;
                    end
                    3'b100: begin  // OR: A | op2
                        alu_s = 3'b100;   // F = A | B
                        alu_cin = 1'b0;
                    end
                    3'b101: begin  // XOR: A xor op2
                        alu_s = 3'b101;   // F = A xor B
                        alu_cin = 1'b0;
                    end
                    3'b110: begin  // NOT: ~A
                        alu_s = 3'b110;   // F = ~A
                        alu_cin = 1'b0;
                    end
                    default: begin
                        alu_s = 3'b000;
                        alu_cin = 1'b0;
                    end
                endcase
            end
            
            STORE: begin
                // Write ALU result back to RAM at address op1
                ram_csn = 1'b0;       // Enable RAM
                ram_rwn = 1'b0;       // Write mode
                ram_addr_sel = 1'b1;  // Use op1 as address
                ram_data_sel = 1'b1;  // Use ALU output as data
            end
            
            default: begin
                // Default safe state
                ram_csn = 1'b1;
                ram_rwn = 1'b1;
            end
        endcase
    end

endmodule
