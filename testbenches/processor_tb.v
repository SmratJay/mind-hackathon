// Integration Testbench for 4-bit Processor
// Tests the complete processor executing the sample program

`timescale 1ns/1ps

module processor_tb;

    reg clk, reset_n;
    integer cycle_count;
    
    // Instantiate the processor
    simple4_proc uut (
        .clk(clk),
        .reset_n(reset_n)
    );
    
    // Clock generation (20ns period = 50MHz)
    initial begin
        clk = 0;
        forever #10 clk = ~clk;
    end
    
    initial begin
        $display("===== 4-bit Processor Integration Test =====");
        $display("Loading program and initializing...");
        
        // Initialize memory with program
        // Note: In the actual design, program would be loaded via $readmemb
        // For this simulation, we'll manually initialize key memory locations
        
        // Initialize data memory locations that will be used
        #1;
        uut.ram_inst.mem[4] = 4'b0000;  // Memory[0x4] starts at 0
        uut.ram_inst.mem[1] = 4'b0000;  // Memory[0x1] starts at 0
        uut.ram_inst.mem[15] = 4'b0000; // Memory[0xF] starts at 0
        
        // Load the test program into instruction memory
        // NOTE: This is a simplified model - the actual processor needs
        // a proper instruction fetch mechanism for 11-bit instructions
        // For demo purposes, we're assuming the FSM can decode properly
        
        cycle_count = 0;
        
        // Apply reset
        reset_n = 0;
        #50;
        reset_n = 1;
        $display("Reset released, processor starting...");
        
        // Run for enough cycles to execute the program
        // Each instruction takes ~5 cycles (FETCH, LOAD, EXECUTE, STORE)
        // 5 instructions × 5 cycles = 25 cycles + margin
        repeat(50) begin
            @(posedge clk);
            cycle_count = cycle_count + 1;
            
            // Monitor key signals
            if (cycle_count % 10 == 0) begin
                $display("Cycle %0d: PC=%h, State=%b", 
                         cycle_count, uut.pc, uut.fsm_inst.current_state);
            end
        end
        
        $display("\n===== Program Execution Complete =====");
        $display("Checking final memory state...");
        
        // Expected results based on the program:
        // 1. STO 0x4 0x5  → mem[4] = 5
        // 2. ADD 0x4 0x6  → mem[4] = 5 + 6 = 11 (0xB)
        // 3. STO 0x1 0xF  → mem[1] = 15 (0xF)
        // 4. SUB 0x1 0x7  → mem[1] = 15 - 7 = 8
        // 5. NOT 0xF 0x0  → mem[F] = ~mem[F] = ~0 = 15 (0xF)
        
        $display("\nMemory Contents:");
        $display("mem[0x1] = %h (expected: 0x8)", uut.ram_inst.mem[1]);
        $display("mem[0x4] = %h (expected: 0xB)", uut.ram_inst.mem[4]);
        $display("mem[0xF] = %h (expected: 0xF)", uut.ram_inst.mem[15]);
        
        // Verify results
        if (uut.ram_inst.mem[1] == 4'h8 && 
            uut.ram_inst.mem[4] == 4'hB &&
            uut.ram_inst.mem[15] == 4'hF) begin
            $display("\n*** PASS: Processor executed program correctly! ***");
        end else begin
            $display("\n*** FAIL: Processor results incorrect ***");
        end
        
        $display("\nAll memory locations:");
        for (integer i = 0; i < 16; i = i + 1) begin
            $display("mem[%h] = %h", i, uut.ram_inst.mem[i]);
        end
        
        $finish;
    end
    
    // Timeout watchdog
    initial begin
        #10000;
        $display("ERROR: Simulation timeout!");
        $finish;
    end

endmodule
