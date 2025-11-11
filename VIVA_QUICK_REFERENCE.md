# 🎯 VIVA QUICK REFERENCE CARD
## 4-Bit Processor - Essential Facts at a Glance

---

## ⚡ QUICK STATS

| Metric | Value |
|--------|-------|
| **Data Width** | 4 bits |
| **Instruction Width** | 11 bits |
| **Memory Size** | 16 words × 4 bits = 64 bits |
| **Operations** | 7 (STO, ADD, SUB, AND, OR, XOR, NOT) |
| **FSM States** | 5 (INIT → FETCH → LOAD → EXECUTE → STORE) |
| **CPI** | 4 cycles per instruction |
| **Modules** | 8 RTL files |
| **Testbenches** | 6 verification files |

---

## 📐 MODULE HIERARCHY

```
simple4_proc (Top)
├── decoder_fsm (FSM Controller)
├── ram16x4_sync (Memory - Step 8)
├── alu_4b (4-bit ALU - Step 3)
│   ├── adder_4b (4-bit Adder - Step 2)
│   │   └── fa_1b (4×) (1-bit Full Adder - Step 2)
│   │       └── xor_1b (2×) (Custom XOR - Step 1)
│   └── xor_1b (4×) (for XOR operation)
└── alu_reg_4b (Registered ALU - Step 4)

ram16x4_async (Standalone - Step 6)
```

---

## 🔢 INSTRUCTION FORMAT

```
Bit:  10  9  8 | 7  6  5  4 | 3  2  1  0
     └─────────┴────────────┴───────────┘
       Opcode      op1          op2
      (3 bits)   (4 bits)     (4 bits)
```

**Example:** `00101000110`
- `001` = ADD
- `0100` = address 4
- `0110` = constant 6
- **Meaning:** `mem[4] = mem[4] + 6`

---

## 🎮 OPERATION CODES

| Code | Op  | Pseudo-code | Example |
|------|-----|-------------|---------|
| 000  | STO | mem[op1] = op2 | `STO 4, 5` → mem[4]=5 |
| 001  | ADD | mem[op1] += op2 | `ADD 4, 6` → mem[4]+=6 |
| 010  | SUB | mem[op1] -= op2 | `SUB 1, 7` → mem[1]-=7 |
| 011  | AND | mem[op1] &= op2 | `AND 2, 15` → mem[2]&=15 |
| 100  | OR  | mem[op1] \|= op2 | `OR 3, 8` → mem[3]\|=8 |
| 101  | XOR | mem[op1] ^= op2 | `XOR 5, 12` → mem[5]^=12 |
| 110  | NOT | mem[op1] = ~mem[op1] | `NOT 15, 0` → mem[15]=~mem[15] |

---

## 🔄 FSM STATE ACTIONS

| State | RAM | Address | Data | PC | ALU | Duration |
|-------|-----|---------|------|-----|-----|----------|
| **INIT** | Idle | - | - | Reset | Idle | 1 cycle |
| **FETCH** | Read | PC | - | PC++ | Idle | 1 cycle |
| **LOAD** | Read | op1 | - | Hold | Idle | 1 cycle |
| **EXECUTE** | Idle | - | - | Hold | Compute | 1 cycle |
| **STORE** | Write | op1 | ALU | Hold | Hold | 1 cycle |

**Total:** 5 cycles (1 INIT + 4 per instruction)

---

## 🔐 KEY DESIGN CONSTRAINTS

✅ **No `^` operator** → Custom XOR: `(A & ~B) | (~A & B)`
✅ **No `+` operator** → Structural adder chain
✅ **Structural hierarchy** → All modules instantiated
✅ **Async reset** → `negedge reset_n` in sensitivity list
✅ **Tri-state outputs** → Step 6 async RAM only
✅ **Registered outputs** → Step 4 ALU, Step 8 sync RAM

---

## 🧮 ALU INTERNALS

**Subtraction (A - B):**
```
A - B = A + (~B + 1)     [2's complement]
B_mux = ~B               [Invert B]
Cin = 1                  [Add 1 for 2's complement]
Result = adder(A, ~B, 1)
```

**XOR Operation:**
```verilog
xor_1b inst0 (.A(A[0]), .B(B[0]), .C(F[0]));
xor_1b inst1 (.A(A[1]), .B(B[1]), .C(F[1]));
xor_1b inst2 (.A(A[2]), .B(B[2]), .C(F[2]));
xor_1b inst3 (.A(A[3]), .B(B[3]), .C(F[3]));
```

---

## 💾 MEMORY CONTROL SIGNALS

| Signal | Active | Values | Meaning |
|--------|--------|--------|---------|
| **csn** | Low | 0=enable, 1=disable | Chip select |
| **rwn** | - | 1=read, 0=write | Read/write control |

**Read:** `csn=0, rwn=1` → data flows from RAM
**Write:** `csn=0, rwn=0` → data flows to RAM
**Idle:** `csn=1` → RAM disabled

