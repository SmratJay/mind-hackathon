# Quick Start Guide - 4-Bit Processor Hackathon Project

## ✅ What's Already Done

Your complete 4-bit processor is ready! The project includes:

- ✅ **8 RTL modules** (xor_1b, fa_1b, adder_4b, alu_4b, alu_reg_4b, decoder_fsm, ram16x4_sync, simple4_proc)
- ✅ **6 testbenches** (unit tests + integration test)
- ✅ **Test program** in machine code (data/program.mem)
- ✅ **Constraint checker** (tools/check_reuse.py)
- ✅ **Test automation** (run_tests.ps1)
- ✅ **Full documentation** (README.md)

Constraint check: **PASSING** ✅ (all structural requirements verified)

## 🚀 Next Steps - Running Simulations

### Step 1: Install Icarus Verilog (Required for Simulation)

**Windows Download:**
1. Go to: http://bleez.osdn.jp/iverilog_installers/
2. Download the latest Windows installer (e.g., `iverilog-v12-20220611-x64.exe`)
3. Run installer with default settings
4. **Important**: Restart PowerShell after installation

**Verify Installation:**
```powershell
iverilog -v
```

You should see version information like "Icarus Verilog version 12.0 (s20150603-1110-g18392a46)"

### Step 2: Run Quick Unit Test

Test the XOR gate (fastest test):
```powershell
iverilog -o build/xor_1b_tb.vvp rtl/xor_1b.v testbenches/xor_1b_tb.v
vvp build/xor_1b_tb.vvp
```

Expected output:
```
===== XOR 1-bit Testbench =====
Testing truth table...
PASS: All XOR tests passed!
```

### Step 3: Run All Tests (Automated)

```powershell
.\run_tests.ps1
```

This will:
- Compile all modules automatically
- Run 5 unit tests
- Run 1 integration test
- Show pass/fail for each

Expected: **All 6 tests PASS** ✅

### Step 4: View Results

After running tests, you can examine:
- **Terminal output**: Shows which tests passed
- **Memory contents**: Integration test displays final RAM state

Expected final memory state:
- `mem[0x1] = 0x8` (after SUB operation)
- `mem[0x4] = 0xB` (after ADD operation)
- `mem[0xF] = 0xF` (after NOT operation)

## 📊 Individual Test Commands

If you want to run tests one at a time:

**XOR Gate Test:**
```powershell
iverilog -o build/xor_1b_tb.vvp rtl/xor_1b.v testbenches/xor_1b_tb.v
vvp build/xor_1b_tb.vvp
```

**1-bit Full Adder Test:**
```powershell
iverilog -o build/fa_1b_tb.vvp rtl/xor_1b.v rtl/fa_1b.v testbenches/fa_1b_tb.v
vvp build/fa_1b_tb.vvp
```

**4-bit Adder Test:**
```powershell
iverilog -o build/adder_4b_tb.vvp rtl/xor_1b.v rtl/fa_1b.v rtl/adder_4b.v testbenches/adder_4b_tb.v
vvp build/adder_4b_tb.vvp
```

**ALU Test:**
```powershell
iverilog -o build/alu_4b_tb.vvp rtl/xor_1b.v rtl/fa_1b.v rtl/adder_4b.v rtl/alu_4b.v testbenches/alu_4b_tb.v
vvp build/alu_4b_tb.vvp
```

**Registered ALU Test:**
```powershell
iverilog -o build/alu_reg_4b_tb.vvp rtl/alu_reg_4b.v testbenches/alu_reg_4b_tb.v
vvp build/alu_reg_4b_tb.vvp
```

**Full Processor Integration Test:**
```powershell
iverilog -o build/processor_tb.vvp rtl/xor_1b.v rtl/fa_1b.v rtl/adder_4b.v rtl/alu_4b.v rtl/alu_reg_4b.v rtl/decoder_fsm.v rtl/ram16x4_sync.v rtl/simple4_proc.v testbenches/processor_tb.v
vvp build/processor_tb.vvp
```

## 🎓 Understanding the Test Program

The test program executes these instructions:

