"""
Physics-Accurate 4-bit Load-Store Processor Architecture Diagram
Showing all components with precise bus widths and control signals
"""

import tkinter as tk
from tkinter import Canvas

class ArchitectureDiagram:
    """
    Complete architecture diagram with:
    - 4-bit data paths (thick lines)
    - 1-bit control signals (thin dashed lines)
    - All components labeled per technical specs
    - Sequential flow visualization
    """
    
    def __init__(self, canvas, colors):
        self.canvas = canvas
        self.colors = colors
        self.width = 540
        self.height = 400
        
    def draw(self):
        """Draw the complete architecture diagram - CLEAN AND ORGANIZED"""
        c = self.canvas
        c.delete('all')
        
        # Title
        c.create_text(270, 15, text="4-Bit Load-Store Processor Architecture",
                     fill=self.colors['accent2'], font=('Segoe UI', 11, 'bold'))
        
        # Legend (compact)
        self.draw_legend_compact()
        
        # Component positions (clean horizontal flow: PC → RAM → ALU → REG)
        pc_pos = (70, 100)
        addr_mux_pos = (140, 100)
        ram_pos = (240, 100)
        alu_pos = (380, 100)
        alu_reg_pos = (480, 100)
        
        # Bottom row: FSM and IR
        fsm_pos = (70, 240)
        ir_pos = (240, 240)
        data_mux_pos = (240, 180)
        
        # Draw components (simplified, cleaner)
        self.draw_pc_simple(pc_pos)
        self.draw_addr_mux_simple(addr_mux_pos)
        self.draw_ram_simple(ram_pos)
        self.draw_alu_simple(alu_pos)
        self.draw_alu_register_simple(alu_reg_pos)
        self.draw_fsm_simple(fsm_pos)
        self.draw_ir_simple(ir_pos)
        self.draw_data_mux_simple(data_mux_pos)
        
        # Draw data paths (clean routing)
        self.draw_clean_datapath()
        
        # Draw control signals (minimal, clear)
        self.draw_clean_control()
        
        # Clock tree (simple horizontal line)
        self.draw_simple_clock()
        
        # State annotations (compact)
        self.draw_compact_states()
        
    def draw_legend_compact(self):
        """Draw compact legend"""
        c = self.canvas
        x, y = 15, 35
        
        # Data path
        c.create_line(x, y, x+25, y, fill=self.colors['accent2'], width=2)
        c.create_text(x+30, y, text="Data[4]", anchor='w',
                     fill=self.colors['text'], font=('Consolas', 7))
        
        # Control signal
        c.create_line(x+80, y, x+105, y, fill=self.colors['warning'], 
                     width=1, dash=(2, 2))
        c.create_text(x+110, y, text="Control[1]", anchor='w',
                     fill=self.colors['text'], font=('Consolas', 7))
        
        # Clock
        c.create_line(x+180, y, x+205, y, fill=self.colors['success'], width=2)
        c.create_text(x+210, y, text="CLK", anchor='w',
                     fill=self.colors['text'], font=('Consolas', 7))
    
    def draw_pc_simple(self, pos):
        """Draw simple PC box"""
        c = self.canvas
        x, y = pos
        c.create_rectangle(x-25, y-20, x+25, y+20,
                          fill=self.colors['bg_light'], outline=self.colors['accent2'], width=2)
        c.create_text(x, y-8, text="PC", fill=self.colors['accent2'], font=('Consolas', 9, 'bold'))
        c.create_text(x, y+8, text="[4b]", fill=self.colors['text_dim'], font=('Consolas', 6))
        self.pc_pos = pos
    
    def draw_addr_mux_simple(self, pos):
        """Draw simple address mux"""
        c = self.canvas
        x, y = pos
        points = [x-15, y-15, x+15, y-15, x, y+15]
        c.create_polygon(points, fill=self.colors['bg_medium'], outline=self.colors['accent2'], width=2)
        c.create_text(x, y, text="MUX", fill=self.colors['text'], font=('Consolas', 6, 'bold'))
        self.addr_mux_pos = pos
    
    def draw_ram_simple(self, pos):
        """Draw simple RAM box"""
        c = self.canvas
        x, y = pos
        c.create_rectangle(x-40, y-30, x+40, y+30,
                          fill=self.colors['bg_light'], outline=self.colors['accent'], width=3)
        c.create_text(x, y-15, text="RAM", fill=self.colors['accent'], font=('Consolas', 10, 'bold'))
        c.create_text(x, y, text="16×4", fill=self.colors['text'], font=('Consolas', 8))
        c.create_text(x, y+15, text="sync", fill=self.colors['text_dim'], font=('Consolas', 6, 'italic'))
        self.ram_pos = pos
    
    def draw_alu_simple(self, pos):
        """Draw simple ALU"""
        c = self.canvas
        x, y = pos
        points = [x-30, y-25, x+30, y-25, x+25, y+25, x-25, y+25]
        c.create_polygon(points, fill=self.colors['bg_light'], outline=self.colors['accent'], width=2)
        c.create_text(x, y-10, text="ALU", fill=self.colors['accent'], font=('Consolas', 9, 'bold'))
        c.create_text(x, y+8, text="4-bit", fill=self.colors['text'], font=('Consolas', 7))
        self.alu_pos = pos
    
    def draw_alu_register_simple(self, pos):
        """Draw simple ALU register"""
        c = self.canvas
        x, y = pos
        c.create_rectangle(x-25, y-20, x+25, y+20,
                          fill=self.colors['bg_light'], outline=self.colors['success'], width=2)
        c.create_text(x, y-8, text="REG", fill=self.colors['success'], font=('Consolas', 8, 'bold'))
        c.create_text(x, y+8, text="ALU", fill=self.colors['text'], font=('Consolas', 6))
        self.alu_reg_pos = pos
    
    def draw_fsm_simple(self, pos):
        """Draw simple FSM box"""
        c = self.canvas
        x, y = pos
        c.create_rectangle(x-35, y-35, x+35, y+35,
                          fill=self.colors['bg_light'], outline=self.colors['warning'], width=2)
        c.create_text(x, y-20, text="FSM", fill=self.colors['warning'], font=('Consolas', 9, 'bold'))
        c.create_text(x, y-8, text="5-State", fill=self.colors['text'], font=('Consolas', 6))
        c.create_text(x, y+2, text="Control", fill=self.colors['text'], font=('Consolas', 6))
        c.create_text(x, y+15, text="Unit", fill=self.colors['text'], font=('Consolas', 6))
        self.fsm_pos = pos
    
    def draw_ir_simple(self, pos):
        """Draw simple instruction register"""
        c = self.canvas
        x, y = pos
        c.create_rectangle(x-40, y-25, x+40, y+25,
                          fill=self.colors['bg_light'], outline=self.colors['warning'], width=2)
        c.create_text(x, y-12, text="IR [11b]", fill=self.colors['warning'], font=('Consolas', 8, 'bold'))
        c.create_text(x, y+2, text="op[3] a[4]", fill=self.colors['text'], font=('Consolas', 6))
        c.create_text(x, y+12, text="imm[4]", fill=self.colors['text'], font=('Consolas', 6))
        self.ir_pos = pos
    
    def draw_data_mux_simple(self, pos):
        """Draw simple data mux"""
        c = self.canvas
        x, y = pos
        points = [x-15, y-15, x+15, y-15, x, y+15]
        c.create_polygon(points, fill=self.colors['bg_medium'], outline=self.colors['accent2'], width=2)
        c.create_text(x, y, text="MUX", fill=self.colors['text'], font=('Consolas', 6, 'bold'))
        self.data_mux_pos = pos
    
    def draw_clean_datapath(self):
        """Draw clean, organized data paths"""
        c = self.canvas
        
        # PC → Addr MUX
        self.draw_arrow(self.pc_pos[0]+25, self.pc_pos[1], 
                       self.addr_mux_pos[0]-15, self.addr_mux_pos[1]-10, width=2)
        
        # Addr MUX → RAM
        self.draw_arrow(self.addr_mux_pos[0], self.addr_mux_pos[1]+15,
                       self.ram_pos[0]-40, self.ram_pos[1]-15, width=2, label="addr[4]")
        
        # RAM → ALU
        self.draw_arrow(self.ram_pos[0]+40, self.ram_pos[1]-10,
                       self.alu_pos[0]-30, self.alu_pos[1]-15, width=2, label="A[4]")
        
        # RAM → IR (instruction)
        self.draw_arrow(self.ram_pos[0], self.ram_pos[1]+30,
                       self.ir_pos[0], self.ir_pos[1]-25, width=3, 
                       color=self.colors['warning'], label="inst[11]")
        
        # IR → ALU (op2/immediate)
        self.draw_arrow(self.ir_pos[0]+40, self.ir_pos[1],
                       self.alu_pos[0]-10, self.alu_pos[1]+25, width=2, label="B[4]")
        
        # IR → Addr MUX (op1)
        c.create_line(self.ir_pos[0]-40, self.ir_pos[1]-10,
                     self.addr_mux_pos[0]+15, self.addr_mux_pos[1]-10,
                     fill=self.colors['accent2'], width=2, arrow=tk.LAST)
        c.create_text(self.ir_pos[0]-55, self.ir_pos[1]-20, text="op1[4]",
                     fill=self.colors['text_dim'], font=('Consolas', 5))
        
        # ALU → ALU REG
        self.draw_arrow(self.alu_pos[0]+30, self.alu_pos[1],
                       self.alu_reg_pos[0]-25, self.alu_reg_pos[1], width=2, label="F[4]")
        
        # ALU REG → Data MUX
        c.create_line(self.alu_reg_pos[0], self.alu_reg_pos[1]+20,
                     self.data_mux_pos[0]+15, self.data_mux_pos[1]-15,
                     fill=self.colors['accent2'], width=2, arrow=tk.LAST)
        
        # Data MUX → RAM (write data)
        self.draw_arrow(self.data_mux_pos[0], self.data_mux_pos[1]+15,
                       self.ram_pos[0]-40, self.ram_pos[1]+10, width=2, label="din[4]")
    
    def draw_clean_control(self):
        """Draw clean control signals"""
        c = self.canvas
        
        # FSM → RAM control
        c.create_line(self.fsm_pos[0]+35, self.fsm_pos[1]-20,
                     self.ram_pos[0]-20, self.ram_pos[1]+30,
                     fill=self.colors['warning'], width=1, dash=(3, 2))
        c.create_text(self.fsm_pos[0]+60, self.fsm_pos[1], text="csn,rwn",
                     fill=self.colors['warning'], font=('Consolas', 5))
        
        # FSM → ALU control
        c.create_line(self.fsm_pos[0]+35, self.fsm_pos[1]-30,
                     self.alu_pos[0]-20, self.alu_pos[1]+25,
                     fill=self.colors['warning'], width=1, dash=(3, 2))
        c.create_text(self.fsm_pos[0]+70, self.fsm_pos[1]-35, text="S[3],Cin",
                     fill=self.colors['warning'], font=('Consolas', 5))
        
        # FSM → PC control
        c.create_line(self.fsm_pos[0], self.fsm_pos[1]-35,
                     self.pc_pos[0], self.pc_pos[1]+20,
                     fill=self.colors['warning'], width=1, dash=(3, 2))
        c.create_text(self.fsm_pos[0]+15, self.fsm_pos[1]-50, text="pc_inc",
                     fill=self.colors['warning'], font=('Consolas', 5))
    
    def draw_simple_clock(self):
        """Draw simple clock line"""
        c = self.canvas
        y = 360
        c.create_line(50, y, 520, y, fill=self.colors['success'], width=2)
        c.create_text(270, y+12, text="CLK & reset_n",
                     fill=self.colors['success'], font=('Consolas', 7, 'bold'))
        
        # Clock connections (short vertical lines)
        for x in [self.pc_pos[0], self.ram_pos[0], self.ir_pos[0], 
                  self.alu_reg_pos[0], self.fsm_pos[0]]:
            if x < 270:  # Left side components
                y_top = 120 if x == self.pc_pos[0] else 205 if x == self.fsm_pos[0] else 265
            else:  # Right side components
                y_top = 130 if x == self.ram_pos[0] else 265 if x == self.ir_pos[0] else 120
            c.create_line(x, y_top, x, y, fill=self.colors['success'], width=1, dash=(2, 2))
    
    def draw_compact_states(self):
        """Draw compact state annotations"""
        c = self.canvas
        states = [
            ("FETCH", 70, 60, self.colors['accent2']),
            ("LOAD", 240, 60, self.colors['warning']),
            ("EXEC", 380, 60, self.colors['accent']),
            ("STORE", 240, 320, self.colors['success']),
        ]
        for state, x, y, color in states:
            c.create_text(x, y, text=state, fill=color, font=('Consolas', 7, 'bold'))
    
    def draw_arrow(self, x1, y1, x2, y2, width=2, color=None, label=None):
        """Helper to draw an arrow with optional label"""
        c = self.canvas
        if color is None:
            color = self.colors['accent2']
        c.create_line(x1, y1, x2, y2, fill=color, width=width, arrow=tk.LAST)
        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            c.create_text(mid_x, mid_y-7, text=label, 
                         fill=self.colors['text_dim'], font=('Consolas', 5))
    
    # Keep old methods for compatibility but they won't be called
    def draw_pc(self, pos):
        """Draw Program Counter with clock/reset/increment"""
        c = self.canvas
        x, y = pos
        
        # PC box
        c.create_rectangle(x-40, y-30, x+40, y+30,
                          fill=self.colors['bg_light'], 
                          outline=self.colors['accent2'], width=2)
        c.create_text(x, y-15, text="PC", 
                     fill=self.colors['accent2'], font=('Consolas', 10, 'bold'))
        c.create_text(x, y, text="Program", 
                     fill=self.colors['text'], font=('Consolas', 7))
        c.create_text(x, y+12, text="Counter", 
                     fill=self.colors['text'], font=('Consolas', 7))
        
        # Width indicator
        c.create_text(x+50, y, text="[4]", 
                     fill=self.colors['accent2'], font=('Consolas', 7, 'bold'))
        
        # Control inputs
        c.create_text(x-50, y-10, text="CLK", anchor='e',
                     fill=self.colors['success'], font=('Consolas', 6))
        c.create_text(x-50, y+10, text="reset_n", anchor='e',
                     fill=self.colors['success'], font=('Consolas', 6))
        
        # Store position for connections
        self.pc_pos = pos
        
    def draw_ram(self, pos):
        """Draw Synchronous RAM with all ports"""
        c = self.canvas
        x, y = pos
        
        # RAM box (larger)
        c.create_rectangle(x-60, y-50, x+60, y+50,
                          fill=self.colors['bg_light'], 
                          outline=self.colors['accent'], width=3)
        c.create_text(x, y-30, text="RAM 16×4", 
                     fill=self.colors['accent'], font=('Consolas', 11, 'bold'))
        c.create_text(x, y-15, text="ram16x4_sync.v", 
                     fill=self.colors['text_dim'], font=('Consolas', 6, 'italic'))
        
        # Port labels
        c.create_text(x-70, y-20, text="addr[3:0]", anchor='e',
                     fill=self.colors['accent2'], font=('Consolas', 7))
        c.create_text(x-70, y, text="datain[3:0]", anchor='e',
                     fill=self.colors['accent2'], font=('Consolas', 7))
        c.create_text(x-70, y+20, text="csn", anchor='e',
                     fill=self.colors['warning'], font=('Consolas', 7))
        
        c.create_text(x+70, y-10, text="dataout[3:0]", anchor='w',
                     fill=self.colors['accent2'], font=('Consolas', 7))
        c.create_text(x-70, y+30, text="rwn", anchor='e',
                     fill=self.colors['warning'], font=('Consolas', 7))
        
        # Clock
        c.create_text(x, y+60, text="CLK", 
                     fill=self.colors['success'], font=('Consolas', 7))
        
        self.ram_pos = pos
        
    def draw_instruction_register(self, pos):
        """Draw 11-bit Instruction Register"""
        c = self.canvas
        x, y = pos
        
        # IR box
        c.create_rectangle(x-60, y-35, x+60, y+35,
                          fill=self.colors['bg_light'], 
                          outline=self.colors['warning'], width=2)
        c.create_text(x, y-20, text="Instruction Register", 
                     fill=self.colors['warning'], font=('Consolas', 9, 'bold'))
        c.create_text(x, y-5, text="[10:8] opcode (3b)", 
                     fill=self.colors['text'], font=('Consolas', 6))
        c.create_text(x, y+7, text="[7:4] op1 (4b)", 
                     fill=self.colors['text'], font=('Consolas', 6))
        c.create_text(x, y+19, text="[3:0] op2 (4b)", 
                     fill=self.colors['text'], font=('Consolas', 6))
        
        # Width indicator
        c.create_text(x+70, y, text="[11]", 
                     fill=self.colors['warning'], font=('Consolas', 7, 'bold'))
        
        self.ir_pos = pos
        
    def draw_alu(self, pos):
        """Draw 4-bit ALU"""
        c = self.canvas
        x, y = pos
        
        # ALU trapezoid shape
        points = [x-50, y-40, x+50, y-40, x+40, y+40, x-40, y+40]
        c.create_polygon(points, fill=self.colors['bg_light'], 
                        outline=self.colors['accent'], width=3)
        
        c.create_text(x, y-20, text="ALU 4-bit", 
                     fill=self.colors['accent'], font=('Consolas', 10, 'bold'))
        c.create_text(x, y-5, text="alu_4b.v", 
                     fill=self.colors['text_dim'], font=('Consolas', 6, 'italic'))
        c.create_text(x, y+10, text="7 Operations", 
                     fill=self.colors['text'], font=('Consolas', 7))
        
        # Input/output labels
        c.create_text(x-60, y-20, text="A[3:0]", anchor='e',
                     fill=self.colors['success'], font=('Consolas', 7))
        c.create_text(x-60, y+20, text="B[3:0]", anchor='e',
                     fill=self.colors['success'], font=('Consolas', 7))
        c.create_text(x, y-50, text="S[2:0]", 
                     fill=self.colors['warning'], font=('Consolas', 7))
        c.create_text(x+50, y, text="F[3:0]", anchor='w',
                     fill=self.colors['accent2'], font=('Consolas', 7))
        
        self.alu_pos = pos
        
    def draw_alu_register(self, pos):
        """Draw ALU Register (pipeline stage)"""
        c = self.canvas
        x, y = pos
        
        c.create_rectangle(x-50, y-25, x+50, y+25,
                          fill=self.colors['bg_light'], 
                          outline=self.colors['success'], width=2)
        c.create_text(x, y-10, text="ALU Register", 
                     fill=self.colors['success'], font=('Consolas', 9, 'bold'))
        c.create_text(x, y+5, text="alu_reg_4b.v", 
                     fill=self.colors['text_dim'], font=('Consolas', 6, 'italic'))
        
        # Clock input
        c.create_text(x-60, y, text="CLK", anchor='e',
                     fill=self.colors['success'], font=('Consolas', 7))
        
        c.create_text(x+60, y, text="f[3:0]", anchor='w',
                     fill=self.colors['accent2'], font=('Consolas', 7))
        
        self.alu_reg_pos = pos
        
    def draw_fsm(self, pos):
        """Draw FSM Decoder (control unit)"""
        c = self.canvas
        x, y = pos
        
        # FSM box
        c.create_rectangle(x-60, y-60, x+60, y+60,
                          fill=self.colors['bg_light'], 
                          outline=self.colors['warning'], width=3)
        c.create_text(x, y-40, text="FSM Decoder", 
                     fill=self.colors['warning'], font=('Consolas', 10, 'bold'))
        c.create_text(x, y-25, text="decoder_fsm.v", 
                     fill=self.colors['text_dim'], font=('Consolas', 6, 'italic'))
        
        # State list
        states = ["INIT", "FETCH", "LOAD", "EXEC", "STORE"]
        for i, state in enumerate(states):
            c.create_text(x, y-8 + i*10, text=state, 
                         fill=self.colors['text'], font=('Consolas', 6))
        
        self.fsm_pos = pos
        
    def draw_addr_mux(self, pos):
        """Draw Address Multiplexer"""
        c = self.canvas
        x, y = pos
        
        # Mux triangle
        points = [x-20, y-30, x+20, y-30, x, y+10]
        c.create_polygon(points, fill=self.colors['bg_medium'], 
                        outline=self.colors['accent2'], width=2)
        c.create_text(x, y-10, text="MUX", 
                     fill=self.colors['text'], font=('Consolas', 7, 'bold'))
        
        # Input labels
        c.create_text(x-25, y-25, text="PC", anchor='e',
                     fill=self.colors['text'], font=('Consolas', 6))
        c.create_text(x+25, y-25, text="op1", anchor='w',
                     fill=self.colors['text'], font=('Consolas', 6))
        
        # Control
        c.create_text(x+15, y-5, text="sel", 
                     fill=self.colors['warning'], font=('Consolas', 5))
        
        self.addr_mux_pos = pos
        
    def draw_data_mux(self, pos):
        """Draw Data Input Multiplexer"""
        c = self.canvas
        x, y = pos
        
        # Mux triangle
        points = [x-20, y-30, x+20, y-30, x, y+10]
        c.create_polygon(points, fill=self.colors['bg_medium'], 
                        outline=self.colors['accent2'], width=2)
        c.create_text(x, y-10, text="MUX", 
                     fill=self.colors['text'], font=('Consolas', 7, 'bold'))
        
        # Input labels
        c.create_text(x-25, y-25, text="op2", anchor='e',
                     fill=self.colors['text'], font=('Consolas', 6))
        c.create_text(x+25, y-25, text="ALU", anchor='w',
                     fill=self.colors['text'], font=('Consolas', 6))
        
        self.data_mux_pos = pos
        
    def draw_datapath_connections(self):
        """Draw all 4-bit data buses (thick solid lines)"""
        c = self.canvas
        
        # PC to Address Mux (4-bit)
        self.draw_bus(self.pc_pos[0]+40, self.pc_pos[1], 
                     self.addr_mux_pos[0]-20, self.addr_mux_pos[1]-25,
                     width=3, color=self.colors['accent2'])
        
        # Address Mux to RAM addr (4-bit)
        self.draw_bus(self.addr_mux_pos[0], self.addr_mux_pos[1]+10,
                     self.ram_pos[0]-60, self.ram_pos[1]-20,
                     width=3, color=self.colors['accent2'])
        
        # RAM dataout to IR (11-bit, shown as thick)
        self.draw_bus(self.ram_pos[0]+60, self.ram_pos[1]-10,
                     self.ram_pos[0]+100, self.ram_pos[1]-10,
                     width=4, color=self.colors['warning'], label="[11]")
        self.draw_bus(self.ram_pos[0]+100, self.ram_pos[1]-10,
                     self.ram_pos[0]+100, self.ir_pos[1],
                     width=4, color=self.colors['warning'])
        self.draw_bus(self.ram_pos[0]+100, self.ir_pos[1],
                     self.ir_pos[0]+60, self.ir_pos[1],
                     width=4, color=self.colors['warning'])
        
        # IR op1 to Address Mux (4-bit)
        self.draw_bus(self.ir_pos[0]-60, self.ir_pos[1]+7,
                     self.ir_pos[0]-100, self.ir_pos[1]+7,
                     width=3, color=self.colors['accent2'], label="op1[4]")
        self.draw_bus(self.ir_pos[0]-100, self.ir_pos[1]+7,
                     self.ir_pos[0]-100, self.addr_mux_pos[1]-25,
                     width=3, color=self.colors['accent2'])
        self.draw_bus(self.ir_pos[0]-100, self.addr_mux_pos[1]-25,
                     self.addr_mux_pos[0]+20, self.addr_mux_pos[1]-25,
                     width=3, color=self.colors['accent2'])
        
        # RAM dataout to ALU A (4-bit)
        self.draw_bus(self.ram_pos[0]+60, self.ram_pos[1]-10,
                     self.alu_pos[0]-60, self.alu_pos[1]-20,
                     width=3, color=self.colors['success'], label="A[4]")
        
        # IR op2 to ALU B (4-bit)
        self.draw_bus(self.ir_pos[0], self.ir_pos[1]+35,
                     self.ir_pos[0], self.alu_pos[1]+50,
                     width=3, color=self.colors['success'], label="op2[4]")
        self.draw_bus(self.ir_pos[0], self.alu_pos[1]+50,
                     self.alu_pos[0]-60, self.alu_pos[1]+20,
                     width=3, color=self.colors['success'])
        
        # ALU F to ALU Register (4-bit)
        self.draw_bus(self.alu_pos[0]+40, self.alu_pos[1]+40,
                     self.alu_pos[0]+40, self.alu_reg_pos[1],
                     width=3, color=self.colors['accent2'])
        self.draw_bus(self.alu_pos[0]+40, self.alu_reg_pos[1],
                     self.alu_reg_pos[0]-50, self.alu_reg_pos[1],
                     width=3, color=self.colors['accent2'], label="F[4]")
        
        # ALU Register to Data Mux (4-bit)
        self.draw_bus(self.alu_reg_pos[0], self.alu_reg_pos[1]-25,
                     self.alu_reg_pos[0], self.data_mux_pos[1]-25,
                     width=3, color=self.colors['accent2'])
        self.draw_bus(self.alu_reg_pos[0], self.data_mux_pos[1]-25,
                     self.data_mux_pos[0]+20, self.data_mux_pos[1]-25,
                     width=3, color=self.colors['accent2'], label="f[4]")
        
        # op2 to Data Mux (4-bit)
        self.draw_bus(self.ir_pos[0], self.alu_pos[1]+50,
                     self.data_mux_pos[0]-30, self.alu_pos[1]+50,
                     width=3, color=self.colors['success'])
        self.draw_bus(self.data_mux_pos[0]-30, self.alu_pos[1]+50,
                     self.data_mux_pos[0]-20, self.data_mux_pos[1]-25,
                     width=3, color=self.colors['success'])
        
        # Data Mux to RAM datain (4-bit)
        self.draw_bus(self.data_mux_pos[0], self.data_mux_pos[1]+10,
                     self.ram_pos[0]-60, self.ram_pos[1],
                     width=3, color=self.colors['accent2'])
        
    def draw_control_signals(self):
        """Draw all 1-bit control signals (thin dashed lines)"""
        c = self.canvas
        
        # FSM to RAM (csn, rwn)
        self.draw_control(self.fsm_pos[0]+60, self.fsm_pos[1]-30,
                         self.ram_pos[0]-60, self.ram_pos[1]+20,
                         label="csn,rwn")
        
        # FSM to PC (pc_inc)
        self.draw_control(self.fsm_pos[0], self.fsm_pos[1]-60,
                         self.pc_pos[0], self.pc_pos[1]+30,
                         label="pc_inc")
        
        # FSM to Address Mux (ram_addr_sel)
        self.draw_control(self.fsm_pos[0]+40, self.fsm_pos[1]-40,
                         self.addr_mux_pos[0]+15, self.addr_mux_pos[1]-5,
                         label="addr_sel")
        
        # FSM to Data Mux (ram_data_sel)
        self.draw_control(self.fsm_pos[0]+60, self.fsm_pos[1]+30,
                         self.data_mux_pos[0]-10, self.data_mux_pos[1],
                         label="data_sel")
        
        # FSM to ALU (alu_s[2:0], alu_cin)
        self.draw_control(self.fsm_pos[0]+60, self.fsm_pos[1],
                         self.alu_pos[0], self.alu_pos[1]-50,
                         label="S[3],Cin")
        
    def draw_clock_tree(self):
        """Draw clock and reset distribution (green lines)"""
        c = self.canvas
        
        # Main clock line (horizontal backbone)
        clock_y = 550
        c.create_line(30, clock_y, 530, clock_y,
                     fill=self.colors['success'], width=2)
        c.create_text(280, clock_y+15, text="CLK & reset_n Distribution",
                     fill=self.colors['success'], font=('Consolas', 8, 'bold'))
        
        # Clock to PC
        c.create_line(self.pc_pos[0], self.pc_pos[1]+30,
                     self.pc_pos[0], clock_y,
                     fill=self.colors['success'], width=2)
        
        # Clock to RAM
        c.create_line(self.ram_pos[0], self.ram_pos[1]+50,
                     self.ram_pos[0], clock_y,
                     fill=self.colors['success'], width=2)
        
        # Clock to IR
        c.create_line(self.ir_pos[0], self.ir_pos[1]+35,
                     self.ir_pos[0], clock_y,
                     fill=self.colors['success'], width=2)
        
        # Clock to ALU Register
        c.create_line(self.alu_reg_pos[0]-60, self.alu_reg_pos[1],
                     self.alu_reg_pos[0]-60, clock_y,
                     fill=self.colors['success'], width=2)
        c.create_line(self.alu_reg_pos[0]-60, clock_y,
                     self.alu_reg_pos[0], clock_y,
                     fill=self.colors['success'], width=2)
        
        # Clock to FSM
        c.create_line(self.fsm_pos[0], self.fsm_pos[1]+60,
                     self.fsm_pos[0], clock_y,
                     fill=self.colors['success'], width=2)
        
    def draw_state_flow(self):
        """Annotate the 5-state pipeline flow"""
        c = self.canvas
        
        # State flow annotations (adjusted for 560px width)
        states = [
            ("① INIT", 25, 350, self.colors['text_dim']),
            ("② FETCH", 110, 80, self.colors['accent2']),
            ("③ LOAD", 310, 80, self.colors['warning']),
            ("④ EXECUTE", 490, 240, self.colors['accent']),
            ("⑤ STORE", 310, 480, self.colors['success'])
        ]
        
        for state, x, y, color in states:
            c.create_text(x, y, text=state, 
                         fill=color, font=('Segoe UI', 9, 'bold'))
        
    def draw_bus(self, x1, y1, x2, y2, width=3, color='#00d4ff', label=None):
        """Draw a data bus with optional label"""
        c = self.canvas
        c.create_line(x1, y1, x2, y2, fill=color, width=width, arrow=tk.LAST)
        
        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            c.create_text(mid_x, mid_y-10, text=label, 
                         fill=color, font=('Consolas', 6, 'bold'))
    
    def draw_control(self, x1, y1, x2, y2, label=None):
        """Draw a control signal (dashed line)"""
        c = self.canvas
        c.create_line(x1, y1, x2, y2, 
                     fill=self.colors['warning'], width=1, dash=(3, 2))
        
        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            c.create_text(mid_x, mid_y-8, text=label, 
                         fill=self.colors['warning'], font=('Consolas', 5))

# Test standalone
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Processor Architecture Diagram")
    root.geometry("820x650")
    root.configure(bg='#1a1a2e')
    
    colors = {
        'bg_dark': '#1a1a2e',
        'bg_medium': '#16213e',
        'bg_light': '#0f3460',
        'text': '#e0e0e0',
        'text_dim': '#888888',
        'accent': '#00d4ff',
        'accent2': '#00d4ff',
        'success': '#00ff88',
        'warning': '#ffa500'
    }
    
    canvas = Canvas(root, width=800, height=600, bg=colors['bg_dark'], 
                   highlightthickness=0)
    canvas.pack(padx=10, pady=10)
    
    diagram = ArchitectureDiagram(canvas, colors)
    diagram.draw()
    
    root.mainloop()
