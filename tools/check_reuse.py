#!/usr/bin/env python3
"""
Structural Reuse Verification Script
Checks that generated Verilog modules enforce required constraints:
1. No use of forbidden operators (^, xnor, + in certain contexts)
2. Required module instantiations exist
3. Proper structural hierarchy is maintained
"""

import os
import re
import sys
from pathlib import Path

class VerilogConstraintChecker:
    def __init__(self, rtl_dir):
        self.rtl_dir = Path(rtl_dir)
        self.errors = []
        self.warnings = []
        
    def check_forbidden_tokens(self, filename, forbidden_tokens):
        """Check if file contains forbidden Verilog operators"""
        filepath = self.rtl_dir / filename
        if not filepath.exists():
            self.errors.append(f"File not found: {filename}")
            return
            
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Remove comments before checking
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        for token in forbidden_tokens:
            # Escape special regex characters
            escaped_token = re.escape(token)
            if re.search(escaped_token, content):
                self.errors.append(
                    f"{filename}: Found forbidden token '{token}'"
                )
    
    def check_instantiation(self, filename, required_module):
        """Check if file instantiates a required module"""
        filepath = self.rtl_dir / filename
        if not filepath.exists():
            self.errors.append(f"File not found: {filename}")
            return False
            
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Pattern to match module instantiation
        pattern = rf'\b{required_module}\s+\w+'
        if re.search(pattern, content):
            return True
        else:
            self.errors.append(
                f"{filename}: Missing required instantiation of '{required_module}'"
            )
            return False
    
    def check_xor_module(self):
        """Check XOR gate constraints"""
        print("Checking xor_1b.v...")
        self.check_forbidden_tokens('xor_1b.v', ['^', 'xnor'])
        
    def check_fa_1b(self):
        """Check 1-bit full adder constraints"""
        print("Checking fa_1b.v...")
        self.check_instantiation('fa_1b.v', 'xor_1b')
        self.check_forbidden_tokens('fa_1b.v', ['^'])
        
    def check_adder_4b(self):
        """Check 4-bit adder constraints"""
        print("Checking adder_4b.v...")
        found = self.check_instantiation('adder_4b.v', 'fa_1b')
        
        # Check that there are 4 instantiations
        if found:
            filepath = self.rtl_dir / 'adder_4b.v'
            with open(filepath, 'r') as f:
                content = f.read()
            instances = re.findall(r'\bfa_1b\s+\w+', content)
            if len(instances) != 4:
                self.errors.append(
                    f"adder_4b.v: Expected 4 fa_1b instances, found {len(instances)}"
                )
        
        # Check no use of + operator for addition
        filepath = self.rtl_dir / 'adder_4b.v'
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
            # Remove comments
            content = re.sub(r'//.*', '', content)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            # Check for + used in assignments (not in instantiations)
            if re.search(r'assign\s+\w+\s*=.*\+', content):
                self.errors.append(
                    "adder_4b.v: Found '+' operator in assign statement (structural adder required)"
                )
    
    def check_alu_4b(self):
        """Check ALU constraints"""
        print("Checking alu_4b.v...")
        self.check_instantiation('alu_4b.v', 'adder_4b')
        self.check_instantiation('alu_4b.v', 'xor_1b')
        
        # Check for 4 XOR instantiations for XOR operation
        filepath = self.rtl_dir / 'alu_4b.v'
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
            xor_instances = re.findall(r'xor_1b\s+\w+', content)
            if len(xor_instances) < 4:
                self.warnings.append(
                    f"alu_4b.v: Expected 4 xor_1b instances for XOR operation, found {len(xor_instances)}"
                )
    
    def check_sequential_logic(self, filename):
        """Check proper sequential logic syntax"""
        filepath = self.rtl_dir / filename
        if not filepath.exists():
            return
            
        print(f"Checking sequential logic in {filename}...")
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        in_async_reset = False
        in_clocked_block = False
        
        for i, line in enumerate(lines, 1):
            # Check for always block with async reset
            if re.search(r'always\s*@\s*\(\s*posedge\s+clk\s+or\s+negedge\s+reset_n', line):
                in_clocked_block = True
                
            # Check for reset branch
            if in_clocked_block and re.search(r'if\s*\(\s*!\s*reset_n', line):
                in_async_reset = True
                
            # Check for end of reset branch
            if in_async_reset and re.search(r'end\s+else', line):
                in_async_reset = False
                
            # Check for assignment type
            if in_clocked_block and '=' in line and not '//' in line[:line.find('=')]:
                if in_async_reset and '<=' in line:
                    self.warnings.append(
                        f"{filename}:{i}: Non-blocking assignment in reset branch (blocking '=' recommended)"
                    )
                elif not in_async_reset and not '<=' in line and '=' in line:
                    # Check if it's an assignment (not comparison)
                    if re.search(r'\w+\s*=(?!=)', line):
                        self.warnings.append(
                            f"{filename}:{i}: Blocking assignment in clocked branch (non-blocking '<=' recommended)"
                        )
    
    def run_all_checks(self):
        """Run all constraint checks"""
        print("=" * 60)
        print("Running Verilog Constraint Checks...")
        print("=" * 60)
        
        self.check_xor_module()
        self.check_fa_1b()
        self.check_adder_4b()
        self.check_alu_4b()
        self.check_sequential_logic('alu_reg_4b.v')
        self.check_sequential_logic('decoder_fsm.v')
        self.check_sequential_logic('ram16x4_sync.v')
        
        print("\n" + "=" * 60)
        print("Check Results:")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("\n✅ No errors found!")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print("\n" + "=" * 60)
        
        return len(self.errors) == 0

def main():
    # Get RTL directory
    script_dir = Path(__file__).parent
    rtl_dir = script_dir.parent / 'rtl'
    
    if not rtl_dir.exists():
        print(f"Error: RTL directory not found: {rtl_dir}")
        sys.exit(1)
    
    checker = VerilogConstraintChecker(rtl_dir)
    success = checker.run_all_checks()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