```assembly
Address | Machine Code    | Assembly      | Effect
--------|-----------------|---------------|---------------------------
0x0     | 00001000101     | STO 0x4 0x5   | mem[4] = 5
0x1     | 00101000110     | ADD 0x4 0x6   | mem[4] = 5 + 6 = 11 (0xB)
0x2     | 00000011111     | STO 0x1 0xF   | mem[1] = 15 (0xF)
0x3     | 01000010111     | SUB 0x1 0x7   | mem[1] = 15 - 7 = 8
0x4     | 11011110000     | NOT 0xF 0x0   | mem[F] = ~0 = 15 (0xF)
```

## 🔍 Verifying Design Constraints

Run the constraint checker:
```powershell
python tools/check_reuse.py
```

This verifies:
- ✅ No use of `^` operator (XOR expanded to primitives)
- ✅ No use of `+` in adder_4b (structural instantiation only)
- ✅ Custom XOR instantiated in fa_1b
- ✅ fa_1b instances chained in adder_4b
- ✅ adder_4b instantiated in alu_4b
- ✅ xor_1b instantiated in alu_4b for XOR operation

## 📝 Hackathon Submission Checklist

- [x] Complete RTL implementation (8 modules)
- [x] Comprehensive test coverage (6 testbenches)
- [x] Constraint verification passing
- [x] Sample program with expected results
- [x] Automated test script
- [x] Full documentation
- [ ] Install Icarus Verilog
- [ ] Run all tests successfully
- [ ] (Optional) Generate waveforms with GTKWave

## 🎯 Expected Test Results Summary

When all tests run:

```
===== 4-bit Processor Test Suite =====

--- Unit Tests ---
Running: XOR Gate
  Compiling... OK
  Simulating... PASSED

Running: 1-bit Full Adder
  Compiling... OK
  Simulating... PASSED

Running: 4-bit Adder
  Compiling... OK
  Simulating... PASSED

Running: 4-bit ALU
  Compiling... OK
  Simulating... PASSED

Running: Registered ALU
  Compiling... OK
  Simulating... PASSED

--- Integration Test ---
Running: Processor Integration
  Compiling... OK
  Simulating... PASSED

===== Test Summary =====
Tests Run: 6
Passed: 6
Failed: 0

✅ All tests passed!
```

## 🚨 Troubleshooting

**Problem**: `iverilog: command not found`
- **Solution**: Install Icarus Verilog and restart PowerShell

**Problem**: Python script errors
- **Solution**: Ensure Python 3.7+ is installed (`python --version`)

**Problem**: Tests fail with syntax errors
- **Solution**: Check that all files in rtl/ are present and unmodified

**Problem**: Integration test shows wrong memory values
- **Solution**: This indicates a logic bug - check FSM state transitions and ALU control signals

## 🎨 Optional: View Waveforms

To generate VCD waveforms for debugging:

1. Add to testbench:
```verilog
initial begin
    $dumpfile("build/waveform.vcd");
    $dumpvars(0, module_name_tb);
end
```

2. Run test
3. View with GTKWave: `gtkwave build/waveform.vcd`

## 📚 Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `rtl/xor_1b.v` | Custom XOR gate (no ^ operator) | 17 |
| `rtl/fa_1b.v` | 1-bit full adder | 29 |
| `rtl/adder_4b.v` | 4-bit structural adder | 29 |
| `rtl/alu_4b.v` | 4-bit ALU (7 operations) | 98 |
| `rtl/alu_reg_4b.v` | Registered ALU output | 27 |
| `rtl/decoder_fsm.v` | FSM instruction decoder | 153 |
| `rtl/ram16x4_sync.v` | 16×4 synchronous RAM | 50 |
| `rtl/simple4_proc.v` | Top-level processor | 118 |

Total RTL: ~521 lines  
Total Testbenches: ~453 lines

## 🏆 Success Criteria

Your project is **submission-ready** when:

1. ✅ Constraint checker passes (already done!)
2. ⏳ All 6 tests pass when you run `.\run_tests.ps1`
3. ⏳ Integration test shows correct final memory values
4. ✅ Documentation is complete (already done!)

**Current Status**: Ready for testing! Just install Icarus Verilog and run tests.

## 💡 Tips for Demo/Presentation

1. **Show constraint checker first** - proves structural requirements
2. **Run automated test suite** - shows comprehensive verification
3. **Highlight key design choices**:
   - No primitive XOR (expanded to Boolean gates)
   - Structural adder hierarchy (not just `+` operator)
   - Proper async reset semantics
   - 5-state FSM with nested output logic
4. **Walk through sample program execution** - shows it works end-to-end

Good luck with your hackathon! 🚀
