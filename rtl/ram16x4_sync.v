// Module 8: Synchronous 16x4 RAM
// Synchronous read and write operations on clock edge
// Supports initialization via $readmemb for testbench program loading

module ram16x4_sync(
    input wire clk,
    input wire reset_n,
    input wire [3:0] addr,      // 4-bit address (16 locations)
    input wire [3:0] datain,    // 4-bit data input
    input wire csn,              // Chip select (active low)
    input wire rwn,              // Read/Write control (1=read, 0=write)
    output wire [3:0] dataout   // 4-bit data output
);

    // Memory array: 16 locations x 4 bits
    reg [3:0] mem [0:15];
    
    // Internal output register for synchronous read
    reg [3:0] dout_reg;
    
    // Synchronous write operation
    always @(posedge clk) begin
        if (csn == 1'b0 && rwn == 1'b0) begin
            // Write data to memory when selected and in write mode
            mem[addr] <= datain;
        end
    end
    
    // Synchronous read operation
    always @(posedge clk) begin
        if (csn == 1'b0 && rwn == 1'b1) begin
            // Latch read data into output register when selected and in read mode
            dout_reg <= mem[addr];
        end
    end
    
    // Continuous output from registered data
    assign dataout = dout_reg;
    
    // Initialization for simulation (load program memory)
    // Use $readmemb("program.mem", mem) in testbench or here for convenience
    initial begin
        // Initialize all memory to zero
        integer i;
        for (i = 0; i < 16; i = i + 1) begin
            mem[i] = 4'b0000;
        end
        // Program memory will be loaded by testbench
    end

endmodule
