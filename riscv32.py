class RiscVCPU():
    def __init__(self):
        self.regs = [0] * 33  # 32 Register + PC
        self.PC = 0           # PC startet bei 0
        self.memory = bytearray(16384)  # 16 KB Speicher

    def fetch(self):
        ins = int.from_bytes(self.memory[self.PC:self.PC+4], "little")
        self.PC += 4
        return ins
    
    def decode(self, ins):
        opcode = ins & 0x7F
        rd = (ins >> 7) & 0x1F
        funct3 = (ins >> 12) & 0x7
        rs1 = (ins >> 15) & 0x1F
        
        def gibi(s, e):
            return (ins >> e) & ((1 << (s - e + 1)) - 1)
        
        if opcode == 0x33:  # R-Typ
            rs2 = (ins >> 20) & 0x1F
            funct7 = (ins >> 25) & 0x7F
            return "R", opcode, rd, funct3, rs1, rs2, funct7, 0
        elif opcode == 0x13:  # I-Typ (ADDI)
            imm = gibi(31, 20)
            if imm & 0x800: imm -= 0x1000
            return "I", opcode, rd, funct3, rs1, 0, 0, imm
        elif opcode == 0x63:  # B-Typ (BEQ)
            rs2 = (ins >> 20) & 0x1F
            imm = (gibi(31, 31) << 12) | (gibi(7, 7) << 11) | \
                  (gibi(30, 25) << 5) | (gibi(11, 8) << 1)
            if imm & 0x1000: imm -= 0x2000
            return "B", opcode, 0, funct3, rs1, rs2, 0, imm
        elif opcode == 0x23:  # S-Typ (SW)
            rs2 = (ins >> 20) & 0x1F
            imm = (gibi(31, 25) << 5) | gibi(11, 7)
            if imm & 0x800: imm -= 0x1000
            return "S", opcode, 0, funct3, rs1, rs2, 0, imm
        elif opcode == 0x03:  # I-Typ (LW)
            imm = gibi(31, 20)
            if imm & 0x800: imm -= 0x1000
            return "I", opcode, rd, funct3, rs1, 0, 0, imm
        elif opcode == 0x6F:  # J-Typ (JAL)
            imm = (gibi(31, 31) << 20) | (gibi(30, 21) << 1) | \
                  (gibi(20, 20) << 11) | (gibi(19, 12) << 12)
            if imm & 0x100000: imm -= 0x200000
            return "J", opcode, rd, 0, 0, 0, 0, imm
        elif opcode == 0x37:  # U-Typ (LUI)
            imm = gibi(31, 12) << 12
            return "U", opcode, rd, 0, 0, 0, 0, imm
        else:
            return "Unknown", opcode, 0, 0, 0, 0, 0, 0
    
    def r32(self, addr):
        addr -= 0x80000000
        if addr < 0 or addr >= len(self.memory):
            raise Exception(f"read out of bounds: 0x{addr:x}")
        return int.from_bytes(self.memory[addr:addr+4], "little")

    def ws(self, addr, dat):
        addr -= 0x80000000
        if addr < 0 or addr >= len(self.memory):
            raise Exception(f"write out of bounds: 0x{addr:x}")
        self.memory[addr:addr+len(dat)] = dat
    
    def step(self):
        ins = self.fetch()
        typ, opcode, rd, funct3, rs1, rs2, funct7, imm = self.decode(ins)
        vpc = self.PC - 4  # PC before fetch

        if typ == "R" and opcode == 0x33:
            if funct3 == 0x0 and funct7 == 0x00:  # ADD
                if rd != 0:
                    self.regs[rd] = (self.regs[rs1] + self.regs[rs2]) & 0xFFFFFFFF
            elif funct3 == 0x0 and funct7 == 0x20:  # SUB
                if rd != 0:
                    self.regs[rd] = (self.regs[rs1] - self.regs[rs2]) & 0xFFFFFFFF
        elif typ == "I":
            if opcode == 0x13 and funct3 == 0x0:  # ADDI
                if rd != 0:
                    self.regs[rd] = (self.regs[rs1] + imm) & 0xFFFFFFFF
            elif opcode == 0x03 and funct3 == 0x2:  # LW
                if rd != 0:
                    self.regs[rd] = self.r32(self.regs[rs1] + imm)
        elif typ == "B" and opcode == 0x63 and funct3 == 0x0:  # BEQ
            if self.regs[rs1] == self.regs[rs2]:
                self.PC = vpc + imm  # Branch taken
            # PC already incremented by fetch if no branch
        elif typ == "S" and opcode == 0x23 and funct3 == 0x2:  # SW
            self.ws(self.regs[rs1] + imm, (self.regs[rs2] & 0xFFFFFFFF).to_bytes(4, "little"))
        elif typ == "J" and opcode == 0x6F:  # JAL
            if rd != 0:
                self.regs[rd] = self.PC  # Return address (after fetch)
            self.PC = vpc + imm  # Jump to target
        elif typ == "U" and opcode == 0x37:  # LUI
            if rd != 0:
                self.regs[rd] = imm
        return True

    def dump(self):
        print(f"PC: {self.PC}, x1: {self.regs[1]}, x2: {self.regs[2]}")

# Testprogramm
cpu = RiscVCPU()
cpu.memory[0:4] = (0x00500093).to_bytes(4, "little")  # ADDI x1, x0, 5
cpu.memory[4:8] = (0x00308133).to_bytes(4, "little")  # ADD x2, x1, x3
cpu.memory[8:12] = (0xFE000F63).to_bytes(4, "little")  # BEQ x0, x0, -4
cpu.memory[12:16] = (0x00108023).to_bytes(4, "little")  # SW x1, 0(x0)
cpu.memory[16:20] = (0x00008103).to_bytes(4, "little")  # LW x2, 0(x0)
cpu.memory[20:24] = (0xFF5FF06F).to_bytes(4, "little")  # JAL x0, -10
cpu.memory[24:28] = (0x000005B7).to_bytes(4, "little")  # LUI x11, 0

cpu.step()  # ADDI
cpu.dump()
cpu.step()  # ADD
cpu.dump()
cpu.step()  # BEQ
cpu.dump()
cpu.PC = 12  # Überspringe Schleife
cpu.step()  # SW
cpu.dump()
cpu.step()  # LW
cpu.dump()
cpu.step()  # JAL
cpu.dump()
cpu.step()  # LUI
cpu.dump()
print(f"Memory at 0x80000000: {cpu.r32(0x80000000)}, x11: {cpu.regs[11]}")