
"""CPU functionality."""

import sys

# Operation Tables
binary_operation = {
    0b00000001: 'HLT',  # 1
    0b10000010: 'LDI',  # 300
    0b01000111: 'PRN',  # 71
    0b01000101: 'PUSH', # 69
    0b01000110: 'POP',  # 70
    0b01010000: 'CALL', # 80
    0b00010001: 'RET',  # 17
    0b01010100: 'JMP',  # 84
    0b01010101: 'JEQ',  # 85
    0b01010110: 'JNE',  # 87 Was b01010111
}

math_operation = {
    "ADD": 0b10100000,  # 160
    "SUB": 0b10100001,  # 161
    "MUL": 0b10100010,  # 162
    'CMP': 0b10100111   # 167
}

# Global Constants
SP = 7          # Stack Pointer

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        # Registers
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.operand_a = None
        self.operand_b = None

        # Internal Registers
        self.PC = 0             # Program counter set to 0
        self.MAR = None         # Memory address register
        self.MDR = None         # Memory data register
        
        self.FL = 0b00000000    # Flags

        # Branch Table
        self.instructions = {}
        self.instructions['HLT'] = self.HALT
        self.instructions['LDI'] = self.LOAD
        self.instructions['PRN'] = self.PRINT
        self.instructions['PUSH'] = self.PUSH
        self.instructions['POP'] = self.POP
        self.instructions['CALL'] = self.CALL
        self.instructions['RET'] = self.RET
        self.instructions['JMP'] = self.JMP
        self.instructions['JEQ'] = self.JEQ
        self.instructions['JNE'] = self.JNE

    def CALL(self):
        """Calls a subroutine (function) at the address stored in the register."""
        self.reg[SP] -= 1

        instruction_address = self.PC + 2            # Address of the instruction
        self.ram[self.reg[SP]] = instruction_address # Pushing instruction address onto the stack
        register = self.operand_a                    # PC is set to the address stored in the register
        self.PC = self.reg[register]

    def RET(self):
        self.PC = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    def JMP(self):
        """Jump to the address stored in the given register."""
        address = self.reg[self.operand_a]

        self.PC = address

    def JEQ(self):
        """If `equal` flag is set (true), jump to the address stored in the given register."""
        address = self.reg[self.operand_a]

        if self.FL == 1:
            self.PC = address
        else:
            self.PC += 2

    def JNE(self):
        """If `E` flag is clear (false, 0), jump to the address stored in the given register."""
        address = self.reg[self.operand_a]

        if self.FL == 0:
            self.PC = address
        else:
            self.PC += 2

    def HALT(self):
        """Exit the current program"""
        sys.exit()

    def LOAD(self):
        """Load value to register"""
        self.reg[self.operand_a] = self.operand_b

    def PRINT(self):
        """Print the value in a register"""
        print(self.reg[self.operand_a])

    def PUSH(self):
        """Push the value in the given register to the top of the stack"""
        # decrement the SP
        global SP

        self.reg[SP] -= 1

        # copy the value in the given register to the address pointed to by SP
        value = self.reg[self.operand_a]

        self.ram[self.reg[SP]] = value

    def POP(self):
        """Pop the value at the top of the stack into the given register"""
        global SP
        # copy the value from the address pointed to by SP to the given register

        value = self.ram[self.reg[SP]]      # value at the address pointed to by SP
        register = self.operand_a           # given register from argument
        self.reg[register] = value          # copying the value from memory to the given register
        self.reg[SP] += 1                   # increment SP

    def ram_read(self, address):
        """Accepts an address to read and returns the value stored there"""
        self.MAR = address
        self.MDR = self.ram[address]
        return self.ram[address]

    def ram_write(self, value, address):
        """Accepts a value to write, and the address to write it to"""
        self.MAR = address
        self.MDR = value
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("ERROR: Must have file name")
            sys.exit(1)

        filename = sys.argv[1]

        try:
            address = 0
            # Open the file
            with open(filename) as program:
                
                for instruction in program:                         # Read all the lines
                    comment_split = instruction.strip().split("#")  # Parse out comments
                    value = comment_split[0].strip()                # Cast the numbers from strings to ints
                    if value == "":                                 # Ignore blank lines
                        continue

                    num = int(value, 2)
                    self.ram[address] = num
                    address += 1

        except FileNotFoundError:
            print("File not found")
            sys.exit(2)

    def ALU(self, op, reg_a, reg_b):
        """ALU operations."""
   
        if op == math_operation["ADD"]:
            # print("ADDING")
            self.reg[reg_a] += self.reg[reg_b]

        elif op == math_operation["SUB"]:
            # print("SUBTRACTING")
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == math_operation["MUL"]:
            # print("MULTIPYING")
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == math_operation["CMP"]:       # Compare the values in two registers
            valueA = self.reg[self.operand_a]
            valueB = self.reg[self.operand_b]
            
            if valueA == valueB:        # FLAG -> 0000LGE
                self.FL = 0b00000001

            if valueA < valueB:
                self.FL = 0b00000100

            if valueA > valueB:
                self.FL = 0b00000010
            print(self.FL)
        else:
            raise Exception("Unsupported ALU operation")
    
    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def move_PC(self, IR):
        """Accepts an Instruction Register.\n
        Increments the PC by the number of arguments returned by the IR."""

        # increment the PC only if the instruction doesn't set it
        if (IR << 3) % 255 >> 7 != 1:
            self.PC += (IR >> 6) + 1

    def run(self):
        """Run the CPU."""
        while True:
            # read the memory address that's stored in register PC,
            # store that result in IR (Instruction Register).
            # This can just be a local variable
            IR = self.ram_read(self.PC)
    
            # using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables
            self.operand_a = self.ram_read(self.PC + 1)
            self.operand_b = self.ram_read(self.PC + 2)

            # if bit is on, run math operation
            if (IR << 2) % 255 >> 7 == 1:
                self.ALU(IR, self.operand_a, self.operand_b)
                self.move_PC(IR)

            # else, run basic operations
            elif (IR << 2) % 255 >> 7 == 0:
                self.instructions[binary_operation[IR]]()
                self.move_PC(IR)

            # if instruction is unrecognized, exit
            else:
                print(f"Did not understand that command: {IR}")
                print(self.trace())
                sys.exit(1)
