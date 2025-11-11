#!/usr/bin/env python3
"""
4-Bit Processor Simulator - Enhanced Modern GUI
Advanced SaaS-style interface with interactive circuit diagrams and real-time visualization
Mind Hackathon 2025
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, Canvas, messagebox
from typing import List, Dict, Tuple, Optional
from enum import Enum
import math

# ============================================================
# BEHAVIORAL MODELS OF VERILOG MODULES
# ============================================================

class XOR_1b:
    """Behavioral model of custom XOR gate (Step 1)"""
    @staticmethod
    def compute(a: bool, b: bool) -> bool:
        # C = (A & ~B) | (~A & B)
        return (a and not b) or (not a and b)

class FA_1b:
    """Behavioral model of 1-bit full adder (Step 2)"""
    @staticmethod
    def compute(a: bool, b: bool, cin: bool) -> tuple:
        xor_ab = XOR_1b.compute(a, b)
        s = XOR_1b.compute(xor_ab, cin)
        cout = (a and b) or (cin and xor_ab)
        return s, cout

class Adder_4b:
    """Behavioral model of 4-bit adder (Step 2)"""
    @staticmethod
    def compute(a: int, b: int, cin: bool) -> tuple:
        result = 0
        carry = cin
        
        for i in range(4):
            a_bit = (a >> i) & 1
            b_bit = (b >> i) & 1
            s_bit, carry = FA_1b.compute(a_bit, b_bit, carry)
            result |= (s_bit << i)
        
        return result & 0xF, carry

class ALU_4b:
    """Behavioral model of 4-bit ALU (Step 3)"""
    @staticmethod
    def compute(a: int, b: int, s: int, cin: bool) -> tuple:
        a &= 0xF
        b &= 0xF
        s &= 0x7
        
        if s == 0b000:  # Transfer A
            return a, False
        elif s == 0b001:  # A + B
            return Adder_4b.compute(a, b, cin)
        elif s == 0b010:  # A - B (2's complement)
            return Adder_4b.compute(a, (~b) & 0xF, True)
        elif s == 0b011:  # A & B
            return a & b, False
        elif s == 0b100:  # A | B
            return a | b, False
        elif s == 0b101:  # A xor B
            result = 0
            for i in range(4):
                a_bit = (a >> i) & 1
                b_bit = (b >> i) & 1
                xor_bit = XOR_1b.compute(a_bit, b_bit)
                result |= (xor_bit << i)
            return result, False
        elif s == 0b110:  # NOT A
            return (~a) & 0xF, False
        else:
            return 0, False

class FSMState(Enum):
    INIT = 0
    FETCH = 1
    LOAD = 2
    EXECUTE = 3
    STORE = 4

class Processor:
    """Behavioral model of the 4-bit processor (Step 7)"""
    def __init__(self):
        self.memory = [0] * 16
        self.pc = 0
        self.state = FSMState.INIT
        self.instruction = 0
        self.alu_result = 0
        self.alu_cout = False
        self.cycle_count = 0
        self.execution_log = []
        self.program = []
        
        # Waveform tracking
        self.waveform_history = {
            'clk': [],
            'pc': [],
            'state': [],
            'alu_out': [],
            'ram_addr': [],
            'ram_data': [],
            'instruction': []
        }
        
    def reset(self):
        self.pc = 0
        self.state = FSMState.INIT
        self.instruction = 0
        self.alu_result = 0
        self.alu_cout = False
        self.cycle_count = 0
        self.execution_log = []
        self.waveform_history = {k: [] for k in self.waveform_history}
        
    def load_program(self, program: List[int]):
        self.program = program
        self.pc = 0
        
    def clock_cycle(self) -> bool:
        """Execute one clock cycle, returns True if program continues"""
        self.cycle_count += 1
        
        # Record waveform data
        self.waveform_history['clk'].append(self.cycle_count % 2)
        self.waveform_history['pc'].append(self.pc)
        self.waveform_history['state'].append(self.state.value)
        self.waveform_history['alu_out'].append(self.alu_result)
        self.waveform_history['instruction'].append(self.instruction)
        
        if self.state == FSMState.INIT:
            self.log("INIT: Initializing processor")
            self.state = FSMState.FETCH
            
        elif self.state == FSMState.FETCH:
            if self.pc >= len(self.program):
                self.log("FETCH: Program complete")
                return False
            self.instruction = self.program[self.pc]
            self.log(f"FETCH: PC={self.pc:X}, Instr={self.instruction:011b}")
            self.pc += 1
            self.state = FSMState.LOAD
            
        elif self.state == FSMState.LOAD:
            opcode = (self.instruction >> 8) & 0x7
            op1 = (self.instruction >> 4) & 0xF
            op2 = self.instruction & 0xF
            
            mem_value = self.memory[op1]
            self.log(f"LOAD: M[{op1:X}] = {mem_value:X}")
            self.loaded_op1 = op1
            self.loaded_op2 = op2
            self.loaded_opcode = opcode
            self.loaded_mem = mem_value
            self.waveform_history['ram_addr'].append(op1)
            self.waveform_history['ram_data'].append(mem_value)
            self.state = FSMState.EXECUTE
            
        elif self.state == FSMState.EXECUTE:
            opcode = self.loaded_opcode
            mem_val = self.loaded_mem
            op2 = self.loaded_op2
            
            alu_s = 0
            alu_cin = False
            alu_a = mem_val
            alu_b = op2
            
            op_name = ["STO", "ADD", "SUB", "AND", "OR", "XOR", "NOT"][opcode]
            
            if opcode == 0b000:  # STO - transfer op2 through ALU
                alu_s = 0b000
                alu_a = op2
            elif opcode == 0b001:  # ADD
                alu_s = 0b001
            elif opcode == 0b010:  # SUB
                alu_s = 0b010
            elif opcode == 0b011:  # AND
                alu_s = 0b011
            elif opcode == 0b100:  # OR
                alu_s = 0b100
            elif opcode == 0b101:  # XOR
                alu_s = 0b101
            elif opcode == 0b110:  # NOT
                alu_s = 0b110
            
            self.alu_result, self.alu_cout = ALU_4b.compute(alu_a, alu_b, alu_s, alu_cin)
            self.log(f"EXECUTE: {op_name} A={alu_a:X} B={alu_b:X} S={alu_s:03b} → Result = {self.alu_result:X}")
            self.state = FSMState.STORE
            
        elif self.state == FSMState.STORE:
            self.memory[self.loaded_op1] = self.alu_result
            self.log(f"STORE: M[{self.loaded_op1:X}] ← {self.alu_result:X}")
            self.waveform_history['ram_addr'].append(self.loaded_op1)
            self.waveform_history['ram_data'].append(self.alu_result)
            self.state = FSMState.FETCH
        
        return True
    
    def log(self, message: str):
        self.execution_log.append(f"[Cycle {self.cycle_count:3d}] {message}")
    
    def run_program(self, max_cycles: int = 100) -> bool:
        self.reset()
        self.state = FSMState.FETCH
        
        for _ in range(max_cycles):
            if not self.clock_cycle():
                return True
        
        return False

# ============================================================
# ENHANCED GUI APPLICATION
# ============================================================

class ModernButton(tk.Canvas):
    """Custom modern button with gradient and hover effects"""
    def __init__(self, parent, text, command, color, **kwargs):
        super().__init__(parent, **kwargs)
        self.command = command
        self.text = text
        self.base_color = color
        self.hover_color = self.lighten_color(color, 1.3)
        self.is_hover = False
        
        self.config(highlightthickness=0, bg=self['bg'])
        self.bind('<Button-1>', lambda e: self.command())
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
        self.draw()
    
    def draw(self):
        self.delete('all')
        color = self.hover_color if self.is_hover else self.base_color
        
        # Rounded rectangle button
        x0, y0, x1, y1 = 5, 5, self.winfo_reqwidth()-5, self.winfo_reqheight()-5
        r = 8
        self.create_oval(x0, y0, x0+2*r, y0+2*r, fill=color, outline='')
        self.create_oval(x1-2*r, y0, x1, y0+2*r, fill=color, outline='')
        self.create_oval(x0, y1-2*r, x0+2*r, y1, fill=color, outline='')
        self.create_oval(x1-2*r, y1-2*r, x1, y1, fill=color, outline='')
        self.create_rectangle(x0+r, y0, x1-r, y1, fill=color, outline='')
        self.create_rectangle(x0, y0+r, x1, y1-r, fill=color, outline='')
        
        # Text
        self.create_text((x0+x1)/2, (y0+y1)/2, text=self.text, 
                        fill='white', font=('Segoe UI', 10, 'bold'))
    
    def on_enter(self, e):
        self.is_hover = True
        self.draw()
    
    def on_leave(self, e):
        self.is_hover = False
        self.draw()
    
    @staticmethod
    def lighten_color(hex_color, factor=1.2):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'

class ProcessorSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ 4-Bit Processor Simulator - Enhanced Edition")
        self.root.geometry("1800x1000")
        
        # Modern vibrant color scheme (SaaS-style)
        self.colors = {
            'bg_dark': '#0a0e27',
            'bg_medium': '#1a1d3f',
            'bg_light': '#242948',
            'bg_card': '#2d3250',
            'accent': '#ff6b9d',
            'accent2': '#00f5ff',
            'accent3': '#c77dff',
            'accent4': '#ffd60a',
            'success': '#06ffa5',
            'warning': '#ffba08',
            'error': '#ff006e',
            'text': '#ffffff',
            'text_dim': '#a0a8b7',
            'glow': '#7b2cbf'
        }
        
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Processor instance
        self.processor = Processor()
        self.animation_running = False
        self.animation_speed = 500  # ms
        self.diagram_mode = 'block'  # 'block' or 'circuit'
        
        # Tooltip
        self.tooltip = None
        self.tooltip_id = None
        
        # Create GUI
        self.create_widgets()
        self.load_default_program()
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header with gradient effect
        header = self.create_header(main_frame)
        header.pack(fill=tk.X, pady=(0, 15))
        
        # Main content area
        content = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        content.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls (300px)
        left_panel = self.create_control_panel(content)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Center panel - Visualizations (800px)
        center_panel = self.create_visualization_panel(content)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right panel - Execution log (500px)
        right_panel = self.create_log_panel(content)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.update_display()
    
    def create_header(self, parent):
        """Create animated header with gradient"""
        header = Canvas(parent, height=100, bg=self.colors['bg_dark'], highlightthickness=0)
        
        # Gradient background
        for i in range(100):
            color_ratio = i / 100
            r1, g1, b1 = 123, 44, 191  # Purple
            r2, g2, b2 = 0, 245, 255   # Cyan
            r = int(r1 + (r2 - r1) * color_ratio)
            g = int(g1 + (g2 - g1) * color_ratio)
            b = int(b1 + (b2 - b1) * color_ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            header.create_rectangle(i*20, 0, (i+1)*20, 100, fill=color, outline='')
        
        # Title with glow effect
        for offset in [(2, 2), (1, 1), (0, 0)]:
            alpha = 0.3 if offset != (0, 0) else 1.0
            color = self.colors['glow'] if offset != (0, 0) else 'white'
            header.create_text(50 + offset[0], 30 + offset[1], 
                             text="⚡ 4-BIT PROCESSOR SIMULATOR", 
                             font=('Segoe UI', 32, 'bold'), 
                             fill=color, anchor=tk.W)
        
        header.create_text(50, 65, 
                         text="Mind Hackathon 2025 | Real-Time HDL Visualization & Interactive Circuit Diagrams", 
                         font=('Segoe UI', 11), 
                         fill=self.colors['accent2'], anchor=tk.W)
        
        return header
    
    def create_control_panel(self, parent):
        """Create left control panel with modern cards"""
        panel = tk.Frame(parent, bg=self.colors['bg_dark'], width=300)
        
        # Control buttons card
        controls_card = self.create_card(panel, "⚙️ CONTROLS")
        controls_card.pack(fill=tk.X, pady=(0, 10))
        
        btn_container = tk.Frame(controls_card, bg=self.colors['bg_card'])
        btn_container.pack(padx=15, pady=15)
        
        # Modern gradient buttons
        buttons = [
            ("▶️ RUN", self.run_program, self.colors['success'], 0, 0),
            ("⏭️ STEP", self.step_cycle, self.colors['accent2'], 0, 1),
            ("🔄 RESET", self.reset_processor, self.colors['warning'], 1, 0),
            ("🧪 TEST", self.run_tests, self.colors['accent3'], 1, 1),
        ]
        
        for text, cmd, color, row, col in buttons:
            btn = ModernButton(btn_container, text, cmd, color, 
                             width=130, height=45, bg=self.colors['bg_card'])
            btn.grid(row=row, column=col, padx=5, pady=5)
            btn.draw()
        
        # Speed control
        speed_frame = tk.Frame(controls_card, bg=self.colors['bg_card'])
        speed_frame.pack(padx=15, pady=(0, 15))
        
        tk.Label(speed_frame, text="⚡ Animation Speed:", 
                font=('Segoe UI', 9, 'bold'),
                bg=self.colors['bg_card'], fg=self.colors['text']).pack(anchor=tk.W)
        
        self.speed_scale = tk.Scale(speed_frame, from_=100, to=1000, 
                                    orient=tk.HORIZONTAL, 
                                    bg=self.colors['bg_light'], 
                                    fg=self.colors['accent2'],
                                    troughcolor=self.colors['bg_medium'],
                                    highlightthickness=0,
                                    command=self.update_speed)
        self.speed_scale.set(500)
        self.speed_scale.pack(fill=tk.X, pady=5)
        
        # Status card
        status_card = self.create_card(panel, "📊 PROCESSOR STATUS")
        status_card.pack(fill=tk.X, pady=(0, 10))
        
        status_container = tk.Frame(status_card, bg=self.colors['bg_card'])
        status_container.pack(padx=15, pady=15, fill=tk.X)
        
        self.status_labels = {}
        status_items = [
            ("FSM State", "state", self.colors['accent']),
            ("Program Counter", "pc", self.colors['accent2']),
            ("Cycle Count", "cycle", self.colors['success']),
            ("ALU Output", "alu", self.colors['warning']),
            ("ALU Carry", "carry", self.colors['accent3'])
        ]
        
        for label, key, color in status_items:
            self.create_status_indicator(status_container, label, key, color)
        
        # Memory card
        mem_card = self.create_card(panel, "💾 RAM (16×4)")
        mem_card.pack(fill=tk.BOTH, expand=True)
        
        mem_container = tk.Frame(mem_card, bg=self.colors['bg_card'])
        mem_container.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
        
        self.mem_text = scrolledtext.ScrolledText(mem_container, width=30, height=20, 
                                                  font=('JetBrains Mono', 9),
                                                  bg=self.colors['bg_light'], 
                                                  fg=self.colors['text'],
                                                  insertbackground=self.colors['accent2'],
                                                  relief='flat', bd=0)
        self.mem_text.pack(fill=tk.BOTH, expand=True)
        
        return panel
    
    def create_visualization_panel(self, parent):
        """Create center visualization panel"""
        panel = tk.Frame(parent, bg=self.colors['bg_dark'])
        
        # Circuit diagram card
        circuit_card = self.create_card(panel, "🔌 ARCHITECTURE DIAGRAM")
        circuit_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Diagram controls
        ctrl_frame = tk.Frame(circuit_card, bg=self.colors['bg_card'])
        ctrl_frame.pack(padx=15, pady=(10, 5), fill=tk.X)
        
        tk.Label(ctrl_frame, text="View Mode:", 
                font=('Segoe UI', 9, 'bold'),
                bg=self.colors['bg_card'], fg=self.colors['text']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.mode_var = tk.StringVar(value='block')
        modes = [("📦 Block Diagram", 'block'), ("⚡ Circuit View", 'circuit')]
        for text, mode in modes:
            rb = tk.Radiobutton(ctrl_frame, text=text, variable=self.mode_var, 
                              value=mode, command=self.switch_diagram_mode,
                              bg=self.colors['bg_card'], fg=self.colors['text'],
                              selectcolor=self.colors['bg_light'],
                              activebackground=self.colors['bg_card'],
                              activeforeground=self.colors['accent2'],
                              font=('Segoe UI', 9))
            rb.pack(side=tk.LEFT, padx=5)
        
        # Circuit canvas
        canvas_frame = tk.Frame(circuit_card, bg=self.colors['bg_light'])
        canvas_frame.pack(padx=15, pady=(5, 15), fill=tk.BOTH, expand=True)
        
        self.circuit_canvas = Canvas(canvas_frame, bg=self.colors['bg_light'], 
                                     highlightthickness=0)
        self.circuit_canvas.pack(fill=tk.BOTH, expand=True)
        self.circuit_canvas.bind('<Motion>', self.on_circuit_hover)
        
        # Waveform card
        wave_card = self.create_card(panel, "〰️ SIGNAL WAVEFORMS")
        wave_card.pack(fill=tk.BOTH, expand=True)
        
        wave_frame = tk.Frame(wave_card, bg=self.colors['bg_light'])
        wave_frame.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
        
        self.waveform_canvas = Canvas(wave_frame, bg=self.colors['bg_light'], 
                                      highlightthickness=0)
        self.waveform_canvas.pack(fill=tk.BOTH, expand=True)
        
        return panel
    
    def create_log_panel(self, parent):
        """Create right execution log panel"""
        panel = tk.Frame(parent, bg=self.colors['bg_dark'])
        
        log_card = self.create_card(panel, "📝 EXECUTION LOG")
        log_card.pack(fill=tk.BOTH, expand=True)
        
        log_frame = tk.Frame(log_card, bg=self.colors['bg_light'])
        log_frame.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=55, height=50, 
                                                  font=('JetBrains Mono', 9),
                                                  bg=self.colors['bg_light'], 
                                                  fg=self.colors['text'],
                                                  insertbackground=self.colors['accent2'],
                                                  relief='flat', bd=0,
                                                  wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        return panel
    
    def create_card(self, parent, title):
        """Create a modern glassmorphic card"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='flat')
        
        # Title bar with gradient
        title_canvas = Canvas(card, height=40, bg=self.colors['bg_card'], 
                             highlightthickness=0)
        title_canvas.pack(fill=tk.X, padx=2, pady=2)
        
        # Subtle gradient
        for i in range(40):
            ratio = i / 40
            color_val = int(42 + 20 * ratio)
            color = f'#{color_val:02x}{color_val:02x}{int(color_val * 1.2):02x}'
            title_canvas.create_line(0, i, 2000, i, fill=color)
        
        title_canvas.create_text(20, 20, text=title, 
                               font=('Segoe UI', 13, 'bold'), 
                               fill=self.colors['accent2'], anchor=tk.W)
        
        return card
    
    def create_status_indicator(self, parent, label, key, color):
        """Create a modern status indicator"""
        frame = tk.Frame(parent, bg=self.colors['bg_light'], relief='flat')
        frame.pack(fill=tk.X, pady=4)
        
        tk.Label(frame, text=label, font=('Segoe UI', 8),
                bg=self.colors['bg_light'], fg=self.colors['text_dim']).pack(anchor=tk.W, padx=12, pady=(6, 0))
        
        self.status_labels[key] = tk.Label(frame, text="--", 
                                          font=('JetBrains Mono', 14, 'bold'),
                                          bg=self.colors['bg_light'], fg=color)
        self.status_labels[key].pack(anchor=tk.W, padx=12, pady=(0, 6))
    
    def draw_block_diagram(self):
        """Draw factually correct block diagram based on Verilog RTL"""
        c = self.circuit_canvas
        c.delete('all')
        
        width = c.winfo_width() if c.winfo_width() > 1 else 750
        height = c.winfo_height() if c.winfo_height() > 1 else 400
        
        # Module definitions with hover info
        modules = {
            'pc': {
                'rect': (50, 50, 180, 130),
                'label': "PC\nCounter",
                'info': "4-bit Program Counter\nInputs: clk, reset_n, pc_inc\nOutputs: pc[3:0]\nIncrement on pc_inc signal"
            },
            'ram': {
                'rect': (250, 50, 380, 130),
                'label': "RAM 16×4\n(Sync)",
                'info': "Synchronous RAM (Step 8)\nInputs: clk, addr[3:0], datain[3:0], csn, rwn\nOutputs: dataout[3:0]\nrwn: 0=Write, 1=Read"
            },
            'fsm': {
                'rect': (450, 50, 580, 130),
                'label': "FSM\nDecoder",
                'info': "5-State FSM (Step 5)\nStates: INIT→FETCH→LOAD→EXECUTE→STORE\nOutputs: ram_csn, ram_rwn, alu_s[2:0], alu_cin, pc_inc"
            },
            'alu': {
                'rect': (250, 200, 380, 280),
                'label': "ALU 4-bit\n(Step 3)",
                'info': "4-bit ALU with 7 operations\nInputs: A[3:0], B[3:0], S[2:0], Cin\nOutputs: F[3:0], Cout\nOps: STO,ADD,SUB,AND,OR,XOR,NOT"
            },
            'alu_reg': {
                'rect': (450, 200, 580, 280),
                'label': "ALU Reg\n(Step 4)",
                'info': "Registered ALU (Step 4)\nInputs: clk, reset_n, alu_f[3:0], alu_cout\nOutputs: alu_f_reg[3:0], alu_cout_reg\nAsync active-low reset"
            }
        }
        
        # Draw modules
        for key, mod in modules.items():
            x1, y1, x2, y2 = mod['rect']
            
            # Shadow
            c.create_rectangle(x1+4, y1+4, x2+4, y2+4, 
                             fill='#000000', outline='', tags=key)
            
            # Module box with gradient
            mid_y = (y1 + y2) / 2
            for i in range(int(y1), int(y2), 2):
                ratio = (i - y1) / (y2 - y1)
                r = int(42 + 15 * ratio)
                color = f'#{r:02x}{r:02x}{int(r*1.3):02x}'
                c.create_rectangle(x1, i, x2, i+2, fill=color, outline='', tags=key)
            
            # Border
            c.create_rectangle(x1, y1, x2, y2, outline=self.colors['accent2'], 
                             width=2, tags=key)
            
            # Label
            c.create_text((x1+x2)/2, (y1+y2)/2, text=mod['label'], 
                         fill='white', font=('Segoe UI', 11, 'bold'), tags=key)
            
            # Bind hover events
            c.tag_bind(key, '<Enter>', lambda e, m=mod: self.show_tooltip(e, m['info']))
            c.tag_bind(key, '<Leave>', self.hide_tooltip)
        
        # Draw connections with arrows
        connections = [
            (180, 90, 250, 90, "pc[3:0]", self.colors['accent2']),
            (380, 90, 450, 90, "instruction[10:0]", self.colors['accent']),
            (515, 130, 515, 200, "alu_s[2:0], cin", self.colors['warning']),
            (315, 130, 315, 200, "ram_dataout[3:0]", self.colors['success']),
            (380, 240, 450, 240, "alu_f[3:0]", self.colors['accent3']),
        ]
        
        for x1, y1, x2, y2, label, color in connections:
            # Draw arrow
            c.create_line(x1, y1, x2, y2, fill=color, width=3, 
                         arrow=tk.LAST, arrowshape=(12, 15, 6))
            
            # Label
            mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
            c.create_text(mid_x, mid_y-10, text=label, 
                         fill=color, font=('Consolas', 8, 'bold'))
        
        # Data bus
        c.create_line(50, 320, width-50, 320, fill=self.colors['accent4'], 
                     width=5, dash=(8, 4))
        c.create_text(width/2, 340, text="🔄 Data Bus (4-bit bidirectional)", 
                     fill=self.colors['accent4'], font=('Segoe UI', 10, 'bold'))
        
        # Clock signal
        c.create_text(width-100, 30, text="🕐 clk", 
                     fill=self.colors['accent2'], font=('Segoe UI', 10, 'bold'))
        c.create_text(width-100, 50, text="⚡ reset_n", 
                     fill=self.colors['error'], font=('Segoe UI', 10, 'bold'))
    
    def draw_circuit_diagram(self):
        """Draw detailed gate-level circuit view"""
        c = self.circuit_canvas
        c.delete('all')
        
        width = c.winfo_width() if c.winfo_width() > 1 else 750
        height = c.winfo_height() if c.winfo_height() > 1 else 400
        
        c.create_text(width/2, 30, text="⚡ Gate-Level Circuit View", 
                     fill=self.colors['accent2'], font=('Segoe UI', 14, 'bold'))
        
        # Draw XOR gate (Step 1)
        xor_x, xor_y = 100, 100
        self.draw_gate(c, xor_x, xor_y, "XOR", "custom_xor", 
                      "Custom XOR Gate (Step 1)\nC = (A & ~B) | (~A & B)\nNo ^ operator used")
        
        # Draw Full Adder (Step 2)
        fa_x, fa_y = 250, 100
        self.draw_gate(c, fa_x, fa_y, "FA", "fa_1b", 
                      "1-bit Full Adder (Step 2)\nInstantiates 2× xor_1b\nOutputs: sum, cout")
        
        # Draw 4-bit Adder chain
        adder_x, adder_y = 400, 100
        self.draw_gate(c, adder_x, adder_y, "ADDER\n4-bit", "adder_4b", 
                      "4-bit Structural Adder (Step 2)\nChains 4× fa_1b instances\nRipple carry propagation")
        
        # Draw ALU
        alu_x, alu_y = 550, 100
        self.draw_gate(c, alu_x, alu_y, "ALU\n4-bit", "alu_4b", 
                      "4-bit ALU (Step 3)\nInstantiates adder_4b + 4× xor_1b\n7 operations controlled by S[2:0]")
        
        # Connection arrows
        c.create_line(150, 115, 220, 115, fill=self.colors['accent2'], 
                     width=2, arrow=tk.LAST)
        c.create_line(300, 115, 370, 115, fill=self.colors['accent2'], 
                     width=2, arrow=tk.LAST)
        c.create_line(450, 115, 520, 115, fill=self.colors['accent2'], 
                     width=2, arrow=tk.LAST)
        
        # Legend
        legend_y = 220
        c.create_text(100, legend_y, text="📊 Module Hierarchy & Reuse:", 
                     fill=self.colors['accent2'], font=('Segoe UI', 11, 'bold'), 
                     anchor=tk.W)
        
        hierarchy = [
            "Step 1: xor_1b (custom XOR without ^)",
            "Step 2: fa_1b uses 2× xor_1b",
            "Step 2: adder_4b chains 4× fa_1b",
            "Step 3: alu_4b uses adder_4b + 4× xor_1b",
            "Step 4: alu_reg_4b registers ALU outputs",
            "Step 5: decoder_fsm controls all operations",
            "Step 6: ram16x4_async (tri-state outputs)",
            "Step 7: simple4_proc integrates all modules",
            "Step 8: ram16x4_sync (registered outputs)"
        ]
        
        for i, line in enumerate(hierarchy):
            c.create_text(100, legend_y + 30 + i*20, text=f"• {line}", 
                         fill=self.colors['text'], font=('Consolas', 9), 
                         anchor=tk.W)
    
    def draw_gate(self, canvas, x, y, label, tag, info):
        """Draw a logic gate with hover info"""
        # Gate body
        canvas.create_rectangle(x-40, y-25, x+40, y+25, 
                              fill=self.colors['bg_medium'], 
                              outline=self.colors['accent3'], 
                              width=2, tags=tag)
        canvas.create_text(x, y, text=label, fill='white', 
                          font=('Segoe UI', 10, 'bold'), tags=tag)
        
        # Bind hover
        canvas.tag_bind(tag, '<Enter>', lambda e, i=info: self.show_tooltip(e, i))
        canvas.tag_bind(tag, '<Leave>', self.hide_tooltip)
    
    def draw_waveforms(self):
        """Draw enhanced real-time waveforms"""
        c = self.waveform_canvas
        c.delete('all')
        
        width = c.winfo_width() if c.winfo_width() > 1 else 750
        height = c.winfo_height() if c.winfo_height() > 1 else 300
        
        history = self.processor.waveform_history
        if not history['clk']:
            c.create_text(width/2, height/2, 
                         text="⏳ Run program to see waveforms", 
                         fill=self.colors['text_dim'], 
                         font=('Segoe UI', 12, 'italic'))
            return
        
        max_cycles = min(60, len(history['clk']))
        if max_cycles == 0:
            return
        
        margin_left = 100
        margin_right = 30
        margin_top = 30
        signal_height = 45
        
        x_scale = (width - margin_left - margin_right) / max(1, max_cycles - 1)
        
        # Signals with proper scaling
        signals = [
            ('CLK', history['clk'][-max_cycles:], self.colors['accent2'], 0, 1, True),
            ('PC[3:0]', history['pc'][-max_cycles:], self.colors['success'], 0, 15, False),
            ('STATE', history['state'][-max_cycles:], self.colors['warning'], 0, 4, False),
            ('ALU[3:0]', history['alu_out'][-max_cycles:], self.colors['accent'], 0, 15, False),
        ]
        
        for idx, (name, data, color, min_val, max_val, is_clock) in enumerate(signals):
            y_base = margin_top + idx * signal_height
            
            # Signal name with colored background
            name_bg = c.create_rectangle(5, y_base, margin_left-10, y_base+30, 
                                        fill=self.colors['bg_medium'], outline=color, width=2)
            c.create_text(margin_left/2, y_base+15, text=name, 
                         fill=color, font=('Segoe UI', 10, 'bold'))
            
            # Grid line
            c.create_line(margin_left, y_base+15, width-margin_right, y_base+15, 
                         fill=self.colors['text_dim'], width=1, dash=(3, 3))
            
            # Draw waveform
            if len(data) > 0:
                if is_clock:
                    # Square wave for clock
                    for i in range(len(data)):
                        x = margin_left + i * x_scale
                        val = data[i]
                        y = y_base + 25 if val == 0 else y_base + 5
                        x_next = margin_left + (i+1) * x_scale if i < len(data)-1 else x
                        c.create_line(x, y, x_next, y, fill=color, width=2)
                        if i < len(data)-1:
                            y_next = y_base + 25 if data[i+1] == 0 else y_base + 5
                            c.create_line(x_next, y, x_next, y_next, fill=color, width=2)
                else:
                    # Multi-level signal
                    prev_x, prev_y = None, None
                    for i in range(len(data)):
                        x = margin_left + i * x_scale
                        normalized = (data[i] - min_val) / max(1, max_val - min_val)
                        y = y_base + 25 - (normalized * 20)
                        
                        if prev_x is not None:
                            c.create_line(prev_x, prev_y, x, prev_y, fill=color, width=2)
                            c.create_line(x, prev_y, x, y, fill=color, width=2)
                        
                        prev_x, prev_y = x, y
                        
                        # Value labels at transitions
                        if i == 0 or (i > 0 and data[i] != data[i-1]):
                            c.create_text(x, y-10, text=f"{data[i]:X}", 
                                        fill=color, font=('Consolas', 7, 'bold'))
                
                # Current value
                if len(data) > 0:
                    c.create_text(width-15, y_base+15, text=f"{data[-1]:X}", 
                                fill=color, font=('JetBrains Mono', 10, 'bold'), 
                                anchor=tk.E)
        
        # Time axis
        for i in range(0, max_cycles, 10):
            x = margin_left + i * x_scale
            cycle_num = len(history['clk']) - max_cycles + i
            c.create_line(x, margin_top, x, height-20, 
                         fill=self.colors['text_dim'], width=1, dash=(1, 4))
            c.create_text(x, height-10, text=str(cycle_num), 
                         fill=self.colors['text_dim'], font=('Consolas', 8))
    
    def show_tooltip(self, event, text):
        """Show hover tooltip"""
        self.hide_tooltip()
        
        x, y = event.x_root + 10, event.y_root + 10
        
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        frame = tk.Frame(self.tooltip, bg=self.colors['bg_dark'], 
                        relief='solid', borderwidth=2)
        frame.pack()
        
        label = tk.Label(frame, text=text, justify=tk.LEFT,
                        bg=self.colors['bg_dark'], fg=self.colors['text'],
                        font=('Segoe UI', 9), padx=10, pady=5)
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    
    def on_circuit_hover(self, event):
        """Handle mouse hover over circuit"""
        pass  # Tooltips are handled by tag bindings
    
    def switch_diagram_mode(self):
        """Switch between block and circuit diagram views"""
        self.diagram_mode = self.mode_var.get()
        if self.diagram_mode == 'block':
            self.draw_block_diagram()
        else:
            self.draw_circuit_diagram()
    
    def update_speed(self, value):
        """Update animation speed"""
        self.animation_speed = int(value)
    
    def load_default_program(self):
        """Load sample program from program.mem"""
        program = [
            0b00001000101,  # STO 0x4 0x5
            0b00101000110,  # ADD 0x4 0x6
            0b00000011111,  # STO 0x1 0xF
            0b01000010111,  # SUB 0x1 0x7
            0b11011110000,  # NOT 0xF 0x0
        ]
        self.processor.load_program(program)
        self.log("✅ Loaded program.mem (5 instructions)")
        self.log("📋 Program:")
        self.log("  [0] STO M[0x4] ← 0x5")
        self.log("  [1] ADD M[0x4] ← M[0x4] + 0x6")
        self.log("  [2] STO M[0x1] ← 0xF")
        self.log("  [3] SUB M[0x1] ← M[0x1] - 0x7")
        self.log("  [4] NOT M[0xF] ← ~M[0xF]")
    
    def run_program(self):
        """Run program with animation"""
        if self.animation_running:
            return
        
        self.log("\n" + "="*50)
        self.log("▶️ RUNNING PROGRAM...")
        self.log("="*50)
        self.animation_running = True
        self.animate_execution()
    
    def animate_execution(self):
        """Animate program execution"""
        if self.animation_running:
            running = self.processor.clock_cycle()
            self.update_display()
            
            if running:
                self.root.after(self.animation_speed, self.animate_execution)
            else:
                self.animation_running = False
                self.log("\n✅ Program execution complete!")
                self.check_results()
    
    def step_cycle(self):
        """Execute one cycle"""
        if self.animation_running:
            return
        
        running = self.processor.clock_cycle()
        self.update_display()
        
        if not running:
            self.log("\n✅ Program complete")
            self.check_results()
    
    def reset_processor(self):
        """Reset processor"""
        self.animation_running = False
        self.processor.reset()
        self.load_default_program()
        self.update_display()
        self.log("\n🔄 Processor reset to initial state")
    
    def update_display(self):
        """Update all GUI elements"""
        # Status indicators
        state_name = self.processor.state.name
        self.status_labels['state'].config(text=state_name)
        self.status_labels['pc'].config(text=f"0x{self.processor.pc:X}")
        self.status_labels['cycle'].config(text=str(self.processor.cycle_count))
        self.status_labels['alu'].config(text=f"0x{self.processor.alu_result:X}")
        self.status_labels['carry'].config(text="1" if self.processor.alu_cout else "0")
        
        # Memory display
        self.mem_text.delete(1.0, tk.END)
        self.mem_text.insert(tk.END, "┌──────┬───────┬──────────┐\n", 'header')
        self.mem_text.insert(tk.END, "│ ADDR │ VALUE │  BINARY  │\n", 'header')
        self.mem_text.insert(tk.END, "├──────┼───────┼──────────┤\n", 'header')
        
        for i in range(16):
            val = self.processor.memory[i]
            line = f"│  {i:X}   │   {val:X}   │  {val:04b}  │\n"
            
            if val != 0:
                self.mem_text.insert(tk.END, line, 'highlight')
            else:
                self.mem_text.insert(tk.END, line, 'normal')
        
        self.mem_text.insert(tk.END, "└──────┴───────┴──────────┘\n", 'header')
        
        # Configure tags
        self.mem_text.tag_config('header', foreground=self.colors['accent2'], 
                                font=('JetBrains Mono', 9, 'bold'))
        self.mem_text.tag_config('highlight', foreground=self.colors['success'], 
                                font=('JetBrains Mono', 9, 'bold'))
        self.mem_text.tag_config('normal', foreground=self.colors['text_dim'])
        
        # Execution log
        self.log_text.delete(1.0, tk.END)
        for line in self.processor.execution_log:
            if 'FETCH' in line:
                self.log_text.insert(tk.END, line + "\n", 'fetch')
            elif 'EXECUTE' in line:
                self.log_text.insert(tk.END, line + "\n", 'execute')
            elif 'STORE' in line:
                self.log_text.insert(tk.END, line + "\n", 'store')
            elif 'LOAD' in line:
                self.log_text.insert(tk.END, line + "\n", 'load')
            else:
                self.log_text.insert(tk.END, line + "\n")
        
        self.log_text.tag_config('fetch', foreground=self.colors['accent2'])
        self.log_text.tag_config('load', foreground=self.colors['warning'])
        self.log_text.tag_config('execute', foreground=self.colors['accent'])
        self.log_text.tag_config('store', foreground=self.colors['success'])
        self.log_text.see(tk.END)
        
        # Update diagrams
        if self.diagram_mode == 'block':
            self.draw_block_diagram()
        else:
            self.draw_circuit_diagram()
        
        self.draw_waveforms()
    
    def log(self, message: str):
        """Add message to execution log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def check_results(self):
        """Verify program results"""
        expected = {
            0x1: 0x8,  # 0xF - 0x7 = 0x8
            0x4: 0xB,  # 0x5 + 0x6 = 0xB
            0xF: 0xF,  # ~0x0 = 0xF
        }
        
        self.log("\n" + "="*50)
        self.log("🧪 VERIFICATION")
        self.log("="*50)
        
        all_pass = True
        for addr, expected_val in expected.items():
            actual = self.processor.memory[addr]
            status = "✅ PASS" if actual == expected_val else "❌ FAIL"
            self.log(f"mem[0x{addr:X}] = 0x{actual:X} (expected 0x{expected_val:X}) {status}")
            if actual != expected_val:
                all_pass = False
        
        if all_pass:
            self.log("\n🎉 ALL TESTS PASSED! 🎉")
            messagebox.showinfo("Tests Passed", "🎉 All verification tests passed!")
        else:
            self.log("\n❌ Some tests failed - check execution log")
            messagebox.showwarning("Tests Failed", "❌ Some tests failed. Check the execution log for details.")
    
    def run_tests(self):
        """Run unit tests"""
        self.log("\n" + "="*50)
        self.log("🧪 RUNNING UNIT TESTS")
        self.log("="*50 + "\n")
        
        # Test XOR
        self.log("Testing XOR_1b (Step 1)...")
        tests = [(0,0,0), (0,1,1), (1,0,1), (1,1,0)]
        xor_pass = all(XOR_1b.compute(a, b) == expected for a, b, expected in tests)
        self.log(f"  {'✅ PASS' if xor_pass else '❌ FAIL'}\n")
        
        # Test Full Adder
        self.log("Testing FA_1b (Step 2)...")
        s, c = FA_1b.compute(1, 1, 1)
        fa_pass = (s == 1 and c == 1)
        self.log(f"  1+1+1 = {s} carry {c}")
        self.log(f"  {'✅ PASS' if fa_pass else '❌ FAIL'}\n")
        
        # Test Adder
        self.log("Testing Adder_4b (Step 2)...")
        result, cout = Adder_4b.compute(5, 6, False)
        self.log(f"  5 + 6 = {result}, carry = {cout}")
        self.log(f"  {'✅ PASS' if result == 11 else '❌ FAIL'}\n")
        
        # Test ALU
        self.log("Testing ALU_4b (Step 3)...")
        alu_tests = [
            (10, 6, 0b001, False, 0, "ADD"),
            (10, 6, 0b010, False, 4, "SUB"),
            (10, 6, 0b011, False, 2, "AND"),
            (10, 6, 0b100, False, 14, "OR"),
            (10, 6, 0b101, False, 12, "XOR"),
            (5, 0, 0b110, False, 10, "NOT"),
        ]
        
        alu_pass = True
        for a, b, s, cin, exp_f, name in alu_tests:
            f, c = ALU_4b.compute(a, b, s, cin)
            status = "✅" if f == exp_f else "❌"
            self.log(f"  {name}: A={a:X} B={b:X} → F={f:X} (exp {exp_f:X}) {status}")
            if f != exp_f:
                alu_pass = False
        
        self.log(f"\n  {'✅ ALL ALU TESTS PASSED' if alu_pass else '❌ SOME ALU TESTS FAILED'}\n")
        
        # Integration test
        self.log("Running Full Processor Integration Test...")
        self.reset_processor()
        self.root.after(500, self.run_program)

def main():
    root = tk.Tk()
    app = ProcessorSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
