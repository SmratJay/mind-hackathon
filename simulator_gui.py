#!/usr/bin/env python3
"""
4-Bit Processor Simulator with Advanced Modern GUI
A custom-built behavioral simulator for the 4-bit processor
with modern SaaS-style UI, interactive circuit diagrams, and real-time waveforms
Mind Hackathon 2025
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, Canvas, messagebox
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum
import math
from architecture_diagram import ArchitectureDiagram

# ============================================================
# BEHAVIORAL MODELS OF VERILOG MODULES
# ============================================================

class XOR_1b:
    """Behavioral model of custom XOR gate"""
    @staticmethod
    def compute(a: bool, b: bool) -> bool:
        # C = (A & ~B) | (~A & B)
        return (a and not b) or (not a and b)

class FA_1b:
    """Behavioral model of 1-bit full adder"""
    @staticmethod
    def compute(a: bool, b: bool, cin: bool) -> tuple:
        # S = A xor B xor Cin
        xor_ab = XOR_1b.compute(a, b)
        s = XOR_1b.compute(xor_ab, cin)
        # Cout = (A & B) | (Cin & (A xor B))
        cout = (a and b) or (cin and xor_ab)
        return s, cout

class Adder_4b:
    """Behavioral model of 4-bit adder"""
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
    """Behavioral model of 4-bit ALU"""
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
    """Behavioral model of the 4-bit processor"""
    def __init__(self):
        self.memory = [0] * 16  # 16 words of 4 bits
        self.pc = 0
        self.state = FSMState.INIT
        self.instruction = 0
        self.alu_result = 0
        self.alu_cout = False
        self.cycle_count = 0
        self.execution_log = []
        
        # Waveform tracking
        self.waveform_history = {
            'clk': [],
            'pc': [],
            'state': [],
            'alu_out': [],
            'ram_addr': [],
            'ram_data': []
        }
        
    def reset(self):
        self.pc = 0
        self.state = FSMState.INIT
        self.instruction = 0
        self.alu_result = 0
        self.alu_cout = False
        self.cycle_count = 0
        self.execution_log = []
        self.waveform_history = {
            'clk': [],
            'pc': [],
            'state': [],
            'alu_out': [],
            'ram_addr': [],
            'ram_data': []
        }
        
    def load_program(self, program: List[int]):
        """Load program into memory (11-bit instructions compressed)"""
        # For simplicity, store instructions as-is
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
        
        if self.state == FSMState.INIT:
            self.log("INIT: Initializing processor")
            self.state = FSMState.FETCH
            
        elif self.state == FSMState.FETCH:
            if self.pc >= len(self.program):
                self.log("FETCH: Program complete")
                return False  # Program done
            self.instruction = self.program[self.pc]
            self.log(f"FETCH: PC={self.pc:X}, Instr={self.instruction:011b}")
            self.pc += 1
            self.state = FSMState.LOAD
            
        elif self.state == FSMState.LOAD:
            # Decode instruction
            opcode = (self.instruction >> 8) & 0x7
            op1 = (self.instruction >> 4) & 0xF
            op2 = self.instruction & 0xF
            
            # Read operand from memory
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
            op1 = self.loaded_op1
            op2 = self.loaded_op2
            mem_val = self.loaded_mem
            
            # Map opcode to ALU control
            alu_s = 0
            alu_cin = False
            alu_a = mem_val
            alu_b = op2
            
            op_name = ["STO", "ADD", "SUB", "AND", "OR", "XOR", "NOT"][opcode]
            
            if opcode == 0b000:  # STO
                alu_s = 0b000
                alu_a = op2  # Transfer op2 through ALU
            elif opcode == 0b001:  # ADD
                alu_s = 0b001
            elif opcode == 0b010:  # SUB
                alu_s = 0b010
                alu_cin = True
            elif opcode == 0b011:  # AND
                alu_s = 0b011
            elif opcode == 0b100:  # OR
                alu_s = 0b100
            elif opcode == 0b101:  # XOR
                alu_s = 0b101
            elif opcode == 0b110:  # NOT
                alu_s = 0b110
            
            # Execute ALU operation
            self.alu_result, self.alu_cout = ALU_4b.compute(alu_a, alu_b, alu_s, alu_cin)
            self.log(f"EXECUTE: {op_name} A={alu_a:X} B={alu_b:X} S={alu_s:03b} → Result = {self.alu_result:X}")
            self.state = FSMState.STORE
            
        elif self.state == FSMState.STORE:
            # Write result back to memory
            self.memory[self.loaded_op1] = self.alu_result
            self.log(f"STORE: M[{self.loaded_op1:X}] ← {self.alu_result:X}")
            self.waveform_history['ram_addr'].append(self.loaded_op1)
            self.waveform_history['ram_data'].append(self.alu_result)
            self.state = FSMState.FETCH
        
        return True
    
    def log(self, message: str):
        self.execution_log.append(f"[Cycle {self.cycle_count:3d}] {message}")
    
    def run_program(self, max_cycles: int = 100) -> bool:
        """Run program until completion or max cycles"""
        self.reset()
        self.state = FSMState.FETCH
        
        for _ in range(max_cycles):
            if not self.clock_cycle():
                return True  # Success
        
        return False  # Timeout

# ============================================================
# GUI APPLICATION
# ============================================================

class ProcessorSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 4-Bit Processor Simulator - Mind Hackathon 2025")
        self.root.geometry("1600x900")
        
        # Modern color scheme
        self.colors = {
            'bg_dark': '#1a1a2e',
            'bg_medium': '#16213e',
            'bg_light': '#0f3460',
            'accent': '#e94560',
            'accent2': '#00d4ff',
            'accent3': '#7b2cbf',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'text': '#ffffff',
            'text_dim': '#a0a0b0'
        }
        
        # Configure modern style
        self.root.configure(bg=self.colors['bg_dark'])
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom styles
        style.configure('Modern.TFrame', background=self.colors['bg_dark'])
        style.configure('Card.TFrame', background=self.colors['bg_medium'], 
                       relief='flat', borderwidth=0)
        style.configure('Modern.TLabel', background=self.colors['bg_dark'], 
                       foreground=self.colors['text'], font=('Segoe UI', 10))
        style.configure('Title.TLabel', background=self.colors['bg_dark'], 
                       foreground=self.colors['accent2'], font=('Segoe UI', 24, 'bold'))
        style.configure('Card.TLabel', background=self.colors['bg_medium'], 
                       foreground=self.colors['text'], font=('Segoe UI', 10))
        style.configure('Status.TLabel', background=self.colors['bg_medium'], 
                       foreground=self.colors['accent2'], font=('Segoe UI', 12, 'bold'))
        
        # Create processor
        self.processor = Processor()
        self.animation_running = False
        
        # Create GUI elements
        self.create_widgets()
        
        # Load default program
        self.load_default_program()
        
    def create_widgets(self):
        # Main container with dark background
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title bar with gradient effect
        title_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'], height=80)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(title_frame, text="� 4-Bit Processor Simulator", 
                        font=('Segoe UI', 28, 'bold'),
                        bg=self.colors['bg_dark'], fg=self.colors['accent2'])
        title.pack(side=tk.LEFT, padx=10)
        
        subtitle = tk.Label(title_frame, text="Mind Hackathon 2025 | Real-time HDL Visualization", 
                           font=('Segoe UI', 12),
                           bg=self.colors['bg_dark'], fg=self.colors['text_dim'])
        subtitle.pack(side=tk.LEFT, padx=10, pady=(15, 0))
        
        # Content area - 3 columns
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Controls and Status
        left_frame = self.create_card(content_frame, "⚙️ Control Panel", width=320)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Control buttons with modern styling
        btn_frame = tk.Frame(left_frame, bg=self.colors['bg_medium'])
        btn_frame.pack(pady=10, padx=10)
        
        self.run_btn = self.create_button(btn_frame, "▶ RUN", self.run_program, 
                                          self.colors['success'], row=0, col=0)
        self.step_btn = self.create_button(btn_frame, "⏭ STEP", self.step_cycle, 
                                           self.colors['accent2'], row=0, col=1)
        self.reset_btn = self.create_button(btn_frame, "🔄 RESET", self.reset_processor, 
                                            self.colors['warning'], row=1, col=0)
        self.test_btn = self.create_button(btn_frame, "🧪 TEST", self.run_tests, 
                                           self.colors['accent3'], row=1, col=1)
        
        # Status display with modern cards
        status_container = tk.Frame(left_frame, bg=self.colors['bg_medium'])
        status_container.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(status_container, text="📊 STATUS", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['bg_medium'], fg=self.colors['accent2']).pack(anchor=tk.W, pady=(0, 10))
        
        self.status_labels = {}
        status_items = [
            ("State", "state", self.colors['accent']),
            ("PC", "pc", self.colors['accent2']),
            ("Cycle", "cycle", self.colors['success']),
            ("ALU Out", "alu", self.colors['warning'])
        ]
        
        for label, key, color in status_items:
            status_card = tk.Frame(status_container, bg=self.colors['bg_light'], 
                                  relief='flat', bd=0)
            status_card.pack(fill=tk.X, pady=5)
            
            tk.Label(status_card, text=label, font=('Segoe UI', 9),
                    bg=self.colors['bg_light'], fg=self.colors['text_dim']).pack(anchor=tk.W, padx=10, pady=(5, 0))
            
            self.status_labels[key] = tk.Label(status_card, text="--", 
                                              font=('Segoe UI', 16, 'bold'),
                                              bg=self.colors['bg_light'], fg=color)
            self.status_labels[key].pack(anchor=tk.W, padx=10, pady=(0, 5))
        
        # Memory display with modern styling
        mem_container = tk.Frame(left_frame, bg=self.colors['bg_medium'])
        mem_container.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(mem_container, text="💾 MEMORY", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['bg_medium'], fg=self.colors['accent2']).pack(anchor=tk.W, pady=(0, 10))
        
        self.mem_text = scrolledtext.ScrolledText(mem_container, width=30, height=16, 
                                                  font=('Consolas', 9),
                                                  bg=self.colors['bg_light'], 
                                                  fg=self.colors['text'],
                                                  insertbackground=self.colors['accent2'],
                                                  relief='flat', bd=0)
        self.mem_text.pack(fill=tk.BOTH, expand=True)
        
        # Middle column - Circuit Diagram and Waveforms (SCROLLABLE)
        middle_outer = tk.Frame(content_frame, bg=self.colors['bg_medium'])
        middle_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Add scrollbar
        middle_scroll = tk.Scrollbar(middle_outer, bg=self.colors['bg_medium'])
        middle_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create canvas for scrolling
        middle_canvas = Canvas(middle_outer, bg=self.colors['bg_medium'], 
                              highlightthickness=0, yscrollcommand=middle_scroll.set)
        middle_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        middle_scroll.config(command=middle_canvas.yview)
        
        # Create frame inside canvas
        middle_frame = tk.Frame(middle_canvas, bg=self.colors['bg_medium'])
        middle_canvas.create_window((0, 0), window=middle_frame, anchor='nw', width=580)
        
        # Update scroll region when frame changes size
        def update_scroll_region(event=None):
            middle_canvas.configure(scrollregion=middle_canvas.bbox('all'))
        middle_frame.bind('<Configure>', update_scroll_region)
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            middle_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        middle_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Circuit diagram canvas
        circuit_label = tk.Label(middle_frame, text="📐 Processor Architecture", 
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['bg_medium'], fg=self.colors['accent2'])
        circuit_label.pack(pady=(10, 5), padx=10, anchor=tk.W)
        
        self.circuit_canvas = Canvas(middle_frame, width=540, height=400, 
                                     bg=self.colors['bg_dark'], 
                                     highlightthickness=0, cursor='hand2')
        self.circuit_canvas.pack(padx=10, pady=5)
        self.circuit_canvas.bind('<Button-1>', self.zoom_circuit)
        self.draw_circuit()
        
        # Add zoom hint
        zoom_hint = tk.Label(middle_frame, text="🔍 Click diagram to zoom", 
                            font=('Segoe UI', 9, 'italic'),
                            bg=self.colors['bg_medium'], fg=self.colors['text_dim'])
        zoom_hint.pack(padx=10, anchor=tk.W)
        
        # RAM Comparison Display (Async vs Sync)
        ram_label = tk.Label(middle_frame, text="⚡ RAM Timing Comparison: Async vs Sync", 
                             font=('Segoe UI', 11, 'bold'),
                             bg=self.colors['bg_medium'], fg=self.colors['accent2'])
        ram_label.pack(pady=(15, 5), padx=10, anchor=tk.W)

        # Side-by-side RAM timing canvases
        ram_compare_frame = tk.Frame(middle_frame, bg=self.colors['bg_medium'])
        ram_compare_frame.pack(padx=10, pady=5, fill=tk.X)

        # Async RAM canvas (left)
        async_container = tk.Frame(ram_compare_frame, bg=self.colors['bg_light'], relief='flat', bd=0)
        async_container.pack(side=tk.LEFT, padx=(0, 5), fill=tk.BOTH, expand=True)

        async_title = tk.Label(async_container, text="🔴 ASYNCHRONOUS RAM (Step 6)", 
                              font=('Segoe UI', 9, 'bold'),
                              bg=self.colors['bg_light'], fg=self.colors['accent'])
        async_title.pack(pady=3)

        self.async_canvas = Canvas(async_container, width=270, height=180,
                                   bg=self.colors['bg_dark'], highlightthickness=0)
        self.async_canvas.pack(padx=5, pady=(0, 5))

        # Sync RAM canvas (right)
        sync_container = tk.Frame(ram_compare_frame, bg=self.colors['bg_light'], relief='flat', bd=0)
        sync_container.pack(side=tk.LEFT, padx=(5, 0), fill=tk.BOTH, expand=True)

        sync_title = tk.Label(sync_container, text="🟢 SYNCHRONOUS RAM (Step 8)", 
                             font=('Segoe UI', 9, 'bold'),
                             bg=self.colors['bg_light'], fg=self.colors['success'])
        sync_title.pack(pady=3)

        self.sync_canvas = Canvas(sync_container, width=270, height=180,
                                  bg=self.colors['bg_dark'], highlightthickness=0)
        self.sync_canvas.pack(padx=5, pady=(0, 5))

        # Draw initial RAM comparison
        try:
            self.draw_ram_comparison()
        except Exception:
            # If canvases not ready for some reason, ignore and draw later in update_display
            pass

        # Waveform display
        wave_label = tk.Label(middle_frame, text="〰️ Signal Waveforms", 
                             font=('Segoe UI', 11, 'bold'),
                             bg=self.colors['bg_medium'], fg=self.colors['accent2'])
        wave_label.pack(pady=(10, 5), padx=10, anchor=tk.W)

        self.waveform_canvas = Canvas(middle_frame, width=560, height=220, 
                                      bg=self.colors['bg_light'], 
                                      highlightthickness=0)
        self.waveform_canvas.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Right column - Advanced Features
        right_frame = self.create_card(content_frame, "🚀 Advanced Features", width=450)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Assembly Editor
        asm_label = tk.Label(right_frame, text="✍️ Assembly Editor", 
                            font=('Segoe UI', 11, 'bold'),
                            bg=self.colors['bg_medium'], fg=self.colors['accent2'])
        asm_label.pack(pady=(10, 5), padx=10, anchor=tk.W)
        
        self.asm_text = scrolledtext.ScrolledText(right_frame, width=50, height=8, 
                                                  font=('Consolas', 9),
                                                  bg=self.colors['bg_dark'], 
                                                  fg=self.colors['success'],
                                                  insertbackground=self.colors['accent2'],
                                                  relief='flat', bd=0)
        self.asm_text.pack(padx=10, pady=5, fill=tk.X)
        
        # Assembly editor buttons
        asm_btn_frame = tk.Frame(right_frame, bg=self.colors['bg_medium'])
        asm_btn_frame.pack(padx=10, pady=5, fill=tk.X)
        
        compile_btn = tk.Button(asm_btn_frame, text="⚙️ Compile & Load", 
                               command=self.compile_assembly,
                               font=('Segoe UI', 9, 'bold'),
                               bg=self.colors['accent2'], fg='#ffffff',
                               relief='flat', padx=15, pady=5, cursor='hand2')
        compile_btn.pack(side=tk.LEFT, padx=5)
        
        example_btn = tk.Button(asm_btn_frame, text="📝 Load Example", 
                               command=self.load_example_assembly,
                               font=('Segoe UI', 9, 'bold'),
                               bg=self.colors['accent3'], fg='#ffffff',
                               relief='flat', padx=15, pady=5, cursor='hand2')
        example_btn.pack(side=tk.LEFT, padx=5)
        
        # Critical Path Analyzer
        crit_label = tk.Label(right_frame, text="⚡ Critical Path Analysis", 
                             font=('Segoe UI', 11, 'bold'),
                             bg=self.colors['bg_medium'], fg=self.colors['accent2'])
        crit_label.pack(pady=(15, 5), padx=10, anchor=tk.W)
        
        self.crit_canvas = Canvas(right_frame, width=430, height=120,
                                 bg=self.colors['bg_dark'], highlightthickness=0)
        self.crit_canvas.pack(padx=10, pady=5)
        
        # ALU Visualizer
        alu_viz_label = tk.Label(right_frame, text="🔬 ALU Operation Visualizer", 
                                font=('Segoe UI', 11, 'bold'),
                                bg=self.colors['bg_medium'], fg=self.colors['accent2'])
        alu_viz_label.pack(pady=(15, 5), padx=10, anchor=tk.W)
        
        self.alu_viz_canvas = Canvas(right_frame, width=430, height=180,
                                     bg=self.colors['bg_dark'], highlightthickness=0)
        self.alu_viz_canvas.pack(padx=10, pady=5)
        
        # Execution Log (smaller)
        log_label = tk.Label(right_frame, text="📋 Execution Log", 
                            font=('Segoe UI', 11, 'bold'),
                            bg=self.colors['bg_medium'], fg=self.colors['accent2'])
        log_label.pack(pady=(15, 5), padx=10, anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(right_frame, width=50, height=12, 
                                                  font=('Consolas', 8),
                                                  bg=self.colors['bg_light'], 
                                                  fg=self.colors['text'],
                                                  insertbackground=self.colors['accent2'],
                                                  relief='flat', bd=0)
        self.log_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Initialize advanced features
        self.draw_critical_path()
        self.draw_alu_visualizer()
        self.load_example_assembly()
        
        self.update_display()
    
    def create_card(self, parent, title, width=None):
        """Create a modern card container"""
        card = tk.Frame(parent, bg=self.colors['bg_medium'], relief='flat', bd=0)
        if width:
            card.config(width=width)
        
        # Card title
        title_label = tk.Label(card, text=title, 
                              font=('Segoe UI', 14, 'bold'),
                              bg=self.colors['bg_medium'], 
                              fg=self.colors['text'])
        title_label.pack(pady=(15, 5), padx=15, anchor=tk.W)
        
        # Separator line
        sep = tk.Frame(card, height=2, bg=self.colors['accent'], relief='flat')
        sep.pack(fill=tk.X, padx=15)
        
        return card
    
    def create_button(self, parent, text, command, color, row, col):
        """Create a modern styled button"""
        btn = tk.Button(parent, text=text, command=command,
                       font=('Segoe UI', 10, 'bold'),
                       bg=color, fg='#ffffff',
                       activebackground=color, activeforeground='#ffffff',
                       relief='flat', bd=0,
                       padx=20, pady=10,
                       cursor='hand2')
        btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Hover effects
        def on_enter(e):
            btn.config(bg=self.lighten_color(color))
        def on_leave(e):
            btn.config(bg=color)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def lighten_color(self, hex_color, factor=1.2):
        """Lighten a hex color"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def draw_circuit(self, canvas=None, scale=1.0):
        """Draw the physics-accurate processor architecture diagram"""
        c = canvas if canvas else self.circuit_canvas
        c.delete('all')
        
        # Use the detailed architecture diagram
        if not hasattr(self, 'arch_diagram'):
            self.arch_diagram = ArchitectureDiagram(c, self.colors)
        else:
            self.arch_diagram.canvas = c  # Update canvas reference
        
        self.arch_diagram.draw()
    
    def show_tooltip(self, event, text):
        """Show tooltip on hover"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
        
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(self.tooltip, text=text, 
                        background=self.colors['bg_dark'],
                        foreground=self.colors['accent2'],
                        font=('Segoe UI', 9),
                        relief='solid', borderwidth=1,
                        padx=10, pady=5)
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide tooltip"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            delattr(self, 'tooltip')
    
    def zoom_circuit(self, event=None):
        """Open zoomed circuit diagram in new window"""
        zoom_win = tk.Toplevel(self.root)
        zoom_win.title("🔍 Circuit Diagram - Zoomed View")
        zoom_win.geometry("1200x800")
        zoom_win.configure(bg=self.colors['bg_dark'])
        
        # Title
        title = tk.Label(zoom_win, text="🔌 4-Bit Processor Architecture (Detailed View)", 
                        font=('Segoe UI', 20, 'bold'),
                        bg=self.colors['bg_dark'], fg=self.colors['accent2'])
        title.pack(pady=20)
        
        # Canvas for zoomed diagram
        zoom_canvas = Canvas(zoom_win, width=1100, height=650, 
                            bg=self.colors['bg_light'], 
                            highlightthickness=0)
        zoom_canvas.pack(padx=20, pady=10)
        
        # Draw circuit at 2x scale
        self.draw_circuit(zoom_canvas, scale=2.0)
        
        # Close button
        close_btn = tk.Button(zoom_win, text="✕ Close", 
                             command=zoom_win.destroy,
                             font=('Segoe UI', 10, 'bold'),
                             bg=self.colors['accent'], fg='#ffffff',
                             relief='flat', padx=20, pady=10,
                             cursor='hand2')
        close_btn.pack(pady=10)
    
    def draw_ram_comparison(self):
        """Draw side-by-side async vs sync RAM timing diagrams with live state highlighting"""
        # Get current processor state
        current_state = self.processor.state.name if hasattr(self.processor, 'state') else 'INIT'
        current_cycle = self.processor.cycle_count if hasattr(self.processor, 'cycle_count') else 0
        
        # ASYNCHRONOUS RAM TIMING
        c_async = self.async_canvas
        c_async.delete('all')
        
        width, height = 260, 170
        x_start = 20
        y_base = 20
        step = 35
        pulse_width = 30
        
        # Determine if RAM is active (FETCH, LOAD, or STORE states)
        ram_active = current_state in ['FETCH', 'LOAD', 'STORE']
        is_read = current_state in ['FETCH', 'LOAD']
        is_write = current_state == 'STORE'
        
        # Title features
        c_async.create_text(130, 10, text="Tri-state outputs (4'hZ)", 
                           fill=self.colors['text_dim'], font=('Consolas', 8, 'italic'))
        
        # Signal labels
        signals_async = ['CSN', 'RWN', 'ADDR', 'DOUT']
        colors_async = [self.colors['accent'], self.colors['accent2'], 
                       self.colors['warning'], self.colors['success']]
        
        for i, (sig, color) in enumerate(zip(signals_async, colors_async)):
            y = y_base + i * step
            c_async.create_text(10, y, text=sig, fill=color, 
                              font=('Consolas', 7, 'bold'), anchor=tk.E)
        
        # Draw timing waveforms for ASYNC
        # CSN: active low, immediate response
        y = y_base
        c_async.create_line(x_start, y, x_start+40, y, fill=self.colors['accent'], width=2)
        c_async.create_line(x_start+40, y, x_start+40, y+15, fill=self.colors['accent'], width=2)  # falling edge
        c_async.create_line(x_start+40, y+15, x_start+120, y+15, fill=self.colors['accent'], width=2)  # low
        c_async.create_line(x_start+120, y+15, x_start+120, y, fill=self.colors['accent'], width=2)  # rising edge
        c_async.create_line(x_start+120, y, x_start+220, y, fill=self.colors['accent'], width=2)
        c_async.create_text(x_start+80, y+20, text="ACTIVE", fill=self.colors['accent'], 
                          font=('Consolas', 6, 'bold'))
        
        # RWN: high for read
        y = y_base + step
        c_async.create_line(x_start, y, x_start+40, y, fill=self.colors['accent2'], width=2)
        c_async.create_line(x_start+40, y, x_start+120, y, fill=self.colors['accent2'], width=2)
        c_async.create_line(x_start+120, y, x_start+220, y, fill=self.colors['accent2'], width=2)
        c_async.create_text(x_start+80, y+20, text="READ=1", fill=self.colors['accent2'], 
                          font=('Consolas', 6, 'bold'))
        
        # ADDR: stable address
        y = y_base + 2*step
        c_async.create_line(x_start, y+7, x_start+40, y+7, fill=self.colors['warning'], width=2)
        c_async.create_line(x_start+40, y, x_start+50, y+7, fill=self.colors['warning'], width=2)  # transition
        c_async.create_line(x_start+50, y+14, x_start+40, y+7, fill=self.colors['warning'], width=2)
        c_async.create_line(x_start+50, y, x_start+110, y, fill=self.colors['warning'], width=2)
        c_async.create_line(x_start+50, y+14, x_start+110, y+14, fill=self.colors['warning'], width=2)
        c_async.create_line(x_start+110, y, x_start+120, y+7, fill=self.colors['warning'], width=2)
        c_async.create_line(x_start+110, y+14, x_start+120, y+7, fill=self.colors['warning'], width=2)
        c_async.create_line(x_start+120, y+7, x_start+220, y+7, fill=self.colors['warning'], width=2)
        c_async.create_text(x_start+80, y+20, text="0x4", fill=self.colors['warning'], 
                          font=('Consolas', 7, 'bold'))
        
        # DOUT: immediate valid data (no Z state shown as immediate response)
        y = y_base + 3*step
        c_async.create_line(x_start, y+7, x_start+40, y+7, fill=self.colors['text_dim'], 
                          width=2, dash=(2, 2))
        c_async.create_text(x_start+30, y+20, text="Z", fill=self.colors['text_dim'], 
                          font=('Consolas', 6))
        c_async.create_line(x_start+45, y, x_start+55, y+7, fill=self.colors['success'], width=2)  # transition
        c_async.create_line(x_start+55, y+14, x_start+45, y+7, fill=self.colors['success'], width=2)
        c_async.create_line(x_start+55, y, x_start+115, y, fill=self.colors['success'], width=2)
        c_async.create_line(x_start+55, y+14, x_start+115, y+14, fill=self.colors['success'], width=2)
        c_async.create_text(x_start+85, y+7, text="VALID", fill=self.colors['success'], 
                          font=('Consolas', 7, 'bold'))
        c_async.create_line(x_start+115, y, x_start+125, y+7, fill=self.colors['success'], width=2)
        c_async.create_line(x_start+115, y+14, x_start+125, y+7, fill=self.colors['success'], width=2)
        c_async.create_line(x_start+125, y+7, x_start+220, y+7, fill=self.colors['text_dim'], 
                          width=2, dash=(2, 2))
        c_async.create_text(x_start+170, y+20, text="Z", fill=self.colors['text_dim'], 
                          font=('Consolas', 6))
        
        # Add timing annotation
        c_async.create_line(x_start+45, y_base-10, x_start+45, y_base+3*step+25, 
                          fill=self.colors['accent'], width=1, dash=(1, 2))
        c_async.create_text(x_start+45, y_base+3*step+32, text="t=0", 
                          fill=self.colors['accent'], font=('Consolas', 6))
        c_async.create_text(130, 165, text="⚡ IMMEDIATE response (no clock)", 
                          fill=self.colors['accent'], font=('Consolas', 7, 'bold'))
        
        # SYNCHRONOUS RAM TIMING
        c_sync = self.sync_canvas
        c_sync.delete('all')
        
        # Title features
        c_sync.create_text(130, 10, text="Registered outputs (1-cycle latency)", 
                          fill=self.colors['text_dim'], font=('Consolas', 8, 'italic'))
        
        # Signal labels
        signals_sync = ['CLK', 'CSN', 'ADDR', 'DOUT']
        colors_sync = [self.colors['accent2'], self.colors['accent'], 
                      self.colors['warning'], self.colors['success']]
        
        for i, (sig, color) in enumerate(zip(signals_sync, colors_sync)):
            y = y_base + i * step
            c_sync.create_text(10, y, text=sig, fill=color, 
                             font=('Consolas', 7, 'bold'), anchor=tk.E)
        
        # Draw timing waveforms for SYNC
        # CLK: show 4 clock cycles
        y = y_base
        for i in range(4):
            x = x_start + i*pulse_width*2
            # Rising edge
            c_sync.create_line(x, y+15, x, y, fill=self.colors['accent2'], width=2)
            # High
            c_sync.create_line(x, y, x+pulse_width, y, fill=self.colors['accent2'], width=2)
            # Falling edge
            c_sync.create_line(x+pulse_width, y, x+pulse_width, y+15, fill=self.colors['accent2'], width=2)
            # Low
            c_sync.create_line(x+pulse_width, y+15, x+pulse_width*2, y+15, 
                             fill=self.colors['accent2'], width=2)
        
        # CSN: active during cycles 1-3
        y = y_base + step
        c_sync.create_line(x_start, y, x_start+pulse_width, y, fill=self.colors['accent'], width=2)
        c_sync.create_line(x_start+pulse_width, y, x_start+pulse_width, y+15, 
                         fill=self.colors['accent'], width=2)  # falling
        c_sync.create_line(x_start+pulse_width, y+15, x_start+pulse_width*5, y+15, 
                         fill=self.colors['accent'], width=2)  # active low
        c_sync.create_line(x_start+pulse_width*5, y+15, x_start+pulse_width*5, y, 
                         fill=self.colors['accent'], width=2)  # rising
        c_sync.create_line(x_start+pulse_width*5, y, x_start+220, y, fill=self.colors['accent'], width=2)
        
        # ADDR: stable from cycle 1
        y = y_base + 2*step
        c_sync.create_line(x_start, y+7, x_start+pulse_width, y+7, fill=self.colors['warning'], width=2)
        c_sync.create_line(x_start+pulse_width, y, x_start+pulse_width+10, y+7, 
                         fill=self.colors['warning'], width=2)
        c_sync.create_line(x_start+pulse_width+10, y+14, x_start+pulse_width, y+7, 
                         fill=self.colors['warning'], width=2)
        c_sync.create_line(x_start+pulse_width+10, y, x_start+pulse_width*5, y, 
                         fill=self.colors['warning'], width=2)
        c_sync.create_line(x_start+pulse_width+10, y+14, x_start+pulse_width*5, y+14, 
                         fill=self.colors['warning'], width=2)
        c_sync.create_line(x_start+pulse_width*5, y, x_start+pulse_width*5+10, y+7, 
                         fill=self.colors['warning'], width=2)
        c_sync.create_line(x_start+pulse_width*5, y+14, x_start+pulse_width*5+10, y+7, 
                         fill=self.colors['warning'], width=2)
        c_sync.create_line(x_start+pulse_width*5+10, y+7, x_start+220, y+7, 
                         fill=self.colors['warning'], width=2)
        c_sync.create_text(x_start+pulse_width*3, y+20, text="0x4", 
                         fill=self.colors['warning'], font=('Consolas', 7, 'bold'))
        
        # DOUT: registered output appears NEXT cycle
        y = y_base + 3*step
        c_sync.create_line(x_start, y+7, x_start+pulse_width*3, y+7, 
                         fill=self.colors['text_dim'], width=2, dash=(2, 2))
        c_sync.create_text(x_start+pulse_width*2, y+20, text="OLD", 
                         fill=self.colors['text_dim'], font=('Consolas', 6))
        # Transition at 2nd rising edge
        c_sync.create_line(x_start+pulse_width*3, y, x_start+pulse_width*3+10, y+7, 
                         fill=self.colors['success'], width=2)
        c_sync.create_line(x_start+pulse_width*3+10, y+14, x_start+pulse_width*3, y+7, 
                         fill=self.colors['success'], width=2)
        c_sync.create_line(x_start+pulse_width*3+10, y, x_start+pulse_width*5, y, 
                         fill=self.colors['success'], width=2)
        c_sync.create_line(x_start+pulse_width*3+10, y+14, x_start+pulse_width*5, y+14, 
                         fill=self.colors['success'], width=2)
        c_sync.create_text(x_start+pulse_width*4, y+7, text="VALID", 
                         fill=self.colors['success'], font=('Consolas', 7, 'bold'))
        c_sync.create_line(x_start+pulse_width*5, y, x_start+pulse_width*5+10, y+7, 
                         fill=self.colors['success'], width=2)
        c_sync.create_line(x_start+pulse_width*5, y+14, x_start+pulse_width*5+10, y+7, 
                         fill=self.colors['success'], width=2)
        c_sync.create_line(x_start+pulse_width*5+10, y+7, x_start+220, y+7, 
                         fill=self.colors['success'], width=2)
        
        # Add cycle annotations
        for i in range(3):
            x = x_start + pulse_width + i*pulse_width*2
            c_sync.create_line(x, y_base-10, x, y_base+3*step+25, 
                             fill=self.colors['accent2'], width=1, dash=(1, 2))
            c_sync.create_text(x, y_base+3*step+32, text=f"C{i}", 
                             fill=self.colors['accent2'], font=('Consolas', 6))
        
        c_sync.create_text(130, 165, text="⏱️ 1-CYCLE LATENCY (synchronized)", 
                         fill=self.colors['success'], font=('Consolas', 7, 'bold'))
        
        # ADD REAL-TIME HIGHLIGHTING OVERLAY
        if ram_active:
            # Highlight async RAM active region
            highlight_color = self.colors['success'] if is_read else self.colors['accent']
            c_async.create_rectangle(x_start+40, y_base-5, x_start+120, y_base+3*step+20,
                                    outline=highlight_color, width=3, dash=(4, 2))
            c_async.create_text(x_start+80, y_base-10, text=f"● {current_state}",
                              fill=highlight_color, font=('Consolas', 8, 'bold'))
            
            # Highlight sync RAM - show cycle position
            cycle_pos = (current_cycle % 4)  # Which clock cycle we're in
            highlight_x = x_start + cycle_pos * pulse_width * 2
            c_sync.create_rectangle(highlight_x, y_base-5, highlight_x+pulse_width*2, y_base+3*step+20,
                                   outline=highlight_color, width=3, dash=(4, 2))
            c_sync.create_text(highlight_x+pulse_width, y_base-10, text=f"● {current_state}",
                             fill=highlight_color, font=('Consolas', 8, 'bold'))
    
    def compile_assembly(self):
        """Compile assembly code to machine code and load into processor"""
        asm_code = self.asm_text.get("1.0", tk.END).strip()
        
        # ISA mapping
        opcodes = {
            'STO': 0b000, 'ADD': 0b001, 'SUB': 0b010,
            'AND': 0b011, 'OR': 0b100, 'XOR': 0b101, 'NOT': 0b110
        }
        
        program = []
        errors = []
        
        for line_num, line in enumerate(asm_code.split('\n'), 1):
            line = line.split('//')[0].strip()  # Remove comments
            if not line:
                continue
                
            parts = line.replace(',', ' ').split()
            if len(parts) < 2:
                errors.append(f"Line {line_num}: Invalid syntax")
                continue
            
            mnemonic = parts[0].upper()
            if mnemonic not in opcodes:
                errors.append(f"Line {line_num}: Unknown instruction '{mnemonic}'")
                continue
            
            try:
                op1 = int(parts[1], 0) & 0xF  # Support 0x prefix
                op2 = int(parts[2], 0) & 0xF if len(parts) > 2 else 0
                
                # Encode: [opcode(3) | op1(4) | op2(4)] = 11 bits
                instruction = (opcodes[mnemonic] << 8) | (op1 << 4) | op2
                program.append(instruction)
                
            except (ValueError, IndexError):
                errors.append(f"Line {line_num}: Invalid operands")
        
        if errors:
            self.log("\n".join(errors))
            return
        
        # Load program into processor
        self.processor.load_program(program)
        self.reset_processor()
        self.log(f"✅ Compiled {len(program)} instructions successfully!")
        self.log(f"Machine code: {[f'0x{i:03X}' for i in program]}")
    
    def load_example_assembly(self):
        """Load random example assembly program - different each time!"""
        import random
        
        examples = [
            # Example 1: Basic Arithmetic
            """// Program 1: Basic Arithmetic Operations
