// Module 6: 16x4 Asynchronous RAM Model (Step 6)
// Active-low chip select and read/write control
// Tri-state output for bus arbitration

module ram16x4_async(
    input wire [3:0] addr,      // 4-bit address (16 locations)
    input wire [3:0] datain,    // 4-bit data input
    input wire csn,              // Chip select (active low)
    input wire rwn,              // Read/Write control (1=read, 0=write)
    output wire [3:0] dataout   // 4-bit data output (tri-state)
);

    // Memory array: 16 locations x 4 bits
    reg [3:0] mem [0:15];
    
    // Asynchronous write operation
    always @(*) begin
        if (csn == 1'b0 && rwn == 1'b0) begin
            mem[addr] = datain;
        end
    end
    
    // Tri-state output for read operation
    // High-impedance (ZZZZ) when not selected or during write
    assign dataout = (csn == 1'b0 && rwn == 1'b1) ? mem[addr] : 4'hZ;
    
    // Initialization for simulation
    initial begin
        integer i;
        for (i = 0; i < 16; i = i + 1) begin
            mem[i] = 4'b0000;
        end
    end

endmodule