---

## 🔍 COMMON MISTAKES TO AVOID

❌ **"We used the + operator"** → NO! Structural adder only
❌ **"Synchronous reset"** → NO! Async reset (negedge reset_n)
❌ **"Blocking in sequential"** → Use non-blocking (<=) for flip-flops
❌ **"Step 6 has registered output"** → NO! Async RAM is combinational with tri-state
❌ **"5 cycles per instruction"** → It's 4 (FETCH-LOAD-EXEC-STORE), plus 1 INIT at start

---

## 📊 TEST PROGRAM TRACE

**Program:**
```
0: STO 0x4, 0x5    // mem[4] = 5
1: ADD 0x4, 0x6    // mem[4] = 5 + 6 = 11
2: STO 0x1, 0xF    // mem[1] = 15
3: SUB 0x1, 0x7    // mem[1] = 15 - 7 = 8
4: NOT 0xF, 0x0    // mem[15] = ~0 = 15
```

**Expected Results:**
- `mem[0x1] = 0x8` ✓
- `mem[0x4] = 0xB` ✓
- `mem[0xF] = 0xF` ✓

---

## 💡 VIVA POWER PHRASES

### When asked about XOR:
> "We implemented XOR using Boolean algebra: `C = (A & ~B) | (~A & B)`, which uses only AND, OR, and NOT operators as required. This is the sum-of-products form derived from the XOR truth table."

### When asked about subtraction:
> "Subtraction uses 2's complement arithmetic: `A - B = A + (~B + 1)`. We invert B and set Cin=1 to add the +1, then use our structural adder. This is standard in digital systems."

### When asked about async reset:
> "Asynchronous reset means the reset occurs immediately when reset_n goes low, without waiting for a clock edge. We include `negedge reset_n` in the sensitivity list and use blocking assignments in the reset branch for immediate effect."

### When asked about states:
> "Our 5-state FSM provides clear separation: INIT for reset, FETCH for instruction retrieval, LOAD for operand read, EXECUTE for computation, and STORE for write-back. Each state performs one major operation, simplifying timing analysis."

### When asked about testing:
> "We verified each module individually with dedicated testbenches, then performed system-level integration testing with a 5-instruction program. All ALU operations, memory accesses, and FSM state transitions were validated. Results matched expected values with 100% accuracy."

---

## 🎯 OPENING/CLOSING STATEMENTS

**Opening (30 sec):**
> "We've designed a complete 4-bit load-store processor meeting all 8 assignment requirements. It features custom arithmetic built from primitive gates, a 5-state FSM controller, dual RAM implementations, and a 7-operation ISA. All design constraints were satisfied including no use of primitive +, ^, or xor operators, structural hierarchy throughout, and proper async reset methodology."

**Closing (20 sec):**
> "This project demonstrates comprehensive understanding from gate-level to system architecture. Every module has been verified, constraints met, and the processor successfully executes test programs. We're prepared to discuss any aspect of the design, from Boolean algebra to instruction execution flow."

---

## 🔧 TECHNICAL SPECS

**Clock Period:** T_clk ≥ T_critical_path
**Critical Path:** RAM → ALU (4×FA) → ALU_REG ≈ 8-12ns
**Max Frequency:** ~80-120 MHz (conservative)
**Power:** CMOS dynamic + static leakage
**Area:** ~1000-2000 gates (including RAM)

---

## 📚 QUICK THEORY REFRESHER

**Setup Time:** Data stable BEFORE clock ↑
**Hold Time:** Data stable AFTER clock ↑
**Metastability:** Unstable state when timing violated
**Race Condition:** Order of assignment matters
**Critical Path:** Longest combinational delay
**Pipeline:** Overlap instruction stages (we don't have)
**Hazards:** Data/control conflicts (not an issue in our design)

---

## ✅ VERIFICATION CHECKLIST

- [x] Step 1: XOR without ^ → `xor_1b.v`
- [x] Step 2: Adder without + → `fa_1b.v`, `adder_4b.v`
- [x] Step 3: ALU structural → `alu_4b.v`
- [x] Step 4: Registered ALU → `alu_reg_4b.v`
- [x] Step 5: FSM 5-state → `decoder_fsm.v`
- [x] Step 6: Async RAM tri-state → `ram16x4_async.v`
- [x] Step 7: Top integration → `simple4_proc.v`
- [x] Step 8: Sync RAM → `ram16x4_sync.v`
- [x] All testbenches pass
- [x] GUI simulator functional
- [x] Documentation complete

---

## 🚀 CONFIDENCE BUILDERS

✅ **Every requirement met**
✅ **All tests passing**
✅ **Complete documentation**
✅ **Working simulator**
✅ **Deep understanding**

**You've got this! 💪**

---

*Print this card and keep it handy during viva preparation!*
