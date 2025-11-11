# 4-Bit Load-Store Processor - Hackathon Submission

A constraint-driven 4-bit processor implementation in Verilog HDL, designed using hierarchical component reuse and strict RTL synthesis guidelines.

## 🎯 Project Overview

This project implements a complete 4-bit load-store processor with:
- **Custom ALU** supporting 7 operations (add, subtract, AND, OR, XOR, NOT, transfer)
- **5-state FSM controller** (INIT → FETCH → LOAD → EXECUTE → STORE)
- **16×4 synchronous RAM** with program/data memory
- **Hierarchical component design** enforcing structural reuse
- **Active-low asynchronous reset** for all sequential elements

### Key Design Constraints

The design enforces strict architectural constraints to demonstrate proper RTL methodology:

1. ✅ **No primitive XOR operator** (`^`) - expanded into Boolean primitives
2. ✅ **No vector addition operator** (`+`) in adders - structural instantiation only
3. ✅ **Mandatory component hierarchy**: custom XOR → 1-bit FA → 4-bit FA → ALU
4. ✅ **Asynchronous reset semantics** with proper blocking/non-blocking assignments
5. ✅ **Synchronous RAM** with registered outputs

## 📁 Project Structure

```
d:\mind-hackathon\
├── rtl/                      # Verilog RTL source files
│   ├── xor_1b.v              # Custom 1-bit XOR gate (no ^ operator)
│   ├── fa_1b.v               # 1-bit full adder (uses xor_1b)
│   ├── adder_4b.v            # 4-bit structural adder (chains fa_1b)
│   ├── alu_4b.v              # 4-bit ALU (uses adder_4b & xor_1b)
│   ├── alu_reg_4b.v          # Registered ALU output stage
│   ├── decoder_fsm.v         # Instruction decoder FSM
│   ├── ram16x4_sync.v        # 16×4 synchronous RAM
│   └── simple4_proc.v        # Top-level processor integration
├── testbenches/              # Verilog testbenches
│   ├── xor_1b_tb.v           # XOR gate tests
│   ├── fa_1b_tb.v            # 1-bit adder tests
│   ├── adder_4b_tb.v         # 4-bit adder tests
│   ├── alu_4b_tb.v           # ALU operation tests
│   ├── alu_reg_4b_tb.v       # Registered ALU tests
│   └── processor_tb.v        # Full processor integration test
├── data/
│   └── program.mem           # 11-bit machine code test program
├── tools/
│   └── check_reuse.py        # Constraint verification script
├── run_tests.ps1             # PowerShell test automation script
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Icarus Verilog** (iverilog) - for simulation
   - Windows: Download from http://bleez.osdn.jp/iverilog_installers/
   - Linux: `sudo apt-get install iverilog`
   - macOS: `brew install icarus-verilog`

2. **Python 3.7+** (optional, for constraint checking)

### Running Tests

#### Option 1: Run All Tests (PowerShell)

```powershell
.\run_tests.ps1
```

This will:
- Compile all modules
- Run unit tests (XOR, FA, Adder, ALU, Registered ALU)
- Run integration test (full processor)
- Display pass/fail summary

#### Option 2: Run Individual Tests

**Unit Tests:**
```powershell
# XOR gate test
iverilog -o build/xor_1b_tb.vvp rtl/xor_1b.v testbenches/xor_1b_tb.v
vvp build/xor_1b_tb.vvp

# 4-bit Adder test
iverilog -o build/adder_4b_tb.vvp rtl/xor_1b.v rtl/fa_1b.v rtl/adder_4b.v testbenches/adder_4b_tb.v
vvp build/adder_4b_tb.vvp

