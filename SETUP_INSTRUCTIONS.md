# 🎯 Setup Instructions for Your Friend

## Quick Start (3 Steps!)

### Step 1: Get the Code

```bash
# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/mind-hackathon.git
cd mind-hackathon
```

**OR** Download ZIP from GitHub and extract it.

---

### Step 2: Check Python Version

```bash
python --version
```

**Need:** Python 3.7 or higher

If you don't have Python:
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **macOS:** `brew install python3`
- **Linux:** Usually pre-installed

---

### Step 3: Run the Simulator

```bash
python simulator_gui.py
```

**That's it! No installation required.** ✨

---

## ⚠️ Troubleshooting

### Issue: "tkinter not found"

**Windows:**
- Reinstall Python and check "tcl/tk and IDLE" option

**Linux:**
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo dnf install python3-tkinter  # Fedora
sudo pacman -S tk                 # Arch
```

**macOS:**
```bash
brew install python-tk
```

---

### Issue: "architecture_diagram module not found"

Make sure both files are in the same folder:
- `simulator_gui.py`
- `architecture_diagram.py`

---

### Issue: Can't see everything in the GUI

The interface is **scrollable**! 
- Use your **mouse wheel** to scroll down
- Or use the **scrollbar** on the right side

---

## 🎮 How to Use

### Load and Run Programs

1. Click **"Load Example"** → Loads random assembly program
2. Click **"Run"** → Watch it execute with animation
3. Click **"Step"** → Execute one cycle at a time
4. Click **"Reset"** → Start over

### Write Your Own Program

1. Type assembly code in the **Assembly Editor** box:
   ```assembly
   STO 0x4, 0x5    // Store 5 at address 4
   ADD 0x4, 0x6    // Add 6 to mem[4]
   ```
2. Click **"Compile & Load"**
3. Click **"Run"** or **"Step"**

### Assembly Language Syntax

**7 Instructions Available:**
- `STO addr, imm` - Store immediate value
- `ADD addr, imm` - Add to memory value
- `SUB addr, imm` - Subtract from memory value
- `AND addr, imm` - Bitwise AND
- `OR addr, imm` - Bitwise OR
- `XOR addr, imm` - Bitwise XOR
- `NOT addr, imm` - Bitwise NOT

**Example:**
```assembly
// Calculate (5 + 6) - 3
STO 0x0, 0x5    // mem[0] = 5
ADD 0x0, 0x6    // mem[0] = 5 + 6 = 11
SUB 0x0, 0x3    // mem[0] = 11 - 3 = 8
```

---

## 📊 What You'll See

### Real-Time Features:

1. **Architecture Diagram** - Clean block diagram showing all components
2. **ALU Visualizer** - Gate-level animation during execution
   - **● ACTIVE** (cyan) when executing
   - Shows adder chain for ADD/SUB
   - Shows XOR gates for XOR operation
3. **RAM Timing Comparison** - Async vs Sync side-by-side
   - Green = READ operations
   - Red = WRITE operations
4. **Critical Path Analyzer** - Shows timing bottlenecks
5. **Memory Viewer** - Live memory state
6. **Waveforms** - Signal visualization
7. **Execution Log** - Color-coded state transitions

---

## 🚀 Pro Tips

- **Press "Load Example" multiple times** - 8 different programs!
- **Use "Step" for learning** - See each state transition
- **Use "Run" for demos** - Smooth animation
- **Scroll down** - More features below!
- **Click on architecture diagram** - Zoom view

---

## 📁 Project Files

```
mind-hackathon/
├── simulator_gui.py           # Main GUI (run this!)
├── architecture_diagram.py    # Diagram module
├── rtl/                       # Verilog modules (9 files)
├── testbenches/               # Test files (6 files)
├── README.md                  # Full documentation
├── requirements.txt           # Empty (no packages needed!)
└── VIVA_PREPARATION_GUIDE.md  # Q&A for viva
```

---

## ❓ Need Help?

1. Check **README.md** for full documentation
2. Check **VIVA_PREPARATION_GUIDE.md** for technical details
3. All code has comments explaining functionality

---

## 🎉 Enjoy!

**Made with ❤️ for Mind Hackathon 2025**

Try clicking "Load Example" and "Run" to see the magic! ✨
