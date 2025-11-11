// Module 7: Top-Level 4-bit Load-Store Processor
// Integrates: Instruction Decoder FSM, Synchronous RAM, ALU, and Registered ALU
// Implements Program Counter (PC) and data path arbitration

module simple4_proc(
    input wire clk,
    input wire reset_n     // Active-low asynchronous reset
);

    // ========== Internal Signals ==========
    
    // Program Counter
    reg [3:0] pc;
    
    // Instruction register
    reg [10:0] instruction_reg;
    wire [2:0] opcode;
    wire [3:0] op1, op2;
    
    assign opcode = instruction_reg[10:8];
    assign op1 = instruction_reg[7:4];
    assign op2 = instruction_reg[3:0];
    
    // RAM signals
    wire [3:0] ram_addr;
    wire [3:0] ram_datain;
    wire [3:0] ram_dataout;
    wire ram_csn, ram_rwn;
    wire ram_addr_sel, ram_data_sel;
    
    // ALU signals
    wire [3:0] alu_a, alu_b;
    wire [3:0] alu_f;
    wire alu_cout;
    wire [2:0] alu_s;
    wire alu_cin;
    
    // Registered ALU signals
    wire [3:0] alu_f_reg;
    wire alu_cout_reg;
    
    // FSM control signals
    wire pc_inc, pc_reset;
    
    // ========== Program Counter Logic ==========
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            pc = 4'b0000;
        end else if (pc_inc) begin
            pc <= pc + 1'b1;
        end
    end
    
    // ========== Instruction Register ==========
    // Latch instruction during FETCH state
    // NOTE: Real implementation would need 3 consecutive fetches for 11-bit instruction
    // or wider RAM. For now, assuming instruction is pre-loaded
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            instruction_reg <= 11'b0;
        end else if (!ram_csn && ram_rwn && !ram_addr_sel) begin
            // During FETCH: csn=0, rwn=1, addr_sel=0 (PC)
            // In real design: would fetch 11 bits over multiple cycles
            // For testbench: instruction should be pre-loaded or fetched properly
            instruction_reg <= instruction_reg; // Placeholder - to be loaded by testbench
        end
    end
    
    // ========== Address Multiplexer ==========
    // Select between PC (for instruction fetch) and op1 (for data access)
    assign ram_addr = ram_addr_sel ? op1 : pc;
    
    // ========== Data Input Multiplexer ==========
    // Select between op2 (constant) and ALU registered output
    assign ram_datain = ram_data_sel ? alu_f_reg : op2;
    
    // ========== ALU Input Assignment ==========
    // ALU A input: data read from RAM (memory operand)
    // ALU B input: op2 (immediate constant)
    assign alu_a = ram_dataout;
    assign alu_b = op2;
    
    // ========== Module Instantiations ==========
    
    // Instruction Decoder FSM
    decoder_fsm fsm_inst (
        .clk(clk),
        .reset_n(reset_n),
        .instruction(instruction_reg),
        .ram_csn(ram_csn),
        .ram_rwn(ram_rwn),
        .ram_addr_sel(ram_addr_sel),
        .ram_data_sel(ram_data_sel),
        .alu_s(alu_s),
        .alu_cin(alu_cin),
        .pc_inc(pc_inc),
        .pc_reset(pc_reset)
    );
    
    // Synchronous RAM (16x4) - Step 8
    ram16x4_sync ram_inst (
        .clk(clk),
        .reset_n(reset_n),
        .addr(ram_addr),
        .datain(ram_datain),
        .csn(ram_csn),
        .rwn(ram_rwn),
        .dataout(ram_dataout)
    );
    
    // 4-bit ALU (combinational)
    alu_4b alu_inst (
        .A(alu_a),
        .B(alu_b),
        .S(alu_s),
        .Cin(alu_cin),
        .F(alu_f),
        .Cout(alu_cout)
    );
    
    // Registered ALU output stage
    alu_reg_4b alu_reg_inst (
        .clk(clk),
        .reset_n(reset_n),
        .alu_f_in(alu_f),
        .alu_cout_in(alu_cout),
        .f(alu_f_reg),
        .cout(alu_cout_reg)
    );

endmodule