# ALU test
iverilog -o build/alu_4b_tb.vvp rtl/xor_1b.v rtl/fa_1b.v rtl/adder_4b.v rtl/alu_4b.v testbenches/alu_4b_tb.v
vvp build/alu_4b_tb.vvp
```

**Integration Test:**
```powershell
iverilog -o build/processor_tb.vvp rtl/*.v testbenches/processor_tb.v
vvp build/processor_tb.vvp
```

### Verify Structural Constraints

```powershell
python tools/check_reuse.py
```

This script validates:
- ✅ No forbidden operators (`^`, `xnor`, `+` in specific contexts)
- ✅ Required module instantiations exist
- ✅ Proper sequential logic syntax (blocking vs non-blocking assignments)

## 🏗️ Architecture Details

### Instruction Set Architecture (ISA)

11-bit instruction format: `[10:8] opcode | [7:4] op1 (address) | [3:0] op2 (data)`

| Opcode | Mnemonic | Operation | Description |
|--------|----------|-----------|-------------|
| `000` | STO | `M[op1] ← op2` | Store constant to memory |
| `001` | ADD | `M[op1] ← M[op1] + op2` | Add constant to memory |
| `010` | SUB | `M[op1] ← M[op1] - op2` | Subtract constant |
| `011` | AND | `M[op1] ← M[op1] & op2` | Logical AND |
| `100` | OR | `M[op1] ← M[op1] \| op2` | Logical OR |
| `101` | XOR | `M[op1] ← M[op1] ⊕ op2` | Logical XOR |
| `110` | NOT | `M[op1] ← ~M[op1]` | Logical NOT |

### Sample Program

The test program in `data/program.mem`:

```assembly
STO 0x4 0x5   ; mem[4] = 5
ADD 0x4 0x6   ; mem[4] = 5 + 6 = 11 (0xB)
STO 0x1 0xF   ; mem[1] = 15 (0xF)
SUB 0x1 0x7   ; mem[1] = 15 - 7 = 8
NOT 0xF 0x0   ; mem[F] = ~mem[F] = 15 (0xF)
```

**Expected Results:**
- `mem[0x1] = 0x8`
- `mem[0x4] = 0xB`
- `mem[0xF] = 0xF`

### FSM State Diagram

```
INIT → FETCH → LOAD → EXECUTE → STORE
         ↑                         |
         └─────────────────────────┘
```

- **INIT**: Reset state
- **FETCH**: Read instruction from RAM[PC], increment PC
- **LOAD**: Read operand from RAM[op1]
- **EXECUTE**: ALU performs operation
- **STORE**: Write result to RAM[op1]

## 🧪 Test Results

### Unit Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| `xor_1b` | Truth table (4 cases) | 100% |
| `fa_1b` | All 8 input combinations | 100% |
| `adder_4b` | Addition + overflow cases | Key scenarios |
| `alu_4b` | All 7 operations | 100% |
| `alu_reg_4b` | Reset + clocking | Full behavior |

### Integration Test

The processor testbench executes the sample program and validates:
- ✅ Correct FSM state transitions
- ✅ Program counter increments
- ✅ Memory operations (read/write)
- ✅ Final memory state matches expected values

## 📊 Design Statistics

- **Total Modules**: 8
- **Lines of RTL**: ~500
- **Test Lines**: ~450
- **4-bit Operations**: 7 ALU ops
- **Memory Size**: 16 words × 4 bits
- **Clock Cycles per Instruction**: ~5

## 🎓 Learning Outcomes

This project demonstrates:

1. **Hierarchical RTL Design**: Building complex systems from simple, reusable components
2. **Constraint-Driven Development**: Enforcing design rules to ensure structural correctness
3. **Synchronous Design Principles**: Proper use of clocking, reset, and register inference
4. **FSM Design**: Multi-state control logic with complex output decoding
5. **Verification Methodology**: Unit testing → Integration testing → Constraint checking

## 🔧 Customization & Extensions

### Easy Modifications

1. **Expand Memory**: Change RAM from 16×4 to 256×4 (8-bit address)
2. **Add Instructions**: Extend opcode from 3 bits to 4 bits (16 operations)
3. **Wider Data Path**: Scale from 4-bit to 8-bit or 16-bit
4. **Pipeline Stages**: Add more pipeline registers for higher frequency

### Advanced Extensions

- [ ] Add multiplication unit
- [ ] Implement conditional branching (BEQ, BNE)
- [ ] Add stack pointer and PUSH/POP
- [ ] Create Harvard architecture (separate instruction/data memory)
- [ ] Add interrupt handling logic

## 📝 Design Methodology Notes

This design follows **LLM-assisted RTL generation** best practices:

### Prompt Engineering Techniques Used

1. **Context Refresher**: Always include parent module interfaces when generating child modules
2. **Explicit Constraints**: List forbidden operators/keywords in prompts
3. **Chain-of-Thought (CoT)**: Break complex modules (FSM) into step-by-step generation
4. **Style Enforcement**: Mandate non-blocking assignments in clocked logic
5. **Verification First**: Generate testbenches immediately after modules

### Common LLM Pitfalls Avoided

- ❌ Using `^` instead of expanded XOR logic
- ❌ Using `+` operator instead of structural adder
- ❌ Mixing blocking/non-blocking assignments incorrectly
- ❌ Forgetting tri-state logic for bus arbitration
- ❌ Synchronous reset instead of asynchronous

## 🏆 Hackathon Submission Checklist

- [x] Complete RTL source code
- [x] Comprehensive testbenches
- [x] All unit tests passing
- [x] Integration test passing
- [x] Constraint verification passing
- [x] Documentation (README)
- [x] Automated test script
- [x] Sample program with expected results
- [x] Design methodology document

## 📄 License

This project is created for educational/hackathon purposes. Feel free to use, modify, and learn from it.

## 🙏 Acknowledgments

Design methodology inspired by:
- "RTL Modeling with SystemVerilog for Simulation and Synthesis" by Stuart Sutherland
- "Digital Design and Computer Architecture" by Harris & Harris
- Modern LLM-assisted HDL generation research

---

**Built for Mind Hackathon 2025**  
**Author**: [Your Name/Team]  
**Date**: November 11, 2025

For questions or issues, please refer to the detailed design document or testbench outputs.