STO 0x4, 0x5    // Store 5 at address 4
ADD 0x4, 0x6    // Add 6 to mem[4] (5+6=11)
STO 0x1, 0xF    // Store 15 at address 1
SUB 0x1, 0x7    // Subtract 7 from mem[1] (15-7=8)
NOT 0xF, 0x0    // NOT mem[15] (~0=15)
XOR 0x4, 0x3    // XOR mem[4] with 3""",
            
            # Example 2: Bitwise Logic Showcase
            """// Program 2: Bitwise Logic Operations
STO 0x2, 0xA    // Store 1010 (10) at addr 2
AND 0x2, 0x3    // AND with 0011 (3) → 0010 (2)
STO 0x3, 0xC    // Store 1100 (12) at addr 3
OR  0x3, 0x5    // OR with 0101 (5) → 1101 (13)
STO 0x5, 0x9    // Store 1001 (9) at addr 5
XOR 0x5, 0x6    // XOR with 0110 (6) → 1111 (15)
NOT 0x2, 0x0    // NOT mem[2] → 1101 (13)""",
            
            # Example 3: Complex Arithmetic Chain
            """// Program 3: Arithmetic Chain (Fibonacci-like)
STO 0x0, 0x1    // F0 = 1
STO 0x1, 0x1    // F1 = 1
ADD 0x0, 0x1    // F0 = F0 + 1 = 2
ADD 0x1, 0x2    // F1 = F1 + 2 = 3
ADD 0x0, 0x3    // F0 = F0 + 3 = 5
ADD 0x1, 0x5    // F1 = F1 + 5 = 8
SUB 0x0, 0x3    // F0 = F0 - 3 = 2""",
            
            # Example 4: Memory Manipulation
            """// Program 4: Memory Copy & Transform
STO 0x8, 0x7    // Store 0111 (7) at addr 8
ADD 0x8, 0x0    // Read mem[8] (acts as MOV)
STO 0x9, 0x7    // Copy to addr 9
NOT 0x8, 0x0    // Invert mem[8] → 1000 (8)
XOR 0x9, 0xF    // XOR mem[9] with 1111 → 1000 (8)
AND 0x8, 0x9    // AND of both → result""",
            
            # Example 5: Overflow Test
            """// Program 5: Overflow & Underflow Test
STO 0xA, 0xF    // Store max value (15) at addr A
ADD 0xA, 0x1    // 15 + 1 = 16 → 0 (overflow!)
STO 0xB, 0x0    // Store 0 at addr B
SUB 0xB, 0x1    // 0 - 1 = -1 → 15 (underflow!)
ADD 0xA, 0x8    // 0 + 8 = 8
ADD 0xB, 0x7    // 15 + 7 = 22 → 6 (overflow)""",
            
            # Example 6: Logic Pattern Generator
            """// Program 6: Pattern Generation
STO 0xC, 0x5    // Store 0101 pattern
XOR 0xC, 0xA    // XOR with 1010 → 1111 (15)
AND 0xC, 0x6    // AND with 0110 → 0110 (6)
OR  0xC, 0x9    // OR with 1001 → 1111 (15)
NOT 0xC, 0x0    // NOT → 0000 (0)
STO 0xD, 0x3    // Store final result
XOR 0xD, 0xC    // XOR with previous""",
            
            # Example 7: Nested Operations
            """// Program 7: Nested Arithmetic
STO 0x6, 0x2    // a = 2
STO 0x7, 0x3    // b = 3
ADD 0x6, 0x4    // a = a + 4 = 6
ADD 0x7, 0x5    // b = b + 5 = 8
SUB 0x6, 0x2    // a = a - 2 = 4
SUB 0x7, 0x3    // b = b - 3 = 5
AND 0x6, 0x7    // a = a & mem[7]""",
            
            # Example 8: All Operations Test
            """// Program 8: Complete ISA Test
STO 0xE, 0x8    // Test STO: store 8
ADD 0xE, 0x4    // Test ADD: 8+4=12
SUB 0xE, 0x3    // Test SUB: 12-3=9
AND 0xE, 0xD    // Test AND: 1001&1101=1001 (9)
OR  0xE, 0x2    // Test OR: 1001|0010=1011 (11)
XOR 0xE, 0x5    // Test XOR: 1011^0101=1110 (14)
NOT 0xE, 0x0    // Test NOT: ~1110=0001 (1)"""
        ]
        
        # Pick a random example
        example = random.choice(examples)
        
        self.asm_text.delete("1.0", tk.END)
        self.asm_text.insert("1.0", example)
        
        # Syntax highlighting
        self.asm_text.tag_config('comment', foreground=self.colors['text_dim'])
        self.asm_text.tag_config('instruction', foreground=self.colors['accent2'])
        self.asm_text.tag_config('operand', foreground=self.colors['warning'])
        
        # Apply syntax highlighting
        for i, line in enumerate(example.split('\n'), 1):
            if '//' in line:
                comment_start = line.index('//')
                self.asm_text.tag_add('comment', f"{i}.{comment_start}", f"{i}.end")
        
        # Log which example was loaded
        program_name = example.split('\n')[0].replace('//', '').strip()
        self.log(f"📝 Loaded: {program_name}")
    
    def draw_critical_path(self):
        """Draw critical path analysis with timing information"""
        c = self.crit_canvas
        c.delete('all')
        
        # Gate delays (in arbitrary time units)
        delays = {
            'NOT': 1,
            'AND/OR': 2,
            'XOR (custom)': 5,  # (A & ~B) | (~A & B) = 2 AND + 2 NOT + 1 OR
            'FA': 10,  # 2× XOR + AND + OR
            'Adder_4b': 40,  # 4× FA ripple
            'ALU': 45,  # Adder + mux overhead
            'Register': 2  # Setup time
        }
        
        # Critical path: RAM → ALU → Register
        paths = [
            {'name': 'RAM Output', 'delay': 3, 'color': self.colors['text_dim']},
            {'name': 'ALU (4-bit Ripple Adder)', 'delay': 45, 'color': self.colors['accent']},
            {'name': 'ALU Register', 'delay': 2, 'color': self.colors['success']},
        ]
        
        total_delay = sum(p['delay'] for p in paths)
        max_freq = 1000 / total_delay  # MHz (assuming 1 time unit = 1 ns)
        
        # Draw title
        c.create_text(215, 10, text=f"Critical Path: {total_delay} ns → Max Freq: ~{max_freq:.0f} MHz",
                     fill=self.colors['accent2'], font=('Segoe UI', 10, 'bold'))
        
        # Draw path blocks
        x_start = 10
        y = 35
        max_width = 410
        
        for path in paths:
            width = (path['delay'] / total_delay) * max_width
            
            # Draw block
            c.create_rectangle(x_start, y, x_start + width, y + 30,
                             fill=path['color'], outline=self.colors['text'], width=2)
            
            # Label
            c.create_text(x_start + width/2, y + 15, text=f"{path['name']}\n{path['delay']}ns",
                         fill='#ffffff', font=('Consolas', 7, 'bold'))
            
            x_start += width
        
        # Bottleneck indicator
        c.create_text(215, 75, text="🔴 Bottleneck: Ripple-Carry Adder (45 ns)",
                     fill=self.colors['accent'], font=('Consolas', 9, 'bold'))
        c.create_text(215, 92, text="💡 Optimization: Use Carry-Lookahead Adder → ~20 ns",
                     fill=self.colors['success'], font=('Consolas', 8, 'italic'))
        c.create_text(215, 107, text=f"⚙️ Current: {max_freq:.0f} MHz  |  Optimized: ~{1000/28:.0f} MHz",
                     fill=self.colors['warning'], font=('Consolas', 8, 'bold'))
    
    def draw_alu_visualizer(self):
        """Draw ALU operation visualization with gate-level detail"""
        c = self.alu_viz_canvas
        c.delete('all')
        
        # Get current processor state
        current_state = self.processor.state.name if hasattr(self.processor, 'state') else 'INIT'
        
        # Get REAL instruction data from processor
        instruction = getattr(self.processor, 'instruction', 0)
        opcode = (instruction >> 8) & 0x7
        op1 = (instruction >> 4) & 0xF
        op2 = instruction & 0xF
        
        # Decode operation
        ops = ['STO', 'ADD', 'SUB', 'AND', 'OR', 'XOR', 'NOT']
        operation = ops[opcode] if opcode < len(ops) else 'STO'
        
        # Get REAL ALU operands from processor memory
        alu_a = self.processor.memory[op1] if op1 < len(self.processor.memory) else 0
        alu_b = op2  # Immediate operand from instruction
        
        # Highlight if currently executing
        is_active = (current_state == 'EXECUTE')
        title_color = self.colors['accent'] if is_active else self.colors['text_dim']
        state_indicator = "● ACTIVE" if is_active else "○ IDLE"
        
        # Title with real-time state
        c.create_text(215, 10, 
                     text=f"{state_indicator} | {operation} | mem[0x{op1:X}]={alu_a:04b} ({alu_a}), imm={alu_b:04b} ({alu_b})",
                     fill=title_color, font=('Segoe UI', 9, 'bold'))
        
        if operation in ['ADD', 'SUB']:
            # Draw adder chain visualization
            x_start = 20
            y_start = 35
            
            # Show 4-bit ripple carry adder
            for i in range(4):
                x = x_start + i * 100
                
                # Full Adder block - highlight if executing
                block_color = self.colors['accent'] if is_active else self.colors['bg_medium']
                border_color = self.colors['success'] if is_active else self.colors['accent2']
                c.create_rectangle(x, y_start, x+80, y_start+60,
                                 fill=block_color, outline=border_color, width=3 if is_active else 2)
                c.create_text(x+40, y_start+15, text=f"FA{i}",
                            fill=border_color, font=('Consolas', 10, 'bold'))
                
                # Input bits
                a_bit = (alu_a >> i) & 1
                b_bit = (alu_b >> i) & 1
                
                c.create_text(x+20, y_start+35, text=f"A[{i}]={a_bit}",
                            fill=self.colors['success'], font=('Consolas', 7))
                c.create_text(x+60, y_start+35, text=f"B[{i}]={b_bit}",
                            fill=self.colors['warning'], font=('Consolas', 7))
                
                # Calculate sum and carry for this bit
                if operation == 'SUB':
                    b_bit = 1 - b_bit  # Invert for subtraction
                
                cin = 1 if (operation == 'SUB' and i == 0) else 0
                if i > 0:
                    # Get carry from previous stage
                    prev_a = (alu_a >> (i-1)) & 1
                    prev_b = (alu_b >> (i-1)) & 1
                    if operation == 'SUB':
                        prev_b = 1 - prev_b
                    cin = 1 if (prev_a + prev_b + (1 if operation == 'SUB' and i == 1 else 0) > 1) else 0
                
                s = (a_bit + b_bit + cin) & 1
                cout = 1 if (a_bit + b_bit + cin > 1) else 0
                
                c.create_text(x+40, y_start+50, text=f"S={s} C={cout}",
                            fill=self.colors['accent'], font=('Consolas', 8, 'bold'))
                
                # Carry chain arrow
                if i < 3:
                    c.create_line(x+80, y_start+30, x+100, y_start+30,
                                arrow=tk.LAST, fill=self.colors['accent'], width=2)
                    c.create_text(x+90, y_start+20, text=f"C{i}",
                                fill=self.colors['accent'], font=('Consolas', 6))
        
        elif operation == 'XOR':
            # Draw XOR gate array
            for i in range(4):
                x = 50 + i * 90
                y = 50
                
                # XOR gate symbol - highlight if executing
                gate_color = self.colors['accent'] if is_active else self.colors['accent2']
                gate_width = 3 if is_active else 2
                c.create_oval(x, y, x+60, y+50, outline=gate_color, width=gate_width)
                c.create_text(x+30, y+25, text="XOR",
                            fill=gate_color, font=('Consolas', 9, 'bold'))
                
                # Bits
                a_bit = (alu_a >> i) & 1
                b_bit = (alu_b >> i) & 1
                result = a_bit ^ b_bit
                
                c.create_text(x+30, y-10, text=f"[{i}]",
                            fill=self.colors['text_dim'], font=('Consolas', 7))
                c.create_text(x+10, y+25, text=str(a_bit),
                            fill=self.colors['success'], font=('Consolas', 10, 'bold'))
                c.create_text(x+50, y+25, text=str(b_bit),
                            fill=self.colors['warning'], font=('Consolas', 10, 'bold'))
                c.create_text(x+30, y+65, text=str(result),
                            fill=self.colors['accent'], font=('Consolas', 12, 'bold'))
        
        else:
            # Simple operation display
            result_map = {
                'AND': alu_a & alu_b,
                'OR': alu_a | alu_b,
                'NOT': (~alu_a) & 0xF,
                'STO': alu_b
            }
            result = result_map.get(operation, 0)
            
            c.create_text(215, 70, text=f"{operation} Operation",
                         fill=self.colors['accent2'], font=('Segoe UI', 14, 'bold'))
            c.create_text(215, 105, text=f"Result = {result:04b} ({result})",
                         fill=self.colors['success'], font=('Consolas', 16, 'bold'))
        
        # Final result - use REAL ALU result from processor
        final_result = self.processor.alu_result if hasattr(self.processor, 'alu_result') else 0
        result_color = self.colors['success'] if is_active else self.colors['text_dim']
        
        c.create_text(215, 140, text=f"{'✅' if is_active else '○'} ALU Result: {final_result:04b} ({final_result})",
                     fill=result_color, font=('Consolas', 11, 'bold'))
        
        # Show if overflow occurred
        if operation in ['ADD', 'SUB']:
            full_result = alu_a + alu_b if operation == 'ADD' else alu_a - alu_b
            if full_result > 15 or full_result < 0:
                c.create_text(215, 160, text="⚠️ Overflow/Underflow detected",
                            fill=self.colors['accent'], font=('Consolas', 9, 'italic'))
    
    def draw_waveforms(self):
        """Draw real-time signal waveforms"""
        c = self.waveform_canvas
        c.delete('all')
        
        if not self.processor.waveform_history['clk']:
            c.create_text(280, 140, text="⏳ Run program to see waveforms", 
                         fill=self.colors['text_dim'], font=('Segoe UI', 12, 'italic'))
            return
        
        # Get data
        history = self.processor.waveform_history
        max_cycles = min(50, len(history['clk']))  # Show last 50 cycles
        
        if max_cycles == 0:
            return
        
        # Canvas dimensions
        width = 540
        height = 200
        margin_left = 60
        margin_top = 15
        signal_height = 30
        
        # Scale
        x_scale = (width - margin_left - 20) / max(1, max_cycles - 1)
        
        # Signals to display
        signals = [
            ('CLK', history['clk'][-max_cycles:], self.colors['accent2'], 0, 1),
            ('PC', history['pc'][-max_cycles:], self.colors['success'], 0, 15),
            ('State', history['state'][-max_cycles:], self.colors['warning'], 0, 4),
            ('ALU', history['alu_out'][-max_cycles:], self.colors['accent'], 0, 15),
        ]
        
        for idx, (name, data, color, min_val, max_val) in enumerate(signals):
            y_base = margin_top + idx * signal_height
            
            # Draw signal name
            c.create_text(30, y_base + 15, text=name, 
                         fill=color, font=('Segoe UI', 9, 'bold'), anchor=tk.W)
            
            # Draw baseline
            c.create_line(margin_left, y_base + 25, width, y_base + 25, 
                         fill=self.colors['text_dim'], width=1, dash=(2, 2))
            
            # Draw waveform
            if len(data) > 1:
                points = []
                for i, val in enumerate(data):
                    x = margin_left + i * x_scale
                    # Normalize value
                    normalized = (val - min_val) / max(1, max_val - min_val)
                    y = y_base + 25 - (normalized * 20)
                    points.extend([x, y])
                
                if len(points) >= 4:
                    c.create_line(points, fill=color, width=2, smooth=False)
                    
                    # Draw value at last point
                    if len(data) > 0:
                        last_val = data[-1]
                        c.create_text(width - 10, y_base + 5, 
                                    text=f"{last_val:X}" if isinstance(last_val, int) else str(last_val), 
                                    fill=color, font=('Consolas', 8, 'bold'), 
                                    anchor=tk.E)
        
        # Grid lines
        for i in range(0, max_cycles, 5):
            x = margin_left + i * x_scale
            c.create_line(x, margin_top, x, height - 20, 
                         fill=self.colors['text_dim'], width=1, dash=(1, 3))
            c.create_text(x, height - 10, text=str(len(history['clk']) - max_cycles + i), 
                         fill=self.colors['text_dim'], font=('Consolas', 7))
    
    def load_default_program(self):
        """Load the sample test program"""
        # Sample program from program.mem
        # Binary strings converted to integers
        program = [
            0b00001000101,  # STO 0x4 0x5
            0b00101000110,  # ADD 0x4 0x6
            0b00000011111,  # STO 0x1 0xF
            0b01000010111,  # SUB 0x1 0x7
            0b11011110000,  # NOT 0xF 0x0
        ]
        self.processor.load_program(program)
        self.log("✅ Loaded sample program (5 instructions)")
    
    def run_program(self):
        """Run the complete program with animation"""
        self.log("▶ Running program...")
        self.animation_running = True
        self.animate_execution()
    
    def animate_execution(self):
        """Animate program execution"""
        if self.animation_running:
            running = self.processor.clock_cycle()
            self.update_display()
            
            if running:
                self.root.after(300, self.animate_execution)  # 300ms delay
            else:
                self.animation_running = False
                self.log("✅ Program execution complete!")
                self.check_results()
    
    def step_cycle(self):
        """Execute one clock cycle"""
        running = self.processor.clock_cycle()
        self.update_display()
        if not running:
            self.log("✅ Program complete")
    
    def reset_processor(self):
        """Reset processor to initial state"""
        self.processor.reset()
        self.load_default_program()
        self.update_display()
        self.log("🔄 Processor reset")
    
    def update_display(self):
        """Update all display elements"""
        # Update status with colors based on state
        state_colors = {
            'INIT': self.colors['text_dim'],
            'FETCH': self.colors['accent2'],
            'LOAD': self.colors['warning'],
            'EXECUTE': self.colors['accent'],
            'STORE': self.colors['success']
        }
        
        state_name = self.processor.state.name
        self.status_labels["state"].config(text=state_name, 
                                          fg=state_colors.get(state_name, self.colors['text']))
        self.status_labels["pc"].config(text=f"0x{self.processor.pc:X}")
        self.status_labels["cycle"].config(text=str(self.processor.cycle_count))
        self.status_labels["alu"].config(text=f"0x{self.processor.alu_result:X}")
        
        # Update memory display with highlighting
        self.mem_text.delete(1.0, tk.END)
        self.mem_text.insert(tk.END, "╔═════╦═══════╦══════════╗\n", 'header')
        self.mem_text.insert(tk.END, "║ Addr║ Value ║  Binary  ║\n", 'header')
        self.mem_text.insert(tk.END, "╠═════╬═══════╬══════════╣\n", 'header')
        
        for i in range(16):
            val = self.processor.memory[i]
            line = f"║  {i:X}  ║   {val:X}   ║  {val:04b}  ║\n"
            
            # Highlight non-zero values
            if val != 0:
                self.mem_text.insert(tk.END, line, 'highlight')
            else:
                self.mem_text.insert(tk.END, line)
        
        self.mem_text.insert(tk.END, "╚═════╩═══════╩══════════╝\n", 'header')
        
        # Configure tags
        self.mem_text.tag_config('header', foreground=self.colors['accent2'])
        self.mem_text.tag_config('highlight', foreground=self.colors['success'], 
                                font=('Consolas', 9, 'bold'))
        
        # Update execution log with colors
        self.log_text.delete(1.0, tk.END)
        for line in self.processor.execution_log:
            if 'FETCH' in line:
                self.log_text.insert(tk.END, line + "\n", 'fetch')
            elif 'EXECUTE' in line:
                self.log_text.insert(tk.END, line + "\n", 'execute')
            elif 'STORE' in line:
                self.log_text.insert(tk.END, line + "\n", 'store')
            else:
                self.log_text.insert(tk.END, line + "\n")
        
        self.log_text.tag_config('fetch', foreground=self.colors['accent2'])
        self.log_text.tag_config('execute', foreground=self.colors['accent'])
        self.log_text.tag_config('store', foreground=self.colors['success'])
        self.log_text.see(tk.END)
        
        # Update RAM comparison with live highlighting
        self.draw_ram_comparison()
        
        # Update critical path analyzer (static but always visible)
        self.draw_critical_path()
        
        # Update ALU visualizer with real-time processor state
        self.draw_alu_visualizer()
        
        # Update waveforms
        self.draw_waveforms()
    
    def log(self, message: str):
        """Add message to log with color"""
        if '✅' in message or 'PASS' in message:
            self.log_text.insert(tk.END, f"{message}\n", 'success')
            self.log_text.tag_config('success', foreground=self.colors['success'])
        elif '❌' in message or 'FAIL' in message:
            self.log_text.insert(tk.END, f"{message}\n", 'error')
            self.log_text.tag_config('error', foreground=self.colors['accent'])
        elif '▶' in message or 'Running' in message:
            self.log_text.insert(tk.END, f"{message}\n", 'info')
            self.log_text.tag_config('info', foreground=self.colors['accent2'])
        else:
            self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def check_results(self):
        """Check if program results are correct"""
        # Program trace:
        # Instr 0: STO 0x4 0x5 → mem[0x4] = 0x5
        # Instr 1: ADD 0x4 0x6 → mem[0x4] = mem[0x4] + 0x6 = 0x5 + 0x6 = 0xB
        # Instr 2: STO 0x1 0xF → mem[0x1] = 0xF
        # Instr 3: SUB 0x1 0x7 → mem[0x1] = mem[0x1] - 0x7 = 0xF - 0x7 = 0x8
        # Instr 4: NOT 0xF 0x0 → mem[0xF] = ~mem[0xF] = ~0x0 = 0xF
        expected = {
            0x1: 0x8,  # 15 - 7 = 8
            0x4: 0xB,  # 5 + 6 = 11
            0xF: 0xF,  # ~0 = 15
        }
        
        self.log("\n=== VERIFICATION ===")
        all_pass = True
        for addr, expected_val in expected.items():
            actual = self.processor.memory[addr]
            status = "✅ PASS" if actual == expected_val else "❌ FAIL"
            self.log(f"mem[0x{addr:X}] = 0x{actual:X} (expected 0x{expected_val:X}) {status}")
            if actual != expected_val:
                all_pass = False
        
        if all_pass:
            self.log("\n🎉 ALL TESTS PASSED! 🎉")
        else:
            self.log("\n❌ Some tests failed")
    
    def run_tests(self):
        """Run unit tests"""
        self.log("\n=== RUNNING UNIT TESTS ===\n")
        
        # Test XOR
        self.log("Testing XOR_1b...")
        tests = [(0,0,0), (0,1,1), (1,0,1), (1,1,0)]
        xor_pass = all(XOR_1b.compute(a, b) == expected for a, b, expected in tests)
        self.log(f"  XOR_1b: {'✅ PASS' if xor_pass else '❌ FAIL'}")
        
        # Test Full Adder
        self.log("Testing FA_1b...")
        fa_pass = True
        s, c = FA_1b.compute(1, 1, 1)
        if s != 1 or c != 1:
            fa_pass = False
        self.log(f"  FA_1b: {'✅ PASS' if fa_pass else '❌ FAIL'}")
        
        # Test 4-bit Adder
        self.log("Testing Adder_4b...")
        result, cout = Adder_4b.compute(5, 6, False)
        adder_pass = (result == 11 and cout == False)
        self.log(f"  Adder_4b (5+6): {'✅ PASS' if adder_pass else '❌ FAIL'}")
        
        # Test ALU
        self.log("Testing ALU_4b...")
        alu_tests = [
            (10, 6, 0b001, False, 0, True),  # 10+6=16 (overflow)
            (10, 6, 0b010, True, 4, True),   # 10-6=4
            (10, 6, 0b011, False, 2, False), # 10&6=2
            (10, 6, 0b100, False, 14, False),# 10|6=14
            (10, 6, 0b101, False, 12, False),# 10^6=12
        ]
        alu_pass = True
        for a, b, s, cin, exp_f, exp_c in alu_tests:
            f, c = ALU_4b.compute(a, b, s, cin)
            if f != exp_f:
                alu_pass = False
        self.log(f"  ALU_4b: {'✅ PASS' if alu_pass else '❌ FAIL'}")
        
        # Run integration test
        self.log("\nTesting Full Processor...")
        self.reset_processor()
        self.run_program()

# ============================================================
# MAIN
# ============================================================

def main():
    root = tk.Tk()
    app = ProcessorSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
